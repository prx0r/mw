"""Git wiring — commit artifacts, track versions."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any


class GitWiring:
    """Wire Git to WorkerKit."""

    def __init__(self, repo_path: str = "/root/lab-campaigns"):
        self.repo_path = Path(repo_path)

    def ensure_repo(self):
        if not (self.repo_path / ".git").exists():
            subprocess.run(["git", "init"], cwd=self.repo_path, capture_output=True)

    def commit_artifacts(self, campaign_id: str, message: str = "") -> str:
        """Commit campaign artifacts to Git."""
        self.ensure_repo()
        campaign_dir = self.repo_path / campaign_id
        if not campaign_dir.exists():
            return ""

        subprocess.run(["git", "add", str(campaign_dir)], cwd=self.repo_path, capture_output=True)
        msg = message or f"campaign: {campaign_id} artifacts"
        result = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=self.repo_path, capture_output=True, text=True,
        )

        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path, capture_output=True, text=True,
        )
        return hash_result.stdout.strip() if hash_result.returncode == 0 else ""

    def tree_digest(self, path: str) -> str:
        """Compute SHA-256 digest of a directory tree."""
        h = hashlib.sha256()
        for p in sorted(Path(path).rglob("*")):
            if p.is_file():
                h.update(p.relative_to(path).as_posix().encode())
                h.update(b"\0")
                h.update(hashlib.sha256(p.read_bytes()).digest())
                h.update(b"\0")
        return h.hexdigest()

    def file_digest(self, path: str) -> str:
        """Compute SHA-256 of a file."""
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
