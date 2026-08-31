"""GraphStore — abstract interface for Hydra.

SQLite now, real HydraDB over Bolt/HTTP later.
Same API either way.
"""
from __future__ import annotations

import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Any


def _sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


class GraphStore:
    """Graph interface — swap SQLite for HydraDB without changing callers."""

    def __init__(self, db_path: str = "data/hydradb.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hydra_nodes (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                properties TEXT NOT NULL,
                created_at REAL DEFAULT (strftime('%s','now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hydra_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src TEXT NOT NULL,
                dst TEXT NOT NULL,
                label TEXT NOT NULL,
                properties TEXT DEFAULT '{}',
                created_at REAL DEFAULT (strftime('%s','now')),
                FOREIGN KEY (src) REFERENCES hydra_nodes(id),
                FOREIGN KEY (dst) REFERENCES hydra_nodes(id)
            )
        """)
        conn.commit()
        conn.close()

    def upsert_node(self, node_id: str, label: str, properties: dict[str, Any] = None):
        props = properties or {}
        props["_label"] = label
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO hydra_nodes(id, label, properties) VALUES(?,?,?)",
            (node_id, label, json.dumps(props, default=str)),
        )
        conn.commit()
        conn.close()

    def upsert_edge(self, src: str, dst: str, label: str, properties: dict[str, Any] = None):
        props = properties or {}
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO hydra_edges(src, dst, label, properties) VALUES(?,?,?,?)",
            (src, dst, label, json.dumps(props, default=str)),
        )
        conn.commit()
        conn.close()

    def query(self, cypher: str, params: dict = None) -> list[dict]:
        """Minimal OpenCypher-like query (SQLite backend)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Simple pattern: MATCH (n:Label) WHERE n.prop = ? RETURN n
        # For now, just do basic node lookup
        rows = conn.execute("SELECT * FROM hydra_nodes").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_node(self, node_id: str) -> dict | None:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM hydra_nodes WHERE id=?", (node_id,)).fetchone()
        conn.close()
        if row:
            d = dict(row)
            d["properties"] = json.loads(d["properties"])
            return d
        return None

    def get_edges_from(self, node_id: str, edge_label: str = None) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        if edge_label:
            rows = conn.execute(
                "SELECT * FROM hydra_edges WHERE src=? AND label=?", (node_id, edge_label)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM hydra_edges WHERE src=?", (node_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_edges_to(self, node_id: str, edge_label: str = None) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        if edge_label:
            rows = conn.execute(
                "SELECT * FROM hydra_edges WHERE dst=? AND label=?", (node_id, edge_label)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM hydra_edges WHERE dst=?", (node_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def node_count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        n = conn.execute("SELECT COUNT(*) FROM hydra_nodes").fetchone()[0]
        conn.close()
        return n

    def edge_count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        n = conn.execute("SELECT COUNT(*) FROM hydra_edges").fetchone()[0]
        conn.close()
        return n
