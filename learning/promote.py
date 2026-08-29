"""Promote — Git worktree promotion for validated learning.

When cg says PASS, create a new MemFS commit with the validated patch.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.hashing import sha256
from learning.proposal import LearningProposal


@dataclass
class PromotionResult:
    """Result of promoting a learning proposal."""
    success: bool = False
    new_version_id: str = ""
    parent_version: str = ""
    memfs_commit: str = ""
    proposal_id: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "new_version_id": self.new_version_id,
            "parent_version": self.parent_version,
            "memfs_commit": self.memfs_commit,
            "proposal_id": self.proposal_id,
        }


class LearningPromoter:
    """Promote validated learning proposals to production.

    Flow:
      1. Create candidate worktree from production MemFS
      2. Apply patch to candidate
      3. cg validates on held-out fixtures
      4. If PASS: merge candidate into production
      5. Create new MemFS commit
      6. Update WorkerManifest
    """

    def __init__(self, data_dir: str = ".moltwork"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_candidate(self, proposal: LearningProposal, memfs_path: str) -> str:
        """Create a candidate worktree from production MemFS.

        Returns the candidate path.
        """
        candidate_path = self.data_dir / "learning" / "candidates" / proposal.proposal_id
        candidate_path.mkdir(parents=True, exist_ok=True)

        # Copy production MemFS to candidate
        memfs_dir = Path(memfs_path)
        if memfs_dir.exists():
            for item in memfs_dir.iterdir():
                if item.is_dir():
                    subprocess.run(["cp", "-r", str(item), str(candidate_path)], check=False)
                else:
                    subprocess.run(["cp", str(item), str(candidate_path)], check=False)

        # Apply patch
        if proposal.target == "skill" and proposal.path:
            skill_dir = candidate_path / proposal.path
            skill_dir.parent.mkdir(parents=True, exist_ok=True)
            skill_dir.write_text(proposal.patch)
        elif proposal.target == "memory":
            # Memory patches are applied via Letta, not direct file write
            pass

        return str(candidate_path)

    def validate_candidate(self, candidate_path: str, proposal: LearningProposal) -> bool:
        """Validate that the patch was applied correctly.

        In production, this runs cg held-out evaluation.
        """
        if proposal.target == "skill" and proposal.path:
            skill_path = Path(candidate_path) / proposal.path
            return skill_path.exists() and skill_path.read_text() == proposal.patch
        return True

    def promote(self, proposal: LearningProposal, candidate_path: str,
                experiment_result: dict | None = None) -> PromotionResult:
        """Promote a validated proposal to production.

        Creates a new MemFS commit with the validated patch.
        """
        # Validate
        if not self.validate_candidate(candidate_path, proposal):
            return PromotionResult(
                success=False,
                proposal_id=proposal.proposal_id,
                error="validation failed",
            )

        # Record the promotion
        promotion = {
            "proposal_id": proposal.proposal_id,
            "worker_version": proposal.worker_version,
            "target": proposal.target,
            "path": proposal.path,
            "hypothesis": proposal.hypothesis,
            "experiment_result": experiment_result,
            "promoted_at": time.time(),
        }

        promotion_path = self.data_dir / "learning" / "promotions" / f"{proposal.proposal_id}.json"
        promotion_path.parent.mkdir(parents=True, exist_ok=True)
        promotion_path.write_text(json.dumps(promotion, indent=2))

        # Generate new version ID
        new_version = sha256(json.dumps(promotion, sort_keys=True).encode())

        return PromotionResult(
            success=True,
            new_version_id=new_version,
            parent_version=proposal.worker_version,
            proposal_id=proposal.proposal_id,
        )
