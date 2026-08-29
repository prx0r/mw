"""Encryption — MOCK .af package encryption.

NOT real AES-256-GCM. Uses XOR for demonstration only.
Replace with real AES-256-GCM in production.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any

from core.hashing import sha256


@dataclass
class EncryptedAFPackage:
    """An encrypted .af package (MOCK encryption)."""
    ciphertext: bytes = b""
    nonce: bytes = b""
    aad: str = ""
    dek_digest: str = ""
    scheme: str = "XOR-mock"  # NOT AES-256-GCM

    def to_dict(self) -> dict:
        import base64
        return {
            "ciphertext": base64.b64encode(self.ciphertext).decode(),
            "nonce": base64.b64encode(self.nonce).decode(),
            "aad": self.aad,
            "dek_digest": self.dek_digest,
            "scheme": self.scheme,
        }


class AFArchiver:
    """MOCK encryption for .af packages.

    Uses XOR instead of real AES-256-GCM.
    In production, replace with real AES-256-GCM.
    """

    def encrypt(self, plaintext: bytes, dek: bytes, asset_version_digest: str) -> EncryptedAFPackage:
        """MOCK encrypt — XOR, NOT AES-256-GCM."""
        nonce = os.urandom(12)
        key_stream = hashlib.sha256(dek + nonce).digest()
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, (key_stream * 4)[:len(plaintext)]))
        return EncryptedAFPackage(
            ciphertext=ciphertext, nonce=nonce, aad=asset_version_digest,
            dek_digest=sha256(dek),
        )

    def decrypt(self, package: EncryptedAFPackage, dek: bytes) -> bytes:
        """MOCK decrypt — XOR, NOT AES-256-GCM."""
        key_stream = hashlib.sha256(dek + package.nonce).digest()
        return bytes(a ^ b for a, b in zip(package.ciphertext, (key_stream * 4)[:len(package.ciphertext)]))

    def pack_af(self, af_json: dict, dek: bytes, asset_version_digest: str) -> EncryptedAFPackage:
        plaintext = json.dumps(af_json, sort_keys=True, indent=2).encode()
        return self.encrypt(plaintext, dek, asset_version_digest)

    def unpack_af(self, package: EncryptedAFPackage, dek: bytes) -> dict:
        plaintext = self.decrypt(package, dek)
        return json.loads(plaintext)
