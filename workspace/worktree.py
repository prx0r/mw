"""Worktree — per-run workspace with Letta session context.

Each run gets its own worktree. Letta gets a new session within it.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from workspace.git import GitWorkspaceManager


@dataclass
class RunWorkspace:
    """A workspace for a single run."""
    run_id: str = ""
    worktree_path: str = ""
    branch: str = ""
    letta_agent_id: str = ""
    letta_session_id: str = ""
    cwd: str = ""

    # Letta session config
    allowed_tools: list[str] = field(default_factory=lambda: [
        "Read", "LS", "Glob", "Grep", "Write", "Edit",
    ])
    permission_mode: str = "standard"

    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "worktree_path": self.worktree_path,
            "branch": self.branch,
            "letta_agent_id": self.letta_agent_id,
            "letta_session_id": self.letta_session_id,
            "cwd": self.cwd,
            "allowed_tools": self.allowed_tools,
        }


class WorkspaceManager:
    """Manage workspaces for runs.

    Creates worktree + Letta session config for each run.
    """

    def __init__(self, git_manager: GitWorkspaceManager, data_dir: str = ".moltwork"):
        self.git = git_manager
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._workspaces: dict[str, RunWorkspace] = {}

    def create_workspace(self, run_id: str, letta_agent_id: str = "",
                         branch: str = "", tools: list[str] | None = None) -> RunWorkspace:
        """Create a workspace for a run."""
        # Create worktree
        wt_info = self.git.create_worktree(run_id, branch)

        # Create workspace
        ws = RunWorkspace(
            run_id=run_id,
            worktree_path=wt_info.path,
            branch=wt_info.branch,
            letta_agent_id=letta_agent_id,
            cwd=wt_info.path,
            allowed_tools=tools or ["Read", "LS", "Glob", "Grep", "Write", "Edit"],
        )

        # Save workspace config
        ws_path = self.data_dir / "workspaces" / f"{run_id}.json"
        ws_path.parent.mkdir(parents=True, exist_ok=True)
        ws_path.write_text(json.dumps(ws.to_dict(), indent=2))

        self._workspaces[run_id] = ws
        return ws

    def get_workspace(self, run_id: str) -> RunWorkspace | None:
        if run_id in self._workspaces:
            return self._workspaces[run_id]
        # Try loading from disk
        ws_path = self.data_dir / "workspaces" / f"{run_id}.json"
        if ws_path.exists():
            data = json.loads(ws_path.read_text())
            ws = RunWorkspace(**data)
            self._workspaces[run_id] = ws
            return ws
        return None

    def close_workspace(self, run_id: str) -> bool:
        """Close a workspace (commit + cleanup)."""
        ws = self.get_workspace(run_id)
        if not ws:
            return False

        # Commit any changes
        self.git.commit_all(f"run: {run_id} completed", ws.worktree_path)

        # Record final HEAD
        status = self.git.get_status(ws.worktree_path)

        return True

    def destroy_workspace(self, run_id: str) -> bool:
        """Destroy a workspace (remove worktree)."""
        ws = self.get_workspace(run_id)
        if not ws:
            return False
        self.git.remove_worktree(run_id)
        self._workspaces.pop(run_id, None)
        # Remove config file
        ws_path = self.data_dir / "workspaces" / f"{run_id}.json"
        if ws_path.exists():
            ws_path.unlink()
        return True
