"""AttestedWorkReceiptV1 — the canonical object connecting WorkerKit to crypto.

This is the bridge between WorkerKit's evidence layer and Ethereum/TEE.

Not signed. Not authenticated. A content-addressed statement + TEE attestation.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from evidence.canonical import sha256, keccak256, canonical_json
from evidence.commitments import RunCommitment


@dataclass
class TEEInfo:
    """TEE execution environment info."""
    platform: str = "dstack"
    app_id: str = ""
    instance_id: str = ""
    compose_hash: str = ""
    signing_public_key: str = ""
    attestation_digest: str = ""
    attestation_uri: str = ""


@dataclass
class AgentIdentity:
    """ERC-8004 agent identity."""
    chain_id: int = 84532  # Base Sepolia
    identity_registry: str = ""
    agent_id: str = ""


@dataclass
class JobRef:
    """ERC-8183 job reference."""
    protocol: str = "ERC-8183"
    chain_id: int = 84532
    contract: str = ""
    job_id: str = ""


@dataclass
class DelegationRef:
    """ERC-7710 delegation reference."""
    delegation_hash: str = ""
    policy_digest: str = ""
    expires_at: str = ""


@dataclass
class AttestedWorkReceiptV1:
    """The canonical attested work receipt.

    Schema version: moltwork.attested-work-receipt.v1

    Minimum fields for a serious receipt:
    - run ID, work order ID
    - event chain head, event count
    - artifact hashes
    - worker manifest hash
    - policy hash
    - agent ID
    - receipt digest
    - TEE signing public key
    - signature
    - attestation evidence
    """
    schema_version: str = "moltwork.attested-work-receipt.v1"

    # Run
    run_id: str = ""
    work_order_id: str = ""
    worker_manifest_digest: str = ""
    input_commitment: str = ""
    policy_digest: str = ""
    event_chain_head: str = ""
    event_count: int = 0

    # Artifacts
    artifacts: list[dict] = field(default_factory=list)

    # Economics
    known_cost: str = "0"
    currency: str = "USD"

    # Agent identity
    agent: AgentIdentity = field(default_factory=AgentIdentity)

    # Job reference
    job: JobRef = field(default_factory=JobRef)

    # Delegation
    delegation: DelegationRef = field(default_factory=DelegationRef)

    # TEE
    tee: TEEInfo = field(default_factory=TEEInfo)

    # Payments
    payments: list[dict] = field(default_factory=list)

    # Cryptographic binding
    receipt_digest: str = ""
    signature: str = ""

    # Metadata
    created_at: float = field(default_factory=time.time)

    def compute_receipt_digest(self) -> str:
        """Keccak-256 of the canonical receipt (excluding signature)."""
        data = {
            "schemaVersion": self.schema_version,
            "run": {
                "runId": self.run_id,
                "workOrderId": self.work_order_id,
                "workerManifestDigest": self.worker_manifest_digest,
                "inputCommitment": self.input_commitment,
                "policyDigest": self.policy_digest,
                "eventChainHead": self.event_chain_head,
                "eventCount": self.event_count,
            },
            "artifacts": self.artifacts,
            "economics": {"knownCost": self.known_cost, "currency": self.currency},
            "agent": {
                "chainId": self.agent.chain_id,
                "identityRegistry": self.agent.identity_registry,
                "agentId": self.agent.agent_id,
            },
            "job": {
                "protocol": self.job.protocol,
                "chainId": self.job.chain_id,
                "contract": self.job.contract,
                "jobId": self.job.job_id,
            },
            "delegation": {
                "delegationHash": self.delegation.delegation_hash,
                "policyDigest": self.delegation.policy_digest,
                "expiresAt": self.delegation.expires_at,
            },
            "tee": {
                "platform": self.tee.platform,
                "appId": self.tee.app_id,
                "instanceId": self.tee.instance_id,
                "composeHash": self.tee.compose_hash,
                "signingPublicKey": self.tee.signing_public_key,
            },
            "payments": self.payments,
            "createdAt": self.created_at,
        }
        return keccak256(canonical_json(data))

    def to_dict(self) -> dict:
        """Full receipt as dict (for serialization)."""
        self.receipt_digest = self.compute_receipt_digest()
        return {
            "schemaVersion": self.schema_version,
            "run": {
                "runId": self.run_id,
                "workOrderId": self.work_order_id,
                "workerManifestDigest": self.worker_manifest_digest,
                "inputCommitment": self.input_commitment,
                "policyDigest": self.policy_digest,
                "eventChainHead": self.event_chain_head,
                "eventCount": self.event_count,
            },
            "artifacts": self.artifacts,
            "economics": {"knownCost": self.known_cost, "currency": self.currency},
            "agent": {
                "chainId": self.agent.chain_id,
                "identityRegistry": self.agent.identity_registry,
                "agentId": self.agent.agent_id,
            },
            "job": {
                "protocol": self.job.protocol,
                "chainId": self.job.chain_id,
                "contract": self.job.contract,
                "jobId": self.job.job_id,
            },
            "delegation": {
                "delegationHash": self.delegation.delegation_hash,
                "policyDigest": self.delegation.policy_digest,
                "expiresAt": self.delegation.expires_at,
            },
            "tee": {
                "platform": self.tee.platform,
                "appId": self.tee.app_id,
                "instanceId": self.tee.instance_id,
                "composeHash": self.tee.compose_hash,
                "signingPublicKey": self.tee.signing_public_key,
                "attestationDigest": self.tee.attestation_digest,
                "attestationUri": self.tee.attestation_uri,
            },
            "payments": self.payments,
            "receiptDigest": self.receipt_digest,
            "signature": self.signature,
            "createdAt": self.created_at,
        }

    def save(self, path: str):
        """Save receipt to file."""
        import os
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/attested-receipt.json", "w") as f:
            json.dump(self.to_dict(), f, indent=2)


def from_workerkit_receipt(receipt, run, artifacts: list = None,
                           manifest_digest: str = "", policy_digest: str = "",
                           agent_id: str = "", chain_id: int = 84532,
                           identity_registry: str = "",
                           job_contract: str = "", job_id: str = "",
                           delegation_hash: str = "", delegation_expires: str = "",
                           tee_info: TEEInfo | None = None,
                           signing_key: str = "", payments: list | None = None) -> AttestedWorkReceiptV1:
    """Convert a WorkerKit WorkReceipt into AttestedWorkReceiptV1.

    Fills all subsystem fields when provided. Missing fields stay empty.
    """
    att = AttestedWorkReceiptV1()
    att.run_id = receipt.run_id
    att.work_order_id = receipt.work_order_id
    att.event_chain_head = receipt.events_hash.split(":")[0] if ":" in receipt.events_hash else ""
    att.event_count = int(receipt.events_hash.split(":")[1]) if ":" in receipt.events_hash else 0
    att.known_cost = run.known_cost_usd if hasattr(run, "known_cost_usd") else "0"

    # Artifacts
    att.artifacts = [{"sha256": a.get("sha256", ""), "mediaType": a.get("media_type", "")} for a in (artifacts or [])]

    # Worker manifest
    att.worker_manifest_digest = manifest_digest
    att.policy_digest = policy_digest

    # Agent identity (ERC-8004)
    att.agent.chain_id = chain_id
    att.agent.identity_registry = identity_registry
    att.agent.agent_id = agent_id

    # Job (ERC-8183)
    att.job.chain_id = chain_id
    att.job.contract = job_contract
    att.job.job_id = job_id

    # Delegation (ERC-7710)
    att.delegation.delegation_hash = delegation_hash
    att.delegation.policy_digest = policy_digest
    att.delegation.expires_at = delegation_expires

    # TEE
    if tee_info:
        att.tee = tee_info
    att.tee.signing_public_key = signing_key

    # Payments
    att.payments = payments or []

    # Compute receipt digest
    att.receipt_digest = att.compute_receipt_digest()

    return att
