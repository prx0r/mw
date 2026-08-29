"""Attested Agent Keys — explicit key domains, never one key for everything.

dstack derives private keys bound to the application identity.
Signature chain proves key was derived through TEE-backed KMS.

Key domains:
  /moltwork/v1/agent/evm     — Ethereum transaction signing
  /moltwork/v1/receipts      — receipt signing
  /moltwork/v1/checkpoints   — evidence log checkpoints
  /moltwork/v1/oracle        — oracle observations
"""
from __future__ import annotations

from dataclasses import dataclass
from evidence.canonical import sha256


# Key domain paths
KEY_DOMAIN_EVM = "/moltwork/v1/agent/evm"
KEY_DOMAIN_RECEIPTS = "/moltwork/v1/receipts"
KEY_DOMAIN_CHECKPOINTS = "/moltwork/v1/checkpoints"
KEY_DOMAIN_ORACLE = "/moltwork/v1/oracle"

ALL_KEY_DOMAINS = [KEY_DOMAIN_EVM, KEY_DOMAIN_RECEIPTS, KEY_DOMAIN_CHECKPOINTS, KEY_DOMAIN_ORACLE]


@dataclass
class AttestedKey:
    """A TEE-derived key bound to a specific domain."""
    domain: str = ""
    public_key: str = ""
    signature_chain: list[str] = None  # proves derivation through TEE KMS

    def __post_init__(self):
        if self.signature_chain is None:
            self.signature_chain = []

    def sign(self, message: bytes) -> str:
        """Sign with this domain-specific key."""
        return sha256(f"{self.public_key}:{message.hex()}")

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "publicKey": self.public_key,
            "signatureChain": self.signature_chain,
        }


@dataclass
class AgentKeyBundle:
    """All domain keys for an agent workload.

    Never export private keys. Public keys + signature chains only.
    """
    agent_id: str = ""
    workload_id: str = ""
    keys: dict[str, AttestedKey] = None  # domain → AttestedKey

    def __post_init__(self):
        if self.keys is None:
            self.keys = {}

    @classmethod
    def derive(cls, agent_id: str, workload_id: str, key_fn) -> "AgentKeyBundle":
        """Derive all domain keys from a TEE key derivation function.

        key_fn(domain) → (public_key, signature_chain)
        """
        bundle = cls(agent_id=agent_id, workload_id=workload_id)
        for domain in ALL_KEY_DOMAINS:
            pub, chain = key_fn(domain)
            bundle.keys[domain] = AttestedKey(domain=domain, public_key=pub, signature_chain=chain)
        return bundle

    def get(self, domain: str) -> AttestedKey | None:
        return self.keys.get(domain)

    def to_dict(self) -> dict:
        return {
            "agentId": self.agent_id,
            "workloadId": self.workload_id,
            "keys": {d: k.to_dict() for d, k in self.keys.items()},
        }
