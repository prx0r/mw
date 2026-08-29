"""Letta Snapshot — export Letta agent state as portable snapshot.

Produces a content-addressed snapshot of a Letta agent's cognitive state.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from core.hashing import sha256, jcs, SCHEMA_SNAPSHOT


@dataclass
class MemoryBlock:
    """One memory block from Letta."""
    label: str = ""
    digest: str = ""  # SHA-256 of block content
    size_bytes: int = 0


@dataclass
class SkillEntry:
    """One skill from Letta MemFS."""
    path: str = ""
    digest: str = ""  # SHA-256 of skill content
    size_bytes: int = 0


@dataclass
class LettaSnapshot:
    """Content-addressed snapshot of a Letta agent's cognitive state.

    This is what .af contains for the cognition layer.
    The public version reveals digests, not contents.
    """
    schema: str = SCHEMA_SNAPSHOT
    agent_type: str = "letta_v1_agent"
    agent_id: str = ""

    # Model config
    model: str = ""
    model_provider: str = ""
    model_settings_digest: str = ""

    # Core memory blocks
    blocks: list[MemoryBlock] = field(default_factory=list)

    # MemFS (git-backed)
    memfs_root_digest: str = ""
    memfs_files: list[dict] = field(default_factory=list)  # [{path, digest, size}]

    # Skills
    skills: list[SkillEntry] = field(default_factory=list)
    skills_tree_digest: str = ""

    # Tool schema
    tool_schema_digest: str = ""

    # Message state
    message_state_digest: str = ""

    # Metadata
    snapshot_time: float = field(default_factory=time.time)
    memfs_commit: str = ""  # git commit hash if available

    def content_digest(self) -> str:
        """Content-addressed digest of this snapshot."""
        d = {
            "schema": self.schema,
            "agent_id": self.agent_id,
            "model": self.model,
            "model_provider": self.model_provider,
            "model_settings_digest": self.model_settings_digest,
            "blocks": [{"label": b.label, "digest": b.digest} for b in self.blocks],
            "memfs_root_digest": self.memfs_root_digest,
            "skills_tree_digest": self.skills_tree_digest,
            "tool_schema_digest": self.tool_schema_digest,
            "message_state_digest": self.message_state_digest,
            "memfs_commit": self.memfs_commit,
        }
        return sha256(jcs(d))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["content_digest"] = self.content_digest()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "LettaSnapshot":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        blocks = [MemoryBlock(**b) for b in d.get("blocks", [])]
        d["blocks"] = blocks
        return cls(**{k: v for k, v in d.items() if k in known})

    def save(self, path: str | Path):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "LettaSnapshot":
        return cls.from_dict(json.loads(Path(path).read_text()))


class LettaSnapshotExporter:
    """Export Letta agent state as a LettaSnapshot.

    In production, this talks to the Letta SDK.
    For now, produces a snapshot from available data.
    """

    def snapshot_from_agent(self, agent_id: str, model: str = "",
                            blocks: list[dict] | None = None,
                            memfs_commit: str = "",
                            memfs_files: list[dict] | None = None,
                            skills: list[dict] | None = None) -> LettaSnapshot:
        """Create snapshot from agent data."""
        mem_blocks = []
        for b in (blocks or []):
            content = json.dumps(b, sort_keys=True).encode()
            mem_blocks.append(MemoryBlock(
                label=b.get("label", ""),
                digest=sha256(content),
                size_bytes=len(content),
            ))

        skill_entries = []
        for s in (skills or []):
            content = s.get("content", "").encode()
            skill_entries.append(SkillEntry(
                path=s.get("path", ""),
                digest=sha256(content),
                size_bytes=len(content),
            ))

        # Compute skills tree digest
        if skill_entries:
            skills_data = json.dumps([asdict(s) for s in skill_entries], sort_keys=True).encode()
            skills_tree_digest = sha256(skills_data)
        else:
            skills_tree_digest = ""

        return LettaSnapshot(
            agent_id=agent_id,
            model=model,
            blocks=mem_blocks,
            memfs_commit=memfs_commit,
            memfs_files=memfs_files or [],
            skills=skill_entries,
            skills_tree_digest=skills_tree_digest,
        )

    def snapshot_from_dict(self, data: dict) -> LettaSnapshot:
        """Create snapshot from a dictionary (e.g., from Letta SDK)."""
        return LettaSnapshot(
            agent_id=data.get("agent_id", data.get("id", "")),
            model=data.get("model", ""),
            model_provider=data.get("model_provider", ""),
            blocks=[MemoryBlock(**b) for b in data.get("blocks", [])],
            memfs_commit=data.get("memfs_commit", ""),
            memfs_files=data.get("memfs_files", []),
            skills=[SkillEntry(**s) for s in data.get("skills", [])],
        )
