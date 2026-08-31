from __future__ import annotations
import json
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Callable
from .records import HarborTrialRecord
from .hashing import sha256_file, sha256_json


def _extract_reward(result: dict) -> tuple[float | None, dict[str, float]]:
    # Harbor result shapes can evolve; accept common locations defensively.
    candidates = [result.get("reward"), result.get("verifier_result"), result.get("rewards")]
    dims: dict[str, float] = {}
    scalar: float | None = None
    for c in candidates:
        if isinstance(c, (int, float)):
            scalar = float(c)
            break
        if isinstance(c, dict):
            for k, v in c.items():
                if isinstance(v, (int, float)):
                    dims[str(k)] = float(v)
            if "reward" in dims:
                scalar = dims["reward"]
            elif dims and scalar is None:
                scalar = sum(dims.values()) / len(dims)
    return scalar, dims


class HarborJobParser:
    @staticmethod
    def parse_trial(trial_dir: str | Path) -> HarborTrialRecord:
        p = Path(trial_dir)
        lock_path = p / "lock.json"
        result_path = p / "result.json"
        manifest_path = p / "artifacts" / "manifest.json"
        lock = json.loads(lock_path.read_text()) if lock_path.exists() else {}
        result = json.loads(result_path.read_text()) if result_path.exists() else {}
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
        reward, dims = _extract_reward(result)
        source = lock.get("source_trial") or (json.loads((p / "config.json").read_text()).get("source_trial") if (p / "config.json").exists() else None)
        trial_id = str(result.get("trial_id") or lock.get("trial_id") or p.name)
        return HarborTrialRecord(
            trial_dir=str(p), trial_id=trial_id, reward=reward, reward_dimensions=dims,
            lock=lock, result=result, artifact_manifest=manifest, source_trial=source,
            lock_digest=sha256_file(lock_path) if lock_path.exists() else "",
            result_digest=sha256_file(result_path) if result_path.exists() else "",
        )

    @staticmethod
    def trials(job_dir: str | Path) -> list[HarborTrialRecord]:
        p = Path(job_dir)
        result_files = sorted(x for x in p.rglob("result.json") if x.parent != p)
        return [HarborJobParser.parse_trial(x.parent) for x in result_files]


class HarborCLI:
    """CLI adapter only; intentionally does not wrap Harbor's internal Python API."""
    def __init__(self, executable: str = "harbor"):
        self.executable = executable

    def available(self) -> bool:
        return shutil.which(self.executable) is not None

    def run_command(self, task_path: str, *, agent: str = "nop", model: str = "", env: str = "docker") -> list[str]:
        cmd = [self.executable, "run", "-p", task_path, "-a", agent]
        if model:
            cmd += ["-m", model]
        if env:
            cmd += ["--env", env]
        return cmd

    def regrade_command(self, source_job: str, task_path: str, *, env: str = "docker") -> list[str]:
        return [self.executable, "job", "regrade", source_job, "-p", task_path, "-e", env]

    def run(self, task_path: str, *, cwd: str, agent: str = "nop", model: str = "", env: str = "docker", timeout: int = 900) -> subprocess.CompletedProcess:
        return subprocess.run(self.run_command(task_path, agent=agent, model=model, env=env), cwd=cwd, text=True, capture_output=True, timeout=timeout)

    def regrade(self, source_job: str, task_path: str, *, cwd: str, env: str = "docker", timeout: int = 900) -> subprocess.CompletedProcess:
        return subprocess.run(self.regrade_command(source_job, task_path, env=env), cwd=cwd, text=True, capture_output=True, timeout=timeout)


class MockHarbor:
    """Creates Harbor-shaped trial evidence without Docker/Harbor.

    This is not a Harbor emulator. It is deliberately tiny and exists to test
    Moltwork's parsing, binding, regrade matrix and graph projection quickly.
    """
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def run_artifact(self, source_workspace: str | Path, scorer: Callable[[Path], dict[str, float]], *, task_digest: str = "mock-task-v0") -> Path:
        job = self.root / f"job-{int(time.time()*1000)}-{uuid.uuid4().hex[:6]}"
        trial = job / f"artifact__{uuid.uuid4().hex[:7]}"
        artifact_dst = trial / "artifacts" / "app" / "workspace"
        artifact_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_workspace, artifact_dst)
        manifest = [{"source": "/app/workspace", "destination": "artifacts/app/workspace", "type": "directory", "status": "ok", "service": None}]
        (trial / "artifacts" / "manifest.json").write_text(json.dumps(manifest, indent=2))
        scores = scorer(artifact_dst)
        reward = sum(scores.values()) / len(scores) if scores else 0.0
        lock = {"trial_id": trial.name, "task": {"name": "mock/artifact", "content_digest": task_digest}, "agent": {"name": "nop"}, "verifier": {"environment_mode": "separate"}}
        result = {"trial_id": trial.name, "reward": {**scores, "reward": reward}, "agent": {"name": "nop"}, "cost_usd": 0.0}
        (trial / "lock.json").write_text(json.dumps(lock, indent=2))
        (trial / "config.json").write_text(json.dumps({}, indent=2))
        (trial / "result.json").write_text(json.dumps(result, indent=2))
        (trial / "verifier").mkdir()
        (trial / "verifier" / "reward.json").write_text(json.dumps({**scores, "reward": reward}, indent=2))
        return job

    def regrade(self, source_job: str | Path, scorer: Callable[[Path], dict[str, float]], *, assessor_version: str) -> Path:
        src_trials = HarborJobParser.trials(source_job)
        out = self.root / f"regrade-{assessor_version}-{uuid.uuid4().hex[:6]}"
        for src in src_trials:
            src_dir = Path(src.trial_dir)
            trial = out / f"{src_dir.name}__regrade"
            shutil.copytree(src_dir / "artifacts", trial / "artifacts")
            workspace = trial / "artifacts" / "app" / "workspace"
            scores = scorer(workspace)
            reward = sum(scores.values()) / len(scores) if scores else 0.0
            lock = dict(src.lock)
            lock["source_trial"] = {"action": "regrade", "type": "local", "path": str(src_dir), "task": src.lock.get("task", {})}
            lock["verifier"] = {"environment_mode": "separate", "assessor_version": assessor_version}
            result = dict(src.result)
            result["reward"] = {**scores, "reward": reward}
            (trial / "lock.json").parent.mkdir(parents=True, exist_ok=True)
            (trial / "lock.json").write_text(json.dumps(lock, indent=2))
            (trial / "config.json").write_text(json.dumps({"source_trial": lock["source_trial"]}, indent=2))
            (trial / "result.json").write_text(json.dumps(result, indent=2))
            (trial / "verifier").mkdir()
            (trial / "verifier" / "reward.json").write_text(json.dumps({**scores, "reward": reward}, indent=2))
        return out
