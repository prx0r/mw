"""LabProjection — SQLite-backed lab intelligence.

Immutable truth: Agent → Run → Opportunity/Model/Tools/Skills/Cost/Duration/Artifact/Evaluation/Outcome + MemoryRevision

This is a disposable projection over the WorkerKit event ledger.
The event ledger (core/events.py) is canonical. This can be rebuilt.
Lab queries: which skills correlate with wins? which model is most profitable?

Naming: 'LabProjection' because this is SQLite, not HydraDB.
HydraDB is a graph database — this is not that.
When HydraDB integration arrives, add HydraLabProjection alongside SQLiteLabProjection.
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
    lineage TEXT,
    lab_id TEXT,
    data TEXT,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_runs (
    run_id TEXT PRIMARY KEY,
    agent_id TEXT,
    opportunity_id TEXT,
    task_family TEXT,
    model TEXT,
    tools TEXT,
    skills TEXT,
    cost_usd REAL,
    duration_s REAL,
    artifact_hash TEXT,
    evaluation_score REAL,
    outcome TEXT,
    reward_usd REAL,
    worker_version TEXT,
    failure_reason TEXT,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_memory_revisions (
    revision_id TEXT PRIMARY KEY,
    agent_id TEXT,
    commit_hash TEXT,
    change_type TEXT,
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
CREATE TABLE IF NOT EXISTS lab_worker_versions (
    version_id TEXT PRIMARY KEY,
    agent_id TEXT,
    af_hash TEXT,
    memfs_commit TEXT,
    skills_root TEXT,
    mods_root TEXT,
    runtime_version TEXT,
    parent_version TEXT,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_opportunities (
    opportunity_id TEXT PRIMARY KEY,
    title TEXT,
    reward_usd REAL,
    task_family TEXT,
    source TEXT,
    data TEXT,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_submissions (
    submission_id TEXT PRIMARY KEY,
    run_id TEXT,
    agent_id TEXT,
    content_hash TEXT,
    evaluation_score REAL,
    outcome TEXT,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    run_id TEXT,
    submission_id TEXT,
    score REAL,
    gates_passed TEXT,
    reviewer TEXT,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_experiments (
    experiment_id TEXT PRIMARY KEY,
    hypothesis TEXT,
    worker_version TEXT,
    status TEXT,
    data TEXT,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS lab_run_dependencies (
    run_id TEXT PRIMARY KEY,
    worker_version_id TEXT,
    skill_version_ids TEXT,
    briefing_id TEXT,
    process_version_id TEXT,
    memory_revision_id TEXT,
    reviewer_id TEXT,
    context_pack_ids TEXT,
    created_at REAL
);
CREATE INDEX IF NOT EXISTS idx_runs_task_family ON lab_runs(task_family);
CREATE INDEX IF NOT EXISTS idx_runs_agent ON lab_runs(agent_id);
CREATE INDEX IF NOT EXISTS idx_runs_outcome ON lab_runs(outcome);
CREATE INDEX IF NOT EXISTS idx_runs_worker_version ON lab_runs(worker_version);
"""


class LabProjection:
    """SQLite-backed lab intelligence. One instance per lab.

    This is a disposable projection over the WorkerKit event ledger.
    The event ledger is canonical. This can be rebuilt from events.
    """

    def __init__(self, db_path: str = "data/hydra.db", append_only: bool = True):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.append_only = append_only
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

    def _check_append(self, conn, table: str, pk: str, pk_value: str) -> None:
        """If append_only, raise if record already exists."""
        if not self.append_only:
            return
        existing = conn.execute(f"SELECT 1 FROM {table} WHERE {pk}=?", (pk_value,)).fetchone()
        if existing:
            raise ValueError(f"Append-only violation: {table}.{pk}={pk_value} already exists")

    def record_run(self, run_id: str, agent_id: str, opportunity_id: str = "", model: str = "",
                   tools: list[str] | None = None, skills: list[str] | None = None,
                   cost_usd: float = 0, duration_s: float = 0,
                   artifact_hash: str = "", evaluation_score: float = 0,
                   outcome: str = "pending", reward_usd: float = 0, worker_version: str = "",
                   task_family: str = "", failure_reason: str = ""):
        conn = self._conn()
        if self.append_only:
            self._check_append(conn, "lab_runs", "run_id", run_id)
        conn.execute(
            "INSERT OR REPLACE INTO lab_runs (run_id, agent_id, opportunity_id, task_family, model, tools, skills, cost_usd, duration_s, artifact_hash, evaluation_score, outcome, reward_usd, worker_version, failure_reason, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (run_id, agent_id, opportunity_id, task_family, model, json.dumps(tools or []), json.dumps(skills or []),
             cost_usd, duration_s, artifact_hash, evaluation_score, outcome, reward_usd, worker_version, failure_reason, time.time()),
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

    # ─── Worker versions — .af lineage ──────────────────────────────────

    def record_worker_version(self, version_id: str, agent_id: str, af_hash: str = "", memfs_commit: str = "",
                              skills_root: str = "", mods_root: str = "", runtime_version: str = "", parent_version: str = ""):
        conn = self._conn()
        conn.execute("INSERT OR REPLACE INTO lab_worker_versions VALUES (?,?,?,?,?,?,?,?,?)",
                     (version_id, agent_id, af_hash, memfs_commit, skills_root, mods_root, runtime_version, parent_version, time.time()))
        conn.commit()
        conn.close()

    def get_worker_versions(self, agent_id: str) -> list[dict]:
        conn = self._conn()
        rows = conn.execute("SELECT * FROM lab_worker_versions WHERE agent_id=? ORDER BY created_at", (agent_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── Opportunities ──────────────────────────────────────────────────

    def record_opportunity(self, opportunity_id: str, title: str, reward_usd: float = 0, task_family: str = "", source: str = "", data: dict | None = None):
        conn = self._conn()
        conn.execute("INSERT OR REPLACE INTO lab_opportunities VALUES (?,?,?,?,?,?,?)",
                     (opportunity_id, title, reward_usd, task_family, source, json.dumps(data or {}), time.time()))
        conn.commit()
        conn.close()

    # ─── Submissions ────────────────────────────────────────────────────

    def record_submission(self, submission_id: str, run_id: str, agent_id: str, content_hash: str = "", evaluation_score: float = 0, outcome: str = "pending"):
        conn = self._conn()
        conn.execute("INSERT OR REPLACE INTO lab_submissions VALUES (?,?,?,?,?,?,?)",
                     (submission_id, run_id, agent_id, content_hash, evaluation_score, outcome, time.time()))
        conn.commit()
        conn.close()

    # ─── Evaluations ────────────────────────────────────────────────────

    def record_evaluation(self, evaluation_id: str, run_id: str, submission_id: str = "", score: float = 0, gates_passed: list | None = None, reviewer: str = ""):
        conn = self._conn()
        conn.execute("INSERT OR REPLACE INTO lab_evaluations VALUES (?,?,?,?,?,?,?)",
                     (evaluation_id, run_id, submission_id, score, json.dumps(gates_passed or []), reviewer, time.time()))
        conn.commit()
        conn.close()

    # ─── Experiments ────────────────────────────────────────────────────

    def record_experiment(self, experiment_id: str, hypothesis: str, worker_version: str = "", status: str = "running", data: dict | None = None):
        conn = self._conn()
        if self.append_only:
            self._check_append(conn, "lab_experiments", "experiment_id", experiment_id)
        conn.execute("INSERT OR REPLACE INTO lab_experiments VALUES (?,?,?,?,?,?)",
                     (experiment_id, hypothesis, worker_version, status, json.dumps(data or {}), time.time()))
        conn.commit()
        conn.close()

    # ─── Run Dependencies — provenance tracking ────────────────────────

    def record_run_dependency(self, run_id: str, worker_version_id: str,
                              skill_version_ids: list[str] | None = None,
                              briefing_id: str = "", process_version_id: str = "",
                              memory_revision_id: str = "", reviewer_id: str = "",
                              context_pack_ids: list[str] | None = None):
        """Record the exact versions of all inputs used by a run."""
        conn = self._conn()
        if self.append_only:
            self._check_append(conn, "lab_run_dependencies", "run_id", run_id)
        conn.execute(
            "INSERT OR REPLACE INTO lab_run_dependencies VALUES (?,?,?,?,?,?,?,?,?)",
            (run_id, worker_version_id, json.dumps(skill_version_ids or []),
             briefing_id, process_version_id, memory_revision_id, reviewer_id,
             json.dumps(context_pack_ids or []), time.time()),
        )
        conn.commit()
        conn.close()

    def get_run_dependencies(self, run_id: str) -> dict | None:
        """Get the full provenance chain for a run."""
        conn = self._conn()
        row = conn.execute("SELECT * FROM lab_run_dependencies WHERE run_id=?", (run_id,)).fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        d["skill_version_ids"] = json.loads(d["skill_version_ids"]) if d["skill_version_ids"] else []
        d["context_pack_ids"] = json.loads(d["context_pack_ids"]) if d["context_pack_ids"] else []
        return d

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

    # ─── Interface methods (for future HydraDB implementation) ────────

    def project_event(self, event: dict) -> None:
        """Project a canonical WorkerEvent into this store."""
        event_type = event.get("event_type", "")
        run_id = event.get("run_id", "")
        payload = event.get("payload", {})
        if event_type == "run.started":
            self.record_run(run_id=run_id, agent_id=payload.get("agent_id", ""),
                          opportunity_id=payload.get("opportunity_id", ""),
                          model=payload.get("model", ""),
                          tools=payload.get("tools"),
                          skills=payload.get("skills"),
                          worker_version=payload.get("worker_version", ""))
        elif event_type == "run.cost":
            self.record_run(run_id=run_id, agent_id=payload.get("agent_id", ""),
                          cost_usd=payload.get("cost_usd", 0))
        elif event_type == "run.completed":
            self.record_run(run_id=run_id, agent_id=payload.get("agent_id", ""),
                          outcome=payload.get("outcome", "pending"),
                          reward_usd=payload.get("reward_usd", 0),
                          evaluation_score=payload.get("evaluation_score", 0))

    def rebuild(self) -> None:
        """Drop and recreate all tables from event ledger."""
        conn = self._conn()
        for table in ["lab_agents", "lab_runs", "lab_memory_revisions",
                       "lab_insights", "lab_worker_versions", "lab_opportunities",
                       "lab_submissions", "lab_evaluations", "lab_experiments"]:
            conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()
        conn.close()
        self._init()

    def query(self, table: str, filters: dict | None = None, limit: int = 100) -> list[dict]:
        """Generic query interface."""
        conn = self._conn()
        q = f"SELECT * FROM {table}"
        args: list = []
        if filters:
            conditions = []
            for k, v in filters.items():
                conditions.append(f"{k}=?")
                args.append(v)
            q += " WHERE " + " AND ".join(conditions)
        q += f" ORDER BY rowid DESC LIMIT ?"
        args.append(limit)
        rows = conn.execute(q, args).fetchall()
        conn.close()
        return [dict(r) for r in rows]


# Deprecated alias — use LabProjection
HydraStore = LabProjection
