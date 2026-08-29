"""SQLite-backed market store — replaces in-memory dicts."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS listings (
    id TEXT PRIMARY KEY,
    asset_id TEXT,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS grants (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS receipts (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS invocations (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS leases (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS boards (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS distribution_grants (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS requests (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS settlements (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS workers (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at REAL
);
CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    listing_id TEXT,
    data TEXT NOT NULL,
    created_at REAL
);
"""


class MarketStore:
    """SQLite persistence for marketplace."""

    def __init__(self, db_path: str = "data/market.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()

    def _conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def put(self, table: str, obj_id: str, data: dict):
        conn = self._conn()
        conn.execute(
            f"INSERT OR REPLACE INTO {table} (id, data, created_at) VALUES (?, ?, ?)",
            (obj_id, json.dumps(data), data.get("created_at", time.time())),
        )
        conn.commit()
        conn.close()

    def get(self, table: str, obj_id: str) -> dict | None:
        conn = self._conn()
        row = conn.execute(f"SELECT data FROM {table} WHERE id=?", (obj_id,)).fetchone()
        conn.close()
        return json.loads(row["data"]) if row else None

    def list_all(self, table: str, limit: int = 50) -> list[dict]:
        conn = self._conn()
        rows = conn.execute(
            f"SELECT data FROM {table} ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [json.loads(r["data"]) for r in rows]

    def count(self, table: str) -> int:
        conn = self._conn()
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()
        return n

    def delete(self, table: str, obj_id: str):
        conn = self._conn()
        conn.execute(f"DELETE FROM {table} WHERE id=?", (obj_id,))
        conn.commit()
        conn.close()
