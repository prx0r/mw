"""dstack TEE integration — production-grade, simulator-aware.

Uses real dstack-sdk when running inside TEE (socket at /var/run/dstack.sock).
Falls back to deterministic derivation outside TEE (dev/test).
Never silently substitutes — caller knows which mode is active.

Real SDK: DstackClientV1.get_key(domain, algorithm) / attest(report_data) / info()
Simulator: DSTACK_SIMULATOR_ENDPOINT env var (see reference/dstack/sdk/python)
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field

from evidence.canonical import sha256

try:
    from dstack_sdk import DstackClient  # type: ignore

    HAS_DSTACK_SDK = True
except ImportError:
    HAS_DSTACK_SDK = False
    DstackClient = None  # type: ignore


# ─── Public types (same shape whether real or simulated) ────────────────


@dataclass
class DstackInfo:
    app_id: str = ""
    compose_hash: str = ""
    instance_id: str = ""
    version: str = "0.1.0"
    is_simulated: bool = True


@dataclass
class DstackKey:
    public_key: str = ""
    signature_chain: list[str] = field(default_factory=list)
    algorithm: str = "secp256k1"
    path: str = ""
    is_simulated: bool = True
    private_key: str = ""  # simulator only, never exported from real TEE


@dataclass
class DstackQuote:
    quote: bytes = b""
    report_data: bytes = b""
    version: str = "3.0"
    is_simulated: bool = True


@dataclass
class DstackAttestation:
    version: str = "1.0"
    quote: DstackQuote = field(default_factory=DstackQuote)
    info: DstackInfo = field(default_factory=DstackInfo)
    signing_key: DstackKey = field(default_factory=DstackKey)
    receipt_digest: str = ""
    challenge: str = ""
    attestation_hex: str = ""  # raw attestation blob (real TEE) or empty (sim)
    timestamp: float = field(default_factory=time.time)
    is_simulated: bool = True

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "info": {
                "appId": self.info.app_id,
                "composeHash": self.info.compose_hash,
                "instanceId": self.info.instance_id,
                "version": self.info.version,
                "simulated": self.info.is_simulated,
            },
            "signingKey": {
                "publicKey": self.signing_key.public_key,
                "algorithm": self.signing_key.algorithm,
                "path": self.signing_key.path,
                "simulated": self.signing_key.is_simulated,
            },
            "receiptDigest": self.receipt_digest,
            "challenge": self.challenge,
            "attestationHex": self.attestation_hex[:32] + "..." if self.attestation_hex else "",
            "timestamp": self.timestamp,
            "simulated": self.is_simulated,
        }


# ─── Real client (inside TEE) ───────────────────────────────────────────


class RealDstackClient:
    """Wraps DstackClientV1 — only works inside a dstack CVM."""

    def __init__(self, endpoint: str | None = None):
        if not HAS_DSTACK_SDK:
            raise RuntimeError("dstack-sdk not installed: pip install dstack-sdk")
        self._client = DstackClient(endpoint=endpoint)

    def info(self) -> DstackInfo:
        r = self._client.info()
        return DstackInfo(
            app_id=r.app_id.hex() if isinstance(r.app_id, bytes) else str(r.app_id),
            compose_hash=r.compose_hash.hex() if isinstance(r.compose_hash, bytes) else str(r.compose_hash),
            instance_id=r.instance_id.hex() if isinstance(r.instance_id, bytes) else str(r.instance_id),
            version="0.1.0",
            is_simulated=False,
        )

    def get_key(self, domain: str, algorithm: str = "secp256k1") -> DstackKey:
        r = self._client.get_key(domain, algorithm)
        pub = r.public_key.hex() if isinstance(r.public_key, bytes) else str(r.public_key)
        chain = [c.hex() if isinstance(c, bytes) else str(c) for c in r.signature_chain]
        return DstackKey(
            public_key=pub,
            signature_chain=chain,
            algorithm=algorithm,
            path=domain,
            is_simulated=False,
        )

    def attest(self, report_data: bytes) -> tuple[bytes, str]:
        """Returns (attestation_hex, quote_hex). report_data must be <=64 bytes."""
        if len(report_data) > 64:
            raise ValueError(f"report_data must be <=64 bytes, got {len(report_data)}")
        if len(report_data) == 0:
            raise ValueError("report_data must not be empty")
        r = self._client.attest(report_data)
        att_hex = r.attestation.hex() if isinstance(r.attestation, bytes) else str(r.attestation)
        return r.attestation if isinstance(r.attestation, bytes) else bytes.fromhex(att_hex), att_hex

    def close(self):
        try:
            self._client.close()
        except Exception:
            pass


# ─── Simulator (outside TEE) ────────────────────────────────────────────


class DstackSimulator:
    """Deterministic simulator — for dev/test outside TEE.

    Key derivation is NOT cryptographically equivalent to real TEE.
    Signatures from simulator must never be treated as TEE-verified (E3).
    """

    def __init__(self, app_id: str = "moltwork-worker-001"):
        self.app_id = app_id
        self.compose_hash = sha256(f"moltwork-worker:{app_id}")
        self.instance_id = sha256(f"instance:{app_id}:{time.time()}")

    def info(self) -> DstackInfo:
        return DstackInfo(
            app_id=self.app_id,
            compose_hash=self.compose_hash,
            instance_id=self.instance_id,
            version="0.1.0",
            is_simulated=True,
        )

    def get_key(self, domain: str, algorithm: str = "secp256k1") -> DstackKey:
        seed = f"{self.app_id}:{domain}:{algorithm}"
        # Use domain+algorithm binding like real v1 KDF (not just domain)
        private_key = sha256(seed)
        public_key = sha256(f"pub:{private_key}:{algorithm}")
        return DstackKey(
            public_key=public_key,
            private_key=private_key,  # type: ignore  # simulator only
            algorithm=algorithm,
            path=domain,
            is_simulated=True,
        )

    def get_quote(self, report_data: bytes = b"") -> DstackQuote:
        if not report_data:
            report_data = b"\x00" * 64
        quote_data = f"{self.app_id}:{report_data.hex()}".encode()
        return DstackQuote(
            quote=hashlib.sha256(quote_data).digest(),
            report_data=report_data[:64].ljust(64, b"\x00"),
            version="3.0",
            is_simulated=True,
        )

    def attest(self, receipt_digest: str, challenge: str) -> DstackAttestation:
        rd = bytes.fromhex(receipt_digest) if receipt_digest else b"\x00" * 32
        ch = bytes.fromhex(challenge) if challenge else b"\x00" * 32
        report_data = rd[:32].ljust(32, b"\x00") + ch[:32].ljust(32, b"\x00")
        quote = self.get_quote(report_data)
        key = self.get_key(f"/moltwork/agents/{self.app_id}/receipt-signing", "secp256k1")
        return DstackAttestation(
            quote=quote,
            info=self.info(),
            signing_key=key,
            receipt_digest=receipt_digest,
            challenge=challenge,
            attestation_hex=quote.quote.hex(),
            is_simulated=True,
        )


# ─── Auto-detecting client ──────────────────────────────────────────────


def is_inside_tee() -> bool:
    """True if running inside a dstack CVM (socket exists or simulator endpoint set)."""
    if os.environ.get("DSTACK_SIMULATOR_ENDPOINT"):
        return True
    for path in ["/var/run/dstack.sock", "/run/dstack.sock"]:
        if os.path.exists(path):
            return True
    return False


def get_dstack_client(app_id: str = "moltwork-worker-001"):
    """Returns RealDstackClient if inside TEE, else DstackSimulator.

    Caller can check .is_simulated on returned objects to enforce policy
    (e.g., never treat simulator signatures as E3_TEE_VERIFIED).
    """
    if is_inside_tee() and HAS_DSTACK_SDK:
        try:
            c = RealDstackClient()
            # Probe with info() to confirm socket actually works
            c.info()
            return c
        except Exception:
            pass
    return DstackSimulator(app_id=app_id)
