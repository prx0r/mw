"""Comprehensive data import from all sources."""
from __future__ import annotations

import json
import time
import urllib.request
from typing import Any


def _get(url: str, headers: dict = None) -> Any:
    try:
        h = {"Accept": "application/json", "User-Agent": "MoltworkOracle/1.0"}
        if headers: h.update(headers)
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def import_all():
    """Import data from all sources."""
    from oracle.store import upsert_opp, upsert_svc, q
    
    print("=== Importing all data sources ===")
    
    # 1. Work sources
    print("\n[WORK SOURCES]")
    _import_bountybook()
    _import_github()
    _import_superteam()
    _import_agenthansa()
    _import_daydreams()
    
    # 2. Service sources
    print("\n[SERVICE SOURCES]")
    _import_apify()
    _import_the402()
    _import_smithery()
    _import_mcp_registry()
    
    # 3. Signal sources
    print("\n[SIGNAL SOURCES]")
    _import_openrouter()
    _import_npm()
    _import_huggingface()
    _import_bittensor()
    
    # 4. Export to R2
    print("\n[EXPORT TO R2]")
    _export_to_r2()
    
    print("\n=== Import complete ===")


def _import_bountybook():
    """Import BountyBook bounties."""
    data = _get("https://api.bountybook.ai/jobs?limit=100")
    if not data:
        print("  BountyBook: no data")
        return
    jobs = data.get("jobs", [])
    count = 0
    for j in jobs:
        try:
            reward = j.get("budget_usdc", 0) or j.get("budget", 0) or j.get("reward", 0) or j.get("maxReward", 0)
            if isinstance(reward, str):
                reward = float(reward.replace("$","").replace(",","") or 0)
            
            item = {
                "id": f"bountybook:{j.get('id','')}",
                "src": "bountybook",
                "title": j.get("title",""),
                "desc": (j.get("description","") or "")[:500],
                "url": j.get("url", j.get("jobUrl","")),
                "cat": j.get("job_type", j.get("category","")),
                "skills": j.get("tags", j.get("skills",[])),
                "reward": reward,
                "currency": "USDC",
                "status": "open",
            }
            upsert_opp(item)
            count += 1
        except Exception as e:
            pass
    print(f"  BountyBook: {count} items")


def _import_github():
    """Import GitHub bounties."""
    import os
    token = os.environ.get("GITHUB_TOKEN","")
    h = {"Accept": "application/vnd.github.v3+json"}
    if token: h["Authorization"] = f"token {token}"
    
    try:
        req = urllib.request.Request(
            "https://api.github.com/search/issues?q=label:bounty+is:open+is:issue&per_page=100",
            headers=h)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except: data = None
    
    if not data:
        print("  GitHub: no data")
        return
    
    count = 0
    for item in data.get("items", [])[:100]:
        labels = [l.get("name","") for l in item.get("labels",[])]
        reward = 0
        for l in labels:
            if "$" in l:
                try: reward = float(l.replace("$","").replace(",",""))
                except: pass
        
        try:
            upsert_opp({
                "id": f"github:{item.get('repository_url','').split('/')[-1]}#{item.get('number','')}",
                "src": "github",
                "title": item.get("title",""),
                "desc": (item.get("body","") or "")[:500],
                "url": item.get("html_url",""),
                "cat": "development",
                "skills": [l for l in labels if l not in ["bounty","paid"]],
                "reward": reward,
                "currency": "USD",
                "status": "open",
            })
            count += 1
        except: pass
    print(f"  GitHub: {count} items")


def _import_superteam():
    """Import SuperTeam bounties."""
    data = _get("https://superteam.fun/api/listings")
    if not data:
        print("  SuperTeam: no data")
        return
    
    listings = data if isinstance(data, list) else data.get("listings", data.get("data", []))
    count = 0
    for l in listings:
        try:
            reward = l.get("rewardAmount", l.get("reward", 0))
            if isinstance(reward, str):
                reward = float(reward.replace("$","").replace(",","") or 0)
            
            upsert_opp({
                "id": f"superteam:{l.get('id','')}",
                "src": "superteam",
                "title": l.get("title",""),
                "desc": (l.get("description","") or "")[:500],
                "url": f"https://superteam.fun/earn/{l.get('slug','')}",
                "cat": l.get("type",""),
                "skills": l.get("skills", l.get("tags",[])),
                "reward": reward,
                "currency": l.get("token","USD"),
                "status": "open",
            })
            count += 1
        except: pass
    print(f"  SuperTeam: {count} items")


def _import_agenthansa():
    """Import AgentHansa bounties."""
    data = _get("https://agenthansa.com/api/collective/bounties/public")
    if not data:
        print("  AgentHansa: no data")
        return
    
    bounties = data if isinstance(data, list) else data.get("bounties", data.get("data", []))
    count = 0
    for b in bounties:
        try:
            upsert_opp({
                "id": f"agenthansa:{b.get('id','')}",
                "src": "agenthansa",
                "title": b.get("title",""),
                "desc": (b.get("description","") or "")[:500],
                "url": b.get("url",""),
                "cat": b.get("category",""),
                "skills": b.get("tags",[]),
                "reward": b.get("reward",0),
                "currency": b.get("currency","USD"),
                "status": "open",
            })
            count += 1
        except: pass
    print(f"  AgentHansa: {count} items")


def _import_daydreams():
    """Import Daydreams tasks."""
    data = _get("https://taskmarket.dev/api/tasks")
    if not data:
        print("  Daydreams: no data")
        return
    
    tasks = data if isinstance(data, list) else data.get("tasks", data.get("data", []))
    count = 0
    for t in tasks:
        try:
            reward = t.get("reward", 0)
            if isinstance(reward, str):
                reward = float(reward.replace("$","").replace(",","") or 0)
            
            upsert_opp({
                "id": f"daydreams:{t.get('id','')}",
                "src": "daydreams",
                "title": t.get("title",""),
                "desc": (t.get("description","") or "")[:500],
                "url": t.get("url",""),
                "cat": t.get("category",""),
                "skills": t.get("tags",[]),
                "reward": reward,
                "currency": t.get("currency","USD"),
                "status": "open",
            })
            count += 1
        except: pass
    print(f"  Daydreams: {count} items")


def _import_apify():
    """Import Apify actors."""
    data = _get("https://api.apify.com/v2/store?limit=50")
    if not data:
        print("  Apify: no data")
        return
    
    actors = data.get("data", {}).get("items", [])
    count = 0
    for a in actors:
        try:
            stats = a.get("stats", {})
            total_runs = stats.get("totalRuns", 0) if isinstance(stats, dict) else 0
            
            upsert_svc({
                "id": f"apify:{a.get('id','')}",
                "src": "apify",
                "name": a.get("name",""),
                "desc": (a.get("description","") or "")[:500],
                "url": f"https://apify.com/{a.get('username','')}/{a.get('name','')}",
                "cat": (a.get("categories",[]) or [""])[0] if a.get("categories") else "",
                "price": 0,
                "calls": total_runs,
                "rating": a.get("actorReviewRating",0),
            })
            count += 1
        except: pass
    print(f"  Apify: {count} items")


def _import_the402():
    """Import the402 services."""
    data = _get("https://api.the402.ai/v1/services/catalog")
    if not data:
        print("  the402: no data")
        return
    
    services = data if isinstance(data, list) else data.get("services", data.get("data", []))
    count = 0
    for s in services:
        try:
            upsert_svc({
                "id": f"the402:{s.get('id','')}",
                "src": "the402",
                "name": s.get("name",""),
                "desc": (s.get("description","") or "")[:500],
                "url": s.get("url",""),
                "cat": s.get("category",""),
                "price": s.get("price",0),
                "calls": s.get("calls",0),
                "rating": s.get("rating",0),
            })
            count += 1
        except: pass
    print(f"  the402: {count} items")


def _import_smithery():
    """Import Smithery MCP servers."""
    data = _get("https://api.smithery.ai/servers?limit=100")
    if not data:
        print("  Smithery: no data")
        return
    
    servers = data if isinstance(data, list) else data.get("servers", data.get("data", []))
    count = 0
    for s in servers:
        try:
            upsert_svc({
                "id": f"smithery:{s.get('qualifiedName', s.get('id',''))}",
                "src": "smithery",
                "name": s.get("qualifiedName", s.get("name","")),
                "desc": (s.get("description","") or "")[:500],
                "url": s.get("url",""),
                "cat": s.get("category",""),
                "price": 0,
                "calls": s.get("useCount",0),
                "rating": 0,
            })
            count += 1
        except: pass
    print(f"  Smithery: {count} items")


def _import_mcp_registry():
    """Import MCP Registry servers."""
    data = _get("https://registry.modelcontextprotocol.io/v0.1/servers?limit=100")
    if not data:
        print("  MCP Registry: no data")
        return
    
    servers = data if isinstance(data, list) else data.get("servers", data.get("data", []))
    count = 0
    for s in servers:
        try:
            upsert_svc({
                "id": f"mcp:{s.get('id','')}",
                "src": "mcp_registry",
                "name": s.get("name",""),
                "desc": (s.get("description","") or "")[:500],
                "url": s.get("url", s.get("homepage","")),
                "cat": s.get("category",""),
                "price": 0,
                "calls": 0,
                "rating": 0,
            })
            count += 1
        except: pass
    print(f"  MCP Registry: {count} items")


def _import_openrouter():
    """Import OpenRouter models."""
    data = _get("https://openrouter.ai/api/v1/models")
    if not data:
        print("  OpenRouter: no data")
        return
    
    models = data.get("data", [])
    count = 0
    for m in models:
        try:
            pricing = m.get("pricing", {})
            prompt_price = float(pricing.get("prompt", "0") or "0")
            
            upsert_svc({
                "id": f"openrouter:{m.get('id','')}",
                "src": "openrouter",
                "name": m.get("name",""),
                "desc": (m.get("description","") or "")[:500],
                "url": f"https://openrouter.ai/{m.get('id','')}",
                "cat": "llm",
                "price": prompt_price * 1000000,  # per 1M tokens
                "calls": 0,
                "rating": 0,
            })
            count += 1
        except: pass
    print(f"  OpenRouter: {count} items")


def _import_npm():
    """Import npm package downloads."""
    from oracle.store import conn
    
    pkgs = ["@modelcontextprotocol/sdk", "langchain", "crewai", "bittensor", 
            "openai", "anthropic", "ai", "llamaindex", "autogpt", "swarm"]
    
    c = conn()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    count = 0
    for pkg in pkgs:
        data = _get(f"https://api.npmjs.org/downloads/point/last-week/{pkg}")
        if data:
            try:
                c.execute("""INSERT OR REPLACE INTO sig (id, src, metric, value, observed, extra)
                    VALUES (?,?,?,?,?,?)""",
                    (f"npm:{pkg}", "npm", f"downloads:{pkg}",
                     json.dumps(data.get("downloads",0)), now, json.dumps(data)))
                count += 1
            except: pass
    c.commit(); c.close()
    print(f"  npm: {count} packages")


def _import_huggingface():
    """Import HuggingFace model downloads."""
    from oracle.store import conn
    
    data = _get("https://huggingface.co/api/models?limit=20&sort=downloads&direction=-1")
    if not data:
        print("  HuggingFace: no data")
        return
    
    c = conn()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    count = 0
    for m in data:
        try:
            c.execute("""INSERT OR REPLACE INTO sig (id, src, metric, value, observed, extra)
                VALUES (?,?,?,?,?,?)""",
                (f"hf:{m.get('id','')}", "hf", f"downloads:{m.get('id','')}",
                 json.dumps(m.get("downloads",0)), now, json.dumps({"tags": m.get("tags",[])})))
            count += 1
        except: pass
    c.commit(); c.close()
    print(f"  HuggingFace: {count} models")


def _import_bittensor():
    """Import Bittensor subnet data."""
    from oracle.store import conn
    
    # Get TAO price
    price_data = _get("https://coins.llama.fi/prices/current/coingecko:bittensor")
    tao_price = 0
    if price_data:
        coins = price_data.get("coins", {})
        tao_price = coins.get("coingecko:bittensor", {}).get("price", 0)
    
    # Get subnets
    data = _get("https://api.metagraph.sh/api/v1/subnets")
    if not data:
        print("  Bittensor: no data")
        return
    
    subnets = data.get("data", {}).get("subnets", []) if isinstance(data, dict) else []
    c = conn()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    count = 0
    for s in subnets:
        try:
            netuid = s.get("netuid", s.get("id", 0))
            emission = s.get("emission_pct", s.get("emission", 0))
            daily_usd = emission * tao_price * 7200 / 100  # rough estimate
            
            c.execute("""INSERT OR REPLACE INTO sub
                (id, netuid, name, emission, miners, validators, tao_price, status, extra, first_seen, last_seen)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (f"bittensor:sn{netuid}", netuid, s.get("name", f"SN{netuid}"),
                 emission, s.get("miners",0), s.get("validators",0),
                 tao_price, "active", json.dumps({"daily_usd": daily_usd}),
                 now, now))
            count += 1
        except: pass
    c.commit(); c.close()
    print(f"  Bittensor: {count} subnets (TAO ${tao_price:.2f})")


def _export_to_r2():
    """Export canonical opportunities to R2 for the worker."""
    import boto3
    from oracle.store import q
    
    opps = q("""
        SELECT o.id, o.canonical_title as title, o.canonical_description as desc,
               o.market_id, o.status, o.execution_mode, o.reward_usd, o.reward_currency,
               o.canonical_url as url, o.first_seen_at, o.last_seen_at,
               GROUP_CONCAT(s.slug) as skill_list
        FROM oracle_opps o
        LEFT JOIN oracle_opp_skills os ON o.id = os.opportunity_id
        LEFT JOIN oracle_skills s ON os.skill_id = s.id
        GROUP BY o.id
    """)
    
    for o in opps:
        o['skills'] = (o.get('skill_list') or '').split(',') if o.get('skill_list') else []
    
    try:
        s3 = boto3.client('s3',
            endpoint_url='https://954612afb5a97bb15dddcdc70176813d.r2.cloudflarestorage.com',
            aws_access_key_id='a963808d8055d84d5fcb3505e202516f',
            aws_secret_access_key='956d78a15121527925fee5ebc7325902bd222b6e3653c42f1cf0a4cddc8063ce',
            region_name='auto'
        )
        s3.put_object(
            Bucket='qdw',
            Key='oracle/opps.json',
            Body=json.dumps(opps),
            ContentType='application/json'
        )
        print(f"  Exported {len(opps)} opportunities to R2")
    except Exception as e:
        print(f"  R2 export error: {e}")


if __name__ == "__main__":
    import_all()
