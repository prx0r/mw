from __future__ import annotations
import json
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from .records import CampaignRef, WorkerVersionRef, RunBinding, EvaluationRecord
from .runtime import WorkerRuntime
from .hashing import tree_digest, sha256_json
from .harbor import MockHarbor, HarborJobParser


def simple_scorer_v0(workspace: Path) -> dict[str, float]:
    p = workspace / "submission.md"
    if not p.exists():
        return {"requirements": 0.0, "technical": 0.0, "evidence": 0.0}
    text = p.read_text()
    return {
        "requirements": 1.0 if "Requirements" in text else 0.0,
        "technical": 1.0 if "Architecture" in text else 0.0,
        "evidence": 1.0 if "Evidence" in text and len(text) > 120 else 0.0,
    }


def stricter_scorer_v1(workspace: Path) -> dict[str, float]:
    p = workspace / "submission.md"
    text = p.read_text() if p.exists() else ""
    return {
        "requirements": 1.0 if "Requirements" in text and "tests" in text.lower() else 0.0,
        "technical": 1.0 if "Architecture" in text and "Harbor" in text else 0.0,
        "evidence": 1.0 if "Evidence" in text and "deterministic" in text.lower() else 0.0,
        "specificity": 1.0 if "Git" in text else 0.0,
    }


class FastCampaignHarness:
    """Checkpoint harness: real contracts, fake slow systems.

    This deliberately does NOT automate a magical 17-step loop. It exercises
    only the first production checkpoint: execute -> artifact -> grade -> bind ->
    regrade -> project.
    """
    def __init__(self, root: str | Path, runtime: WorkerRuntime):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.runtime = runtime
        self.harbor = MockHarbor(self.root / "mock-harbor")

    def execute_and_grade(self, opportunity_id: str, task: str, worker: WorkerVersionRef) -> tuple[RunBinding, EvaluationRecord, Path]:
        campaign_id = f"C-{uuid.uuid4().hex[:8]}"
        run_id = f"R-{uuid.uuid4().hex[:8]}"
        workspace = self.root / "campaigns" / campaign_id / "workspace"
        self.runtime.ensure_worker(worker.worker_id, model=worker.model)
        execution = self.runtime.execute(worker.worker_id, task, str(workspace))
        if not execution.ok:
            raise RuntimeError("worker execution failed")
        job = self.harbor.run_artifact(workspace, simple_scorer_v0)
        trial = HarborJobParser.trials(job)[0]
        binding = RunBinding(
            run_id=run_id,
            campaign=CampaignRef(campaign_id=campaign_id, opportunity_id=opportunity_id),
            worker=worker,
            execution=execution,
            workspace_digest=tree_digest(workspace),
            harbor_trial=trial,
            trajectory_ref=f"letta://{execution.conversation_id}" if execution.conversation_id else "",
        )
        eval_record = EvaluationRecord(
            evaluation_id=f"E-{uuid.uuid4().hex[:8]}", run_id=run_id,
            assessor_version="technical-submission/v0", reward=trial.reward,
            dimensions=trial.reward_dimensions, harbor_trial_dir=trial.trial_dir,
        )
        evidence_dir = self.root / "evidence" / run_id
        evidence_dir.mkdir(parents=True)
        (evidence_dir / "run-binding.json").write_text(json.dumps(binding.statement(), indent=2))
        (evidence_dir / "evaluation-v0.json").write_text(json.dumps(asdict(eval_record), indent=2))
        return binding, eval_record, job

    def regrade(self, binding: RunBinding, source_job: str | Path) -> EvaluationRecord:
        out = self.harbor.regrade(source_job, stricter_scorer_v1, assessor_version="v1")
        trial = HarborJobParser.trials(out)[0]
        record = EvaluationRecord(
            evaluation_id=f"E-{uuid.uuid4().hex[:8]}", run_id=binding.run_id,
            assessor_version="technical-submission/v1", reward=trial.reward,
            dimensions=trial.reward_dimensions, harbor_trial_dir=trial.trial_dir,
            source_trial_dir=binding.harbor_trial.trial_dir if binding.harbor_trial else "",
        )
        evidence_dir = self.root / "evidence" / binding.run_id
        (evidence_dir / "evaluation-v1.json").write_text(json.dumps(asdict(record), indent=2))
        return record
