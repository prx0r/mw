"""Harvest — extract reusable assets from completed work.

After every merged WorkUnit, inspect the diff and create AssetCandidates.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.hashing import sha256, jcs


class AssetType(str, Enum):
    CODE_COMPONENT = "CODE_COMPONENT"
    CONNECTOR = "CONNECTOR"
    SKILL = "SKILL"
    PROCESS = "PROCESS"
    TEMPLATE = "TEMPLATE"
    EVALUATION = "EVALUATION"
    DATASET = "DATASET"
    RESEARCH = "RESEARCH"
    PROMPT = "PROMPT"
    DEPLOYMENT_RECIPE = "DEPLOYMENT_RECIPE"
    DESIGN_ASSET = "DESIGN_ASSET"


class AssetVisibility(str, Enum):
    LAB_PRIVATE = "LAB_PRIVATE"
    REUSABLE = "REUSABLE"
    VERIFIED = "VERIFIED"
    LISTABLE = "LISTABLE"
    MARKETPLACE = "MARKETPLACE"


@dataclass
class AssetCandidate:
    """A potentially reusable asset extracted from work."""
    asset_id: str = ""
    asset_type: str = "CODE_COMPONENT"
    name: str = ""
    description: str = ""
    version: str = "0.1.0"

    source_repo: str = ""
    source_commit: str = ""
    source_paths: list[str] = field(default_factory=list)

    derived_from_runs: list[str] = field(default_factory=list)
    derived_from_opportunities: list[str] = field(default_factory=list)
    process_version: str = ""

    sha256: str = ""

    tests: list[str] = field(default_factory=list)
    verification_refs: list[str] = field(default_factory=list)
    receipt_refs: list[str] = field(default_factory=list)

    capabilities: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    visibility: str = "LAB_PRIVATE"
    commercialization: str = "UNREVIEWED"

    created_at: float = field(default_factory=time.time)

    def content_hash(self) -> str:
        d = {
            "asset_type": self.asset_type,
            "name": self.name,
            "version": self.version,
            "sha256": self.sha256,
            "source_commit": self.source_commit,
        }
        return sha256(jcs(d))

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "sha256": self.sha256,
            "source_commit": self.source_commit,
            "source_paths": self.source_paths,
            "derived_from_runs": self.derived_from_runs,
            "capabilities": self.capabilities,
            "visibility": self.visibility,
        }


class Harvester:
    """Extract reusable assets from completed work."""

    def __init__(self):
        self._candidates: list[AssetCandidate] = []

    def harvest(self, run_id: str, artifact_paths: list[str],
                git_diff: str = "", receipt_id: str = "",
                process_version: str = "") -> list[AssetCandidate]:
        """Harvest assets from a completed run."""
        candidates = []

        # Analyze diff for reusable components
        if git_diff:
            for diff_path in self._extract_paths(git_diff):
                candidate = AssetCandidate(
                    asset_type="CODE_COMPONENT",
                    name=Path(diff_path).stem,
                    source_paths=[diff_path],
                    derived_from_runs=[run_id],
                    receipt_refs=[receipt_id] if receipt_id else [],
                    process_version=process_version,
                )
                candidates.append(candidate)

        # Analyze artifacts
        for artifact_path in artifact_paths:
            candidate = AssetCandidate(
                asset_type="CODE_COMPONENT",
                name=Path(artifact_path).stem,
                source_paths=[artifact_path],
                derived_from_runs=[run_id],
                receipt_refs=[receipt_id] if receipt_id else [],
            )
            candidates.append(candidate)

        self._candidates.extend(candidates)
        return candidates

    def _extract_paths(self, diff: str) -> list[str]:
        """Extract file paths from a git diff."""
        paths = []
        for line in diff.split("\n"):
            if line.startswith("+++ b/"):
                paths.append(line[6:])
            elif line.startswith("--- a/"):
                pass  # skip
            elif line.startswith("diff --git"):
                parts = line.split(" ")
                if len(parts) >= 4:
                    paths.append(parts[3][2:])  # remove b/
        return list(set(paths))

    def list_candidates(self, visibility: str = "") -> list[AssetCandidate]:
        if visibility:
            return [c for c in self._candidates if c.visibility == visibility]
        return list(self._candidates)

    def promote(self, asset_id: str, new_visibility: str) -> bool:
        for c in self._candidates:
            if c.asset_id == asset_id:
                c.visibility = new_visibility
                return True
        return False


from pathlib import Path
