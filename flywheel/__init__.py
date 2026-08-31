"""Flywheel — the complete opportunity → rubric → submit → review → refine loop.

This is the core Moltwork cycle:
1. Find opportunity (Oracle)
2. Research the opportunity (build understanding)
3. Create rubric (what would win)
4. Generate submission (worker produces artifact)
5. Evaluate (assessor checks against rubric)
6. Refine (feedback loop)
7. Submit (when ready)
8. Post-run (learn, molte, optimize)

Every step is recorded in Git and HydraDB.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


# ─── Opportunity types ────────────────────────────────────────────────

SUBMISSION_TYPES = {
    "technical_ideation": {
        "gates": ["G0_format", "G1_requirements", "G2_feasibility", "G3_specificity", "G5_novelty"],
        "rubric": {
            "requirements_coverage": 0.25,
            "technical_feasibility": 0.20,
            "specificity": 0.20,
            "novelty": 0.15,
            "evidence": 0.10,
            "rationale": 0.10,
        },
        "capabilities": ["text.reason", "code.understand", "search.web"],
    },
    "technical_implementation": {
        "gates": ["G0_format", "G1_structure", "G2_correctness", "G3_quality", "G5_documentation"],
        "rubric": {
            "builds_and_runs": 0.25,
            "tests_pass": 0.20,
            "code_quality": 0.20,
            "documentation": 0.15,
            "novelty": 0.10,
            "integration": 0.10,
        },
        "capabilities": ["code.write", "code.review", "deploy.local"],
    },
    "research_analysis": {
        "gates": ["G0_format", "G1_completeness", "G2_accuracy", "G4_evidence"],
        "rubric": {
            "source_quality": 0.25,
            "completeness": 0.20,
            "accuracy": 0.20,
            "actionability": 0.20,
            "clarity": 0.15,
        },
        "capabilities": ["search.web", "source.verify", "text.reason"],
    },
}


# ─── Rubric generation ────────────────────────────────────────────────

@dataclass
class Rubric:
    """Evaluation rubric for a specific opportunity."""
    opportunity_id: str
    submission_type: str
    created_at: float = field(default_factory=time.time)
    
    # What the worker sees (public)
    requirements: list[str] = field(default_factory=list)
    judging_criteria: list[str] = field(default_factory=list)
    recommended_strategy: str = ""
    
    # What the evaluator uses (hidden)
    rubric_weights: dict[str, float] = field(default_factory=dict)
    hidden_checks: list[dict] = field(default_factory=list)
    quality_gates: list[str] = field(default_factory=list)
    
    # Learning from past runs
    past_wins: list[dict] = field(default_factory=list)
    past_failures: list[dict] = field(default_factory=list)
    failure_patterns: list[str] = field(default_factory=list)
    
    def content_hash(self) -> str:
        return _sha256({
            "opportunity_id": self.opportunity_id,
            "submission_type": self.submission_type,
            "requirements": self.requirements,
            "rubric_weights": self.rubric_weights,
        })
    
    def to_dict(self) -> dict:
        return {
            "opportunity_id": self.opportunity_id,
            "submission_type": self.submission_type,
            "created_at": self.created_at,
            "requirements": self.requirements,
            "judging_criteria": self.judging_criteria,
            "recommended_strategy": self.recommended_strategy,
            "rubric_weights": self.rubric_weights,
            "hidden_checks": self.hidden_checks,
            "quality_gates": self.quality_gates,
            "past_wins_count": len(self.past_wins),
            "past_failures_count": len(self.past_failures),
            "failure_patterns": self.failure_patterns,
            "content_hash": self.content_hash()[:16],
        }
    
    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "rubric.json").write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: Path) -> "Rubric":
        data = json.loads((path / "rubric.json").read_text())
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def generate_rubric(opportunity: dict, past_runs: list[dict] = None) -> Rubric:
    """Generate a rubric for an opportunity based on its type and past runs."""
    opp_type = opportunity.get("submission_type", "technical_ideation")
    type_config = SUBMISSION_TYPES.get(opp_type, SUBMISSION_TYPES["technical_ideation"])
    
    rubric = Rubric(
        opportunity_id=opportunity.get("id", f"opp-{int(time.time())}"),
        submission_type=opp_type,
        requirements=opportunity.get("requirements", []),
        judging_criteria=opportunity.get("judging_criteria", []),
        rubric_weights=type_config["rubric"].copy(),
        quality_gates=type_config["gates"],
    )
    
    # Analyze past runs to improve rubric
    if past_runs:
        wins = [r for r in past_runs if r.get("outcome") == "won"]
        losses = [r for r in past_runs if r.get("outcome") == "lost"]
        
        rubric.past_wins = wins[:5]
        rubric.past_failures = losses[:5]
        
        # Extract failure patterns
        failure_reasons = []
        for loss in losses:
            if loss.get("failure_reason"):
                failure_reasons.append(loss["failure_reason"])
            if loss.get("gate_failures"):
                failure_reasons.extend(loss["gate_failures"])
        
        rubric.failure_patterns = list(set(failure_reasons))[:10]
        
        # Adjust weights based on what caused failures
        if "novelty" in str(failure_reasons).lower():
            rubric.rubric_weights["novelty"] = min(0.30, rubric.rubric_weights.get("novelty", 0.15) + 0.05)
        
        if "requirements" in str(failure_reasons).lower():
            rubric.rubric_weights["requirements_coverage"] = min(0.35, rubric.rubric_weights.get("requirements_coverage", 0.25) + 0.05)
    
    # Generate recommended strategy
    rubric.recommended_strategy = _generate_strategy(opportunity, rubric)
    
    # Generate hidden checks
    rubric.hidden_checks = _generate_hidden_checks(opp_type, opportunity)
    
    return rubric


def _generate_strategy(opportunity: dict, rubric: Rubric) -> str:
    """Generate a recommended strategy based on opportunity and rubric."""
    parts = []
    
    # Primary focus based on highest-weighted criterion
    top_criterion = max(rubric.rubric_weights, key=rubric.rubric_weights.get)
    parts.append(f"Focus on {top_criterion.replace('_', ' ')} (weight: {rubric.rubric_weights[top_criterion]:.0%})")
    
    # Address failure patterns
    if rubric.failure_patterns:
        parts.append(f"Avoid past failures: {', '.join(rubric.failure_patterns[:3])}")
    
    # Build on wins
    if rubric.past_wins:
        parts.append(f"Build on past success patterns")
    
    return ". ".join(parts)


def _generate_hidden_checks(sub_type: str, opportunity: dict) -> list[dict]:
    """Generate hidden evaluation checks."""
    checks = []
    
    if sub_type == "technical_ideation":
        checks.extend([
            {"name": "has_code_reference", "description": "References specific code/API/protocol", "weight": 0.15},
            {"name": "addresses_all_requirements", "description": "Every requirement addressed", "weight": 0.20},
            {"name": "differentiates_from_existing", "description": "Not just a clone of existing solutions", "weight": 0.15},
            {"name": "concrete_not_vague", "description": "Specific tools, versions, numbers", "weight": 0.15},
        ])
    elif sub_type == "technical_implementation":
        checks.extend([
            {"name": "tests_exist", "description": "Has test files", "weight": 0.15},
            {"name": "builds_cleanly", "description": "No warnings/errors on build", "weight": 0.15},
            {"name": "has_readme", "description": "README with setup instructions", "weight": 0.10},
        ])
    
    return checks


# ─── Flywheel state ───────────────────────────────────────────────────

@dataclass
class FlywheelRun:
    """State of a complete flywheel cycle for one opportunity."""
    run_id: str
    opportunity_id: str
    worker_id: str
    worker_version: str
    
    # Research phase
    opportunity_research: dict = field(default_factory=dict)
    rubric: Rubric | None = None
    
    # Generation phase
    artifacts: list[dict] = field(default_factory=list)
    current_artifact_hash: str = ""
    
    # Evaluation phase
    evaluations: list[dict] = field(default_factory=list)
    best_score: float = 0.0
    iteration_count: int = 0
    
    # Submission phase
    submitted: bool = False
    submission_url: str = ""
    outcome: str = ""  # won | lost | pending
    reward_usd: float = 0.0
    
    # Post-run
    lessons_learned: list[str] = field(default_factory=list)
    assets_molted: list[str] = field(default_factory=list)
    
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    
    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "flywheel.json").write_text(json.dumps(self.to_dict(), indent=2))
    
    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "opportunity_id": self.opportunity_id,
            "worker_id": self.worker_id,
            "worker_version": self.worker_version,
            "rubric": self.rubric.to_dict() if self.rubric else None,
            "artifacts": self.artifacts,
            "current_artifact_hash": self.current_artifact_hash,
            "evaluations": self.evaluations,
            "best_score": self.best_score,
            "iteration_count": self.iteration_count,
            "submitted": self.submitted,
            "submission_url": self.submission_url,
            "outcome": self.outcome,
            "reward_usd": self.reward_usd,
            "lessons_learned": self.lessons_learned,
            "assets_molted": self.assets_molted,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
    
    @classmethod
    def load(cls, path: Path) -> "FlywheelRun":
        data = json.loads((path / "flywheel.json").read_text())
        rubric_data = data.pop("rubric", None)
        rubric = Rubric(**rubric_data) if rubric_data else None
        return cls(rubric=rubric, **{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ─── Post-run molting ─────────────────────────────────────────────────

@dataclass
class MoltingResult:
    """Assets extracted and lessons learned from a completed run."""
    run_id: str
    extracted_skills: list[dict] = field(default_factory=list)
    extracted_processes: list[dict] = field(default_factory=list)
    extracted_patterns: list[dict] = field(default_factory=list)
    memory_updates: list[dict] = field(default_factory=list)
    rubric_updates: list[dict] = field(default_factory=list)
    world_updates: list[dict] = field(default_factory=list)
    
    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "molting.json").write_text(json.dumps(self.to_dict(), indent=2))
    
    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "extracted_skills": self.extracted_skills,
            "extracted_processes": self.extracted_processes,
            "extracted_patterns": self.extracted_patterns,
            "memory_updates": self.memory_updates,
            "rubric_updates": self.rubric_updates,
            "world_updates": self.world_updates,
        }


def molte_run(run: FlywheelRun, artifact_content: str, evaluation: dict) -> MoltingResult:
    """Extract reusable assets from a completed run."""
    result = MoltingResult(run_id=run.run_id)
    
    # Extract skills from successful runs
    if run.outcome == "won":
        result.extracted_skills.append({
            "name": f"skill-{run.opportunity_id[:20]}",
            "type": "submission_pattern",
            "content": f"Successful {run.rubric.submission_type} submission for {run.opportunity_id}",
            "evidence": [run.current_artifact_hash],
        })
    
    # Extract failure patterns
    if run.outcome == "lost":
        for pattern in run.rubric.failure_patterns if run.rubric else []:
            result.extracted_patterns.append({
                "pattern": pattern,
                "context": run.opportunity_id,
                "action": f"avoid: {pattern}",
            })
    
    # Update rubric based on what worked/didn't
    if evaluation:
        gate_results = evaluation.get("gate_results", {})
        failed_gates = [g for g, p in gate_results.items() if not p]
        if failed_gates:
            result.rubric_updates.append({
                "type": "increase_weight",
                "gate": failed_gates[0],
                "reason": f"Gate {failed_gates[0]} failed in run {run.run_id}",
            })
    
    return result
