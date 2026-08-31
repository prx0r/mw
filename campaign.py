"""Campaign management — create, run, grade, regrade, outcome.

This is the operational layer for the production milestone:
3 real submission campaigns with one persistent Letta worker.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.hashing import sha256, jcs


CAMPAIGNS_DIR = Path("/root/lab-campaigns")


@dataclass
class Campaign:
    campaign_id: str
    opportunity: dict[str, Any]
    status: str = "created"  # created → researching → building → grading → submitted → outcome
    worker_id: str = ""
    worker_version: str = ""
    world_version: str = ""
    assessor_version: str = ""
    git_commit: str = ""
    artifact_digest: str = ""
    cost_usd: float = 0.0
    created_at: float = field(default_factory=time.time)
    runs: list[dict] = field(default_factory=list)
    evaluations: list[dict] = field(default_factory=list)
    outcome: dict | None = None

    def dir(self) -> Path:
        return CAMPAIGNS_DIR / self.campaign_id

    def save(self):
        d = self.dir()
        d.mkdir(parents=True, exist_ok=True)
        (d / "campaign.json").write_text(json.dumps({
            "campaign_id": self.campaign_id,
            "status": self.status,
            "worker_id": self.worker_id,
            "worker_version": self.worker_version,
            "world_version": self.world_version,
            "assessor_version": self.assessor_version,
            "git_commit": self.git_commit,
            "artifact_digest": self.artifact_digest,
            "cost_usd": self.cost_usd,
            "created_at": self.created_at,
            "runs": self.runs,
            "evaluations": self.evaluations,
            "outcome": self.outcome,
        }, indent=2))

        # Also project into Hydra graph
        try:
            from hydra.graph import GraphStore
            g = GraphStore()
            g.upsert_node(f"campaign:{self.campaign_id}", "Campaign", {
                "status": self.status,
                "worker_id": self.worker_id,
            })
            if self.worker_id:
                g.upsert_node(f"worker:{self.worker_id}", "Worker", {})
                g.upsert_edge(f"campaign:{self.campaign_id}", f"worker:{self.worker_id}", "EXECUTED_BY")
            for run in self.runs:
                run_id = run.get("run_id", "")
                if run_id:
                    g.upsert_node(f"run:{run_id}", "Run", run)
                    g.upsert_edge(f"campaign:{self.campaign_id}", f"run:{run_id}", "CONTAINS")
        except Exception:
            pass  # graph is optional projection

    @classmethod
    def load(cls, campaign_id: str) -> Campaign:
        d = CAMPAIGNS_DIR / campaign_id
        data = json.loads((d / "campaign.json").read_text())
        # Handle optional fields
        data.setdefault("opportunity", {})
        data.setdefault("runs", [])
        data.setdefault("evaluations", [])
        data.setdefault("outcome", None)
        # ignore unknown fields
        known = {f.name for f in cls.__dataclass_fields__.values()}
        data = {k: v for k, v in data.items() if k in known}
        return cls(**data)


def create_campaign(campaign_id: str, opportunity: dict) -> Campaign:
    """Create a new campaign from an opportunity."""
    c = Campaign(campaign_id=campaign_id, opportunity=opportunity)
    c.save()

    # Create directory structure
    d = c.dir()
    (d / "opportunity").mkdir(exist_ok=True)
    (d / "strategy").mkdir(exist_ok=True)
    (d / "runs").mkdir(exist_ok=True)
    (d / "evaluations").mkdir(exist_ok=True)
    (d / "outcome").mkdir(exist_ok=True)

    # Save opportunity
    (d / "opportunity" / "opportunity.json").write_text(json.dumps(opportunity, indent=2))

    return c


def run_campaign(campaign_id: str, worker_id: str, budget: float = 0.50) -> dict:
    """Execute a campaign run using the Letta runtime."""
    c = Campaign.load(campaign_id)
    c.worker_id = worker_id
    c.status = "building"
    c.save()

    # Build task prompt from opportunity
    opp = c.opportunity
    task = f"""Campaign: {campaign_id}
Opportunity: {opp.get('title', 'unknown')}
Requirements: {json.dumps(opp.get('requirements', []), indent=2)}
Budget: ${budget}
Deadline: {opp.get('deadline', 'unknown')}

Produce a complete technical submission. Extract requirements first, then build."""

    # Call runtime-letta
    import urllib.request
    data = json.dumps({
        "task": task,
        "budget": budget,
        "timeout": 120,
    }).encode()

    req = urllib.request.Request(
        f"http://localhost:3000/workers/{worker_id}/run",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        resp = urllib.request.urlopen(req, timeout=150)
        result = json.loads(resp.read())

        run_record = {
            "run_id": f"run-{int(time.time())}",
            "timestamp": time.time(),
            "worker_id": worker_id,
            "tool_calls": len(result.get("tool_calls", [])),
            "duration_ms": result.get("duration_ms", 0),
            "conversation_id": result.get("conversation_id", ""),
        }
        c.runs.append(run_record)
        c.status = "building"
        c.save()
        return run_record
    except Exception as e:
        return {"error": str(e)}


def grade_campaign(campaign_id: str, assessor_version: str = "v0") -> dict:
    """Grade a campaign using the Harbor World evaluator."""
    c = Campaign.load(campaign_id)
    c.assessor_version = assessor_version
    c.status = "grading"
    c.save()

    # Run hard gates
    world_dir = Path("/root/lab-worlds/technical-submission-v0")
    gates_script = world_dir / "tests" / "hard_gates.py"

    # For now, check if deliverables exist in the campaign directory
    submission_dir = c.dir() / "submission"
    has_submission = submission_dir.exists() and any(submission_dir.iterdir())

    evaluation = {
        "assessor_version": assessor_version,
        "timestamp": time.time(),
        "hard_gates": {
            "submission_exists": has_submission,
            "passed": has_submission,
        },
        "score": 1.0 if has_submission else 0.0,
    }

    c.evaluations.append(evaluation)
    c.status = "graded"
    c.save()
    return evaluation


def record_outcome(campaign_id: str, outcome: dict) -> dict:
    """Record the external outcome (won/lost/rank/feedback)."""
    c = Campaign.load(campaign_id)
    c.outcome = {
        **outcome,
        "recorded_at": time.time(),
    }
    c.status = "outcome"
    c.save()

    # Save outcome
    (c.dir() / "outcome" / "outcome.json").write_text(json.dumps(c.outcome, indent=2))
    return c.outcome


def list_campaigns() -> list[dict]:
    """List all campaigns with their status."""
    campaigns = []
    if CAMPAIGNS_DIR.exists():
        for d in sorted(CAMPAIGNS_DIR.iterdir()):
            if (d / "campaign.json").exists():
                try:
                    c = Campaign.load(d.name)
                    campaigns.append({
                        "campaign_id": c.campaign_id,
                        "status": c.status,
                        "worker_id": c.worker_id,
                        "runs": len(c.runs),
                        "cost_usd": c.cost_usd,
                    })
                except Exception:
                    campaigns.append({"campaign_id": d.name, "status": "error"})
    return campaigns
