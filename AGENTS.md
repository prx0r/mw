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
