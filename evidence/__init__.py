"""Moltwork Evidence — cryptographic work primitives.

Seven primitives:
1. WorkloadManifestV1 — attested workload identity
2. Attested Agent Keys — explicit key domains
3. WorkOrderV1 + WorkAcceptanceV1 — EIP-712 commitments
4. AgentLeaseV1 — cryptographically restricted authority
5. RunReceiptV1 — verifiable execution provenance
6. Trace commitments — Merkle tree over trace events
7. Transparency log — append-only evidence with Ethereum checkpoints
"""
