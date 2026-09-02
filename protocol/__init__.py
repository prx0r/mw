"""Moltwork Economic Protocol — Canonical objects for bounded agent economy.

Objects:
  Mandate  — what the human authorized conceptually
  Grant    — exact economic authority
  Intent   — agent proposal
  Plan     — deterministically resolved transaction
  Approval — human or policy authorization
  Receipt  — what happened
  EconomicOutcome — normalized financial results

Core flow:
  Mandate → Grant → Intent → Plan → Approval → Execution → Receipt → EconomicOutcome

All Pydantic. All immutable/versioned.
"""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, computed_field


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _future(hours: int = 6) -> str:
    return datetime.now(timezone.utc).replace(
        hour=(datetime.now(timezone.utc).hour + hours) % 24
    ).isoformat()


def _hash_fields(model: BaseModel) -> str:
    """Deterministic hash excluding volatile fields."""
    import hashlib
    exclude = {"created_at", "schema_version"}
    data = {k: v for k, v in model.model_dump().items() if k not in exclude}
    return hashlib.sha256(str(data).encode()).hexdigest()[:16]


# ─── Enums ──────────────────────────────────────────────────────────────

class ActionType(str, Enum):
    BENCHMARK = "benchmark"
    REGISTER = "register"
    STAKE = "stake"
    UNSTAKE = "unstake"
    SWAP_STAKE = "swap_stake"
    TRANSFER = "transfer"
    HOLD = "hold"
    DEPLOY = "deploy"


class GrantStatus(str, Enum):
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ReceiptStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REVERTED = "reverted"


class ApprovalSource(str, Enum):
    HUMAN = "human"
    POLICY = "policy"
    AUTO = "auto"


# ─── Mandate ────────────────────────────────────────────────────────────

class Mandate(BaseModel):
    """What the human actually authorized conceptually.

    Example:
        Mandate(
            objective="Test whether our coding worker can profitably mine SN62",
            max_total_loss_usd=10,
            expires_at="2026-09-03T00:00:00Z",
        )
    """
    mandate_id: str = Field(default_factory=lambda: f"MND-{int(datetime.now().timestamp())}")
    objective: str
    max_total_loss_usd: float = 10.0
    max_total_loss_tao: float = 0.5
    allowed_environments: list[str] = Field(default_factory=lambda: ["bittensor"])
    expires_at: str = Field(default_factory=lambda: _future(24))
    created_at: str = Field(default_factory=_now)
    schema_version: str = "1.0.0"

    def compute_digest(self) -> str:
        return _hash_fields(self)


# ─── Grant ──────────────────────────────────────────────────────────────

class Grant(BaseModel):
    """Exact economic authority — what the agent can do with real limits.

    Example:
        Grant(
            agent_id="coding-03",
            environment="bittensor",
            allowed_actions=[ActionType.BENCHMARK, ActionType.REGISTER],
            allowed_netuids=[62],
            max_tao=0.20,
            max_api_usd=5,
            max_registrations=1,
            expires_at="2026-09-02T18:00:00Z",
        )
    """
    grant_id: str = Field(default_factory=lambda: f"MWGR-{int(datetime.now().timestamp())}")
    mandate_id: str
    agent_id: str
    environment: str
    allowed_actions: list[ActionType]
    allowed_netuids: list[int] = Field(default_factory=list)
    max_tao: float = 0.0
    max_api_usd: float = 0.0
    max_registrations: int = 0
    max_stake_tao: float = 0.0
    max_slippage_bps: int = 50
    expires_at: str = Field(default_factory=lambda: _future(6))
    status: GrantStatus = GrantStatus.ACTIVE
    spent_tao: float = 0.0
    spent_usd: float = 0.0
    registrations_used: int = 0
    created_at: str = Field(default_factory=_now)
    schema_version: str = "1.0.0"

    def compute_digest(self) -> str:
        return _hash_fields(self)

    def remaining_tao(self) -> float:
        return max(0, self.max_tao - self.spent_tao)

    def remaining_registrations(self) -> int:
        return max(0, self.max_registrations - self.registrations_used)

    def is_valid(self) -> bool:
        if self.status != GrantStatus.ACTIVE:
            return False
        if datetime.fromisoformat(self.expires_at) < datetime.now(timezone.utc):
            return False
        return True

    def check_action(self, action: ActionType, netuid: int, cost_tao: float) -> tuple[bool, str]:
        """Check if an action is within grant bounds."""
        if not self.is_valid():
            return False, f"Grant {self.status.value} or expired"
        if action not in self.allowed_actions:
            return False, f"Action {action.value} not in {self.allowed_actions}"
        if self.allowed_netuids and netuid not in self.allowed_netuids:
            return False, f"Netuid {netuid} not in {self.allowed_netuids}"
        if cost_tao > self.remaining_tao():
            return False, f"Cost {cost_tao} > remaining {self.remaining_tao()}"
        return True, "ok"


# ─── Intent ─────────────────────────────────────────────────────────────

class Intent(BaseModel):
    """Agent proposal — what the agent wants to do.

    Example:
        Intent(
            grant_id="MWGR-001",
            action=ActionType.REGISTER,
            netuid=62,
            max_cost_tao=0.14,
            evidence=["benchmark-run-918"],
        )
    """
    intent_id: str = Field(default_factory=lambda: f"INT-{int(datetime.now().timestamp())}")
    grant_id: str
    action: ActionType
    netuid: int = 0
    max_cost_tao: float = 0.0
    max_cost_usd: float = 0.0
    evidence: list[str] = Field(default_factory=list)
    reasoning: str = ""
    created_at: str = Field(default_factory=_now)
    schema_version: str = "1.0.0"

    def compute_digest(self) -> str:
        return _hash_fields(self)


# ─── Plan ───────────────────────────────────────────────────────────────

class Plan(BaseModel):
    """Deterministically resolved transaction — exact predicted effects.

    Example:
        Plan(
            intent_id="INT-001",
            action=ActionType.REGISTER,
            netuid=62,
            call="BurnedRegister",
            origin="5DHnQ...signer",
            amount_tao=0.127,
            fee_tao=0.001,
            expected_effects=["uid_assigned", "stake_required"],
            grant_check={"passed": True, "remaining": 0.073},
        )
    """
    plan_id: str = Field(default_factory=lambda: f"PLAN-{int(datetime.now().timestamp())}")
    intent_id: str
    action: ActionType
    netuid: int = 0
    call: str = ""
    origin: str = ""
    signer: str = ""
    amount_tao: float = 0.0
    fee_tao: float = 0.0
    slippage_bps: int = 0
    expected_effects: list[str] = Field(default_factory=list)
    grant_check: dict = Field(default_factory=dict)
    created_at: str = Field(default_factory=_now)
    schema_version: str = "1.0.0"

    def compute_digest(self) -> str:
        return _hash_fields(self)


# ─── Approval ───────────────────────────────────────────────────────────

class Approval(BaseModel):
    """Human or policy authorization before execution."""
    approval_id: str = Field(default_factory=lambda: f"APR-{int(datetime.now().timestamp())}")
    plan_id: str
    source: ApprovalSource
    approved: bool
    comment: str = ""
    created_at: str = Field(default_factory=_now)
    schema_version: str = "1.0.0"


# ─── Receipt ────────────────────────────────────────────────────────────

class Receipt(BaseModel):
    """What happened — chain confirmation or failure.

    Example:
        Receipt(
            plan_id="PLAN-001",
            tx_hash="0xabc...",
            block=12345,
            actual_spend_tao=0.128,
            status=ReceiptStatus.CONFIRMED,
            events=["uid_assigned:72"],
        )
    """
    receipt_id: str = Field(default_factory=lambda: f"RCT-{int(datetime.now().timestamp())}")
    plan_id: str
    tx_hash: str = ""
    block: int = 0
    actual_spend_tao: float = 0.0
    actual_spend_usd: float = 0.0
    status: ReceiptStatus = ReceiptStatus.PENDING
    events: list[str] = Field(default_factory=list)
    error: str = ""
    remaining_grant_tao: float = 0.0
    created_at: str = Field(default_factory=_now)
    schema_version: str = "1.0.0"

    def compute_digest(self) -> str:
        return _hash_fields(self)


# ─── EconomicOutcome ────────────────────────────────────────────────────

class EconomicOutcome(BaseModel):
    """Normalized financial results for a WorkerRun.

    Attached to every run. Enables Hydra queries like:
      "SN62 + skill-v8 + MiMo is profitable"
      "SN60 + same model is not"
      "This agent wastes 18% of API budget"
    """
    outcome_id: str = Field(default_factory=lambda: f"ECO-{int(datetime.now().timestamp())}")
    run_id: str = ""

    # Revenue
    gross_reward: float = 0.0
    reward_currency: str = "TAO"

    # Costs (broken down)
    cost_inference: float = 0.0
    cost_compute: float = 0.0
    cost_api: float = 0.0
    cost_chain: float = 0.0
    cost_registration: float = 0.0
    cost_fees: float = 0.0
    cost_human: float = 0.0

    @computed_field
    @property
    def total_cost(self) -> float:
        return (self.cost_inference + self.cost_compute + self.cost_api +
                self.cost_chain + self.cost_registration + self.cost_fees +
                self.cost_human)

    # Capital
    capital_at_risk: float = 0.0
    returned_capital: float = 0.0

    # Derived
    @computed_field
    @property
    def net_profit(self) -> float:
        return self.gross_reward - self.total_cost

    @computed_field
    @property
    def roi(self) -> float:
        if self.capital_at_risk <= 0:
            return 0.0
        return self.net_profit / self.capital_at_risk

    # Operational
    success: bool = False
    survival: bool = False
    score: float = 0.0
    opportunity_cost: float = 0.0

    created_at: str = Field(default_factory=_now)
    schema_version: str = "1.0.0"

    def compute_digest(self) -> str:
        return _hash_fields(self)
