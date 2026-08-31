"""GitHubVenue — GitHub bounties as a venue.

GitHub issues with bounty labels are work opportunities.
This adapter normalizes them into the WorkVenue interface.
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from typing import Any

from .base import Opportunity, SubmissionRef, Outcome, Settlement


class GitHubVenue:
    """GitHub bounty venue. Discovers bounty-labeled issues."""

    def __init__(self, token: str = ""):
        self.venue_id = "github"
        self.token = token

    def discover(self) -> list[Opportunity]:
        """Find GitHub issues with bounty labels."""
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Moltwork"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        try:
            req = urllib.request.Request(
                "https://api.github.com/search/issues?q=label:bounty+is:open+is:issue&per_page=50",
                headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return [self._norm_issue(i) for i in data.get("items", [])]
        except:
            return []

    def inspect(self, opportunity_id: str) -> Opportunity | None:
        """Inspect a specific GitHub issue."""
        # opportunity_id format: gh:<number>
        parts = opportunity_id.split(":")
        if len(parts) < 2:
            return None
        try:
            headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Moltwork"}
            if self.token:
                headers["Authorization"] = f"token {self.token}"
            # Search by number
            req = urllib.request.Request(
                f"https://api.github.com/search/issues?q=repo:{parts[0]}+is:issue+number:{parts[1]}",
                headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                items = data.get("items", [])
                if items:
                    return self._norm_issue(items[0])
        except:
            pass
        return None

    def submit(self, opportunity_id: str, artifact_hash: str = "",
               artifact_content: bytes = b"") -> SubmissionRef | None:
        """Submit to GitHub (typically via PR or comment).

        In practice, the agent creates a PR referencing the issue.
        """
        return SubmissionRef(
            submission_id=f"gh-sub:{opportunity_id}",
            venue=self.venue_id,
            opportunity_id=opportunity_id,
            artifact_hash=artifact_hash,
            status="submitted",
        )

    def status(self, submission_id: str) -> Outcome | None:
        """Check if the PR was merged / bounty paid."""
        return Outcome(submission_id=submission_id, status="pending")

    def settle(self, submission_id: str) -> Settlement | None:
        """GitHub bounties are paid externally."""
        return Settlement(
            submission_id=submission_id,
            method="external",
        )

    def _norm_issue(self, issue: dict) -> Opportunity:
        """Normalize a GitHub issue to Opportunity."""
        text = f"{issue.get('title', '')} {issue.get('body', '')[:500]}"
        amt = 0
        for pattern in [r'\$(\d+(?:,\d{3})*)\b', r'Bounty:\s*\$(\d+)']:
            m = re.search(pattern, text)
            if m:
                try:
                    amt = float(m.group(1).replace(",", ""))
                except:
                    pass
                break

        labels = [l.get("name", "") for l in issue.get("labels", [])]

        return Opportunity(
            id=f"gh:{issue.get('html_url', '').split('/')[-1]}",
            venue=self.venue_id,
            title=issue.get("title", ""),
            description=(issue.get("body") or "")[:200],
            task_family="software.backend",  # default for GitHub bounties
            capabilities=[],  # would need NLP to extract
            reward_usd=amt,
            currency="USD",
            source_url=issue.get("html_url", ""),
            metadata={"labels": labels, "repo": issue.get("repository_url", "").split("/")[-2:]},
        )
