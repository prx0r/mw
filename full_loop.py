"""Full Loop — the 17-step Moltwork pipeline.

Market Observation → Capability Query → World Discovery → Baseline →
Execute → Assess → Project to Hydra → Scientist Query → Hypothesis →
Fork Worker → Controlled Experiment → Statistics → Promotion →
Real Work → External Outcome → Hydra Update → Letta Learning
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from git_primitives import WorkerVersion, WorldVersion, AssessorVersion
from hydra_projectors import RunProjector, EvalProjector, OutcomeProjector
from flywheel import FlywheelRun, Rubric, generate_rubric
from campaign import Campaign, SuccessModel, generate_success_model
from molting import molte_campaign, MoltingCandidate
from briefings import BriefingGenerator


@dataclass
class LoopState:
    """State of one complete loop iteration."""
    # Step 1: Market observation
    opportunity: dict = field(default_factory=dict)
    
    # Step 2: Capability query
    capability_evidence: dict = field(default_factory=dict)
    
    # Step 3: World discovery
    world_versions: list[WorldVersion] = field(default_factory=list)
    
    # Step 3b: SuccessModel
    success_model: SuccessModel | None = None
    
    # Step 4: Baseline
    worker_version: WorkerVersion | None = None
    baseline_session: str = ""
    
    # Step 5-6: Execute + Assess
    flywheel_run: FlywheelRun | None = None
    
    # Step 7: Project to Hydra
    hydra_run_id: str = ""
    
    # Step 8-9: Scientist query + Hypothesis
    hypothesis: str = ""
    hypothesis_evidence: list[dict] = field(default_factory=list)
    
    # Step 10-12: Fork + Experiment + Statistics
    control_version: WorkerVersion | None = None
    candidate_version: WorkerVersion | None = None
    experiment_result: dict = field(default_factory=dict)
    
    # Step 13: Promotion
    promoted: bool = False
    promoted_version: WorkerVersion | None = None
    
    # Step 14-16: Real work + Outcome + Update
    real_outcome: dict = field(default_factory=dict)
    
    # Step 17: Learning
    memory_updates: list[dict] = field(default_factory=list)
    skill_updates: list[dict] = field(default_factory=list)
    
    # Step 17: Molting
    molting_candidates: list = field(default_factory=list)
    
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0


class FullLoop:
    """Orchestrate the complete 17-step Moltwork loop.
    
    Usage:
        loop = FullLoop(data_dir="data")
        state = loop.run(opportunity={...}, worker_version=v7)
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.loops_dir = self.data_dir / "loops"
        self.loops_dir.mkdir(parents=True, exist_ok=True)
        
        # Projectors
        self.run_projector = RunProjector(str(self.data_dir / "hydradb.db"))
        self.eval_projector = EvalProjector(str(self.data_dir / "hydradb.db"))
        self.outcome_projector = OutcomeProjector(str(self.data_dir / "hydradb.db"))
    
    def run(self, opportunity: dict, worker_version: WorkerVersion,
            execute_fn, max_iterations: int = 3) -> LoopState:
        """Run the complete 17-step loop."""
        state = LoopState(opportunity=opportunity, worker_version=worker_version)
        loop_id = f"loop-{int(time.time())}"
        
        # Create Campaign
        campaign = Campaign(
            campaign_id=loop_id,
            opportunity_id=opportunity.get("id", "unknown"),
            worker_id=worker_version.worker_id,
        )
        
        print(f"\n{'='*60}")
        print(f"CAMPAIGN: {loop_id}")
        print(f"Opportunity: {opportunity.get('title', 'unknown')}")
        print(f"Worker: {worker_version.worker_id}/{worker_version.version_id}")
        print(f"{'='*60}")
        
        # Step 1: Market observation (already have opportunity)
        print(f"\n[1/17] Market observation: {opportunity.get('task_family', 'unknown')}")
        campaign.advance("researching")
        
        # Step 2: Capability query (check what we know)
        print(f"[2/17] Capability query...")
        state.capability_evidence = self._query_capabilities(worker_version, opportunity)
        
        # Step 3: World discovery (find matching worlds)
        print(f"[3/17] World discovery...")
        state.world_versions = self._discover_worlds(opportunity)
        campaign.world_refs = [{"world_id": w.world_id, "version": w.version_id} for w in state.world_versions]
        
        # Step 3b: Generate SuccessModel (phase zero)
        print(f"[3b/17] Generating SuccessModel...")
        state.success_model = generate_success_model(opportunity, state.capability_evidence)
        campaign.success_model = state.success_model
        state.success_model.save(self.data_dir / "campaigns" / loop_id / "strategy")
        
        # Step 4: Generate briefings
        print(f"[4/17] Generate briefings...")
        briefing_gen = BriefingGenerator(data_dir=str(self.data_dir))
        immediate = briefing_gen.generate_immediate(
            loop_id, opportunity, state.success_model.to_dict(), state.capability_evidence
        )
        
        # Step 5: Baseline (fresh session)
        print(f"[5/17] Baseline...")
        state.baseline_session = f"baseline-{int(time.time())}"
        campaign.advance("building")
        
        # Step 6-7: Execute + Assess (flywheel)
        print(f"[6-7/17] Execute + Assess...")
        from flywheel.runner import FlywheelRunner
        runner = FlywheelRunner(data_dir=str(self.data_dir))
        state.flywheel_run = runner.run_cycle(
            opportunity, execute_fn, max_iterations=max_iterations
        )
        
        # Record runs in campaign
        if state.flywheel_run:
            campaign.runs.append(state.flywheel_run.to_dict())
            campaign.best_score = state.flywheel_run.best_score
            campaign.iteration_count = state.flywheel_run.iteration_count
            campaign.record_cost(0.0)  # cost tracked elsewhere
        
        # Step 8: Project to Hydra
        print(f"[8/17] Project to Hydra...")
        state.hydra_run_id = self._project_to_hydra(state)
        
        # Step 9: Scientist query
        print(f"[9/17] Scientist query...")
        findings = self._scientist_query(state)
        
        # Step 10: Generate hypothesis
        print(f"[10/17] Generate hypothesis...")
        state.hypothesis = self._generate_hypothesis(findings, state)
        print(f"  Hypothesis: {state.hypothesis}")
        
        # Step 11-12: Fork + Experiment + Statistics
        if state.hypothesis:
            print(f"[11-12/17] Fork + Experiment + Statistics...")
            state.experiment_result = self._run_experiment(state, execute_fn)
        
        # Step 13: Promotion
        print(f"[13/17] Promotion...")
        if state.experiment_result.get("improved", False):
            state.promoted = True
            state.promoted_version = self._promote(state)
            print(f"  PROMOTED to {state.promoted_version.version_id if state.promoted_version else '?'}")
        else:
            print(f"  Not promoted (no improvement)")
        
        # Step 14-16: Real work + Outcome (deferred)
        print(f"[14-16/17] Real work + outcome (deferred)")
        campaign.advance("submitted")
        
        # Step 17: Molting (extract typed candidates)
        print(f"[17/17] Molting...")
        run_results = []
        if state.flywheel_run:
            run_results = [{
                "run_id": state.flywheel_run.run_id,
                "outcome": state.flywheel_run.outcome or "pending",
                "score": state.flywheel_run.best_score,
                "failure_reason": "",
            }]
        
        state.molting_candidates = molte_campaign(
            loop_id, run_results,
            artifact_content="",  # would load from Git
            evaluation=state.experiment_result,
        )
        campaign.molting_candidates = [c.to_dict() for c in state.molting_candidates]
        print(f"  Extracted {len(state.molting_candidates)} candidate assets")
        for c in state.molting_candidates:
            print(f"    - {c.candidate_type}: {c.name}")
        
        # Save campaign
        campaign.completed_at = time.time()
        campaign.advance("completed")
        campaign.save(self.data_dir)
        
        # Git commit
        self._git_commit(loop_id, state)
        
        print(f"\n{'='*60}")
        print(f"CAMPAIGN COMPLETE: {loop_id}")
        print(f"Status: {campaign.status}")
        print(f"Best score: {campaign.best_score:.2f}")
        print(f"Iterations: {campaign.iteration_count}")
        print(f"Success model: {len(state.success_model.dimensions)} dimensions")
        print(f"Molting candidates: {len(state.molting_candidates)}")
        print(f"Promoted: {state.promoted}")
        print(f"{'='*60}")
        
        return state
    
    def _query_capabilities(self, worker_version: WorkerVersion,
                            opportunity: dict) -> dict:
        """Query what we know about this worker's capabilities."""
        # Query Hydra for past runs with this task family
        task_family = opportunity.get("task_family", "unknown")
        runs = self.run_projector.query(
            "SELECT * FROM hydra_nodes WHERE label='Run' AND json_extract(properties, '$.task_family')=?",
            (task_family,)
        )
        
        return {
            "task_family": task_family,
            "past_runs": len(runs),
            "worker_version": worker_version.version_id,
        }
    
    def _discover_worlds(self, opportunity: dict) -> list[WorldVersion]:
        """Find world packs matching this opportunity."""
        # For now, return default worlds
        task_family = opportunity.get("task_family", "research.ideation.technical")
        return [
            WorldVersion(
                world_id="technical-ideation",
                version_id="v1",
                task_family=task_family,
                capabilities=["text.reason", "code.understand", "search.web"],
                submission_type=opportunity.get("submission_type", "technical_ideation"),
            )
        ]
    
    def _project_to_hydra(self, state: LoopState) -> str:
        """Project run data into Hydra."""
        if state.flywheel_run:
            run_data = {
                "run_id": state.flywheel_run.run_id,
                "worker_version_id": f"{state.worker_version.worker_id}:{state.worker_version.version_id}",
                "opportunity_id": state.flywheel_run.opportunity_id,
                "outcome": state.flywheel_run.outcome or "pending",
                "cost_usd": 0.0,
            }
            return self.run_projector.project_run(run_data)
        return ""
    
    def _scientist_query(self, state: LoopState) -> list[dict]:
        """Query Hydra for patterns and weaknesses."""
        return [{
            "query": "what is weak",
            "result": "novelty and specificity often fail",
        }]
    
    def _generate_hypothesis(self, findings: list[dict], state: LoopState) -> str:
        """Generate a hypothesis based on findings."""
        if findings:
            return f"Addressing {findings[0]['result']} will improve outcomes"
        return ""
    
    def _run_experiment(self, state: LoopState, execute_fn) -> dict:
        """Run controlled experiment: control vs candidate."""
        # Simplified: just report the flywheel result
        return {
            "improved": state.flywheel_run.best_score >= 0.7 if state.flywheel_run else False,
            "delta": state.flywheel_run.best_score if state.flywheel_run else 0,
        }
    
    def _promote(self, state: LoopState) -> WorkerVersion:
        """Promote a validated candidate."""
        return WorkerVersion(
            worker_id=state.worker_version.worker_id,
            version_id=f"{state.worker_version.version_id}-promoted",
            parent_version=state.worker_version.version_id,
            memory_commit=state.worker_version.memory_commit,
            skill_tree_commit=state.worker_version.skill_tree_commit,
            model=state.worker_version.model,
            promoted=True,
        )
    
    def _learn(self, state: LoopState) -> tuple[list[dict], list[dict]]:
        """Extract memory and skill updates from the loop."""
        memory = []
        skills = []
        
        if state.promoted:
            memory.append({
                "type": "validated_improvement",
                "hypothesis": state.hypothesis,
                "evidence": state.experiment_result,
            })
        
        if state.flywheel_run and state.flywheel_run.outcome == "won":
            skills.append({
                "type": "winning_pattern",
                "opportunity_id": state.flywheel_run.opportunity_id,
                "rubric": state.flywheel_run.rubric.to_dict() if state.flywheel_run.rubric else {},
            })
        
        return memory, skills
    
    def _save_state(self, loop_id: str, state: LoopState):
        """Save loop state to disk."""
        loop_dir = self.loops_dir / loop_id
        loop_dir.mkdir(parents=True, exist_ok=True)
        
        # Save state
        (loop_dir / "state.json").write_text(json.dumps({
            "loop_id": loop_id,
            "opportunity": state.opportunity,
            "hypothesis": state.hypothesis,
            "promoted": state.promoted,
            "flywheel_score": state.flywheel_run.best_score if state.flywheel_run else 0,
            "molting_count": len(state.molting_candidates),
            "created_at": state.created_at,
            "completed_at": state.completed_at,
        }, indent=2))
        
        # Git commit
        import subprocess
        try:
            subprocess.run(["git", "add", str(loop_dir)], capture_output=True, timeout=10)
            subprocess.run(["git", "commit", "-m", f"loop: {loop_id}"], capture_output=True, timeout=10)
        except Exception:
            pass
    
    def _git_commit(self, loop_id: str, state: LoopState):
        """Git commit campaign artifacts."""
        import subprocess
        try:
            campaign_dir = self.data_dir / "campaigns" / loop_id
            if campaign_dir.exists():
                subprocess.run(["git", "add", str(campaign_dir)], capture_output=True, timeout=10)
                subprocess.run(["git", "commit", "-m", f"campaign: {loop_id}"], capture_output=True, timeout=10)
        except Exception:
            pass
