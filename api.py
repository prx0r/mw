"""REST API — short endpoint names."""
from __future__ import annotations

import json
import time
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from oracle.store import q, q1, stats, upsert_opp, upsert_svc, upsert_sub

app = FastAPI(title="oracle", version="0.1.0")

DASHBOARD = Path(__file__).parent / "dashboard.html"


@app.get("/", response_class=HTMLResponse)
def dashboard():
    """Moltwork Oracle dashboard."""
    return DASHBOARD.read_text()


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
    from oracle.models import HUMAN_LEVELS
    return {"levels": HUMAN_LEVELS}


@app.get("/work-receipts")
def work_receipts(limit: int = 20):
    """WorkReceipts — what WorkerKit observed."""
    rows = q("SELECT * FROM obs WHERE metric='status' AND curr_val IN ('completed','paid') ORDER BY observed DESC LIMIT ?", (limit,))
    return {"receipts": rows, "count": len(rows)}


@app.get("/observations")
def observations(opp_id: str = "", source: str = "", limit: int = 50):
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


# ============================================
# DeFiLlama-style API endpoints
# ============================================

@app.get("/v1/totals")
def v1_totals():
    """Overview metrics — DefiLlama /protocols style."""
    s = stats()
    markets = q("SELECT COUNT(*) as c FROM oracle_opps GROUP BY market_id")
    skills = q("SELECT COUNT(*) as c FROM oracle_skills")
    categories = q("SELECT COUNT(*) as c FROM oracle_categories")

    # Reward distribution
    rewards = q("SELECT reward_usd FROM oracle_opps WHERE reward_usd > 0 ORDER BY reward_usd")
    rewards_list = [r["reward_usd"] for r in rewards]
    n = len(rewards_list)
    median = rewards_list[n//2] if n > 0 else 0
    p25 = rewards_list[n//4] if n > 0 else 0
    p75 = rewards_list[3*n//4] if n > 0 else 0
    p90 = rewards_list[9*n//10] if n > 0 else 0
    avg = sum(rewards_list) / n if n > 0 else 0

    return {
        "active_opportunities": s["oracle_opps"],
        "total_reward_usd": round(s["oracle_usd"], 2),
        "median_reward_usd": round(median, 2),
        "avg_reward_usd": round(avg, 2),
        "p25_reward_usd": round(p25, 2),
        "p75_reward_usd": round(p75, 2),
        "p90_reward_usd": round(p90, 2),
        "markets": len(markets),
        "skills": len(skills),
        "categories": len(categories),
        "observations": s["oracle_opp_obs"],
        "events": s["oracle_opp_events"],
    }


@app.get("/v1/totals/by-market")
def v1_totals_by_market():
    """Totals broken down by market."""
    rows = q("""SELECT market_id,
        COUNT(*) as opportunities,
        SUM(reward_usd) as total_reward_usd,
        AVG(reward_usd) as avg_reward_usd,
        MIN(first_seen_at) as first_seen,
        MAX(last_seen_at) as last_seen
        FROM oracle_opps
        GROUP BY market_id
        ORDER BY total_reward_usd DESC""")
    return {"markets": rows}


@app.get("/v1/totals/by-category")
def v1_totals_by_category():
    """Totals broken down by category."""
    rows = q("""SELECT c.slug as category,
        COUNT(DISTINCT o.id) as opportunities,
        SUM(o.reward_usd) as total_reward_usd,
        AVG(o.reward_usd) as avg_reward_usd
        FROM oracle_opps o
        JOIN oracle_opp_categories oc ON o.id = oc.opportunity_id
        JOIN oracle_categories c ON oc.category_id = c.id
        GROUP BY c.slug
        ORDER BY total_reward_usd DESC""")
    return {"categories": rows}


@app.get("/v1/totals/by-skill")
def v1_totals_by_skill():
    """Totals broken down by skill."""
    rows = q("""SELECT s.slug as skill,
        COUNT(DISTINCT o.id) as opportunities,
        SUM(o.reward_usd) as total_reward_usd,
        AVG(o.reward_usd) as avg_reward_usd
        FROM oracle_opps o
        JOIN oracle_opp_skills os ON o.id = os.opportunity_id
        JOIN oracle_skills s ON os.skill_id = s.id
        GROUP BY s.slug
        ORDER BY total_reward_usd DESC
        LIMIT 50""")
    return {"skills": rows}


@app.get("/v1/timeseries")
def v1_timeseries(metric: str = "opportunities", window: str = "30d", market: str = ""):
    """Time-series data — DefiLlama /chart style."""
    # For now, use observation timestamps as proxy
    if market:
        rows = q("""SELECT DATE(observed_at) as date,
            COUNT(DISTINCT opportunity_id) as opportunities,
            SUM(reward_usd) as reward_usd
            FROM oracle_opp_obs
            WHERE source_id LIKE ?
            GROUP BY DATE(observed_at)
            ORDER BY date""", (f"%{market}%",))
    else:
        rows = q("""SELECT DATE(observed_at) as date,
            COUNT(DISTINCT opportunity_id) as opportunities,
            SUM(reward_usd) as reward_usd
            FROM oracle_opp_obs
            GROUP BY DATE(observed_at)
            ORDER BY date""")
    return {"metric": metric, "window": window, "data": rows}


@app.get("/v1/rankings")
def v1_rankings(kind: str = "market", sort: str = "reward_usd", limit: int = 20):
    """Ranked tables — DefiLlama /protocols sorted."""
    if kind == "market":
        rows = q(f"""SELECT market_id as id,
            COUNT(*) as opportunities,
            SUM(reward_usd) as total_reward_usd,
            AVG(reward_usd) as avg_reward_usd,
            MAX(last_seen_at) as last_active
            FROM oracle_opps
            GROUP BY market_id
            ORDER BY {sort} DESC
            LIMIT ?""", (limit,))
    elif kind == "skill":
        rows = q(f"""SELECT s.slug as id,
            COUNT(DISTINCT o.id) as opportunities,
            SUM(o.reward_usd) as total_reward_usd,
            AVG(o.reward_usd) as avg_reward_usd
            FROM oracle_opps o
            JOIN oracle_opp_skills os ON o.id = os.opportunity_id
            JOIN oracle_skills s ON os.skill_id = s.id
            GROUP BY s.slug
            ORDER BY {sort} DESC
            LIMIT ?""", (limit,))
    elif kind == "category":
        rows = q(f"""SELECT c.slug as id,
            COUNT(DISTINCT o.id) as opportunities,
            SUM(o.reward_usd) as total_reward_usd,
            AVG(o.reward_usd) as avg_reward_usd
            FROM oracle_opps o
            JOIN oracle_opp_categories oc ON o.id = oc.opportunity_id
            JOIN oracle_categories c ON oc.category_id = c.id
            GROUP BY c.slug
            ORDER BY {sort} DESC
            LIMIT ?""", (limit,))
    else:
        rows = []
    return {"kind": kind, "sort": sort, "rankings": rows}


@app.get("/v1/opportunities")
def v1_opportunities(
    market: str = "",
    category: str = "",
    skill: str = "",
    status: str = "",
    min_reward: float = 0,
    execution_mode: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: str = "reward_usd",
    order: str = "desc"
):
    """Filterable opportunity list — core DefiLlama-style query."""
    conditions = []
    params = []

    if market:
        conditions.append("o.market_id = ?")
        params.append(market)
    if category:
        conditions.append("o.id IN (SELECT opportunity_id FROM oracle_opp_categories oc JOIN oracle_categories c ON oc.category_id = c.id WHERE c.slug = ?)")
        params.append(category)
    if skill:
        conditions.append("o.id IN (SELECT opportunity_id FROM oracle_opp_skills os JOIN oracle_skills s ON os.skill_id = s.id WHERE s.slug = ?)")
        params.append(skill)
    if status:
        conditions.append("o.status = ?")
        params.append(status)
    if min_reward > 0:
        conditions.append("o.reward_usd >= ?")
        params.append(min_reward)
    if execution_mode:
        conditions.append("o.execution_mode = ?")
        params.append(execution_mode)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    allowed_sorts = {"reward_usd", "first_seen_at", "last_seen_at", "created_at"}
    if sort not in allowed_sorts:
        sort = "reward_usd"
    order_dir = "DESC" if order.lower() == "desc" else "ASC"

    rows = q(f"""SELECT o.*,
        (SELECT GROUP_CONCAT(s.slug) FROM oracle_opp_skills os
         JOIN oracle_skills s ON os.skill_id = s.id
         WHERE os.opportunity_id = o.id) as skill_list
        FROM oracle_opps o
        {where}
        ORDER BY o.{sort} {order_dir}
        LIMIT ? OFFSET ?""",
        tuple(params) + (limit, offset))

    # Get total count
    count_row = q1(f"SELECT COUNT(*) as c FROM oracle_opps o {where}", tuple(params))
    total = count_row["c"] if count_row else 0

    return {"total": total, "limit": limit, "offset": offset, "opportunities": rows}


@app.get("/v1/opportunities/{opp_id}")
def v1_opportunity_detail(opp_id: str):
    """Single opportunity with full history."""
    opp = q1("SELECT * FROM oracle_opps WHERE id=?", (opp_id,))
    if not opp:
        return {"error": "not found"}

    observations = q("""SELECT * FROM oracle_opp_obs
        WHERE opportunity_id=? ORDER BY observed_at DESC LIMIT 100""", (opp_id,))
    events = q("""SELECT * FROM oracle_opp_events
        WHERE opportunity_id=? ORDER BY observed_at DESC LIMIT 100""", (opp_id,))
    skills = q("""SELECT s.slug, s.name FROM oracle_opp_skills os
        JOIN oracle_skills s ON os.skill_id = s.id
        WHERE os.opportunity_id=?""", (opp_id,))

    return {
        "opportunity": opp,
        "skills": skills,
        "observations": observations,
        "events": events,
    }


@app.get("/v1/skills")
def v1_skills(limit: int = 100, sort: str = "opportunities"):
    """Skill taxonomy with metrics."""
    rows = q(f"""SELECT s.id, s.slug, s.name,
        COUNT(DISTINCT os.opportunity_id) as opportunities,
        SUM(o.reward_usd) as total_reward_usd,
        AVG(o.reward_usd) as avg_reward_usd
        FROM oracle_skills s
        LEFT JOIN oracle_opp_skills os ON s.id = os.skill_id
        LEFT JOIN oracle_opps o ON os.opportunity_id = o.id
        GROUP BY s.id
        ORDER BY {sort} DESC
        LIMIT ?""", (limit,))
    return {"skills": rows}


@app.get("/v1/skills/trending")
def v1_skills_trending(window: str = "7d", limit: int = 20):
    """Trending skills by recent opportunity count."""
    rows = q("""SELECT s.slug, s.name,
        COUNT(DISTINCT o.id) as recent_opportunities,
        SUM(o.reward_usd) as recent_reward_usd
        FROM oracle_skills s
        JOIN oracle_opp_skills os ON s.id = os.skill_id
        JOIN oracle_opps o ON os.opportunity_id = o.id
        WHERE o.first_seen_at >= datetime('now', '-7 days')
        GROUP BY s.id
        ORDER BY recent_opportunities DESC
        LIMIT ?""", (limit,))
    return {"skills": rows, "window": window}


@app.get("/v1/categories")
def v1_categories():
    """Category list with metrics."""
    rows = q("""SELECT c.id, c.slug, c.name,
        COUNT(DISTINCT oc.opportunity_id) as opportunities,
        SUM(o.reward_usd) as total_reward_usd,
        AVG(o.reward_usd) as avg_reward_usd
        FROM oracle_categories c
        LEFT JOIN oracle_opp_categories oc ON c.id = oc.category_id
        LEFT JOIN oracle_opps o ON oc.opportunity_id = o.id
        GROUP BY c.id
        ORDER BY total_reward_usd DESC""")
    return {"categories": rows}


@app.get("/v1/sources")
def v1_sources():
    """Source health and freshness."""
    rows = q("""SELECT o.market_id as source,
        COUNT(*) as opportunities,
        MAX(o.last_seen_at) as last_active,
        MIN(o.first_seen_at) as first_seen,
        SUM(o.reward_usd) as total_reward_usd
        FROM oracle_opps o
        GROUP BY o.market_id
        ORDER BY opportunities DESC""")
    return {"sources": rows}


@app.get("/v1/sources/{source}/opportunities")
def v1_source_opportunities(source: str, limit: int = 50, offset: int = 0):
    """Opportunities from a specific source."""
    rows = q("""SELECT * FROM oracle_opps
        WHERE market_id=?
        ORDER BY reward_usd DESC
        LIMIT ? OFFSET ?""", (source, limit, offset))
    count = q1("SELECT COUNT(*) as c FROM oracle_opps WHERE market_id=?", (source,))
    return {"source": source, "total": count["c"] if count else 0, "opportunities": rows}


@app.get("/v1/events")
def v1_events(event_type: str = "", limit: int = 50):
    """Recent events across all opportunities."""
    if event_type:
        rows = q("""SELECT e.*, o.canonical_title, o.market_id
            FROM oracle_opp_events e
            JOIN oracle_opps o ON e.opportunity_id = o.id
            WHERE e.event_type=?
            ORDER BY e.observed_at DESC LIMIT ?""", (event_type, limit))
    else:
        rows = q("""SELECT e.*, o.canonical_title, o.market_id
            FROM oracle_opp_events e
            JOIN oracle_opps o ON e.opportunity_id = o.id
            ORDER BY e.observed_at DESC LIMIT ?""", (limit,))
    return {"events": rows}


@app.get("/v1/ingest/runs")
def v1_ingest_runs(limit: int = 20):
    """Recent ingest runs."""
    rows = q("SELECT * FROM oracle_ingest_runs ORDER BY started_at DESC LIMIT ?", (limit,))
    return {"runs": rows}


@app.get("/v1/rewards/distribution")
def v1_rewards_distribution():
    """Reward distribution histogram."""
    brackets = [
        (0, 10, "$0-10"),
        (10, 50, "$10-50"),
        (50, 100, "$50-100"),
        (100, 500, "$100-500"),
        (500, 1000, "$500-1K"),
        (1000, 5000, "$1K-5K"),
        (5000, 10000, "$5K-10K"),
        (10000, 100000, "$10K+"),
    ]
    result = []
    for low, high, label in brackets:
        count = q1("SELECT COUNT(*) as c FROM oracle_opps WHERE reward_usd >= ? AND reward_usd < ?",
                   (low, high))
        result.append({"range": label, "count": count["c"] if count else 0})
    return {"distribution": result}


@app.get("/v1/compare")
def v1_compare():
    """Market comparison table."""
    rows = q("""SELECT market_id as source,
        COUNT(*) as opportunities,
        SUM(reward_usd) as total_reward_usd,
        AVG(reward_usd) as avg_reward_usd,
        MIN(reward_usd) as min_reward_usd,
        MAX(reward_usd) as max_reward_usd,
        MAX(last_seen_at) as last_active
        FROM oracle_opps
        GROUP BY market_id
        ORDER BY total_reward_usd DESC""")
    return {"platforms": rows}


# ============================================
# TAXONOMY-AWARE ENDPOINTS (shared ontology)
# ============================================

from oracle.store import (
    get_opps_by_task_family, get_opps_by_capability,
    get_opps_by_agent_caps, get_taxonomy_stats, get_agent_match_score,
)
from oracle.taxonomy import classify_opportunity, SOURCE_CATEGORY_MAP


@app.get("/v1/work/taxonomy")
def v1_work_taxonomy():
    """List all known task families and their opportunity counts."""
    stats = get_taxonomy_stats()
    return {"task_families": stats["by_task_family"],
            "autonomy_levels": stats["by_autonomy"],
            "top_capabilities": stats["by_capability"]}


@app.get("/v1/work/by-task/{task_family}")
def v1_work_by_task(task_family: str, status: str = "open", limit: int = 50):
    """Get opportunities by canonical task family."""
    opps = get_opps_by_task_family(task_family, status, limit)
    return {"task_family": task_family, "opportunities": opps, "count": len(opps)}


@app.get("/v1/work/by-capability/{capability}")
def v1_work_by_capability(capability: str, status: str = "open", limit: int = 50):
    """Get opportunities requiring a specific capability."""
    opps = get_opps_by_capability(capability, status, limit)
    return {"capability": capability, "opportunities": opps, "count": len(opps)}


@app.get("/v1/work/match")
def v1_work_match(caps: str = "", status: str = "open", limit: int = 50):
    """Match opportunities to agent capabilities.

    Query param: caps = comma-separated capability list
    Returns opportunities sorted by relevance (capability overlap).
    """
    agent_caps = [c.strip() for c in caps.split(",") if c.strip()] if caps else []
    if not agent_caps:
        return {"error": "provide caps parameter (comma-separated capabilities)", "opportunities": []}
    opps = get_opps_by_agent_caps(agent_caps, status, limit)
    # Add match score to each
    for opp in opps:
        opp["match_score"] = get_agent_match_score(agent_caps, opp)
    opps.sort(key=lambda o: o.get("match_score", 0), reverse=True)
    return {"agent_capabilities": agent_caps, "opportunities": opps, "count": len(opps)}


@app.get("/v1/work/classify")
def v1_classify(source: str = "", category: str = "", skills: str = ""):
    """Classify raw source data into canonical taxonomy.

    For testing the mapping without a full ingest.
    """
    skill_list = [s.strip() for s in skills.split(",") if s.strip()] if skills else []
    result = classify_opportunity(source, category, skill_list)
    return {"source": source, "raw_category": category, "raw_skills": skill_list,
            "classification": result}


@app.get("/v1/work/taxonomy-map")
def v1_taxonomy_map():
    """Show the source→canonical category mapping."""
    return {"mappings": SOURCE_CATEGORY_MAP, "count": len(SOURCE_CATEGORY_MAP)}


# ============================================
# DEMAND / SUPPLY INTELLIGENCE ENDPOINTS
# ============================================

from oracle.store import get_labor_demand, get_capability_demand, get_supply_deficit, get_training_opportunities


@app.get("/v1/intelligence/demand")
def v1_demand():
    """Open labor demand by task family."""
    return {"demand": get_labor_demand()}


@app.get("/v1/intelligence/capabilities")
def v1_capability_demand():
    """Demand per capability."""
    return {"capabilities": get_capability_demand()}


@app.get("/v1/intelligence/supply-deficit")
def v1_supply_deficit(caps: str = ""):
    """Compare worker capabilities against market demand.

    Query param: caps = comma-separated capability list
    """
    worker_caps = [c.strip() for c in caps.split(",") if c.strip()] if caps else []
    if not worker_caps:
        return {"error": "provide caps parameter"}
    return get_supply_deficit(worker_caps)


@app.get("/v1/intelligence/training")
def v1_training_opportunities(caps: str = ""):
    """What training would unlock the most demand?

    Query param: caps = comma-separated capability list
    """
    worker_caps = [c.strip() for c in caps.split(",") if c.strip()] if caps else []
    return {"opportunities": get_training_opportunities(worker_caps)}
