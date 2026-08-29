"""TEE key management — derived keys, not raw secrets."""
from __future__ import annotations

from dataclasses import dataclass
from tee.dstack import DstackSimulator, DstackKey


@dataclass
class TEESigner:
    """TEE-derived signing identity.

    The TEE signer proves a specific attested workload produced something.
    Separated from agent wallet (which owns funds/permissions).
    """
    app_id: str = ""
    public_key: str = ""
    address: str = ""  # Ethereum address derived from public key
    key_path: str = ""

    @classmethod
    def from_dstack(cls, dstack: DstackSimulator, path: str = "/moltwork/agents/default/receipt-signing") -> "TEESigner":
        """Derive signer from dstack TEE."""
        key = dstack.get_key(path)
        return cls(
            app_id=dstack.app_id,
            public_key=key.public_key,
            address="0x" + key.public_key[:40],  # simplified
            key_path=path,
        )

    def sign(self, message: bytes) -> str:
        """Sign a message with the TEE-derived key.

        In production: actual secp256k1 signing inside TEE.
        Here: deterministic simulation.
        """
        from evidence.canonical import sha256
        return sha256(f"{self.public_key}:{message.hex()}")

    def to_dict(self) -> dict:
        return {
            "appId": self.app_id,
            "publicKey": self.public_key,
            "address": self.address,
            "keyPath": self.key_path,
        }
