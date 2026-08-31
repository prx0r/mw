from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
from .hashing import sha256_json


@dataclass(frozen=True)
class CampaignRef:
    campaign_id: str
    opportunity_id: str
    git_commit: str = ""


@dataclass(frozen=True)
class WorkerVersionRef:
    worker_id: str
    version_id: str
    letta_agent_id: str = ""
    memory_commit: str = ""
    skills_commit: str = ""
    model: str = ""


@dataclass(frozen=True)
class CredentialRef:
    """Reference only. Never put secret material in this record."""
    provider: str
    ref: str
    scopes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        suspicious = ("sk-", "api_key=", "token=", "secret=")
        raw = (self.ref + " " + " ".join(self.scopes)).lower()
        if any(x in raw for x in suspicious):
            raise ValueError("CredentialRef must not contain raw secret material")


@dataclass
class WorkerExecution:
    ok: bool
    worker_id: str
    conversation_id: str = ""
    session_id: str = ""
    output_content: str = ""
    artifact_paths: list[str] = field(default_factory=list)
    duration_ms: int = 0
    cost_usd: float = 0.0
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HarborTrialRecord:
    trial_dir: str
    trial_id: str = ""
    reward: float | None = None
    reward_dimensions: dict[str, float] = field(default_factory=dict)
    lock: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    artifact_manifest: list[dict[str, Any]] = field(default_factory=list)
    source_trial: dict[str, Any] | None = None
    lock_digest: str = ""
    result_digest: str = ""


@dataclass
class EvaluationRecord:
    evaluation_id: str
    run_id: str
    assessor_version: str
    reward: float | None
    dimensions: dict[str, float] = field(default_factory=dict)
    harbor_trial_dir: str = ""
    source_trial_dir: str = ""


@dataclass
class RunBinding:
    """The small Moltwork-owned binding between upstream evidence systems."""
    run_id: str
    campaign: CampaignRef
    worker: WorkerVersionRef
    execution: WorkerExecution
    workspace_digest: str
    harbor_trial: HarborTrialRecord | None = None
    trajectory_ref: str = ""
    trajectory_digest: str = ""
    workerkit_chain_head: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def statement(self) -> dict[str, Any]:
        d = {
            "schema": "moltwork:run-binding:v1",
            "run_id": self.run_id,
            "campaign": asdict(self.campaign),
            "worker": asdict(self.worker),
            "execution": {
                "worker_id": self.execution.worker_id,
                "conversation_id": self.execution.conversation_id,
                "session_id": self.execution.session_id,
                "duration_ms": self.execution.duration_ms,
                "cost_usd": self.execution.cost_usd,
            },
            "workspace_digest": self.workspace_digest,
            "trajectory_ref": self.trajectory_ref,
            "trajectory_digest": self.trajectory_digest,
            "workerkit_chain_head": self.workerkit_chain_head,
            "harbor": None,
            "metadata": self.metadata,
        }
        if self.harbor_trial:
            d["harbor"] = {
                "trial_dir": self.harbor_trial.trial_dir,
                "trial_id": self.harbor_trial.trial_id,
                "lock_digest": self.harbor_trial.lock_digest,
                "result_digest": self.harbor_trial.result_digest,
            }
        return d

    def content_hash(self) -> str:
        return sha256_json(self.statement())
