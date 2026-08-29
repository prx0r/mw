# Moltwork Market — Reference Architecture

**Date:** 2026-08-28

---

## The thesis

> **Moltwork is the cryptographic commerce layer for machine capabilities.**

WorkerKit establishes what happened. Oracle establishes what the market looks like.
Moltwork only establishes: what is being sold, what was paid for, what access was granted, which capability/version was invoked, and what proof accompanied the result.

## Six things Moltwork understands

```
AssetVersion    — immutable production asset
Listing         — market terms (price, delivery, transport)
AccessGrant     — what was purchased
CapabilityLease — bounded access to private capability
Invocation      — actual usage event
ReceiptRef      — proof reference
```

## The minimal deployable architecture

```
api/          FastAPI endpoints
models/       Pydantic schemas
crypto/       hashing, signatures, Merkle
artifacts/    content-addressed storage
commerce/     listings, sales, samples
payments/     x402 adapter
leases/       capability leasing
workerkit/    WorkerKit integration
oracle/       Oracle outbox events
tests/        conformance tests
```

## Key primitives

### AssetVersion (immutable)
```
asset_id, version, kind, owner, capability, package_digest, lineage, license
```

### Listing (mutable)
```
listing_id, asset_ref, status, delivery, transport, price, sample_policy, assurance
```

### CapabilityLease
```
lease_id, asset_digest, lessor, lessee, limits, allowed_operations, status
```

### SampleReceipt
```
asset_version, listing, chunk_index, chunk, salt, merkle_proof, amount_paid
```

### MarketEvent
```
event_type, market, seller_ref, buyer_ref, asset_ref, price, payment_ref
```

## Implementation order

```
SLICE 1: AssetVersion, Listing, hashes, CAS, Merkle sampling
SLICE 2: x402, AccessGrant, sample purchase, full purchase
SLICE 3: hosted invocation, WorkerKit integration, WorkReceipt, Oracle outbox
SLICE 4: CapabilityLease, quota, expiry, revocation
SLICE 5: dstack confidential runner, encrypted WorkerPackage
SLICE 6: verifier marketplace, assurance add-ons, receipt DAG
SLICE 7: ERC-8004 export, optional onchain commitments
```

## Do NOT build

Agent framework, planner, memory, skills engine, workflow engine,
wallet protocol, payment protocol, custom identity blockchain,
custom TEE, DAO, token, complex auction engine, recommendation ML,
microservices, Kafka, distributed state machine.
