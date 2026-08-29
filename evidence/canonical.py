"""Canonical serialization — one way to encode, one way to hash.

SHA-256 for: artifacts, event chains, Docker/OCI, files, in-toto evidence
Keccak-256 for: Ethereum commitments (receipt, delegation, validation)
EIP-712 for: typed Ethereum messages
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


# ─── SHA-256 (off-chain, WorkerKit native) ─────────────────────────────

def sha256(data: str | bytes) -> str:
    """Full SHA-256 — 64 hex characters."""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def sha256_bytes(data: str | bytes) -> bytes:
    """SHA-256 as raw 32 bytes."""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).digest()


def artifact_digest(content: bytes) -> str:
    """SHA-256 of artifact content."""
    return sha256(content)


def artifacts_root(artifacts: list[dict]) -> str:
    """Deterministic root over a list of artifact digests.

    Not a Merkle tree for v1 — just a sorted canonical hash.
    """
    canonical = json.dumps(artifacts, sort_keys=True, separators=(",", ":"))
    return sha256(canonical)


# ─── Keccak-256 (on-chain commitments) ─────────────────────────────────

def keccak256(data: str | bytes) -> str:
    """Keccak-256 — 64 hex characters, for Ethereum commitments."""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.new("sha3_256", data).hexdigest()


def keccak256_bytes(data: str | bytes) -> bytes:
    """Keccak-256 as raw 32 bytes."""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.new("sha3_256", data).digest()


# ─── Canonical encoding ─────────────────────────────────────────────────

def canonical_json(obj: Any) -> str:
    """Deterministic JSON encoding."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def canonical_bytes(obj: Any) -> bytes:
    """Canonical encoding as bytes."""
    return canonical_json(obj).encode()
