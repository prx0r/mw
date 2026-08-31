"""InferenceTreasury — manage compute credits, quotas, shadow pricing."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QuotaBucket:
    provider: str = ""
    unit: str = ""  # neurons, credits, tokens
    daily_limit: float = 0.0
    remaining: float = 0.0
    reset_at: str = ""  # ISO timestamp
    paid_enabled: bool = False

    def shadow_price(self) -> float:
        """Shadow price approaches 0 near reset."""
        if self.daily_limit <= 0:
            return 0.0
        utilization = 1.0 - (self.remaining / self.daily_limit)
        # Near reset (high utilization), shadow price drops
        return max(0.0, 0.1 * (1.0 - utilization))

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class CashBalance:
    provider: str = ""
    remaining_usd: float = 0.0
    expires_at: str = ""

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}


class InferenceTreasury:
    """Manage compute resources across providers."""

    def __init__(self):
        self.quotas: dict[str, QuotaBucket] = {}
        self.cash: dict[str, CashBalance] = {}

    def register_quota(self, provider: str, unit: str, daily_limit: float, reset_at: str = ""):
        self.quotas[provider] = QuotaBucket(
            provider=provider, unit=unit,
            daily_limit=daily_limit, remaining=daily_limit,
            reset_at=reset_at,
        )

    def register_cash(self, provider: str, remaining_usd: float, expires_at: str = ""):
        self.cash[provider] = CashBalance(
            provider=provider, remaining_usd=remaining_usd, expires_at=expires_at,
        )

    def effective_cost(self, provider: str, money_cost: float, quota_units: int = 0) -> float:
        """Calculate effective cost including shadow pricing."""
        shadow = 0.0
        if provider in self.quotas:
            q = self.quotas[provider]
            shadow = q.shadow_price() * quota_units
            q.remaining = max(0, q.remaining - quota_units)

        if provider in self.cash:
            self.cash[provider].remaining_usd = max(0, self.cash[provider].remaining_usd - money_cost)

        return money_cost + shadow

    def available_providers(self) -> list[dict]:
        """List providers with available resources."""
        providers = []
        for provider, q in self.quotas.items():
            if q.remaining > 0:
                providers.append({
                    "provider": provider,
                    "type": "quota",
                    "remaining": q.remaining,
                    "unit": q.unit,
                    "shadow_price": q.shadow_price(),
                })
        for provider, c in self.cash.items():
            if c.remaining_usd > 0:
                providers.append({
                    "provider": provider,
                    "type": "cash",
                    "remaining_usd": c.remaining_usd,
                })
        return providers

    def status(self) -> dict:
        return {
            "quotas": {k: v.to_dict() for k, v in self.quotas.items()},
            "cash": {k: v.to_dict() for k, v in self.cash.items()},
            "available": self.available_providers(),
        }
