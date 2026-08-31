from __future__ import annotations
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AssessorSpec:
    assessor_id: str = "technical-submission"
    version: str = "v0"
    judge: str = "anthropic/claude-sonnet-4-6"
    include_subjective_judge: bool = False
    required_files: list[str] = field(default_factory=lambda: ["submission.md"])
    dimensions: list[str] = field(default_factory=lambda: ["requirements", "technical", "evidence"])


def build_artifact_evaluation_task(source_workspace: str | Path, task_dir: str | Path, spec: AssessorSpec) -> Path:
    """Build a *real Harbor task layout* around an externally produced artifact.

    Bridge-mode checkpoint:
      Letta produces Git workspace -> this task snapshots it -> Harbor `nop`
      evaluates it. The Harbor trial is regradable; the actual worker identity is
      bound separately by WorkerKit/Moltwork.
    """
    src = Path(source_workspace)
    out = Path(task_dir)
    if out.exists():
        shutil.rmtree(out)
    (out / "environment" / "seed" / "workspace").mkdir(parents=True)
    (out / "tests" / "requirements").mkdir(parents=True)
    (out / "tests" / "technical").mkdir(parents=True)
    (out / "tests" / "evidence").mkdir(parents=True)

    for item in src.iterdir():
        if item.name == ".git":
            continue
        dst = out / "environment" / "seed" / "workspace" / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)

    (out / "instruction.md").write_text(
        "# Artifact evaluation wrapper\n\n"
        "The artifact in /app/workspace was produced by an external Moltwork worker. "
        "Do not modify it. This Harbor trial exists to capture reproducible, regradable evaluation evidence.\n"
    )
    (out / "environment" / "Dockerfile").write_text(
        "FROM python:3.12-slim\nWORKDIR /app\nCOPY seed/workspace/ /app/workspace/\nRUN mkdir -p /logs/artifacts\n"
    )
    task_name = f"moltwork/{spec.assessor_id}-{spec.version}".replace("_", "-")
    (out / "task.toml").write_text(
        f'[task]\nname = "{task_name}"\n\n'
        'artifacts = ["/app/workspace"]\n\n'
        '[agent]\ntimeout_sec = 60.0\n\n'
        '[environment]\nbuild_timeout_sec = 600.0\ncpus = 1\nmemory_mb = 2048\nstorage_mb = 4096\n\n'
        '[verifier]\nenvironment_mode = "separate"\ntimeout_sec = 300.0\n'
    )

    # Programmatic criteria use Reward Kit's real public Python API.
    required_py = ["import rewardkit as rk", ""]
    for f in spec.required_files:
        required_py.append(f'rk.file_exists("workspace/{f}", weight=3.0)')
    required_py.append('rk.command_succeeds("test -s /app/workspace/submission.md", isolated=True, weight=2.0)')
    (out / "tests" / "requirements" / "checks.py").write_text("\n".join(required_py) + "\n")

    (out / "tests" / "technical" / "checks.py").write_text(
        "import rewardkit as rk\n\n"
        'rk.file_contains("workspace/submission.md", "Architecture", weight=1.0)\n'
        'rk.file_contains("workspace/submission.md", "Evidence", weight=1.0)\n'
    )
    (out / "tests" / "evidence" / "checks.py").write_text(
        "from pathlib import Path\nfrom rewardkit import criterion\n\n"
        "@criterion\n"
        "def evidence_is_nonempty(workspace: Path) -> bool:\n"
        "    p = workspace / 'workspace' / 'submission.md'\n"
        "    return p.exists() and len(p.read_text().strip()) > 120\n"
    )

    if spec.include_subjective_judge:
        (out / "tests" / "subjective.toml").write_text(
            "[judge]\n"
            f'judge = "{spec.judge}"\n'
            'files = ["/app/workspace/submission.md"]\n\n'
            "[[criterion]]\n"
            'description = "Does the submission provide a technically credible implementation rather than vague claims?"\n'
            'type = "likert"\npoints = 5\nweight = 2.0\n\n'
            "[[criterion]]\n"
            'description = "Does the evidence directly support the claimed implementation?"\n'
            'type = "likert"\npoints = 5\n'
        )

    (out / "tests" / "test.sh").write_text(
        "#!/bin/bash\nset -euo pipefail\n"
        "uvx --with harbor-rewardkit rewardkit /tests\n"
    )
    (out / "tests" / "test.sh").chmod(0o755)

    (out / "ASSESSOR.json").write_text(json.dumps({
        "assessor_id": spec.assessor_id,
        "version": spec.version,
        "bridge_mode": True,
        "note": "Harbor agent identity is nop; bind actual Letta WorkerRun separately.",
    }, indent=2))
    return out
