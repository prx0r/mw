#!/usr/bin/env python3
"""mwgo init — create a fresh Moltwork Lab.

Creates: Git repo + WorkerKit + Letta agent + MemFS + WorkerManifest + Lab projection
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def run(cmd: list[str], cwd: str = ".") -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"  ERROR: {' '.join(cmd)}: {result.stderr[:200]}")
    return result.stdout.strip()


def init_lab(lab_name: str = "my-lab"):
    """Initialize a new Moltwork Lab."""
    lab_dir = Path.cwd() / lab_name

    print(f"$ mwgo init {lab_name}\n")

    # 1. Preflight
    print("1. Preflight checks...")
    git = run(["git", "--version"])
    if not git:
        print("  ERROR: git not found"); return
    node = run(["node", "--version"])
    if not node:
        print("  WARNING: node not found (needed for Letta runtime)")

    # 2. Create directory
    print(f"2. Creating {lab_name}/...")
    lab_dir.mkdir(parents=True, exist_ok=True)

    # 3. Git init
    print("3. Git init...")
    run(["git", "init"], cwd=str(lab_dir))

    # 4. Write moltwork.toml
    print("4. Writing moltwork.toml...")
    worker_id = f"worker_{int(time.time())}"
    lab_id = f"lab_{int(time.time())}"
    config = f'''schema = "moltwork.lab.v1"

[lab]
id = "{lab_id}"
name = "{lab_name}"

[worker]
id = "{worker_id}"

[runtime]
provider = "letta"
backend = "local"

[workerkit]
ledger = ".moltwork/ledger/workerkit.sqlite"
receipts = ".moltwork/receipts"

[workspace]
provider = "git"
worktrees = ".moltwork/worktrees"

[index]
provider = "sqlite"
fallback = "hydra"
authoritative = false

[learning]
enabled = true
minimum_runs = 5
auto_propose = true
auto_promote = false

[budget]
default_run_usd = 2.00
'''
    (lab_dir / "moltwork.toml").write_text(config)

    # 5. Initialize WorkerKit
    print("5. Initializing WorkerKit...")
    (lab_dir / ".moltwork" / "ledger").mkdir(parents=True, exist_ok=True)
    (lab_dir / ".moltwork" / "receipts").mkdir(parents=True, exist_ok=True)
    (lab_dir / ".moltwork" / "runs").mkdir(parents=True, exist_ok=True)
    (lab_dir / ".moltwork" / "workers").mkdir(parents=True, exist_ok=True)
    (lab_dir / ".moltwork" / "snapshots").mkdir(parents=True, exist_ok=True)
    (lab_dir / ".moltwork" / "learning").mkdir(parents=True, exist_ok=True)
    (lab_dir / ".moltwork" / "learning" / "proposals").mkdir(exist_ok=True)
    (lab_dir / ".moltwork" / "learning" / "experiments").mkdir(exist_ok=True)
    (lab_dir / ".moltwork" / "worktrees").mkdir(exist_ok=True)
    (lab_dir / ".moltwork" / "hydra").mkdir(exist_ok=True)

    # 6. Write worker manifest v1
    print("6. Creating WorkerManifest v1...")
    manifest = {
        "schemaVersion": "moltwork.worker-manifest.v1",
        "workerId": worker_id,
        "versionId": "",
        "parentVersion": "",
        "runtime": {"adapter": "letta-agent-sdk", "backend": "local"},
        "agent": {"provider": "letta", "agentId": "", "afSnapshotDigest": ""},
        "memory": {"memfsCommit": "", "memfsTreeDigest": ""},
        "skills": {"treeDigest": "", "entries": []},
        "model": {"id": "opencode-go/mimo-v2.5", "provider": "opencode-go"},
        "tools": {"policyDigest": "", "schemaDigest": ""},
        "workerkit": {"version": "0.1.0", "evidenceSchema": "moltwork:event:v1"},
        "promotion": {"learningProposal": None, "experimentReceipt": None},
    }
    manifest_path = lab_dir / ".moltwork" / "workers" / worker_id / "current.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))

    # 7. Write lineage
    lineage = {"worker_id": worker_id, "versions": [], "head": ""}
    (lab_dir / ".moltwork" / "workers" / worker_id / "lineage.json").write_text(
        json.dumps(lineage, indent=2)
    )

    # 8. Write .gitignore
    print("7. Writing .gitignore...")
    (lab_dir / ".gitignore").write_text(""".moltwork/ledger/*.sqlite*
.moltwork/worktrees/
.moltwork/runtime/
.moltwork/hydra/*.db*
.moltwork/secrets/
*.pyc
__pycache__/
node_modules/
""")

    # 9. Write AGENTS.md
    print("8. Writing AGENTS.md...")
    (lab_dir / "AGENTS.md").write_text(f"""# {lab_name} — Moltwork Lab

## Quick start

```bash
mwgo work          # start working
mwgo status        # check status
mwgo lab brief     # get lab context
```

## Architecture

- **Worker**: {worker_id}
- **Runtime**: Letta Agent SDK (local)
- **Model**: opencode-go/mimo-v2.5
- **WorkerKit**: events, costs, receipts, verification

## Rules

1. Never pkill — use PID kill
2. Fail fast — 3 attempts max
3. Log everything to .moltwork/
4. Test before claiming
""")

    # 10. Write README.md
    (lab_dir / "README.md").write_text(f"""# {lab_name}

A Moltwork Lab — persistent worker + learning + verified execution.

## Setup

```bash
cd {lab_name}
mwgo work
```

## Architecture

- Worker: {worker_id}
- Runtime: Letta (local backend)
- Model: opencode-go/mimo-v2.5
- Evidence: WorkerKit
- Learning: Lab projection + cg
""")

    # 11. Initial git commit
    print("9. Initial git commit...")
    run(["git", "add", "-A"], cwd=str(lab_dir))
    run(["git", "commit", "-m", f"init: {lab_name} Moltwork Lab"], cwd=str(lab_dir))

    # 12. Summary
    print(f"\n{'='*50}")
    print(f"{lab_name} is ready.")
    print(f"{'='*50}")
    print(f"Worker:     {worker_id}")
    print(f"Lab:        {lab_id}")
    print(f"Runtime:    Letta Agent SDK (local)")
    print(f"Model:      opencode-go/mimo-v2.5")
    print(f"")
    print(f"cd {lab_name}")
    print(f"mwgo work")
    print(f"{'='*50}")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "my-lab"
    init_lab(name)
