"""Append-only event ledger — events are truth, projections are derived.

Canonical event: WorkerEvent is the single serialization.
recorded_at is part of the hash to bind timestamps cryptographically.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from core.schema import uid, sha256, WorkerEvent


class EventLedger:
    """Append-only event store. Never mutate existing events."""

    def __init__(self, db_path: str = "data/wk-events.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE,
                run_id TEXT,
                event_type TEXT,
                payload TEXT,
                payload_sha256 TEXT,
                recorded_at TEXT,
                prev_sha256 TEXT,
                event_sha256 TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _conn(self):
        return sqlite3.connect(str(self.db_path))

    def append(self, run_id: str, event_type: str, payload: dict) -> str:
        """Append event. Returns event_id."""
        conn = self._conn()
        event_id = uid()
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        payload_json = json.dumps(payload, sort_keys=True)
        payload_hash = sha256(payload_json)

        # Get previous hash for this run only
        row = conn.execute("SELECT event_sha256 FROM events WHERE run_id=? ORDER BY seq DESC LIMIT 1", (run_id,)).fetchone()
        prev_hash = row[0] if row else ""

        # Compute event hash — recorded_at is part of the canonical serialization
        event_data = f"{event_id}:{run_id}:{event_type}:{payload_json}:{now}:{prev_hash}"
        event_hash = sha256(event_data)

        conn.execute("""
            INSERT INTO events (event_id, run_id, event_type, payload, payload_sha256, recorded_at, prev_sha256, event_sha256)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (event_id, run_id, event_type, payload_json, payload_hash, now, prev_hash, event_hash))
        conn.commit()
        conn.close()
        return event_id

    def get_events(self, run_id: str, since_seq: int = 0) -> list[dict]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT * FROM events WHERE run_id=? AND seq>? ORDER BY seq",
            (run_id, since_seq)
        ).fetchall()
        cols = [d[0] for d in conn.execute("SELECT * FROM events LIMIT 0").description]
        conn.close()
        return [dict(zip(cols, r)) for r in rows]

    def count(self, run_id: str = "") -> int:
        conn = self._conn()
        if run_id:
            n = conn.execute("SELECT COUNT(*) FROM events WHERE run_id=?", (run_id,)).fetchone()[0]
        else:
            n = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        conn.close()
        return n

    def verify_chain(self, run_id: str) -> bool:
        """Verify event chain integrity. Returns False for empty chains."""
        events = self.get_events(run_id)
        if not events:
            return False
        prev = ""
        for e in events:
            if e["prev_sha256"] != prev:
                return False
            # recorded_at is now part of the canonical hash
            expected = sha256(f"{e['event_id']}:{e['run_id']}:{e['event_type']}:{e['payload']}:{e['recorded_at']}:{prev}")
            if e["event_sha256"] != expected:
                return False
            prev = e["event_sha256"]
        return True
