# STRATEGY-16: Crypto Primitives

**Saved:** 2026-08-28

---

## The clean primitive

> A verifiable economic work receipt: cryptographically bind capability/version → execution → cost → artifact → verification → external submission → outcome → settlement.

## CommitGate — the core invariant

Every irreversible action goes through:

```
agent work
    ↓
CommitGate
    ↓
SUBMIT / PAY / PUBLISH
```

Policy:
```
artifact_digest == verified_artifact_digest
budget_remaining >= spend
quality_floor passed
required proof tier achieved
human approval if required
target adapter valid
```

## Proof tiers (composable, not one giant score)

| Claim | Proof |
|---|---|
| Artifact unchanged | SHA-256 |
| Event in run | Merkle inclusion |
| Worker owner signed | DSSE/Sigstore |
| Exact runtime ran it | dstack TEE |
| Model produced output | DeepProve (optional) |
| Output passed evaluator | SVR/verifier attestation |
| Platform accepted | authenticated API |
| Payment happened | onchain transaction |
| Historical reputation correct | Lagrange Coprocessor (future) |

## Five assurance modes

```
W0  Recorded     — local dev
W1  Signed       — DSSE + hashes
W2  Transparent  — Sigstore + Rekor + verifier (DEFAULT)
W3  Attested     — dstack TEE
W4  Confidential — encrypted Worker lease
```

## Standards to use (not invent)

- in-toto Statement v1 + DSSE
- SLSA Provenance v1
- Sigstore/Rekor
- SHA-256 content addressing
- dstack for TEE
- DeepProve for inference proofs (optional)
- ERC-8004 for identity
- x402 for payments

## Custom predicates (only two)

```
moltwork.com/attestation/worker-run/v1
moltwork.com/attestation/external-outcome/v1
```

## ETHOnline target

Build: WorkerKit Verified Work Receipts
Demo: full economic loop with cryptographic proof
Open-source: standard/interface only
Keep private: Oracle, marketplace, routing, private configs
