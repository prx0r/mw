# AGENTS.md — WorkerKit Operating Rules

## Architecture

```
Opportunity → Campaign → WorkOrder → Run → Receipt → Lab → Harvest → Capabilities → Learning
     ↑              ↑                          ↓           ↓              ↓              ↓
  Oracle      WorkPlan/WorkUnit          EventLedger   Harvester    CapabilityTracker  ReflectionPipeline
```

**Key modules:**
- `orchestrator.py` — wires the full pipeline
- `sdk.py` — WorkerKit core (start → event → cost → verify → gate → close)
- `capabilities.py` — multi-dimensional capability evidence from runs
- `harvest/candidates.py` — extract reusable assets from completed work
- `lab/reflection.py` — outcome-gated learning (OBSERVED → PROPOSED → UNDER_TEST → VALIDATED)
- `lab/projection.py` — EventLedger → LabProjection sync
- `lab/assessor/` — OpportunityResearchPack + AssessorPack (G0-G2 gates)
- `lab/bridge.py` — HTTP bridge connecting Letta mod tools to WorkerKit
- `mods/moltwork-lab/` — Letta Code mod (11 tools + lifecycle hooks)
- `economics/decisions.py` — marginal EV continue/abort decisions
- `core/hashing.py` — SHA-256 + Keccak-256 + JCS canonicalization (single source of truth)

## Letta Integration

**Runtime:** Letta Code with `backend: "local"`
**Model:** ALWAYS mimo-v2.5 via opencode-go. NEVER kimi or expensive models.
**Fallback:** Groq gpt-oss for testing only.
**Mod:** `@moltwork/letta-lab` in `mods/moltwork-lab/`

### Letta conventions

- **Worker identity:** persistent `worker_id → letta_agent_id` mapping in `data/letta-workers/`
- **Sessions:** fresh Letta session per WorkOrder (never reuse conversations)
- **Memory:** Letta MemFS for durable facts; `scratch/` for timestamped working notes; `WORKING.md` for compact mutable state
- **Skills:** Letta/Agent Skills format (SKILL.md)
- **Trajectories:** `@letta-ai/trajectory` format for experience export
- **Learning:** ACE-style ADD/UPDATE/REMOVE memory deltas, not full rewrites
- **Three mutation classes:**
  - COGNITIVE (memory/context) → Letta memory
  - PROCEDURAL (skill) → Letta Skills
  - HARNESS (mod/tool/permission) → Letta Mods
- **Evaluation:** `letta-evals` as runner, NOT custom eval infrastructure
- **Benchmarks:** CGE WorldPacks (Git-native, forkable, composable)

### Letta mod tools (registered by @moltwork/letta-lab)

- `oracle_search`, `oracle_get_opportunity`
- `lab_brief`, `lab_recall_experiment`, `lab_get_capability_claim`, `lab_list_worker_versions`
- `budget_check`, `budget_record`
- `assessor_preflight`, `assessor_request_review`
- `moltwork_record_outcome`

### Lifecycle hooks (silent witnesses → WorkerKit events)

- `session.started` → run.started
- `tool.called` → tool.invoked
- `artifact.created` → artifact.registered
- `session.completed` → run.completed

## CGE Worlds

**Repo:** `/root/mwgit` (Git-native evaluation substrate)
**Schema:** `mwgit/schema/` (world, result, claim schemas)

### WorldPack structure

```
worlds/<name>/
├── world.yaml          # taxonomy, capabilities, evaluator config
├── public/             # what the worker sees (requirements, docs)
├── scenarios/
│   ├── dev.jsonl       # training scenarios
│   └── validation.jsonl
├── hidden/             # sealed test suite (worker never sees)
├── evaluator/
│   ├── gates/          # deterministic checks
│   ├── rubric.yaml     # scoring rubric
│   └── llm_judge.md    # LLM-as-judge prompt
└── README.md
```

### Two capability claims

- **WorkerCapabilityClaim** — "worker X performs well on task Y"
- **WorldValidityClaim** — "world Z predicts external outcomes"

## Commands

```bash
# Run all tests (PYTHONPATH required)
cd /root/workerkit && PYTHONPATH=/root:/root/workerkit for t in tests/test_*.py; do python3 "$t" 2>&1 | tail -3; done

# Run single test
cd /root/workerkit && PYTHONPATH=/root:/root/workerkit python3 tests/test_orchestrator.py 2>&1

# Start lab bridge (background)
setsid nohup python3 lab/bridge.py --port 8789 > /tmp/lab-bridge.log 2>&1 &

# Start runtime-letta (background)
cd /root/workerkit/services/runtime-letta && setsid nohup npx tsx src/index.ts > /tmp/runtime-letta.log 2>&1 &

# Run a real task
cd /root/workerkit && PYTHONPATH=/root:/root/workerkit python3 wk_run.py --worker researcher-v1 --task "..." --budget 1.0

# Start background task
setsid nohup CMD > /tmp/output.log 2>&1 &
echo "PID: $!"

# Kill by PID (NEVER pkill)
kill PID
```

## Rules

1. **Fail fast** — if something doesn't work in 3 attempts, stop and report
2. **Background tasks** — always `setsid nohup CMD > /tmp/log 2>&1 &`
3. **Kill by PID** — find PID first, then `kill PID`. NEVER `pkill`.
4. **No long timeouts** — max 30s for any single command unless explicitly told otherwise
5. **Log everything** — write to `/root/workerkit/data/logs/`
6. **Test before claiming** — run the code, don't assume it works
7. **mimo-v2.5 only** — NEVER use kimi, gpt-5.x, or expensive models. Groq gpt-oss for fallback testing only.

## Module Cleanup

- `archive/dead/` — archived dead code
- `tests/support/` — test-only modules
- `evidence/canonical.py` — re-exports from `core/hashing.py`
- `vendor/` — cloned reference repos (letta-evals, trace2skill, ace, hydradb, prometheus, mods, BEAM)

## Model Config

Provider: opencode-go
Model: mimo-v2.5 (ALWAYS)
Backend: local
Fallback: Groq openai/gpt-oss-120b (testing only)
API keys: in `.env` file

## Fast Iteration Rules (CRITICAL — VIOLATION = WASTED TIME)

1. **NEVER sleep or wait** — `sleep` is FORBIDDEN. If something takes time, do other work while it runs. Check logs with `tail`, not `sleep`.
2. **Always use nohup** — `setsid nohup CMD > /tmp/log 2>&1 &` then move on immediately
3. **Run tests while building** — start test in background, continue coding in same message
4. **Simultaneous processes** — build + test + integrate in parallel, never sequential
5. **Fail fast** — if something fails 3 times, stop and try a different approach
6. **Check results by reading logs** — `tail /tmp/log` not `sleep N && tail`
7. **Push to git early and often** — commit working state before risky changes
8. **Import first, build second** — use existing frameworks (Harbor, GEPA, OpenEvolve, Trace2Skill) before writing custom code

### The ritual (before EVERY long job):
```
1. Background it:  setsid nohup CMD > /tmp/log 2>&1 &
2. Note the PID:   echo "PID $!"
3. Move on:        do real work in same response
4. Check later:    tail /tmp/log   (NOT sleep + tail)
```

### What NOT to do:
```
BAD:  sleep 5 && tail /tmp/log
BAD:  sleep 300  (waiting for background job)
BAD:  python3 script.py  (foreground blocking)
GOOD: setsid nohup python3 script.py > /tmp/out.log 2>&1 & PID=$!; echo "PID $PID"; # now do other work
```

## Harbor Integration

- API key: HARBOR_API_KEY in env
- Agent: opencode with OPENCODE_API_KEY
- Binary: /root/.opencode/bin/opencode
- Run: `harbor exec -p TASK -a opencode -m opencode-go/mimo-v2.5 --disable-verification`

## Production Milestone (the only thing that matters)

> **Complete three real submission campaigns with one persistent Letta worker, where every run is reproducible through Harbor/Git, every evaluation can be regraded later, and Campaign 3 can query structured evidence from Campaigns 1-2.**

### Immediate coding order (DO THIS NOW)

1. ~~Archive `full_loop.py` as non-production reference~~ DONE
2. ~~Delete/replace the custom RewardKit imitation and regex evaluator~~ DONE (archived flywheel evaluator)
3. Get `runtime-letta` running reliably as one persistent real worker. Fresh session per Campaign. Freeze cognition during active Campaigns.
4. Create private `lab-campaigns` and `lab-worlds` Git repos.
5. Make `mw campaign create/run/grade/regrade/outcome` work explicitly.
6. Use Harbor trial directories as execution records rather than duplicating them.
7. Wire actual HydraDB over Bolt/HTTP; demote SQLite "Hydra" to optional local projection.
8. Build one real `technical-submission-v0` Harbor World.
9. Run one actual live Campaign end-to-end.
10. Regrade it with Assessor v1.
11. Record the external outcome.
12. Only then create the first memory/process/Skill candidate.

### What NOT to build yet

- OpenEvolve orchestration
- Agent Lightning
- A-MEM
- Custom memory algorithms
- Custom benchmark runtime
- GEPA (wait for 3-5 real campaigns first)
- Marketplace UI
- Tokenomics
- TEE (use Harbor separate verifier first)

### The production stack

```
ORACLE → economic demand
    ↓
MOLTWORK → Campaign + budget + experiment policy
    ↓
┌───────────┬───────────┐
│ LETTA     │ HARBOR    │
│ persistent│ world +   │
│ worker    │ execution │
└───────────┴───────────┘
    ↓
WorkerRun = Harbor Trial + Letta WorkerVersion + Campaign ID + WorkerKit Receipt
    ↓
HYDRADB → derived evidence graph
    ↓
CGE → "what should we try next?"
```

### Learning hierarchy (enforce ruthlessly)

```
Level 0: NO learning — just finish real work
Level 1: artifact optimization within a Campaign
Level 2: process reuse between Campaigns
Level 3: Letta memory/Skill evolution (only after evidence)
Level 4: World/assessor evolution via regrade + outcomes
Level 5: optimizer experimentation (GEPA/OpenEvolve)
Level 6: actual policy/model training
```

**We need Levels 0-2 right now. Everything above waits.**
