"""KMS auth — conditional key release via dstack AppAuth.

dstack KMS runs in its own TEE, verifies workloads before releasing keys.
Can enforce authorization using smart contracts (auth-eth).

Guarantee:
  agent private key
    X operator cannot obtain it
    X modified WorkerKit cannot obtain it
    X unapproved container cannot obtain it
    → ONLY approved measured Moltwork workload
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from evidence.canonical import sha256, canonical_json


@dataclass
class KMSAuthPolicy:
    """Policy for conditional key release."""
    agent_id: str = ""
    permitted_workloads: list[str] = field(default_factory=list)  # approved workload hashes
    permitted_compose_hashes: list[str] = field(default_factory=list)
    permitted_image_digests: list[str] = field(default_factory=list)
    max_key_age_seconds: float = 3600.0  # keys expire after 1 hour
    require_fresh_attestation: bool = True

    def is_workload_approved(self, workload_id: str) -> bool:
        if not self.permitted_workloads:
            return True  # no restriction
        return workload_id in self.permitted_workloads

    def is_compose_approved(self, compose_hash: str) -> bool:
        if not self.permitted_compose_hashes:
            return True
        return compose_hash in self.permitted_compose_hashes

    def to_dict(self) -> dict:
        return {
            "agentId": self.agent_id,
            "permittedWorkloads": self.permitted_workloads,
            "permittedComposeHashes": self.permitted_compose_hashes,
            "permittedImageDigests": self.permitted_image_digests,
            "maxKeyAgeSeconds": self.max_key_age_seconds,
            "requireFreshAttestation": self.require_fresh_attestation,
        }


@dataclass
class KeyReleaseRequest:
    """Request to dstack KMS for key release."""
    agent_id: str = ""
    workload_id: str = ""
    compose_hash: str = ""
    key_domain: str = ""  # /moltwork/v1/agent/evm, etc.
    attestation_hash: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "agentId": self.agent_id,
            "workloadId": self.workload_id,
            "composeHash": self.compose_hash,
            "keyDomain": self.key_domain,
            "attestationHash": self.attestation_hash,
            "timestamp": self.timestamp,
        }


@dataclass
class KeyReleaseResponse:
    """Response from dstack KMS."""
    approved: bool = False
    public_key: str = ""
    signature_chain: list[str] = field(default_factory=list)
    expires_at: float = 0.0
    rejection_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "approved": self.approved,
            "publicKey": self.public_key,
            "signatureChain": self.signature_chain,
            "expiresAt": self.expires_at,
            "rejectionReason": self.rejection_reason,
        }


class KMSAuthorizer:
    """Authorizes key release based on policy + attestation.

    In production: calls dstack KMS API.
    Here: local verification against policy.
    """

    def __init__(self, policy: KMSAuthPolicy):
        self.policy = policy
        self._release_log: list[dict] = []

    def authorize(self, request: KeyReleaseRequest) -> KeyReleaseResponse:
        """Check if key release is authorized."""
        # Check workload approval
        if not self.policy.is_workload_approved(request.workload_id):
            return KeyReleaseResponse(
                approved=False,
                rejection_reason=f"workload {request.workload_id[:16]}... not in permitted list",
            )

        # Check compose hash
        if not self.policy.is_compose_approved(request.compose_hash):
            return KeyReleaseResponse(
                approved=False,
                rejection_reason=f"compose {request.compose_hash[:16]}... not approved",
            )

        # Check freshness
        if self.policy.require_fresh_attestation and not request.attestation_hash:
            return KeyReleaseResponse(
                approved=False,
                rejection_reason="fresh attestation required but not provided",
            )

        # Approved — derive key (in production: dstack KMS does this)
        public_key = sha256(f"kms:{request.agent_id}:{request.key_domain}:{request.workload_id}")
        expires_at = time.time() + self.policy.max_key_age_seconds

        response = KeyReleaseResponse(
            approved=True,
            public_key=public_key,
            signature_chain=[request.attestation_hash, request.workload_id],
            expires_at=expires_at,
        )

        # Log release
        self._release_log.append({
            "request": request.to_dict(),
            "response": response.to_dict(),
            "timestamp": time.time(),
        })

        return response

    def get_release_log(self) -> list[dict]:
        return self._release_log
