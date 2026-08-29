"""Reflection — outcome-gated promotion with ExperimentResult requirement.

Old: promote() just sets status = "proven" with no evidence.
New: promote() requires an ExperimentResult proving improvement on held-out fixtures.

States: OBSERVED → PROPOSED → UNDER_TEST → VALIDATED | REJECTED
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ExperimentResult:
    """Proof that a lesson improves performance on held-out fixtures."""
    experiment_id: str = ""
    lesson_id: str = ""
    parent_version: str = ""
    candidate_version: str = ""
    hidden_mean_before: float = 0.0
    hidden_mean_after: float = 0.0
    gate_regressions: list[str] = field(default_factory=list)
    cost_delta: float = 0.0
    promoted: bool = False
    reasoning: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "lesson_id": self.lesson_id,
            "parent_version": self.parent_version,
            "candidate_version": self.candidate_version,
            "hidden_mean_before": self.hidden_mean_before,
            "hidden_mean_after": self.hidden_mean_after,
            "improvement": self.hidden_mean_after - self.hidden_mean_before,
            "gate_regressions": self.gate_regressions,
            "cost_delta": self.cost_delta,
            "promoted": self.promoted,
            "reasoning": self.reasoning,
        }


@dataclass
class CandidateLesson:
    """A proposed lesson with full context for evaluation."""
    lesson_id: str
    content: str
    evidence_runs: int
    target: str  # memory / skill / mod
    status: str = "OBSERVED"  # OBSERVED / PROPOSED / UNDER_TEST / VALIDATED / REJECTED
    hypothesis: str = ""
    patch: dict = field(default_factory=dict)
    source_runs: list[str] = field(default_factory=list)
    evaluation_plan: str = ""
    experiment_result: ExperimentResult | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class ReflectionPipeline:
    """Outcome-gated reflection. Never blindly rewrite after every run.

    A lesson can only become VALIDATED after cg proves it improves performance
    on held-out fixtures. No ExperimentResult → no promotion.
    """

    def __init__(self, hydra=None):
        self.hydra = hydra
        self.candidates: dict[str, CandidateLesson] = {}
        self._failure_counts: dict[str, int] = defaultdict(int)
        self._total_runs: int = 0

    def observe(self, run_id: str, evaluation: float, outcome: str, failure_reason: str = ""):
        """Store observation. No immediate memory write."""
        self._total_runs += 1
        if failure_reason:
            self._failure_counts[failure_reason] += 1

    def scan_candidates(self, min_evidence: int = 3) -> list[CandidateLesson]:
        """Find failure patterns with enough evidence to propose."""
        result = []
        for reason, count in self._failure_counts.items():
            if count >= min_evidence and reason not in self.candidates:
                c = CandidateLesson(
                    lesson_id=f"lesson-{len(self.candidates)}",
                    content=reason,
                    evidence_runs=count,
                    target="memory",
                    status="PROPOSED",
                    hypothesis=f"Addressing '{reason}' will improve outcomes",
                )
                self.candidates[reason] = c
                result.append(c)
        return result

    def submit_for_testing(self, lesson_id: str, evaluation_plan: str = "") -> bool:
        """Move a proposed lesson to UNDER_TEST."""
        c = self._find(lesson_id)
        if not c or c.status != "PROPOSED":
            return False
        c.status = "UNDER_TEST"
        c.evaluation_plan = evaluation_plan
        c.updated_at = time.time()
        return True

    def promote(self, lesson_id: str, experiment_result: ExperimentResult | None = None) -> bool:
        """Promote a lesson to VALIDATED. Requires ExperimentResult.

        Without experiment evidence, promotion is blocked.
        The experiment must show improvement on held-out fixtures.
        """
        c = self._find(lesson_id)
        if not c:
            return False

        # Can only promote from UNDER_TEST
        if c.status != "UNDER_TEST":
            return False

        # Require experiment result
        if experiment_result is None:
            return False

        # Must show improvement
        if experiment_result.hidden_mean_after <= experiment_result.hidden_mean_before:
            experiment_result.promoted = False
            experiment_result.reasoning = "No improvement on held-out fixtures"
            c.experiment_result = experiment_result
            return False

        # Must have no gate regressions
        if experiment_result.gate_regressions:
            experiment_result.promoted = False
            experiment_result.reasoning = f"Gate regressions: {experiment_result.gate_regressions}"
            c.experiment_result = experiment_result
            return False

        # Promote
        c.status = "VALIDATED"
        c.experiment_result = experiment_result
        experiment_result.promoted = True
        experiment_result.reasoning = f"Improved from {experiment_result.hidden_mean_before:.3f} to {experiment_result.hidden_mean_after:.3f}"
        c.updated_at = time.time()
        return True

    def reject(self, lesson_id: str, reason: str = "") -> bool:
        """Reject a lesson."""
        c = self._find(lesson_id)
        if not c:
            return False
        c.status = "REJECTED"
        c.updated_at = time.time()
        if reason and c.experiment_result:
            c.experiment_result.reasoning = reason
        return True

    def _find(self, lesson_id: str) -> CandidateLesson | None:
        return next((v for v in self.candidates.values() if v.lesson_id == lesson_id), None)

    def list_by_status(self, status: str) -> list[CandidateLesson]:
        return [c for c in self.candidates.values() if c.status == status]
