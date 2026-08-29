"""Signal feed — market metrics."""
from __future__ import annotations

import json
import urllib.request
from typing import Any


def _get(url: str) -> Any:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except: return None


def npm_downloads() -> list[dict]:
    pkgs = ["@modelcontextprotocol/sdk", "langchain", "crewai", "bittensor", "openai", "anthropic"]
    items = []
    for pkg in pkgs:
        data = _get(f"https://api.npmjs.org/downloads/point/last-week/{pkg}")
        if data:
            items.append({"id": f"npm:{pkg}", "src": "npm", "metric": f"downloads:{pkg}",
                         "value": data.get("downloads",0), "observed": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
    return items


def hf_downloads() -> list[dict]:
    data = _get("https://huggingface.co/api/models?limit=10&sort=downloads&direction=-1")
    if not data: return []
    return [{"id": f"hf:{m.get('id','')}", "src": "hf", "metric": f"downloads:{m.get('id','')}",
             "value": m.get("downloads",0), "observed": time.strftime("%Y-%m-%dT%H:%M:%SZ")} for m in data]


def openrouter_models() -> list[dict]:
    data = _get("https://openrouter.ai/api/v1/models?limit=10")
    if not data: return []
    return [{"id": f"or:{m.get('id','')}", "src": "openrouter", "metric": f"model:{m.get('id','')}",
             "value": 1, "observed": time.strftime("%Y-%m-%dT%H:%M:%SZ")} for m in data.get("data",[])]


def agent_economy() -> list[dict]:
    data = _get("https://agenteconomy.to/data.json")
    if not data: return []
    items = []
    for k, v in data.items():
        if isinstance(v, dict) and "daily" in str(v):
            items.append({"id": f"ae:{k}", "src": "agenteconomy", "metric": k,
                         "value": v, "observed": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
    return items[:20]


import time
