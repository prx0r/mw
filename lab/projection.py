"""Lab Projection — wires EventLedger → HydraDB.

The EventLedger (core/events.py) is canonical truth.
HydraDB (Rust, distributed graph DB) is the graph store.
This module projects events into HydraDB.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from workerkit.core.events import EventLedger


class LabProjector:
    """Projects EventLedger events into HydraDB.

    Usage:
        projector = LabProjector(ledger, hydra_client)
        projector.rebuild()  # full rebuild from events
        projector.sync()     # incremental sync new events
    """

    def __init__(self, ledger: EventLedger, projection):
        self.ledger = ledger
        self.projection = projection
        self._last_sync_seq: dict[str, int] = {}  # run_id → last synced seq

    def rebuild(self) -> dict:
        """Drop and rebuild projection from all events."""
        self.projection.rebuild()

        # Get all unique run IDs
        conn = self.ledger._conn()
        rows = conn.execute("SELECT DISTINCT run_id FROM events").fetchall()
        conn.close()

        stats = {"runs": 0, "events": 0, "errors": 0}

        for (run_id,) in rows:
            try:
                self._project_run(run_id)
                stats["runs"] += 1
            except Exception as e:
                stats["errors"] += 1
                print(f"Error projecting run {run_id}: {e}")

        stats["events"] = self.ledger.count()
        return stats

    def sync(self) -> dict:
        """Incremental sync — project only new events."""
        stats = {"new_runs": 0, "new_events": 0, "errors": 0}

        conn = self.ledger._conn()
        rows = conn.execute("SELECT DISTINCT run_id FROM events").fetchall()
        conn.close()

        for (run_id,) in rows:
            last_seq = self._last_sync_seq.get(run_id, 0)
            events = self.ledger.get_events(run_id, since_seq=last_seq)
            if events:
                try:
                    self._project_run(run_id)
                    self._last_sync_seq[run_id] = max(e["seq"] for e in events)
                    stats["new_events"] += len(events)
                    stats["new_runs"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    print(f"Error syncing run {run_id}: {e}")

        return stats

    def _project_run(self, run_id: str) -> None:
        """Project a single run's events into LabProjection."""
        events = self.ledger.get_events(run_id)
        if not events:
            return

        # Extract run metadata from events
        agent_id = ""
        opportunity_id = ""
        task_family = ""
        model = ""
        tools = []
        skills = []
        cost_usd = 0.0
        duration_s = 0.0
        artifact_hash = ""
        evaluation_score = 0.0
        outcome = "pending"
        reward_usd = 0.0
        worker_version = ""
        failure_reason = ""

        for e in events:
            payload = json.loads(e["payload"]) if isinstance(e["payload"], str) else e["payload"]
            etype = e["event_type"]

            if etype == "run.started":
                agent_id = payload.get("agent_id", payload.get("order", ""))
                opportunity_id = payload.get("opportunity_id", "")
                task_family = payload.get("task_family", "")
                model = payload.get("model", "")
                tools = payload.get("tools", [])
                skills = payload.get("skills", [])
                worker_version = payload.get("worker_version", "")
            elif etype == "cost.recorded":
                cost_usd += float(payload.get("amount", 0))
            elif etype == "artifact.registered":
                artifact_hash = payload.get("sha256", artifact_hash)
            elif etype == "verification.completed":
                evaluation_score = payload.get("score", evaluation_score)
                if payload.get("status") == "FAIL":
                    outcome = "lost"
            elif etype == "gate.decided":
                if payload.get("decision") == "DENY":
                    outcome = "lost"
            elif etype == "run.completed":
                outcome = payload.get("outcome", outcome)
                reward_usd = float(payload.get("reward_usd", reward_usd))
                failure_reason = payload.get("failure_reason", failure_reason)
                cost_usd = float(payload.get("cost", cost_usd))

        # Determine final outcome
        if outcome == "pending":
            won_events = sum(1 for e in events if e["event_type"] == "gate.decided"
                           and json.loads(e["payload"]).get("decision") == "ALLOW")
            outcome = "won" if won_events > 0 else "lost"

        # Record in projection (append_only=False for rebuilds)
        try:
            self.projection.record_run(
                run_id=run_id,
                agent_id=agent_id,
                opportunity_id=opportunity_id,
                task_family=task_family,
                model=model,
                tools=tools,
                skills=skills,
                cost_usd=cost_usd,
                duration_s=duration_s,
                artifact_hash=artifact_hash,
                evaluation_score=evaluation_score,
                outcome=outcome,
                reward_usd=reward_usd,
                worker_version=worker_version,
                failure_reason=failure_reason,
            )
        except ValueError:
            # Append-only violation — run already projected, skip
            pass

    def project_run(self, run_id: str) -> None:
        """Project a single run (public interface)."""
        self._project_run(run_id)


def wire_lab(ledger_db: str = "data/wk-events.db",
             hydra_client=None) -> tuple[EventLedger, object, LabProjector]:
    """Convenience: create wired ledger + hydra client + projector."""
    ledger = EventLedger(ledger_db)
    # TODO: Wire real HydraDB client here
    projector = LabProjector(ledger, hydra_client)
    return ledger, hydra_client, projector
