"""RunReceiptV1 — verifiable execution provenance.

The centerpiece. Every WorkerKit execution ends with a signed run receipt.
TEE key signs the receipt.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from evidence.canonical import sha256, keccak256, canonical_json


@dataclass
class RunReceiptV1:
    """Full verifiable run receipt.

    Schema: moltwork.run-receipt.v1

    Contains:
    - run identity (runId, agentId)
    - job commitment (workOrderHash, leaseHash)
    - workload identity (workloadId, attestationHash)
    - commitments (inputCommitment, outputCommitment, traceRoot)
    - economics (tokensUsed, executionCost, paymentReference)
    - artifacts (artifactRoot)
    - signatures (teeSigner, signature)
    """
    schema_version: str = "moltwork.run-receipt.v1"

    # Run identity
    run_id: str = ""
    agent_id: str = ""
    workload_id: str = ""

    # Job commitment
    work_order_hash: str = ""
    lease_hash: str = ""

    # Workload attestation
    attestation_hash: str = ""
    compose_hash: str = ""

    # Commitments
    input_commitment: str = ""
    output_commitment: str = ""
    trace_root: str = ""  # Merkle root over TraceEvents
    artifact_root: str = ""  # hash over artifact digests

    # Economics
    tokens_used: int = 0
    execution_cost: str = "0"
    cost_currency: str = "USD"
    payment_reference: str = ""

    # Policy
    model_policy_hash: str = ""
    tool_policy_hash: str = ""

    # Timing
    started_at: float = 0.0
    completed_at: float = field(default_factory=time.time)

    # Status
    status: str = ""  # completed, failed, rejected

    # Cryptographic binding
    tee_signer: str = ""  # TEE-derived public key
    signature: str = ""  # TEE signature over receipt digest

    def receipt_digest(self) -> str:
        """Keccak-256 of canonical receipt (excluding signature)."""
        return keccak256(canonical_json({
            "schemaVersion": self.schema_version,
            "runId": self.run_id,
            "agentId": self.agent_id,
            "workloadId": self.workload_id,
            "workOrderHash": self.work_order_hash,
            "leaseHash": self.lease_hash,
            "attestationHash": self.attestation_hash,
            "composeHash": self.compose_hash,
            "inputCommitment": self.input_commitment,
            "outputCommitment": self.output_commitment,
            "traceRoot": self.trace_root,
            "artifactRoot": self.artifact_root,
            "tokensUsed": self.tokens_used,
            "executionCost": self.execution_cost,
            "costCurrency": self.cost_currency,
            "paymentReference": self.payment_reference,
            "modelPolicyHash": self.model_policy_hash,
            "toolPolicyHash": self.tool_policy_hash,
            "startedAt": self.started_at,
            "completedAt": self.completed_at,
            "status": self.status,
            "teeSigner": self.tee_signer,
        }))

    def to_dict(self) -> dict:
        digest = self.receipt_digest()
        return {
            "schemaVersion": self.schema_version,
            "run": {
                "runId": self.run_id,
                "agentId": self.agent_id,
                "workloadId": self.workload_id,
            },
            "job": {
                "workOrderHash": self.work_order_hash,
                "leaseHash": self.lease_hash,
            },
            "attestation": {
                "attestationHash": self.attestation_hash,
                "composeHash": self.compose_hash,
            },
            "commitments": {
                "inputCommitment": self.input_commitment,
                "outputCommitment": self.output_commitment,
                "traceRoot": self.trace_root,
                "artifactRoot": self.artifact_root,
            },
            "economics": {
                "tokensUsed": self.tokens_used,
                "executionCost": self.execution_cost,
                "costCurrency": self.cost_currency,
                "paymentReference": self.payment_reference,
            },
            "policy": {
                "modelPolicyHash": self.model_policy_hash,
                "toolPolicyHash": self.tool_policy_hash,
            },
            "timing": {
                "startedAt": self.started_at,
                "completedAt": self.completed_at,
            },
            "status": self.status,
            "receiptDigest": digest,
            "teeSigner": self.tee_signer,
            "signature": self.signature,
        }

    def save(self, path: str):
        import os
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/run-receipt.json", "w") as f:
            json.dump(self.to_dict(), f, indent=2)
