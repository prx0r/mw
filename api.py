"""REST API — short endpoint names."""
from __future__ import annotations

import json
import time
from fastapi import FastAPI, Query
from oracle.store import q, stats, upsert_opp, upsert_svc, upsert_sub

app = FastAPI(title="oracle", version="0.1.0")


@app.get("/pulse")
def pulse():
    """Market snapshot."""
    s = stats()
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    by_src = conn.execute("SELECT src, COUNT(*) as c FROM opp GROUP BY src").fetchall()
    conn.close()
    return {"opp": s["opp"], "svc": s["svc"], "sub": s["sub"],
            "obs": s["obs"], "opp_usd": round(s["opp_usd"],2),
            "svc_calls": round(s["svc_calls"]),
            "by_src": {r["src"]: r["c"] for r in by_src}}


@app.get("/work")
def list_work(src: str = "", cat: str = "", skill: str = "",
              min_reward: float = 0, limit: int = 50):
    """List work opportunities."""
    sql = "SELECT * FROM opp WHERE 1=1"
    p = []
    if src: sql += " AND src=?"; p.append(src)
    if cat: sql += " AND cat=?"; p.append(cat)
    if skill: sql += " AND skills LIKE ?"; p.append(f"%{skill}%")
    if min_reward > 0: sql += " AND reward>=?"; p.append(min_reward)
    sql += " ORDER BY reward DESC LIMIT ?"
    p.append(limit)
    rows = q(sql, tuple(p))
    for r in rows: r["skills"] = json.loads(r.get("skills","[]")); r["extra"] = json.loads(r.get("extra","{}"))
    return {"work": rows, "count": len(rows)}


@app.get("/svc")
def list_svc(src: str = "", cat: str = "", limit: int = 50):
    """List services/tools."""
    sql = "SELECT * FROM svc WHERE 1=1"
    p = []
    if src: sql += " AND src=?"; p.append(src)
    if cat: sql += " AND cat=?"; p.append(cat)
    sql += " ORDER BY calls DESC LIMIT ?"
    p.append(limit)
    rows = q(sql, tuple(p))
    for r in rows: r["extra"] = json.loads(r.get("extra","{}"))
    return {"svc": rows, "count": len(rows)}


@app.get("/sub")
def sub(limit: int = 50):
    """List Bittensor subnets."""
    rows = q("SELECT * FROM sub ORDER BY emission DESC LIMIT ?", (limit,))
    for r in rows: r["extra"] = json.loads(r.get("extra","{}"))
    # Also include bittensor from svc table
    bt_rows = q("SELECT * FROM svc WHERE src='bittensor' ORDER BY extra DESC LIMIT ?", (limit,))
    for r in bt_rows:
        extra = json.loads(r.get("extra","{}"))
        rows.append({"id": r["id"], "netuid": 0, "name": r.get("name",""),
                     "emission": extra.get("emission_pct",0), "tao_price": extra.get("tao_price",0),
                     "miners": extra.get("miners",0), "validators": extra.get("validators",0),
                     "daily_usd": extra.get("daily_usd",0), "extra": extra})
    return {"sub": rows[:limit], "count": len(rows[:limit])}


@app.get("/demand")
def demand(window: str = "30d"):
    """Cross-layer demand analysis."""
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))

    work_rows = conn.execute("SELECT skills, reward, src FROM opp WHERE first_seen>=? AND reward>0", (since,)).fetchall()
    svc_rows = conn.execute("SELECT cat, src, calls FROM svc WHERE calls>0").fetchall()
    conn.close()

    skill_work = {}
    for r in work_rows:
        for s in json.loads(r["skills"] or "[]"):
            if s not in skill_work: skill_work[s] = {"n":0, "usd":0, "srcs": set()}
            skill_work[s]["n"] += 1; skill_work[s]["usd"] += r["reward"] or 0; skill_work[s]["srcs"].add(r["src"])

    skill_svc = {}
    for r in svc_rows:
        c = r["cat"]
        if c not in skill_svc: skill_svc[c] = {"n":0, "calls":0}
        skill_svc[c]["n"] += 1; skill_svc[c]["calls"] += r["calls"] or 0

    all_skills = set(list(skill_work.keys()) + list(skill_svc.keys()))
    results = []
    for s in all_skills:
        w = skill_work.get(s, {"n":0,"usd":0,"srcs":set()})
        v = skill_svc.get(s, {"n":0,"calls":0})
        results.append({"skill": s, "work_n": w["n"], "work_usd": round(w["usd"],2),
                        "svc_n": v["n"], "svc_calls": v["calls"], "score": w["n"]+v["n"]})
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"window": window, "skills": results}


@app.get("/compare")
def compare(window: str = "30d"):
    """Platform comparison."""
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))
    rows = conn.execute("SELECT src, reward, cat FROM opp WHERE first_seen>=? AND reward>0", (since,)).fetchall()
    conn.close()

    srcs = {}
    for r in rows:
        s = r["src"]
        if s not in srcs: srcs[s] = {"n":0, "usd":0, "rewards":[], "cats":{}}
        srcs[s]["n"] += 1; srcs[s]["usd"] += r["reward"] or 0
        srcs[s]["rewards"].append(r["reward"] or 0)
        c = r["cat"] or "general"; srcs[s]["cats"][c] = srcs[s]["cats"].get(c,0) + 1

    results = []
    for s, d in srcs.items():
        rw = d["rewards"]
        results.append({"src": s, "n": d["n"], "usd": round(d["usd"],2),
                        "median": round(sorted(rw)[len(rw)//2],2) if rw else 0,
                        "top_cat": max(d["cats"].items(), key=lambda x:x[1])[0] if d["cats"] else ""})
    results.sort(key=lambda x: x["median"], reverse=True)
    return {"window": window, "platforms": results}


@app.get("/brief")
def brief(skills: str = "", min_reward: float = 0, window: str = "30d"):
    """Agent briefing for specific skills."""
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]

    sql = "SELECT * FROM opp WHERE first_seen>=?"
    p = [since]
    for s in skill_list: sql += " AND skills LIKE ?"; p.append(f"%{s}%")
    if min_reward > 0: sql += " AND reward>=?"; p.append(min_reward)
    sql += " ORDER BY reward DESC LIMIT 50"
    rows = conn.execute(sql, tuple(p)).fetchall()
    conn.close()

    opps = []
    for r in rows:
        d = dict(r); d["skills"] = json.loads(d.get("skills","[]")); d["extra"] = json.loads(d.get("extra","{}"))
        opps.append(d)

    rw = sorted([o.get("reward",0) for o in opps if o.get("reward",0) > 0])
    return {"skills": skill_list, "window": window,
            "summary": {"n": len(opps), "usd": round(sum(o.get("reward",0) for o in opps),2),
                        "median": round(rw[len(rw)//2],2) if rw else 0,
                        "p75": round(rw[int(len(rw)*0.75)],2) if rw else 0},
            "top": opps[:10]}


@app.get("/supply")
def supply(cat: str = "", src: str = "", limit: int = 50):
    """Service supply."""
    sql = "SELECT * FROM svc WHERE 1=1"
    p = []
    if src: sql += " AND src=?"; p.append(src)
    if cat: sql += " AND cat=?"; p.append(cat)
    sql += " ORDER BY calls DESC LIMIT ?"; p.append(limit)
    rows = q(sql, tuple(p))
    for r in rows: r["extra"] = json.loads(r.get("extra","{}"))
    return {"svc": rows, "count": len(rows)}


@app.get("/trends")
def trends(window: str = "30d"):
    """Timeseries."""
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))
    rows = conn.execute("SELECT DATE(first_seen) as day, COUNT(*) as n, SUM(reward) as usd FROM opp WHERE first_seen>=? GROUP BY day ORDER BY day", (since,)).fetchall()
    conn.close()
    return {"window": window, "data": [{"date": r["day"], "n": r["n"], "usd": round(r["usd"] or 0,2)} for r in rows]}


@app.get("/boards")
def boards(limit: int = 20):
    """Leaderboards."""
    rows = q("SELECT * FROM opp WHERE reward>0 ORDER BY reward DESC LIMIT ?", (limit,))
    for r in rows: r["skills"] = json.loads(r.get("skills","[]")); r["extra"] = json.loads(r.get("extra","{}"))
    return {"leaders": rows, "count": len(rows)}


@app.get("/econ")
def econ():
    """Economics summary."""
    s = stats()
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    w = conn.execute("SELECT COUNT(*) as c, SUM(reward) as usd FROM opp WHERE reward>0").fetchone()
    svc = conn.execute("SELECT COUNT(*) as c, SUM(calls) as calls FROM svc").fetchone()
    conn.close()
    return {"work": {"n": w["c"], "usd": round(w["usd"] or 0,2)},
            "svc": {"n": svc["c"], "calls": round(svc["calls"] or 0)}}


@app.get("/data")
def data_summary():
    """Data summary."""
    s = stats()
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    by_src = conn.execute("SELECT src, COUNT(*) as c FROM opp GROUP BY src").fetchall()
    conn.close()
    return {"opp": s["opp"], "svc": s["svc"], "sub": s["sub"],
            "obs": s["obs"], "sig": s["sig"],
            "opp_usd": round(s["opp_usd"],2), "svc_calls": round(s["svc_calls"]),
            "by_src": {r["src"]: r["c"] for r in by_src}}


# === O3 Metrics (6 canonical families) ===

@app.get("/metrics")
def metrics(window: str = "30d"):
    """Compute all 6 canonical metric families."""
    from oracle.metrics import compute_metrics
    return compute_metrics(window)


# === History ===

@app.get("/history")
def history(window: str = "30d"):
    """Historical state changes over time."""
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))
    rows = conn.execute(
        "SELECT DATE(first_seen) as day, COUNT(*) as n, SUM(reward) as usd, "
        "SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END) as closed "
        "FROM opp WHERE first_seen>=? GROUP BY day ORDER BY day",
        (since,)
    ).fetchall()
    conn.close()
    return {"window": window, "history": [
        {"date": r["day"], "n": r["n"], "usd": round(r["usd"] or 0,2), "closed": r["closed"]}
        for r in rows
    ]}


# === Signals ===

@app.get("/signals")
def signals():
    """Market signals — unserved demand, emerging opportunities."""
    conn = __import__("oracle.store", fromlist=["conn"]).conn()

    # Unserved demand: high reward but few completions
    rows = conn.execute("""
        SELECT src, cat, COUNT(*) as n, AVG(reward) as avg_reward
        FROM opp WHERE status='open' AND reward>0
        GROUP BY src, cat ORDER BY avg_reward DESC LIMIT 20
    """).fetchall()

    # Emerging: recently posted with high reward
    recent = conn.execute("""
        SELECT src, title, reward, posted FROM opp
        WHERE reward>100 AND posted>datetime('now', '-7 days')
        ORDER BY reward DESC LIMIT 10
    """).fetchall()

    conn.close()

    return {
        "unserved_demand": [{"src": r["src"], "cat": r["cat"], "n": r["n"],
                            "avg_reward": round(r["avg_reward"],2)} for r in rows],
        "emerging": [{"src": r["src"], "title": r["title"], "reward": r["reward"],
                      "posted": r["posted"]} for r in recent],
    }


# === Core Primitives ===

@app.get("/opportunities")
def list_opportunities(kind: str = "", skill: str = "", min_reward: float = 0,
                       human_level: str = "", limit: int = 50):
    """List opportunities — the fundamental unit."""
    sql = "SELECT * FROM opp WHERE 1=1"
    p = []
    if skill:
        sql += " AND skills LIKE ?"; p.append(f"%{skill}%")
    if min_reward > 0:
        sql += " AND reward>=?"; p.append(min_reward)
    sql += " ORDER BY reward DESC LIMIT ?"; p.append(limit)
    rows = q(sql, tuple(p))
    for r in rows:
        r["skills"] = json.loads(r.get("skills","[]"))
        r["extra"] = json.loads(r.get("extra","{}"))
    return {"opportunities": rows, "count": len(rows)}


@app.get("/markets")
def list_markets():
    """All markets (platforms) with activity stats."""
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    rows = conn.execute("""
        SELECT src, COUNT(*) as n, SUM(reward) as usd,
               COUNT(CASE WHEN status='closed' THEN 1 END) as completed
        FROM opp GROUP BY src ORDER BY n DESC
    """).fetchall()
    conn.close()
    return {"markets": [{"src": r["src"], "n": r["n"], "usd": round(r["usd"] or 0,2),
                         "completed": r["completed"]} for r in rows]}


@app.get("/settlements")
def list_settlements():
    """Settlement options — how to pay across chains."""
    return {"options": [
        {"protocol": "X402", "networks": ["Base", "Solana"], "asset": "USDC"},
        {"protocol": "DIRECT_CHAIN", "networks": ["Solana", "NEAR"], "asset": "SOL/NEAR"},
        {"protocol": "NEAR_INTENT", "networks": ["cross-chain"], "asset": "any"},
        {"protocol": "FIAT", "networks": ["Stripe"], "asset": "USD"},
        {"protocol": "PLATFORM_NATIVE", "networks": ["Moltwork"], "asset": "credits"},
    ]}


@app.get("/h-levels")
def human_levels():
    """H0-H4 human intervention taxonomy."""
    from oracle.models import HUMAN_LEVELS, HUMAN_MARKET_CHARS
    return {"levels": HUMAN_LEVELS, "market_characteristics": HUMAN_MARKET_CHARS}


@app.get("/work-receipts")
def work_receipts(limit: int = 20):
    """WorkReceipts — what WorkerKit observed."""
    rows = q("SELECT * FROM obs WHERE metric='status' AND curr_val IN ('completed','paid') ORDER BY observed DESC LIMIT ?", (limit,))
    return {"receipts": rows, "count": len(rows)}


@app.get("/history")
def history(opp_id: str = "", source: str = "", limit: int = 50):
    """Longitudinal observation history for opportunities."""
    if opp_id:
        rows = q("SELECT * FROM opp_obs WHERE opp_id=? ORDER BY observed_at DESC LIMIT ?", (opp_id, limit))
        events = q("SELECT * FROM opp_events WHERE opp_id=? ORDER BY event_at DESC LIMIT ?", (opp_id, limit))
        return {"opp_id": opp_id, "observations": rows, "events": events}
    elif source:
        rows = q("""SELECT o.* FROM opp_obs o 
            JOIN opp ON o.opp_id = opp.id 
            WHERE opp.src=? ORDER BY o.observed_at DESC LIMIT ?""", (source, limit))
        return {"source": source, "observations": rows}
    else:
        rows = q("SELECT * FROM opp_obs ORDER BY observed_at DESC LIMIT ?", (limit,))
        return {"observations": rows}


@app.get("/market-history")
def market_history(source: str = "", limit: int = 50):
    """Market-level observations over time."""
    if source:
        rows = q("""SELECT o.opp_id, o.observed_at, o.status, o.reward, opp.src, opp.title 
            FROM opp_obs o JOIN opp ON o.opp_id = opp.id 
            WHERE opp.src=? ORDER BY o.observed_at DESC LIMIT ?""", (source, limit))
    else:
        rows = q("""SELECT o.opp_id, o.observed_at, o.status, o.reward, opp.src, opp.title 
            FROM opp_obs o JOIN opp ON o.opp_id = opp.id 
            ORDER BY o.observed_at DESC LIMIT ?""", (limit,))
    return {"history": rows}
