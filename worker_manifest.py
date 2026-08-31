"""WorkerManifest v1 — Bill of Materials for an economically useful worker.

References:
  MemoryRef → where cognition lives (Letta MemFS)
  WorkspaceRef → where code lives (Git)
  TrajectoryRef → what happened (pluggable format)
  SkillRef → procedural assets (Agent Skills standard)
  AssetVersion → portable worker snapshot (.af)
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

from core.hashing import sha256


def file_sha256(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()


@dataclass
class AgentRef:
    format: str = "agent-file"
    uri: str = ""
    sha256: str = ""
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SkillRef:
    format: str = "agent-skills"
    uri: str = ""
    sha256: str = ""
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RuntimeRef:
    adapter: str = "letta-agent-sdk"
    backend: str = "local"
    sdk_version: str = ""
    image: str = ""
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkerManifest:
    """Bill of Materials for a Moltwork worker. v1."""
    schema_version: str = "moltwork.worker-manifest.v1"
    worker_id: str = ""
    version_id: str = ""  # content digest of this manifest
    parent_version: str = ""

    # Runtime
    runtime: RuntimeRef = field(default_factory=RuntimeRef)

    # Agent (Letta)
    agent: AgentRef = field(default_factory=AgentRef)
    agent_id: str = ""  # Letta agent ID

    # Memory (where cognition lives)
    memory_commit: str = ""  # MemFS Git commit
    memory_tree_digest: str = ""  # SHA-256 of file tree

    # Skills (procedural assets)
    skills: list[SkillRef] = field(default_factory=list)
    skills_tree_digest: str = ""

    # Model
    model_id: str = ""
    model_provider: str = ""
    model_settings_digest: str = ""

    # Tools
    tool_policy_digest: str = ""
    tool_schema_digest: str = ""

    # WorkerKit
    workerkit_version: str = "0.1.0"
    evidence_schema: str = "moltwork:event:v1"

    # Promotion
    learning_proposal: str = ""  # proposal_id if promoted
    experiment_receipt: str = ""  # receipt_id if promoted

    created_at: float = field(default_factory=time.time)

    def manifest_hash(self) -> str:
        """Content-addressed hash of this manifest.

        Excludes versionId and manifestHash (self-referential).
        Includes ALL security-relevant fields.
        """
        d = {
            "schemaVersion": self.schema_version,
            "workerId": self.worker_id,
            "parentVersion": self.parent_version,
            "runtime": self.runtime.to_dict(),
            "agent": self.agent.to_dict(),
            "agentId": self.agent_id,
            "memoryCommit": self.memory_commit,
            "memoryTreeDigest": self.memory_tree_digest,
            "skills": [s.to_dict() for s in self.skills],
            "skillsTreeDigest": self.skills_tree_digest,
            "modelId": self.model_id,
            "modelProvider": self.model_provider,
            "modelSettingsDigest": self.model_settings_digest,
            "toolPolicyDigest": self.tool_policy_digest,
            "toolSchemaDigest": self.tool_schema_digest,
            "workerkitVersion": self.workerkit_version,
            "evidenceSchema": self.evidence_schema,
            "learningProposal": self.learning_proposal,
            "experimentReceipt": self.experiment_receipt,
        }
        return sha256(json.dumps(d, sort_keys=True).encode())

    def to_dict(self) -> dict:
        d = {
            "schemaVersion": self.schema_version,
            "workerId": self.worker_id,
            "versionId": self.version_id or self.manifest_hash(),
            "parentVersion": self.parent_version,
            "runtime": self.runtime.to_dict(),
            "agent": self.agent.to_dict(),
            "agentId": self.agent_id,
            "memory": {
                "commit": self.memory_commit,
                "treeDigest": self.memory_tree_digest,
            },
            "skills": [s.to_dict() for s in self.skills],
            "skillsTreeDigest": self.skills_tree_digest,
            "model": {
                "id": self.model_id,
                "provider": self.model_provider,
                "settingsDigest": self.model_settings_digest,
            },
            "tools": {
                "policyDigest": self.tool_policy_digest,
                "schemaDigest": self.tool_schema_digest,
            },
            "workerkit": {
                "version": self.workerkit_version,
                "evidenceSchema": self.evidence_schema,
            },
            "promotion": {
                "learningProposal": self.learning_proposal,
                "experimentReceipt": self.experiment_receipt,
            },
        }
        d["manifestHash"] = self.manifest_hash()
        return d

    def save(self, path: str | Path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "WorkerManifest":
        d = json.loads(Path(path).read_text())
        m = cls(worker_id=d.get("workerId", ""))
        m.version_id = d.get("versionId", "")
        m.parent_version = d.get("parentVersion", "")
        if "runtime" in d:
            m.runtime = RuntimeRef(**{k: v for k, v in d["runtime"].items() if k in RuntimeRef.__dataclass_fields__})
        m.agent_id = d.get("agentId", "")
        if "agent" in d:
            m.agent = AgentRef(**{k: v for k, v in d["agent"].items() if k in AgentRef.__dataclass_fields__})
        mem = d.get("memory", {})
        m.memory_commit = mem.get("commit", "")
        m.memory_tree_digest = mem.get("treeDigest", "")
        for s in d.get("skills", []):
            m.skills.append(SkillRef(**{k: v for k, v in s.items() if k in SkillRef.__dataclass_fields__}))
        m.skills_tree_digest = d.get("skillsTreeDigest", "")
        model = d.get("model", {})
        m.model_id = model.get("id", "")
        m.model_provider = model.get("provider", "")
        m.model_settings_digest = model.get("settingsDigest", "")
        tools = d.get("tools", {})
        m.tool_policy_digest = tools.get("policyDigest", "")
        m.tool_schema_digest = tools.get("schemaDigest", "")
        wk = d.get("workerkit", {})
        m.workerkit_version = wk.get("version", "0.1.0")
        m.evidence_schema = wk.get("evidenceSchema", "moltwork:event:v1")
        promo = d.get("promotion", {})
        m.learning_proposal = promo.get("learningProposal", "")
        m.experiment_receipt = promo.get("experimentReceipt", "")
        return m


def build_manifest(
    worker_name: str,
    agent_id: str = "",
    af_path: str = "",
    skill_paths: list[str] | None = None,
    runtime_adapter: str = "letta-agent-sdk",
    model_id: str = "opencode-go/mimo-v2.5",
) -> WorkerManifest:
    m = WorkerManifest(
        worker_id=worker_name,
        agent_id=agent_id,
        runtime=RuntimeRef(adapter=runtime_adapter),
        model_id=model_id,
    )
    if af_path and Path(af_path).exists():
        m.agent = AgentRef(format="agent-file", uri=af_path, sha256=file_sha256(af_path))
    for sp in skill_paths or []:
        if Path(sp).exists():
            if Path(sp).is_dir():
                h = hashlib.sha256()
                for f in sorted(Path(sp).rglob("SKILL.md")):
                    h.update(f.read_bytes())
                m.skills.append(SkillRef(format="agent-skills", uri=sp, sha256=h.hexdigest()))
            else:
                m.skills.append(SkillRef(format="agent-skills", uri=sp, sha256=file_sha256(sp)))
    return m
