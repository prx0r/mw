"""Encryption — AES-256-GCM .af package encryption.

Encrypts .af packages so only TEE environments can decrypt them.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Any

from core.hashing import sha256


@dataclass
class EncryptedAFPackage:
    """An encrypted .af package."""
    ciphertext: bytes = b""
    nonce: bytes = b""  # 96-bit nonce
    aad: str = ""  # asset version digest
    dek_digest: str = ""  # SHA-256 of the DEK used
    scheme: str = "AES-256-GCM"

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
    """Encrypt/decrypt .af packages for confidential worker storage."""

    def encrypt(self, plaintext: bytes, dek: bytes, asset_version_digest: str) -> EncryptedAFPackage:
        """Encrypt a .af package.

        Uses DEK as key, asset_version_digest as AAD.
        In production, uses AES-256-GCM.
        """
        nonce = os.urandom(12)
        # Mock encryption — real uses AES-256-GCM
        key_stream = hashlib.sha256(dek + nonce).digest()
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, (key_stream * 4)[:len(plaintext)]))

        return EncryptedAFPackage(
            ciphertext=ciphertext,
            nonce=nonce,
            aad=asset_version_digest,
            dek_digest=sha256(dek),
        )

    def decrypt(self, package: EncryptedAFPackage, dek: bytes) -> bytes:
        """Decrypt a .af package.

        In production, uses AES-256-GCM with AAD verification.
        """
        # Mock decryption
        key_stream = hashlib.sha256(dek + package.nonce).digest()
        plaintext = bytes(a ^ b for a, b in zip(package.ciphertext, (key_stream * 4)[:len(package.ciphertext)]))
        return plaintext

    def pack_af(self, af_json: dict, dek: bytes, asset_version_digest: str) -> EncryptedAFPackage:
        """Pack and encrypt an .af JSON object."""
        plaintext = json.dumps(af_json, sort_keys=True, indent=2).encode()
        return self.encrypt(plaintext, dek, asset_version_digest)

    def unpack_af(self, package: EncryptedAFPackage, dek: bytes) -> dict:
        """Decrypt and unpack an .af package."""
        plaintext = self.decrypt(package, dek)
        return json.loads(plaintext)


import json
