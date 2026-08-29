"""GitWorkspaceManager — manage Git branches and worktrees for campaigns.

Each Campaign gets a branch. Each WorkUnit gets a worktree.
"""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.hashing import sha256


def _run(cmd: list[str], cwd: str = ".") -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


@dataclass
class WorktreeInfo:
    """Info about a Git worktree."""
    path: str = ""
    branch: str = ""
    head: str = ""
    run_id: str = ""

    def to_dict(self) -> dict:
        return {"path": self.path, "branch": self.branch, "head": self.head, "run_id": self.run_id}


@dataclass
class BranchInfo:
    """Info about a Git branch."""
    name: str = ""
    head: str = ""
    campaign_id: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "head": self.head, "campaign_id": self.campaign_id}


class GitWorkspaceManager:
    """Manage Git workspaces for Moltwork campaigns.

    Conventions:
      campaign branch: mw/opp_<id>/campaign
      work branches:   mw/opp_<id>/<workunit_id>/<attempt>
      experiments:     mw/opp_<id>/experiment/<hypothesis>
      final:           mw/opp_<id>/submission
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self._worktrees: dict[str, WorktreeInfo] = {}

    def _git(self, *args: str) -> tuple[int, str, str]:
        return _run(["git"] + list(args), cwd=str(self.repo_path))

    def ensure_repo(self) -> bool:
        """Check if this is a Git repo."""
        code, out, err = self._git("rev-parse", "--git-dir")
        return code == 0

    def current_head(self) -> str:
        code, out, _ = self._git("rev-parse", "HEAD")
        return out if code == 0 else ""

    def campaign_branch(self, opportunity_id: str) -> str:
        """Generate campaign branch name."""
        safe_id = opportunity_id.replace("/", "-").replace(" ", "-").lower()
        return f"mw/opp_{safe_id}/campaign"

    def work_branch(self, opportunity_id: str, work_unit_id: str, attempt: int = 1) -> str:
        """Generate work branch name."""
        safe_opp = opportunity_id.replace("/", "-").replace(" ", "-").lower()
        safe_wu = work_unit_id.replace("/", "-").replace(" ", "-").lower()
        return f"mw/opp_{safe_opp}/{safe_wu}/{attempt}"

    def create_campaign_branch(self, opportunity_id: str) -> str:
        """Create a campaign branch from HEAD."""
        branch = self.campaign_branch(opportunity_id)
        code, _, err = self._git("branch", branch)
        if code != 0:
            # Branch might exist, try checkout
            self._git("checkout", "-B", branch)
        else:
            self._git("checkout", branch)
        return branch

    def create_worktree(self, run_id: str, branch: str = "") -> WorktreeInfo:
        """Create a worktree for a run."""
        worktree_path = self.repo_path / ".moltwork" / "worktrees" / run_id
        worktree_path.mkdir(parents=True, exist_ok=True)

        if not branch:
            branch = f"mw/run/{run_id}"

        # Create branch if it doesn't exist
        self._git("branch", branch)
        # Create worktree
        code, out, err = self._git("worktree", "add", str(worktree_path), branch)

        head = self.current_head()

        info = WorktreeInfo(
            path=str(worktree_path),
            branch=branch,
            head=head,
            run_id=run_id,
        )
        self._worktrees[run_id] = info
        return info

    def remove_worktree(self, run_id: str) -> bool:
        """Remove a worktree."""
        info = self._worktrees.get(run_id)
        if not info:
            return False
        code, _, _ = self._git("worktree", "remove", info.path, "--force")
        self._worktrees.pop(run_id, None)
        return code == 0

    def commit_all(self, message: str, worktree_path: str = "") -> str:
        """Stage all and commit."""
        cwd = worktree_path or str(self.repo_path)
        self._git("add", "-A", cwd=cwd)
        code, out, _ = self._git("commit", "-m", message, cwd=cwd)
        if code == 0:
            # Extract commit hash
            code2, head, _ = _run(["git", "rev-parse", "HEAD"], cwd=cwd)
            return head if code2 == 0 else ""
        return ""

    def get_diff(self, base: str = "HEAD~1", worktree_path: str = "") -> str:
        """Get git diff."""
        cwd = worktree_path or str(self.repo_path)
        code, out, _ = _run(["git", "diff", base], cwd=cwd)
        return out if code == 0 else ""

    def get_status(self, worktree_path: str = "") -> dict:
        """Get git status."""
        cwd = worktree_path or str(self.repo_path)
        code, out, _ = _run(["git", "status", "--porcelain"], cwd=cwd)
        changed = len([l for l in out.split("\n") if l.strip()]) if out else 0
        head = self.current_head()
        return {"head": head, "changed_files": changed, "clean": changed == 0}

    def list_worktrees(self) -> list[WorktreeInfo]:
        """List all Moltwork worktrees."""
        return list(self._worktrees.values())
