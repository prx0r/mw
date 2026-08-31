"""HydraDB wiring — SQLite now, Bolt/HTTP when available."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class HydraWiring:
    """Wire HydraDB to WorkerKit."""

    def __init__(self, db_path: str = "data/hydradb.db"):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""CREATE TABLE IF NOT EXISTS hydra_nodes (
            id TEXT PRIMARY KEY, label TEXT NOT NULL,
            properties TEXT NOT NULL, created_at REAL DEFAULT (strftime('%s','now'))
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS hydra_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL, target_id TEXT NOT NULL,
            type TEXT NOT NULL, properties TEXT DEFAULT '{}',
            created_at REAL DEFAULT (strftime('%s','now'))
        )""")
        conn.commit()
        conn.close()

    def project_campaign(self, campaign_id: str, data: dict):
        """Project a campaign into the graph."""
        self.upsert_node(f"campaign:{campaign_id}", "Campaign", data)

    def project_run(self, run_id: str, campaign_id: str, data: dict):
        """Project a run into the graph."""
        self.upsert_node(f"run:{run_id}", "Run", data)
        self.upsert_edge(f"campaign:{campaign_id}", f"run:{run_id}", "CONTAINS")

    def project_binding(self, binding_hash: str, run_id: str, data: dict):
        """Project a RunBinding into the graph."""
        self.upsert_node(f"binding:{binding_hash[:12]}", "RunBinding", data)
        self.upsert_edge(f"run:{run_id}", f"binding:{binding_hash[:12]}", "HAS_BINDING")

    def project_decision(self, decision_id: str, run_id: str, data: dict):
        """Project a DecisionPoint into the graph."""
        self.upsert_node(f"decision:{decision_id}", "DecisionPoint", data)
        self.upsert_edge(f"run:{run_id}", f"decision:{decision_id}", "CONTAINS")

    def project_worker_genome(self, genome_id: str, data: dict):
        """Project a WorkerGenome into the graph."""
        self.upsert_node(f"genome:{genome_id}", "WorkerGenome", data)

    def project_model_call(self, call_id: str, run_id: str, data: dict):
        """Project a ModelCall into the graph."""
        self.upsert_node(f"model_call:{call_id}", "ModelCall", data)
        self.upsert_edge(f"run:{run_id}", f"model_call:{call_id}", "USED")

    def upsert_node(self, node_id: str, label: str, properties: dict = None):
        props = properties or {}
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO hydra_nodes(id, label, properties) VALUES(?,?,?)",
            (node_id, label, json.dumps(props, default=str)),
        )
        conn.commit()
        conn.close()

    def upsert_edge(self, src: str, dst: str, label: str, properties: dict = None):
        props = properties or {}
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO hydra_edges(source_id, target_id, type, properties) VALUES(?,?,?,?)",
            (src, dst, label, json.dumps(props, default=str)),
        )
        conn.commit()
        conn.close()

    def stats(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        nodes = conn.execute("SELECT COUNT(*) FROM hydra_nodes").fetchone()[0]
        edges = conn.execute("SELECT COUNT(*) FROM hydra_edges").fetchone()[0]
        by_label = conn.execute("SELECT label, COUNT(*) FROM hydra_nodes GROUP BY label").fetchall()
        conn.close()
        return {"nodes": nodes, "edges": edges, "by_label": {l: c for l, c in by_label}}
