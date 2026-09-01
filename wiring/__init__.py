"""Wiring — connects all frameworks to WorkerKit."""
from __future__ import annotations

from .harbor import HarborWiring
from .git import GitWiring
from .mimo import MiMoWiring
from .trace2skill import Trace2SkillWiring


class Wiring:
    """Central wiring hub — connects all frameworks."""

    def __init__(self):
        self.harbor = HarborWiring()
        self.git = GitWiring()
        self.mimo = MiMoWiring()
        self.trace2skill = Trace2SkillWiring()

    def status(self) -> dict:
        return {
            "harbor": self.harbor.available(),
            "git": True,
            "mimo": True,
            "trace2skill": self.trace2skill.available,
        }

    def full_cycle(self, campaign_id: str, workspace: str, task: str, runtime: str = "direct"):
        """Full wiring cycle: Harbor → Git → skill proposal."""
        # 1. Generate Harbor task
        harbor_task = self.harbor.generate_task(workspace, f"/tmp/harbor-tasks/{campaign_id}")

        # 2. Commit to Git
        git_commit = self.git.commit_artifacts(campaign_id, f"campaign {campaign_id}")

        # 3. Tree digest
        digest = self.git.tree_digest(workspace)

        return {
            "campaign_id": campaign_id,
            "harbor_task": str(harbor_task),
            "git_commit": git_commit,
            "tree_digest": digest,
        }
