"""BATS — Budget-Aware Token Scheduler.

Uses real pricing from ProviderRegistry + LiveLLM.
Makes economic decisions about which model to use when.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BudgetState:
    total_usd: float = 0.0
    spent_usd: float = 0.0
    remaining_usd: float = 0.0

    total_tokens: int = 0
    spent_tokens: int = 0

    model_calls: int = 0
    max_model_calls: int = 10

    wall_seconds: float = 0.0
    max_wall_seconds: float = 60.0

    def can_afford(self, estimated_cost: float) -> bool:
        return self.remaining_usd >= estimated_cost and self.model_calls < self.max_model_calls

    def record_spend(self, cost_usd: float, tokens: int = 0):
        self.spent_usd += cost_usd
        self.remaining_usd = max(0, self.total_usd - self.spent_usd)
        self.spent_tokens += tokens
        self.model_calls += 1


class BATS:
    """Budget-Aware Token Scheduler — decides when to use which model."""

    def __init__(self, registry):
        self.registry = registry

    def select_model(self, task_type: str, budget: BudgetState, uncertainty: float = 0.5) -> dict:
        """Select the best model given task, budget, and uncertainty.

        Returns: {"model": str, "reason": str, "estimated_cost": float}
        """
        # High uncertainty → use stronger model
        # Low uncertainty → use cheapest model
        # Budget tight → use free model

        if budget.remaining_usd < 0.001:
            return {
                "model": "opencode-go/mimo-v2.5",
                "reason": "budget_tight_use_free",
                "estimated_cost": 0.0,
            }

        if uncertainty > 0.7 and budget.remaining_usd > 0.01:
            # High uncertainty, budget allows → use stronger model
            for model in ["groq/llama-3.3-70b-versatile", "groq/llama-3.1-8b-instant"]:
                cost = self.registry.estimate_cost(model, 1000, 500)
                if budget.can_afford(cost):
                    return {
                        "model": model,
                        "reason": f"high_uncertainty_budget_allows",
                        "estimated_cost": cost,
                    }

        # Default: use free model
        return {
            "model": "opencode-go/mimo-v2.5",
            "reason": "default_free",
            "estimated_cost": 0.0,
        }

    def should_escalate(self, current_model: str, quality_score: float, budget: BudgetState) -> bool:
        """Decide if we should escalate to a stronger model."""
        if quality_score > 0.8:
            return False  # good enough
        if budget.remaining_usd < 0.005:
            return False  # too expensive
        return True  # worth trying stronger model

    def should_branch(self, budget: BudgetState, n_candidates: int) -> bool:
        """Decide if we should explore multiple candidates."""
        if n_candidates >= 3:
            return False  # already enough
        if budget.remaining_usd < 0.002:
            return False  # too expensive
        return True

    def should_verify(self, quality_score: float, budget: BudgetState) -> bool:
        """Decide if we should verify the result."""
        if quality_score > 0.9:
            return False  # already good enough
        if budget.remaining_usd < 0.001:
            return False  # too expensive
        return True

    def budget_report(self, budget: BudgetState) -> dict:
        """Generate a budget report."""
        return {
            "spent_usd": round(budget.spent_usd, 4),
            "remaining_usd": round(budget.remaining_usd, 4),
            "total_usd": round(budget.total_usd, 4),
            "model_calls": budget.model_calls,
            "max_model_calls": budget.max_model_calls,
            "spent_tokens": budget.spent_tokens,
            "efficiency": round(budget.spent_usd / max(1, budget.model_calls), 4),
        }
