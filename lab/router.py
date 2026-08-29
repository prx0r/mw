"""Lab Context Router — Rekal-style structured/episode/why routing.

Routes different types of questions to different retrieval substrates:
  - "What modules exist?" → inventory / Git tree
  - "Have we seen this error?" → trajectory episodes
  - "Why did we reject approach X?" → decision synthesis
  - "What happened economically?" → WorkerKit ledger
  - "What procedure do I know?" → SKILL.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.hashing import sha256


@dataclass
class RetrievalResult:
    """Result from a specific retrieval substrate."""
    substrate: str = ""
    query: str = ""
    results: list[dict] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "substrate": self.substrate,
            "query": self.query,
            "result_count": len(self.results),
            "confidence": self.confidence,
        }


class LabContextRouter:
    """Route questions to the right retrieval substrate.

    Rekal-style: different questions need different retrieval strategies.
    Don't dump everything into one vector search.
    """

    def __init__(self, lab_projection: Any = None, inventory: Any = None):
        self.projection = lab_projection
        self.inventory = inventory

    def route(self, question: str, task_family: str = "") -> list[RetrievalResult]:
        """Route a question to appropriate retrieval substrates."""
        results = []

        q = question.lower()

        # Structure questions → inventory / Git tree
        if any(w in q for w in ["what modules", "what assets", "what exists", "inventory"]):
            results.append(self._retrieve_structure(task_family))

        # Historical questions → trajectory episodes
        if any(w in q for w in ["have we seen", "previous", "before", "error", "failure"]):
            results.append(self._retrieve_episodes(task_family))

        # Why questions → decision synthesis
        if any(w in q for w in ["why", "reason", "decided", "rejected", "chose"]):
            results.append(self._retrieve_decisions(task_family))

        # Economic questions → WorkerKit ledger
        if any(w in q for w in ["cost", "revenue", "profit", "spend", "budget", "economic"]):
            results.append(self._retrieve_economics(task_family))

        # Procedure questions → skills
        if any(w in q for w in ["procedure", "how to", "process", "skill", "workflow"]):
            results.append(self._retrieve_skills(task_family))

        # Default: retrieve from all substrates
        if not results:
            results = [
                self._retrieve_structure(task_family),
                self._retrieve_episodes(task_family),
                self._retrieve_skills(task_family),
            ]

        return results

    def _retrieve_structure(self, task_family: str) -> RetrievalResult:
        """What modules/assets exist?"""
        return RetrievalResult(
            substrate="inventory",
            query=f"structure:{task_family}",
            results=[],
            confidence=0.5,
        )

    def _retrieve_episodes(self, task_family: str) -> RetrievalResult:
        """Have we seen this before?"""
        return RetrievalResult(
            substrate="trajectory",
            query=f"episodes:{task_family}",
            results=[],
            confidence=0.5,
        )

    def _retrieve_decisions(self, task_family: str) -> RetrievalResult:
        """Why did we do X?"""
        return RetrievalResult(
            substrate="decisions",
            query=f"decisions:{task_family}",
            results=[],
            confidence=0.5,
        )

    def _retrieve_economics(self, task_family: str) -> RetrievalResult:
        """What happened economically?"""
        return RetrievalResult(
            substrate="ledger",
            query=f"economics:{task_family}",
            results=[],
            confidence=0.5,
        )

    def _retrieve_skills(self, task_family: str) -> RetrievalResult:
        """What procedures do we know?"""
        return RetrievalResult(
            substrate="skills",
            query=f"skills:{task_family}",
            results=[],
            confidence=0.5,
        )
