# WorkerKit v0.1 Hardening Plan
**Date:** 2026-08-29
**Reviewer assessment:** Architecture validated; core integrity hardening in progress.

## Previous Review vs Now

| Area | Previous | Now | Still wrong |
|------|----------|-----|-------------|
| Architecture | 8.5 | 9 | Clean |
| Hash/provenance | 2 | 6 | workerId wrong, receipt unsigned |
| Verification | 2 | 3.5 | Gate fixed; verifier still placeholder |
| Economics | 7 | 7.5 | Marginal EV logic wrong, Decimal incomplete |
| Tests | 3 | 5.5 | Several tests overclaim |
| Packaging | 3 | 2.5 | Broken CLI, broken pyproject.toml |
| Repo hygiene | 3 | 6 | Stale data in git |

## P0 Items (execute now)

1. **Artifact registration** — `run.artifact()` computes digest, not arbitrary string
2. **Verifier registry** — typed verifiers, unsupported check → UNKNOWN
3. **Gate binds VerificationResult** — CommitGate requires verification input
4. **close() validates chain** — refuse receipt on invalid chain
5. **Canonical WorkerEvent = ledger** — one serialization, both sides use it
6. **Fix workerId** — use WorkerManifest digest or runId
7. **Stop calling receipts signed** — rename to "content-addressed statement"
8. **Fix marginal EV** — continue on marginal, not whole-run
9. **Decimal all the way** — money is Decimal, string at boundaries
10. **Fix packaging + CLI + delete stale data**

## P0.5 Items (after P0)

- verify_receipt() independent verifier
- Freeze capability/process modules
- Actual tamper tests (UPDATE/DELETE in SQLite)
- Real CI from clean checkout

## Acceptance test for v0.1

```
fresh machine → git clone → pip install .
→ Oracle fixture → WorkOrder
→ WorkerKit starts run
→ real executor produces bytes
→ WorkerKit registers artifact itself (digest computed internally)
→ real deterministic acceptance contract evaluated
→ VerificationResult PASS
→ gate allows SUBMIT
→ SubmissionReceipt produced
→ OutcomeReceipt recorded independently
→ SettlementReceipt recorded independently
→ WorkReceipt/evidence bundle produced
→ new process verifies full bundle from scratch
→ modify ANY canonical event or artifact → verification fails
```

If that passes, freeze WorkerKit v0.1.
