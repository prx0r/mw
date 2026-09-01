"""Fleet manager — 5 persistent Letta workers, one HydraDB.

One Letta server, five agents:
  researcher, coder, it, sales, reviewer
Each has: own memory, own skills, own .af lineage, shared lab priors

Lab genome → template → new worker with priors (not reputation)
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


TEMPLATES = {
    "researcher": {"persona": "research analyst", "skills": ["research-bounties", "api-docs"], "tools": ["web_search", "read_file"]},
    "coder": {"persona": "software engineer", "skills": ["code-review", "testing"], "tools": ["code_exec", "read_file"]},
    "it": {"persona": "IT helpdesk specialist", "skills": ["network-triage", "m365"], "tools": ["code_exec", "web_search"]},
    "sales": {"persona": "lead generation specialist", "skills": ["lead-research", "outreach"], "tools": ["web_search"]},
    "reviewer": {"persona": "QA reviewer", "skills": ["evaluation", "verification"], "tools": ["read_file"]},
}

# Lab-wide shared priors (inherited by new workers)
LAB_PRIORS = {
    "rules": ["establish scope before changing anything", "prefer reversible interventions"],
    "model_selection": {"research": "glm-5.3", "code": "mimo-v2.5", "default": "mimo-v2.5"},
    "failure_warnings": ["pricing omission appears in 3/12 failed submissions"],
}


@dataclass
class FleetWorker:
    agent_id: str
    role: str  # researcher/coder/it/sales/reviewer
    template: str
    af_path: str = ""
    lineage: list[str] = field(default_factory=list)  # .af hashes
    personal_runs: int = 0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {"agent_id": self.agent_id, "role": self.role, "template": self.template,
                "af_path": self.af_path, "lineage": self.lineage, "personal_runs": self.personal_runs}


class FleetManager:
    """Manages the 5-worker lab fleet."""

    ROLES = ["researcher", "coder", "it", "sales", "reviewer"]

    def __init__(self, hydra=None, letta_url: str = ""):
        self.hydra = hydra  # TODO: Wire real HydraDB client
        self.letta_url = letta_url
        self.workers: dict[str, FleetWorker] = {}  # agent_id → FleetWorker

    def create_worker(self, role: str, agent_id: str = "", af_path: str = "") -> FleetWorker:
        if role not in TEMPLATES:
            raise ValueError(f"unknown role {role}, choose from {self.ROLES}")
        if not agent_id:
            import uuid
            agent_id = f"{role}-{uuid.uuid4().hex[:8]}"
        w = FleetWorker(agent_id=agent_id, role=role, template=role, af_path=af_path)
        self.workers[agent_id] = w
        self.hydra.upsert_agent(agent_id, template=role, lineage=[], data=TEMPLATES[role])
        return w

    def create_fleet(self) -> list[FleetWorker]:
        """Create all 5 workers."""
        return [self.create_worker(r) for r in self.ROLES]

    def seed_worker(self, role: str, agent_id: str = "") -> FleetWorker:
        """Seed new worker with lab genome + role priors."""
        w = self.create_worker(role, agent_id)
        # Attach lab priors as shared context (not personal memory)
        w.priors = dict(LAB_PRIORS)  # type: ignore
        w.role_priors = dict(TEMPLATES[role])  # type: ignore
        return w

    def record_outcome(self, agent_id: str, run_id: str, outcome: str, reward: float = 0, cost: float = 0, evaluation: float = 0):
        w = self.workers.get(agent_id)
        if w:
            w.personal_runs += 1
        self.hydra.record_run(run_id=run_id, agent_id=agent_id, outcome=outcome, reward_usd=reward, cost_usd=cost, evaluation_score=evaluation)

    def get_worker(self, agent_id: str) -> FleetWorker | None:
        return self.workers.get(agent_id)

    def list_workers(self) -> list[dict]:
        return [w.to_dict() for w in self.workers.values()]

    def fleet_summary(self) -> dict:
        hydra_stats = self.hydra.lab_summary()
        return {
            "fleet_size": len(self.workers),
            "workers": self.list_workers(),
            "lab": hydra_stats,
        }

    def lineage(self, agent_id: str) -> list[str]:
        w = self.workers.get(agent_id)
        return w.lineage if w else []
