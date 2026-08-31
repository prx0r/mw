"""Flywheel Runner — the complete opportunity → submit → learn loop.

Orchestrates: Oracle → Rubric → Worker → Evaluator → Git → Hydra → Learn
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from flywheel import (
    FlywheelRun, Rubric, MoltingResult,
    generate_rubric, molte_run, SUBMISSION_TYPES,
)
from flywheel.evaluator import run_gates


class FlywheelRunner:
    """Run the complete flywheel cycle for an opportunity.
    
    Usage:
        runner = FlywheelRunner(data_dir="data")
        result = runner.run_cycle(
            opportunity={...},
            worker_fn=my_worker_fn,
        )
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir = self.data_dir / "flywheel-runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
    
    def run_cycle(self, opportunity: dict, worker_fn, max_iterations: int = 3) -> FlywheelRun:
        """Run one complete flywheel cycle.
        
        1. Generate rubric from opportunity + past runs
        2. Worker generates artifact
        3. Evaluate against rubric
        4. If not good enough, refine and retry
        5. When ready or max iterations reached, return result
        """
        # 1. Create run
        run = FlywheelRun(
            run_id=f"fw-{int(time.time())}",
            opportunity_id=opportunity.get("id", "unknown"),
            worker_id=opportunity.get("worker_id", "default"),
            worker_version=opportunity.get("worker_version", "v1"),
        )
        
        # 2. Generate rubric
        past_runs = self._load_past_runs(opportunity.get("id", ""))
        run.rubric = generate_rubric(opportunity, past_runs)
        
        print(f"\n{'='*60}")
        print(f"FLYWHEEL: {run.opportunity_id}")
        print(f"Type: {run.rubric.submission_type}")
        print(f"Strategy: {run.rubric.recommended_strategy}")
        print(f"Rubric weights: {run.rubric.rubric_weights}")
        if run.rubric.failure_patterns:
            print(f"Avoid: {run.rubric.failure_patterns[:3]}")
        print(f"{'='*60}")
        
        # 3. Iterate
        for iteration in range(max_iterations):
            run.iteration_count = iteration + 1
            print(f"\n--- Iteration {iteration + 1}/{max_iterations} ---")
            
            # 3a. Worker generates artifact
            artifact_content = worker_fn(opportunity, run.rubric)
            artifact_hash = self._hash(artifact_content)
            run.current_artifact_hash = artifact_hash
            run.artifacts.append({
                "hash": artifact_hash,
                "iteration": iteration + 1,
                "length": len(artifact_content),
            })
            print(f"Artifact: {artifact_hash[:16]} ({len(artifact_content)} chars)")
            
            # 3b. Evaluate
            eval_result = self._evaluate(artifact_content, run)
            run.evaluations.append(eval_result)
            
            score = eval_result["overall_score"]
            gates_passed = eval_result["gates_passed"]
            print(f"Score: {score:.2f} | Gates: {gates_passed}/{len(run.rubric.quality_gates)}")
            
            if score > run.best_score:
                run.best_score = score
            
            # 3c. Check if good enough
            if gates_passed >= len(run.rubric.quality_gates) * 0.8 and score >= 0.7:
                print(f"\n>>> ARTIFACT READY (score={score:.2f}, gates={gates_passed}/{len(run.rubric.quality_gates)})")
                break
            
            # 3d. Provide feedback for next iteration
            failed_gates = [g for g in eval_result.get("gate_details", {}).items() if not g[1].get("passed", True)]
            if failed_gates:
                print(f"Failed: {[f[0] for f in failed_gates[:3]]}")
        
        # 4. Save run
        run.completed_at = time.time()
        run.save(self.runs_dir / run.run_id)
        
        # 5. Git commit
        self._git_commit(run, artifact_content)
        
        print(f"\n{'='*60}")
        print(f"FLYWHEEL COMPLETE: {run.run_id}")
        print(f"Best score: {run.best_score:.2f}")
        print(f"Iterations: {run.iteration_count}")
        print(f"Status: {'READY' if run.best_score >= 0.7 else 'NEEDS_WORK'}")
        print(f"{'='*60}")
        
        return run
    
    def submit(self, run: FlywheelRun, artifact_content: str,
               submission_url: str = "") -> FlywheelRun:
        """Mark a run as submitted."""
        run.submitted = True
        run.submission_url = submission_url
        run.save(self.runs_dir / run.run_id)
        return run
    
    def record_outcome(self, run: FlywheelRun, outcome: str,
                       reward_usd: float = 0.0) -> FlywheelRun:
        """Record the outcome of a submission."""
        run.outcome = outcome
        run.reward_usd = reward_usd
        run.save(self.runs_dir / run.run_id)
        
        # 6. Post-run molting
        if run.artifacts:
            artifact_content = ""  # would need to load from Git
            molting = molte_run(run, artifact_content, run.evaluations[-1] if run.evaluations else {})
            molting.save(self.runs_dir / run.run_id / "molting")
            
            # Extract lessons
            if outcome == "won":
                run.lessons_learned.append(f"Won with strategy: {run.rubric.recommended_strategy}")
            else:
                for pattern in run.rubric.failure_patterns[:3]:
                    run.lessons_learned.append(f"Avoid: {pattern}")
            
            run.save(self.runs_dir / run.run_id)
        
        return run
    
    def _evaluate(self, content: str, run: FlywheelRun) -> dict:
        """Evaluate artifact against rubric."""
        gate_results = run_gates(
            content=content,
            gate_names=run.rubric.quality_gates,
            requirements=run.rubric.requirements,
            past_submissions=[w.get("content", "") for w in run.rubric.past_wins],
        )
        
        gates_passed = sum(1 for g in gate_results if g.passed)
        overall_score = sum(g.score for g in gate_results) / len(gate_results) if gate_results else 0
        
        return {
            "overall_score": overall_score,
            "gates_passed": gates_passed,
            "gate_details": {g.gate: {"passed": g.passed, "score": g.score, "details": g.details} for g in gate_results},
        }
    
    def _load_past_runs(self, opportunity_id: str) -> list[dict]:
        """Load past runs for this opportunity type."""
        past = []
        if self.runs_dir.exists():
            for d in self.runs_dir.iterdir():
                if d.is_dir() and (d / "flywheel.json").exists():
                    try:
                        run_data = json.loads((d / "flywheel.json").read_text())
                        if run_data.get("outcome"):
                            past.append(run_data)
                    except:
                        pass
        return past
    
    def _hash(self, content: str) -> str:
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _git_commit(self, run: FlywheelRun, artifact_content: str):
        """Commit run artifacts to Git."""
        import subprocess
        try:
            # Create artifact file
            artifact_dir = self.runs_dir / run.run_id / "artifacts"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "submission.md").write_text(artifact_content)
            
            # Git add and commit
            subprocess.run(["git", "add", str(self.runs_dir / run.run_id)],
                         capture_output=True, timeout=10)
            subprocess.run(["git", "commit", "-m", f"flywheel: {run.run_id} ({run.outcome or 'pending'})"],
                         capture_output=True, timeout=10)
        except Exception:
            pass
