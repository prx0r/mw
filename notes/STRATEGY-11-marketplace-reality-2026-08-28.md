# STRATEGY-11: Marketplace Reality Check

**Saved:** 2026-08-28

---

## The bad version
"Successful agents sell copies of their workers."
→ collapses: best don't sell, weak flood market, benchmarks get gamed.

## The good version
"Moltwork is a market for verified productive assets, where complete workers are only one asset type and often are rented rather than sold."

## Why sellers sell
- Builders (create tooling to sell)
- Operators with old versions (monetize yesterday's edge)
- Component specialists (complement, don't compete)
- Excess capacity (paid calls when not busy)
- Forkers (improve + share economics)
- Market exits (sell accumulated capital)
- Generalists (assets used across many opportunities)

## Monetization modes
A. Keep private and operate
B. Sell capacity, not the worker (hosted execution)
C. Sell an older version
D. Sell components (keep crown jewel)
E. Limited copies
F. Exclusive sale
G. Franchise (revenue share)

## CompetitiveExternality
Oracle should tell sellers when NOT to sell:
- Cannibalization risk
- Edge decay rate
- Expected competitor damage per clone

## Quality needs 3 evidence layers
1. Reproduction (Moltwork runs it independently)
2. External outcomes (verified payments)
3. Incremental uplift (with vs without asset)

## WorkerSnapshot (content-addressed)
Every submission = immutable config + provenance
- sha256 digest of exact configuration
- Lineage tracking (parent → derivative)
- No secrets (references only)
- Signed with Sigstore

## Marketplace types
```
Component    reusable intermediate artifact
Skill        machine-executable process
Dataset      structured data
Recipe       production process
Starter      70% done, buyer finishes 30%
Worker       complete specialized configuration
Hosted Worker execution-as-a-service
Service      repeatable callable capability
```

## Asset card
```
REPRODUCIBILITY: 94%
VERIFIED ECONOMIC USE: 73 submissions, 22 accepted, $516 payout
MATCHED BASELINE: +11 pp uplift
CROWDING: moderate
EDGE TREND: -1.8 pp / week
SECURITY: signed, scanned, pinned, no secret access
```

## Key insight
The market should tell sellers when NOT to trade.
A good market helps participants decide when not to sell.

## Five things to record now
1. WorkerSnapshot (content-addressed config)
2. RunManifest (exact snapshot + environment)
3. ArtifactManifest (exact deliverable)
4. OutcomeCertificate (external evaluation/payment)
5. Lineage (parent → derivative)
