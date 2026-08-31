"""School — curriculum + worlds + assessor + feedback.

A World answers: "Can this agent do X?"
A School answers: "How do I make an agent better at X?"

Structure:
  ontology mapping
  curriculum (easy/medium/hard/adversarial)
  WorldPacks
  assessor
  feedback interpreter
  known failure taxonomy
  reference materials
  optional skill/process seeds
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
class CurriculumItem:
    """A single curriculum step: a world to practice on with a difficulty level."""
    world_id: str
    world_version: str
    difficulty: str  # "easy", "medium", "hard", "adversarial"
    focus: str  # what this step targets
    expected_duration_s: float = 60.0
    prerequisites: list[str] = field(default_factory=list)


@dataclass
class SchoolVersion:
    """A complete school: curriculum + worlds + assessor + feedback."""
    school_id: str
    version_id: str
    parent_version: str = ""
    
    task_family: str = ""
    description: str = ""
    
    curriculum: list[CurriculumItem] = field(default_factory=list)
    world_versions: list[str] = field(default_factory=list)
    assessor_version: str = ""
    
    # Reference materials
    reference_docs: list[str] = field(default_factory=list)
    failure_taxonomy: list[str] = field(default_factory=list)
    skill_seeds: list[str] = field(default_factory=list)
    
    # Empirical results
    baseline_score: float = 0.0
    post_curriculum_score: float = 0.0
    held_out_improvement: float = 0.0
    real_world_results: list[dict] = field(default_factory=list)
    
    created_at: float = field(default_factory=time.time)
    
    def content_hash(self) -> str:
        return _sha256({
            "school_id": self.school_id,
            "version_id": self.version_id,
            "curriculum": [{"world": c.world_id, "difficulty": c.difficulty} for c in self.curriculum],
            "assessor_version": self.assessor_version,
        })
    
    def to_dict(self) -> dict:
        return {
            "school_id": self.school_id,
            "version_id": self.version_id,
            "parent_version": self.parent_version,
            "task_family": self.task_family,
            "description": self.description,
            "curriculum": [
                {"world_id": c.world_id, "world_version": c.world_version,
                 "difficulty": c.difficulty, "focus": c.focus}
                for c in self.curriculum
            ],
            "world_versions": self.world_versions,
            "assessor_version": self.assessor_version,
            "reference_docs": self.reference_docs,
            "failure_taxonomy": self.failure_taxonomy,
            "skill_seeds": self.skill_seeds,
            "baseline_score": self.baseline_score,
            "post_curriculum_score": self.post_curriculum_score,
            "held_out_improvement": self.held_out_improvement,
            "real_world_results": self.real_world_results,
            "created_at": self.created_at,
            "content_hash": self.content_hash()[:16],
        }
    
    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "school.json").write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: Path) -> "SchoolVersion":
        data = json.loads((path / "school.json").read_text())
        curriculum = [
            CurriculumItem(**c) for c in data.pop("curriculum", [])
        ]
        return cls(curriculum=curriculum, **{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ─── Pre-built school for competition technical submissions ────────────

def create_competition_school() -> SchoolVersion:
    """Create the default school for competition technical submissions."""
    return SchoolVersion(
        school_id="competition.technical_submission",
        version_id="v1",
        task_family="research.ideation.technical",
        description="Improve workers at competitive technical submissions: hackathons, bounties, grants",
        curriculum=[
            CurriculumItem(
                world_id="requirements-extraction",
                world_version="v1",
                difficulty="easy",
                focus="Extract and organize all requirements from a brief",
            ),
            CurriculumItem(
                world_id="source-verification",
                world_version="v1",
                difficulty="easy",
                focus="Verify claims against real documentation",
            ),
            CurriculumItem(
                world_id="technical-ideation",
                world_version="v1",
                difficulty="medium",
                focus="Generate feasible technical solutions",
            ),
            CurriculumItem(
                world_id="sponsor-integration",
                world_version="v1",
                difficulty="medium",
                focus="Deep integration with sponsor tools/APIs",
            ),
            CurriculumItem(
                world_id="submission-communication",
                world_version="v1",
                difficulty="medium",
                focus="Clear, compelling submission narrative",
            ),
            CurriculumItem(
                world_id="novelty-differentiation",
                world_version="v1",
                difficulty="hard",
                focus="Stand out from existing solutions",
            ),
            CurriculumItem(
                world_id="adversarial-review",
                world_version="v1",
                difficulty="adversarial",
                focus="Defend against hostile evaluation",
            ),
        ],
        world_versions=[
            "requirements-extraction:v1",
            "source-verification:v1",
            "technical-ideation:v1",
            "sponsor-integration:v1",
            "submission-communication:v1",
            "novelty-differentiation:v1",
            "adversarial-review:v1",
        ],
        failure_taxonomy=[
            "missing_explicit_requirement",
            "shallow_sponsor_integration",
            "generic_not_novel",
            "vague_not_specific",
            "broken_demo",
            "poor_communication",
            "over_budget",
            "under_time",
        ],
        skill_seeds=[
            "requirements-audit",
            "evidence-research",
            "constraint-decomposition",
        ],
    )
