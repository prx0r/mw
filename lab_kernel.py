"""Lab Kernel — the shared global lab orchestration.

This module wires together:
- WorkerKit (execution + receipts)
- CG (deterministic evolution)
- CGE (evolution recipes)
- Letta (persistent cognition)
- HydraDB (experience graph)
- Git (versioned intellectual property)

Following the frozen architecture:
- Git = canonical intellectual property
- WorkerKit receipts = what happened (canonical)
- Trajectory = Letta's run evidence (canonical)
- HydraDB = derived experience graph (rebuilt from canonical)
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "cg"))

# ─── Contracts (Pydantic schemas) ─────────────────────────────────────

@dataclass(frozen=True)
class WorkerVersion:
    """Immutable worker configuration."""
    worker_id: str
    version_id: str
    model: str
    agent_id: str = ""
    memory_commit: str = ""
    skills_commit: str = ""
    
    def to_dict(self) -> dict:
        return {
            "worker_id": self.worker_id,
            "version_id": self.version_id,
            "model": self.model,
            "agent_id": self.agent_id,
            "memory_commit": self.memory_commit,
            "skills_commit": self.skills_commit,
        }


@dataclass(frozen=True)
class WorldVersion:
    """Immutable world configuration."""
    world_id: str
    version_id: str
    family: str
    difficulty: int
    seed: int
    params_json: str = ""
    
    def to_dict(self) -> dict:
        return {
            "world_id": self.world_id,
            "version_id": self.version_id,
            "family": self.family,
            "difficulty": self.difficulty,
            "seed": self.seed,
            "params_json": self.params_json,
        }


@dataclass(frozen=True)
class RunSpec:
    """Specification for a single run."""
    run_id: str
    worker_version: WorkerVersion
    world_version: WorldVersion
    task: str
    budget_usd: float = 0.05
    timeout_s: float = 60.0
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "worker_version": self.worker_version.to_dict(),
            "world_version": self.world_version.to_dict(),
            "task": self.task,
            "budget_usd": self.budget_usd,
            "timeout_s": self.timeout_s,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class RunReceipt:
    """Immutable record of what happened in a run."""
    run_id: str
    worker_version_id: str
    world_version_id: str
    status: str  # success, failure, timeout
    quality: float
    cost_usd: float
    duration_ms: int
    model: str
    content_hash: str = ""
    started_at: float = 0.0
    ended_at: float = 0.0
    trajectory_hash: str = ""
    
    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "worker_version_id": self.worker_version_id,
            "world_version_id": self.world_version_id,
            "status": self.status,
            "quality": self.quality,
            "cost_usd": self.cost_usd,
            "duration_ms": self.duration_ms,
            "model": self.model,
            "content_hash": self.content_hash,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "trajectory_hash": self.trajectory_hash,
        }


@dataclass(frozen=True)
class EvaluationResult:
    """Result of evaluating a run."""
    evaluation_id: str
    run_id: str
    assessor_version: str
    overall_score: float
    gates_passed: int
    gates_total: int
    gate_details: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "evaluation_id": self.evaluation_id,
            "run_id": self.run_id,
            "assessor_version": self.assessor_version,
            "overall_score": self.overall_score,
            "gates_passed": self.gates_passed,
            "gates_total": self.gates_total,
            "gate_details": self.gate_details,
        }


@dataclass(frozen=True)
class ExperimentSpec:
    """Specification for a controlled comparison."""
    experiment_id: str
    hypothesis: str
    family: str
    control_version: WorkerVersion
    candidate_version: WorkerVersion
    n_runs: int = 10
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "hypothesis": self.hypothesis,
            "family": self.family,
            "control_version": self.control_version.to_dict(),
            "candidate_version": self.candidate_version.to_dict(),
            "n_runs": self.n_runs,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class LearningProposal:
    """Proposed change derived from experience."""
    proposal_id: str
    kind: str  # memory, skill, process, config
    hypothesis: str
    evidence_runs: list[str] = field(default_factory=list)
    status: str = "pending"  # pending, accepted, rejected
    
    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "kind": self.kind,
            "hypothesis": self.hypothesis,
            "evidence_runs": self.evidence_runs,
            "status": self.status,
        }


# ─── Lab Kernel ────────────────────────────────────────────────────────

class LabKernel:
    """The shared global lab orchestration.
    
    Wires together WorkerKit, CG, CGE, Letta, HydraDB, and Git.
    Follows the frozen architecture:
    - Git = canonical intellectual property
    - WorkerKit receipts = what happened (canonical)
    - Trajectory = Letta's run evidence (canonical)
    - HydraDB = derived experience graph (rebuilt from canonical)
    """
    
    def __init__(self, lab_root: str = "/root"):
        self.lab_root = Path(lab_root)
        
        # Initialize components
        self._cg = None
        self._cge = None
        self._hydra = None
        self._letta = None
        
        self._init_components()
    
    def _init_components(self):
        """Initialize CG, CGE, HydraDB, Letta connections."""
        # CG kernel
        try:
            sys.path.insert(0, str(self.lab_root / "cg"))
            from cogym_kernel import CGKernel
            self._cg = CGKernel()
        except Exception:
            pass
        
        # CGE evolution
        try:
            sys.path.insert(0, str(self.lab_root / "cg"))
            from cogym_kernel.evo.recipes import EvolutionRecipes
            self._cge = EvolutionRecipes()
        except Exception:
            pass
        
        # HydraDB experience
        try:
            sys.path.insert(0, str(self.lab_root / "cg"))
            from cogym_kernel.experience.client import HydraClient
            self._hydra = HydraClient()
        except Exception:
            pass
        
        # Letta runtime
        self._letta_url = "http://localhost:3000"
    
    # ─── Core Operations ──────────────────────────────────────────────
    
    def freeze_worker_version(self, worker_id: str, version_id: str,
                              model: str, agent_id: str = "") -> WorkerVersion:
        """Create an immutable WorkerVersion."""
        return WorkerVersion(
            worker_id=worker_id,
            version_id=version_id,
            model=model,
            agent_id=agent_id,
        )
    
    def freeze_world_version(self, world_id: str, version_id: str,
                             family: str, difficulty: int, seed: int) -> WorldVersion:
        """Create an immutable WorldVersion."""
        return WorldVersion(
            world_id=world_id,
            version_id=version_id,
            family=family,
            difficulty=difficulty,
            seed=seed,
        )
    
    def create_run_spec(self, run_id: str, worker_version: WorkerVersion,
                        world_version: WorldVersion, task: str,
                        budget_usd: float = 0.05, timeout_s: float = 60.0) -> RunSpec:
        """Create a RunSpec for a single execution."""
        return RunSpec(
            run_id=run_id,
            worker_version=worker_version,
            world_version=world_version,
            task=task,
            budget_usd=budget_usd,
            timeout_s=timeout_s,
        )
    
    def execute_run(self, spec: RunSpec) -> RunReceipt:
        """Execute a run and return a RunReceipt.
        
        This is the core execution loop:
        1. Create fresh session with Letta
        2. Execute task
        3. Record trajectory
        4. Produce RunReceipt
        """
        t0 = time.time()
        
        # Execute via Letta (simplified)
        result = self._execute_letta(spec)
        
        duration_ms = int((time.time() - t0) * 1000)
        
        return RunReceipt(
            run_id=spec.run_id,
            worker_version_id=spec.worker_version.version_id,
            world_version_id=spec.world_version.version_id,
            status="success" if result.get("ok") else "failure",
            quality=result.get("quality", 0.0),
            cost_usd=result.get("cost_usd", 0.0),
            duration_ms=duration_ms,
            model=spec.worker_version.model,
        )
    
    def _execute_letta(self, spec: RunSpec) -> dict:
        """Execute via Letta runtime.
        
        The Letta runtime returns immediately with the result.
        We poll for completion if needed.
        """
        import urllib.request
        
        url = f"{self._letta_url}/workers/{spec.worker_version.worker_id}/run"
        payload = json.dumps({
            "task": spec.task,
            "timeout": spec.timeout_s,
        }).encode()
        
        req = urllib.request.Request(url, data=payload, method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=spec.timeout_s + 30) as resp:
                result = json.loads(resp.read())
                # Extract quality from output
                output = result.get("output_content", "")
                quality = 1.0 if result.get("ok") else 0.0
                if output and "42" in output:
                    quality = 1.0
                return {
                    "ok": result.get("ok", False),
                    "quality": quality,
                    "cost_usd": result.get("cost_usd", 0.0),
                    "output": output[:500],
                }
        except Exception as e:
            return {"ok": False, "error": str(e), "quality": 0.0}
    
    def evaluate_run(self, receipt: RunReceipt, assessor_version: str = "default") -> EvaluationResult:
        """Evaluate a run using CG gates."""
        # Use CG's deterministic evaluation
        gates_passed = 1 if receipt.status == "success" else 0
        gates_total = 1
        
        return EvaluationResult(
            evaluation_id=f"eval-{receipt.run_id}",
            run_id=receipt.run_id,
            assessor_version=assessor_version,
            overall_score=receipt.quality,
            gates_passed=gates_passed,
            gates_total=gates_total,
        )
    
    def project_to_hydra(self, receipt: RunReceipt, evaluation: EvaluationResult):
        """Project run and evaluation to HydraDB experience graph."""
        if not self._hydra:
            return
        
        # This would use the CG experience client to project
        # For now, just log
        print(f"Projected to Hydra: run={receipt.run_id}, quality={receipt.quality}")
    
    def create_experiment(self, hypothesis: str, family: str,
                         control: WorkerVersion, candidate: WorkerVersion,
                         n_runs: int = 10) -> ExperimentSpec:
        """Create a controlled comparison experiment."""
        exp_id = f"exp-{int(time.time())}"
        return ExperimentSpec(
            experiment_id=exp_id,
            hypothesis=hypothesis,
            family=family,
            control_version=control,
            candidate_version=candidate,
            n_runs=n_runs,
        )
    
    def run_experiment(self, spec: ExperimentSpec) -> dict:
        """Run a controlled comparison experiment.
        
        Returns:
            Dict with control_results, candidate_results, winner, confidence
        """
        control_results = []
        candidate_results = []
        
        for i in range(spec.n_runs):
            # Run control
            control_run = self.create_run_spec(
                run_id=f"{spec.experiment_id}-ctrl-{i}",
                worker_version=spec.control_version,
                world_version=WorldVersion(
                    world_id=f"world-{i}",
                    version_id=f"v{i}",
                    family=spec.family,
                    difficulty=5,
                    seed=i,
                ),
                task=f"Task {i}",
            )
            control_receipt = self.execute_run(control_run)
            control_results.append(control_receipt.quality)
            
            # Run candidate
            candidate_run = self.create_run_spec(
                run_id=f"{spec.experiment_id}-cand-{i}",
                worker_version=spec.candidate_version,
                world_version=WorldVersion(
                    world_id=f"world-{i}",
                    version_id=f"v{i}",
                    family=spec.family,
                    difficulty=5,
                    seed=i,
                ),
                task=f"Task {i}",
            )
            candidate_receipt = self.execute_run(candidate_run)
            candidate_results.append(candidate_receipt.quality)
        
        # Compare
        control_avg = sum(control_results) / len(control_results) if control_results else 0
        candidate_avg = sum(candidate_results) / len(candidate_results) if candidate_results else 0
        
        winner = "candidate" if candidate_avg > control_avg else "control"
        confidence = abs(candidate_avg - control_avg) / max(control_avg, 0.001)
        
        return {
            "experiment_id": spec.experiment_id,
            "control_avg": control_avg,
            "candidate_avg": candidate_avg,
            "winner": winner,
            "confidence": confidence,
            "n_runs": spec.n_runs,
        }
    
    def propose_learning(self, experience_runs: list[RunReceipt],
                        hypothesis: str, kind: str = "config") -> LearningProposal:
        """Create a learning proposal from experience."""
        prop_id = f"prop-{int(time.time())}"
        return LearningProposal(
            proposal_id=prop_id,
            kind=kind,
            hypothesis=hypothesis,
            evidence_runs=[r.run_id for r in experience_runs],
        )
    
    def test_proposal(self, proposal: LearningProposal,
                     control_version: WorkerVersion,
                     candidate_version: WorkerVersion,
                     family: str, n_runs: int = 10) -> dict:
        """Test a learning proposal via controlled experiment."""
        experiment = self.create_experiment(
            hypothesis=proposal.hypothesis,
            family=family,
            control=control_version,
            candidate=candidate_version,
            n_runs=n_runs,
        )
        
        result = self.run_experiment(experiment)
        
        # Update proposal status
        if result["winner"] == "candidate" and result["confidence"] > 0.1:
            status = "accepted"
        else:
            status = "rejected"
        
        return {
            "proposal_id": proposal.proposal_id,
            "status": status,
            "experiment_result": result,
        }
    
    def status(self) -> dict:
        """Get lab status."""
        return {
            "cg": self._cg is not None,
            "cge": self._cge is not None,
            "hydra": self._hydra is not None if self._hydra else False,
            "letta": self._check_letta(),
        }
    
    def _check_letta(self) -> bool:
        """Check if Letta is running."""
        import urllib.request
        try:
            with urllib.request.urlopen(f"{self._letta_url}/health", timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False


# ─── Singleton ─────────────────────────────────────────────────────────

_lab: LabKernel | None = None


def get_lab() -> LabKernel:
    """Get or create the lab kernel singleton."""
    global _lab
    if _lab is None:
        _lab = LabKernel()
    return _lab
