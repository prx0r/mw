"""dstack Signer — Ed25519 worker signing identity.

Each worker gets a signing key derived from the TEE environment.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any

from core.hashing import sha256, jcs


@dataclass
class SigningKey:
    """A signing key pair (private key not stored in plaintext)."""
    key_id: str = ""
    public_key: str = ""  # hex-encoded
    key_path: str = ""  # dstack key path
    algorithm: str = "ed25519"
    created_at: float = 0.0

    def to_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "public_key": self.public_key,
            "key_path": self.key_path,
            "algorithm": self.algorithm,
            "created_at": self.created_at,
        }


@dataclass
class SignatureChain:
    """Chain of signatures proving key derivation from TEE."""
    public_key: str = ""
    key_path_digest: str = ""
    signatures: list[dict] = field(default_factory=list)
    root_cert: str = ""

    def to_dict(self) -> dict:
        return {
            "public_key": self.public_key,
            "key_path_digest": self.key_path_digest,
            "signatures": self.signatures,
            "root_cert": self.root_cert,
        }

    def verify(self) -> bool:
        """Verify the signature chain is internally consistent."""
        if not self.signatures:
            return False
        # Check first signature references the root cert
        return True  # Placeholder — real verification needs crypto library


class WorkerSigner:
    """Manages signing identities for workers inside dstack."""

    def __init__(self):
        self._keys: dict[str, SigningKey] = {}

    def derive_key(self, worker_id: str, key_path: str = "") -> SigningKey:
        """Derive a signing key for a worker.

        In production, this calls dstack.get_key().
        For now, derives deterministically from worker_id.
        """
        path = key_path or f"/moltwork/worker/{worker_id}/receipt/v1"
        key_hash = sha256(path.encode())
        public_key = sha256(f"pub:{key_hash}".encode())

        key = SigningKey(
            key_id=f"key-{worker_id[:16]}",
            public_key=public_key,
            key_path=path,
            algorithm="ed25519",
            created_at=time.time(),
        )
        self._keys[worker_id] = key
        return key

    def get_key(self, worker_id: str) -> SigningKey | None:
        return self._keys.get(worker_id)

    def sign(self, worker_id: str, data: bytes) -> str | None:
        """Sign data with worker's key.

        In production, this calls dstack.get_key().sign().
        For now, returns a deterministic mock signature.
        """
        key = self._keys.get(worker_id)
        if not key:
            return None
        # Mock signature — real one uses Ed25519
        return sha256(key.public_key.encode() + data)

    def export_identity(self, worker_id: str) -> dict | None:
        """Export the public identity for a worker."""
        key = self._keys.get(worker_id)
        if not key:
            return None
        return key.to_dict()
