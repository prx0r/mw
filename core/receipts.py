"""WorkReceipt — the signed envelope over a complete run."""
from __future__ import annotations

import json
from workerkit.core.schema import uid, sha256


class WorkReceipt:
    """Signed receipt for a completed worker run."""

    def __init__(self, run, events_hash: str = ""):
        self.run_id = run.id
        self.worker_id = run.work_order_id
        self.events_hash = events_hash
        self.root_hash = self._compute_root(run, events_hash)

    def _compute_root(self, run, events_hash: str) -> str:
        parts = [
            run.work_order_id,
            events_hash,
            run.known_cost_usd,
            str(run.status),
            str(len(run.outputs)),
        ]
        return sha256(":".join(parts))

    def to_attestation(self) -> dict:
        return {
            "_type": "https://in-toto.io/Statement/v1",
            "subject": [{"name": "worker-run", "digest": {"sha256": self.root_hash}}],
            "predicateType": "https://moltwork.com/attestation/worker-run/v1",
            "predicate": {
                "runId": self.run_id,
                "workerId": self.worker_id,
                "eventsHash": self.events_hash,
                "rootHash": self.root_hash,
            },
        }

    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "receipt.json").write_text(json.dumps(self.to_attestation(), indent=2))
        (path / "root_hash.txt").write_text(self.root_hash)
