"""Moltwork Interfaces — the smallest boundaries.

These are the ONLY interfaces Moltwork defines.
Everything else is replaceable behind them.

RuntimeAdapter  → execute work
MemoryRef       → where cognition lives
WorkspaceRef    → where code lives
TrajectoryRef   → what happened (pluggable format)
SkillRef        → procedural assets (Agent Skills standard)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.hashing import sha256, jcs


# ─── RuntimeAdapter ────────────────────────────────────────────────────

@dataclass
class ExecutionResult:
    """Result of executing work through a runtime."""
    ok: bool = False
    output_content: str = ""
    output_hash: str = ""
    artifacts: list[str] = field(default_factory=list)
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    error: str = ""
    error_code: str = ""  # NO_RUNTIME, NOT_EXECUTED, FAIL, TIMEOUT
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "output_hash": self.output_hash,
            "artifacts": self.artifacts,
            "cost_usd": self.cost_usd,
            "duration_seconds": self.duration_seconds,
            "error_code": self.error_code,
        }


@dataclass
class RunContext:
    """Context for a single work execution."""
    run_id: str = ""
    worker_id: str = ""
    workspace: str = ""
    budget_remaining: float = 0.0
    timeout_seconds: int = 300
    allowed_tools: list[str] = field(default_factory=list)
    policy: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "worker_id": self.worker_id,
            "workspace": self.workspace,
            "budget_remaining": self.budget_remaining,
            "allowed_tools": self.allowed_tools,
        }


class RuntimeAdapter:
    """Execute work. Today: Letta. Tomorrow: OpenHands, Hermes, whatever wins."""

    async def execute(self, context: RunContext, task: str) -> ExecutionResult:
        """Execute a task in a workspace."""
        ...

    async def health(self) -> dict:
        """Check runtime health."""
        ...


# ─── MemoryRef ─────────────────────────────────────────────────────────

@dataclass
class MemoryRef:
    """Where cognition lives. Moltwork doesn't implement memory.

    Today: Letta MemFS (Git-backed)
    Tomorrow: anything
    """
    provider: str = "letta-memfs"
    commit: str = ""  # Git commit SHA
    tree_digest: str = ""  # SHA-256 of file tree
    skills_tree_digest: str = ""  # SHA-256 of skills directory

    def content_hash(self) -> str:
        return sha256(jcs({
            "provider": self.provider,
            "commit": self.commit,
            "tree_digest": self.tree_digest,
        }))

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "commit": self.commit,
            "tree_digest": self.tree_digest,
            "skills_tree_digest": self.skills_tree_digest,
        }


# ─── WorkspaceRef ──────────────────────────────────────────────────────

@dataclass
class WorkspaceRef:
    """Where code lives. Git is the version/control substrate."""
    provider: str = "git"
    base_commit: str = ""
    branch: str = ""
    head_commit: str = ""
    worktree_path: str = ""

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "base_commit": self.base_commit,
            "branch": self.branch,
            "head_commit": self.head_commit,
            "worktree_path": self.worktree_path,
        }


# ─── TrajectoryRef ─────────────────────────────────────────────────────

@dataclass
class TrajectoryRef:
    """What happened. Format is pluggable.

    Today: letta-trajectory-v1
    Tomorrow: opentrajectory-0.1 or anything
    """
    format: str = "letta-trajectory-v1"
    uri: str = ""
    sha256: str = ""
    run_id: str = ""

    def to_dict(self) -> dict:
        return {
            "format": self.format,
            "uri": self.uri,
            "sha256": self.sha256,
            "run_id": self.run_id,
        }


# ─── SkillRef ──────────────────────────────────────────────────────────

@dataclass
class SkillRef:
    """Procedural asset using Agent Skills standard.

    No bespoke schema. Use agentskills.io specification.
    """
    format: str = "agent-skills"
    uri: str = ""  # e.g. "skills/hackathon-requirements/"
    git_commit: str = ""
    sha256: str = ""
    name: str = ""

    def to_dict(self) -> dict:
        return {
            "format": self.format,
            "uri": self.uri,
            "git_commit": self.git_commit,
            "sha256": self.sha256,
            "name": self.name,
        }
