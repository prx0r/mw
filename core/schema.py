"""Canonical record types — short names, clean schemas.

11 record types. That's it.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


def uid() -> str:
    return f"wk_{uuid.uuid4().hex[:12]}"


def sha256(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()[:16]


@dataclass
class ArtifactRef:
    """Content-addressed reference to an artifact."""
    id: str = field(default_factory=uid)
    name: str = ""
    uri: str = ""
    media_type: str = ""
    size_bytes: int = 0
    sha256: str = ""
    disclosure: str = "PUBLIC"  # PUBLIC | PRIVATE | ENCRYPTED | REDACTED
    annotations: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkOrder:
    """Frozen opportunity — the input to a run."""
    id: str = field(default_factory=uid)
    source: str = ""  # "taskmarket", "apify", etc.
    source_id: str = ""
    objective: str = ""
    reward_value: str = ""
    reward_currency: str = "USD"
    deadline: str = ""
    acceptance_contract_id: str = ""
    created_at: float = field(default_factory=time.time)
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AcceptanceContract:
    """What must be true for work to be accepted."""
    id: str = field(default_factory=uid)
    required_outputs: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    minimum_quality: float = 0.6
    maximum_cost: float = 5.0
    verifier_id: str = ""
    external_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkerManifest:
    """Worker identity and configuration hash."""
    id: str = field(default_factory=uid)
    version: str = "1.0"
    adapter: str = ""  # "hermes", "pydanticai", "claude", etc.
    config_hash: str = ""
    skills_hash: str = ""
    disclosure: str = "PUBLIC"  # PUBLIC | PRIVATE | ENCRYPTED
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkerRun:
    """Execution record — projection over events."""
    id: str = field(default_factory=uid)
    work_order_id: str = ""
    worker_id: str = ""
    status: str = "RUNNING"  # RUNNING | COMPLETED | FAILED | ABORTED
    started_at: float = field(default_factory=time.time)
    finished_at: float = 0.0
    known_cost_usd: str = "0"
    unpriced_events: int = 0
    outputs: list[str] = field(default_factory=list)
    verification_refs: list[str] = field(default_factory=list)
    submission_ref: str = ""
    outcome_ref: str = ""
    settlement_ref: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkerEvent:
    """Append-only canonical event."""
    id: str = field(default_factory=uid)
    run_id: str = ""
    sequence: int = 0
    event_type: str = ""  # "run.started", "model.call", "cost.recorded", etc.
    occurred_at: float = field(default_factory=time.time)
    recorded_at: float = field(default_factory=time.time)
    actor_type: str = ""  # WORKER | RUNTIME | VERIFIER | PLATFORM | HUMAN
    actor_id: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    payload: dict = field(default_factory=dict)
    payload_sha256: str = ""
    prev_event_sha256: str = ""
    event_sha256: str = ""

    def compute_hash(self) -> str:
        """Hash the event (excluding event_sha256 itself)."""
        data = {
            "id": self.id, "run_id": self.run_id, "sequence": self.sequence,
            "event_type": self.event_type, "occurred_at": self.occurred_at,
            "actor_type": self.actor_type, "actor_id": self.actor_id,
            "payload": self.payload, "prev": self.prev_event_sha256,
        }
        return sha256(json.dumps(data, sort_keys=True))

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CostEvent:
    """One economic event."""
    id: str = field(default_factory=uid)
    run_id: str = ""
    category: str = ""  # MODEL | API | TOOL | COMPUTE | SERVICE | PAYMENT
    provider: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    amount_usd: str = ""  # decimal string, never float
    measurement: str = "OBSERVED"  # OBSERVED | DERIVED | UNKNOWN
    source: str = "COMPUTED"  # PROVIDER_REPORTED | COMPUTED | RECEIPT
    occurred_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EconomicDecision:
    """Make/buy/abort decision."""
    id: str = field(default_factory=uid)
    run_id: str = ""
    decision: str = ""  # CONTINUE | SWITCH | BUY_HELP | ABORT
    expected_reward: str = ""
    expected_cost: str = ""
    p_success: str = ""
    expected_net: str = ""
    reason_codes: list[str] = field(default_factory=list)
    occurred_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VerificationResult:
    """Independent quality check."""
    id: str = field(default_factory=uid)
    run_id: str = ""
    subject_sha256: str = ""
    verifier_id: str = ""
    status: str = ""  # PASS | FAIL | INCONCLUSIVE
    score: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    issued_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CommitDecision:
    """Gate for irreversible actions."""
    id: str = field(default_factory=uid)
    run_id: str = ""
    action: str = ""  # SUBMIT | PAY | PUBLISH | SIGN
    target: str = ""
    subject_sha256: str = ""
    checks: list[dict] = field(default_factory=list)
    decision: str = ""  # ALLOW | DENY | REQUIRE_APPROVAL
    decided_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SubmissionReceipt:
    """Proof of submission."""
    id: str = field(default_factory=uid)
    run_id: str = ""
    venue: str = ""
    external_id: str = ""
    artifact_sha256: str = ""
    submitted_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class OutcomeReceipt:
    """External outcome evidence."""
    id: str = field(default_factory=uid)
    submission_id: str = ""
    status: str = ""  # UNKNOWN | ACCEPTED | REJECTED | DISPUTED
    reward_value: str = ""
    reward_currency: str = ""
    observed_at: float = field(default_factory=time.time)
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SettlementReceipt:
    """Payment/settlement evidence."""
    id: str = field(default_factory=uid)
    outcome_id: str = ""
    status: str = ""  # UNSETTLED | PENDING | SETTLED | REVERSED
    amount: str = ""
    currency: str = ""
    tx_hash: str = ""
    settled_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)
