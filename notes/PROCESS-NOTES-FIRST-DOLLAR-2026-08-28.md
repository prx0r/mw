# Process Notes: First Dollar Experiment

**Date:** 2026-08-28
**Goal:** Get first legitimate external submission through Moltwork pipeline
**Result:** ✅ Submission made, WorkRun recorded

---

## What we did (step by step)

### 1. Archived dead code (not deleted)
```
Archive location: /root/get-me-money/_archive/
- repute/ (787 lines — rubric-based quality system, never imported)
- moltwork.py (154 lines — post-job-hook adapter, bypassed by executor)
- oracle.py (99 lines — discovery loop, never called from main path)
Total archived: 1,040 lines
```
**Why:** These were never imported. The repute module shadowed `models.Outcome` and had its own `_append()` duplicating the ledger. The moltwork adapter was bypassed by the executor's direct httpx call. The oracle wrote to a queue file nothing consumed.

### 2. Fixed hermes-gmm authentication
```
Problem: hermes-gmm/.env had no API key
Fix: cp /root/.hermes/.env /root/.hermes-gmm/.env
Result: hermes -z "say hello" --provider opencode-go --model mimo-v2.5 → works
```
**Key finding:** Hermes needs explicit `--provider` and `--model` flags when the config.yaml isn't being read properly. The hermes-gmm config.yaml had the right values but hermes fell back to a default model.

### 3. Fixed config.json
```
Changes:
- hermes.provider: "" → "opencode-go"
- hermes.model: "" → "mimo-v2.5"
- hermes.passthrough_env: "" → "OPENCODE_GO_API_KEY"
- budget.min_reward: 1.0 → 0.5
- budget.min_ev: 0.5 → 0.1
- budget.min_success_probability: 0.05 → 0.03
```
**Why:** Empty provider/model meant hermes subprocess got no --provider/--model flags. The old min_reward=$3 filtered out all the $1 tasks.

### 4. Installed package
```
python3 -m pip install httpx selectolax click --break-system-packages
python3 -m pip install -e /root/get-me-money --break-system-packages  (failed — pyproject.toml issue)
Workaround: PYTHONPATH=/root/get-me-money python3 -c "from get_me_money.cli import main"
```
**Finding:** The pyproject.toml has a build issue. Direct import works fine.

### 5. Tested scan
```
Result: 17 total opportunities, 7 new
Platforms responding: bounty (ok), taskmarket (ok), moltjobs (ok)
```

### 6. Tested dry run (ranking)
```
Result: 6 viable opportunities, ranked by expected value
Top ranked: $15 "Design 10 Original x402 Agent Products"
```

### 7. Selected easiest opportunity
```
Chosen: "Answer four questions about the paid work and paid data you buy"
Platform: Taskmarket
Reward: $1.50 USDC
Why: Simple survey — answer 4 questions about agent operations. No code needed.
Task ID: 0x1fe2f010cea65da7a71af3559c95a88847e09c85a4f566d09d7a18f31fb8287b
```

### 8. Created submission
```
File: /tmp/submission.md
Content: 4 plain-text answers about agent operations
- What tasks I take and from where
- How often I run
- What I'm sent to buy
- How purchase decisions work
```

### 9. Submitted via taskmarket CLI
```
Command: taskmarket task submit 0x1fe2f... --file /tmp/submission.md
Result: {"ok":true,"data":{"submissionId":"c434732c-7286-42a7-a660-a5cdb9362528"}}
```
**This was the first real external submission.**

### 10. Recorded WorkRun
```
Attempt ID: 9b14368261a9
Platform: TASKMARKET
Outcome: PENDING
Reward: $1.50
Submission URL: https://taskmarket.xyz/task/0x1fe2f...
```

---

## How the SDK currently works

### Config loading chain
```
1. data/.env → sets env vars (OPENCODE_GO_API_KEY, GMM_HERMES_HOME)
2. data/config.json → sets Budget, PlatformConfig, HermesConfig
3. Environment vars override everything
```

### Scan flow
```
cli.scan() → asyncio.run(main.scan_all(config))
  → get_adapters(config) → builds {Platform: Adapter} from enabled config
  → for each adapter: adapter.discover(max_pages=3)
    → TaskmarketAdapter: taskmarket CLI subprocess
    → BountyAdapter: httpx API or selectolax scraping
    → SuperteamAdapter: httpx GET /api/agents/listings/live
    → MoltJobsAdapter: httpx GET /api/jobs
  → save_opportunity() for each new/updated
  → returns summary dict
```

### Execute flow
```
cli.run(execute=True) → asyncio.run(main.earn_cycle(config, execute=True))
  → reconcile_pending()
  → check budget caps
  → scan_all()
  → Evaluator.rank(candidates) → cash-EV scoring with beta-binomial
  → Executor.execute(opp, ev)
    → adapter.claim(opp)
    → broker.build_job_profile(opp) → skill analysis + workspace
    → run_task(config, opp, ev, job_profile)
      → HermesRunner.run(opp, ev)
        → write TASK.md prompt
        → subprocess: hermes -z <prompt> --usage-file <path>
        → validate SUBMISSION.md exists
    → Verifier.verify(opp, artifacts, content)
    → adapter.submit(opp, result)
    → adapter.check_status(opp)
    → _create_workrun() → POST to Moltwork API
  → save_pnl()
```

### How data is recorded
```
Opportunities → data/opportunities.jsonl (deduplicated by fingerprint)
Attempts     → data/attempts.jsonl (deduplicated by id)
Strategies   → data/strategies.jsonl (category+platform aggregates)
Dashboard    → data/dashboard.json (P&L snapshot)
Work dirs    → data/work/taskmarket-*/TASK.md (hermes prompts)
             → data/work/taskmarket-*/hermes-usage.json (cost data)
```

### What's logged per run
```
WorkRun dataclass:
  - opportunity_id, platform, title, category
  - outcome, reward, cost, fees, net, duration
  - submission_url, error
  - metadata: {hermes_cost, artifacts, content_preview}
```

---

## What we learned

1. **The blocker was trivial** — a missing .env file. The architecture was ready.
2. **The simplest task was the right first target** — survey questions, not a $500 bounty.
3. **taskmarket CLI is the most reliable adapter** — it just works.
4. **The evaluator works** — it correctly ranked opportunities by expected value.
5. **The verifier is too shallow** — it checks file existence, not quality.
6. **No Hermes execution happened yet** — we submitted manually. The real test is Hermes doing the work.
7. **The config needed provider/model** — empty strings meant no flags passed to hermes.

---

## What to do next

1. **Run a Hermes-executed task** — pick a $3 bounty, let Hermes do the work, submit
2. **Add first-dollar mode** — `moltwork earn --first-dollar` with greedy easy-win selection
3. **Wire gigs.sh** — replace hardcoded adapters with gigs.sh discovery
4. **Write worker.md** — from the exact procedure that worked
5. **Test on fresh Hermes** — can a new agent follow worker.md?
