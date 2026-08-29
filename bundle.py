"""Worker Bundle — Moltwork Worker snapshot.

worker.json + agent.af + memory/ (git) + skills/ + mods/ + runtime.lock
Hashes: agent_file_hash, memfs_commit, skills_root, mods_root, runtime_version
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

from core.hashing import sha256


def dir_hash(path: Path) -> str:
    """Hash of all files under a directory."""
    if not path.exists(): return ""
    h = hashlib.sha256()
    for f in sorted(path.rglob("*")):
        if f.is_file():
            h.update(f.relative_to(path).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()


@dataclass
class WorkerBundle:
    """Snapshot of a worker at a point in time. Version in lineage."""
    worker_id: str = ""
    version: str = "v1"
    agent_file_hash: str = ""
    memfs_commit: str = ""
    skills_root: str = ""
    mods_root: str = ""
    runtime_version: str = ""
    template_parent: str = ""
    parent_version: str = ""
    created_at: float = field(default_factory=time.time)

    def bundle_hash(self) -> str:
        return sha256(json.dumps({
            "worker_id": self.worker_id, "version": self.version,
            "agent_file_hash": self.agent_file_hash, "memfs_commit": self.memfs_commit,
            "skills_root": self.skills_root, "mods_root": self.mods_root,
            "runtime_version": self.runtime_version, "template_parent": self.template_parent,
        }, sort_keys=True))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["bundle_hash"] = self.bundle_hash()
        return d

    @classmethod
    def from_paths(cls, worker_id: str, af_path: str | Path = "", memfs_path: str | Path = "",
                   skills_path: str | Path = "", mods_path: str | Path = "",
                   runtime_version: str = "", parent_version: str = "") -> "WorkerBundle":
        af_hash = sha256(Path(af_path).read_bytes()) if af_path and Path(af_path).exists() else ""
        # MemFS git commit — read HEAD if exists
        memfs_commit = ""
        if memfs_path and Path(memfs_path).exists():
            head = Path(memfs_path) / ".git" / "HEAD"
            if head.exists():
                try: memfs_commit = head.read_text().strip()[:40]
                except: pass
            if not memfs_commit:
                memfs_commit = dir_hash(Path(memfs_path))
        skills_root = dir_hash(Path(skills_path)) if skills_path and Path(skills_path).exists() else ""
        mods_root = dir_hash(Path(mods_path)) if mods_path and Path(mods_path).exists() else ""
        return cls(worker_id=worker_id, agent_file_hash=af_hash, memfs_commit=memfs_commit,
                   skills_root=skills_root, mods_root=mods_root,
                   runtime_version=runtime_version, parent_version=parent_version)
