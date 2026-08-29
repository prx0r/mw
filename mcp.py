"""MCP server — 14 tools with short names."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from .store import q, stats


TOOLS = [
    {"name": "mol_pulse", "desc": "Market snapshot", "schema": {}},
    {"name": "mol_work", "desc": "List work opportunities", "schema": {"src": "string", "cat": "string", "skill": "string", "min": "number"}},
    {"name": "mol_svc", "desc": "List services/tools", "schema": {"src": "string", "cat": "string"}},
    {"name": "mol_sub", "desc": "List Bittensor subnets", "schema": {}},
    {"name": "mol_demand", "desc": "Cross-layer demand analysis", "schema": {"window": "string"}},
    {"name": "mol_compare", "desc": "Platform comparison", "schema": {"window": "string"}},
    {"name": "mol_brief", "desc": "Agent briefing for skills", "schema": {"skills": "string", "min": "number"}},
    {"name": "mol_supply", "desc": "Service supply", "schema": {"src": "string", "cat": "string"}},
    {"name": "mol_trends", "desc": "Timeseries", "schema": {"window": "string"}},
    {"name": "mol_boards", "desc": "Leaderboards", "schema": {}},
    {"name": "mol_econ", "desc": "Economics summary", "schema": {}},
    {"name": "mol_data", "desc": "Data summary", "schema": {}},
    {"name": "mol_search", "desc": "Search work by text", "schema": {"q": "string"}},
    {"name": "mol_obs", "desc": "Observations for entity", "schema": {"id": "string"}},
]

HANDLERS = {
    "mol_pulse": lambda **kw: _pulse(),
    "mol_work": lambda **kw: _work(kw.get("src",""), kw.get("cat",""), kw.get("skill",""), kw.get("min",0)),
    "mol_svc": lambda **kw: _svc(kw.get("src",""), kw.get("cat","")),
    "mol_sub": lambda **kw: _sub(),
    "mol_demand": lambda **kw: _demand(kw.get("window","30d")),
    "mol_compare": lambda **kw: _compare(kw.get("window","30d")),
    "mol_brief": lambda **kw: _brief(kw.get("skills",""), kw.get("min",0)),
    "mol_supply": lambda **kw: _supply(kw.get("src",""), kw.get("cat","")),
    "mol_trends": lambda **kw: _trends(kw.get("window","30d")),
    "mol_boards": lambda **kw: _boards(),
    "mol_econ": lambda **kw: _econ(),
    "mol_data": lambda **kw: _data(),
    "mol_search": lambda **kw: _search(kw.get("q","")),
    "mol_obs": lambda **kw: _obs(kw.get("id","")),
}


def _pulse():
    s = stats()
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    by_src = conn.execute("SELECT src, COUNT(*) as c FROM opp GROUP BY src").fetchall()
    conn.close()
    return {"opp": s["opp"], "svc": s["svc"], "sub": s["sub"],
            "opp_usd": round(s["opp_usd"],2), "by_src": {r["src"]: r["c"] for r in by_src}}


def _work(src="", cat="", skill="", min_r=0):
    sql = "SELECT * FROM opp WHERE 1=1"; p = []
    if src: sql += " AND src=?"; p.append(src)
    if cat: sql += " AND cat=?"; p.append(cat)
    if skill: sql += " AND skills LIKE ?"; p.append(f"%{skill}%")
    if min_r > 0: sql += " AND reward>=?"; p.append(min_r)
    sql += " ORDER BY reward DESC LIMIT 20"
    rows = q(sql, tuple(p))
    for r in rows: r["skills"] = json.loads(r.get("skills","[]"))
    return {"work": rows, "count": len(rows)}


def _svc(src="", cat=""):
    sql = "SELECT * FROM svc WHERE 1=1"; p = []
    if src: sql += " AND src=?"; p.append(src)
    if cat: sql += " AND cat=?"; p.append(cat)
    sql += " ORDER BY calls DESC LIMIT 20"
    return {"svc": q(sql, tuple(p)), "count": len(q(sql, tuple(p)))}


def _sub():
    return {"sub": q("SELECT * FROM sub ORDER BY emission DESC LIMIT 20"), "count": len(q("SELECT * FROM sub LIMIT 1"))}


def _demand(window="30d"):
    from oracle.store import conn as _conn
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))
    c = _conn()
    wr = c.execute("SELECT skills, reward, src FROM opp WHERE first_seen>=? AND reward>0", (since,)).fetchall()
    sr = c.execute("SELECT cat, src, calls FROM svc WHERE calls>0").fetchall()
    c.close()
    sw = {}
    for r in wr:
        for s in json.loads(r["skills"] or "[]"):
            if s not in sw: sw[s] = {"n":0,"usd":0}
            sw[s]["n"] += 1; sw[s]["usd"] += r["reward"] or 0
    return {"skills": [{"skill":s, **d} for s,d in sorted(sw.items(), key=lambda x: -x[1]["n"])[:20]]}


def _compare(window="30d"):
    from oracle.store import conn as _conn
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))
    c = _conn()
    rows = c.execute("SELECT src, reward FROM opp WHERE first_seen>=? AND reward>0", (since,)).fetchall()
    c.close()
    srcs = {}
    for r in rows:
        s = r["src"]
        if s not in srcs: srcs[s] = {"n":0, "rewards":[]}
        srcs[s]["n"] += 1; srcs[s]["rewards"].append(r["reward"] or 0)
    return [{"src":s, "n":d["n"], "median": round(sorted(d["rewards"])[len(d["rewards"])//2],2) if d["rewards"] else 0} for s,d in sorted(srcs.items(), key=lambda x: -x[1]["n"])]


def _brief(skills="", min_r=0):
    from oracle.store import conn as _conn
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    c = _conn()
    sql = "SELECT * FROM opp WHERE first_seen>=?"; p = [time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 30*86400))]
    for s in skill_list: sql += " AND skills LIKE ?"; p.append(f"%{s}%")
    if min_r > 0: sql += " AND reward>=?"; p.append(min_r)
    sql += " ORDER BY reward DESC LIMIT 10"
    rows = c.execute(sql, tuple(p)).fetchall()
    c.close()
    return {"skills": skill_list, "n": len(rows), "top": [dict(r) for r in rows]}


def _supply(src="", cat=""):
    sql = "SELECT * FROM svc WHERE 1=1"; p = []
    if src: sql += " AND src=?"; p.append(src)
    if cat: sql += " AND cat=?"; p.append(cat)
    sql += " ORDER BY calls DESC LIMIT 10"
    return q(sql, tuple(p))


def _trends(window="30d"):
    from oracle.store import conn as _conn
    days = int(window.rstrip("d")) if window.endswith("d") else 30
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))
    c = _conn()
    rows = c.execute("SELECT DATE(first_seen) as day, COUNT(*) as n FROM opp WHERE first_seen>=? GROUP BY day", (since,)).fetchall()
    c.close()
    return [{"date": r["day"], "n": r["n"]} for r in rows]


def _boards():
    return q("SELECT * FROM opp WHERE reward>0 ORDER BY reward DESC LIMIT 10")


def _econ():
    s = stats()
    return {"opp_usd": round(s["opp_usd"],2), "svc_calls": round(s["svc_calls"])}


def _data():
    s = stats()
    conn = __import__("oracle.store", fromlist=["conn"]).conn()
    by_src = conn.execute("SELECT src, COUNT(*) as c FROM opp GROUP BY src").fetchall()
    conn.close()
    return {"opp": s["opp"], "svc": s["svc"], "sub": s["sub"], "obs": s["obs"],
            "by_src": {r["src"]: r["c"] for r in by_src}}


def _search(q_str):
    sql = "SELECT * FROM opp WHERE title LIKE ? OR desc LIKE ? OR skills LIKE ? ORDER BY reward DESC LIMIT 20"
    p = [f"%{q_str}%"] * 3
    return q(sql, tuple(p))


def _obs(eid):
    return q("SELECT * FROM obs WHERE entity_id=? ORDER BY observed", (eid,))
