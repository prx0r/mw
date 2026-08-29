"""WorkerSigner — MOCK signing identity.

NOT real Ed25519. Uses SHA-256 for demonstration only.
Replace with real Ed25519 from dstack.get_key() in production.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

from core.hashing import sha256, jcs


@dataclass
class SigningKey:
    """A signing key pair (MOCK — not real Ed25519)."""
    key_id: str = ""
    public_key: str = ""  # SHA-256 hash, NOT a real public key
    key_path: str = ""
    algorithm: str = "sha256-mock"  # NOT ed25519
    created_at: float = 0.0

    def to_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "public_key": self.public_key,
            "key_path": self.key_path,
            "algorithm": self.algorithm,
            "created_at": self.created_at,
        }


class WorkerSigner:
    """MOCK signing identity for demonstration.

    Uses SHA-256 instead of real Ed25519.
    In production, replace with dstack.get_key().sign().
    """

    def __init__(self):
        self._keys: dict[str, SigningKey] = {}

    def derive_key(self, worker_id: str, key_path: str = "") -> SigningKey:
        """Derive a MOCK signing key for a worker."""
        path = key_path or f"/moltwork/worker/{worker_id}/receipt/v1"
        key_hash = sha256(path.encode())
        public_key = sha256(f"pub:{key_hash}".encode())

        key = SigningKey(
            key_id=f"key-{worker_id[:16]}",
            public_key=public_key,
            key_path=path,
            algorithm="sha256-mock",
            created_at=time.time(),
        )
        self._keys[worker_id] = key
        return key

    def get_key(self, worker_id: str) -> SigningKey | None:
        return self._keys.get(worker_id)

    def sign(self, worker_id: str, data: bytes) -> str | None:
        """MOCK sign — returns SHA-256, NOT a real signature."""
        key = self._keys.get(worker_id)
        if not key:
            return None
        return sha256(key.public_key.encode() + data)

    def export_identity(self, worker_id: str) -> dict | None:
        key = self._keys.get(worker_id)
        if not key:
            return None
        return key.to_dict()
