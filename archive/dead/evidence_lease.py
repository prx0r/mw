"""AgentLease — cryptographically restricted authority.

Compile high-level agent permission language into ERC-7710 delegations.
Owner signs the lease. TEE signer becomes delegate.
Worker can autonomously act within exactly those limits.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from evidence.canonical import sha256, keccak256, canonical_json


@dataclass
class LeasePermissions:
    """High-level agent permissions."""
    # x402 spending
    x402_max_total_usd: str = "5.00"
    x402_max_request_usd: str = "0.25"

    # Contract interactions
    allowed_targets: list[str] = field(default_factory=list)
    allowed_methods: list[str] = field(default_factory=list)

    # Job categories
    allowed_job_categories: list[str] = field(default_factory=list)

    # TEE requirement
    required_tee_workload: str = ""  # hex workload ID

    # Time bounds
    valid_after: float = 0.0
    valid_until: float = 0.0

    # Call limits
    max_total_calls: int = 1000

    def to_dict(self) -> dict:
        return {
            "x402MaxTotalUsd": self.x402_max_total_usd,
            "x402MaxRequestUsd": self.x402_max_request_usd,
            "allowedTargets": self.allowed_targets,
            "allowedMethods": self.allowed_methods,
            "allowedJobCategories": self.allowed_job_categories,
            "requiredTeeWorkload": self.required_tee_workload,
            "validAfter": self.valid_after,
            "validUntil": self.valid_until,
            "maxTotalCalls": self.max_total_calls,
        }


@dataclass
class AgentLeaseV1:
    """Cryptographically restricted agent authority.

    Schema: moltwork.agent-lease.v1

    Owner signs this. Delegate (TEE signer) can act within limits.
    """
    schema_version: str = "moltwork.agent-lease.v1"

    lease_id: str = ""
    agent_id: str = ""
    owner: str = ""  # owner address
    delegate: str = ""  # TEE signer address

    permissions: LeasePermissions = field(default_factory=LeasePermissions)

    # Revocation
    revocation_epoch: int = 0
    nonce: int = 0

    # Signing
    owner_signature: str = ""

    created_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        if self.permissions.valid_until <= 0:
            return False
        return time.time() > self.permissions.valid_until

    def lease_digest(self) -> str:
        """Keccak-256 of canonical lease."""
        return keccak256(canonical_json({
            "schemaVersion": self.schema_version,
            "leaseId": self.lease_id,
            "agentId": self.agent_id,
            "owner": self.owner,
            "delegate": self.delegate,
            "permissions": self.permissions.to_dict(),
            "revocationEpoch": self.revocation_epoch,
            "nonce": self.nonce,
            "createdAt": self.created_at,
        }))

    def compile_to_erc7710(self) -> dict:
        """Compile lease into ERC-7710 delegation with CaveatEnforcers."""
        caveats = []

        # Allowed targets
        if self.permissions.allowed_targets:
            caveats.append({
                "enforcer": "AllowedTargetsEnforcer",
                "terms": ",".join(self.permissions.allowed_targets),
            })

        # Allowed methods
        if self.permissions.allowed_methods:
            caveats.append({
                "enforcer": "AllowedMethodsEnforcer",
                "terms": ",".join(self.permissions.allowed_methods),
            })

        # Spending limit (x402 max total)
        caveats.append({
            "enforcer": "ERC20TransferAmountEnforcer",
            "terms": self.permissions.x402_max_total_usd,
        })

        # Call limit
        if self.permissions.max_total_calls < 10000:
            caveats.append({
                "enforcer": "LimitedCallsEnforcer",
                "terms": str(self.permissions.max_total_calls),
            })

        # Time bounds
        if self.permissions.valid_until > 0:
            caveats.append({
                "enforcer": "ValidUntilEnforcer",
                "terms": str(int(self.permissions.valid_until)),
            })

        # Nonce for revocation
        caveats.append({
            "enforcer": "NonceEnforcer",
            "terms": str(self.nonce),
        })

        return {
            "delegate": self.delegate,
            "caveats": caveats,
            "policyDigest": self.lease_digest(),
            "expiresAt": self.permissions.valid_until,
            "nonce": self.nonce,
        }

    def to_dict(self) -> dict:
        return {
            "schemaVersion": self.schema_version,
            "leaseId": self.lease_id,
            "agentId": self.agent_id,
            "owner": self.owner,
            "delegate": self.delegate,
            "permissions": self.permissions.to_dict(),
            "revocationEpoch": self.revocation_epoch,
            "nonce": self.nonce,
            "ownerSignature": self.owner_signature,
            "leaseDigest": self.lease_digest(),
            "erc7710Delegation": self.compile_to_erc7710(),
            "createdAt": self.created_at,
        }


def compile_permission_language(yaml_like: dict) -> AgentLeaseV1:
    """Compile high-level permission language into AgentLeaseV1.

    Input format:
    {
        "agent": "842",
        "expires": "2026-09-05T00:00:00Z",
        "permissions": {
            "x402": {"max_total_usd": 5, "max_request_usd": 0.20},
            "contracts": {"allow": [{"target": "0x...", "methods": ["submit(...)"]}]},
            "jobs": {"categories": ["research", "code-review"]}
        },
        "require": {"tee_workload": "0xabc..."}
    }
    """
    perms = LeasePermissions()

    p = yaml_like.get("permissions", {})

    # x402
    x402 = p.get("x402", {})
    if x402:
        perms.x402_max_total_usd = str(x402.get("max_total_usd", "5.00"))
        perms.x402_max_request_usd = str(x402.get("max_request_usd", "0.25"))

    # contracts
    contracts = p.get("contracts", {})
    for allow in contracts.get("allow", []):
        target = allow.get("target", "")
        methods = allow.get("methods", [])
        if target:
            perms.allowed_targets.append(target)
        perms.allowed_methods.extend(methods)

    # jobs
    jobs = p.get("jobs", {})
    perms.allowed_job_categories = jobs.get("categories", [])

    # require
    req = yaml_like.get("require", {})
    perms.required_tee_workload = req.get("tee_workload", "")

    # time
    expires = yaml_like.get("expires", "")
    if expires:
        from datetime import datetime
        try:
            perms.valid_until = datetime.fromisoformat(expires.replace("Z", "+00:00")).timestamp()
        except (ValueError, TypeError):
            pass

    lease = AgentLeaseV1(
        agent_id=str(yaml_like.get("agent", "")),
        permissions=perms,
    )
    return lease
