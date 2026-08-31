"""SearchSpec — typed search object for exploration.

Every exploration mutates a typed thing.
Hydra records the search itself, not just the result.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


def _sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


@dataclass
class SearchSpec:
    """A typed search specification for exploration."""
    
    # What we're searching for
    target_type: str  # idea | process | memory | skill | worker-config | assessor | world | code
    
    # Objective
    world_ref: str = ""  # Harbor task ref
    assessor_ref: str = ""  # evaluator ref
    
    # Optimizer
    optimizer_kind: str = "gepa"  # gepa | openevolve | random | human
    
    # Budget
    max_candidates: int = 20
    max_cost_usd: float = 2.0
    max_iterations: int = 10
    
    # Constraints
    model_fixed: bool = True
    worker_fixed: bool = True
    
    # Dimensions to optimize
    dimensions: list[str] = field(default_factory=lambda: ["novelty", "feasibility", "requirements_coverage"])
    
    # Metadata
    campaign_id: str = ""
    created_at: float = field(default_factory=time.time)
    
    # Results
    candidates_evaluated: int = 0
    best_score: float = 0.0
    best_candidate_id: str = ""
    pareto_front: list[dict] = field(default_factory=list)
    
    def content_hash(self) -> str:
        return _sha256({
            "target_type": self.target_type,
            "optimizer_kind": self.optimizer_kind,
            "dimensions": self.dimensions,
            "max_candidates": self.max_candidates,
        })
    
    def to_dict(self) -> dict:
        return {
            "target_type": self.target_type,
            "world_ref": self.world_ref,
            "assessor_ref": self.assessor_ref,
            "optimizer_kind": self.optimizer_kind,
            "max_candidates": self.max_candidates,
            "max_cost_usd": self.max_cost_usd,
            "max_iterations": self.max_iterations,
            "model_fixed": self.model_fixed,
            "worker_fixed": self.worker_fixed,
            "dimensions": self.dimensions,
            "campaign_id": self.campaign_id,
            "created_at": self.created_at,
            "candidates_evaluated": self.candidates_evaluated,
            "best_score": self.best_score,
            "best_candidate_id": self.best_candidate_id,
            "content_hash": self.content_hash()[:16],
        }
    
    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "search_spec.json").write_text(json.dumps(self.to_dict(), indent=2))


@dataclass
class SearchResult:
    """Result of a search: candidates + selections."""
    search_spec_hash: str
    candidates: list[dict] = field(default_factory=list)
    selected: str = ""  # candidate_id
    pareto_front: list[str] = field(default_factory=list)  # candidate_ids
    total_cost_usd: float = 0.0
    total_time_s: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "search_spec_hash": self.search_spec_hash,
            "candidates": self.candidates,
            "selected": self.selected,
            "pareto_front": self.pareto_front,
            "total_cost_usd": self.total_cost_usd,
            "total_time_s": self.total_time_s,
        }
