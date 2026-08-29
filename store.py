"""SQLite storage — append-only."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from .config import DB, DATA

DATA.mkdir(parents=True, exist_ok=True)


def conn() -> sqlite3.Connection:
    c = sqlite3.connect(str(DB), check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init():
    c = conn()
    c.executescript("""
        -- Core entities
        CREATE TABLE IF NOT EXISTS opp (
            id TEXT PRIMARY KEY, src TEXT, source_id TEXT,
            title TEXT, desc TEXT, url TEXT, cat TEXT, skills TEXT,
            reward REAL, currency TEXT, status TEXT, posted TEXT,
            extra TEXT, first_seen TEXT, last_seen TEXT
        );
        CREATE TABLE IF NOT EXISTS svc (
            id TEXT PRIMARY KEY, src TEXT, source_id TEXT,
            name TEXT, desc TEXT, url TEXT, cat TEXT,
            price REAL, calls INT, rating REAL, extra TEXT,
            first_seen TEXT, last_seen TEXT
        );
        CREATE TABLE IF NOT EXISTS sub (
            id TEXT PRIMARY KEY, netuid INT, name TEXT,
            emission REAL, miners INT, validators INT,
            tao_price REAL, status TEXT, extra TEXT,
            first_seen TEXT, last_seen TEXT
        );
        CREATE TABLE IF NOT EXISTS obs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT, src TEXT, metric TEXT,
            prev_val TEXT, curr_val TEXT, observed TEXT
        );
        CREATE TABLE IF NOT EXISTS sig (
            id TEXT PRIMARY KEY, src TEXT, metric TEXT,
            value TEXT, observed TEXT, extra TEXT
        );
        CREATE TABLE IF NOT EXISTS src (
            id TEXT PRIMARY KEY, name TEXT, type TEXT,
            url TEXT, auth TEXT, agent_native INT, extra TEXT
        );
        CREATE TABLE IF NOT EXISTS mkt (
            id TEXT PRIMARY KEY, name TEXT, type TEXT,
            chain TEXT, url TEXT, agent_native INT, extra TEXT
        );
        CREATE TABLE IF NOT EXISTS actor (
            id TEXT PRIMARY KEY, name TEXT, type TEXT,
            network TEXT, wallet TEXT, caps TEXT,
            reputation REAL, extra TEXT
        );
        CREATE TABLE IF NOT EXISTS cap (
            id TEXT PRIMARY KEY, slug TEXT, name TEXT,
            parent_id TEXT, desc TEXT, extra TEXT
        );
        CREATE TABLE IF NOT EXISTS sub_run (
            id TEXT PRIMARY KEY, agent_id TEXT, opp_id TEXT,
            recipe_id TEXT, started TEXT, submitted TEXT,
            compute_usd REAL, api_usd REAL, human_min REAL,
            artifact_hash TEXT, judge_score REAL, extra TEXT
        );
        CREATE TABLE IF NOT EXISTS outcome (
            id TEXT PRIMARY KEY, sub_id TEXT, status TEXT,
            rank INT, gross_usd REAL, net_usd REAL,
            feedback TEXT, settled TEXT, extra TEXT
        );
        CREATE TABLE IF NOT EXISTS pay (
            id TEXT PRIMARY KEY, payer TEXT, payee TEXT,
            amount REAL, currency TEXT, tx_hash TEXT,
            chain TEXT, status TEXT, observed TEXT, extra TEXT
        );
        CREATE TABLE IF NOT EXISTS pred (
            id TEXT PRIMARY KEY, opp_id TEXT, worker_id TEXT,
            model TEXT, computed TEXT, p_entry REAL, p_award REAL,
            p_accept REAL, est_cost REAL, est_payout REAL, est_net REAL,
            conf_low REAL, conf_high REAL, features TEXT
        );

        -- Oracle-specific tables (append-only where history matters)
        CREATE TABLE IF NOT EXISTS opp_obs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opp_id TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            status TEXT,
            reward REAL,
            applicant_count INT,
            submission_count INT,
            deadline TEXT,
            raw_digest TEXT,
            raw_blob_uri TEXT
        );
        CREATE TABLE IF NOT EXISTS opp_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opp_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_at TEXT NOT NULL,
            data TEXT,
            confidence TEXT DEFAULT 'observed'
        );
        CREATE TABLE IF NOT EXISTS market_snap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src TEXT NOT NULL,
            snapshot_at TEXT NOT NULL,
            metrics TEXT
        );
        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY, name TEXT, type TEXT,
            url TEXT, auth TEXT, agent_native INT, last_polled TEXT, extra TEXT
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS i_opp_src ON opp(src);
        CREATE INDEX IF NOT EXISTS i_opp_status ON opp(status);
        CREATE INDEX IF NOT EXISTS i_svc_src ON svc(src);
        CREATE INDEX IF NOT EXISTS i_obs_entity ON obs(entity_id);
        CREATE INDEX IF NOT EXISTS i_sub_agent ON sub_run(agent_id);
        CREATE INDEX IF NOT EXISTS i_outcome_sub ON outcome(sub_id);
        CREATE INDEX IF NOT EXISTS i_opp_obs_opp ON opp_obs(opp_id);
        CREATE INDEX IF NOT EXISTS i_opp_obs_time ON opp_obs(observed_at);
        CREATE INDEX IF NOT EXISTS i_opp_events_opp ON opp_events(opp_id);
        CREATE INDEX IF NOT EXISTS i_market_snap_src ON market_snap(src);
    """)
    c.commit()


init()


def upsert_opp(o: dict) -> str:
    c = conn()
    eid = o.get("id", "")
    existing = c.execute("SELECT * FROM opp WHERE id=?", (eid,)).fetchone()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    c.execute("""INSERT OR REPLACE INTO opp
        (id,src,source_id,title,desc,url,cat,skills,reward,currency,status,posted,extra,first_seen,last_seen)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (eid, o.get("src",""), o.get("source_id",""), o.get("title",""),
         o.get("desc",""), o.get("url",""), o.get("cat",""),
         json.dumps(o.get("skills",[])), o.get("reward",0),
         o.get("currency","USD"), o.get("status","open"), o.get("posted",""),
         json.dumps(o.get("extra",{})),
         existing["first_seen"] if existing else now, now))

    # Record observation
    if not existing:
        _obs(eid, o.get("src",""), "status", None, "open")
        _obs(eid, o.get("src",""), "reward", None, o.get("reward",0))
    c.commit()


def upsert_svc(s: dict) -> str:
    c = conn()
    sid = s.get("id", "")
    existing = c.execute("SELECT * FROM svc WHERE id=?", (sid,)).fetchone()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    c.execute("""INSERT OR REPLACE INTO svc
        (id,src,source_id,name,desc,url,cat,price,calls,rating,extra,first_seen,last_seen)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (sid, s.get("src",""), s.get("source_id",""), s.get("name",""),
         s.get("desc",""), s.get("url",""), s.get("cat",""),
         s.get("price",0), s.get("calls",0), s.get("rating",0),
         json.dumps(s.get("extra",{})),
         existing["first_seen"] if existing else now, now))
    c.commit()
    return sid


def upsert_sub(s: dict) -> str:
    c = conn()
    sid = s.get("id", "")
    existing = c.execute("SELECT * FROM sub WHERE id=?", (sid,)).fetchone()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    c.execute("""INSERT OR REPLACE INTO sub
        (id,netuid,name,emission,miners,validators,tao_price,status,extra,first_seen,last_seen)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (sid, s.get("netuid",0), s.get("name",""), s.get("emission",0),
         s.get("miners",0), s.get("validators",0), s.get("tao_price",0),
         s.get("status","active"), json.dumps(s.get("extra",{})),
         existing["first_seen"] if existing else now, now))
    c.commit()
    return sid


def _obs(eid: str, src: str, metric: str, prev, curr):
    c = conn()
    c.execute("INSERT INTO obs (entity_id,src,metric,prev_val,curr_val,observed) VALUES (?,?,?,?,?,?)",
        (eid, src, metric, json.dumps(prev), json.dumps(curr),
         time.strftime("%Y-%m-%dT%H:%M:%SZ")))
    c.commit()


def q(sql: str, params: tuple = ()) -> list[dict]:
    c = conn()
    rows = c.execute(sql, params).fetchall()
    
    return [dict(r) for r in rows]


def stats() -> dict:
    c = conn()
    s = {}
    for t in ["opp", "svc", "sub", "obs", "sig", "opp_obs", "opp_events"]:
        try:
            s[t] = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except:
            s[t] = 0
    s["opp_usd"] = c.execute("SELECT SUM(reward) FROM opp WHERE reward>0").fetchone()[0] or 0
    s["svc_calls"] = c.execute("SELECT SUM(calls) FROM svc").fetchone()[0] or 0
    
    return s
