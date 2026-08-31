"""ComputeBroker — route tasks to cheapest capable model.

Escalation ladder:
  FREE → evaluator pass? → done
                       → CHEAP → evaluator pass? → done
                                              → STRONG → done
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .registry import ProviderRegistry
from .treasury import InferenceTreasury
from .bats import BATS, BudgetState


@dataclass
class RouteDecision:
    model: str = ""
    provider: str = ""
    reason: str = ""
    estimated_cost_usd: float = 0.0
    estimated_quality: float = 0.0
    escalation_level: str = ""  # free, cheap, strong


class ComputeBroker:
    """Route tasks to cheapest capable model."""

    def __init__(self, registry: ProviderRegistry, treasury: InferenceTreasury):
        self.registry = registry
        self.treasury = treasury
        self.bats = BATS(registry)

    def route(self, task_type: str, quality_floor: float, budget: BudgetState,
              uncertainty: float = 0.5) -> RouteDecision:
        """Route a task to the appropriate model."""

        # Try free first
        free_model = self.registry.cheapest_model(task_type)
        free_pricing = self.registry.get_pricing(free_model)

        if free_pricing.get("free", False):
            return RouteDecision(
                model=free_model,
                provider=free_pricing.get("provider", ""),
                reason="free_available",
                estimated_cost_usd=0.0,
                estimated_quality=0.7,  # assume reasonable quality
                escalation_level="free",
            )

        # Try cheap
        cheap_decision = self.bats.select_model(task_type, budget, uncertainty)
        cheap_cost = cheap_decision.get("estimated_cost", 0.0)

        if cheap_cost < 0.005 and budget.can_afford(cheap_cost):
            return RouteDecision(
                model=cheap_decision["model"],
                provider=cheap_decision["model"].split("/")[0],
                reason=cheap_decision["reason"],
                estimated_cost_usd=cheap_cost,
                estimated_quality=0.8,
                escalation_level="cheap",
            )

        # Use strong model
        strong_models = ["anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini"]
        for model in strong_models:
            cost = self.registry.estimate_cost(model, 1000, 500)
            if budget.can_afford(cost):
                return RouteDecision(
                    model=model,
                    provider=model.split("/")[0],
                    reason="strong_model_needed",
                    estimated_cost_usd=cost,
                    estimated_quality=0.95,
                    escalation_level="strong",
                )

        # Fallback to free
        return RouteDecision(
            model=free_model,
            provider="opencode-go",
            reason="budget_exhausted_use_free",
            estimated_cost_usd=0.0,
            estimated_quality=0.7,
            escalation_level="free",
        )

    def execute_with_escalation(self, task: str, quality_floor: float,
                                 budget: BudgetState, evaluator: Any = None) -> dict:
        """Execute task with escalation ladder."""
        levels = ["free", "cheap", "strong"]
        results = []

        for level in levels:
            decision = self.route(task, quality_floor, budget, uncertainty=0.5)
            if decision.escalation_level != level:
                continue

            # Execute (placeholder — would call actual model)
            result = {
                "model": decision.model,
                "level": level,
                "cost": decision.estimated_cost_usd,
                "quality": decision.estimated_quality,
            }
            results.append(result)

            # Check quality
            if evaluator and decision.estimated_quality >= quality_floor:
                return {"success": True, "results": results, "final_level": level}

            # Budget check
            budget.record_spend(decision.estimated_cost_usd)

        return {"success": False, "results": results, "final_level": levels[-1]}
