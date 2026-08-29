"""dstack Quote — TDX quote commitment for run attestation.

Binds a specific run to a TEE execution environment.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from core.hashing import sha256, jcs, SCHEMA_RUN_COMMITMENT


@dataclass
class QuoteCommitment:
    """The object attested inside a TDX quote.

    Proves: this version of this Worker, performing this task with these
    dependencies, committed to this output/run history inside this attested
    environment.
    """
    schema: str = SCHEMA_RUN_COMMITMENT
    run_id: str = ""
    worker_id: str = ""

    # What gets committed
    worker_version_digest: str = ""
    work_order_digest: str = ""
    process_version_digest: str = ""
    dependency_root: str = ""
    event_chain_head: str = ""
    artifact_root: str = ""
    memory_before_digest: str = ""
    memory_after_digest: str = ""

    # Taxonomy
    task_family_id: str = ""
    taxonomy_hash: str = ""

    # TEE context
    server_nonce: str = ""
    receipt_pubkey: str = ""

    def compute_digest(self) -> str:
        """Compute the commitment digest. This is what gets attested."""
        d = {
            "schema": self.schema,
            "run_id": self.run_id,
            "worker_id": self.worker_id,
            "worker_version_digest": self.worker_version_digest,
            "work_order_digest": self.work_order_digest,
            "process_version_digest": self.process_version_digest,
            "dependency_root": self.dependency_root,
            "event_chain_head": self.event_chain_head,
            "artifact_root": self.artifact_root,
            "memory_before_digest": self.memory_before_digest,
            "memory_after_digest": self.memory_after_digest,
            "task_family_id": self.task_family_id,
            "taxonomy_hash": self.taxonomy_hash,
            "server_nonce": self.server_nonce,
            "receipt_pubkey": self.receipt_pubkey,
        }
        return sha256(jcs(d))

    def to_report_data(self, challenge_hash: str = "") -> bytes:
        """Format for TDX reportData.

        reportData = commitment_digest (32 bytes) || challenge_hash (32 bytes)
        """
        digest_bytes = bytes.fromhex(self.compute_digest())
        challenge_bytes = bytes.fromhex(challenge_hash) if challenge_hash else b'\x00' * 32
        return digest_bytes + challenge_bytes

    def to_dict(self) -> dict:
        d = {
            "schema": self.schema,
            "run_id": self.run_id,
            "worker_id": self.worker_id,
            "worker_version_digest": self.worker_version_digest,
            "work_order_digest": self.work_order_digest,
            "process_version_digest": self.process_version_digest,
            "dependency_root": self.dependency_root,
            "event_chain_head": self.event_chain_head,
            "artifact_root": self.artifact_root,
            "memory_before_digest": self.memory_before_digest,
            "memory_after_digest": self.memory_after_digest,
            "task_family_id": self.task_family_id,
            "taxonomy_hash": self.taxonomy_hash,
            "server_nonce": self.server_nonce,
            "receipt_pubkey": self.receipt_pubkey,
        }
        d["commitment_digest"] = self.compute_digest()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "QuoteCommitment":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})
