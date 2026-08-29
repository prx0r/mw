"""Hydra — Lab intelligence graph.

Immutable truth: Agent → Run → Opportunity/Model/Tools/Skills/Cost/Duration/Artifact/Evaluation/Outcome + MemoryRevision

This is the authoritative store. Letta memory is derived, not primary.
Lab queries: which skills correlate with wins? which model is most profitable?
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS lab_agents (
    agent_id TEXT PRIMARY KEY,
    template TEXT,
    lineage TEXT,  -- JSON array of parent version hashes
    lab_id TEXT,
    data TEXT,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_runs (
    run_id TEXT PRIMARY KEY,
    agent_id TEXT,
    opportunity_id TEXT,
    model TEXT,
    tools TEXT,  -- JSON array
    skills TEXT, -- JSON array
    cost_usd REAL,
    duration_s REAL,
    artifact_hash TEXT,
    evaluation_score REAL,
    outcome TEXT,  -- won/lost/pending
    reward_usd REAL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_memory_revisions (
    revision_id TEXT PRIMARY KEY,
    agent_id TEXT,
    commit_hash TEXT,
    change_type TEXT,  -- memory/skill/mod
    content TEXT,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_insights (
    insight_id TEXT PRIMARY KEY,
    title TEXT,
    body TEXT,
    evidence_runs INTEGER,
    confidence REAL,
    created_at REAL
);
"""


class HydraStore:
    """SQLite-backed lab intelligence. One instance per lab."""

    def __init__(self, db_path: str = "data/hydra.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()

    def _conn(self):
        c = sqlite3.connect(str(self.db_path))
        c.row_factory = sqlite3.Row
        return c

    # ─── Agents ───────────────────────────────────────────────────────

    def upsert_agent(self, agent_id: str, template: str, lineage: list[str] | None = None, lab_id: str = "default", data: dict | None = None):
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO lab_agents (agent_id, template, lineage, lab_id, data, created_at) VALUES (?,?,?,?,?,?)",
            (agent_id, template, json.dumps(lineage or []), lab_id, json.dumps(data or {}), time.time()),
        )
        conn.commit()
        conn.close()

    def get_agent(self, agent_id: str) -> dict | None:
        conn = self._conn()
        row = conn.execute("SELECT * FROM lab_agents WHERE agent_id=?", (agent_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    # ─── Runs — the core immutable record ─────────────────────────────

    def record_run(self, run_id: str, agent_id: str, opportunity_id: str = "", model: str = "",
                   tools: list[str] | None = None, skills: list[str] | None = None,
                   cost_usd: float = 0, duration_s: float = 0,
                   artifact_hash: str = "", evaluation_score: float = 0,
                   outcome: str = "pending", reward_usd: float = 0):
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO lab_runs (run_id, agent_id, opportunity_id, model, tools, skills, cost_usd, duration_s, artifact_hash, evaluation_score, outcome, reward_usd, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (run_id, agent_id, opportunity_id, model, json.dumps(tools or []), json.dumps(skills or []),
             cost_usd, duration_s, artifact_hash, evaluation_score, outcome, reward_usd, time.time()),
        )
        conn.commit()
        conn.close()

    def get_runs(self, agent_id: str = "", outcome: str = "", limit: int = 100) -> list[dict]:
        conn = self._conn()
        q = "SELECT * FROM lab_runs WHERE 1=1"
        args: list = []
        if agent_id:
            q += " AND agent_id=?"; args.append(agent_id)
        if outcome:
            q += " AND outcome=?"; args.append(outcome)
        q += " ORDER BY created_at DESC LIMIT ?"; args.append(limit)
        rows = conn.execute(q, args).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── Memory revisions ─────────────────────────────────────────────

    def record_memory_revision(self, revision_id: str, agent_id: str, commit_hash: str, change_type: str, content: str = ""):
        conn = self._conn()
        conn.execute("INSERT OR REPLACE INTO lab_memory_revisions VALUES (?,?,?,?,?,?)",
                     (revision_id, agent_id, commit_hash, change_type, content, time.time()))
        conn.commit()
        conn.close()

    # ─── Insights ─────────────────────────────────────────────────────

    def add_insight(self, insight_id: str, title: str, body: str, evidence_runs: int, confidence: float):
        conn = self._conn()
        conn.execute("INSERT OR REPLACE INTO lab_insights VALUES (?,?,?,?,?,?)",
                     (insight_id, title, body, evidence_runs, confidence, time.time()))
        conn.commit()
        conn.close()

    # ─── Lab intelligence queries ─────────────────────────────────────

    def win_rate(self, agent_id: str = "") -> float:
        conn = self._conn()
        q = "SELECT COUNT(*) FROM lab_runs WHERE outcome='won'"
        args: list = []
        if agent_id:
            q += " AND agent_id=?"; args.append(agent_id)
        total = conn.execute(q, args).fetchone()[0]
        q2 = "SELECT COUNT(*) FROM lab_runs WHERE outcome IN ('won','lost')"
        if agent_id:
            q2 += " AND agent_id=?"
        all_done = conn.execute(q2, args).fetchone()[0]
        conn.close()
        return total / all_done if all_done else 0.0

    def profitability_by_model(self) -> list[dict]:
        conn = self._conn()
        rows = conn.execute("""
            SELECT model, COUNT(*) as n, AVG(reward_usd - cost_usd) as avg_profit,
                   AVG(evaluation_score) as avg_score
            FROM lab_runs WHERE outcome IN ('won','lost') GROUP BY model
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def skill_win_correlation(self) -> list[dict]:
        """Which skills correlate with wins? Simple frequency analysis."""
        conn = self._conn()
        rows = conn.execute("SELECT skills, outcome FROM lab_runs WHERE outcome IN ('won','lost')").fetchall()
        conn.close()
        from collections import Counter
        win_skills: Counter = Counter()
        loss_skills: Counter = Counter()
        for r in rows:
            try:
                skills = json.loads(r["skills"])
            except Exception:
                continue
            for s in skills:
                if r["outcome"] == "won":
                    win_skills[s] += 1
                else:
                    loss_skills[s] += 1
        result = []
        for skill in set(list(win_skills.keys()) + list(loss_skills.keys())):
            w = win_skills[skill]
            l = loss_skills[skill]
            total = w + l
            if total >= 3:  # minimum evidence
                result.append({"skill": skill, "wins": w, "losses": l, "win_rate": w / total, "n": total})
        return sorted(result, key=lambda x: x["win_rate"], reverse=True)

    def lab_summary(self) -> dict:
        conn = self._conn()
        total = conn.execute("SELECT COUNT(*) FROM lab_runs").fetchone()[0]
        won = conn.execute("SELECT COUNT(*) FROM lab_runs WHERE outcome='won'").fetchone()[0]
        revenue = conn.execute("SELECT COALESCE(SUM(reward_usd),0) FROM lab_runs WHERE outcome='won'").fetchone()[0]
        cost = conn.execute("SELECT COALESCE(SUM(cost_usd),0) FROM lab_runs").fetchone()[0]
        insights = conn.execute("SELECT COUNT(*) FROM lab_insights").fetchone()[0]
        agents = conn.execute("SELECT COUNT(*) FROM lab_agents").fetchone()[0]
        conn.close()
        return {"total_runs": total, "won": won, "win_rate": won / total if total else 0,
                "revenue": revenue, "cost": cost, "net": revenue - cost,
                "insights": insights, "agents": agents}

    def stats(self) -> dict:
        return self.lab_summary()
