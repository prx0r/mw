"""AssetVersion — content-addressed worker build.

An .af is a portable, immutable snapshot of a worker at a point in time.
Every meaningful change creates a new AssetVersion.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from core.hashing import sha256, jcs, SCHEMA_AF


@dataclass
class AssetVersion:
    """Immutable version of a worker asset.

    Content-addressed: the digest uniquely identifies this exact configuration.
    """
    schema: str = SCHEMA_AF
    worker_id: str = ""
    version: str = "v1"

    # Runtime config (what is this worker?)
    runtime_type: str = "letta"
    runtime_version: str = ""
    model: str = ""
    model_provider: str = ""

    # Cognition (what has it learned?)
    memory_digest: str = ""  # SHA-256 of Letta memory state
    memory_lineage: list[str] = field(default_factory=list)  # parent memory digests
    skills_digest: str = ""  # SHA-256 of skills tree
    core_memory_hash: str = ""  # SHA-256 of core memory blocks

    # Capabilities (what can it do?)
    tools: list[str] = field(default_factory=list)
    tool_permissions: dict = field(default_factory=dict)
    processes: list[dict] = field(default_factory=list)  # [{name, version, hash}]

    # Performance (proven track record)
    total_runs: int = 0
    successful_runs: int = 0
    total_cost_usd: float = 0.0
    total_earned_usd: float = 0.0

    # Provenance
    parent_digest: str = ""  # previous version digest
    source_commit: str = ""
    created_at: float = field(default_factory=time.time)

    # Content tree (what files are in this asset?)
    file_tree: list[dict] = field(default_factory=list)  # [{path, digest, size}]

    def content_digest(self) -> str:
        """Content-addressed digest of this exact configuration."""
        d = {
            "schema": self.schema,
            "worker_id": self.worker_id,
            "version": self.version,
            "runtime_type": self.runtime_type,
            "runtime_version": self.runtime_version,
            "model": self.model,
            "model_provider": self.model_provider,
            "memory_digest": self.memory_digest,
            "memory_lineage": self.memory_lineage,
            "skills_digest": self.skills_digest,
            "core_memory_hash": self.core_memory_hash,
            "tools": self.tools,
            "tool_permissions": self.tool_permissions,
            "processes": self.processes,
            "parent_digest": self.parent_digest,
            "source_commit": self.source_commit,
            "file_tree": self.file_tree,
        }
        return sha256(jcs(d))

    def file_tree_root(self) -> str:
        """Merkle root over file tree entries."""
        if not self.file_tree:
            return ""
        leaves = [sha256(json.dumps(f, sort_keys=True)) for f in self.file_tree]
        # Simple merkle
        while len(leaves) > 1:
            if len(leaves) % 2:
                leaves.append("")
            leaves = [sha256(leaves[i] + leaves[i+1]) for i in range(0, len(leaves), 2)]
        return leaves[0]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["content_digest"] = self.content_digest()
        d["file_tree_root"] = self.file_tree_root()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AssetVersion":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})

    def save(self, path: str | Path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "AssetVersion":
        return cls.from_dict(json.loads(Path(path).read_text()))

    def new_version(self, **changes) -> "AssetVersion":
        """Create a new version with changes, preserving lineage."""
        d = self.to_dict()
        d.update(changes)
        d["parent_digest"] = self.content_digest()
        d["version"] = f"v{int(self.version.lstrip('v')) + 1}"
        d["created_at"] = time.time()
        return cls.from_dict(d)
