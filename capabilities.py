"""Capability evidence — derive capabilities from run history.

Not self-reported. Backed by actual runs.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field


def uid() -> str:
    import os
    return f"cap_{os.urandom(4).hex()}"


@dataclass
class Capability:
    id: str = field(default_factory=uid)
    name: str = ""  # "python_bugfix", "web_research", etc.
    category: str = ""
    description: str = ""

    # Evidence (backed by runs)
    total_runs: int = 0
    successful_runs: int = 0
    median_cost: float = 0.0
    median_payout: float = 0.0
    confidence: str = "UNKNOWN"  # LOW, MEDIUM, HIGH, INSUFFICIENT

    # Run references
    run_ids: list[str] = field(default_factory=list)

    created_at: float = field(default_factory=time.time)

    @property
    def success_rate(self) -> float:
        return self.successful_runs / max(1, self.total_runs)

    @property
    def is_confident(self) -> bool:
        return self.total_runs >= 10 and self.confidence in ("MEDIUM", "HIGH")

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "category": self.category,
                "total_runs": self.total_runs, "success_rate": self.success_rate,
                "median_cost": self.median_cost, "confidence": self.confidence}


@dataclass
class CapabilityEvidence:
    run_id: str = ""
    capability_id: str = ""
    accepted: bool = False
    cost: float = 0.0
    payout: float = 0.0
    observed_at: float = field(default_factory=time.time)


class CapabilityTracker:
    """Derive capabilities from run history."""

    def __init__(self):
        self.capabilities: dict[str, Capability] = {}
        self.evidence: list[CapabilityEvidence] = []

    def record_run(self, run_id: str, capability_name: str,
                   accepted: bool, cost: float, payout: float):
        """Record that a run used this capability."""
        cap = self.capabilities.get(capability_name)
        if not cap:
            cap = Capability(name=capability_name)
            self.capabilities[capability_name] = cap

        cap.total_runs += 1
        if accepted:
            cap.successful_runs += 1
        cap.run_ids.append(run_id)

        # Update confidence
        if cap.total_runs >= 10:
            if cap.success_rate > 0.7:
                cap.confidence = "HIGH"
            elif cap.success_rate > 0.5:
                cap.confidence = "MEDIUM"
            else:
                cap.confidence = "LOW"
        elif cap.total_runs >= 3:
            cap.confidence = "LOW"
        else:
            cap.confidence = "INSUFFICIENT"

        self.evidence.append(CapabilityEvidence(
            run_id=run_id, capability_id=cap.id,
            accepted=accepted, cost=cost, payout=payout,
        ))

    def get_capability(self, name: str) -> Capability | None:
        return self.capabilities.get(name)

    def list_capabilities(self) -> list[Capability]:
        return sorted(self.capabilities.values(), key=lambda c: c.success_rate, reverse=True)

    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        data = {
            "capabilities": [c.to_dict() for c in self.capabilities.values()],
            "evidence_count": len(self.evidence),
        }
        (path / "capabilities.json").write_text(json.dumps(data, indent=2))

    def load(self, path: Path):
        p = path / "capabilities.json"
        if p.exists():
            data = json.loads(p.read_text())
            for c_data in data.get("capabilities", []):
                cap = Capability()
                for k, v in c_data.items():
                    if hasattr(cap, k): setattr(cap, k, v)
                self.capabilities[cap.name] = cap
