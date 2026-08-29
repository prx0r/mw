# STRATEGY-17: Ecosystem Reuse

**Saved:** 2026-08-28

---

## The insight

WorkerKit is not unique as an agent harness. That layer is commoditizing.

The moat is the layer AROUND harnesses:

```
economic run → exact costs → durable trajectory → verification
→ external outcome → learning → reusable process → portable reputation
```

## What to reuse (not rebuild)

| Concern | Use |
|---|---|
| Agent capabilities | Pydantic AI Harness |
| Durable execution | DBOS initially |
| Run checkpoint/fork | Pydantic StepPersistence |
| Trace schema | OpenInference + OTEL |
| Evaluation | Inspect AI |
| Portable agent | Letta Agent File |
| Agent-to-agent | A2A |
| Tools | MCP |
| Payments | x402 adapters |
| Economic routing | QDW (ours) |
| CostEvents | QDW (ours) |
| Work/outcome schema | WorkerKit (ours) |
| Verified WorkReceipt | WorkerKit/Moltwork (ours) |
| Process learning | WorkerKit (ours) |
| Market intelligence | Oracle (ours) |

## Architecture

```
ORACLE → opportunities + market data
    ↓
WORKERKIT (economic + evidence runtime)
    ↓
FRAMEWORK ADAPTERS (Pydantic/Hermes/LangGraph)
    ↓
capabilities (Pydantic Harness / MCP / A2A)
    ↓
execution
    ↓
submission
    ↓
External Outcome
    ↓
learning (Inspect/Phoenix)
    ↓
Worker vNext
```

## The moat

Generic agent runtime is NOT the moat. Pydantic's harness proves that layer is commoditizing.

The moat is:

```
Oracle sees work
  → WorkerKit attempts it
  → records exact process + economics
  → external result arrives
  → which approach actually won?
  → process improves
  → verified history accumulates
  → better routing / reputation
  → more work
```

That dataset gets better ONLY by doing real work.
