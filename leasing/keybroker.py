"""KeyBroker — HPKE DEK release to TEE.

Releases encryption keys only into attested TEE environments.
Uses X25519 + HPKE (RFC 9180) for recipient-specific key delivery.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Any

from core.hashing import sha256, jcs


@dataclass
class EncryptedPackage:
    """An encrypted .af package ready for TEE release."""
    ciphertext: bytes = b""
    nonce: bytes = b""  # 96-bit nonce for AES-GCM
    aad: str = ""  # additional authenticated data (asset version digest)
    encryption_scheme: str = "AES-256-GCM"
    ciphertext_digest: str = ""  # SHA-256 of ciphertext

    def to_dict(self) -> dict:
        import base64
        return {
            "ciphertext": base64.b64encode(self.ciphertext).decode(),
            "nonce": base64.b64encode(self.nonce).decode(),
            "aad": self.aad,
            "encryption_scheme": self.encryption_scheme,
            "ciphertext_digest": self.ciphertext_digest,
        }


@dataclass
class TEEKeyRequest:
    """Request from TEE for key release."""
    tee_public_key: str = ""  # X25519 public key (hex)
    asset_version_digest: str = ""
    lease_digest: str = ""
    invocation_id: str = ""
    server_nonce: str = ""
    quote_digest: str = ""  # TDX quote digest

    def commitment_hash(self) -> str:
        """Hash of the TEE's commitment for key release."""
        d = {
            "tee_public_key": self.tee_public_key,
            "asset_version_digest": self.asset_version_digest,
            "lease_digest": self.lease_digest,
            "invocation_id": self.invocation_id,
            "server_nonce": self.server_nonce,
            "quote_digest": self.quote_digest,
        }
        return sha256(jcs(d))


@dataclass
class HPKEEncryptedKey:
    """HPKE-encrypted DEK for a specific TEE."""
    encrypted_dek: bytes = b""
    encapsulated_key: bytes = ""  # X25519 ephemeral public key
    algorithm: str = "HPKE(X25519, HKDF-SHA256, AES-256-GCM)"

    def to_dict(self) -> dict:
        import base64
        return {
            "encrypted_dek": base64.b64encode(self.encrypted_dek).decode(),
            "encapsulated_key": base64.b64encode(self.encapsulated_key).decode(),
            "algorithm": self.algorithm,
        }


class KeyBroker:
    """Manages DEK release to attested TEE environments.

    Flow:
    1. TEE generates ephemeral X25519 keypair
    2. TEE includes public key in attested quote
    3. Key broker verifies quote
    4. Key broker encrypts DEK to TEE's public key via HPKE
    5. TEE decrypts DEK
    6. TEE decrypts .af package
    """

    def __init__(self):
        self._deks: dict[str, bytes] = {}  # asset_digest → DEK
        self._released: dict[str, str] = {}  # invocation_id → asset_digest

    def register_dek(self, asset_version_digest: str, dek: bytes) -> None:
        """Register a DEK for an asset version."""
        self._deks[asset_version_digest] = dek

    def generate_dek(self) -> bytes:
        """Generate a random 256-bit DEK."""
        return os.urandom(32)

    def encrypt_package(self, plaintext: bytes, dek: bytes, aad: str) -> EncryptedPackage:
        """Encrypt a .af package with AES-256-GCM.

        In production, use a real crypto library.
        For now, XOR-based mock (NOT real encryption).
        """
        nonce = os.urandom(12)
        # Mock encryption — real implementation uses AES-256-GCM
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, (dek + dek)[:len(plaintext)]))
        return EncryptedPackage(
            ciphertext=ciphertext,
            nonce=nonce,
            aad=aad,
            ciphertext_digest=sha256(ciphertext),
        )

    def decrypt_package(self, package: EncryptedPackage, dek: bytes) -> bytes:
        """Decrypt a .af package.

        In production, use a real crypto library.
        """
        # Mock decryption — real implementation uses AES-256-GCM
        plaintext = bytes(a ^ b for a, b in zip(package.ciphertext, (dek + dek)[:len(package.ciphertext)]))
        return plaintext

    def create_key_request(self, tee_public_key: str, asset_version_digest: str,
                           lease_digest: str = "", invocation_id: str = "",
                           server_nonce: str = "", quote_digest: str = "") -> TEEKeyRequest:
        """Create a key release request from TEE."""
        return TEEKeyRequest(
            tee_public_key=tee_public_key,
            asset_version_digest=asset_version_digest,
            lease_digest=lease_digest,
            invocation_id=invocation_id,
            server_nonce=server_nonce,
            quote_digest=quote_digest,
        )

    def release_key(self, request: TEEKeyRequest, verified: bool = False) -> HPKEEncryptedKey | None:
        """Release DEK to TEE if quote is verified.

        In production, this performs real HPKE encryption.
        """
        if not verified:
            return None

        dek = self._deks.get(request.asset_version_digest)
        if not dek:
            return None

        # Mock HPKE — real implementation uses X25519 + HKDF
        encapsulated_key = bytes.fromhex(request.tee_public_key[:64].ljust(64, "0"))
        encrypted_dek = bytes(a ^ b for a, b in zip(dek, encapsulated_key[:32]))

        self._released[request.invocation_id] = request.asset_version_digest

        return HPKEEncryptedKey(
            encrypted_dek=encrypted_dek,
            encapsulated_key=encapsulated_key[:32],
        )
