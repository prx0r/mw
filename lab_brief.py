"""Lab brief builder — query Hydra for evidence from prior campaigns.

This is what makes C003 start smarter than C001.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CAMPAIGNS_DIR = Path("/root/lab-campaigns")


def build_lab_brief(current_campaign_id: str) -> dict[str, Any]:
    """Build a lab brief from all completed campaigns."""
    brief = {
        "current_campaign": current_campaign_id,
        "prior_campaigns": [],
        "lessons_learned": [],
        "strong_evidence": [],
        "weak_evidence": [],
        "known_failures": [],
    }

    if not CAMPAIGNS_DIR.exists():
        return brief

    for d in sorted(CAMPAIGNS_DIR.iterdir()):
        if d.name == current_campaign_id:
            continue
        if not (d / "campaign.json").exists():
            continue

        data = json.loads((d / "campaign.json").read_text())
        status = data.get("status", "unknown")
        outcome = data.get("outcome")
        runs = data.get("runs", [])

        brief["prior_campaigns"].append({
            "campaign_id": d.name,
            "status": status,
            "outcome": outcome,
            "runs": len(runs),
        })

        # Extract lessons from submissions
        submission_dir = d / "submission"
        if submission_dir.exists():
            for f in submission_dir.glob("*.md"):
                content = f.read_text()
                if "learned" in content.lower():
                    brief["lessons_learned"].append({
                        "campaign": d.name,
                        "source": f.name,
                        "snippet": content[:200],
                    })

        # Extract from outcome
        if outcome:
            if outcome.get("won") is False:
                brief["known_failures"].append({
                    "campaign": d.name,
                    "reason": outcome.get("feedback", "unknown"),
                })
            elif outcome.get("won") is True:
                brief["strong_evidence"].append({
                    "campaign": d.name,
                    "what_worked": outcome.get("feedback", "unknown"),
                })

    return brief


def format_brief_for_worker(brief: dict) -> str:
    """Format a lab brief as markdown for the worker."""
    lines = ["# Lab Brief", ""]

    if brief["prior_campaigns"]:
        lines.append("## Prior Campaigns")
        for pc in brief["prior_campaigns"]:
            lines.append(f"- {pc['campaign_id']}: {pc['status']} (runs: {pc['runs']})")
        lines.append("")

    if brief["lessons_learned"]:
        lines.append("## Lessons Learned")
        for ll in brief["lessons_learned"]:
            lines.append(f"- [{ll['campaign']}] {ll['snippet'][:100]}...")
        lines.append("")

    if brief["strong_evidence"]:
        lines.append("## Strong Evidence")
        for se in brief["strong_evidence"]:
            lines.append(f"- [{se['campaign']}] {se['what_worked']}")
        lines.append("")

    if brief["known_failures"]:
        lines.append("## Known Failures")
        for kf in brief["known_failures"]:
            lines.append(f"- [{kf['campaign']}] {kf['reason']}")
        lines.append("")

    if not any([brief["prior_campaigns"], brief["lessons_learned"],
                brief["strong_evidence"], brief["known_failures"]]):
        lines.append("_No prior evidence available. This is the first campaign._")
        lines.append("")

    return "\n".join(lines)
