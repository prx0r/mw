# workerkit

**The economic evidence kernel for autonomous agents.**

WorkerKit proves what happened during work. It's the thin layer between "agent did something" and "here's the receipt."

## What it does

```
WorkOrder → Run → events → costs → verify → gate → receipt
```

11 record families. 55/55 tests. ~1,200 lines.

## Quick start

```python
from workerkit.sdk import WorkerKit, WorkOrder

wk = WorkerKit()
run = wk.start(WorkOrder(objective="Research", reward_value="25.00"))
run.event("model.call", {"model": "mimo", "tokens": 8000})
run.cost("llm", 0.08)
vr = await wk.verify(run, contract, "abc")
cd = wk.gate(run, "SUBMIT", vr, 5.0)
receipt = wk.close(run)
```

## What WorkerKit IS

Economic runtime for autonomous agents. Thin wrapper around arbitrary frameworks.

## What WorkerKit is NOT

Agent framework, memory, skills, orchestration, marketplace.

## Tests

```bash
python tests/test_invariants.py  # 55 tests, all passing
```

## Related repos

- `mwmarket/` — marketplace layer (listings, transactions)
- `mwgo/` — consumer product (connect agent, start earning)
- `repute/` — oracle (market intelligence)
