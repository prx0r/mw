"""InferenceBroker — route tasks to cheapest capable model.

Three policies:
  strong_only: always use best model
  free_first: try free, escalate on failure
  bats: budget-aware routing
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from .wallet import ComputeWallet
from .bats import BudgetState


@dataclass
class RouteDecision:
    model: str = ""
    provider: str = ""
    policy: str = ""
    reason: str = ""
    estimated_cost_usd: float = 0.0
    shadow_cost_usd: float = 0.0
    estimated_quality: float = 0.0
    escalation_level: str = ""


class InferenceBroker:
    """Route tasks to cheapest capable model."""

    def __init__(self, wallet: ComputeWallet):
        self.wallet = wallet
        self._free_models = [
            {"model": "opencode-go/mimo-v2.5", "provider": "opencode-go", "quality": 0.7},
        ]
        self._cheap_models = [
            {"model": "groq/llama-3.1-8b-instant", "provider": "groq", "quality": 0.8},
            {"model": "groq/llama-3.3-70b-versatile", "provider": "groq", "quality": 0.85},
        ]
        self._strong_models = [
            {"model": "anthropic/claude-3.5-sonnet", "provider": "anthropic", "quality": 0.95},
        ]

    def route(self, task_type: str, quality_floor: float,
              policy: str = "free_first", budget: BudgetState = None) -> RouteDecision:
        """Route based on policy."""

        if policy == "strong_only":
            return self._route_strong(quality_floor)
        elif policy == "free_first":
            return self._route_free_first(task_type, quality_floor)
        elif policy == "bats":
            return self._route_bats(task_type, quality_floor, budget)
        else:
            return self._route_free_first(task_type, quality_floor)

    def _route_strong(self, quality_floor: float) -> RouteDecision:
        for m in self._strong_models:
            if m["quality"] >= quality_floor:
                cost = 0.04  # approximate
                return RouteDecision(
                    model=m["model"], provider=m["provider"],
                    policy="strong_only", reason="always_strong",
                    estimated_cost_usd=cost, estimated_quality=m["quality"],
                    escalation_level="strong",
                )
        return RouteDecision(model="opencode-go/mimo-v2.5", policy="strong_only",
                           reason="fallback", escalation_level="free")

    def _route_free_first(self, task_type: str, quality_floor: float) -> RouteDecision:
        # Check if free model meets quality floor
        for m in self._free_models:
            if m["quality"] >= quality_floor:
                # Check quota
                q = self.wallet.quotas.get(m["provider"])
                if q and q.remaining > 0:
                    shadow = self.wallet.consume_quota(m["provider"], 1)
                    return RouteDecision(
                        model=m["model"], provider=m["provider"],
                        policy="free_first", reason="free_meets_quality",
                        shadow_cost_usd=shadow, estimated_quality=m["quality"],
                        escalation_level="free",
                    )

        # Escalate to cheap
        for m in self._cheap_models:
            if m["quality"] >= quality_floor:
                return RouteDecision(
                    model=m["model"], provider=m["provider"],
                    policy="free_first", reason="escalated_cheap",
                    estimated_cost_usd=0.001, estimated_quality=m["quality"],
                    escalation_level="cheap",
                )

        # Escalate to strong
        for m in self._strong_models:
            return RouteDecision(
                model=m["model"], provider=m["provider"],
                policy="free_first", reason="escalated_strong",
                estimated_cost_usd=0.04, estimated_quality=m["quality"],
                escalation_level="strong",
            )

        return RouteDecision(model="opencode-go/mimo-v2.5", policy="free_first",
                           reason="fallback", escalation_level="free")

    def _route_bats(self, task_type: str, quality_floor: float,
                    budget: BudgetState = None) -> RouteDecision:
        """BATS routing: consider uncertainty + budget + quotas."""
        if budget and not budget.can_afford(0.001):
            # Budget tight — use free
            m = self._free_models[0]
            shadow = self.wallet.consume_quota(m["provider"], 1)
            return RouteDecision(
                model=m["model"], provider=m["provider"],
                policy="bats", reason="budget_tight_free",
                shadow_cost_usd=shadow, estimated_quality=m["quality"],
                escalation_level="free",
            )

        # Default: free first
        return self._route_free_first(task_type, quality_floor)

    def record_outcome(self, decision: RouteDecision, success: bool,
                       actual_cost: float = 0.0, tokens: int = 0):
        """Record routing outcome for Hydra."""
        return {
            "model": decision.model,
            "policy": decision.policy,
            "reason": decision.reason,
            "level": decision.escalation_level,
            "success": success,
            "cost_usd": actual_cost,
            "shadow_cost_usd": decision.shadow_cost_usd,
            "tokens": tokens,
            "timestamp": time.time(),
        }
