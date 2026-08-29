"""Budget enforcement — hard limits."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Budget:
    daily_cap: float = 5.0
    per_run_cap: float = 2.0
    lifetime_cap: float = 50.0

    def can_spend(self, amount: float, daily_spent: float, lifetime_spent: float,
                  run_spent: float = 0.0) -> bool:
        return (run_spent + amount <= self.per_run_cap and
                daily_spent + amount <= self.daily_cap and
                lifetime_spent + amount <= self.lifetime_cap)
