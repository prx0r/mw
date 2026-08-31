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

    evaluations = data.get("evaluations", [])
    if not evaluations:
        return {"error": "no prior evaluation to regrade"}

    original = evaluations[-1]
    submission_dir = c_dir / "submission"
    score = 0.0
    checks = {}

    if new_assessor_version == "v1":
        # v1: checks topic coverage + process + learning
        readme = submission_dir / "README.md"
        if readme.exists():
            content = readme.read_text().lower()
            checks["topic_coverage"] = any(s in content for s in ["x402", "mcp", "error", "payment", "agent", "ideas", "classification"])
            score += 0.3 if checks["topic_coverage"] else 0.0

        sub = submission_dir / "submission.md"
        if sub.exists():
            content = sub.read_text().lower()
            checks["has_process"] = "process" in content or "approach" in content
            score += 0.2 if checks["has_process"] else 0.0

            checks["demonstrates_learning"] = any(w in content for w in [
                "requirement", "learned", "lesson", "applied", "first",
                "extracted", "validation", "error case", "prior",
            ])
            score += 0.5 if checks["demonstrates_learning"] else 0.0

    elif new_assessor_version == "v2":
        # v2: uses OUTCOME data — calibration + learning + rank correlation
        outcome = data.get("outcome", {})
        actual_rank = outcome.get("rank", 3)
        actual_won = outcome.get("won", False)

        # Did v0 predict reality?
        v0_score = original.get("score", 0.0)
        v0_correct = (v0_score > 0.5) == actual_won
        checks["v0_calibration"] = v0_correct
        score += 0.4 if v0_correct else 0.0

        # Does submission demonstrate learning?
        sub = submission_dir / "submission.md"
        if sub.exists():
            content = sub.read_text().lower()
            checks["applies_prior"] = any(w in content for w in [
                "requirement", "first", "applied", "prior", "extracted", "validation",
            ])
            score += 0.3 if checks["applies_prior"] else 0.0

        # Rank correlation: higher score = better rank
        rank_score = max(0, 1.0 - (actual_rank - 1) / 10.0)
        checks["rank_correlation"] = round(rank_score, 2)
        score += 0.3 * rank_score

    else:
        # Unknown version: passthrough
        score = original.get("score", 0.0)

    new_eval = {
        "assessor_version": new_assessor_version,
        "timestamp": time.time(),
        "regrade_of": original.get("assessor_version", "unknown"),
        "checks": checks,
        "score": round(min(1.0, score), 3),
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
        "delta": round(new_eval["score"] - original.get("score", 0.0), 3),
        "checks": new_eval.get("checks", {}),
    }


def compare_assessors(campaign_ids: list[str], assessor_a: str, assessor_b: str) -> dict:
    """Compare two assessors across multiple campaigns."""
    results_a = []
    results_b = []

    for cid in campaign_ids:
        c_dir = CAMPAIGNS_DIR / cid
        if not (c_dir / "campaign.json").exists():
            continue
        data = json.loads((c_dir / "campaign.json").read_text())
        for ev in data.get("evaluations", []):
            if ev.get("assessor_version") == assessor_a:
                results_a.append({"campaign": cid, "score": ev["score"]})
            if ev.get("assessor_version") == assessor_b:
                results_b.append({"campaign": cid, "score": ev["score"]})

    mean_a = sum(r["score"] for r in results_a) / max(len(results_a), 1)
    mean_b = sum(r["score"] for r in results_b) / max(len(results_b), 1)

    return {
        "assessor_a": {"version": assessor_a, "mean_score": round(mean_a, 3), "n": len(results_a)},
        "assessor_b": {"version": assessor_b, "mean_score": round(mean_b, 3), "n": len(results_b)},
        "delta": round(mean_b - mean_a, 3),
        "winner": assessor_b if mean_b > mean_a else assessor_a,
    }
