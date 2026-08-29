"""ERC-8004 adapter — agent identity / reputation / validation.

Base Sepolia deployments:
  IdentityRegistry: 0x8004A818BFB912233c491871b3d84c89A494BD9e
  ReputationRegistry: 0x8004B663056A597Dffe9eCcC1965A193B7388713
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ERC8004Config:
    """ERC-8004 deployment config."""
    chain_id: int = 84532  # Base Sepolia
    identity_registry: str = "0x8004A818BFB912233c491871b3d84c89A494BD9e"
    reputation_registry: str = "0x8004B663056A597Dffe9eCcC1965A193B7388713"


@dataclass
class IdentityAdapter:
    """ERC-8004 Identity Registry adapter.

    Registers agents with metadata:
    - name, description, services
    - supportedTrust: ["tee-attestation"]
    - moltwork: { workerManifest, attestationEndpoint, receiptSchema }
    """
    config: ERC8004Config = field(default_factory=ERC8004Config)

    def registration_metadata(self, agent_id: str, name: str, manifest_digest: str) -> dict:
        return {
            "name": name,
            "description": f"Moltwork Worker {agent_id}",
            "services": [{"name": "A2A", "endpoint": ""}],
            "supportedTrust": ["tee-attestation"],
            "moltwork": {
                "workerManifest": manifest_digest,
                "attestationEndpoint": "/v1/attest",
                "receiptSchema": "moltwork.attested-work-receipt.v1",
            },
        }


@dataclass
class ValidationAdapter:
    """ERC-8004 Validation Registry adapter.

    TEE oracles are explicitly listed as a validation mechanism.
    """
    config: ERC8004Config = field(default_factory=ERC8004Config)

    def validation_request(self, agent_id: str, receipt_hash: str) -> dict:
        return {
            "agentId": agent_id,
            "requestHash": receipt_hash,
            "validatorType": "tee-attestation",
        }
