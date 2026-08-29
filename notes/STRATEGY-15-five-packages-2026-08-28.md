# STRATEGY-15: Five Packages + Standards

**Saved:** 2026-08-28

---

## Five packages

```
workerkit-core       framework-neutral execution
workerkit-economics  cost model, routing, learning
workerkit-proof      in-toto, SLSA, Sigstore, DSSE
workerkit-outcomes   external receipts, verification
workerkit-confidential  dstack TEE (optional)
```

## Standards to use (not invent)

- in-toto Statement v1 + DSSE
- SLSA Provenance v1
- in-toto Runtime Trace v0.1
- in-toto SVR v0.2
- Sigstore bundles + Rekor
- SHA-256 content addressing
- OpenTelemetry GenAI conventions
- LiteLLM for execution
- dstack for confidential mode

## Custom predicates (only two)

```
moltwork.com/attestation/worker-run/v1
moltwork.com/attestation/external-outcome/v1
```

## Five assurance modes

```
W0  Recorded     — local dev
W1  Signed       — DSSE + hashes
W2  Transparent  — Sigstore + Rekor + verifier (DEFAULT)
W3  Attested     — dstack TEE
W4  Confidential — encrypted Worker lease
```

## Canonical objects

```
Opportunity → WorkerRun → Submission → Outcome → Settlement
```

Never mix submission accepted ≠ money received.

## First implementation target

TaskMarket → WorkerKit → in-toto/Sigstore → TaskMarket on-chain settlement.

TaskMarket already provides artifact hashes, award records, Base settlement.
