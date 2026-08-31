"""Experiment framework — compare worker versions on same tasks.

This is the core of the Lab. Without this, "learning" is just claims.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from core.hashing import sha256


EXPERIMENTS_DIR = Path("/root/lab-campaigns/experiments")


@dataclass
class Experiment:
    id: str = ""
    hypothesis: str = ""
    world: str = ""                    # which Harbor World
    control_worker_version: str = ""   # baseline
    treatment_worker_version: str = "" # the change
    controls: dict = field(default_factory=lambda: {
        "same_model": True,
        "same_budget": True,
        "same_world": True,
        "same_assessor": True,
    })
    task_ids: list[str] = field(default_factory=list)
    status: str = "planned"            # planned → running → complete
    results: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def save(self):
        d = EXPERIMENTS_DIR / self.id
        d.mkdir(parents=True, exist_ok=True)
        (d / "experiment.json").write_text(json.dumps(asdict(self), indent=2))

    @classmethod
    def load(cls, exp_id: str) -> Experiment:
        d = EXPERIMENTS_DIR / exp_id
        data = json.loads((d / "experiment.json").read_text())
        return cls(**data)


@dataclass
class ExperimentResult:
    experiment_id: str = ""
    worker_version: str = ""
    task_id: str = ""
    success: bool = False
    cost_usd: float = 0.0
    duration_s: float = 0.0
    score: float = 0.0
    human_intervention: bool = False
    run_id: str = ""
    recorded_at: float = field(default_factory=time.time)


def run_comparison(experiment_id: str, task_ids: list[str],
                   control_version: str, treatment_version: str,
                   budget_per_task: float = 0.20) -> dict:
    """Run a controlled comparison. Returns summary.

    In production this would call runtime-letta for each worker version.
    For now, returns synthetic results for architecture validation.
    """
    exp = Experiment(
        id=experiment_id,
        hypothesis=f"{treatment_version} outperforms {control_version}",
        world="technical-submission-v0",
        control_worker_version=control_version,
        treatment_worker_version=treatment_version,
        task_ids=task_ids,
        status="running",
    )
    exp.save()

    # In production: run each task with each worker version via Harbor
    # For now: record the experiment structure
    results = {
        "experiment_id": experiment_id,
        "control": control_version,
        "treatment": treatment_version,
        "tasks": task_ids,
        "status": "structured",
        "note": "Run via Harbor for real results",
    }

    exp.status = "structured"
    exp.results = results
    exp.save()
    return results


def analyze_experiment(experiment_id: str) -> dict:
    """Analyze results. Compare control vs treatment.

    In production: paired bootstrap, Wilson CI, non-inferiority test.
    """
    exp = Experiment.load(experiment_id)
    return {
        "experiment_id": experiment_id,
        "hypothesis": exp.hypothesis,
        "status": exp.status,
        "n_tasks": len(exp.task_ids),
        "note": "Need real Harbor runs for actual analysis",
    }


def list_experiments() -> list[dict]:
    if not EXPERIMENTS_DIR.exists():
        return []
    exps = []
    for d in sorted(EXPERIMENTS_DIR.iterdir()):
        if (d / "experiment.json").exists():
            exp = Experiment.load(d.name)
            exps.append({
                "id": exp.id,
                "hypothesis": exp.hypothesis,
                "status": exp.status,
                "n_tasks": len(exp.task_ids),
            })
    return exps
