"""WorkerManifest v0 — Bill of Materials for an economically useful worker.

Not a new agent serialization format. References standards:
  .af → Agent File (Letta)
  SKILL.md → Agent Skills
  A2A → Agent Card
  OCI → container digest
  MCP → tool servers

Example:
{
  "worker": "researcher-v12",
  "agent": {"format": "agent-file", "uri": "researcher-v12.af", "sha256": "..."},
  "skills": [{"format": "agent-skills", "uri": "./skills/research", "sha256": "..."}],
  "runtime": {"adapter": "letta", "image": "ghcr.io/...@sha256:..."},
  "interfaces": {"a2a": "./agent-card.json", "mcp": ["moltwork", "github"]},
  "policy": {"maxCostUsd": 4, "allowedModels": ["glm-5.3-flash"]}
}
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    from workerkit.evidence.canonical import sha256 as _wk_sha256
    def sha256(data): return _wk_sha256(data)
except ImportError:
    def sha256(data: str | bytes) -> str:
        if isinstance(data, str): data = data.encode()
        return hashlib.sha256(data).hexdigest()


def file_sha256(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()


@dataclass
class AgentRef:
    format: str = "agent-file"  # agent-file | prompt | custom
    uri: str = ""  # path to .af file
    sha256: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SkillRef:
    format: str = "agent-skills"  # agent-skills | mcp | custom
    uri: str = ""
    sha256: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RuntimeRef:
    adapter: str = "letta"  # letta | openclaw | hermes | openhands | custom
    image: str = ""  # ghcr.io/...@sha256:...
    version: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkerManifest:
    """Bill of Materials for a Moltwork worker. v0."""

    schema_version: str = "moltwork.worker-manifest.v0"
    worker: str = ""  # e.g. researcher-v12

    agent: AgentRef = field(default_factory=AgentRef)
    skills: list[SkillRef] = field(default_factory=list)
    runtime: RuntimeRef = field(default_factory=RuntimeRef)

    interfaces: dict = field(default_factory=lambda: {"a2a": "", "mcp": []})
    policy: dict = field(default_factory=lambda: {"maxCostUsd": 4})

    created_at: float = field(default_factory=time.time)

    def manifest_hash(self) -> str:
        """Content hash of the manifest (excluding created_at)."""
        d = {
            "schemaVersion": self.schema_version,
            "worker": self.worker,
            "agent": self.agent.to_dict(),
            "skills": [s.to_dict() for s in self.skills],
            "runtime": self.runtime.to_dict(),
            "interfaces": self.interfaces,
            "policy": self.policy,
        }
        return sha256(json.dumps(d, sort_keys=True))

    def to_dict(self) -> dict:
        return {
            "schemaVersion": self.schema_version,
            "worker": self.worker,
            "agent": self.agent.to_dict(),
            "skills": [s.to_dict() for s in self.skills],
            "runtime": self.runtime.to_dict(),
            "interfaces": self.interfaces,
            "policy": self.policy,
            "manifestHash": self.manifest_hash(),
            "createdAt": self.created_at,
        }

    def save(self, path: str | Path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "WorkerManifest":
        d = json.loads(Path(path).read_text())
        m = cls(worker=d.get("worker", ""))
        if "agent" in d:
            m.agent = AgentRef(**{k: v for k, v in d["agent"].items() if k in AgentRef.__dataclass_fields__})
        for s in d.get("skills", []):
            m.skills.append(SkillRef(**{k: v for k, v in s.items() if k in SkillRef.__dataclass_fields__}))
        if "runtime" in d:
            m.runtime = RuntimeRef(**{k: v for k, v in d["runtime"].items() if k in RuntimeRef.__dataclass_fields__})
        m.interfaces = d.get("interfaces", {})
        m.policy = d.get("policy", {})
        m.created_at = d.get("createdAt", time.time())
        return m


def build_manifest(
    worker_name: str,
    af_path: str = "",
    skill_paths: list[str] | None = None,
    runtime_adapter: str = "letta",
    runtime_image: str = "",
) -> WorkerManifest:
    """Build a WorkerManifest from local files."""
    m = WorkerManifest(worker=worker_name, runtime=RuntimeRef(adapter=runtime_adapter, image=runtime_image))
    if af_path and Path(af_path).exists():
        m.agent = AgentRef(format="agent-file", uri=af_path, sha256=file_sha256(af_path))
    for sp in skill_paths or []:
        if Path(sp).exists():
            # Skill dir: hash all SKILL.md files inside
            if Path(sp).is_dir():
                h = hashlib.sha256()
                for f in sorted(Path(sp).rglob("SKILL.md")):
                    h.update(f.read_bytes())
                m.skills.append(SkillRef(format="agent-skills", uri=sp, sha256=h.hexdigest()))
            else:
                m.skills.append(SkillRef(format="agent-skills", uri=sp, sha256=file_sha256(sp)))
    return m
