"""Trace2Skill wiring — distill trajectories into skills."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


class Trace2SkillWiring:
    """Wire Trace2Skill to WorkerKit."""

    def __init__(self, vendor_path: str = "/root/workerkit/vendor/Trace2Skill"):
        self.vendor_path = Path(vendor_path)
        self.available = self.vendor_path.exists()

    def analyze_trajectories(self, trajectories: list[dict], output_dir: str = "/tmp/trace2skill") -> dict:
        """Analyze trajectories and propose skills."""
        if not self.available:
            return {"ok": False, "error": "Trace2Skill not available"}

        # Write trajectories to JSONL
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        traj_file = Path(output_dir) / "trajectories.jsonl"
        with open(traj_file, "w") as f:
            for t in trajectories:
                f.write(json.dumps(t) + "\n")

        # Run analysis (would call Trace2Skill CLI in production)
        return {
            "ok": True,
            "trajectories": len(trajectories),
            "output_dir": output_dir,
            "note": "Trace2Skill analysis would run here",
        }

    def propose_skills(self, analysis: dict) -> list[dict]:
        """Propose skills from analysis results."""
        # In production, this would parse Trace2Skill output
        return [{
            "skill_id": "proposed-001",
            "source": "trajectory_analysis",
            "description": "Skill derived from trajectory patterns",
            "validated": False,
        }]
