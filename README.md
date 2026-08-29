# WorkerKit

**Economic runtime for autonomous agents.**

WorkerKit wraps any agent execution in a canonical, measurable, replayable, evaluable and attestable work process.

## Install

```bash
pip install workerkit
```

## Usage

```python
from workerkit.sdk import WorkerKit, WorkOrder

wk = WorkerKit()

# Start a run
run = wk.start(WorkOrder(
    objective="Research competitor pricing",
    reward_value="25.00",
    reward_currency="USD",
))

# Record what happens
run.event("model.call", {"model": "mimo", "tokens": 1000})
run.cost("llm", 0.05)
run.cost("api", 0.02)

# Verify
contract = {"required_outputs": ["SUBMISSION.md"], "minimum_quality": 0.6}
vr = await wk.verify(run, contract, artifact_sha256="abc123")

# Gate
cd = wk.gate(run, "SUBMIT", vr, budget_remaining=5.0)
if cd.decision == "ALLOW":
    # Submit externally
    run.event("submission.made", {"venue": "taskmarket"})

# Close and get receipt
receipt = wk.close(run)
print(f"Receipt: {receipt.root_hash}")
```

## What WorkerKit owns

```
WorkOrder freezing
Worker identity/version binding
canonical events
artifact commitments
actual economic ledger
acceptance contracts
independent verification
irreversible-action gates
submission evidence
external outcomes
settlement evidence
WorkReceipt generation
learning signals
```

## What WorkerKit does NOT own

Agent reasoning, planning, memory, skills, browser, MCP, coding, workflow durability.

WorkerKit wraps the agent. It doesn't replace it.

## Architecture

```
WORKERKIT
├── core/        schema, events, artifacts, receipts
├── economics/   costs, budgets, decisions
├── verify/      contracts, gates, verifier adapters
├── adapters/    execution, telemetry, marketplaces, payments
└── server/      ingest, postgres, object_store
```

## Tests

```bash
python tests/test_invariants.py  # 15 tests, all passing
```

## License

MIT
