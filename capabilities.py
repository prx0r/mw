"""Capability evidence — derive capabilities from multi-dimensional run history.

Not self-reported. Backed by actual runs, evaluations, outcomes, and economics.
The old CapabilityTracker used successful_runs/total_runs — wrong.
A high-quality submission can lose. A terrible submission can win in a weak field.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path


def uid() -> str:
    import os
    return f"cap_{os.urandom(4).hex()}"


@dataclass
class CapabilityEvidence:
    """One piece of evidence that a worker-version can do a task."""
    capability: str = ""
    worker_version: str = ""
    task_family: str = ""
    evaluator_score: float = 0.0
    outcome: str = ""  # won / lost
    payout: float = 0.0
    cost: float = 0.0
    review_scores: list[float] = field(default_factory=list)
    evidence_strength: str = "INSUFFICIENT"  # INSUFFICIENT / WEAK / MODERATE / STRONG
    observed_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "capability": self.capability,
            "worker_version": self.worker_version,
            "task_family": self.task_family,
            "evaluator_score": self.evaluator_score,
            "outcome": self.outcome,
            "payout": self.payout,
            "cost": self.cost,
            "review_scores": self.review_scores,
            "evidence_strength": self.evidence_strength,
            "observed_at": self.observed_at,
        }


@dataclass
class Capability:
    """Derived capability estimate — not directly mutated by runs."""
    id: str = field(default_factory=uid)
    name: str = ""
    category: str = ""
    description: str = ""

    # Derived from CapabilityEvidence list
    evidence_count: int = 0
    quality_estimate: float = 0.0  # multi-dimensional quality score
    confidence: str = "UNKNOWN"  # LOW, MEDIUM, HIGH, INSUFFICIENT
    task_families: list[str] = field(default_factory=list)
    worker_versions: list[str] = field(default_factory=list)

    # Economics
    median_cost: float = 0.0
    median_payout: float = 0.0
    cost_consistency: float = 0.0  # std dev of cost / mean

    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @property
    def is_confident(self) -> bool:
        return self.evidence_count >= 10 and self.confidence in ("MEDIUM", "HIGH")

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "category": self.category,
            "evidence_count": self.evidence_count,
            "quality_estimate": round(self.quality_estimate, 4),
            "confidence": self.confidence,
            "task_families": self.task_families,
            "median_cost": self.median_cost,
            "median_payout": self.median_payout,
        }


class CapabilityTracker:
    """Derive capabilities from multi-dimensional evidence.

    Each run produces a CapabilityEvidence. Capability estimates are derived
    from the full evidence set, not just success/count ratio.
    """

    def __init__(self):
        self.capabilities: dict[str, Capability] = {}
        self.evidence: list[CapabilityEvidence] = []

    def record_evidence(self, ev: CapabilityEvidence) -> None:
        """Record one piece of capability evidence."""
        self.evidence.append(ev)

        cap = self.capabilities.get(ev.capability)
        if not cap:
            cap = Capability(name=ev.capability)
            self.capabilities[ev.capability] = cap

        # Track provenance
        if ev.task_family and ev.task_family not in cap.task_families:
            cap.task_families.append(ev.task_family)
        if ev.worker_version and ev.worker_version not in cap.worker_versions:
            cap.worker_versions.append(ev.worker_version)

        # Recompute derived estimates
        self._recompute(cap)

    def record_run(self, run_id: str, capability_name: str,
                   accepted: bool, cost: float, payout: float,
                   evaluator_score: float = 0.0, task_family: str = "",
                   worker_version: str = "", review_scores: list[float] | None = None):
        """Legacy interface — wraps record_evidence."""
        ev = CapabilityEvidence(
            capability=capability_name,
            worker_version=worker_version,
            task_family=task_family,
            evaluator_score=evaluator_score,
            outcome="won" if accepted else "lost",
            payout=payout,
            cost=cost,
            review_scores=review_scores or [],
        )
        # Derive evidence strength
        signals = 0
        if evaluator_score > 0: signals += 1
        if payout > 0: signals += 1
        if review_scores: signals += 1
        if accepted: signals += 1
        if signals >= 4: ev.evidence_strength = "STRONG"
        elif signals >= 3: ev.evidence_strength = "MODERATE"
        elif signals >= 2: ev.evidence_strength = "WEAK"
        else: ev.evidence_strength = "INSUFFICIENT"
        self.record_evidence(ev)

    def _recompute(self, cap: Capability) -> None:
        """Recompute derived capability estimate from all evidence."""
        evs = [e for e in self.evidence if e.capability == cap.name]
        if not evs:
            return

        cap.evidence_count = len(evs)
        cap.updated_at = time.time()

        # Quality estimate: weighted combination of signals
        scores = []
        for ev in evs:
            # Each evidence contributes a quality signal
            signals = []
            if ev.evaluator_score > 0:
                signals.append(ev.evaluator_score)
            if ev.outcome == "won":
                signals.append(1.0)
            elif ev.outcome == "lost":
                signals.append(0.0)
            if ev.payout > 0 and ev.cost > 0:
                signals.append(min(1.0, ev.payout / max(0.01, ev.cost)))
            if ev.review_scores:
                signals.append(sum(ev.review_scores) / len(ev.review_scores))
            if signals:
                scores.append(sum(signals) / len(signals))

        cap.quality_estimate = sum(scores) / len(scores) if scores else 0.0

        # Economics
        costs = [e.cost for e in evs if e.cost > 0]
        payouts = [e.payout for e in evs if e.payout > 0]
        cap.median_cost = sorted(costs)[len(costs) // 2] if costs else 0.0
        cap.median_payout = sorted(payouts)[len(payouts) // 2] if payouts else 0.0

        if costs and len(costs) >= 2:
            mean_cost = sum(costs) / len(costs)
            variance = sum((c - mean_cost) ** 2 for c in costs) / len(costs)
            cap.cost_consistency = (variance ** 0.5) / max(0.01, mean_cost)
        else:
            cap.cost_consistency = 0.0

        # Confidence
        n_strong = sum(1 for e in evs if e.evidence_strength in ("STRONG", "MODERATE"))
        if cap.evidence_count >= 10 and n_strong >= 5:
            cap.confidence = "HIGH"
        elif cap.evidence_count >= 5 and n_strong >= 2:
            cap.confidence = "MEDIUM"
        elif cap.evidence_count >= 2:
            cap.confidence = "LOW"
        else:
            cap.confidence = "INSUFFICIENT"

    def get_capability(self, name: str) -> Capability | None:
        return self.capabilities.get(name)

    def list_capabilities(self) -> list[Capability]:
        return sorted(self.capabilities.values(), key=lambda c: c.quality_estimate, reverse=True)

    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        data = {
            "capabilities": [c.to_dict() for c in self.capabilities.values()],
            "evidence_count": len(self.evidence),
            "evidence": [e.to_dict() for e in self.evidence[-100:]],  # last 100
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
