"""dstack TEE integration — simulator + real interface.

dstack provides:
  info()     — app identity, compose hash
  getKey()   — derive signing keys from TEE
  getQuote() — SGX/TDX quote for attestation
  attest()   — versioned attestation evidence

The guest communicates through /var/run/dstack.sock.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from evidence.canonical import sha256, keccak256


@dataclass
class DstackInfo:
    """App identity from dstack info()."""
    app_id: str = ""
    compose_hash: str = ""
    instance_id: str = ""
    version: str = "0.1.0"


@dataclass
class DstackKey:
    """Derived key from dstack getKey()."""
    public_key: str = ""
    private_key: str = ""  # never exported from TEE
    algorithm: str = "secp256k1"
    path: str = ""


@dataclass
class DstackQuote:
    """SGX/TDX quote from dstack getQuote()."""
    quote: bytes = b""
    report_data: bytes = b""  # 64 bytes: receiptDigest || challengeHash
    version: str = "3.0"


@dataclass
class DstackAttestation:
    """Attestation evidence from dstack attest()."""
    version: str = "1.0"
    quote: DstackQuote = field(default_factory=DstackQuote)
    info: DstackInfo = field(default_factory=DstackInfo)
    signing_key: DstackKey = field(default_factory=DstackKey)
    receipt_digest: str = ""
    challenge: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "info": {
                "appId": self.info.app_id,
                "composeHash": self.info.compose_hash,
                "instanceId": self.info.instance_id,
                "version": self.info.version,
            },
            "signingKey": {
                "publicKey": self.signing_key.public_key,
                "algorithm": self.signing_key.algorithm,
                "path": self.signing_key.path,
            },
            "receiptDigest": self.receipt_digest,
            "challenge": self.challenge,
            "timestamp": self.timestamp,
        }


class DstackSimulator:
    """Simulator for dstack TEE — for development/testing.

    In production, this would call /var/run/dstack.sock.
    """

    def __init__(self, app_id: str = "moltwork-worker-001"):
        self.app_id = app_id
        self.compose_hash = sha256(f"moltwork-worker:{app_id}")
        self.instance_id = sha256(f"instance:{app_id}:{time.time()}")

    def info(self) -> DstackInfo:
        """Get app identity."""
        return DstackInfo(
            app_id=self.app_id,
            compose_hash=self.compose_hash,
            instance_id=self.instance_id,
            version="0.1.0",
        )

    def get_key(self, path: str) -> DstackKey:
        """Derive a key at the given path.

        In production: dstack.getKey() derives keys bound to the attested workload.
        Here: deterministically derive from app_id + path.
        """
        seed = f"{self.app_id}:{path}"
        private_key = sha256(seed)
        # secp256k1 public key derivation (simplified)
        public_key = sha256(f"pub:{private_key}")
        return DstackKey(
            public_key=public_key,
            private_key=private_key,
            algorithm="secp256k1",
            path=path,
        )

    def get_quote(self, report_data: bytes = b"") -> DstackQuote:
        """Get SGX/TDX quote.

        report_data: 64 bytes — receiptDigest (32) || challengeHash (32)
        """
        if not report_data:
            report_data = b"\x00" * 64
        # Simulated quote (in production: actual SGX/TDX quote)
        quote_data = f"{self.app_id}:{report_data.hex()}".encode()
        return DstackQuote(
            quote=hashlib.sha256(quote_data).digest(),
            report_data=report_data[:64].ljust(64, b"\x00"),
            version="3.0",
        )

    def attest(self, receipt_digest: str, challenge: str) -> DstackAttestation:
        """Generate attestation evidence.

        Binds: receipt digest + fresh challenge into report_data.
        """
        rd = bytes.fromhex(receipt_digest) if receipt_digest else b"\x00" * 32
        ch = bytes.fromhex(challenge) if challenge else b"\x00" * 32
        report_data = rd[:32].ljust(32, b"\x00") + ch[:32].ljust(32, b"\x00")

        quote = self.get_quote(report_data)
        key = self.get_key(f"/moltwork/agents/{self.app_id}/receipt-signing")

        return DstackAttestation(
            quote=quote,
            info=self.info(),
            signing_key=key,
            receipt_digest=receipt_digest,
            challenge=challenge,
        )
