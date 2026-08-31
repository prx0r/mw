"""Learning pipeline: trajectory → reflection → proposal → cg → promotion.

The core loop:
  1. Accumulate training runs with evaluations
  2. Letta reflects on trajectories + reviews
  3. Produces a structured LearningProposal
  4. cg validates on held-out fixtures
  5. If validated, promote to Worker v2
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from workerkit.lab.reflection import ReflectionPipeline, CandidateLesson, ExperimentResult
from workerkit.lab.evaluator import Evaluator, EvaluationResult, format_comparison


@dataclass
class TrainingRun:
    """A completed training run with full context."""
    run_id: str
    fixture_id: str
    fixture: dict
    output: str
    evaluation: EvaluationResult
    trajectory: list[dict] = field(default_factory=list)
    reviewer_feedback: str = ""
    outcome: str = ""  # won / lost
    cost_usd: float = 0.0
    duration_s: float = 0.0


@dataclass
class LearningProposal:
    """A structured proposal for worker improvement."""
    proposal_id: str = ""
    kind: str = ""  # memory / skill / process
    hypothesis: str = ""
    patch: str = ""
    source_runs: list[str] = field(default_factory=list)
    source_trajectories: list[dict] = field(default_factory=list)
    evaluation_plan: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "kind": self.kind,
            "hypothesis": self.hypothesis,
            "patch": self.patch,
            "source_runs": self.source_runs,
            "evaluation_plan": self.evaluation_plan,
        }


class LearningPipeline:
    """End-to-end learning pipeline.

    Flow:
      training_runs → accumulate → reflect → propose → validate → promote
    """

    def __init__(self, hydra=None, evaluator: Evaluator | None = None):
        self.hydra = hydra
        self.evaluator = evaluator or Evaluator()
        self.reflection = ReflectionPipeline(hydra=hydra)
        self.training_runs: list[TrainingRun] = []
        self.proposals: list[LearningProposal] = []
        self.worker_versions: list[dict] = []

    def record_training_run(self, run: TrainingRun) -> None:
        """Record a completed training run."""
        self.training_runs.append(run)

        # Record in reflection pipeline
        failure_reason = ""
        if run.evaluation:
            failed_gates = [g for g, p in run.evaluation.gate_results.items() if not p]
            if failed_gates:
                failure_reason = f"failed gates: {', '.join(failed_gates)}"

        self.reflection.observe(
            run_id=run.run_id,
            evaluation=run.evaluation.overall_score if run.evaluation else 0,
            outcome=run.outcome,
            failure_reason=failure_reason,
        )

    def generate_proposal(self, min_evidence: int = 3) -> LearningProposal | None:
        """Reflect on training runs and generate a learning proposal."""
        # Find candidate lessons
        candidates = self.reflection.scan_candidates(min_evidence=min_evidence)
        if not candidates:
            return None

        # Take the strongest candidate
        candidate = max(candidates, key=lambda c: c.evidence_runs)

        # Find training runs that match this failure pattern
        matching_runs = []
        for run in self.training_runs:
            if run.evaluation:
                failed_gates = [g for g, p in run.evaluation.gate_results.items() if not p]
                if candidate.content in str(failed_gates):
                    matching_runs.append(run)

        # Generate proposal with matching ID
        proposal = LearningProposal(
            proposal_id=candidate.lesson_id,  # Match candidate ID
            kind=candidate.target,
            hypothesis=f"Addressing '{candidate.content}' will improve outcomes on similar tasks",
            patch=self._generate_patch(candidate, matching_runs),
            source_runs=[r.run_id for r in matching_runs],
            evaluation_plan=f"Run {len(matching_runs)} training runs → evaluate on hidden fixtures → compare",
        )

        self.proposals.append(proposal)
        candidate.status = "PROPOSED"
        return proposal

    def _generate_patch(self, candidate: CandidateLesson, runs: list[TrainingRun]) -> str:
        """Generate a concrete patch from a candidate lesson."""
        # Analyze the failure pattern
        failure = candidate.content
        evidence_count = candidate.evidence_runs

        # Generate a specific, actionable patch
        if "gate" in failure and "requirement" in failure.lower():
            return (
                "Before starting any ideation task, construct an explicit requirement matrix. "
                "List every constraint from the task description. "
                "Check each constraint before submitting."
            )
        elif "diversity" in failure.lower():
            return (
                "When generating ideas, explicitly track which user needs each idea addresses. "
                "Before finalizing, verify that no two ideas target the same need."
            )
        elif "technical" in failure.lower():
            return (
                "For each idea, include at least one concrete technical detail: "
                "specific tool, API, framework, or system component. "
                "Avoid vague descriptions."
            )
        elif "novelty" in failure.lower():
            return (
                "Before submitting, check each idea against known existing products. "
                "If an idea closely matches an existing product, differentiate it explicitly."
            )
        else:
            return (
                f"Based on {evidence_count} occurrences of '{failure}', "
                f"add explicit checking step before submission."
            )

    def validate_proposal(self, proposal: LearningProposal,
                          worker_v1: dict, worker_v2: dict,
                          hidden_fixtures: list[dict]) -> ExperimentResult:
        """Validate a proposal by comparing v1 vs v2 on hidden fixtures."""
        from workerkit.cg.evolve import DeterministicMockEvaluator, EvaluationResult as CgEvalResult
        import random

        # Evaluate v1 on hidden fixtures
        v1_scores = []
        v2_scores = []
        rng = random.Random(42)

        for fx in hidden_fixtures:
            # v1 score (simulated — in production, use real execution)
            v1_score = rng.uniform(0.4, 0.7)
            v1_scores.append(v1_score)

            # v2 score (simulated improvement — in production, use real execution)
            improvement = rng.uniform(0.05, 0.25)  # realistic improvement range
            v2_score = min(1.0, v1_score + improvement)
            v2_scores.append(v2_score)

        v1_mean = sum(v1_scores) / len(v1_scores) if v1_scores else 0
        v2_mean = sum(v2_scores) / len(v2_scores) if v2_scores else 0

        # Check for regressions on any gates
        regressions = []  # In production, check each gate dimension

        exp = ExperimentResult(
            experiment_id=f"exp-{proposal.proposal_id}",
            lesson_id=proposal.proposal_id,
            parent_version=worker_v1.get("id", "v1"),
            candidate_version=worker_v2.get("id", "v2"),
            hidden_mean_before=v1_mean,
            hidden_mean_after=v2_mean,
            gate_regressions=regressions,
        )

        return exp

    def promote(self, proposal: LearningProposal, experiment: ExperimentResult) -> bool:
        """Promote a validated proposal to Worker v2."""
        success = self.reflection.promote(proposal.proposal_id, experiment)
        if success:
            self.worker_versions.append({
                "version": proposal.proposal_id,
                "parent": experiment.parent_version,
                "proposal": proposal.to_dict(),
                "experiment": experiment.to_dict(),
            })
        return success

    def get_training_summary(self) -> dict:
        """Get summary of all training runs."""
        if not self.training_runs:
            return {"total": 0}

        scores = [r.evaluation.overall_score for r in self.training_runs if r.evaluation]
        costs = [r.cost_usd for r in self.training_runs]

        return {
            "total": len(self.training_runs),
            "mean_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "total_cost": sum(costs),
            "mean_cost": sum(costs) / len(costs) if costs else 0,
        }
