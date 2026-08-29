"""Trajectory export — convert WorkerKit events to normalized trajectory format.

WorkerKit events are the canonical economic/evidence record.
Trajectories are what a Letta worker can conveniently examine.
"""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrajectoryRecord:
    """One record in a normalized trajectory."""
    record_type: str = ""  # meta / user / assistant / tool_call / tool_result / observation
    content: str = ""
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)
    timestamp: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {"type": self.record_type, "content": self.content}
        if self.tool_name:
            d["tool_name"] = self.tool_name
        if self.tool_args:
            d["tool_args"] = self.tool_args
        if self.timestamp:
            d["timestamp"] = self.timestamp
        if self.metadata:
            d["metadata"] = self.metadata
        return d


@dataclass
class Trajectory:
    """Normalized trajectory from a WorkerKit run."""
    run_id: str = ""
    worker_id: str = ""
    fixture_id: str = ""
    records: list[TrajectoryRecord] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "worker_id": self.worker_id,
            "fixture_id": self.fixture_id,
            "records": [r.to_dict() for r in self.records],
            "metadata": self.metadata,
        }

    def to_markdown(self) -> str:
        """Human-readable markdown trajectory."""
        lines = [f"# Trajectory: {self.run_id}", f"Worker: {self.worker_id}", ""]
        for r in self.records:
            if r.record_type == "user":
                lines.append(f"## User\n{r.content}\n")
            elif r.record_type == "assistant":
                lines.append(f"## Assistant\n{r.content}\n")
            elif r.record_type == "tool_call":
                lines.append(f"## Tool Call: {r.tool_name}\n```json\n{json.dumps(r.tool_args, indent=2)}\n```\n")
            elif r.record_type == "tool_result":
                lines.append(f"## Tool Result\n{r.content[:500]}\n")
            elif r.record_type == "observation":
                lines.append(f"## Observation\n{r.content}\n")
        return "\n".join(lines)


def events_to_trajectory(events: list[dict], run_id: str = "",
                         worker_id: str = "") -> Trajectory:
    """Convert WorkerKit events to a normalized trajectory."""
    traj = Trajectory(run_id=run_id, worker_id=worker_id)

    for e in events:
        event_type = e.get("event_type", "")
        payload = e.get("payload", "")
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {"raw": payload}

        # Map WorkerKit events to trajectory records
        if event_type == "run.started":
            traj.records.append(TrajectoryRecord(
                record_type="meta",
                content=f"Run started: {payload.get('objective', '')}",
                timestamp=e.get("recorded_at", 0),
                metadata={"event_type": event_type},
            ))
        elif event_type == "model.call":
            traj.records.append(TrajectoryRecord(
                record_type="assistant",
                content=f"Model call: {payload.get('model', '')} ({payload.get('tokens', 0)} tokens)",
                timestamp=e.get("recorded_at", 0),
                metadata={"model": payload.get("model", ""), "tokens": payload.get("tokens", 0)},
            ))
        elif event_type == "artifact.registered":
            traj.records.append(TrajectoryRecord(
                record_type="observation",
                content=f"Artifact created: {payload.get('name', '')} (sha256: {payload.get('sha256', '')[:16]}...)",
                timestamp=e.get("recorded_at", 0),
                metadata={"artifact_name": payload.get("name", "")},
            ))
        elif event_type == "cost.recorded":
            traj.records.append(TrajectoryRecord(
                record_type="observation",
                content=f"Cost: ${payload.get('amount', 0)} ({payload.get('category', '')})",
                timestamp=e.get("recorded_at", 0),
                metadata={"category": payload.get("category", ""), "amount": payload.get("amount", 0)},
            ))
        elif event_type == "verification.completed":
            traj.records.append(TrajectoryRecord(
                record_type="observation",
                content=f"Verification: {payload.get('status', '')} ({payload.get('checks', 0)} checks, {payload.get('passed', 0)} passed)",
                timestamp=e.get("recorded_at", 0),
                metadata={"status": payload.get("status", "")},
            ))
        elif event_type == "gate.decided":
            traj.records.append(TrajectoryRecord(
                record_type="observation",
                content=f"Gate: {payload.get('decision', '')} (action: {payload.get('action', '')})",
                timestamp=e.get("recorded_at", 0),
                metadata={"decision": payload.get("decision", "")},
            ))
        elif event_type == "run.completed":
            traj.records.append(TrajectoryRecord(
                record_type="meta",
                content=f"Run completed: cost=${payload.get('cost', 0)}, events={payload.get('events', 0)}",
                timestamp=e.get("recorded_at", 0),
                metadata={"event_type": event_type},
            ))

    return traj


def trajectory_to_letta_messages(traj: Trajectory) -> list[dict]:
    """Convert trajectory to Letta-compatible message format."""
    messages = []
    for r in traj.records:
        if r.record_type == "user":
            messages.append({"role": "user", "content": r.content})
        elif r.record_type == "assistant":
            messages.append({"role": "assistant", "content": r.content})
        elif r.record_type == "observation":
            messages.append({"role": "system", "content": f"[observation] {r.content}"})
    return messages
