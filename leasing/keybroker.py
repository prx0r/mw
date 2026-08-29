"""KeyBroker — MOCK HPKE DEK release.

NOT real HPKE/X25519. Uses XOR for demonstration only.
Replace with real HPKE (RFC 9180) in production.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Any

from core.hashing import sha256, jcs


@dataclass
class EncryptedPackage:
    """An encrypted .af package (MOCK encryption)."""
    ciphertext: bytes = b""
    nonce: bytes = b""
    aad: str = ""
    encryption_scheme: str = "XOR-mock"  # NOT AES-256-GCM

    def to_dict(self) -> dict:
        import base64
        return {
            "ciphertext": base64.b64encode(self.ciphertext).decode(),
            "nonce": base64.b64encode(self.nonce).decode(),
            "aad": self.aad,
            "encryption_scheme": self.encryption_scheme,
        }


@dataclass
class TEEKeyRequest:
    """Request from TEE for key release."""
    tee_public_key: str = ""
    asset_version_digest: str = ""
    invocation_id: str = ""

    def commitment_hash(self) -> str:
        d = {
            "tee_public_key": self.tee_public_key,
            "asset_version_digest": self.asset_version_digest,
            "invocation_id": self.invocation_id,
        }
        return sha256(jcs(d))


@dataclass
class HPKEEncryptedKey:
    """MOCK HPKE-encrypted DEK. NOT real HPKE."""
    encrypted_dek: bytes = b""
    encapsulated_key: bytes = b""
    algorithm: str = "XOR-mock"  # NOT HPKE(X25519, HKDF-SHA256, AES-256-GCM)

    def to_dict(self) -> dict:
        import base64
        return {
            "encrypted_dek": base64.b64encode(self.encrypted_dek).decode(),
            "encapsulated_key": base64.b64encode(self.encapsulated_key).decode(),
            "algorithm": self.algorithm,
        }


class KeyBroker:
    """MOCK key broker for demonstration.

    Uses XOR instead of real HPKE/X25519.
    In production, replace with real HPKE (RFC 9180).
    """

    def __init__(self):
        self._deks: dict[str, bytes] = {}
        self._released: dict[str, str] = {}

    def register_dek(self, asset_version_digest: str, dek: bytes) -> None:
        self._deks[asset_version_digest] = dek

    def generate_dek(self) -> bytes:
        return os.urandom(32)

    def encrypt_package(self, plaintext: bytes, dek: bytes, aad: str) -> EncryptedPackage:
        """MOCK encrypt — XOR, NOT AES-256-GCM."""
        nonce = os.urandom(12)
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, (dek + dek)[:len(plaintext)]))
        return EncryptedPackage(ciphertext=ciphertext, nonce=nonce, aad=aad)

    def decrypt_package(self, package: EncryptedPackage, dek: bytes) -> bytes:
        """MOCK decrypt — XOR, NOT AES-256-GCM."""
        return bytes(a ^ b for a, b in zip(package.ciphertext, (dek + dek)[:len(package.ciphertext)]))

    def create_key_request(self, tee_public_key: str, asset_version_digest: str,
                           invocation_id: str = "") -> TEEKeyRequest:
        return TEEKeyRequest(
            tee_public_key=tee_public_key,
            asset_version_digest=asset_version_digest,
            invocation_id=invocation_id,
        )

    def release_key(self, request: TEEKeyRequest, verified: bool = False) -> HPKEEncryptedKey | None:
        """MOCK key release — XOR, NOT real HPKE."""
        if not verified:
            return None
        dek = self._deks.get(request.asset_version_digest)
        if not dek:
            return None
        encapsulated_key = bytes.fromhex(request.tee_public_key[:64].ljust(64, "0"))
        encrypted_dek = bytes(a ^ b for a, b in zip(dek, encapsulated_key[:32]))
        self._released[request.invocation_id] = request.asset_version_digest
        return HPKEEncryptedKey(encrypted_dek=encrypted_dek, encapsulated_key=encapsulated_key[:32])
