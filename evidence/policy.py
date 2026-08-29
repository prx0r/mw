"""Execution policy — what the TEE is allowed to do."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from evidence.canonical import keccak256, canonical_json


@dataclass
class ExecutionPolicy:
    """Policy binding what a TEE worker can do.

    Two layers:
    - TEE policy: tools, credentials, APIs, memory, files, budget
    - ERC-7710 caveats: contract targets, methods, spend cap, expiry
    """
    # TEE controls
    allowed_tools: list[str] = field(default_factory=list)
    forbidden_tools: list[str] = field(default_factory=list)
    allowed_credentials: list[str] = field(default_factory=list)
    allowed_apis: list[str] = field(default_factory=list)
    max_model_budget: str = "5.00"
    job_type: str = ""
    submission_target: str = ""

    # ERC-7710 on-chain controls
    allowed_targets: list[str] = field(default_factory=list)
    allowed_methods: list[str] = field(default_factory=list)
    max_spend_usd: str = "5.00"
    expires_at: float = 0.0
    max_calls: int = 100

    def digest(self) -> str:
        """Keccak-256 of the canonical policy."""
        return keccak256(canonical_json({
            "allowedTools": self.allowed_tools,
            "forbiddenTools": self.forbidden_tools,
            "allowedCredentials": self.allowed_credentials,
            "allowedApis": self.allowed_apis,
            "maxModelBudget": self.max_model_budget,
            "jobType": self.job_type,
            "submissionTarget": self.submission_target,
            "allowedTargets": self.allowed_targets,
            "allowedMethods": self.allowed_methods,
            "maxSpendUsd": self.max_spend_usd,
            "expiresAt": self.expires_at,
            "maxCalls": self.max_calls,
        }))

    def is_expired(self) -> bool:
        if self.expires_at <= 0:
            return False
        return time.time() > self.expires_at

    def to_dict(self) -> dict:
        return {
            "allowedTools": self.allowed_tools,
            "forbiddenTools": self.forbidden_tools,
            "allowedCredentials": self.allowed_credentials,
            "allowedApis": self.allowed_apis,
            "maxModelBudget": self.max_model_budget,
            "jobType": self.job_type,
            "submissionTarget": self.submission_target,
            "allowedTargets": self.allowed_targets,
            "allowedMethods": self.allowed_methods,
            "maxSpendUsd": self.max_spend_usd,
            "expiresAt": self.expires_at,
            "maxCalls": self.max_calls,
            "digest": self.digest(),
        }


@dataclass
class Lease:
    """A Moltwork lease — standard delegation + off-chain policy + TEE identity."""
    lease_id: str = ""
    agent_id: str = ""
    delegate: str = ""  # TEE signer address
    valid_until: float = 0.0
    budget_usd: str = "10.00"
    policy: ExecutionPolicy = field(default_factory=ExecutionPolicy)
    created_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        return time.time() > self.valid_until

    def to_dict(self) -> dict:
        return {
            "leaseId": self.lease_id,
            "agentId": self.agent_id,
            "delegate": self.delegate,
            "validUntil": self.valid_until,
            "budgetUsd": self.budget_usd,
            "policy": self.policy.to_dict(),
            "createdAt": self.created_at,
        }
