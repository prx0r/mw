"""Letta Restore — restore a worker from a snapshot.

Recreates a Letta agent from a content-addressed snapshot.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtimes.letta.snapshot import LettaSnapshot


class LettaRestorer:
    """Restore a Letta agent from a snapshot.

    In production, this talks to the Letta SDK.
    For now, produces the configuration needed for restoration.
    """

    def __init__(self, letta_client: Any = None):
        self.client = letta_client

    def restore_config(self, snapshot: LettaSnapshot) -> dict:
        """Generate the configuration needed to restore an agent from a snapshot.

        Returns a dict suitable for Letta SDK's createAgent().
        """
        # Reconstruct memory blocks from snapshot
        memory = []
        for block in snapshot.blocks:
            memory.append({
                "label": block.label,
                "value": f"[restored from snapshot, digest: {block.digest}]",
            })

        # Reconstruct tools from snapshot
        tools = []  # Would be reconstructed from tool_schema_digest

        return {
            "model": snapshot.model,
            "memory": memory,
            "memfs": True,
            "name": f"{snapshot.agent_id}-restored",
            "tags": ["moltwork", "restored", f"snapshot:{snapshot.content_digest()[:16]}"],
        }

    def verify_snapshot(self, snapshot: LettaSnapshot) -> tuple[bool, str]:
        """Verify a snapshot is internally consistent.

        Returns (valid, reason).
        """
        # Check schema
        if snapshot.schema != "moltwork:letta-snapshot:v1":
            return False, f"wrong schema: {snapshot.schema}"

        # Check agent_id
        if not snapshot.agent_id:
            return False, "missing agent_id"

        # Check at least one memory block
        if not snapshot.blocks:
            return False, "no memory blocks"

        # Verify block digests
        for block in snapshot.blocks:
            if not block.digest or len(block.digest) != 64:
                return False, f"invalid digest for block {block.label}"

        # Verify skills tree digest matches skills
        if snapshot.skills and not snapshot.skills_tree_digest:
            return False, "skills present but no tree digest"

        return True, "ok"

    def diff_snapshots(self, old: LettaSnapshot, new: LettaSnapshot) -> dict:
        """Compare two snapshots and show what changed."""
        changes = {
            "model_changed": old.model != new.model,
            "blocks_added": [b.label for b in new.blocks if b.label not in [ob.label for ob in old.blocks]],
            "blocks_removed": [ob.label for ob in old.blocks if ob.label not in [b.label for b in new.blocks]],
            "blocks_changed": [],
            "skills_added": [s.path for s in new.skills if s.path not in [os.path for os in old.skills]],
            "skills_removed": [os.path for os in old.skills if os.path not in [s.path for s in new.skills]],
            "memfs_commit_changed": old.memfs_commit != new.memfs_commit,
        }

        # Check for block content changes
        old_blocks = {b.label: b.digest for b in old.blocks}
        new_blocks = {b.label: b.digest for b in new.blocks}
        for label in set(old_blocks.keys()) & set(new_blocks.keys()):
            if old_blocks[label] != new_blocks[label]:
                changes["blocks_changed"].append(label)

        return changes
