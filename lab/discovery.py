"""Lab discovery — Hydra finds patterns, distills to workers."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LabInsight:
    title: str
    body: str
    evidence_runs: int
    confidence: float


class LabDiscovery:
    """Analyzes Hydra to produce shared insights."""

    def __init__(self, hydra):
        self.hydra = hydra

    def discover(self) -> list[LabInsight]:
        insights: list[LabInsight] = []

        # Skill correlation
        for entry in self.hydra.skill_win_correlation():
            if entry["win_rate"] > 0.7 and entry["n"] >= 5:
                insights.append(LabInsight(
                    title=f"Skill '{entry['skill']}' correlates with wins",
                    body=f"Win rate {entry['win_rate']:.0%} over {entry['n']} runs",
                    evidence_runs=entry["n"],
                    confidence=min(0.95, entry["win_rate"]),
                ))

        # Model profitability
        for entry in self.hydra.profitability_by_model():
            if entry["n"] and entry["n"] >= 5 and (entry["avg_profit"] or 0) > 1.0:
                insights.append(LabInsight(
                    title=f"Model {entry['model']} profitable",
                    body=f"Avg profit ${entry['avg_profit']:.2f} over {entry['n']} runs",
                    evidence_runs=int(entry["n"]),
                    confidence=0.8,
                ))

        # Persist to Hydra
        for ins in insights:
            self.hydra.add_insight(
                insight_id=ins.title,
                title=ins.title,
                body=ins.body,
                evidence_runs=ins.evidence_runs,
                confidence=ins.confidence,
            )

        return insights

    def distill_for_worker(self, role: str) -> str:
        """Generate shared lesson markdown for a role."""
        insights = self.discover()
        if not insights:
            return f"# Lab insights for {role}\n\nNo patterns yet — need more runs."
        lines = [f"# Lab insights for {role}\n"]
        for ins in insights:
            lines.append(f"## {ins.title}\n{ins.body} (confidence {ins.confidence:.0%})\n")
        return "\n".join(lines)
