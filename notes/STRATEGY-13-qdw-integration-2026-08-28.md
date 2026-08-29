# STRATEGY-13: QDW → WorkerKit Integration

**Saved:** 2026-08-28

---

## QDW is the ancestor, not a sibling

QDW already built:
- HotSwap router (model/provider selection)
- Bandit learning (Beta posteriors, Wilson bounds)
- Quota economics (shadow cost for free models)
- Hard constraints (exclusions, budget, context)
- Failure classification + circuit breaking
- Cost ledger (CostEvent with tokens, providers)
- CPVS (cost-per-verified-success)
- Make-vs-buy routing
- Persistent posterior learning

## What to transplant

```
workerkit/economics/
  routes.py       ← QDW hotswap/types.py
  router.py       ← QDW HotSwapRouter
  learning.py     ← bandit + persistent posterior
  quota.py        ← quota shadow-cost logic
  failure.py      ← error classes + breaker
  costs.py        ← CostLedger, extended tokens
  budget.py       ← NEW: live EV/reforecast controller
```

## What Moltwork adds (not in QDW)

1. EXTERNAL REWARD — this job pays $20
2. LIVE RUN ECONOMICS — spent/projected mid-run
3. EXTERNAL SUCCESS — did marketplace accept/pay?
4. INCREMENTAL EV — P(success from here) × payout - remaining cost
5. ACTION — CONTINUE / SWITCH / BUY HELP / ABORT

## The loop becomes

```
CostModel (historical prior)
  → PREFLIGHT (route + projected envelope)
  → WORKER RUN (meter everything)
  → REFORECASTER (is this still worth it?)
  → OUTCOME (actual cost-to-success)
  → CostModel update
```

## What NOT to reuse from QDW

- agentic_opportunity_score (collapsed into one number)
- Full DAG orchestration
- Complex scheduling
- Factory OS
