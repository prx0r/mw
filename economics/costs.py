"""Cost tracking — historical benchmark + live metering."""
from __future__ import annotations
import json, time
from dataclasses import dataclass


@dataclass
class CostEnvelope:
    low: float = 0.0
    expected: float = 0.0
    high: float = 0.0
    hard_cap: float = 0.0


class CostModel:
    def __init__(self):
        self._history: dict[str, list[dict]] = {}

    def record(self, task_type: str, model: str, cost: float, success: bool):
        key = f"{task_type}:{model}"
        self._history.setdefault(key, []).append({"cost": cost, "success": success})

    def estimate(self, task_type: str, model: str = "") -> CostEnvelope:
        runs = self._history.get(f"{task_type}:{model}", [])
        if not runs:
            return CostEnvelope(low=0.05, expected=0.20, high=0.50, hard_cap=1.0)
        costs = sorted(r["cost"] for r in runs)
        n = len(costs)
        return CostEnvelope(
            low=costs[0], expected=costs[n//2],
            high=costs[min(int(n*0.9), n-1)],
            hard_cap=costs[min(int(n*0.9), n-1)] * 1.5,
        )

    def success_rate(self, task_type: str, model: str = "") -> float:
        runs = self._history.get(f"{task_type}:{model}", [])
        if not runs: return 0.5
        return sum(1 for r in runs if r["success"]) / len(runs)


class RunMeter:
    def __init__(self):
        self.total_cost: float = 0.0
        self.events: list[dict] = []

    def record(self, category: str, cost: float, **kwargs):
        self.total_cost += cost
        self.events.append({"category": category, "cost": cost, **kwargs, "ts": time.time()})
