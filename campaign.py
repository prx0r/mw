"""Campaign — the Git-native unit of work.

An Oracle opportunity instantiates a Campaign.
The Campaign contains everything: opportunity snapshot, strategy, worlds, experiments, submissions, outcome.
Almost everything is a Git reference, not copied material.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


def _sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


# ─── SuccessModel ─────────────────────────────────────────────────────

@dataclass
class SuccessModel:
    """What would win this opportunity? Constructed before work starts.
    
    Compiles into CGE worlds/evaluators.
    Worker sees public strategy.
    Hidden tests stay hidden.
    """
    # Hard gates (must pass or submission is invalid)
    hard_gates: dict[str, bool] = field(default_factory=dict)
    
    # Scoring dimensions (what distinguishes winners)
    dimensions: dict[str, float] = field(default_factory=dict)
    
    # What we're uncertain about
    uncertainty: dict[str, str] = field(default_factory=dict)
    
    # Research findings
    similar_campaigns: list[dict] = field(default_factory=list)
    winning_patterns: list[str] = field(default_factory=list)
    known_failures: list[str] = field(default_factory=list)
    
    def content_hash(self) -> str:
        return _sha256({
            "hard_gates": self.hard_gates,
            "dimensions": self.dimensions,
            "winning_patterns": self.winning_patterns,
        })
    
    def to_dict(self) -> dict:
        return {
            "hard_gates": self.hard_gates,
            "dimensions": self.dimensions,
            "uncertainty": self.uncertainty,
            "similar_campaigns": self.similar_campaigns,
            "winning_patterns": self.winning_patterns,
            "known_failures": self.known_failures,
            "content_hash": self.content_hash()[:16],
        }
    
    def to_rubric(self) -> dict:
        """Compile SuccessModel into a rubric for CGE evaluation."""
        return {
            "hard_gates": {k: v for k, v in self.hard_gates.items()},
            "rubric_weights": self.dimensions,
        }
    
    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "success_model.json").write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: Path) -> "SuccessModel":
        data = json.loads((path / "success_model.json").read_text())
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def generate_success_model(opportunity: dict, hydra_findings: dict = None) -> SuccessModel:
    """Generate a SuccessModel from opportunity + Hydra research.
    
    Phase 0: model "what would win?" before worker starts.
    """
    model = SuccessModel()
    
    # Extract hard gates from requirements
    for req in opportunity.get("requirements", []):
        key = req.lower().replace(" ", "_")[:30]
        model.hard_gates[key] = True
    
    # Build dimensions from judging criteria
    criteria = opportunity.get("judging_criteria", [])
    if criteria:
        weight = 1.0 / len(criteria)
        for c in criteria:
            key = c.lower().replace(" ", "_")[:30]
            model.dimensions[key] = round(weight, 2)
    
    # Add default dimensions if none provided
    if not model.dimensions:
        model.dimensions = {
            "requirements_coverage": 0.25,
            "technical_feasibility": 0.20,
            "specificity": 0.20,
            "novelty": 0.15,
            "evidence": 0.10,
            "rationale": 0.10,
        }
    
    # Research from Hydra
    if hydra_findings:
        model.similar_campaigns = hydra_findings.get("similar_campaigns", [])
        model.winning_patterns = hydra_findings.get("winning_patterns", [])
        model.known_failures = hydra_findings.get("known_failures", [])
    
    # Default uncertainty
    model.uncertainty = {
        "originality_weight": "high",
        "presentation_weight": "medium",
    }
    
    return model


# ─── Campaign ─────────────────────────────────────────────────────────

@dataclass
class Campaign:
    """Git-native campaign: everything about one opportunity.
    
    Structure:
      campaign.yaml
      opportunity/ (rules, sponsor docs, API docs, evidence)
      strategy/ (success model, rubric, assumptions)
      worlds/ (locked world references)
      experiments/ (E001, E002, ...)
      submissions/ (candidate-a, candidate-b, final)
      outcome/ (result.json, feedback.md)
    """
    campaign_id: str
    opportunity_id: str
    worker_id: str
    
    # Strategy
    success_model: SuccessModel | None = None
    
    # State
    status: str = "created"  # created | researching | building | reviewing | submitted | completed
    current_phase: str = ""
    
    # Budget
    budget_usd: float = 5.0
    spent_usd: float = 0.0
    
    # Git references
    world_refs: list[dict] = field(default_factory=list)
    worker_ref: str = ""  # "repo:commit"
    
    # Iterations
    runs: list[dict] = field(default_factory=list)
    best_score: float = 0.0
    iteration_count: int = 0
    
    # Outcome
    submitted: bool = False
    submission_url: str = ""
    outcome: str = ""  # won | lost | pending
    reward_usd: float = 0.0
    
    # Molting results
    molting_candidates: list[dict] = field(default_factory=list)
    
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    
    def content_hash(self) -> str:
        return _sha256({
            "campaign_id": self.campaign_id,
            "opportunity_id": self.opportunity_id,
            "worker_id": self.worker_id,
            "status": self.status,
        })
    
    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "opportunity_id": self.opportunity_id,
            "worker_id": self.worker_id,
            "status": self.status,
            "current_phase": self.current_phase,
            "budget_usd": self.budget_usd,
            "spent_usd": self.spent_usd,
            "world_refs": self.world_refs,
            "worker_ref": self.worker_ref,
            "runs": self.runs,
            "best_score": self.best_score,
            "iteration_count": self.iteration_count,
            "submitted": self.submitted,
            "submission_url": self.submission_url,
            "outcome": self.outcome,
            "reward_usd": self.reward_usd,
            "molting_candidates": self.molting_candidates,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "success_model": self.success_model.to_dict() if self.success_model else None,
        }
    
    def save(self, data_dir: Path):
        """Save campaign to Git-native directory structure."""
        campaign_dir = data_dir / "campaigns" / self.campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)
        
        # Campaign manifest
        (campaign_dir / "campaign.json").write_text(json.dumps(self.to_dict(), indent=2))
        
        # Success model
        if self.success_model:
            self.success_model.save(campaign_dir / "strategy")
        
        return campaign_dir
    
    @classmethod
    def load(cls, campaign_dir: Path) -> "Campaign":
        data = json.loads((campaign_dir / "campaign.json").read_text())
        sm_data = data.pop("success_model", None)
        success_model = SuccessModel(**sm_data) if sm_data else None
        return cls(success_model=success_model, **{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def can_continue(self) -> bool:
        """Check if campaign can continue (budget + status)."""
        return self.status in ("created", "researching", "building", "reviewing") and self.spent_usd < self.budget_usd
    
    def record_cost(self, amount: float):
        self.spent_usd += amount
    
    def advance(self, new_status: str):
        self.status = new_status
        self.current_phase = new_status
