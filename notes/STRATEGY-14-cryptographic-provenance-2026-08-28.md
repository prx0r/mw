# STRATEGY-14: Cryptographic Provenance

**Saved:** 2026-08-28

---

## The assurance ladder

### Level 1: Content-addressed WorkerRun (DO NOW)
- SHA-256 hashes on all artifacts
- Append-only event chain
- Merkle root at completion
- Sign the root

### Level 2: in-toto attestations (DO NOW)
- Use standard in-toto + DSSE
- Custom predicate: `moltwork.com/attestation/worker-run/v1`
- Signed envelopes with identity

### Level 3: Public transparency log (SOON)
- Sigstore/Rekor for tamper-resistant provenance
- Optional Ethereum anchoring for timestamps

### Level 4: Independent verification (SOON)
- Separate verifier produces attestation
- Simple Verification Result predicate
- Separation of producer and verifier

### Level 5: TEE (OPTIONAL, LATER)
- Cryptographically prove WorkerKit ran correctly
- Encrypted config leasing
- Not needed for V1

### Level 6: TLSNotary (OPTIONAL, LATER)
- Prove HTTPS responses from external markets
- Selective disclosure of authenticated data

### Level 7: ZK proofs (VERY LATER)
- Selective private claims only
- Not for full agent execution

---

## What to build now

1. WorkerRun Bundle (hashes, immutable events, exact configs)
2. in-toto attestations + DSSE (use existing standard)
3. Sigstore/Rekor publication (tamper-resistant provenance)
4. Independent verifier attestations
5. Outcome receipts from marketplaces

## What NOT to build yet

- TEE (optional premium)
- TLSNotary (optional advanced)
- ZK proofs (selective claims only)

---

## The proof architecture

```
WORKER ASSET
    ↓
WORKER MANIFEST (config + code hashes)
    ↓
WORKER RUN (immutable event stream)
    ↓
RUN MERKLE ROOT
    ↓
in-toto attestation + DSSE signature
    ↓
┌─────────────────┬─────────────────┐
Sigstore Rekor    Verifier         TEE (optional)
    ↓                 ↓                 ↓
VERIFIED RUN
    ↓
SUBMISSION
    ↓
external outcome evidence
    ↓
VERIFIED OUTCOME
    ↓
ASSET PROFILE
```

## What WorkerKit proves

```
✓ this output was generated
✓ this run was recorded
✓ this verifier checked it
✓ these artifacts have not changed
✓ this exact configuration was used
```

What it does NOT prove without TEE:
```
✗ the operator didn't modify the environment
```

What it does NOT prove at all:
```
✗ the external marketplace's internal decision
✗ the provider actually ran model X
```
