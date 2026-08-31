"""Git-native primitives — versions of things that live in Git.

WorkerVersion, WorldVersion, SkillVersion, SchoolVersion, AssessorVersion.
Each is identified by: repo + commit + parent.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


def _sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def _git(args: list[str], cwd: str = ".") -> str:
    """Run a git command and return stdout."""
    try:
        r = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=10, cwd=cwd)
        return r.stdout.strip()
    except Exception:
        return ""


# ─── WorkerVersion ────────────────────────────────────────────────────

@dataclass
class WorkerVersion:
    """A versioned state of a worker: memory + skills + harness + model."""
    worker_id: str
    version_id: str  # git tag or commit hash
    parent_version: str = ""
    
    # Git identities
    memory_commit: str = ""
    skill_tree_commit: str = ""
    mod_commit: str = ""
    
    # Runtime config
    model: str = "mimo-v2.5"
    reasoning_effort: str = "medium"
    toolset: str = "default"
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    promoted: bool = False
    promotion_experiment: str = ""
    
    def content_hash(self) -> str:
        return _sha256({
            "worker_id": self.worker_id,
            "version_id": self.version_id,
            "memory_commit": self.memory_commit,
            "skill_tree_commit": self.skill_tree_commit,
            "mod_commit": self.mod_commit,
            "model": self.model,
        })
    
    def to_dict(self) -> dict:
        return {
            "worker_id": self.worker_id,
            "version_id": self.version_id,
            "parent_version": self.parent_version,
            "memory_commit": self.memory_commit,
            "skill_tree_commit": self.skill_tree_commit,
            "mod_commit": self.mod_commit,
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "toolset": self.toolset,
            "created_at": self.created_at,
            "promoted": self.promoted,
            "promotion_experiment": self.promotion_experiment,
            "content_hash": self.content_hash()[:16],
        }
    
    def tag(self, repo_path: str):
        """Create a Git tag for this version."""
        tag_name = f"worker/{self.worker_id}/{self.version_id}"
        _git(["tag", "-a", tag_name, "-m", f"WorkerVersion {self.version_id}"], cwd=repo_path)
        return tag_name


# ─── WorldVersion ─────────────────────────────────────────────────────

@dataclass
class WorldVersion:
    """A versioned evaluation world: scenarios + graders + rubric."""
    world_id: str
    version_id: str
    repo_url: str = ""
    commit_hash: str = ""
    parent_version: str = ""
    
    # Ontology
    task_family: str = ""
    capabilities: list[str] = field(default_factory=list)
    submission_type: str = ""
    
    # Evaluation config
    gates: list[str] = field(default_factory=list)
    rubric: dict[str, float] = field(default_factory=dict)
    
    # Validity
    world_validity_claim: str = ""  # "validated" | "weak" | "untested"
    external_outcomes_checked: int = 0
    prediction_accuracy: float = 0.0
    
    created_at: float = field(default_factory=time.time)
    
    def content_hash(self) -> str:
        return _sha256({
            "world_id": self.world_id,
            "version_id": self.version_id,
            "commit_hash": self.commit_hash,
            "task_family": self.task_family,
            "gates": self.gates,
        })
    
    def to_dict(self) -> dict:
        return {
            "world_id": self.world_id,
            "version_id": self.version_id,
            "repo_url": self.repo_url,
            "commit_hash": self.commit_hash,
            "parent_version": self.parent_version,
            "task_family": self.task_family,
            "capabilities": self.capabilities,
            "submission_type": self.submission_type,
            "gates": self.gates,
            "rubric": self.rubric,
            "world_validity_claim": self.world_validity_claim,
            "external_outcomes_checked": self.external_outcomes_checked,
            "prediction_accuracy": self.prediction_accuracy,
            "created_at": self.created_at,
            "content_hash": self.content_hash()[:16],
        }


# ─── SkillVersion ─────────────────────────────────────────────────────

@dataclass
class SkillVersion:
    """A versioned skill: reusable procedural capability."""
    skill_id: str
    version_id: str
    parent_version: str = ""
    
    name: str = ""
    description: str = ""
    content: str = ""  # SKILL.md content
    content_hash: str = ""
    
    # Evidence
    times_used: int = 0
    success_rate: float = 0.0
    validated: bool = False
    
    created_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if not self.content_hash and self.content:
            self.content_hash = _sha256(self.content)[:16]
    
    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "version_id": self.version_id,
            "parent_version": self.parent_version,
            "name": self.name,
            "description": self.description,
            "content_hash": self.content_hash,
            "times_used": self.times_used,
            "success_rate": self.success_rate,
            "validated": self.validated,
            "created_at": self.created_at,
        }


# ─── SchoolVersion ────────────────────────────────────────────────────

@dataclass
class SchoolVersion:
    """A versioned school: curriculum + worlds + assessor + feedback."""
    school_id: str
    version_id: str
    parent_version: str = ""
    
    task_family: str = ""
    curriculum: list[dict] = field(default_factory=list)  # [{world_id, difficulty, focus}]
    world_versions: list[str] = field(default_factory=list)  # world version IDs
    assessor_version: str = ""
    
    # Empirical results
    baseline_score: float = 0.0
    post_curriculum_score: float = 0.0
    held_out_improvement: float = 0.0
    real_world_results: list[dict] = field(default_factory=list)
    
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "school_id": self.school_id,
            "version_id": self.version_id,
            "parent_version": self.parent_version,
            "task_family": self.task_family,
            "curriculum": self.curriculum,
            "world_versions": self.world_versions,
            "assessor_version": self.assessor_version,
            "baseline_score": self.baseline_score,
            "post_curriculum_score": self.post_curriculum_score,
            "held_out_improvement": self.held_out_improvement,
            "real_world_results": self.real_world_results,
            "created_at": self.created_at,
        }


# ─── AssessorVersion ──────────────────────────────────────────────────

@dataclass
class AssessorVersion:
    """A versioned assessor: model of what "good" means."""
    assessor_id: str
    version_id: str
    parent_version: str = ""
    
    # Config
    gates: list[str] = field(default_factory=list)
    rubric: dict[str, float] = field(default_factory=dict)
    judge_model: str = ""
    
    # Calibration
    predicted_rankings: list[dict] = field(default_factory=list)
    actual_outcomes: list[dict] = field(default_factory=list)
    calibration_error: float = 0.0
    
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "assessor_id": self.assessor_id,
            "version_id": self.version_id,
            "parent_version": self.parent_version,
            "gates": self.gates,
            "rubric": self.rubric,
            "judge_model": self.judge_model,
            "calibration_error": self.calibration_error,
            "created_at": self.created_at,
        }
