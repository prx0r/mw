"""Letta Lineage — version lineage tracking for workers.

Tracks the evolutionary history of a worker through memory/skill changes.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.hashing import sha256, jcs


@dataclass
class VersionNode:
    """One node in the worker version lineage."""
    version_id: str = ""  # content digest of the asset version
    parent_id: str = ""  # previous version digest
    memory_digest: str = ""
    skills_digest: str = ""
    created_at: float = field(default_factory=time.time)
    run_count: int = 0
    success_count: int = 0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "version_id": self.version_id,
            "parent_id": self.parent_id,
            "memory_digest": self.memory_digest,
            "skills_digest": self.skills_digest,
            "created_at": self.created_at,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "metadata": self.metadata,
        }


@dataclass
class Lineage:
    """Complete lineage of a worker through versions."""
    worker_id: str = ""
    versions: list[VersionNode] = field(default_factory=list)

    @property
    def current_version(self) -> VersionNode | None:
        return self.versions[-1] if self.versions else None

    @property
    def head_digest(self) -> str:
        return self.current_version.version_id if self.current_version else ""

    def add_version(self, version_id: str, memory_digest: str = "",
                    skills_digest: str = "", metadata: dict | None = None) -> VersionNode:
        """Add a new version to the lineage."""
        parent = self.head_digest
        node = VersionNode(
            version_id=version_id,
            parent_id=parent,
            memory_digest=memory_digest,
            skills_digest=skills_digest,
            metadata=metadata or {},
        )
        self.versions.append(node)
        return node

    def path_to(self, version_id: str) -> list[VersionNode]:
        """Get the path from HEAD to a specific version."""
        result = []
        for v in reversed(self.versions):
            result.append(v)
            if v.version_id == version_id:
                break
        return list(reversed(result))

    def ancestors(self, version_id: str) -> list[str]:
        """Get all ancestor version IDs."""
        path = self.path_to(version_id)
        return [v.version_id for v in path[:-1]]

    def diff(self, v1: str, v2: str) -> dict:
        """Compare two versions."""
        path1 = self.path_to(v1)
        path2 = self.path_to(v2)
        if not path1 or not path2:
            return {"error": "version not found"}
        a, b = path1[0], path2[0]
        return {
            "from": v1,
            "to": v2,
            "memory_changed": a.memory_digest != b.memory_digest,
            "skills_changed": a.skills_digest != b.skills_digest,
            "runs_between": sum(v.run_count for v in self.path_to(v2) if v.version_id != v1),
        }

    def to_dict(self) -> dict:
        return {
            "worker_id": self.worker_id,
            "versions": [v.to_dict() for v in self.versions],
            "head": self.head_digest,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Lineage":
        versions = [VersionNode(**v) for v in d.get("versions", [])]
        return cls(worker_id=d.get("worker_id", ""), versions=versions)

    def save(self, path: str | Path):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "Lineage":
        return cls.from_dict(json.loads(Path(path).read_text()))


class LineageTracker:
    """Track lineages for multiple workers."""

    def __init__(self, data_dir: str = "data/lineages"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._lineages: dict[str, Lineage] = {}

    def get(self, worker_id: str) -> Lineage:
        """Get or create lineage for a worker."""
        if worker_id not in self._lineages:
            path = self.data_dir / f"{worker_id}.json"
            if path.exists():
                self._lineages[worker_id] = Lineage.load(path)
            else:
                self._lineages[worker_id] = Lineage(worker_id=worker_id)
        return self._lineages[worker_id]

    def record_version(self, worker_id: str, version_id: str,
                       memory_digest: str = "", skills_digest: str = "",
                       metadata: dict | None = None) -> VersionNode:
        """Record a new version for a worker."""
        lineage = self.get(worker_id)
        node = lineage.add_version(version_id, memory_digest, skills_digest, metadata)
        lineage.save(self.data_dir / f"{worker_id}.json")
        return node

    def list_workers(self) -> list[str]:
        """List all tracked workers."""
        return [f.stem for f in self.data_dir.glob("*.json")]

    def summary(self, worker_id: str) -> dict:
        """Get summary of a worker's lineage."""
        lineage = self.get(worker_id)
        return {
            "worker_id": worker_id,
            "total_versions": len(lineage.versions),
            "head": lineage.head_digest,
            "total_runs": sum(v.run_count for v in lineage.versions),
            "total_successes": sum(v.success_count for v in lineage.versions),
        }
