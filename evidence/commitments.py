"""Commitments — cryptographic binds to off-chain state.

Commitments use Keccak-256 for Ethereum compatibility.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from evidence.canonical import keccak256, canonical_json


@dataclass
class RunCommitment:
    """Commitment to a WorkerKit run's canonical state."""
    run_id: str = ""
    work_order_id: str = ""
    event_chain_head: str = ""
    event_count: int = 0
    artifact_root: str = ""
    worker_manifest_digest: str = ""
    policy_digest: str = ""
    cost_summary: str = ""

    def digest(self) -> str:
        """Keccak-256 commitment to the run state."""
        return keccak256(canonical_json({
            "runId": self.run_id,
            "workOrderId": self.work_order_id,
            "eventChainHead": self.event_chain_head,
            "eventCount": self.event_count,
            "artifactRoot": self.artifact_root,
            "workerManifestDigest": self.worker_manifest_digest,
            "policyDigest": self.policy_digest,
            "costSummary": self.cost_summary,
        }))

    def to_dict(self) -> dict:
        return {
            "runId": self.run_id,
            "workOrderId": self.work_order_id,
            "eventChainHead": self.event_chain_head,
            "eventCount": self.event_count,
            "artifactRoot": self.artifact_root,
            "workerManifestDigest": self.worker_manifest_digest,
            "policyDigest": self.policy_digest,
            "costSummary": self.cost_summary,
            "commitmentDigest": self.digest(),
        }


@dataclass
class ReceiptCommitment:
    """Commitment to a full attested receipt."""
    receipt_digest: str = ""
    challenge_hash: str = ""

    def report_data(self) -> bytes:
        """64-byte report_data for TEE attestation.

        receiptDigest (32 bytes) || challengeHash (32 bytes)
        Exactly 64 bytes — binds receipt + fresh challenge.
        """
        rd = bytes.fromhex(self.receipt_digest) if self.receipt_digest else b"\x00" * 32
        ch = bytes.fromhex(self.challenge_hash) if self.challenge_hash else b"\x00" * 32
        return rd[:32].ljust(32, b"\x00") + ch[:32].ljust(32, b"\x00")
