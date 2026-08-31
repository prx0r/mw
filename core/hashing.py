"""Core hashing — RFC 8785 JCS canonicalization + SHA-256.

One way to encode, one way to hash. No competing serializers.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


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


def jcs(obj: Any) -> bytes:
    """RFC 8785 JSON Canonicalization Scheme.

    Deterministic JSON encoding: sorted keys, no whitespace, no trailing commas.
    This is the ONLY way to serialize objects for hashing.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def canonical_hash(obj: Any, prefix: bytes = b"") -> str:
    """Hash a canonicalized object with optional prefix.

    prefix + JCS(obj) → SHA-256 → hex string
    """
    return sha256(prefix + jcs(obj))


def event_hash(schema: str, event: dict) -> str:
    """Hash an event with its schema prefix.

    SHA-256(schema_bytes + 0x00 + JCS(event))
    """
    return sha256(schema.encode() + b"\x00" + jcs(event))


def content_address(data: bytes, prefix: str = "") -> str:
    """Content-address a blob: sha256(prefix + data)."""
    return sha256(prefix.encode() + data)


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


# ─── Artifact helpers ───────────────────────────────────────────────────

def artifact_digest(content: bytes) -> str:
    """SHA-256 of artifact content."""
    return sha256(content)


def artifacts_root(artifacts: list[dict]) -> str:
    """Deterministic root over a list of artifact digests."""
    canonical = json.dumps(artifacts, sort_keys=True, separators=(",", ":"))
    return sha256(canonical)


def canonical_bytes(obj: Any) -> bytes:
    """Canonical encoding as bytes."""
    return jcs(obj)


# ─── Schema prefixes ──────────────────────────────────────────────────

SCHEMA_EVENT = "moltwork:event:v1"
SCHEMA_RECEIPT = "moltwork:receipt:v1"
SCHEMA_AF = "moltwork:af:v1"
SCHEMA_LEASE = "moltwork:lease:v1"
SCHEMA_SNAPSHOT = "moltwork:letta-snapshot:v1"
SCHEMA_RUN_COMMITMENT = "moltwork:run-commitment:v1"
