"""LabContext — HydraDB-backed broker, progressive disclosure.

Indexed queries on graph data via HydraDB.
"""
from __future__ import annotations
import json, time


class LabContext:
    def __init__(self, hydra, worker_id: str):
        self.hydra = hydra
        self.worker_id = worker_id

    def recall_similar_runs(self, task_family: str, limit: int = 5) -> list[dict]:
        """Find similar runs using indexed task_family column."""
        conn = self.hydra._conn()
        # First: try exact task_family match
        rows = conn.execute(
            "SELECT * FROM lab_runs WHERE task_family=? ORDER BY created_at DESC LIMIT ?",
            (task_family, limit * 3)
        ).fetchall()
        cols = [d[0] for d in conn.execute("SELECT * FROM lab_runs LIMIT 0").description]
        runs = [dict(zip(cols, r)) for r in rows]

        # Fallback: if no exact match, try skills column
        if not runs:
            rows = conn.execute(
                "SELECT * FROM lab_runs WHERE skills LIKE ? ORDER BY created_at DESC LIMIT ?",
                (f"%{task_family}%", limit * 3)
            ).fetchall()
            runs = [dict(zip(cols, r)) for r in rows]

        # Further fallback: opportunity_id
        if not runs:
            rows = conn.execute(
                "SELECT * FROM lab_runs WHERE opportunity_id LIKE ? ORDER BY created_at DESC LIMIT ?",
                (f"%{task_family}%", limit * 3)
            ).fetchall()
            runs = [dict(zip(cols, r)) for r in rows]

        conn.close()

        # Prioritize wins, then by score
        wins = [r for r in runs if r.get("outcome") == "won"]
        result = wins[:limit] if wins else runs[:limit]

        return [{
            "run_id": r["run_id"],
            "score": r.get("evaluation_score"),
            "model": r.get("model"),
            "worker_version": r.get("worker_version", ""),
            "task_family": r.get("task_family", ""),
            "skills": json.loads(r["skills"]) if isinstance(r.get("skills"), str) else r.get("skills", []),
        } for r in result]

    def get_task_priors(self, task_family: str) -> dict:
        """Get prior statistics for a task family using indexed queries."""
        conn = self.hydra._conn()
        cols = [d[0] for d in conn.execute("SELECT * FROM lab_runs LIMIT 0").description]

        # Exact match first
        rows = conn.execute(
            "SELECT * FROM lab_runs WHERE task_family=?", (task_family,)
        ).fetchall()
        fam = [dict(zip(cols, r)) for r in rows]

        # Fallback to all runs if no match
        if not fam:
            rows = conn.execute("SELECT * FROM lab_runs").fetchall()
            fam = [dict(zip(cols, r)) for r in rows]

        conn.close()

        won = sum(1 for r in fam if r.get("outcome") == "won")
        tot = sum(1 for r in fam if r.get("outcome") in ("won", "lost"))
        return {
            "task_family": task_family,
            "n": len(fam),
            "win_rate": round(won / max(1, tot), 2),
            "avg_score": round(sum(r.get("evaluation_score", 0) for r in fam) / max(1, len(fam)), 3),
        }

    def get_failure_patterns(self, role: str) -> list[dict]:
        """Get failure patterns using failure_reason column (not score buckets)."""
        conn = self.hydra._conn()
        cols = [d[0] for d in conn.execute("SELECT * FROM lab_runs LIMIT 0").description]

        # Use failure_reason column if available
        rows = conn.execute(
            "SELECT * FROM lab_runs WHERE outcome='lost' AND failure_reason != '' AND failure_reason IS NOT NULL"
        ).fetchall()
        losses = [dict(zip(cols, r)) for r in rows]

        conn.close()

        if losses:
            # Count failure reasons
            buckets: dict[str, int] = {}
            for r in losses:
                reason = r.get("failure_reason", "unknown")
                buckets[reason] = buckets.get(reason, 0) + 1
            return sorted([{"pattern": k, "count": v} for k, v in buckets.items()],
                         key=lambda x: -x["count"])[:3]

        # Fallback: use score buckets (deprecated, but backward compat)
        conn = self.hydra._conn()
        rows = conn.execute(
            "SELECT * FROM lab_runs WHERE outcome='lost'"
        ).fetchall()
        losses = [dict(zip(cols, r)) for r in rows]
        conn.close()

        buckets = {}
        for r in losses:
            k = f"low_score_{int(r.get('evaluation_score', 0) * 10)}"
            buckets[k] = buckets.get(k, 0) + 1
        return sorted([{"pattern": k, "count": v} for k, v in buckets.items()],
                     key=lambda x: -x["count"])[:3]

    def get_best_skill(self, task_family: str) -> dict | None:
        """Find the best skill for a task family using indexed queries."""
        cor = self.hydra.skill_win_correlation()
        if not cor:
            return None

        # Filter by task_family in skill name
        cand = [c for c in cor if task_family.lower() in c["skill"].lower()]
        best = cand[0] if cand else cor[0]
        return {"skill": best["skill"], "win_rate": best["win_rate"], "n": best["n"]}

    def record_observation(self, run_id: str, data: dict) -> None:
        """Record observation as insight if evidence present."""
        if data.get("failure_reason"):
            self.hydra.add_insight(
                f"obs_{run_id}", data["failure_reason"][:80],
                json.dumps(data)[:400], 1, 0.5
            )

    def brief(self, task_family: str) -> str:
        """Generate a compact lab brief for a task family."""
        pri = self.get_task_priors(task_family)
        sim = self.recall_similar_runs(task_family, 3)
        skill = self.get_best_skill(task_family)
        fails = self.get_failure_patterns(task_family)
        econ = self.hydra.profitability_by_model()
        econ_line = ", ".join(f"{e['model']}:${e['avg_profit']:.2f}" for e in econ[:2]) if econ else "n/a"

        lines = [
            f"# LAB BRIEF — {task_family}",
            f"**Worker** {self.worker_id}",
            "",
            f"Task family: {task_family}",
            f"Prior runs: {pri['n']}  win_rate: {pri['win_rate']:.0%}  avg_score: {pri['avg_score']}",
            f"Best skill: {skill['skill']} ({skill['win_rate']:.0%} n={skill['n']})" if skill else "Best skill: n/a",
            f"Model economics: {econ_line}",
            "",
        ]
        if sim:
            lines += ["Similar wins:"] + [f"- {s['run_id']} score={s['score']} model={s['model']}" for s in sim]
        if fails:
            lines += ["", "Failure warnings:"] + [f"- {f['pattern']} x{f['count']}" for f in fails]
        lines += ["", "*Full trajectories on demand — ask for run_id.*"]
        return "\n".join(lines)
