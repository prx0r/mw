"""Canonical serialization — re-exports from core.hashing.

SHA-256 for: artifacts, event chains, Docker/OCI, files, in-toto evidence
Keccak-256 for: Ethereum commitments (receipt, delegation, validation)
"""
from __future__ import annotations

from core.hashing import (
    sha256,
    sha256_bytes,
    keccak256,
    keccak256_bytes,
    artifact_digest,
    artifacts_root,
    canonical_bytes,
)


def canonical_json(obj) -> str:
    """Deterministic JSON encoding."""
    import json
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))
