"""ERC-8004 Identity — onchain agent identity.

ERC-8004 defines Identity Registry, Reputation Registry, and Validation Registry
for trustless agent discovery across organizational boundaries.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from core.hashing import sha256, jcs


@dataclass
class AgentRegistration:
    """ERC-8004 agent registration (off-chain representation)."""
    schema: str = "https://eips.ethereum.org/EIPS/eip-8004#registration-v1"
    name: str = ""
    description: str = ""
    services: list[dict] = field(default_factory=list)  # [{name, endpoint}]
    x402_support: bool = True
    supported_trust: list[str] = field(default_factory=list)  # ["reputation", "tee-attestation"]
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "type": self.schema,
            "name": self.name,
            "description": self.description,
            "services": self.services,
            "x402Support": self.x402_support,
            "supportedTrust": self.supported_trust,
        }

    def content_hash(self) -> str:
        return sha256(jcs(self.to_dict()))


@dataclass
class ReputationFeedback:
    """One piece of reputation feedback on an agent."""
    agent_id: str = ""
    value: float = 0.0  # 0-100
    value_decimals: int = 0
    tag1: str = ""  # e.g. "quality"
    tag2: str = ""  # e.g. "frontend"
    endpoint: str = ""
    feedback_uri: str = ""
    feedback_hash: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> dict:
        return {
            "agentId": self.agent_id,
            "value": self.value,
            "valueDecimals": self.value_decimals,
            "tag1": self.tag1,
            "tag2": self.tag2,
            "endpoint": self.endpoint,
            "feedbackURI": self.feedback_uri,
            "feedbackHash": self.feedback_hash,
            "timestamp": self.timestamp,
        }


@dataclass
class ValidationRequest:
    """Request for independent validation of a worker/run."""
    request_uri: str = ""
    request_hash: str = ""
    worker_id: str = ""
    run_id: str = ""
    receipt_hash: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "requestURI": self.request_uri,
            "requestHash": self.request_hash,
            "workerId": self.worker_id,
            "runId": self.run_id,
            "receiptHash": self.receipt_hash,
        }


@dataclass
class ValidationResponse:
    """Response from an independent validator."""
    response: int = 0  # 0-100 score
    tag: str = ""  # e.g. "tee-workerkit-v1"
    validator: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> dict:
        return {
            "response": self.response,
            "tag": self.tag,
            "validator": self.validator,
            "timestamp": self.timestamp,
        }


class ERC8004Identity:
    """ERC-8004 identity manager for Moltwork workers."""

    def __init__(self):
        self._registrations: dict[str, AgentRegistration] = {}
        self._reputation: dict[str, list[ReputationFeedback]] = {}
        self._validations: dict[str, list[ValidationResponse]] = {}

    def register(self, worker_id: str, name: str, description: str = "",
                 services: list[dict] | None = None,
                 supported_trust: list[str] | None = None) -> AgentRegistration:
        """Register a worker with ERC-8004 identity."""
        reg = AgentRegistration(
            name=name,
            description=description,
            services=services or [],
            supported_trust=supported_trust or ["reputation"],
        )
        self._registrations[worker_id] = reg
        return reg

    def get_registration(self, worker_id: str) -> AgentRegistration | None:
        return self._registrations.get(worker_id)

    def add_reputation(self, feedback: ReputationFeedback) -> None:
        """Record reputation feedback for a worker."""
        self._reputation.setdefault(feedback.agent_id, []).append(feedback)

    def get_reputation(self, worker_id: str) -> list[ReputationFeedback]:
        return self._reputation.get(worker_id, [])

    def avg_reputation(self, worker_id: str) -> float:
        """Get average reputation score."""
        feedbacks = self.get_reputation(worker_id)
        if not feedbacks:
            return 0.0
        return sum(f.value for f in feedbacks) / len(feedbacks)

    def add_validation(self, worker_id: str, response: ValidationResponse) -> None:
        """Record a validation response."""
        self._validations.setdefault(worker_id, []).append(response)

    def get_validations(self, worker_id: str) -> list[ValidationResponse]:
        return self._validations.get(worker_id, [])

    def to_well_known(self, worker_id: str) -> dict | None:
        """Generate .well-known/agent-registration.json for a worker."""
        reg = self.get_registration(worker_id)
        if not reg:
            return None
        return reg.to_dict()
