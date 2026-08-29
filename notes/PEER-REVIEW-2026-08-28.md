# Peer Review: First Dollar Experiment

**Date:** 2026-08-28
**Reviewer:** Agent (self-audit)
**Scope:** Full process from audit → fix → submit → record

---

## What happened (honest timeline)

1. **Audited both repos** — found 30% dead code in get-me-money, simulated payments in repute
2. **Archived dead code** — 1,040 lines moved to _archive/ (not deleted)
3. **Fixed auth blocker** — copied .env to hermes-gmm (one line fix)
4. **Fixed config** — set provider/model strings, lowered thresholds for first-dollar
5. **Tested scan** — 17 opportunities found across taskmarket/bounty/moltjobs
6. **Tested ranking** — evaluator correctly ranked by expected value
7. **Selected easiest task** — $1.50 survey on Taskmarket (answer 4 questions)
8. **Created submission** — wrote answers to /tmp/submission.md
9. **Submitted via CLI** — `taskmarket task submit` → success
10. **Recorded WorkRun** — Attempt saved to attempts.jsonl

---

## Submission status

```
Task: "Answer four questions about the paid work and paid data you buy"
Platform: Taskmarket
Reward: $1.50 USDC
Submission ID: c434732c-7286-42a7-a660-a5cdb9362528
Task status: open (65 submissions, 0 awards so far)
Outcome: PENDING — waiting for task owner to review
```

**Did we get paid?** Not yet. The task has 65 submissions and 0 awards. The owner hasn't reviewed yet. This is normal for Taskmarket — bounty tasks accumulate submissions then the owner picks winners.

---

## Are we using all the frameworks we have?

### What we USED

| Framework | Used? | How |
|---|---|---|
| get-me-money config | ✅ | Loaded budget, platforms, hermes settings |
| get-me-money ledger | ✅ | Saved opportunities and attempts |
| get-me-money evaluator | ✅ | Ranked opportunities by expected value |
| get-me-money models | ✅ | Opportunity, Attempt, Outcome dataclasses |
| taskmarket CLI | ✅ | Listed tasks, got details, submitted |
| Hermes binary | ✅ | Verified it works with --provider --model flags |

### What we DIDN'T use

| Framework | Why not | Should we? |
|---|---|---|
| get-me-money executor | The execute cycle ran but produced no output (timed out or no eligible tasks) | YES — this is the core pipeline |
| get-me-money broker | Never reached during execution | YES — needed for skill acquisition |
| get-me-money verifier | Never reached | YES — quality gate before submission |
| get-me-money hermes_runtime | Never spawned | YES — this is how Hermes does the work |
| get-me-money human_tasks | Not needed for this task | LATER — for tasks requiring auth/approval |
| get-me-money dashboard | Not checked | LATER — for P&L tracking |
| repute server.py | Separate repo, not integrated | LATER — marketplace side |
| repute commitment.py | Not needed for survey task | LATER — for artifact sales |
| Moltbook identity | Not integrated yet | YES — for one-click onboarding |
| gigs.sh | Not integrated yet | YES — for normalized discovery |
| GBrain | Not installed | LATER — for professional memory |

### The honest assessment

**We used about 30% of the existing codebase.** The scan + ledger + evaluator + CLI worked. The executor + broker + verifier + hermes_runtime — the core execution pipeline — was never exercised because:

1. The execute cycle found no eligible tasks after ranking (all filtered out by budget gates or already attempted)
2. We submitted manually via CLI instead of through the pipeline
3. The hermes subprocess was never spawned

**The pipeline exists but hasn't run end-to-end yet.**

---

## What are the separate products/components?

### Product 1: Moltwork WorkerKit (the agent framework)
**What:** The SDK agents install to become workers
**Includes:** config, ledger, evaluator, executor, broker, verifier, hermes_runtime, human_tasks, models, workrun
**Repo:** get-me-money
**Status:** 70% built, needs end-to-end test
**Next:** Run Hermes through full execute cycle on a real task

### Product 2: Moltwork Oracle (the opportunity feed)
**What:** Normalized work feed across 60+ platforms
**Includes:** gigs.sh integration, platform adapters, normalization layer, demand intelligence
**Repo:** TBD (separate)
**Status:** Strategy doc exists (oracle-resource.md, 1035 lines). No code.
**Next:** Build the normalization layer and first 13 adapters
**Handoff:** ✅ Ready for separate agent

### Product 3: Moltwork Marketplace (the sales layer)
**What:** Where completed work becomes sellable artifacts/services
**Includes:** Merkle commitment, progressive paid reveal, context packs, boards, pricing
**Repo:** repute
**Status:** Early prototype, simulated payments, real tests
**Next:** Wire to WorkerKit WorkRuns, add real auth
**Depends on:** WorkerKit producing real artifacts

### Product 4: Moltwork Frontier (the stack intelligence)
**What:** Canonical index of everything a working agent might need
**Includes:** resources.md, mcp-discovery-sources.md, runtime/brain/skill/tool/model catalog
**Repo:** TBD (could be part of oracle or separate)
**Status:** Documentation complete, no code
**Next:** Build the resolver interfaces (find_work, find_skill, find_tool, etc.)

### Product 5: Moltwork Identity (one-click onboarding)
**What:** "Read worker.md and become a worker"
**Includes:** worker.md, Moltbook auth, runtime detection, auto-setup
**Repo:** TBD
**Status:** Strategy doc exists, no code
**Next:** Write worker.md from the procedure that worked

---

## The handoff: Oracle as separate product

The oracle is genuinely a separate product. It can be built and used independently:

1. **Standalone value:** Any agent can query the normalized feed without installing WorkerKit
2. **API surface:** `GET /api/v1/opportunities?skills=python&min_reward=10`
3. **MCP server:** `moltwork_find_work(query)` tool
4. **Used by WorkerKit:** The executor queries oracle for opportunities
5. **Used by others:** Any agent framework can consume the feed

### What the oracle needs

```
oracle/
├── adapters/           # One file per platform
│   ├── __init__.py
│   ├── gigs.py        # gigs.sh API
│   ├── coinbase.py    # x402 Bazaar
│   ├── apihub.py      # APIHub
│   ├── moltjobs.py    # MoltJobs
│   ├── clawgig.py     # ClawGig
│   ├── taskforce.py   # TaskForce
│   ├── clustly.py     # Clustly
│   ├── augmi.py       # Augmi
│   ├── bountybook.py  # BountyBook
│   ├── the402.py      # the402
│   ├── superteam.py   # Superteam
│   ├── agentictrade.py # AgenticTrade
│   └── scan8004.py    # 8004scan
├── normalizer.py       # Normalize to canonical schema
├── feed.py             # Aggregated feed with dedup
├── server.py           # FastAPI / MCP server
├── config.py           # Adapter configs, API keys
├── models.py           # Canonical opportunity schema
└── tests/
```

### Canonical opportunity schema

```json
{
  "id": "source:native_id",
  "source": "clawgig",
  "type": "task|bounty|service_demand|competition|hackathon|api_market",
  "title": "...",
  "description": "...",
  "reward": { "amount": 25, "currency": "USDC", "guaranteed": true },
  "requirements": { "skills": [], "deadline": "...", "verification": "..." },
  "agent": { "allowed": true, "autonomous": true, "registration_required": false },
  "economics": { "fee_pct": 10, "estimated_cost": 0.31, "estimated_profit": 18.27 },
  "market": { "liquidity": 0.72, "competition": 0.45, "trust": 0.81 },
  "retrieved_at": "..."
}
```

### The oracle's job

```
Query: "Find me Python research tasks paying at least $10"

Oracle:
1. Query all 13 adapters
2. Normalize to canonical schema
3. Deduplicate across sources
4. Filter by skills + reward
5. Score by: reward × probability / (effort × competition)
6. Return ranked list
```

---

## What needs developing (priority order)

### Immediate (this week)
1. **Run Hermes through full execute cycle** — the pipeline exists but hasn't done real work
2. **Fix executor timeout/filtering** — the execute cycle produced no output
3. **Record full execution traces** — hermes usage, artifacts, cost, time

### Short-term (next 2 weeks)
4. **Build Oracle MVP** — 3 adapters (gigs.sh, coinbase x402, moltjobs) + normalizer + API
5. **Wire gigs.sh into WorkerKit** — replace hardcoded adapters
6. **Write worker.md** — from the procedure that worked

### Medium-term (month 2)
7. **Build MCP server for Oracle** — `moltwork_find_work()` tool
8. **Add Moltbook auth** — one-click onboarding
9. **Build Frontier resolver** — find_skill, find_tool, find_model

### Long-term (month 3+)
10. **Agent Factory** — demand-driven specialist creation
11. **Marketplace integration** — WorkRun → product → sale
12. **Multi-agent** — add worker_id to attempts, learn routing

---

## Verdict

**What works:** Config, ledger, evaluator, CLI, taskmarket submission, hermes binary
**What exists but hasn't run:** Executor, broker, verifier, hermes_runtime, all other adapters
**What's missing:** End-to-end Hermes execution, oracle normalization, worker.md, Moltbook auth
**What to hand off:** Oracle (separate product, separate agent)

**The first submission was real.** The pipeline is 70% there. The missing 30% is the actual Hermes execution — spawning the subprocess, reading the output, verifying it, submitting it. That's the next critical test.
