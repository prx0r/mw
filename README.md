# WorkerKit

**Execution kernel for the Moltwork Lab.**

WorkerKit does the work and records receipts. It is the canonical source of
truth for what happened during a run. Git stores versions. Hydra stores
evidence. WorkerKit stores receipts.

```
pip install -e ".[dev]"        # install
python3 -m pytest tests/ -q   # tests
```

## What's inside

| Module | Role |
|---|---|
| `lab_kernel.py` | Lab orchestration — wires CG, CGE, Letta, HydraDB |
| `campaign.py` | Campaign lifecycle — create/run/grade/regrade |
| `hydra_projectors.py` | Feed runs, evaluations, outcomes into HydraDB |
| `hydra_schema.py` | Node/edge type definitions for the experience graph |
| `mw_labkit/` | Lab kit — runtime, harbor, records, hashing |
| `venues/` | Platform adapters (Metaculus, GitHub, Moltwork) |
| `providers/` | BATS routing, model registry |
| `services/runtime-letta/` | Letta runtime service |

## Architecture (from Frozen Decisions)

```
                    ORACLE
          finds market opportunities
                     │
                         ▼
                    MOLTWORK
             campaign + scientist layer
                     │
      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼
   LETTA          HARBOR          GEPA/
 persistent      WORLDS        OpenEvolve
 worker          evaluators    search/evolution
 cognition
      │              │              │
      └──────────────┼──────────────┘
                     ▼
                 WorkerRun
                     │
             WorkerKit evidence
                     │
               Trajectory
                     │
               evaluation
                     │
                     ▼
                 HYDRADB
           empirical experience graph
                     │
                     ▼
                 MOLTING
         ┌───────────┼───────────┐
         ▼           ▼           ▼
      Memory       Skill       Process
         │           │           │
         └───────────┼───────────┘
                     ▼
                 Git branch
                     │
               evaluate again
                     │
              promote / reject
```

## The 14-Step Campaign Pipeline

```
0.  INGEST OPPORTUNITY     → Oracle → ontology mapping
1.  BUILD SUCCESS MODEL    → Letta research agent
2.  COMPILE WORLD          → Harbor task(s)
3.  RECALL EXPERIENCE      → Hydra → LabBrief
4.  DECIDE SEARCH MODE     → exploit vs explore
5.  IDEATION SEARCH        → N candidates → successive halving
6.  EXECUTION              → persistent Letta Worker
7.  ITERATIVE REVIEW       → Harbor/RewardKit → diagnostics
8.  FREEZE RUN             → Git commits + WorkerKit receipt
9.  EXTERNAL SUBMISSION    → real opportunity → outcome
10. HYDRA PROJECTION       → project into empirical graph
11. MOLT                   → Trajectory → candidate changes
12. TEST MOLTS             → Git worktrees → control vs candidate
13. PROMOTE                → merge if validated
14. NEXT OPPORTUNITY       → repeat from stronger prior
```

## Frozen Decisions

1. **Letta owns the worker** — do not wrap in pseudo-agent framework
2. **Trajectory is the interchange format** — `@letta-ai/trajectory`
3. **CGE sits on Harbor** — Harbor tasks = worlds, CGE = experiments
4. **Harbor Reward Kit for evaluators** — multi-dimensional reward.json
5. **Letta Evals for stateful evaluation** — memory, config, trajectory
6. **GEPA for reflective search/evolution**
7. **OpenEvolve for MAP-Elites diversity**
8. **Agent Lightning later** — weight/policy training
9. **Trace2Skill for post-run skill distillation**
10. **Letta dreaming as experimental treatment**
11. **A-MEM/Memory-R1 as research arms**
12. **Letta Skills prove Git-asset thesis**
13. **`.af` as worker asset format**

## Key Files

```
lab_kernel.py              Lab orchestration (CG + CGE + Letta + HydraDB)
campaign.py                Campaign lifecycle
hydra_projectors.py        Feed data into HydraDB
hydra_schema.py            Node/edge type definitions
mw_labkit/hydra.py         HTTP client for HydraDB
mw_labkit/records.py       RunBinding, EvaluationRecord
mw_labkit/runtime.py       Runtime adapter
venues/base.py             WorkVenue protocol
venues/metaculus.py        Metaculus adapter
providers/bats.py          Budget-aware model routing
```

## HydraDB

**Status:** Running in Docker on ports 7687/8443/9090

```bash
# Check status
docker ps | grep hydradb

# Auth token
cat /root/workerkit/data/hydradb/auth-token
# → private-lab-hydradb-token-2026-secure

# Connection
from neo4j import GraphDatabase
token = open('/root/workerkit/data/hydradb/auth-token').read().strip()
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', token))
```

## Letta

**Status:** Running on port 3000

```bash
# Check health
curl http://localhost:3000/health

# Worker status
curl http://localhost:3000/workers
```

## Tests

```bash
cd /root/workerkit
python3 -m pytest tests/ -q
```
