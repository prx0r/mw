"""HydraDB client — Bolt/HTTP interface for real HydraDB.

SQLite fallback when HydraDB isn't available.
Same API either way.
"""
from __future__ import annotations

import json
import os
from typing import Any

HYDRADB_URL = os.environ.get("HYDRADB_URL", "")  # e.g. http://localhost:7474


class HydraDBClient:
    """Client for HydraDB — real Bolt/HTTP when available, SQLite fallback."""

    def __init__(self, url: str = ""):
        self.url = url or HYDRADB_URL
        self._use_http = bool(self.url)
        self._sqlite = None

        if not self._use_http:
            from hydra.graph import GraphStore
            self._sqlite = GraphStore()

    def query(self, cypher: str, params: dict = None) -> list[dict]:
        """Run a Cypher query."""
        if self._use_http:
            return self._http_query(cypher, params or {})
        return self._sqlite.query(cypher, params)

    def upsert_node(self, node_id: str, label: str, properties: dict = None):
        if self._use_http:
            self._http_upsert_node(node_id, label, properties or {})
        else:
            self._sqlite.upsert_node(node_id, label, properties)

    def upsert_edge(self, src: str, dst: str, label: str, properties: dict = None):
        if self._use_http:
            self._http_upsert_edge(src, dst, label, properties or {})
        else:
            self._sqlite.upsert_edge(src, dst, label, properties)

    def get_node(self, node_id: str) -> dict | None:
        if self._use_http:
            return self._http_get_node(node_id)
        return self._sqlite.get_node(node_id)

    def stats(self) -> dict:
        if self._use_http:
            return self._http_stats()
        return {"nodes": self._sqlite.node_count(), "edges": self._sqlite.edge_count(), "backend": "sqlite"}

    # ─── HTTP methods ──────────────────────────────────────────────────

    def _http_query(self, cypher: str, params: dict) -> list[dict]:
        import urllib.request
        data = json.dumps({"cypher": cypher, "params": params}).encode()
        req = urllib.request.Request(
            f"{self.url}/cypher",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            return json.loads(resp.read())
        except Exception:
            return []

    def _http_upsert_node(self, node_id: str, label: str, properties: dict):
        import urllib.request
        data = json.dumps({"id": node_id, "label": label, "properties": properties}).encode()
        req = urllib.request.Request(
            f"{self.url}/node",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass

    def _http_upsert_edge(self, src: str, dst: str, label: str, properties: dict):
        import urllib.request
        data = json.dumps({"src": src, "dst": dst, "label": label, "properties": properties}).encode()
        req = urllib.request.Request(
            f"{self.url}/edge",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass

    def _http_get_node(self, node_id: str) -> dict | None:
        import urllib.request
        try:
            resp = urllib.request.urlopen(f"{self.url}/node/{node_id}", timeout=10)
            return json.loads(resp.read())
        except Exception:
            return None

    def _http_stats(self) -> dict:
        import urllib.request
        try:
            resp = urllib.request.urlopen(f"{self.url}/stats", timeout=10)
            return json.loads(resp.read())
        except Exception:
            return {"backend": "http_unavailable"}
