"""Lab Router MVP — honest routing for the demo.

Routes questions to LabProjection queries. Not a retrieval system yet.
3 real queries: structure (runs), episodes (failures), skills (correlations).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrievalResult:
    """Result from a retrieval substrate."""
    substrate: str = ""
    query: str = ""
    results: list[dict] = field(default_factory=list)
    confidence: float = 0.0


class LabRouterMVP:
    """MVP router — 3 real queries backed by LabProjection.

    Not a retrieval system. Just structured access to what LabProjection already knows.
    """

    def __init__(self, lab_projection: Any = None):
        self.projection = lab_projection

    def route(self, question: str, task_family: str = "") -> list[RetrievalResult]:
        q = question.lower()

        if any(w in q for w in ["what modules", "what assets", "what exists", "runs", "history"]):
            return [self._query_runs(task_family)]

        if any(w in q for w in ["have we seen", "error", "failure", "failed"]):
            return [self._query_failures(task_family)]

        if any(w in q for w in ["skill", "correlation", "what works", "predict"]):
            return [self._query_skills(task_family)]

        # Default: runs
        return [self._query_runs(task_family)]

    def _query_runs(self, task_family: str) -> RetrievalResult:
        """Real query: what runs have we done?"""
        if not self.projection:
            return RetrievalResult(substrate="runs", query=task_family)
        runs = self.projection.get_runs(task_family=task_family) if task_family else self.projection.get_runs()
        return RetrievalResult(
            substrate="runs",
            query=task_family,
            results=runs[:10],
            confidence=1.0 if runs else 0.0,
        )

    def _query_failures(self, task_family: str) -> RetrievalResult:
        """Real query: what failed?"""
        if not self.projection:
            return RetrievalResult(substrate="failures", query=task_family)
        runs = self.projection.get_runs(outcome="lost", task_family=task_family) if task_family else self.projection.get_runs(outcome="lost")
        return RetrievalResult(
            substrate="failures",
            query=task_family,
            results=runs[:10],
            confidence=1.0 if runs else 0.0,
        )

    def _query_skills(self, task_family: str) -> RetrievalResult:
        """Real query: what skills predict success?"""
        if not self.projection:
            return RetrievalResult(substrate="skills", query=task_family)
        corr = self.projection.skill_win_correlation()
        relevant = [c for c in corr if task_family in c.get("task_families", [])] if task_family else corr
        return RetrievalResult(
            substrate="skills",
            query=task_family,
            results=relevant[:5],
            confidence=1.0 if relevant else 0.0,
        )
