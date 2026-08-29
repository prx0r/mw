"""HydraLabProjection — SQLite fallback for HydraDB.

When HydraDB is available, would use Cypher queries.
Currently delegates to SQLiteLabProjection.
"""
from __future__ import annotations

from typing import Any

from lab.projections.sqlite import SQLiteLabProjection


class HydraLabProjection:
    """Lab projection with SQLite fallback.

    In production with HydraDB:
    - Uses OpenCypher queries over graph
    - Supports complex traversal (Worker → Version → Run → Artifact)
    - Rebuildable from canonical event ledger

    Currently: delegates to SQLite.
    """

    def __init__(self, db_path: str = "data/hydra.db", hydra_url: str = ""):
        self.hydra_url = hydra_url
        self._fallback = SQLiteLabProjection(db_path)
        self._available = False

        if hydra_url:
            try:
                import httpx
                resp = httpx.get(f"{hydra_url}/health", timeout=5)
                self._available = resp.status_code == 200
            except Exception:
                self._available = False

    def record_worker(self, worker_id: str, data: dict) -> None:
        self._fallback.record_worker(worker_id, data)

    def record_version(self, version_id: str, worker_id: str, data: dict) -> None:
        self._fallback.record_version(version_id, worker_id, data)

    def record_run(self, run_id: str, worker_id: str, data: dict) -> None:
        self._fallback.record_run(run_id, worker_id, data)

    def record_artifact(self, artifact_id: str, data: dict) -> None:
        self._fallback.record_artifact(artifact_id, data)

    def record_verification(self, verification_id: str, data: dict) -> None:
        self._fallback.record_verification(verification_id, data)

    def record_outcome(self, run_id: str, outcome: dict) -> None:
        self._fallback.record_outcome(run_id, outcome)

    def record_learning(self, proposal_id: str, data: dict) -> None:
        self._fallback.record_learning(proposal_id, data)

    def retrieve_brief(self, task_family: str, worker_id: str) -> dict:
        return self._fallback.retrieve_brief(task_family, worker_id)

    def rebuild(self) -> None:
        self._fallback.rebuild()
