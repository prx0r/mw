"""O3 Metrics — 6 canonical metric families.

A. Demand
B. Supply
C. Transactions
D. Outcomes
E. Economics
F. Market Efficiency
"""
from __future__ import annotations

import json
import time
from .store import conn


def compute_metrics(window: str = "30d") -> dict:
    """Compute all 6 metric families."""
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))

    c = conn()

    # A. Demand
    demand = _demand_metrics(c, since)

    # B. Supply
    supply = _supply_metrics(c)

    # C. Transactions
    transactions = _transaction_metrics(c, since)

    # D. Outcomes
    outcomes = _outcome_metrics(c, since)

    # E. Economics
    economics = _economics_metrics(c, since)

    # F. Market Efficiency
    efficiency = _efficiency_metrics(c, since)

    c.close()

    return {
        "window": window,
        "demand": demand,
        "supply": supply,
        "transactions": transactions,
        "outcomes": outcomes,
        "economics": economics,
        "efficiency": efficiency,
    }


def _demand_metrics(c, since: str) -> dict:
    rows = c.execute("SELECT src, COUNT(*) as n, SUM(reward) as usd FROM opp WHERE first_seen>=? GROUP BY src", (since,)).fetchall()
    total = sum(r["n"] for r in rows)
    total_usd = sum(r["usd"] or 0 for r in rows)

    # Skill demand
    skill_rows = c.execute("SELECT skills FROM opp WHERE first_seen>=?", (since,)).fetchall()
    skill_counts = {}
    for r in skill_rows:
        for s in json.loads(r["skills"] or "[]"):
            skill_counts[s] = skill_counts.get(s, 0) + 1

    return {
        "open_opportunities": total,
        "advertised_usd": round(total_usd, 2),
        "by_source": {r["src"]: {"n": r["n"], "usd": round(r["usd"] or 0, 2)} for r in rows},
        "top_skills": sorted(skill_counts.items(), key=lambda x: -x[1])[:10],
    }


def _supply_metrics(c) -> dict:
    rows = c.execute("SELECT src, COUNT(*) as n, SUM(calls) as calls FROM svc GROUP BY src").fetchall()
    total = sum(r["n"] for r in rows)
    total_calls = sum(r["calls"] or 0 for r in rows)

    return {
        "total_services": total,
        "total_calls": round(total_calls),
        "by_source": {r["src"]: {"n": r["n"], "calls": round(r["calls"] or 0)} for r in rows},
    }


def _transaction_metrics(c, since: str) -> dict:
    rows = c.execute("SELECT src, COUNT(*) as n FROM opp WHERE first_seen>=? AND reward>0 GROUP BY src", (since,)).fetchall()
    total = sum(r["n"] for r in rows)

    return {
        "opportunities_with_reward": total,
        "by_source": {r["src"]: r["n"] for r in rows},
    }


def _outcome_metrics(c, since: str) -> dict:
    rows = c.execute("SELECT status, COUNT(*) as n FROM opp WHERE first_seen>=? GROUP BY status", (since,)).fetchall()
    return {r["status"]: r["n"] for r in rows}


def _economics_metrics(c, since: str) -> dict:
    rows = c.execute("SELECT reward FROM opp WHERE first_seen>=? AND reward>0", (since,)).fetchall()
    rewards = sorted([r["reward"] for r in rows])
    if not rewards:
        return {"n": 0}

    return {
        "n": len(rewards),
        "total_usd": round(sum(rewards), 2),
        "median": round(rewards[len(rewards)//2], 2),
        "p25": round(rewards[int(len(rewards)*0.25)], 2),
        "p75": round(rewards[int(len(rewards)*0.75)], 2),
        "avg": round(sum(rewards)/len(rewards), 2),
    }


def _efficiency_metrics(c, since: str) -> dict:
    total = c.execute("SELECT COUNT(*) FROM opp WHERE first_seen>=?", (since,)).fetchone()[0]
    open_n = c.execute("SELECT COUNT(*) FROM opp WHERE first_seen>=? AND status='open'", (since,)).fetchone()[0]
    closed_n = c.execute("SELECT COUNT(*) FROM opp WHERE first_seen>=? AND status='closed'", (since,)).fetchone()[0]

    return {
        "total": total,
        "open": open_n,
        "closed": closed_n,
        "open_rate": round(open_n / max(1, total), 4),
        "closed_rate": round(closed_n / max(1, total), 4),
    }
