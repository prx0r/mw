"""SQLiteLabProjection — SQLite-backed lab projection (dev/fallback).

This is what hydra/store.py currently is. Renamed for truthfulness.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

try:
    from hydra.store import LabProjection as _LegacyProjection
except ImportError:
    from workerkit.hydra.store import LabProjection as _LegacyProjection


class SQLiteLabProjection:
    """SQLite-backed lab projection. Disposable, rebuildable from events."""

    def __init__(self, db_path: str = "data/hydra.db"):
        self._legacy = _LegacyProjection(db_path, append_only=False)

    def record_worker(self, worker_id: str, data: dict) -> None:
        self._legacy.upsert_agent(worker_id, data.get("template", ""), data.get("lineage", []))

    def record_version(self, version_id: str, worker_id: str, data: dict) -> None:
        self._legacy.record_worker_version(
            version_id, worker_id,
            af_hash=data.get("af_hash", ""),
            memfs_commit=data.get("memfs_commit", ""),
            skills_root=data.get("skills_root", ""),
            runtime_version=data.get("runtime_version", ""),
            parent_version=data.get("parent_version", ""),
        )

    def record_run(self, run_id: str, worker_id: str, data: dict) -> None:
        self._legacy.record_run(
            run_id=run_id, agent_id=worker_id,
            task_family=data.get("task_family", ""),
            model=data.get("model", ""),
            outcome=data.get("outcome", "pending"),
            cost_usd=data.get("cost_usd", 0),
            evaluation_score=data.get("evaluation_score", 0),
            reward_usd=data.get("reward_usd", 0),
            worker_version=data.get("worker_version", ""),
        )

    def record_artifact(self, artifact_id: str, data: dict) -> None:
        self._legacy.record_submission(
            submission_id=artifact_id,
            run_id=data.get("run_id", ""),
            agent_id=data.get("worker_id", ""),
            content_hash=data.get("sha256", ""),
            evaluation_score=data.get("score", 0),
            outcome=data.get("outcome", "pending"),
        )

    def record_verification(self, verification_id: str, data: dict) -> None:
        self._legacy.record_evaluation(
            evaluation_id=verification_id,
            run_id=data.get("run_id", ""),
            score=data.get("score", 0),
            gates_passed=data.get("gates_passed", []),
            reviewer=data.get("reviewer", ""),
        )

    def record_outcome(self, run_id: str, outcome: dict) -> None:
        self._legacy.record_run(
            run_id=run_id,
            outcome=outcome.get("status", "pending"),
            reward_usd=outcome.get("reward_usd", 0),
        )

    def record_learning(self, proposal_id: str, data: dict) -> None:
        self._legacy.record_experiment(
            experiment_id=proposal_id,
            hypothesis=data.get("hypothesis", ""),
            worker_version=data.get("worker_version", ""),
            status=data.get("status", "running"),
            data=data,
        )

    def retrieve_brief(self, task_family: str, worker_id: str) -> dict:
        from lab.context import LabContext
        ctx = LabContext(self._legacy, worker_id)
        pri = ctx.get_task_priors(task_family)
        skill = ctx.get_best_skill(task_family)
        return {"priors": pri, "best_skill": skill}

    def rebuild(self) -> None:
        self._legacy.rebuild()
