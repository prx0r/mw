"""Harbor integration — real CLI wrapper + trial parser."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


class HarborWiring:
    """Wire Harbor CLI to WorkerKit."""

    def __init__(self, harbor_bin: str = "harbor"):
        self.harbor_bin = harbor_bin
        self.vendor_path = Path("/root/workerkit/vendor/harbor")

    def available(self) -> bool:
        return shutil.which(self.harbor_bin) is not None or self.vendor_path.exists()

    def generate_task(self, workspace: str, output_dir: str, task_name: str = "moltwork-task") -> Path:
        """Generate a Harbor task from a workspace."""
        out = Path(output_dir) / task_name
        out.mkdir(parents=True, exist_ok=True)

        # Copy workspace as artifact
        artifact_dir = out / "artifacts" / "app" / "workspace"
        artifact_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(workspace, artifact_dir, dirs_exist_ok=True)

        # Generate task.toml
        (out / "task.toml").write_text(f"""[task]
id = "{task_name}"
name = "{task_name}"
version = "1"

[environment]
mode = "local"

[verifier]
mode = "separate"
""")

        # Generate instruction.md
        (out / "instruction.md").write_text(f"# {task_name}\n\nEvaluate the submitted workspace.\n")

        # Generate test script
        tests_dir = out / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "test.sh").write_text("""#!/bin/bash
# Deterministic checks
if [ -f /app/workspace/submission.md ]; then
    echo "PASS: submission exists"
    exit 0
else
    echo "FAIL: no submission"
    exit 1
fi
""")

        # Generate manifest
        manifest = [{"source": "/app/workspace", "destination": "artifacts/app/workspace", "type": "directory"}]
        (out / "artifacts" / "manifest.json").write_text(json.dumps(manifest, indent=2))

        return out

    def run_task(self, task_path: str, agent: str = "nop", env: str = "local") -> dict:
        """Run a Harbor task."""
        cmd = [self.harbor_bin, "run", "-p", task_path, "-a", agent, "--env", env]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return {"ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
        except FileNotFoundError:
            return {"ok": False, "error": "harbor CLI not found"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout"}

    def regrade(self, source_job: str, task_path: str, env: str = "local") -> dict:
        """Regrade a Harbor job with a new verifier."""
        cmd = [self.harbor_bin, "job", "regrade", source_job, "-p", task_path, "-e", env]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return {"ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
        except FileNotFoundError:
            return {"ok": False, "error": "harbor CLI not found"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout"}

    def parse_trial(self, trial_dir: str) -> dict:
        """Parse a Harbor trial directory."""
        p = Path(trial_dir)
        lock = json.loads((p / "lock.json").read_text()) if (p / "lock.json").exists() else {}
        result = json.loads((p / "result.json").read_text()) if (p / "result.json").exists() else {}
        manifest = json.loads((p / "artifacts" / "manifest.json").read_text()) if (p / "artifacts" / "manifest.json").exists() else []
        return {"lock": lock, "result": result, "manifest": manifest, "dir": str(p)}
