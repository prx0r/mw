"""Reflection — outcome-gated promotion: observation → candidate → proven."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class CandidateLesson:
    lesson_id: str
    content: str
    evidence_runs: int
    target: str  # memory / skill / mod
    status: str = "candidate"  # candidate / proven / rejected
    created_at: float = field(default_factory=time.time)


class ReflectionPipeline:
    """Outcome-gated reflection. Never blindly rewrite after every run."""

    def __init__(self, hydra=None):
        self.hydra = hydra
        self.candidates: dict[str, CandidateLesson] = {}
        self._failure_counts: dict[str, int] = defaultdict(int)
        self._total_runs: int = 0

    def observe(self, run_id: str, evaluation: float, outcome: str, failure_reason: str = ""):
        """Store observation in Hydra. No immediate memory write."""
        self._total_runs += 1
        if failure_reason:
            self._failure_counts[failure_reason] += 1

    def scan_candidates(self, min_evidence: int = 3) -> list[CandidateLesson]:
        """Find failure patterns with enough evidence to become candidates."""
        result = []
        for reason, count in self._failure_counts.items():
            if count >= min_evidence and reason not in self.candidates:
                c = CandidateLesson(
                    lesson_id=f"lesson-{len(self.candidates)}",
                    content=reason,
                    evidence_runs=count,
                    target="memory",
                )
                self.candidates[reason] = c
                result.append(c)
        return result

    def promote(self, lesson_id: str) -> bool:
        c = next((v for v in self.candidates.values() if v.lesson_id == lesson_id), None)
        if c:
            c.status = "proven"
            return True
        return False

    def reject(self, lesson_id: str) -> bool:
        c = next((v for v in self.candidates.values() if v.lesson_id == lesson_id), None)
        if c:
            c.status = "rejected"
            return True
        return False
