"""Regrade — run a new assessor over existing campaigns without re-running workers.

This is Harbor's killer feature applied to our Lab.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

CAMPAIGNS_DIR = Path("/root/lab-campaigns")


def regrade(campaign_id: str, new_assessor_version: str) -> dict:
    """Re-grade a campaign with a new assessor version. No worker re-run."""
    c_dir = CAMPAIGNS_DIR / campaign_id
    data = json.loads((c_dir / "campaign.json").read_text())

    # Find the original grade
    evaluations = data.get("evaluations", [])
    if not evaluations:
        return {"error": "no prior evaluation to regrade"}

    original = evaluations[-1]

    # v1 assessor: checks for sponsor depth (not just file existence)
    if new_assessor_version == "v1":
        submission_dir = c_dir / "submission"
        score = 0.0
        checks = {}

        # Check README mentions sponsor
        readme = submission_dir / "README.md"
        if readme.exists():
            content = readme.read_text().lower()
            has_sponsor = any(s in content for s in ["hedera", "phala", "graph", "the graph"])
            checks["sponsor_in_readme"] = has_sponsor
            score += 0.3 if has_sponsor else 0.0

        # Check submission.md has technical depth
        sub = submission_dir / "submission.md"
        if sub.exists():
            content = sub.read_text().lower()
            has_technical = "technical" in content or "api" in content or "protocol" in content
            checks["technical_depth"] = has_technical
            score += 0.3 if has_technical else 0.0

            has_learning = "learned" in content or "changed from" in content or "from c00" in content
            checks["demonstrates_learning"] = has_learning
            score += 0.4 if has_learning else 0.0

        # Check src/ exists
        has_src = (submission_dir / "src").exists() and any((submission_dir / "src").iterdir()) if (submission_dir / "src").exists() else False
        checks["has_source"] = has_src
        score += 0.0  # bonus, not required yet

        new_eval = {
            "assessor_version": new_assessor_version,
            "timestamp": time.time(),
            "regrade_of": original.get("assessor_version", "unknown"),
            "checks": checks,
            "score": min(1.0, score),
        }
    else:
        new_eval = {
            "assessor_version": new_assessor_version,
            "timestamp": time.time(),
            "regrade_of": original.get("assessor_version", "unknown"),
            "score": original.get("score", 0.0),
        }

    evaluations.append(new_eval)
    data["evaluations"] = evaluations
    (c_dir / "campaign.json").write_text(json.dumps(data, indent=2))

    return {
        "campaign_id": campaign_id,
        "original": original.get("assessor_version"),
        "regraded_with": new_assessor_version,
        "original_score": original.get("score"),
        "new_score": new_eval["score"],
        "delta": new_eval["score"] - original.get("score", 0.0),
        "checks": new_eval.get("checks", {}),
    }


def compare_assessors(campaign_ids: list[str], assessor_a: str, assessor_b: str) -> dict:
    """Compare two assessors across multiple campaigns."""
    results_a = []
    results_b = []

    for cid in campaign_ids:
        c_dir = CAMPAIGNS_DIR / cid
        data = json.loads((c_dir / "campaign.json").read_text())
        for ev in data.get("evaluations", []):
            if ev.get("assessor_version") == assessor_a:
                results_a.append({"campaign": cid, "score": ev["score"]})
            if ev.get("assessor_version") == assessor_b:
                results_b.append({"campaign": cid, "score": ev["score"]})

    mean_a = sum(r["score"] for r in results_a) / max(len(results_a), 1)
    mean_b = sum(r["score"] for r in results_b) / max(len(results_b), 1)

    return {
        "assessor_a": {"version": assessor_a, "mean_score": mean_a, "n": len(results_a)},
        "assessor_b": {"version": assessor_b, "mean_score": mean_b, "n": len(results_b)},
        "delta": mean_b - mean_a,
        "winner": assessor_b if mean_b > mean_a else assessor_a,
    }
