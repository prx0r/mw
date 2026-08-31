"""ComputeWallet — track quotas, cash, reset times, shadow pricing."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QuotaBucket:
    provider: str = ""
    unit: str = ""
    daily_limit: float = 0.0
    remaining: float = 0.0
    reset_at: float = 0.0  # unix timestamp
    paid_enabled: bool = False

    def shadow_price(self) -> float:
        """Price approaches 0 near reset, higher when quota is fresh."""
        if self.daily_limit <= 0:
            return 0.0
        utilization = 1.0 - (self.remaining / self.daily_limit)
        time_to_reset = max(0, self.reset_at - time.time())
        hours_to_reset = time_to_reset / 3600

        # Near reset: shadow price drops
        if hours_to_reset < 1:
            return max(0.0, 0.01 * (1.0 - utilization))
        # Fresh quota: higher shadow price
        return max(0.0, 0.10 * utilization * min(1.0, hours_to_reset / 12))

    def is_expiring(self, within_hours: float = 2.0) -> bool:
        """Is this quota about to expire?"""
        return (self.reset_at - time.time()) < within_hours * 3600

    def to_dict(self):
        return {
            "provider": self.provider, "unit": self.unit,
            "daily_limit": self.daily_limit, "remaining": self.remaining,
            "reset_at": self.reset_at, "shadow_price": self.shadow_price(),
            "is_expiring": self.is_expiring(),
        }


@dataclass
class CashBalance:
    provider: str = ""
    remaining_usd: float = 0.0
    expires_at: float = 0.0

    def to_dict(self):
        return {"provider": self.provider, "remaining_usd": self.remaining_usd}


class ComputeWallet:
    """Track all compute resources: cash, quotas, expiring credits."""

    def __init__(self):
        self.quotas: dict[str, QuotaBucket] = {}
        self.cash: dict[str, CashBalance] = {}

    def register_quota(self, provider: str, unit: str, daily_limit: float,
                       reset_hours: float = 24.0):
        import datetime
        now = time.time()
        # Next reset
        reset_at = now + (reset_hours * 3600)
        self.quotas[provider] = QuotaBucket(
            provider=provider, unit=unit,
            daily_limit=daily_limit, remaining=daily_limit,
            reset_at=reset_at,
        )

    def register_cash(self, provider: str, remaining_usd: float):
        self.cash[provider] = CashBalance(provider=provider, remaining_usd=remaining_usd)

    def consume_quota(self, provider: str, units: float) -> float:
        """Consume quota, return shadow cost."""
        if provider not in self.quotas:
            return 0.0
        q = self.quotas[provider]
        shadow = q.shadow_price() * units
        q.remaining = max(0, q.remaining - units)
        return shadow

    def consume_cash(self, provider: str, amount: float):
        if provider in self.cash:
            self.cash[provider].remaining_usd = max(0, self.cash[provider].remaining_usd - amount)

    def expiring_quotas(self, within_hours: float = 2.0) -> list[dict]:
        """Find quotas about to expire — candidates for scavenger."""
        result = []
        for provider, q in self.quotas.items():
            if q.is_expiring(within_hours) and q.remaining > 0:
                result.append(q.to_dict())
        return result

    def total_free_value(self) -> float:
        """Total notional value of remaining free compute."""
        total = 0.0
        for q in self.quotas.values():
            total += q.remaining * q.shadow_price()
        return total

    def status(self) -> dict:
        return {
            "quotas": {k: v.to_dict() for k, v in self.quotas.items()},
            "cash": {k: v.to_dict() for k, v in self.cash.items()},
            "expiring": self.expiring_quotas(),
            "total_free_value": self.total_free_value(),
        }
