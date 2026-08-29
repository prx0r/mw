"""Campaign — the agent deciding to pursue an Opportunity.

An Opportunity is something the Oracle observed.
A Campaign is the agent expending resources to capture it.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.hashing import sha256, jcs


class CampaignStatus(str, Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class WorkUnitStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class WorkUnit:
    """One unit of work within a Campaign."""
    work_unit_id: str = ""
    title: str = ""
    description: str = ""
    status: str = "PENDING"  # WorkUnitStatus

    required_capabilities: list[str] = field(default_factory=list)
    estimated_cost_usd: float = 0.0
    estimated_duration_s: int = 0

    # Execution
    assigned_agent: str = ""
    git_branch: str = ""
    git_worktree: str = ""

    # Results
    artifact_paths: list[str] = field(default_factory=list)
    receipt_ids: list[str] = field(default_factory=list)
    cost_usd: float = 0.0
    duration_s: float = 0.0

    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0

    def to_dict(self) -> dict:
        return {
            "work_unit_id": self.work_unit_id,
            "title": self.title,
            "status": self.status,
            "required_capabilities": self.required_capabilities,
            "estimated_cost_usd": self.estimated_cost_usd,
            "assigned_agent": self.assigned_agent,
            "git_branch": self.git_branch,
            "artifact_paths": self.artifact_paths,
            "receipt_ids": self.receipt_ids,
            "cost_usd": self.cost_usd,
        }


@dataclass
class WorkPlan:
    """Plan for executing a Campaign."""
    plan_id: str = ""
    version: int = 1
    strategy: str = ""
    work_units: list[WorkUnit] = field(default_factory=list)
    total_estimated_cost: float = 0.0
    total_estimated_duration: int = 0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "version": self.version,
            "strategy": self.strategy,
            "work_units": [wu.to_dict() for wu in self.work_units],
            "total_estimated_cost": self.total_estimated_cost,
        }


@dataclass
class Campaign:
    """Agent deciding to pursue an Opportunity."""
    campaign_id: str = ""
    opportunity_id: str = ""
    route_id: str = ""

    status: str = "PLANNING"  # CampaignStatus

    # Budget
    budget_usd: float = 10.0
    spent_usd: float = 0.0
    cost_cap_usd: float = 5.0

    # Work
    work_plan: WorkPlan | None = None
    active_work_units: list[str] = field(default_factory=list)

    # Git
    campaign_branch: str = ""
    worktree_paths: dict[str, str] = field(default_factory=dict)

    # Results
    submission_id: str = ""
    outcome: str = ""  # won/lost/pending
    prize_usd: float = 0.0

    # Metrics
    total_runs: int = 0
    total_events: int = 0

    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    completed_at: float = 0.0

    def remaining_budget(self) -> float:
        return self.budget_usd - self.spent_usd

    def can_continue(self) -> bool:
        if self.status not in ("PLANNING", "ACTIVE"):
            return False
        if self.spent_usd >= self.cost_cap_usd:
            return False
        return True

    def record_cost(self, amount: float) -> None:
        self.spent_usd += amount
        self.updated_at = time.time()

    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "opportunity_id": self.opportunity_id,
            "route_id": self.route_id,
            "status": self.status,
            "budget_usd": self.budget_usd,
            "spent_usd": self.spent_usd,
            "cost_cap_usd": self.cost_cap_usd,
            "work_plan": self.work_plan.to_dict() if self.work_plan else None,
            "total_runs": self.total_runs,
            "outcome": self.outcome,
            "prize_usd": self.prize_usd,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Campaign":
        plan = WorkPlan(**d["work_plan"]) if d.get("work_plan") else None
        return cls(
            campaign_id=d.get("campaign_id", ""),
            opportunity_id=d.get("opportunity_id", ""),
            route_id=d.get("route_id", ""),
            status=d.get("status", "PLANNING"),
            budget_usd=d.get("budget_usd", 10),
            spent_usd=d.get("spent_usd", 0),
            cost_cap_usd=d.get("cost_cap_usd", 5),
            work_plan=plan,
            total_runs=d.get("total_runs", 0),
            outcome=d.get("outcome", ""),
            prize_usd=d.get("prize_usd", 0),
        )
