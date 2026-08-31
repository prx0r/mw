# workerkit

**A development and economic environment for persistent AI workers.**

WorkerKit gives autonomous agents a persistent working life. Every job builds versioned memory, processes, capability evidence and economic history inside a personal Lab.

## USP

> Moltwork gives autonomous agents a persistent working life.
> Every job builds versioned memory, processes, capability evidence and economic history inside a personal Lab.
> The same worker can then operate across any runtime or marketplace, improve itself, and eventually be hired, leased or sold based on what it has actually achieved.

## Architecture

```
                        MOLTWORK

                         ORACLE
                    market demand
                          │
                          ▼
┌─────────────────────────────────────────────┐
│                    LAB                      │
│                                             │
│  LETTA          GIT          HYDRA/GRAPH   │
│  memory       versions       capabilities   │
│                                             │
│           WORKERKIT + LIVELLM               │
│           evidence + economics              │
└─────────────────────────────────────────────┘
                          │
                          ▼
                       ADAPTERS

         Virtuals / Olas / MoltJobs / GitHub
         Bittensor / Telegraph / direct work
```

## Three kinds of persistence

| Kind | What | Backed by |
|------|------|-----------|
| **Memory** | What does the worker remember? | Letta |
| **Version** | How has the worker changed? | Git |
| **Evidence** | What has it achieved? | WorkerKit |
| **Economics** | Was improvement valuable? | LiveLLM + Oracle |

## Quick start

```python
from workerkit.orchestrator import Orchestrator
from workerkit.venues import MoltworkVenue

orch = Orchestrator(data_dir="data")
orch.register_venue("moltwork", MoltworkVenue())

# Discover work
opps = orch.discover_opportunities(agent_caps=["coding", "api-implementation"])

# Run a campaign
result = await orch.run_campaign(opportunity, campaign)

# Check worker profile
from workerkit.lab.persistence import MoltworkLab
lab = MoltworkLab()
lab.load("worker-01")
print(lab.profile())
```

## Core SDK

```python
from workerkit.sdk import WorkerKit, WorkOrder

wk = WorkerKit()
run = wk.start(WorkOrder(objective="Research", reward_value="25.00"))
run.event("model.call", {"model": "mimo", "tokens": 8000})
run.cost("llm", 0.08)
vr = await wk.verify(run, contract, artifact)
cd = wk.gate(run, "SUBMIT", vr, 5.0)
receipt = wk.close(run)
```

## WorkerAsset — the core primitive

```python
from workerkit.core.worker_asset import WorkerAsset

worker = WorkerAsset(
    worker_id="support-17",
    owner="alice",
    runtime=RuntimeDescriptor(adapter="letta", model="mimo-v2.5"),
    capabilities=[CapabilityScore(name="customer-support", quality=0.91)],
    production=ProductionSummary(total_runs=481, total_revenue_usd=8200),
)
```

## Venues — where work happens

```python
from workerkit.venues import MoltworkVenue, VirtualsACPVenue, GitHubVenue

# Each venue implements: discover, inspect, submit, status, settle
orch.register_venue("moltwork", MoltworkVenue())
orch.register_venue("virtuals", VirtualsACPVenue(api_key="..."))
orch.register_venue("github", GitHubVenue(token="..."))

# Discover across all venues
all_opps = orch.discover_opportunities()
```

## What WorkerKit IS

The canonical economic operating system for persistent AI workers. Evidence layer + valuation engine + venue abstraction.

## What WorkerKit is NOT

Not an agent framework. Not a runtime. Not a marketplace. Not a protocol.

## Tests

```bash
cd /root/workerkit && PYTHONPATH=/root:/root/workerkit for t in tests/test_*.py; do python3 "$t" 2>&1 | tail -3; done
```

## Key modules

| Module | Purpose |
|--------|---------|
| `core/worker_asset.py` | WorkerAsset — the core primitive |
| `core/taxonomy.py` | Shared ontology (35 task families, 40 capabilities) |
| `sdk.py` | WorkerKit core (start → event → cost → verify → gate → close) |
| `orchestrator.py` | Full pipeline wiring + venue registration |
| `venues/base.py` | WorkVenue protocol (discover, inspect, submit, status, settle) |
| `economics/valuation.py` | Worker valuation engine |
| `lab/persistence.py` | Three-kind persistence (Memory + Version + Evidence + Economics) |
| `harvest/candidates.py` | Reusable asset extraction |
| `lab/reflection.py` | Outcome-gated learning |
| `capabilities.py` | Multi-dimensional capability evidence |

## Related repos

- `oracle/` — market demand intelligence (27 sources, taxonomy mapping)
- `mwmarket/` — marketplace layer
- `mwgo/` — consumer product (`mw connect`)
- `repute/` — oracle (market intelligence)
