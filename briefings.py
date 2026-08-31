"""Briefings — three time scales for Letta cognitive input.

Immediate: Campaign context (ephemeral, doesn't change memory)
  "You are working opportunity X. Use process P7."

Medium-term: Task-family briefing (retrieved when relevant)
  "For competition.technical_submission: known strengths, failures, processes"

Long-term: Worker cognition (only validated, generalizable findings)
  MemFS, Skills, Mods

This prevents the worker from turning into a junk drawer.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


def _sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


# ─── Immediate Briefing ───────────────────────────────────────────────

@dataclass
class ImmediateBriefing:
    """Campaign-specific context. Ephemeral. Doesn't change permanent memory."""
    campaign_id: str
    opportunity_id: str
    
    # What the worker needs to know right now
    task_description: str = ""
    success_model_summary: str = ""
    recommended_process: str = ""
    relevant_prior_finding: str = ""
    
    # Constraints
    budget_remaining: float = 0.0
    time_remaining_s: float = 0.0
    
    # Historical context
    similar_campaigns_won: int = 0
    similar_campaigns_lost: int = 0
    
    def to_prompt(self) -> str:
        """Generate a prompt for the Letta worker."""
        parts = [
            f"You are working on: {self.opportunity_id}",
            "",
            "Task:",
            self.task_description,
            "",
            "Success criteria:",
            self.success_model_summary,
            "",
        ]
        
        if self.recommended_process:
            parts.extend([
                "Recommended process:",
                self.recommended_process,
                "",
            ])
        
        if self.relevant_prior_finding:
            parts.extend([
                "Relevant prior finding:",
                self.relevant_prior_finding,
                "",
            ])
        
        if self.budget_remaining > 0:
            parts.append(f"Budget: ${self.budget_remaining:.2f}")
        
        if self.similar_campaigns_won > 0:
            parts.append(f"Similar campaigns: {self.similar_campaigns_won} won, {self.similar_campaigns_lost} lost")
        
        return "\n".join(parts)
    
    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "opportunity_id": self.opportunity_id,
            "task_description": self.task_description,
            "success_model_summary": self.success_model_summary,
            "recommended_process": self.recommended_process,
            "relevant_prior_finding": self.relevant_prior_finding,
            "budget_remaining": self.budget_remaining,
            "time_remaining_s": self.time_remaining_s,
            "similar_campaigns_won": self.similar_campaigns_won,
            "similar_campaigns_lost": self.similar_campaigns_lost,
        }


# ─── Medium-term Briefing ─────────────────────────────────────────────

@dataclass
class TaskFamilyBriefing:
    """Task-family briefing. Retrieved when relevant. Not permanent memory."""
    task_family: str
    
    # What we know
    known_strengths: list[str] = field(default_factory=list)
    known_failures: list[str] = field(default_factory=list)
    validated_processes: list[dict] = field(default_factory=list)
    effective_skills: list[str] = field(default_factory=list)
    
    # Statistics
    total_runs: int = 0
    win_rate: float = 0.0
    median_cost: float = 0.0
    avg_score: float = 0.0
    
    # Evidence
    supporting_run_ids: list[str] = field(default_factory=list)
    
    def to_prompt(self) -> str:
        parts = [f"## Task Family: {self.task_family}", ""]
        
        if self.known_strengths:
            parts.append("Known strengths:")
            for s in self.known_strengths[:5]:
                parts.append(f"- {s}")
            parts.append("")
        
        if self.known_failures:
            parts.append("Known failures to avoid:")
            for f in self.known_failures[:5]:
                parts.append(f"- {f}")
            parts.append("")
        
        if self.validated_processes:
            parts.append("Validated processes:")
            for p in self.validated_processes[:3]:
                parts.append(f"- {p.get('name', 'unnamed')}: {p.get('description', '')}")
            parts.append("")
        
        if self.total_runs > 0:
            parts.append(f"History: {self.total_runs} runs, {self.win_rate:.0%} win rate, ${self.median_cost:.2f} median cost")
        
        return "\n".join(parts)
    
    def to_dict(self) -> dict:
        return {
            "task_family": self.task_family,
            "known_strengths": self.known_strengths,
            "known_failures": self.known_failures,
            "validated_processes": self.validated_processes,
            "effective_skills": self.effective_skills,
            "total_runs": self.total_runs,
            "win_rate": self.win_rate,
            "median_cost": self.median_cost,
            "avg_score": self.avg_score,
            "supporting_run_ids": self.supporting_run_ids,
        }


def generate_task_family_briefing(task_family: str, hydra_data: dict) -> TaskFamilyBriefing:
    """Generate a task-family briefing from Hydra data."""
    briefing = TaskFamilyBriefing(task_family=task_family)
    
    # Populate from Hydra
    briefing.total_runs = hydra_data.get("total_runs", 0)
    briefing.win_rate = hydra_data.get("win_rate", 0)
    briefing.median_cost = hydra_data.get("median_cost", 0)
    briefing.avg_score = hydra_data.get("avg_score", 0)
    briefing.known_strengths = hydra_data.get("strengths", [])
    briefing.known_failures = hydra_data.get("failures", [])
    briefing.validated_processes = hydra_data.get("processes", [])
    briefing.effective_skills = hydra_data.get("skills", [])
    briefing.supporting_run_ids = hydra_data.get("run_ids", [])
    
    return briefing


# ─── Briefing Generator ───────────────────────────────────────────────

class BriefingGenerator:
    """Generate briefings at all three time scales."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.briefings_dir = self.data_dir / "briefings"
        self.briefings_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_immediate(self, campaign_id: str, opportunity: dict,
                           success_model: dict, hydra_findings: dict) -> ImmediateBriefing:
        """Generate immediate campaign briefing."""
        briefing = ImmediateBriefing(
            campaign_id=campaign_id,
            opportunity_id=opportunity.get("id", "unknown"),
            task_description=opportunity.get("description", ""),
            success_model_summary=json.dumps(success_model.get("dimensions", {}), indent=2)[:500],
            recommended_process=hydra_findings.get("recommended_process", ""),
            relevant_prior_finding=hydra_findings.get("relevant_finding", ""),
            similar_campaigns_won=hydra_findings.get("similar_won", 0),
            similar_campaigns_lost=hydra_findings.get("similar_lost", 0),
        )
        
        # Save
        path = self.briefings_dir / campaign_id / "immediate"
        path.mkdir(parents=True, exist_ok=True)
        (path / "briefing.json").write_text(json.dumps(briefing.to_dict(), indent=2))
        (path / "prompt.md").write_text(briefing.to_prompt())
        
        return briefing
    
    def generate_task_family(self, task_family: str, hydra_data: dict) -> TaskFamilyBriefing:
        """Generate task-family briefing from Hydra."""
        briefing = generate_task_family_briefing(task_family, hydra_data)
        
        # Save
        path = self.briefings_dir / "task-family" / task_family.replace(".", "/")
        path.mkdir(parents=True, exist_ok=True)
        (path / "briefing.json").write_text(json.dumps(briefing.to_dict(), indent=2))
        (path / "prompt.md").write_text(briefing.to_prompt())
        
        return briefing
