"""DSSE — Dead Simple Signing Envelope.

Authenticates both the payload bytes and their payload type.
Does not depend on parsing/canonicalizing the payload.
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.hashing import sha256, jcs


@dataclass
class DSSESignature:
    """One signature over the payload."""
    keyid: str = ""
    sig: str = ""  # base64-encoded signature

    def to_dict(self) -> dict:
        return {"keyid": self.keyid, "sig": self.sig}


@dataclass
class DSSEEnvelope:
    """Dead Simple Signing Envelope.

    payloadType identifies the payload format.
    payload is base64-encoded.
    signatures are over the canonical encoding of payloadType + payload.
    """
    payload_type: str = "application/vnd.in-toto+json"
    payload: bytes = b""
    signatures: list[DSSESignature] = field(default_factory=list)

    def payload_base64(self) -> str:
        return base64.b64encode(self.payload).decode()

    def signable_bytes(self) -> bytes:
        """Bytes that get signed: payloadType || 0x00 || payload."""
        return self.payload_type.encode() + b"\x00" + self.payload

    def signable_hash(self) -> str:
        """SHA-256 of the signable bytes."""
        return sha256(self.signable_bytes())

    def sign(self, keyid: str, sig_bytes: bytes) -> None:
        """Add a signature."""
        self.signatures.append(DSSESignature(
            keyid=keyid,
            sig=base64.b64encode(sig_bytes).decode(),
        ))

    def verify(self, keyid: str, verify_fn: Any) -> bool:
        """Verify a signature using the provided verify function.

        verify_fn(public_key, signable_bytes, sig_bytes) -> bool
        """
        sig = next((s for s in self.signatures if s.keyid == keyid), None)
        if not sig:
            return False
        sig_bytes = base64.b64decode(sig.sig)
        return verify_fn(keyid, self.signable_bytes(), sig_bytes)

    def to_dict(self) -> dict:
        return {
            "payloadType": self.payload_type,
            "payload": self.payload_base64(),
            "signatures": [s.to_dict() for s in self.signatures],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DSSEEnvelope":
        return cls(
            payload_type=d.get("payloadType", ""),
            payload=base64.b64decode(d.get("payload", "")),
            signatures=[DSSESignature(**s) for s in d.get("signatures", [])],
        )

    def save(self, path: str | Path):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "DSSEEnvelope":
        return cls.from_dict(json.loads(Path(path).read_text()))
