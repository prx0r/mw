"""OpportunityResearchPack — evidence-grounded context for a specific opportunity.

Split into PUBLIC strategy (given to worker) and HIDDEN eval (used by assessor).
This prevents evaluation gaming: the worker sees requirements and strategy,
the assessor independently checks hidden criteria.
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
class CriterionCheck:
    """A single evaluation criterion with its check method."""
    name: str
    description: str
    check_type: str  # "deterministic", "llm_rubric", "pairwise"
    weight: float = 1.0
    hidden: bool = False  # if True, worker doesn't see this


@dataclass
class OpportunityResearchPack:
    """Complete research context for an opportunity.

    PUBLIC (worker sees): requirements, strategy, technical docs, known patterns.
    HIDDEN (assessor uses): evaluation criteria, quality gates, comparison baseline.
    """
    opportunity_id: str
    created_at: float = field(default_factory=time.time)

    # PUBLIC — given to worker
    title: str = ""
    description: str = ""
    requirements: list[str] = field(default_factory=list)
    technical_docs: str = ""
    judging_criteria: list[str] = field(default_factory=list)
    recommended_strategy: str = ""
    known_failure_modes: list[str] = field(default_factory=list)
    similar_past_wins: list[dict] = field(default_factory=list)
    budget_hint: float = 0.0
    deadline: str = ""

    # HIDDEN — assessor only
    hidden_criteria: list[CriterionCheck] = field(default_factory=list)
    quality_gates: list[str] = field(default_factory=list)
    comparison_baseline: str = ""  # hash of previous best submission
    rubric_version: str = ""

    def public_dict(self) -> dict:
        """What the worker sees."""
        return {
            "opportunity_id": self.opportunity_id,
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "technical_docs": self.technical_docs,
            "judging_criteria": self.judging_criteria,
            "recommended_strategy": self.recommended_strategy,
            "known_failure_modes": self.known_failure_modes,
            "similar_past_wins": self.similar_past_wins,
            "budget_hint": self.budget_hint,
            "deadline": self.deadline,
        }

    def hidden_dict(self) -> dict:
        """What the assessor uses (worker never sees this)."""
        return {
            "opportunity_id": self.opportunity_id,
            "hidden_criteria": [
                {"name": c.name, "description": c.description, "check_type": c.check_type, "weight": c.weight}
                for c in self.hidden_criteria
            ],
            "quality_gates": self.quality_gates,
            "comparison_baseline": self.comparison_baseline,
            "rubric_version": self.rubric_version,
        }

    def content_hash(self) -> str:
        return _sha256({
            "opportunity_id": self.opportunity_id,
            "requirements": self.requirements,
            "hidden_criteria": [c.name for c in self.hidden_criteria],
            "rubric_version": self.rubric_version,
        })

    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "public.json").write_text(json.dumps(self.public_dict(), indent=2))
        (path / "hidden.json").write_text(json.dumps(self.hidden_dict(), indent=2))
        (path / "meta.json").write_text(json.dumps({
            "content_hash": self.content_hash(),
            "created_at": self.created_at,
        }, indent=2))

    @classmethod
    def load(cls, path: Path) -> "OpportunityResearchPack":
        public = json.loads((path / "public.json").read_text())
        hidden = json.loads((path / "hidden.json").read_text())
        meta = json.loads((path / "meta.json").read_text())
        return cls(
            opportunity_id=public["opportunity_id"],
            created_at=meta.get("created_at", 0),
            title=public.get("title", ""),
            description=public.get("description", ""),
            requirements=public.get("requirements", []),
            technical_docs=public.get("technical_docs", ""),
            judging_criteria=public.get("judging_criteria", []),
            recommended_strategy=public.get("recommended_strategy", ""),
            known_failure_modes=public.get("known_failure_modes", []),
            similar_past_wins=public.get("similar_past_wins", []),
            budget_hint=public.get("budget_hint", 0),
            deadline=public.get("deadline", ""),
            hidden_criteria=[
                CriterionCheck(**c) for c in hidden.get("hidden_criteria", [])
            ],
            quality_gates=hidden.get("quality_gates", []),
            comparison_baseline=hidden.get("comparison_baseline", ""),
            rubric_version=hidden.get("rubric_version", ""),
        )
