"""Structured briefs — not just text, but machine-readable context.

LabContext returns structured data that a worker can consume programmatically.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StructuredBrief:
    """Machine-readable lab brief for a task family."""
    task_family: str = ""
    worker_id: str = ""

    # Prior statistics
    total_runs: int = 0
    win_rate: float = 0.0
    avg_score: float = 0.0
    avg_cost: float = 0.0
    avg_reward: float = 0.0

    # Best practices
    best_skill: str = ""
    best_skill_win_rate: float = 0.0
    best_process: str = ""

    # Patterns
    strong_patterns: list[str] = field(default_factory=list)
    recurring_failures: list[str] = field(default_factory=list)
    failure_warnings: list[str] = field(default_factory=list)

    # Related runs
    similar_wins: list[dict] = field(default_factory=list)
    similar_losses: list[dict] = field(default_factory=list)

    # Economics
    model_economics: list[dict] = field(default_factory=list)
    cost_efficiency: float = 0.0

    def to_dict(self) -> dict:
        return {
            "task_family": self.task_family,
            "worker_id": self.worker_id,
            "prior_runs": self.total_runs,
            "win_rate": round(self.win_rate, 4),
            "avg_score": round(self.avg_score, 4),
            "avg_cost": round(self.avg_cost, 4),
            "avg_reward": round(self.avg_reward, 4),
            "best_skill": self.best_skill,
            "best_skill_win_rate": round(self.best_skill_win_rate, 4),
            "strong_patterns": self.strong_patterns,
            "recurring_failures": self.recurring_failures,
            "failure_warnings": self.failure_warnings,
            "similar_wins": self.similar_wins[:5],
            "similar_losses": self.similar_losses[:3],
            "model_economics": self.model_economics[:3],
        }

    def to_text(self) -> str:
        """Human-readable text format."""
        lines = [
            f"# LAB BRIEF — {self.task_family}",
            f"**Worker** {self.worker_id}",
            "",
            f"Task family: {self.task_family}",
            f"Prior runs: {self.total_runs}  win_rate: {self.win_rate:.0%}  avg_score: {self.avg_score:.3f}",
        ]
        if self.best_skill:
            lines.append(f"Best skill: {self.best_skill} ({self.best_skill_win_rate:.0%})")
        if self.strong_patterns:
            lines.extend(["", "Strong patterns:"] + [f"- {p}" for p in self.strong_patterns])
        if self.recurring_failures:
            lines.extend(["", "Recurring failures:"] + [f"- {f}" for f in self.recurring_failures])
        if self.similar_wins:
            lines.extend(["", "Similar wins:"] + [f"- {w['run_id']} score={w['score']:.3f}" for w in self.similar_wins[:3]])
        lines.extend(["", "*Full trajectories on demand — ask for run_id.*"])
        return "\n".join(lines)

    def to_prompt(self) -> str:
        """Format as a Letta-friendly prompt."""
        return (
            f"LAB CONTEXT for {self.task_family}:\n"
            f"You have {self.total_runs} prior runs with {self.win_rate:.0%} win rate.\n"
            f"Average score: {self.avg_score:.3f}, average cost: ${self.avg_cost:.3f}\n"
            f"Best skill: {self.best_skill or 'none identified'}\n"
            + (f"Strong patterns: {', '.join(self.strong_patterns[:3])}\n" if self.strong_patterns else "")
            + (f"Avoid: {', '.join(self.recurring_failures[:3])}\n" if self.recurring_failures else "")
            + f"Use this context as evidence, not ground truth."
        )
