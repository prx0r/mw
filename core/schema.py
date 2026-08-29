"""Canonical record types — 10 families, short names, clean schemas.

Frozen architecture from workkitfinal.md.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any


def uid() -> str:
    return f"wk_{uuid.uuid4().hex[:12]}"


def sha256(data: str | bytes) -> str:
    """Full SHA-256 — 64 hex characters."""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


# ─── 1. WorkOrder ──────────────────────────────────────────────────────

@dataclass
class WorkOrder:
    id: str = field(default_factory=uid)
    source: str = ""
    source_id: str = ""
    objective: str = ""
    reward_value: str = ""
    reward_currency: str = "USD"
    deadline: str = ""
    submission_target: str = ""
    acceptance_contract_digest: str = ""
    raw: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


# ─── 2. WorkerManifest ─────────────────────────────────────────────────

@dataclass
class WorkerManifest:
    id: str = field(default_factory=uid)
    version: str = "1.0"
    adapter: str = ""
    executor_digest: str = ""
    config_digest: str = ""
    toolset_digest: str = ""
    skillset_digest: str = ""
    behavioral_identity_digest: str = ""
    disclosure: str = "PUBLIC"
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


# ─── 3. WorkerEvent (canonical truth) ──────────────────────────────────

@dataclass
class WorkerEvent:
    id: str = field(default_factory=uid)
    run_id: str = ""
    sequence: int = 0
    event_type: str = ""
    occurred_at: float = field(default_factory=time.time)
    recorded_at: float = field(default_factory=time.time)
    witness_source: str = ""
    witness_channel: str = ""
    actor_type: str = ""
    actor_id: str = ""
    subject_refs: list[str] = field(default_factory=list)
    causation_id: str = ""
    payload: dict = field(default_factory=dict)
    previous_event_hash: str = ""
    self_hash: str = ""
    def compute_hash(self) -> str:
        data = {
            "id": self.id, "run_id": self.run_id, "sequence": self.sequence,
            "event_type": self.event_type, "occurred_at": self.occurred_at,
            "actor_type": self.actor_type, "payload": self.payload,
            "previous_event_hash": self.previous_event_hash,
        }
        return sha256(json.dumps(data, sort_keys=True))
    def to_dict(self) -> dict:
        return asdict(self)


# ─── 4. ArtifactRef ────────────────────────────────────────────────────

@dataclass
class ArtifactRef:
    id: str = field(default_factory=uid)
    name: str = ""
    media_type: str = ""
    sha256: str = ""
    uri: str = ""
    derived_from: list[str] = field(default_factory=list)
    disclosure: str = "PUBLIC"
    def to_dict(self) -> dict:
        return asdict(self)


# ─── 5. CostEvent ──────────────────────────────────────────────────────

@dataclass
class CostEvent:
    id: str = field(default_factory=uid)
    run_id: str = ""
    category: str = ""
    provider: str = ""
    amount_value: str = ""
    currency: str = "USD"
    measurement: str = "OBSERVED"
    source: str = "COMPUTED"
    occurred_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


# ─── 6. VerificationResult ─────────────────────────────────────────────

@dataclass
class VerificationResult:
    id: str = field(default_factory=uid)
    run_id: str = ""
    subject_sha256: str = ""
    claim_type: str = ""
    verifier_id: str = ""
    independence: str = ""
    method: str = ""
    status: str = ""
    score: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    issued_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


# ─── 7. CommitDecision ─────────────────────────────────────────────────

@dataclass
class CommitDecision:
    id: str = field(default_factory=uid)
    run_id: str = ""
    action: str = ""
    subject_sha256: str = ""
    checks: list[dict] = field(default_factory=list)
    decision: str = ""
    decided_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


# ─── 8-9. External Receipts ────────────────────────────────────────────

@dataclass
class SubmissionReceipt:
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
    id: str = field(default_factory=uid)
    submission_id: str = ""
    status: str = ""
    reward_value: str = ""
    reward_currency: str = ""
    observed_at: float = field(default_factory=time.time)
    evidence: dict = field(default_factory=dict)
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SettlementReceipt:
    id: str = field(default_factory=uid)
    outcome_id: str = ""
    status: str = ""
    amount: str = ""
    currency: str = ""
    tx_hash: str = ""
    settled_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


# ─── 11. WorkerRun (projection over events) ─────────────────────────────

@dataclass
class WorkerRun:
    """Execution record — projection over events. Not canonical truth."""
    id: str = field(default_factory=uid)
    work_order_id: str = ""
    status: str = "RUNNING"
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


# WorkReceipt is defined in receipts.py (canonical, with logic)
