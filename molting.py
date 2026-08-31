"""Molting — extract typed candidate assets from completed campaigns.

Post-run molting asks:
  What did this Campaign create?
  What should be retained?
  What should become reusable?
  What should change in the Worker/World/Assessor?

Produces typed candidates on Git branches (not instantly production).
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


def _sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


@dataclass
class MoltingCandidate:
    """A candidate asset extracted from a campaign run."""
    candidate_id: str
    candidate_type: str  # memory | skill | process | world | assessor | school | code | research | harness
    source_run_id: str
    source_campaign_id: str
    
    # What it is
    name: str = ""
    description: str = ""
    content: str = ""
    
    # Evidence
    evidence_runs: list[str] = field(default_factory=list)
    hypothesis: str = ""
    
    # Status
    status: str = "candidate"  # candidate | testing | validated | rejected | promoted
    
    # Testing
    experiment_id: str = ""
    paired_delta: float = 0.0
    cost_impact: float = 0.0
    
    created_at: float = field(default_factory=time.time)
    
    def content_hash(self) -> str:
        return _sha256({
            "candidate_type": self.candidate_type,
            "name": self.name,
            "content": self.content[:500],
        })
    
    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "candidate_type": self.candidate_type,
            "source_run_id": self.source_run_id,
            "source_campaign_id": self.source_campaign_id,
            "name": self.name,
            "description": self.description,
            "content_hash": self.content_hash()[:16],
            "evidence_runs": self.evidence_runs,
            "hypothesis": self.hypothesis,
            "status": self.status,
            "experiment_id": self.experiment_id,
            "paired_delta": self.paired_delta,
            "cost_impact": self.cost_impact,
            "created_at": self.created_at,
        }
    
    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "candidate.json").write_text(json.dumps(self.to_dict(), indent=2))
        if self.content:
            (path / "content.md").write_text(self.content)


def molte_campaign(campaign_id: str, run_results: list[dict],
                   artifact_content: str = "",
                   evaluation: dict = None) -> list[MoltingCandidate]:
    """Extract typed candidate assets from completed campaign runs.
    
    Returns list of candidates to be tested on Git branches.
    """
    candidates = []
    
    # Analyze all runs in the campaign
    wins = [r for r in run_results if r.get("outcome") == "won"]
    losses = [r for r in run_results if r.get("outcome") == "lost"]
    all_runs = run_results
    
    # 1. Skill candidates (if we found a winning pattern)
    if wins:
        winning_scores = [r.get("score", 0) for r in wins]
        avg_winning = sum(winning_scores) / len(winning_scores) if winning_scores else 0
        
        candidates.append(MoltingCandidate(
            candidate_id=f"skill-{campaign_id[:16]}",
            candidate_type="skill",
            source_run_id=wins[0].get("run_id", ""),
            source_campaign_id=campaign_id,
            name=f"skill-from-{campaign_id[:16]}",
            description=f"Skill extracted from winning run (avg score: {avg_winning:.2f})",
            content=artifact_content[:2000] if artifact_content else "",
            evidence_runs=[r.get("run_id", "") for r in wins],
            hypothesis="This pattern improves outcomes on similar tasks",
            status="candidate",
        ))
    
    # 2. Process candidates (if we found a repeatable process)
    if len(all_runs) >= 2:
        # Extract process from run patterns
        process_steps = []
        for r in all_runs[:3]:
            if r.get("steps"):
                process_steps.extend(r["steps"])
        
        if process_steps:
            candidates.append(MoltingCandidate(
                candidate_id=f"process-{campaign_id[:16]}",
                candidate_type="process",
                source_run_id=all_runs[0].get("run_id", ""),
                source_campaign_id=campaign_id,
                name=f"process-from-{campaign_id[:16]}",
                description=f"Process extracted from {len(all_runs)} runs",
                evidence_runs=[r.get("run_id", "") for r in all_runs],
                hypothesis="This process generalizes to similar opportunities",
                status="candidate",
            ))
    
    # 3. Memory candidates (if we learned something durable)
    if losses:
        failure_reasons = []
        for loss in losses:
            if loss.get("failure_reason"):
                failure_reasons.append(loss["failure_reason"])
            if loss.get("gate_failures"):
                failure_reasons.extend(loss["gate_failures"])
        
        unique_failures = list(set(failure_reasons))
        if unique_failures:
            candidates.append(MoltingCandidate(
                candidate_id=f"memory-{campaign_id[:16]}",
                candidate_type="memory",
                source_run_id=losses[0].get("run_id", ""),
                source_campaign_id=campaign_id,
                name=f"memory-from-{campaign_id[:16]}",
                description=f"Memory update from {len(unique_failures)} failure patterns",
                content="\n".join(f"- Avoid: {f}" for f in unique_failures),
                evidence_runs=[r.get("run_id", "") for r in losses],
                hypothesis="These failure patterns should be remembered to avoid repeating",
                status="candidate",
            ))
    
    # 4. World candidate (if our evaluator was wrong)
    if evaluation and evaluation.get("assessor_disagreed_with_reality"):
        candidates.append(MoltingCandidate(
            candidate_id=f"world-{campaign_id[:16]}",
            candidate_type="world",
            source_run_id=campaign_id,
            source_campaign_id=campaign_id,
            name=f"world-update-{campaign_id[:16]}",
            description="Evaluator calibration update needed",
            evidence_runs=[campaign_id],
            hypothesis="Adjusting rubric weights would better predict outcomes",
            status="candidate",
        ))
    
    # 5. Code asset candidates (if we built reusable code)
    if artifact_content and len(artifact_content) > 500:
        candidates.append(MoltingCandidate(
            candidate_id=f"code-{campaign_id[:16]}",
            candidate_type="code",
            source_run_id=all_runs[0].get("run_id", "") if all_runs else "",
            source_campaign_id=campaign_id,
            name=f"code-from-{campaign_id[:16]}",
            description=f"Reusable code asset ({len(artifact_content)} chars)",
            content=artifact_content[:5000],
            evidence_runs=[r.get("run_id", "") for r in all_runs if r.get("outcome") == "won"],
            hypothesis="This code is reusable for similar opportunities",
            status="candidate",
        ))
    
    return candidates
