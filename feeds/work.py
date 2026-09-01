"""Work feed — bounties/tasks/jobs."""
from __future__ import annotations

import json
import time
import urllib.request
from typing import Any


def _get(url: str) -> Any:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except:
        return None


def bountybook() -> list[dict]:
    data = _get("https://api.bountybook.ai/jobs?limit=100")
    if not data: return []
    return [_norm_bountybook(j) for j in data.get("jobs", [])]


def github(token: str = "") -> list[dict]:
    h = {"Accept": "application/vnd.github.v3+json"}
    if token: h["Authorization"] = f"token {token}"
    try:
        req = urllib.request.Request(
            "https://api.github.com/search/issues?q=label:bounty+is:open+is:issue&per_page=100",
            headers=h)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return [_norm_github(i) for i in data.get("items", [])]
    except: return []


def superteam() -> list[dict]:
    data = _get("https://superteam.fun/api/listings?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("listings", [])
    return [_norm_superteam(b) for b in items]


def agenthansa() -> list[dict]:
    data = _get("https://www.agenthansa.com/api/collective/bounties/public?limit=100")
    if not data: return []
    return [_norm_agenthansa(b) for b in data.get("bounties", [])]


def rentahuman() -> list[dict]:
    data = _get("https://rentahuman.ai/api/bounties?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("bounties", [])
    return [_norm_rentahuman(b) for b in items]


def daydreams() -> list[dict]:
    data = _get("https://taskmarket.dev/api/tasks?limit=100")
    if not data: return []
    return [_norm_daydreams(t) for t in data.get("tasks", [])]


def openserv() -> list[dict]:
    data = _get("https://api.launch.openserv.ai/ideas?limit=100")
    if not data: return []
    return [_norm_openserv(i) for i in data.get("ideas", [])]


def _norm_bountybook(j: dict) -> dict:
    b = j.get("budget_usdc", 0)
    if isinstance(b, str):
        try: b = float(b.replace("$",""))
        except: b = 0
    return {"id": f"bb:{j.get('id','')}", "src": "bountybook", "source_id": str(j.get("id","")),
            "title": j.get("title",""), "desc": (j.get("description") or "")[:500],
            "cat": j.get("job_type","general"), "skills": j.get("tags",[]),
            "reward": float(b), "currency": "USDC", "status": j.get("status","open"),
            "posted": j.get("created_at",""), "url": f"https://bountybook.ai/job/{j.get('id','')}",
            "extra": {"difficulty": j.get("difficulty",""), "network": "base"}}


def _norm_github(i: dict) -> dict:
    amt = 0
    text = f"{i.get('title','')} {i.get('body','')[:500]}"
    for p in [r'\$(\d+(?:,\d{3})*)\b', r'Bounty:\s*\$(\d+)']:
        m = re.search(p, text)
        if m:
            try: amt = float(m.group(1).replace(",",""))
            except: pass
            break
    return {"id": f"gh:{i.get('html_url','').split('/')[-1]}", "src": "github",
            "source_id": str(i.get("number","")), "title": i.get("title",""),
            "desc": (i.get("body") or "")[:500], "cat": "development", "skills": [],
            "reward": amt, "currency": "USD", "status": "open" if i.get("state")=="open" else "closed",
            "posted": i.get("created_at",""), "url": i.get("html_url",""),
            "extra": {"repo": i.get("repository_url","").split("/")[-2:]}}


def _norm_superteam(b: dict) -> dict:
    r = b.get("rewardAmount", 0) or 0
    return {"id": f"st:{b.get('id','')}", "src": "superteam", "source_id": str(b.get("id","")),
            "title": b.get("title",""), "desc": (b.get("description") or "")[:500],
            "cat": b.get("type","bounty"), "skills": [], "reward": float(r),
            "currency": b.get("token","USDG"), "status": b.get("status","OPEN"),
            "posted": b.get("createdAt",""), "url": f"https://superteam.fun/earn/{b.get('slug','')}",
            "extra": {"agent_access": b.get("agentAccess",""), "deadline": b.get("deadline","")}}


def _norm_agenthansa(b: dict) -> dict:
    r = b.get("reward_amount", 0) or 0
    return {"id": f"ah:{b.get('id','')}", "src": "agenthansa", "source_id": str(b.get("id","")),
            "title": b.get("title",""), "desc": (b.get("description") or "")[:500],
            "cat": b.get("category","general"), "skills": b.get("tags",[]),
            "reward": float(r), "currency": b.get("currency","points"),
            "status": b.get("status","open"), "posted": b.get("created_at",""),
            "url": f"https://agenthansa.com/bounty/{b.get('id','')}",
            "extra": {"deadline": b.get("deadline","")}}


def _norm_rentahuman(b: dict) -> dict:
    p = b.get("price", 0)
    if isinstance(p, str):
        try: p = float(p.replace("$",""))
        except: p = 0
    return {"id": f"rh:{b.get('id','')}", "src": "rentahuman", "source_id": str(b.get("id","")),
            "title": b.get("title",""), "desc": (b.get("description") or "")[:500],
            "cat": b.get("category","general"), "skills": b.get("skillsNeeded",[]),
            "reward": float(p), "currency": b.get("currency","USD"),
            "status": b.get("status","open"), "posted": b.get("createdAt",""),
            "url": f"https://rentahuman.ai/bounty/{b.get('id','')}",
            "extra": {"location": b.get("location","")}}


def _norm_daydreams(t: dict) -> dict:
    r = t.get("reward", 0) or 0
    if isinstance(r, str):
        try: r = float(r)
        except: r = 0
    r_usd = r / 1_000_000 if r > 1000 else r
    return {"id": f"dd:{str(t.get('id',''))[:20]}", "src": "daydreams",
            "source_id": str(t.get("id",""))[:20],
            "title": (t.get("description") or "")[:100],
            "desc": (t.get("description") or "")[:500],
            "cat": t.get("tags",["general"])[0] if t.get("tags") else "general",
            "skills": t.get("tags",[]), "reward": round(r_usd,6),
            "currency": "USDC", "status": t.get("status","open"),
            "posted": t.get("createdAt",""), "url": f"https://taskmarket.dev/task/{t.get('id','')}",
            "extra": {"network": "base"}}


def _norm_openserv(i: dict) -> dict:
    ups = len(i.get("upvotes",[]))
    picks = len(i.get("pickups",[]))
    ships = len(i.get("shipments",[]))
    return {"id": f"os:{i.get('id','')}", "src": "openserv", "source_id": str(i.get("id","")),
            "title": i.get("title",""), "desc": (i.get("description") or "")[:500],
            "cat": i.get("tags",["general"])[0] if i.get("tags") else "general",
            "skills": i.get("tags",[]), "reward": 0, "currency": "x402",
            "status": "open", "posted": i.get("createdAt",""),
            "url": f"https://openserv.ai/idea/{i.get('id','')}",
            "extra": {"upvotes": ups, "pickups": picks, "shipments": ships}}


# ─── Additional work sources ─────────────────────────────────────────

def nearai() -> list[dict]:
    """NEAR AI agent.market — agent services and tasks."""
    data = _get("https://market.near.ai/v1/agents?limit=100")
    if not data: return []
    items = data.get("agents", []) if isinstance(data, dict) else data
    return [_norm_nearai(a) for a in items]


def _norm_nearai(a: dict) -> dict:
    jobs = a.get("delivered_jobs", 0)
    rate = a.get("success_rate", 0)
    return {"id": f"near:{a.get('agent_id','')}", "src": "nearai", "source_id": str(a.get("agent_id","")),
            "title": a.get("name", a.get("handle","")), "desc": (a.get("description","") or "")[:500],
            "cat": a.get("category","general"), "skills": a.get("tags",[]),
            "reward": 0, "currency": "NEAR", "status": a.get("listing_status","live"),
            "posted": a.get("created_at",""), "url": f"https://market.near.ai/agent/{a.get('handle','')}",
            "extra": {"network": "near", "delivered_jobs": jobs, "success_rate": rate,
                      "runtime": a.get("runtime",""), "handle": a.get("handle","")}}


def agentlux() -> list[dict]:
    """AgentLux — agent marketplace tasks."""
    data = _get("https://agentlux.ai/api/tasks?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("tasks", [])
    return [_norm_agentlux(t) for t in items]


def _norm_agentlux(t: dict) -> dict:
    reward = 0
    r = t.get("reward", t.get("price", 0))
    if isinstance(r, (int, float)): reward = float(r)
    elif isinstance(r, str):
        try: reward = float(r.replace("$",""))
        except: pass
    return {"id": f"alx:{t.get('id','')}", "src": "agentlux", "source_id": str(t.get("id","")),
            "title": t.get("title",""), "desc": (t.get("description","") or "")[:500],
            "cat": t.get("category","general"), "skills": t.get("tags", t.get("skills",[])),
            "reward": reward, "currency": t.get("currency","USD"),
            "status": t.get("status","open"), "posted": t.get("created_at",""),
            "url": f"https://agentlux.ai/task/{t.get('id','')}",
            "extra": {}}


def augmi() -> list[dict]:
    """Augmi Marketplace — agent gigs."""
    data = _get("https://augmi.world/api/gigs?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("gigs", [])
    return [_norm_augmi(g) for g in items]


def _norm_augmi(g: dict) -> dict:
    reward = 0
    r = g.get("reward", g.get("budget", 0))
    if isinstance(r, (int, float)): reward = float(r)
    elif isinstance(r, str):
        try: reward = float(r.replace("$",""))
        except: pass
    return {"id": f"aug:{g.get('id','')}", "src": "augmi", "source_id": str(g.get("id","")),
            "title": g.get("title",""), "desc": (g.get("description","") or "")[:500],
            "cat": g.get("category","general"), "skills": g.get("tags",[]),
            "reward": reward, "currency": g.get("currency","USD"),
            "status": g.get("status","open"), "posted": g.get("created_at",""),
            "url": f"https://augmi.world/gig/{g.get('id','')}",
            "extra": {}}


def agentworld() -> list[dict]:
    """AgentWorld — agent task board."""
    data = _get("https://agentworld.me/api/tasks?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("tasks", [])
    return [_norm_agentworld(t) for t in items]


def _norm_agentworld(t: dict) -> dict:
    reward = 0
    r = t.get("reward", t.get("payment", 0))
    if isinstance(r, (int, float)): reward = float(r)
    elif isinstance(r, str):
        try: reward = float(r.replace("$",""))
        except: pass
    return {"id": f"aw:{t.get('id','')}", "src": "agentworld", "source_id": str(t.get("id","")),
            "title": t.get("title",""), "desc": (t.get("description","") or "")[:500],
            "cat": t.get("category","general"), "skills": t.get("tags",[]),
            "reward": reward, "currency": t.get("currency","USD"),
            "status": t.get("status","open"), "posted": t.get("created_at",""),
            "url": f"https://agentworld.me/task/{t.get('id','')}",
            "extra": {}}


def atelier() -> list[dict]:
    """Atelier — agent marketplace."""
    data = _get("https://useatelier.ai/api/tasks?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("tasks", [])
    return [_norm_atelier(t) for t in items]


def _norm_atelier(t: dict) -> dict:
    reward = 0
    r = t.get("reward", t.get("price", 0))
    if isinstance(r, (int, float)): reward = float(r)
    elif isinstance(r, str):
        try: reward = float(r.replace("$",""))
        except: pass
    return {"id": f"atl:{t.get('id','')}", "src": "atelier", "source_id": str(t.get("id","")),
            "title": t.get("title",""), "desc": (t.get("description","") or "")[:500],
            "cat": t.get("category","general"), "skills": t.get("tags",[]),
            "reward": reward, "currency": t.get("currency","USD"),
            "status": t.get("status","open"), "posted": t.get("created_at",""),
            "url": f"https://useatelier.ai/task/{t.get('id','')}",
            "extra": {}}


def clustly() -> list[dict]:
    """Clustly — agent gigs."""
    data = _get("https://clustly.ai/api/gigs?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("gigs", [])
    return [_norm_clustly(g) for g in items]


def _norm_clustly(g: dict) -> dict:
    reward = 0
    r = g.get("reward", g.get("budget", 0))
    if isinstance(r, (int, float)): reward = float(r)
    elif isinstance(r, str):
        try: reward = float(r.replace("$",""))
        except: pass
    return {"id": f"clu:{g.get('id','')}", "src": "clustly", "source_id": str(g.get("id","")),
            "title": g.get("title",""), "desc": (g.get("description","") or "")[:500],
            "cat": g.get("category","general"), "skills": g.get("tags",[]),
            "reward": reward, "currency": g.get("currency","USD"),
            "status": g.get("status","open"), "posted": g.get("created_at",""),
            "url": f"https://clustly.ai/gig/{g.get('id','')}",
            "extra": {}}


def taskforce() -> list[dict]:
    """TaskForce — Upwork for AI agents."""
    data = _get("https://www.task-force.app/api/tasks?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("tasks", [])
    return [_norm_taskforce(t) for t in items]


def _norm_taskforce(t: dict) -> dict:
    reward = 0
    r = t.get("reward", t.get("budget", 0))
    if isinstance(r, (int, float)): reward = float(r)
    elif isinstance(r, str):
        try: reward = float(r.replace("$",""))
        except: pass
    return {"id": f"tf:{t.get('id','')}", "src": "taskforce", "source_id": str(t.get("id","")),
            "title": t.get("title",""), "desc": (t.get("description","") or "")[:500],
            "cat": t.get("category","general"), "skills": t.get("tags", t.get("skills",[])),
            "reward": reward, "currency": t.get("currency","USDC"),
            "status": t.get("status","open"), "posted": t.get("created_at",""),
            "url": f"https://www.task-force.app/task/{t.get('id','')}",
            "extra": {"escrow": t.get("escrow_type", "milestone")}}


def moltjobs() -> list[dict]:
    """MoltJobs — agent job board with escrow."""
    data = _get("https://moltjobs.io/api/jobs?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("jobs", [])
    return [_norm_moltjobs(j) for j in items]


def _norm_moltjobs(j: dict) -> dict:
    reward = 0
    r = j.get("reward", j.get("budget", 0))
    if isinstance(r, (int, float)): reward = float(r)
    elif isinstance(r, str):
        try: reward = float(r.replace("$",""))
        except: pass
    return {"id": f"mj:{j.get('id','')}", "src": "moltjobs", "source_id": str(j.get("id","")),
            "title": j.get("title",""), "desc": (j.get("description","") or "")[:500],
            "cat": j.get("category","general"), "skills": j.get("tags", j.get("skills",[])),
            "reward": reward, "currency": j.get("currency","USDC"),
            "status": j.get("status","open"), "posted": j.get("created_at",""),
            "url": f"https://moltjobs.io/job/{j.get('id','')}",
            "extra": {"escrow": j.get("escrow_type", "base")}}


def metaculus(token: str = "") -> list[dict]:
    """Metaculus — forecasting tournament questions.

    Fetches open binary questions as opportunities.
    Each question is a forecasting task with community prediction,
    tournament affiliation, and eventual resolution.
    """
    if not token:
        import os
        token = os.environ.get("METACULUS_API_KEY", "")
    if not token:
        return []

    import urllib.request
    base = "https://www.metaculus.com/api2"
    headers = {
        "Authorization": f"Token {token}",
        "Accept": "application/json",
        "User-Agent": "MoltworkOracle/1.0",
    }

    items = []
    for status in ["open", "closed"]:
        url = f"{base}/questions/?limit=50&type=binary&status={status}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                for q in data.get("results", []):
                    items.append(_norm_metaculus(q))
        except:
            pass

    return items


def _norm_metaculus(q: dict) -> dict:
    """Normalize a Metaculus question to Oracle opportunity schema."""
    qtype = q.get("question", {}).get("type", "binary")
    status = q.get("status", "open")
    resolved = q.get("resolved", False)
    resolution = q.get("question", {}).get("resolution")

    # Map status
    if resolved and resolution is not None:
        opp_status = "resolved"
    elif status == "closed":
        opp_status = "closed"
    elif status in ("open", "approved"):
        opp_status = "open"
    else:
        opp_status = status

    # Extract tournament info
    projects = q.get("projects", {})
    tournaments = []
    for ptype in ("leaderboard_tag", "site_main"):
        for p in projects.get(ptype, []):
            tournaments.append(p.get("name", ""))

    # Community prediction
    cp = q.get("question", {}).get("aggregations", {}).get("unweighted", {}).get("latest")
    if cp and isinstance(cp, dict):
        cp = cp.get("probability", cp.get("expected_value"))

    # Skills from question type + content
    skills = ["forecasting", f"forecasting.{qtype}"]
    if any("AI" in (q.get("title","") or "") for _ in [1]):
        skills.append("forecasting.ai")
    if any("economy" in (q.get("title","") or "").lower() for _ in [1]):
        skills.append("forecasting.economics")

    # Reward: not directly monetary, but tournament prize pool share
    reward = 0  # Metaculus rewards are indirect (tournament prizes)

    # Description from question body
    desc = q.get("description", "") or ""
    if not desc:
        desc = q.get("title", "")

    return {
        "id": f"mc:{q.get('id','')}",
        "src": "metaculus",
        "source_id": str(q.get("id", "")),
        "title": q.get("title", ""),
        "desc": desc[:500],
        "cat": f"forecasting.{qtype}",
        "skills": skills,
        "reward": reward,
        "currency": "USD",
        "status": opp_status,
        "posted": q.get("published_at", ""),
        "url": f"https://www.metaculus.com/questions/{q.get('id','')}/",
        "extra": {
            "question_type": qtype,
            "community_prediction": cp,
            "nr_forecasters": q.get("nr_forecasters", 0),
            "forecasts_count": q.get("forecasts_count", 0),
            "tournaments": tournaments,
            "close_time": q.get("actual_close_time") or q.get("scheduled_close_time"),
            "resolve_time": q.get("actual_resolve_time") or q.get("scheduled_resolve_time"),
            "resolution": resolution,
            "resolved": resolved,
        },
    }


# ─── Security Feeds ──────────────────────────────────────────────────

def immunefi() -> list[dict]:
    """Immunefi bug bounties and competitions."""
    data = _get("https://immunefi.com/api/bounties")
    if not data:
        # Fallback: try their public listing
        data = _get("https://immunefi.com/bounties/")
        if not data:
            return []
    items = data if isinstance(data, list) else data.get("bounties", [])
    return [_norm_immunefi(b) for b in items]


def _norm_immunefi(b: dict) -> dict:
    title = b.get("title") or b.get("name", "")
    reward_max = b.get("max_reward") or b.get("reward", 0)
    if isinstance(reward_max, str):
        reward_max = float(reward_max.replace("$", "").replace(",", "") or 0)

    # Determine type
    btype = b.get("type", "")
    if "competition" in btype.lower() or "contest" in btype.lower():
        cat = "security.code_contest"
    else:
        cat = "security.live_bounty"

    return {
        "id": f"immunefi:{b.get('id', b.get('slug', title[:30]))}",
        "src": "immunefi",
        "source_id": str(b.get("id", "")),
        "title": title,
        "desc": (b.get("description", "") or b.get("scope", ""))[:500],
        "cat": cat,
        "skills": ["security", "smart-contract", "solidity", "code-audit"],
        "reward": float(reward_max),
        "currency": "USD",
        "status": "open",
        "posted": b.get("created_at", b.get("published_at", "")),
        "url": b.get("url", f"https://immunefi.com/bounty/{b.get('slug', '')}/"),
        "extra": {
            "platform": "immunefi",
            "bounty_type": btype,
            "protocols": b.get("protocols", []),
            "max_reward_usd": float(reward_max),
            "school": "code-audit",
            "pool": "security",
        },
    }


def github_security_advisories(token: str = "") -> list[dict]:
    """GitHub Security Advisories (public API, no auth needed for range query)."""
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"token {token}"
    try:
        req = urllib.request.Request(
            "https://api.github.com/advisories?per_page=50&sort=published&direction=desc",
            headers=h)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return [_norm_github_adv(a) for a in data]
    except:
        return []


def _norm_github_adv(a: dict) -> dict:
    severity = a.get("severity", "unknown")
    cve = a.get("cve_id", "")
    desc = a.get("description", "") or a.get("summary", "")

    # Extract ecosystem from vulnerabilities
    ecosystems = set()
    for v in a.get("vulnerabilities", []):
        pkg = v.get("package", {})
        eco = pkg.get("ecosystem", "")
        if eco:
            ecosystems.add(eco.lower())

    skills = ["security", "oss", "vulnerability"]
    for eco in ecosystems:
        if eco in ("npm", "pypi", "cargo", "go", "maven"):
            skills.append(f"security.{eco}")

    return {
        "id": f"ghsa:{a.get('ghsa_id', cve)}",
        "src": "github_security",
        "source_id": a.get("ghsa_id", cve),
        "title": f"{cve}: {a.get('summary', 'Security advisory')}" if cve else a.get("summary", ""),
        "desc": desc[:500],
        "cat": "security.oss_reward",
        "skills": skills,
        "reward": 0,  # GitHub doesn't pay directly, but OEMs do
        "currency": "USD",
        "status": "published",
        "posted": a.get("published_at", ""),
        "url": a.get("html_url", ""),
        "extra": {
            "platform": "github",
            "severity": severity,
            "cve_id": cve,
            "cvss_score": a.get("cvss", {}).get("score", 0) if isinstance(a.get("cvss"), dict) else 0,
            "ecosystems": list(ecosystems),
            "patched_versions": [v.get("patched_version", "") for v in a.get("vulnerabilities", [])],
            "school": "code-audit",
            "pool": "security",
        },
    }


def hackerone_programs() -> list[dict]:
    """HackerOne public program listings."""
    # HackerOne public API is limited, but their directory is scrapable
    data = _get("https://api.hackerone.com/v1/hackers/programs")
    if not data:
        return []
    items = data if isinstance(data, list) else data.get("data", [])
    return [_norm_hackerone(p) for p in items]


def _norm_hackerone(p: dict) -> dict:
    attrs = p.get("attributes", p)
    name = attrs.get("name", "")
    offer_bounties = attrs.get("offers_bounties", False)
    offers_swag = attrs.get("offers_swag", False)

    # Filter to security-relevant programs
    if not (offer_bounties or offers_swag):
        return None

    # Determine category
    offers_ai = any(kw in name.lower() for kw in ["ai", "llm", "agent", "rag", "ml"])
    cat = "security.ai_redteam" if offers_ai else "security.triage"

    skills = ["security"]
    if offers_ai:
        skills.extend(["security.ai", "ai-security"])

    result = {
        "id": f"h1:{p.get('id', name[:30])}",
        "src": "hackerone",
        "source_id": str(p.get("id", "")),
        "title": name,
        "desc": (attrs.get("policy", "") or attrs.get("structured_scope", ""))[:500],
        "cat": cat,
        "skills": skills,
        "reward": 0,
        "currency": "USD",
        "status": "open",
        "posted": "",
        "url": f"https://hackerone.com/{attrs.get('handle', '')}",
        "extra": {
            "platform": "hackerone",
            "offers_bounties": offer_bounties,
            "offers_swag": offers_swag,
            "offers_ai_program": offers_ai,
            "school": "ai-redteam" if offers_ai else "code-audit",
            "pool": "security",
        },
    }
    return result


# Filter out None values from security feeds
def _filter_none(items: list) -> list:
    return [i for i in items if i is not None]
