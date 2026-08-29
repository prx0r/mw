"""Process versioning — versioned production recipes.

A Process is a repeatable way to produce something.
Each version tracks: graph, success rate, cost, components.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field


def uid() -> str:
    import os
    return f"proc_{os.urandom(4).hex()}"


@dataclass
class ProcessStep:
    name: str = ""
    tool: str = ""  # model, api, skill, verifier
    input_from: list[str] = field(default_factory=list)
    output: str = ""


@dataclass
class Process:
    id: str = field(default_factory=uid)
    name: str = ""
    description: str = ""
    category: str = ""  # research, code, data, content
    steps: list[ProcessStep] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "category": self.category,
                "steps": [asdict(s) for s in self.steps], "skills": self.required_skills}


@dataclass
class ProcessVersion:
    id: str = field(default_factory=uid)
    process_id: str = ""
    version: str = "1.0"
    description: str = ""

    # What changed from previous version
    changes: list[str] = field(default_factory=list)

    # The actual graph
    steps: list[ProcessStep] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    models_used: list[str] = field(default_factory=list)

    # Performance (updated after runs)
    total_runs: int = 0
    successful_runs: int = 0
    median_cost: float = 0.0
    median_payout: float = 0.0

    # Dependencies
    components_used: list[str] = field(default_factory=list)  # asset IDs

    created_at: float = field(default_factory=time.time)

    @property
    def success_rate(self) -> float:
        return self.successful_runs / max(1, self.total_runs)

    def to_dict(self) -> dict:
        return {"id": self.id, "process_id": self.process_id,
                "version": self.version, "changes": self.changes,
                "total_runs": self.total_runs, "success_rate": self.success_rate,
                "median_cost": self.median_cost, "median_payout": self.median_payout}

    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "version.json").write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> ProcessVersion:
        data = json.loads((path / "version.json").read_text())
        pv = cls()
        for k, v in data.items():
            if hasattr(pv, k): setattr(pv, k, v)
        return pv
