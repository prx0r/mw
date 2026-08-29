"""ACI receipt integration — dstack Private AI Gateway receipts.

ACI = Attested Confidential Inference.
Standard proof format for individual inference.
MoltworkJobReceipt wraps multiple ACI receipts into a full economic run.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from evidence.canonical import sha256, keccak256, canonical_json


@dataclass
class ACIReceipt:
    """Single ACI inference receipt from dstack Private AI Gateway.

    The gateway publishes workload attestation, verifies the confidential
    inference provider before sending the prompt, and signs request receipts.
    """
    gateway_app_id: str = ""
    provider: str = ""  # tinfoil, near_ai, chutes, secretai, phaladirect, generic
    model: str = ""
    request_hash: str = ""  # SHA-256 of request payload
    response_hash: str = ""  # SHA-256 of response payload
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: str = "0"
    workload_keyset_digest: str = ""
    provider_verification: str = ""  # "VERIFIED" | "PASSTHROUGH"
    signature: str = ""
    timestamp: float = field(default_factory=time.time)

    def receipt_hash(self) -> str:
        """Keccak-256 of the canonical receipt."""
        return keccak256(canonical_json({
            "gatewayAppId": self.gateway_app_id,
            "provider": self.provider,
            "model": self.model,
            "requestHash": self.request_hash,
            "responseHash": self.response_hash,
            "tokensInput": self.tokens_input,
            "tokensOutput": self.tokens_output,
            "costUsd": self.cost_usd,
            "workloadKeysetDigest": self.workload_keyset_digest,
            "providerVerification": self.provider_verification,
            "timestamp": self.timestamp,
        }))

    def to_dict(self) -> dict:
        return {
            "type": "aci_inference",
            "gatewayAppId": self.gateway_app_id,
            "provider": self.provider,
            "model": self.model,
            "requestHash": self.request_hash,
            "responseHash": self.response_hash,
            "tokensInput": self.tokens_input,
            "tokensOutput": self.tokens_output,
            "costUsd": self.cost_usd,
            "workloadKeysetDigest": self.workload_keyset_digest,
            "providerVerification": self.provider_verification,
            "signature": self.signature,
            "receiptHash": self.receipt_hash(),
            "timestamp": self.timestamp,
        }


@dataclass
class HTTPEvidence:
    """HTTP request/response evidence (for non-ACI calls)."""
    method: str = ""
    url: str = ""
    request_hash: str = ""
    response_hash: str = ""
    status_code: int = 0
    cost_usd: str = "0"
    zk_proof: str = ""  # optional TLSNotary/zkFetch proof
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "type": "http",
            "method": self.method,
            "url": self.url,
            "requestHash": self.request_hash,
            "responseHash": self.response_hash,
            "statusCode": self.status_code,
            "costUsd": self.cost_usd,
            "zkProof": self.zk_proof,
            "timestamp": self.timestamp,
        }


@dataclass
class ToolInvocation:
    """ERC-8257 tool invocation evidence."""
    tool_id: str = ""  # ERC-8257 tool registry ID
    tool_name: str = ""
    input_hash: str = ""
    output_hash: str = ""
    cost_usd: str = "0"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "type": "tool",
            "toolId": self.tool_id,
            "toolName": self.tool_name,
            "inputHash": self.input_hash,
            "outputHash": self.output_hash,
            "costUsd": self.cost_usd,
            "timestamp": self.timestamp,
        }


@dataclass
class X402Settlement:
    """x402 payment settlement evidence."""
    protocol: str = "x402"
    chain_id: int = 84532
    asset: str = "USDC"
    amount: str = "0"
    payer: str = ""
    payee: str = ""
    tx_hash: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "type": "x402_settlement",
            "protocol": self.protocol,
            "chainId": self.chain_id,
            "asset": self.asset,
            "amount": self.amount,
            "payer": self.payer,
            "payee": self.payee,
            "txHash": self.tx_hash,
            "timestamp": self.timestamp,
        }
