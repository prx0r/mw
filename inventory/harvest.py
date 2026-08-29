"""Enhanced Harvest — extract capabilities and reusable assets from work.

Extends basic harvest with capability extraction and provenance tracking.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.hashing import sha256, jcs


@dataclass
class CapabilityCandidate:
    """A capability observed from work."""
    capability: str = ""
    evidence_runs: list[str] = field(default_factory=list)
    task_families: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    confidence: str = "INSUFFICIENT"

    def to_dict(self) -> dict:
        return {
            "capability": self.capability,
            "evidence_runs": self.evidence_runs,
            "task_families": self.task_families,
            "quality_score": self.quality_score,
            "confidence": self.confidence,
        }


class EnhancedHarvester:
    """Extract capabilities and reusable assets from completed work."""

    def __init__(self):
        self._capabilities: dict[str, CapabilityCandidate] = {}
        self._assets: list[dict] = []

    def harvest_run(self, run_id: str, task_family: str,
                    output_files: list[str], diff: str = "",
                    evaluation_score: float = 0.0,
                    cost_usd: float = 0.0) -> dict:
        """Harvest capabilities and assets from a completed run."""
        results = {
            "capabilities": [],
            "assets": [],
            "new_files": [],
            "modified_files": [],
        }

        # Extract capabilities from output
        for f in output_files:
            path = Path(f)
            if path.suffix in (".py", ".ts", ".js"):
                cap = f"coding:{path.suffix[1:]}"
                self._add_capability(cap, run_id, task_family, evaluation_score)
                results["capabilities"].append(cap)

        # Extract from diff
        if diff:
            new_files = []
            modified_files = []
            for line in diff.split("\n"):
                if line.startswith("+++ b/"):
                    new_files.append(line[6:])
                elif line.startswith("@@"):
                    pass  # hunks
            results["new_files"] = new_files
            results["modified_files"] = modified_files

            # Harvest reusable components
            for f in new_files:
                path = Path(f)
                if path.suffix in (".py", ".ts", ".md"):
                    asset = {
                        "type": "CODE_COMPONENT",
                        "name": path.stem,
                        "path": f,
                        "run_id": run_id,
                        "task_family": task_family,
                    }
                    self._assets.append(asset)
                    results["assets"].append(asset)

        # Extract process capability
        if evaluation_score > 0.7:
            self._add_capability(f"process:{task_family}", run_id, task_family, evaluation_score)
            results["capabilities"].append(f"process:{task_family}")

        return results

    def _add_capability(self, capability: str, run_id: str,
                        task_family: str, score: float) -> None:
        if capability not in self._capabilities:
            self._capabilities[capability] = CapabilityCandidate(capability=capability)
        cap = self._capabilities[capability]
        if run_id not in cap.evidence_runs:
            cap.evidence_runs.append(run_id)
        if task_family not in cap.task_families:
            cap.task_families.append(task_family)
        # Update quality score (running average)
        n = len(cap.evidence_runs)
        cap.quality_score = ((cap.quality_score * (n - 1)) + score) / n

        # Update confidence
        if cap.evidence_runs:
            n = len(cap.evidence_runs)
            if n >= 10 and cap.quality_score > 0.7:
                cap.confidence = "HIGH"
            elif n >= 5:
                cap.confidence = "MEDIUM"
            elif n >= 2:
                cap.confidence = "LOW"
            else:
                cap.confidence = "INSUFFICIENT"

    def get_capabilities(self) -> list[CapabilityCandidate]:
        return list(self._capabilities.values())

    def get_assets(self) -> list[dict]:
        return list(self._assets)

    def summary(self) -> dict:
        return {
            "total_capabilities": len(self._capabilities),
            "high_confidence": sum(1 for c in self._capabilities.values() if c.confidence == "HIGH"),
            "total_assets": len(self._assets),
        }
