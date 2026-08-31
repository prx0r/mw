"""RunCommitment — the object attested inside dstack TEE.

Not just "some container ran in a TEE."
Proving: this version of this Worker, performing this task with these
dependencies, committed to this output/run history inside this attested
environment.

RunCommitment = SHA256(
    worker_version_digest
    ||
    work_order_digest
    ||
    process_version_digest
    ||
    dependency_root
    ||
    event_chain_head
    ||
    artifact_root
)
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def _sha256(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


@dataclass
class RunCommitment:
    """The object attested inside dstack TEE.

    Binds WorkerVersion + WorkOrder + ProcessVersion + Dependencies
    + EventChain + ArtifactRoot into a single content-addressed commitment.
    """
    worker_version_digest: str = ""  # SHA-256 of WorkerVersion manifest
    work_order_digest: str = ""  # SHA-256 of WorkOrder
    process_version_digest: str = ""  # SHA-256 of ProcessVersion
    dependency_root: str = ""  # SHA-256 of RunDependency
    event_chain_head: str = ""  # Head of append-only event chain
    artifact_root: str = ""  # SHA-256 of artifact Merkle root

    # Metadata (not part of commitment hash, but included in attestation)
    run_id: str = ""
    worker_id: str = ""
    task_family_id: str = ""
    taxonomy_hash: str = ""

    def compute_digest(self) -> str:
        """Compute the commitment digest. This is what gets attested."""
        parts = [
            self.worker_version_digest,
            self.work_order_digest,
            self.process_version_digest,
            self.dependency_root,
            self.event_chain_head,
            self.artifact_root,
        ]
        return _sha256("||".join(parts))

    def to_dict(self) -> dict:
        return {
            "run_commitment_digest": self.compute_digest(),
            "worker_version_digest": self.worker_version_digest,
            "work_order_digest": self.work_order_digest,
            "process_version_digest": self.process_version_digest,
            "dependency_root": self.dependency_root,
            "event_chain_head": self.event_chain_head,
            "artifact_root": self.artifact_root,
            "run_id": self.run_id,
            "worker_id": self.worker_id,
            "task_family_id": self.task_family_id,
            "taxonomy_hash": self.taxonomy_hash,
        }

    @classmethod
    def from_run(cls, run_id: str, worker_id: str,
                 worker_version_digest: str = "",
                 work_order_digest: str = "",
                 process_version_digest: str = "",
                 dependency_root: str = "",
                 event_chain_head: str = "",
                 artifact_root: str = "",
                 task_family_id: str = "",
                 taxonomy_hash: str = "") -> "RunCommitment":
        """Create RunCommitment from a completed run's components."""
        return cls(
            worker_version_digest=worker_version_digest,
            work_order_digest=work_order_digest,
            process_version_digest=process_version_digest,
            dependency_root=dependency_root,
            event_chain_head=event_chain_head,
            artifact_root=artifact_root,
            run_id=run_id,
            worker_id=worker_id,
            task_family_id=task_family_id,
            taxonomy_hash=taxonomy_hash,
        )

    def to_attestation_report_data(self, challenge_hash: str = "") -> bytes:
        """Format for dstack attestation reportData.

        reportData = commitment_digest (32 bytes) || challenge_hash (32 bytes)
        """
        digest_bytes = bytes.fromhex(self.compute_digest())
        challenge_bytes = bytes.fromhex(challenge_hash) if challenge_hash else b'\x00' * 32
        return digest_bytes + challenge_bytes
