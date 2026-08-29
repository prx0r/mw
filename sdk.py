"""Oracle SDK — thin client for agents.

Usage:
    from oracle.sdk import Oracle
    
    o = Oracle()
    print(o.pulse())
    print(o.work(skill="python", min_reward=10))
    print(o.brief(skills="solidity,rust"))
"""

import json
import urllib.request
from typing import Any


class Oracle:
    """Thin client for the Oracle API."""

    def __init__(self, base: str = "http://localhost:8788"):
        self.base = base.rstrip("/")

    def _get(self, path: str, params: dict = None) -> Any:
        url = f"{self.base}{path}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items() if v)
            if query: url += f"?{query}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except: return None

    def pulse(self) -> dict:
        """Market snapshot."""
        return self._get("/pulse") or {}

    def work(self, src: str = "", cat: str = "", skill: str = "",
             min_reward: float = 0, limit: int = 50) -> dict:
        """List work opportunities."""
        return self._get("/work", {"src": src, "cat": cat, "skill": skill,
                                    "min_reward": min_reward, "limit": limit}) or {}

    def svc(self, src: str = "", cat: str = "", limit: int = 50) -> dict:
        """List services."""
        return self._get("/svc", {"src": src, "cat": cat, "limit": limit}) or {}

    def sub(self, limit: int = 50) -> dict:
        """List subnets."""
        return self._get("/sub", {"limit": limit}) or {}

    def demand(self, window: str = "30d") -> dict:
        """Cross-layer demand."""
        return self._get("/demand", {"window": window}) or {}

    def compare(self, window: str = "30d") -> dict:
        """Platform comparison."""
        return self._get("/compare", {"window": window}) or {}

    def brief(self, skills: str = "", min_reward: float = 0) -> dict:
        """Agent briefing."""
        return self._get("/brief", {"skills": skills, "min_reward": min_reward}) or {}

    def supply(self, src: str = "", cat: str = "") -> dict:
        """Service supply."""
        return self._get("/svc", {"src": src, "cat": cat}) or {}

    def trends(self, window: str = "30d") -> dict:
        """Timeseries."""
        return self._get("/trends", {"window": window}) or {}

    def boards(self) -> dict:
        """Leaderboards."""
        return self._get("/boards") or {}

    def econ(self) -> dict:
        """Economics summary."""
        return self._get("/econ") or {}

    def data(self) -> dict:
        """Data summary."""
        return self._get("/data") or {}

    def search(self, q: str) -> dict:
        """Search work."""
        return self._get("/search", {"q": q}) or {}

    def metrics(self, window: str = "30d") -> dict:
        """Compute all 6 canonical metric families."""
        return self._get("/metrics", {"window": window}) or {}

    def history(self, window: str = "30d") -> dict:
        """Historical state changes."""
        return self._get("/history", {"window": window}) or {}

    def signals(self) -> dict:
        """Market signals."""
        return self._get("/signals") or {}
