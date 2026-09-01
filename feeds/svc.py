"""Service feed — tools/APIs/capabilities."""
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
    except: return None


def x402engine() -> list[dict]:
    data = _get("https://x402engine.app/api/services?limit=200")
    if not data: return []
    items = data if isinstance(data, list) else data.get("services", [])
    return [_norm_x402(s) for s in items]


def x402list() -> list[dict]:
    data = _get("https://x402-list.com/api/v1/services?per_page=100")
    if not data: return []
    items = data.get("data", []) if isinstance(data, dict) else data
    return [_norm_x402list(s) for s in items]


def the402() -> list[dict]:
    data = _get("https://api.the402.ai/v1/services/catalog?limit=100")
    if not data: return []
    return [_norm_the402(s) for s in data.get("services", [])]


def payapi() -> list[dict]:
    data = _get("https://payapi.market/agent/list?limit=100")
    if not data: return []
    items = data.get("results", []) if isinstance(data, dict) else data
    return [_norm_payapi(s) for s in items]


def apify() -> list[dict]:
    items = []
    for q in ["scraper", "browser", "data", "ai", "automation"]:
        data = _get(f"https://api.apify.com/v2/store?q={q}&limit=20")
        if data:
            store = data.get("data", {})
            actors = store.get("items", []) if isinstance(store, dict) else []
            for a in actors:
                name = a.get("name", "")
                if name and not any(x["src_id"] == name for x in items):
                    items.append(_norm_apify(a))
    return items


def smithery() -> list[dict]:
    data = _get("https://api.smithery.ai/servers?limit=100")
    if not data: return []
    servers = data.get("servers", [])
    return [_norm_smithery(s) for s in servers]


def openrouter() -> list[dict]:
    data = _get("https://openrouter.ai/api/v1/models?limit=50")
    if not data: return []
    return [_norm_openrouter(m) for m in data.get("data", [])]


def bittensor() -> list[dict]:
    """Bittensor subnets via metagraph.sh economics endpoint."""
    data = _get("https://api.metagraph.sh/api/v1/economics")
    if not data: return []
    
    econ = data.get("data", {})
    subnets = econ.get("subnets", [])
    summary = econ.get("summary", {})
    
    # Get TAO price
    price_data = _get("https://coins.llama.fi/prices/current/coingecko:bittensor")
    tao_price = 0
    if price_data:
        coins = price_data.get("coins", {})
        tao_price = coins.get("coingecko:bittensor", {}).get("price", 0)

    return [_norm_bittensor(s, tao_price) for s in subnets]


def _norm_bittensor(s: dict, tao_price: float = 0) -> dict:
    netuid = s.get("netuid", 0)
    emission_share = s.get("emission_share", 0)
    tao_emission = s.get("tao_in_emission_tao", 0)
    daily_usd = round(float(tao_emission) * tao_price * 3600, 2) if tao_emission and tao_price else 0
    alpha_price = s.get("alpha_price_usd", 0)
    return {"id": f"bittensor:sn{netuid}", "src": "bittensor",
            "source_id": f"sn{netuid}", "name": s.get("name", f"SN{netuid}"),
            "desc": (s.get("description") or "")[:500], "cat": "incentive_market",
            "price": daily_usd, "calls": 0, "rating": 0,
            "url": f"https://taostats.io/subnets/{netuid}",
            "extra": {"emission_share": emission_share, "tao_emission": tao_emission,
                     "daily_usd": daily_usd, "tao_price": tao_price,
                     "alpha_price_usd": alpha_price,
                     "miners": s.get("miner_count", 0),
                     "validators": s.get("validator_count", 0),
                     "registration_cost": s.get("registration_cost_tao", 0)}}


def npm(packages: list[str] = None) -> list[dict]:
    if not packages:
        packages = ["@modelcontextprotocol/sdk", "langchain", "crewai", "bittensor", "openai"]
    items = []
    for pkg in packages:
        data = _get(f"https://api.npmjs.org/downloads/point/last-week/{pkg}")
        if data:
            items.append({"id": f"npm:{pkg}", "src": "npm", "source_id": pkg,
                         "name": pkg, "desc": f"npm: {pkg}", "cat": "package",
                         "price": 0, "calls": data.get("downloads",0), "rating": 0,
                         "url": f"https://npmjs.com/package/{pkg}", "extra": {}})
    return items


def hf() -> list[dict]:
    data = _get("https://huggingface.co/api/models?limit=20&sort=downloads&direction=-1")
    if not data: return []
    return [{"id": f"hf:{m.get('id','')}", "src": "hf", "source_id": m.get("id",""),
             "name": m.get("id",""), "desc": (m.get("description") or "")[:500],
             "cat": m.get("pipeline_tag",""), "price": 0, "calls": m.get("downloads",0),
             "rating": m.get("likes",0), "url": f"https://huggingface.co/{m.get('id','')}",
             "extra": {"tags": m.get("tags",[])} } for m in data]


def _norm_x402(s: dict) -> dict:
    p = s.get("price", 0)
    if isinstance(p, str):
        try: p = float(p.replace("$",""))
        except: p = 0
    return {"id": f"x402:{s.get('id',s.get('slug',''))}", "src": "x402engine",
            "source_id": str(s.get("id",s.get("slug",""))), "name": s.get("name",""),
            "desc": (s.get("description") or "")[:500], "cat": s.get("category",""),
            "price": float(p) if p else 0, "calls": s.get("total_calls",0),
            "rating": 0, "url": s.get("url",""), "extra": {"networks": s.get("networks",[])}}


def _norm_x402list(s: dict) -> dict:
    p = s.get("min_price_usd", 0)
    if isinstance(p, str):
        try: p = float(p.replace("$",""))
        except: p = 0
    return {"id": f"x402list:{s.get('slug',s.get('id',''))}", "src": "x402list",
            "source_id": str(s.get("slug",s.get("id",""))), "name": s.get("name",""),
            "desc": (s.get("description") or "")[:500], "cat": s.get("category",""),
            "price": float(p) if p else 0, "calls": 0, "rating": 0,
            "url": s.get("url",""), "extra": {"verified": s.get("verified",False)}}


def _norm_the402(s: dict) -> dict:
    p = s.get("price",{})
    if isinstance(p, dict):
        try: p = float(p.get("fixed","0").replace("$","").replace(",",""))
        except: p = 0
    return {"id": f"the402:{s.get('id','')}", "src": "the402",
            "source_id": str(s.get("id","")), "name": s.get("name",""),
            "desc": (s.get("description") or "")[:500], "cat": s.get("category",""),
            "price": float(p) if p else 0, "calls": s.get("provider_completed_jobs",0),
            "rating": 0, "url": s.get("endpoint",""),
            "extra": {"verification": s.get("provider_verification_tier","")}}


def _norm_payapi(s: dict) -> dict:
    p = s.get("price_min", 0)
    if isinstance(p, str):
        try: p = float(p.replace("$",""))
        except: p = 0
    return {"id": f"payapi:{s.get('slug',s.get('id',''))}", "src": "payapi",
            "source_id": str(s.get("id",s.get("slug",""))), "name": s.get("name",""),
            "desc": (s.get("description") or "")[:500], "cat": s.get("category",""),
            "price": float(p) if p else 0, "calls": 0, "rating": 0,
            "url": s.get("marketplace_url",""), "extra": {"verified": s.get("payment_verified",False)}}


def _norm_apify(a: dict) -> dict:
    stats = a.get("stats", {})
    return {"id": f"apify:{a.get('name','')}", "src": "apify",
            "source_id": a.get("name",""), "name": a.get("title",a.get("name","")),
            "desc": (a.get("description") or "")[:500], "cat": (a.get("categories",[""])[0] if a.get("categories") else ""),
            "price": 0, "calls": stats.get("totalRuns",0), "rating": stats.get("actorReviewRating",0),
            "url": f"https://apify.com/{a.get('username','apify')}/{a.get('name','')}",
            "extra": {"users": stats.get("totalUsers",0), "reviews": stats.get("actorReviewCount",0)}}


def _norm_smithery(s: dict) -> dict:
    return {"id": f"smithery:{s.get('qualifiedName','')}", "src": "smithery",
            "source_id": s.get("qualifiedName",""), "name": s.get("qualifiedName",""),
            "desc": (s.get("description") or "")[:500], "cat": s.get("category",""),
            "price": 0, "calls": s.get("useCount",0), "rating": 0, "url": s.get("homepage",""),
            "extra": {"verified": s.get("verified",False)}}


def _norm_openrouter(m: dict) -> dict:
    p = m.get("pricing",{})
    return {"id": f"or:{m.get('id','')}", "src": "openrouter",
            "source_id": m.get("id",""), "name": m.get("name",""),
            "desc": (m.get("description") or "")[:500], "cat": "llm",
            "price": 0, "calls": 0, "rating": 0, "url": m.get("url",""),
            "extra": {"pricing": p, "context": m.get("context_length",0)}}


def _norm_soon(s: dict) -> dict:
    return {"id": f"so:{s.get('id','')}", "src": "soon",
            "source_id": str(s.get("id","")), "name": s.get("name",""),
            "desc": (s.get("description") or "")[:500], "cat": s.get("category",""),
            "price": 0, "calls": 0, "rating": 0, "url": s.get("url",""), "extra": {}}


# ─── Additional service sources ─────────────────────────────────────

def skyfire() -> list[dict]:
    """Skyfire — AI agent payment network."""
    data = _get("https://skyfire.xyz/api/services?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("services", [])
    return [_norm_skyfire(s) for s in items]


def _norm_skyfire(s: dict) -> dict:
    p = s.get("price", s.get("min_price", 0))
    if isinstance(p, str):
        try: p = float(p.replace("$",""))
        except: p = 0
    return {"id": f"sf:{s.get('id','')}", "src": "skyfire",
            "source_id": str(s.get("id","")), "name": s.get("name",""),
            "desc": (s.get("description","") or "")[:500], "cat": s.get("category",""),
            "price": float(p) if p else 0, "calls": s.get("total_calls",0), "rating": 0,
            "url": s.get("url",""), "extra": {"networks": s.get("networks",[])}}


def apihub() -> list[dict]:
    """APIHub — API marketplace."""
    data = _get("https://apihub.io/api/v1/apis?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("apis", data.get("results", []))
    return [_norm_apihub(a) for a in items]


def _norm_apihub(a: dict) -> dict:
    p = a.get("price", a.get("min_price", 0))
    if isinstance(p, str):
        try: p = float(p.replace("$",""))
        except: p = 0
    return {"id": f"hub:{a.get('id','')}", "src": "apihub",
            "source_id": str(a.get("id","")), "name": a.get("name",""),
            "desc": (a.get("description","") or "")[:500], "cat": a.get("category",""),
            "price": float(p) if p else 0, "calls": a.get("total_calls",0), "rating": 0,
            "url": a.get("url",""), "extra": {}}


def agentictrade() -> list[dict]:
    """AgenticTrade — agent service exchange."""
    data = _get("https://agentictrade.io/api/services?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("services", [])
    return [_norm_agentictrade(s) for s in items]


def _norm_agentictrade(s: dict) -> dict:
    p = s.get("price", 0)
    if isinstance(p, str):
        try: p = float(p.replace("$",""))
        except: p = 0
    return {"id": f"atrade:{s.get('id','')}", "src": "agentictrade",
            "source_id": str(s.get("id","")), "name": s.get("name",""),
            "desc": (s.get("description","") or "")[:500], "cat": s.get("category",""),
            "price": float(p) if p else 0, "calls": s.get("total_calls",0), "rating": 0,
            "url": s.get("url",""), "extra": {}}


def fal() -> list[dict]:
    """FAL — AI model hosting."""
    data = _get("https://fal.ai/api/models?limit=100")
    if not data: return []
    items = data if isinstance(data, list) else data.get("models", [])
    return [_norm_fal(m) for m in items]


def _norm_fal(m: dict) -> dict:
    p = m.get("price", 0)
    if isinstance(p, str):
        try: p = float(p.replace("$",""))
        except: p = 0
    return {"id": f"fal:{m.get('id','')}", "src": "fal",
            "source_id": str(m.get("id","")), "name": m.get("name",""),
            "desc": (m.get("description","") or "")[:500], "cat": "ml",
            "price": float(p) if p else 0, "calls": m.get("total_calls",0), "rating": 0,
            "url": m.get("url",""), "extra": {"registry": m.get("registry","")}}
