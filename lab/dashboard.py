"""Fleet dashboard — lineage, attribution, specializations."""
from __future__ import annotations

import json
import time
from pathlib import Path


def fleet_dashboard(fleet, hydra) -> dict:
    """Generate dashboard data for the entire fleet."""
    summary = hydra.lab_summary()
    workers = []
    for wid, w in fleet.workers.items():
        runs = hydra.get_runs(agent_id=wid)
        won = [r for r in runs if r["outcome"] == "won"]
        workers.append({
            "agent_id": wid,
            "role": w.role,
            "template": w.template,
            "age_days": round((time.time() - w.created_at) / 86400, 1),
            "jobs": len(runs),
            "verified_successes": len(won),
            "win_rate": len(won) / len(runs) if runs else 0,
            "personal_runs": w.personal_runs,
            "lineage": w.lineage,
            "specializations": _specializations(hydra, wid),
        })

    return {
        "lab": summary,
        "workers": workers,
        "insights": [dict(r) for r in hydra._conn().execute("SELECT * FROM lab_insights").fetchall()] if _has_insights(hydra) else [],
        "generated_at": time.time(),
    }


def _specializations(hydra, agent_id: str) -> list[dict]:
    # Simple: group by skill from runs
    corr = hydra.skill_win_correlation()
    return [{"skill": c["skill"], "score": round(c["win_rate"], 2)} for c in corr[:3]]


def _has_insights(hydra) -> bool:
    try:
        hydra._conn().execute("SELECT 1 FROM lab_insights LIMIT 1").fetchone()
        return True
    except Exception:
        return False


def dashboard_html(data: dict) -> str:
    rows = "\n".join(
        f"<tr><td>{w['agent_id']}</td><td>{w['role']}</td><td>{w['jobs']}</td><td>{w['verified_successes']}</td><td>{w['win_rate']:.0%}</td><td>{w['age_days']}d</td></tr>"
        for w in data["workers"]
    )
    lab = data["lab"]
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Moltwork Lab</title>
<style>body{{font-family:system-ui;padding:24px}}table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:6px 10px}}th{{background:#f5f5f5}}</style>
</head><body>
<h1>Moltwork Lab — Fleet Dashboard</h1>
<p>Lab: {lab['total_runs']} runs, {lab['won']} won ({lab['win_rate']:.0%}), net ${lab['net']:.2f} — {lab['agents']} agents, {lab['insights']} insights</p>
<table><tr><th>Agent</th><th>Role</th><th>Jobs</th><th>Verified</th><th>Win</th><th>Age</th></tr>{rows}</table>
<p><small>Generated {data['generated_at']:.0f}</small></p>
</body></html>"""
