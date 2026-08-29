"""ERC-8004 adapter — Base Sepolia, web3 when available.

Deployments:
  IdentityRegistry:   0x8004A818BFB912233c491871b3d84c89A494BD9e
  ReputationRegistry: 0x8004B663056A597Dffe9eCcC1965A193B7388713
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

try:
    from web3 import Web3  # type: ignore

    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False
    Web3 = None  # type: ignore

# Minimal ABI fragments we actually need
IDENTITY_ABI = [
    {"inputs": [{"name": "agentId", "type": "uint256"}], "name": "getAgent", "outputs": [{"type": "tuple", "components": [{"name": "owner", "type": "address"}, {"name": "uri", "type": "string"}]}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "uri", "type": "string"}], "name": "register", "outputs": [{"name": "agentId", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
]
REPUTATION_ABI = [
    {"inputs": [{"name": "agentId", "type": "uint256"}, {"name": "score", "type": "int256"}, {"name": "uri", "type": "string"}], "name": "giveFeedback", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
]


@dataclass
class ERC8004Config:
    chain_id: int = 84532
    identity_registry: str = "0x8004A818BFB912233c491871b3d84c89A494BD9e"
    reputation_registry: str = "0x8004B663056A597Dffe9eCcC1965A193B7388713"
    rpc_url: str = field(default_factory=lambda: os.environ.get("BASE_SEPOLIA_RPC", "https://sepolia.base.org"))


@dataclass
class IdentityAdapter:
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

    def _w3(self):
        if not HAS_WEB3:
            raise RuntimeError("web3 not installed: pip install web3")
        return Web3(Web3.HTTPProvider(self.config.rpc_url))

    def get_agent(self, agent_id: int) -> dict | None:
        """Read agent from IdentityRegistry. Returns None if not found or no RPC."""
        if not HAS_WEB3:
            return None
        try:
            w3 = self._w3()
            c = w3.eth.contract(address=self.config.identity_registry, abi=IDENTITY_ABI)
            owner, uri = c.functions.getAgent(agent_id).call()
            return {"agentId": agent_id, "owner": owner, "uri": uri}
        except Exception:
            return None

    def register(self, private_key: str, uri: str) -> dict:
        """Register agent on-chain. Requires funded private key."""
        w3 = self._w3()
        acct = w3.eth.account.from_key(private_key)
        c = w3.eth.contract(address=self.config.identity_registry, abi=IDENTITY_ABI)
        tx = c.functions.register(uri).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 300000, "maxFeePerGas": w3.to_wei("0.01", "gwei"),
            "maxPriorityFeePerGas": w3.to_wei("0.001", "gwei"),
            "chainId": self.config.chain_id,
        })
        signed = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        return {"txHash": tx_hash.hex(), "from": acct.address}


@dataclass
class ValidationAdapter:
    config: ERC8004Config = field(default_factory=ERC8004Config)

    def validation_request(self, agent_id: str, receipt_hash: str) -> dict:
        return {"agentId": agent_id, "requestHash": receipt_hash, "validatorType": "tee-attestation"}
