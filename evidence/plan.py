"""ExecutionPlan — PlanBound-style live quoting + budget discipline.

Key insight: agent doesn't ask "Can I spend $5?"
It shops around, creates a plan with live quotes, then gets approval.
Re-quote each purchase. Stop on plan drift.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from evidence.canonical import sha256, canonical_json


class PlanStatus(Enum):
    DRAFT = "draft"
    QUOTED = "quoted"
    COMMITTED = "committed"
    AUTHORIZED = "authorized"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class PlanStep:
    """A single step in an execution plan."""
    step_id: str = ""
    description: str = ""
    provider: str = ""
    method: str = ""  # model call, API call, tool call, x402 purchase
    estimated_cost: str = "0"
    live_quote: str = ""  # real 402 quote (vs estimated)
    quote_valid_until: float = 0.0
    status: str = "pending"  # pending, executed, skipped, failed
    result_hash: str = ""
    actual_cost: str = "0"

    def is_stale(self) -> bool:
        """Quote has expired."""
        if self.quote_valid_until <= 0:
            return False
        return time.time() > self.quote_valid_until

    def to_dict(self) -> dict:
        return {
            "stepId": self.step_id,
            "description": self.description,
            "provider": self.provider,
            "method": self.method,
            "estimatedCost": self.estimated_cost,
            "liveQuote": self.live_quote,
            "quoteValidUntil": self.quote_valid_until,
            "status": self.status,
            "resultHash": self.result_hash,
            "actualCost": self.actual_cost,
        }


@dataclass
class ExecutionPlan:
    """PlanBound-style execution plan with live quoting.

    Flow: DISCOVER → QUOTE → PLAN → COMMIT → AUTHORIZE → EXECUTE → RECEIPT
    """
    plan_id: str = ""
    job_id: str = ""
    agent_id: str = ""
    steps: list[PlanStep] = field(default_factory=list)
    total_ceiling: str = "0"  # max total spend
    actual_total: str = "0"
    status: PlanStatus = PlanStatus.DRAFT
    drift_tolerance_pct: float = 0.10  # 10% drift allowed
    approved_by: str = ""  # human or contract
    approved_at: float = 0.0
    created_at: float = field(default_factory=time.time)

    def add_step(self, step: PlanStep):
        self.steps.append(step)

    def total_estimated(self) -> str:
        """Sum of estimated costs."""
        total = 0.0
        for s in self.steps:
            try:
                total += float(s.estimated_cost)
            except (ValueError, TypeError):
                pass
        return f"{total:.6f}"

    def total_actual(self) -> str:
        """Sum of actual costs."""
        total = 0.0
        for s in self.steps:
            try:
                total += float(s.actual_cost)
            except (ValueError, TypeError):
                pass
        return f"{total:.6f}"

    def check_drift(self) -> tuple[bool, str]:
        """Check if actual cost drifted too far from estimate.

        Returns (is_acceptable, reason).
        """
        try:
            estimated = float(self.total_estimated())
            actual = float(self.total_actual())
        except (ValueError, TypeError):
            return True, "cannot compute drift"

        if estimated <= 0:
            return actual <= float(self.total_ceiling), "no baseline"

        drift_pct = abs(actual - estimated) / estimated
        if drift_pct > self.drift_tolerance_pct:
            return False, f"drift {drift_pct:.1%} > {self.drift_tolerance_pct:.1%}"
        return True, f"drift {drift_pct:.1%} within tolerance"

    def requote_step(self, step_id: str, new_live_quote: str) -> bool:
        """Re-quote a step before execution. If drift too large, abort."""
        for s in self.steps:
            if s.step_id == step_id:
                s.live_quote = new_live_quote
                # Check if new quote drifts from plan
                try:
                    est = float(s.estimated_cost)
                    new = float(new_live_quote)
                    if est > 0:
                        drift = abs(new - est) / est
                        if drift > self.drift_tolerance_pct:
                            s.status = "failed"
                            return False
                except (ValueError, TypeError):
                    pass
                return True
        return False

    def commit(self, approved_by: str):
        """Commit the plan after approval."""
        self.status = PlanStatus.COMMITTED
        self.approved_by = approved_by
        self.approved_at = time.time()

    def plan_hash(self) -> str:
        """Hash of the committed plan."""
        return sha256(canonical_json({
            "planId": self.plan_id,
            "jobId": self.job_id,
            "agentId": self.agent_id,
            "steps": [s.to_dict() for s in self.steps],
            "totalCeiling": self.total_ceiling,
            "driftTolerance": self.drift_tolerance_pct,
            "approvedBy": self.approved_by,
            "approvedAt": self.approved_at,
        }))

    def to_dict(self) -> dict:
        return {
            "planId": self.plan_id,
            "jobId": self.job_id,
            "agentId": self.agent_id,
            "steps": [s.to_dict() for s in self.steps],
            "totalCeiling": self.total_ceiling,
            "totalEstimated": self.total_estimated(),
            "totalActual": self.total_actual(),
            "status": self.status.value,
            "driftTolerance": self.drift_tolerance_pct,
            "approvedBy": self.approved_by,
            "planHash": self.plan_hash(),
        }
