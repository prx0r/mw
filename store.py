"""SQLite storage — append-only. Full Oracle schema per ORACLE-SPEC.md."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from .config import DB, DATA
from .taxonomy import classify_opportunity

DATA.mkdir(parents=True, exist_ok=True)


def conn() -> sqlite3.Connection:
    c = sqlite3.connect(str(DB), check_same_thread=False, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA busy_timeout=30000")
    return c


def init():
    c = conn()
    c.executescript("""
        -- ============================================
        -- EXISTING TABLES (keep for backwards compat)
        -- ============================================
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

        -- ============================================
        -- ORACLE v1 SCHEMA (per ORACLE-SPEC.md)
        -- ============================================

        -- oracle.sources: where data comes from
        CREATE TABLE IF NOT EXISTS oracle_sources (
            id TEXT PRIMARY KEY,
            slug TEXT UNIQUE,
            name TEXT,
            source_type TEXT,
            website_url TEXT,
            adapter_name TEXT,
            adapter_version TEXT,
            crawl_interval_seconds INT DEFAULT 300,
            enabled INT DEFAULT 1,
            last_success_at TEXT,
            last_attempt_at TEXT,
            freshness_status TEXT DEFAULT 'unknown',
            error_rate_24h REAL DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT
        );

        -- oracle.ingest_runs: every crawler invocation
        CREATE TABLE IF NOT EXISTS oracle_ingest_runs (
            id TEXT PRIMARY KEY,
            source_id TEXT,
            started_at TEXT,
            finished_at TEXT,
            status TEXT,
            records_seen INT DEFAULT 0,
            records_created INT DEFAULT 0,
            records_changed INT DEFAULT 0,
            records_unchanged INT DEFAULT 0,
            records_failed INT DEFAULT 0,
            adapter_version TEXT,
            error_summary TEXT,
            metadata TEXT
        );

        -- oracle.raw_observations: immutable raw data
        CREATE TABLE IF NOT EXISTS oracle_raw_obs (
            id TEXT PRIMARY KEY,
            source_id TEXT,
            ingest_run_id TEXT,
            external_id TEXT,
            observed_at TEXT,
            content_hash TEXT,
            raw_blob_uri TEXT,
            http_status INT,
            source_url TEXT,
            parser_version TEXT,
            metadata TEXT
        );

        -- oracle.markets: marketplace/platform registry
        CREATE TABLE IF NOT EXISTS oracle_markets (
            id TEXT PRIMARY KEY,
            slug TEXT UNIQUE,
            name TEXT,
            market_type TEXT,
            website_url TEXT,
            agent_native INT DEFAULT 0,
            auth_type TEXT,
            submission_method TEXT,
            enabled INT DEFAULT 1,
            last_polled_at TEXT,
            metadata TEXT
        );

        -- oracle.opportunities: canonical work opportunities
        CREATE TABLE IF NOT EXISTS oracle_opps (
            id TEXT PRIMARY KEY,
            canonical_title TEXT,
            canonical_description TEXT,
            market_id TEXT,
            status TEXT DEFAULT 'open',
            category_id TEXT,
            execution_mode TEXT,
            reward_amount REAL,
            reward_currency TEXT DEFAULT 'USD',
            reward_usd REAL,
            reward_min_usd REAL,
            reward_max_usd REAL,
            deadline_at TEXT,
            source_created_at TEXT,
            first_seen_at TEXT,
            last_seen_at TEXT,
            closed_at TEXT,
            remote INT DEFAULT 1,
            human_allowed INT DEFAULT 1,
            agent_allowed INT DEFAULT 1,
            application_required INT DEFAULT 0,
            canonical_url TEXT,
            confidence TEXT DEFAULT 'observed',
            -- Shared ontology: canonical taxonomy from workerkit
            task_family TEXT DEFAULT '',
            canonical_capabilities TEXT DEFAULT '[]',
            autonomy_level TEXT DEFAULT 'H1',
            economic_surface TEXT DEFAULT 'BOUNTY',
            metadata TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        -- oracle.opportunity_sources: one opp may appear on multiple sources
        CREATE TABLE IF NOT EXISTS oracle_opp_sources (
            opportunity_id TEXT,
            source_id TEXT,
            external_id TEXT,
            source_url TEXT,
            first_seen_at TEXT,
            last_seen_at TEXT,
            match_confidence REAL DEFAULT 1.0,
            is_primary INT DEFAULT 0,
            PRIMARY KEY (opportunity_id, source_id)
        );

        -- oracle.opportunity_observations: append-only state snapshots
        CREATE TABLE IF NOT EXISTS oracle_opp_obs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id TEXT,
            source_id TEXT,
            observed_at TEXT,
            status TEXT,
            reward_amount REAL,
            reward_currency TEXT,
            reward_usd REAL,
            deadline_at TEXT,
            applicant_count INT,
            submission_count INT,
            raw_observation_id TEXT,
            normalized_hash TEXT,
            metadata TEXT
        );

        -- oracle.opportunity_events: generated when observations change
        CREATE TABLE IF NOT EXISTS oracle_opp_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id TEXT,
            event_type TEXT,
            occurred_at TEXT,
            observed_at TEXT,
            old_value TEXT,
            new_value TEXT,
            source_id TEXT,
            confidence TEXT DEFAULT 'observed'
        );

        -- oracle.skills: taxonomy
        CREATE TABLE IF NOT EXISTS oracle_skills (
            id TEXT PRIMARY KEY,
            slug TEXT UNIQUE,
            name TEXT,
            description TEXT,
            parent_id TEXT,
            aliases TEXT,
            taxonomy_version TEXT DEFAULT 'v1',
            created_at TEXT,
            deprecated_at TEXT
        );

        -- oracle.opportunity_skills: many-to-many
        CREATE TABLE IF NOT EXISTS oracle_opp_skills (
            opportunity_id TEXT,
            skill_id TEXT,
            confidence REAL DEFAULT 1.0,
            PRIMARY KEY (opportunity_id, skill_id)
        );

        -- oracle.categories: higher-level than skills
        CREATE TABLE IF NOT EXISTS oracle_categories (
            id TEXT PRIMARY KEY,
            slug TEXT UNIQUE,
            name TEXT,
            description TEXT,
            parent_id TEXT,
            created_at TEXT
        );

        -- oracle.opportunity_categories: many-to-many
        CREATE TABLE IF NOT EXISTS oracle_opp_categories (
            opportunity_id TEXT,
            category_id TEXT,
            PRIMARY KEY (opportunity_id, category_id)
        );

        -- oracle.metric_definitions: what metrics exist
        CREATE TABLE IF NOT EXISTS oracle_metric_defs (
            metric_id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            unit TEXT,
            grain TEXT,
            aggregation_method TEXT,
            methodology_version TEXT,
            source_requirements TEXT,
            missing_data_policy TEXT,
            experimental INT DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        );

        -- oracle.metric_points: raw metric data
        CREATE TABLE IF NOT EXISTS oracle_metric_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_id TEXT,
            entity_id TEXT,
            entity_type TEXT,
            period_start TEXT,
            period_end TEXT,
            value REAL,
            metadata TEXT
        );

        -- oracle.daily_market_metrics: rollup per market per day
        CREATE TABLE IF NOT EXISTS oracle_daily_market (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT,
            date TEXT,
            active_opportunities INT,
            new_opportunities INT,
            closed_opportunities INT,
            advertised_reward_usd REAL,
            median_reward_usd REAL,
            avg_reward_usd REAL,
            p25_reward_usd REAL,
            p75_reward_usd REAL,
            p90_reward_usd REAL,
            metadata TEXT
        );

        -- oracle.daily_skill_metrics: rollup per skill per day
        CREATE TABLE IF NOT EXISTS oracle_daily_skill (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT,
            date TEXT,
            active_opportunities INT,
            new_opportunities INT,
            advertised_reward_usd REAL,
            median_reward_usd REAL,
            metadata TEXT
        );

        -- oracle.daily_category_metrics: rollup per category per day
        CREATE TABLE IF NOT EXISTS oracle_daily_cat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id TEXT,
            date TEXT,
            active_opportunities INT,
            new_opportunities INT,
            advertised_reward_usd REAL,
            median_reward_usd REAL,
            metadata TEXT
        );

        -- ============================================
        -- RELATED TABLES (WorkerKit/Marketplace bridge)
        -- ============================================
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

        -- ============================================
        -- INDEXES
        -- ============================================
        CREATE INDEX IF NOT EXISTS i_opp_src ON opp(src);
        CREATE INDEX IF NOT EXISTS i_opp_status ON opp(status);
        CREATE INDEX IF NOT EXISTS i_svc_src ON svc(src);
        CREATE INDEX IF NOT EXISTS i_obs_entity ON obs(entity_id);

        CREATE INDEX IF NOT EXISTS i_ors_src ON oracle_sources(slug);
        CREATE INDEX IF NOT EXISTS i_orir_source ON oracle_ingest_runs(source_id);
        CREATE INDEX IF NOT EXISTS i_orir_status ON oracle_ingest_runs(status);
        CREATE INDEX IF NOT EXISTS i_orobs_source ON oracle_raw_obs(source_id);
        CREATE INDEX IF NOT EXISTS i_orobs_hash ON oracle_raw_obs(content_hash);

        CREATE INDEX IF NOT EXISTS i_oopp_market ON oracle_opps(market_id);
        CREATE INDEX IF NOT EXISTS i_oopp_status ON oracle_opps(status);
        CREATE INDEX IF NOT EXISTS i_oopp_cat ON oracle_opps(category_id);
        CREATE INDEX IF NOT EXISTS i_oopp_reward ON oracle_opps(reward_usd);
        CREATE INDEX IF NOT EXISTS i_oopp_first ON oracle_opps(first_seen_at);
        CREATE INDEX IF NOT EXISTS i_oopp_tf ON oracle_opps(task_family);

        CREATE INDEX IF NOT EXISTS i_oos_opp ON oracle_opp_sources(opportunity_id);
        CREATE INDEX IF NOT EXISTS i_oos_src ON oracle_opp_sources(source_id);

        CREATE INDEX IF NOT EXISTS i_ooobs_opp ON oracle_opp_obs(opportunity_id);
        CREATE INDEX IF NOT EXISTS i_ooobs_time ON oracle_opp_obs(observed_at);

        CREATE INDEX IF NOT EXISTS i_ooev_opp ON oracle_opp_events(opportunity_id);
        CREATE INDEX IF NOT EXISTS i_ooev_type ON oracle_opp_events(event_type);

        CREATE INDEX IF NOT EXISTS i_oos_opp2 ON oracle_opp_skills(opportunity_id);
        CREATE INDEX IF NOT EXISTS i_oos_skill ON oracle_opp_skills(skill_id);

        CREATE INDEX IF NOT EXISTS i_oomp_metric ON oracle_metric_points(metric_id);
        CREATE INDEX IF NOT EXISTS i_oomp_entity ON oracle_metric_points(entity_id);
        CREATE INDEX IF NOT EXISTS i_oomp_period ON oracle_metric_points(period_start);

        CREATE INDEX IF NOT EXISTS i_odmk_market ON oracle_daily_market(market_id);
        CREATE INDEX IF NOT EXISTS i_odmk_date ON oracle_daily_market(date);
        CREATE INDEX IF NOT EXISTS i_odsk_skill ON oracle_daily_skill(skill_id);
        CREATE INDEX IF NOT EXISTS i_odsk_date ON oracle_daily_skill(date);
        CREATE INDEX IF NOT EXISTS i_odct_cat ON oracle_daily_cat(category_id);
        CREATE INDEX IF NOT EXISTS i_odct_date ON oracle_daily_cat(date);
    """)
    c.commit()

    # Migration: add taxonomy columns if missing
    try:
        c.execute("ALTER TABLE oracle_opps ADD COLUMN task_family TEXT DEFAULT ''")
    except:
        pass
    try:
        c.execute("ALTER TABLE oracle_opps ADD COLUMN canonical_capabilities TEXT DEFAULT '[]'")
    except:
        pass
    try:
        c.execute("ALTER TABLE oracle_opps ADD COLUMN autonomy_level TEXT DEFAULT 'H1'")
    except:
        pass
    try:
        c.execute("ALTER TABLE oracle_opps ADD COLUMN economic_surface TEXT DEFAULT 'BOUNTY'")
    except:
        pass
    c.commit()


init()


# ============================================
# EXISTING UPSERT FUNCTIONS (keep for compat)
# ============================================

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

    if not existing:
        c.execute("INSERT INTO obs (entity_id,src,metric,prev_val,curr_val,observed) VALUES (?,?,?,?,?,?)",
            (eid, o.get("src",""), "status", None, "open", now))
        c.execute("INSERT INTO obs (entity_id,src,metric,prev_val,curr_val,observed) VALUES (?,?,?,?,?,?)",
            (eid, o.get("src",""), "reward", None, o.get("reward",0), now))

    # Also upsert into oracle_opps (canonical table) — SAME connection
    src = o.get("src", "")
    market_id = src if src else "unknown"
    reward = o.get("reward", 0) or 0
    skills = o.get("skills", [])
    cat = o.get("cat", "")

    existing_canon = c.execute("SELECT * FROM oracle_opps WHERE id=?", (eid,)).fetchone()

    # Check if taxonomy columns exist
    has_taxonomy = False
    try:
        c.execute("SELECT task_family FROM oracle_opps LIMIT 1")
        has_taxonomy = True
    except:
        pass

    if has_taxonomy:
        # Classify using shared ontology
        classification = classify_opportunity(src, cat, skills)
        task_family = classification["task_family"]
        canonical_caps = json.dumps(classification["capabilities"])
        autonomy = classification["autonomy_level"]
        econ_surface = classification["economic_surface"]

        c.execute("""INSERT OR REPLACE INTO oracle_opps
            (id, canonical_title, canonical_description, market_id, status,
             execution_mode, reward_amount, reward_currency, reward_usd,
             task_family, canonical_capabilities, autonomy_level, economic_surface,
             first_seen_at, last_seen_at, canonical_url, confidence,
             metadata, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (eid, o.get("title",""), o.get("desc",""), market_id,
             o.get("status","open"), "autonomous",
             reward, o.get("currency","USD"), reward,
             task_family, canonical_caps, autonomy, econ_surface,
             existing_canon["first_seen_at"] if existing_canon else now, now,
             o.get("url",""), "observed",
             json.dumps({"src": src, "skills": skills, "cat": cat}),
             existing_canon["created_at"] if existing_canon else now, now))
    else:
        c.execute("""INSERT OR REPLACE INTO oracle_opps
            (id, canonical_title, canonical_description, market_id, status,
             execution_mode, reward_amount, reward_currency, reward_usd,
             first_seen_at, last_seen_at, canonical_url, confidence,
             metadata, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (eid, o.get("title",""), o.get("desc",""), market_id,
             o.get("status","open"), "autonomous",
             reward, o.get("currency","USD"), reward,
             existing_canon["first_seen_at"] if existing_canon else now, now,
             o.get("url",""), "observed",
             json.dumps({"src": src, "skills": skills, "cat": cat}),
             existing_canon["created_at"] if existing_canon else now, now))

    for skill_slug in skills:
        slug = skill_slug.lower().strip().replace(" ", "-")
        sk = c.execute("SELECT id FROM oracle_skills WHERE slug=?", (slug,)).fetchone()
        if not sk:
            skill_id = f"skill:{slug}"
            c.execute("INSERT OR IGNORE INTO oracle_skills (id, slug, name, created_at) VALUES (?,?,?,?)",
                      (skill_id, slug, slug.replace("-", " ").title(), now))
        else:
            skill_id = sk["id"]
        c.execute("INSERT OR IGNORE INTO oracle_opp_skills (opportunity_id, skill_id) VALUES (?,?)",
                  (eid, skill_id))

    if cat:
        cat_slug = cat.lower().strip().replace(" ", "-")
        ck = c.execute("SELECT id FROM oracle_categories WHERE slug=?", (cat_slug,)).fetchone()
        if not ck:
            cat_id = f"cat:{cat_slug}"
            c.execute("INSERT OR IGNORE INTO oracle_categories (id, slug, name, created_at) VALUES (?,?,?,?)",
                      (cat_id, cat_slug, cat_slug.replace("-", " ").title(), now))
        else:
            cat_id = ck["id"]
        c.execute("INSERT OR IGNORE INTO oracle_opp_categories (opportunity_id, category_id) VALUES (?,?)",
                  (eid, cat_id))

    # Record observation in canonical table
    c.execute("""INSERT INTO oracle_opp_obs
        (opportunity_id, source_id, observed_at, status, reward_amount,
         reward_currency, reward_usd, metadata)
        VALUES (?,?,?,?,?,?,?,?)""",
        (eid, src, now, o.get("status","open"), reward, o.get("currency","USD"), reward, json.dumps({})))

    if not existing_canon:
        c.execute("""INSERT INTO oracle_opp_events
            (opportunity_id, event_type, occurred_at, observed_at, source_id)
            VALUES (?,?,?,?,?)""",
            (eid, "discovered", now, now, src))

    c.commit()
    c.close()
    return eid


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
    c.close()
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


# ============================================
# CANONICAL ORACLE FUNCTIONS
# ============================================

def _upsert_canonical_opp(o: dict):
    """Upsert into oracle_opps (canonical table) from raw feed item."""
    c = conn()
    eid = o.get("id", "")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    existing = c.execute("SELECT * FROM oracle_opps WHERE id=?", (eid,)).fetchone()

    # Map source to market_id
    src = o.get("src", "")
    market_id = src if src else "unknown"

    reward = o.get("reward", 0) or 0
    skills = o.get("skills", [])
    cat = o.get("cat", "")

    # Check if taxonomy columns exist
    has_taxonomy = False
    try:
        c.execute("SELECT task_family FROM oracle_opps LIMIT 1")
        has_taxonomy = True
    except:
        pass

    if has_taxonomy:
        # Classify using shared ontology
        classification = classify_opportunity(src, cat, skills)
        task_family = classification["task_family"]
        canonical_caps = json.dumps(classification["capabilities"])
        autonomy = classification["autonomy_level"]
        econ_surface = classification["economic_surface"]

        c.execute("""INSERT OR REPLACE INTO oracle_opps
            (id, canonical_title, canonical_description, market_id, status,
             execution_mode, reward_amount, reward_currency, reward_usd,
             task_family, canonical_capabilities, autonomy_level, economic_surface,
             first_seen_at, last_seen_at, canonical_url, confidence,
             metadata, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (eid, o.get("title",""), o.get("desc",""), market_id,
             o.get("status","open"), "autonomous",
             reward, o.get("currency","USD"), reward,
             task_family, canonical_caps, autonomy, econ_surface,
             existing["first_seen_at"] if existing else now, now,
             o.get("url",""), "observed",
             json.dumps({"src": src, "skills": skills, "cat": cat}),
             existing["created_at"] if existing else now, now))
    else:
        c.execute("""INSERT OR REPLACE INTO oracle_opps
            (id, canonical_title, canonical_description, market_id, status,
             execution_mode, reward_amount, reward_currency, reward_usd,
             first_seen_at, last_seen_at, canonical_url, confidence,
             metadata, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (eid, o.get("title",""), o.get("desc",""), market_id,
             o.get("status","open"), "autonomous",
             reward, o.get("currency","USD"), reward,
             existing["first_seen_at"] if existing else now, now,
             o.get("url",""), "observed",
             json.dumps({"src": src, "skills": skills, "cat": cat}),
             existing["created_at"] if existing else now, now))

    # Link skills
    for skill_slug in skills:
        skill_id = _ensure_skill(c, skill_slug)
        c.execute("INSERT OR IGNORE INTO oracle_opp_skills (opportunity_id, skill_id) VALUES (?,?)",
                  (eid, skill_id))

    # Link category
    if cat:
        cat_id = _ensure_category(c, cat)
        c.execute("INSERT OR IGNORE INTO oracle_opp_categories (opportunity_id, category_id) VALUES (?,?)",
                  (eid, cat_id))

    # Record observation
    _record_opp_observation(c, eid, o)

    c.commit()


def _ensure_skill(c, slug: str) -> str:
    """Ensure a skill exists, return its ID."""
    slug = slug.lower().strip().replace(" ", "-")
    existing = c.execute("SELECT id FROM oracle_skills WHERE slug=?", (slug,)).fetchone()
    if existing:
        return existing["id"]
    skill_id = f"skill:{slug}"
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    c.execute("""INSERT OR IGNORE INTO oracle_skills (id, slug, name, created_at)
        VALUES (?,?,?,?)""", (skill_id, slug, slug.replace("-", " ").title(), now))
    return skill_id


def _ensure_category(c, slug: str) -> str:
    """Ensure a category exists, return its ID."""
    slug = slug.lower().strip().replace(" ", "-")
    existing = c.execute("SELECT id FROM oracle_categories WHERE slug=?", (slug,)).fetchone()
    if existing:
        return existing["id"]
    cat_id = f"cat:{slug}"
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    c.execute("""INSERT OR IGNORE INTO oracle_categories (id, slug, name, created_at)
        VALUES (?,?,?,?)""", (cat_id, slug, slug.replace("-", " ").title(), now))
    return cat_id


def _record_opp_observation(c, opp_id: str, o: dict):
    """Record an observation for an opportunity (append-only)."""
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    reward = o.get("reward", 0) or 0

    # Check if status/reward changed
    prev = c.execute(
        "SELECT status, reward_usd FROM oracle_opp_obs WHERE opportunity_id=? ORDER BY observed_at DESC LIMIT 1",
        (opp_id,)).fetchone()

    c.execute("""INSERT INTO oracle_opp_obs
        (opportunity_id, source_id, observed_at, status, reward_amount,
         reward_currency, reward_usd, metadata)
        VALUES (?,?,?,?,?,?,?,?)""",
        (opp_id, o.get("src",""), now, o.get("status","open"),
         reward, o.get("currency","USD"), reward, json.dumps({})))

    # Generate event if changed
    if prev:
        if prev["status"] != o.get("status","open"):
            c.execute("""INSERT INTO oracle_opp_events
                (opportunity_id, event_type, occurred_at, observed_at,
                 old_value, new_value, source_id)
                VALUES (?,?,?,?,?,?,?)""",
                (opp_id, "status_changed", now, now,
                 json.dumps({"status": prev["status"]}),
                 json.dumps({"status": o.get("status","open")}),
                 o.get("src","")))
        if (prev["reward_usd"] or 0) != reward:
            c.execute("""INSERT INTO oracle_opp_events
                (opportunity_id, event_type, occurred_at, observed_at,
                 old_value, new_value, source_id)
                VALUES (?,?,?,?,?,?,?)""",
                (opp_id, "reward_changed", now, now,
                 json.dumps({"reward_usd": prev["reward_usd"]}),
                 json.dumps({"reward_usd": reward}),
                 o.get("src","")))
    else:
        c.execute("""INSERT INTO oracle_opp_events
            (opportunity_id, event_type, occurred_at, observed_at, source_id)
            VALUES (?,?,?,?,?)""",
            (opp_id, "discovered", now, now, o.get("src","")))


def record_ingest_run(source_id: str, status: str, records_seen: int = 0,
                      records_created: int = 0, records_changed: int = 0,
                      records_unchanged: int = 0, records_failed: int = 0,
                      error_summary: str = "") -> str:
    """Record an ingest run."""
    import uuid
    c = conn()
    run_id = f"run:{uuid.uuid4().hex[:12]}"
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    c.execute("""INSERT INTO oracle_ingest_runs
        (id, source_id, started_at, finished_at, status,
         records_seen, records_created, records_changed,
         records_unchanged, records_failed, error_summary)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (run_id, source_id, now, now, status,
         records_seen, records_created, records_changed,
         records_unchanged, records_failed, error_summary))
    c.commit()
    return run_id


def record_raw_observation(source_id: str, external_id: str, content_hash: str,
                           source_url: str = "", raw_blob_uri: str = "",
                           http_status: int = 200, metadata: dict = None) -> str:
    """Record a raw observation."""
    import uuid
    c = conn()
    obs_id = f"raw:{uuid.uuid4().hex[:12]}"
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    c.execute("""INSERT INTO oracle_raw_obs
        (id, source_id, external_id, observed_at, content_hash,
         raw_blob_uri, http_status, source_url, metadata)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (obs_id, source_id, external_id, now, content_hash,
         raw_blob_uri, http_status, source_url, json.dumps(metadata or {})))
    c.commit()
    return obs_id


def ensure_source(slug: str, name: str, source_type: str = "api",
                  website_url: str = "", adapter_name: str = "") -> str:
    """Ensure a source exists, return its ID."""
    c = conn()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    source_id = f"src:{slug}"
    c.execute("""INSERT OR REPLACE INTO oracle_sources
        (id, slug, name, source_type, website_url, adapter_name,
         created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?)""",
        (source_id, slug, name, source_type, website_url, adapter_name,
         now, now))
    c.commit()
    return source_id


def ensure_market(slug: str, name: str, market_type: str = "bounty",
                  website_url: str = "", agent_native: int = 0) -> str:
    """Ensure a market exists, return its ID."""
    c = conn()
    market_id = f"mkt:{slug}"
    c.execute("""INSERT OR REPLACE INTO oracle_markets
        (id, slug, name, market_type, website_url, agent_native)
        VALUES (?,?,?,?,?,?)""",
        (market_id, slug, name, market_type, website_url, agent_native))
    c.commit()
    return market_id


# ============================================
# QUERY HELPERS
# ============================================

def q(sql: str, params: tuple = ()) -> list[dict]:
    c = conn()
    rows = c.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def q1(sql: str, params: tuple = ()) -> dict | None:
    c = conn()
    row = c.execute(sql, params).fetchone()
    return dict(row) if row else None


def stats() -> dict:
    c = conn()
    s = {}
    for t in ["opp", "svc", "sub", "obs", "sig",
              "oracle_opps", "oracle_opp_obs", "oracle_opp_events",
              "oracle_skills", "oracle_categories"]:
        try:
            s[t] = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except:
            s[t] = 0
    try:
        s["opp_usd"] = c.execute("SELECT SUM(reward) FROM opp WHERE reward>0").fetchone()[0] or 0
    except:
        s["opp_usd"] = 0
    try:
        s["svc_calls"] = c.execute("SELECT SUM(calls) FROM svc").fetchone()[0] or 0
    except:
        s["svc_calls"] = 0
    try:
        s["oracle_usd"] = c.execute("SELECT SUM(reward_usd) FROM oracle_opps WHERE reward_usd>0").fetchone()[0] or 0
    except:
        s["oracle_usd"] = 0
    return s


# ============================================
# TAXONOMY-AWARE QUERIES (shared ontology)
# ============================================

def get_opps_by_task_family(task_family: str, status: str = "open",
                            limit: int = 50) -> list[dict]:
    """Get opportunities matching a canonical task family."""
    return q("""SELECT * FROM oracle_opps
        WHERE task_family = ? AND status = ?
        ORDER BY reward_usd DESC, last_seen_at DESC
        LIMIT ?""", (task_family, status, limit))


def get_opps_by_capability(capability: str, status: str = "open",
                           limit: int = 50) -> list[dict]:
    """Get opportunities requiring a specific capability."""
    return q("""SELECT * FROM oracle_opps
        WHERE canonical_capabilities LIKE ? AND status = ?
        ORDER BY reward_usd DESC, last_seen_at DESC
        LIMIT ?""", (f'%"{capability}"%', status, limit))


def get_opps_by_agent_caps(agent_caps: list[str], status: str = "open",
                           limit: int = 50) -> list[dict]:
    """Get opportunities matching any of the agent's capabilities.

    Returns opportunities where the agent has at least one required capability,
    sorted by reward (highest first).
    """
    if not agent_caps:
        return []
    # Build LIKE conditions for each capability
    conditions = " OR ".join(["canonical_capabilities LIKE ?"] * len(agent_caps))
    params = [f'%"{cap}"%' for cap in agent_caps] + [status, limit]
    return q(f"""SELECT * FROM oracle_opps
        WHERE ({conditions}) AND status = ?
        ORDER BY reward_usd DESC, last_seen_at DESC
        LIMIT ?""", tuple(params))


def get_taxonomy_stats() -> dict:
    """Get statistics per task family."""
    return {
        "by_task_family": q("""SELECT task_family, COUNT(*) as count,
            AVG(reward_usd) as avg_reward, SUM(reward_usd) as total_reward
            FROM oracle_opps WHERE task_family != ''
            GROUP BY task_family ORDER BY count DESC"""),
        "by_autonomy": q("""SELECT autonomy_level, COUNT(*) as count
            FROM oracle_opps WHERE autonomy_level != ''
            GROUP BY autonomy_level ORDER BY count DESC"""),
        "by_capability": q("""SELECT canonical_capabilities, COUNT(*) as count
            FROM oracle_opps WHERE canonical_capabilities != '[]'
            GROUP BY canonical_capabilities ORDER BY count DESC
            LIMIT 20"""),
    }


def get_agent_match_score(agent_caps: list[str], opp: dict) -> float:
    """Score how well an agent matches an opportunity (0.0 - 1.0).

    Based on capability overlap between agent and required capabilities.
    """
    if not agent_caps:
        return 0.0
    try:
        required = set(json.loads(opp.get("canonical_capabilities", "[]")))
    except:
        return 0.0
    if not required:
        return 0.5  # unknown requirements → neutral score
    overlap = set(agent_caps) & required
    return len(overlap) / len(required)


# ============================================
# DEMAND / SUPPLY INTELLIGENCE
# ============================================

def get_labor_demand() -> list[dict]:
    """Open labor demand by task family (total USD)."""
    return q("""SELECT task_family,
        COUNT(*) as open_opportunities,
        SUM(reward_usd) as total_demand_usd,
        AVG(reward_usd) as avg_reward_usd,
        COUNT(DISTINCT market_id) as source_count
        FROM oracle_opps
        WHERE status = 'open' AND task_family != ''
        GROUP BY task_family
        ORDER BY total_demand_usd DESC""")


def get_capability_demand() -> list[dict]:
    """Demand per capability extracted from canonical_capabilities JSON."""
    # This is a rough extraction — JSON array matching
    rows = q("""SELECT canonical_capabilities, reward_usd
        FROM oracle_opps WHERE status = 'open' AND canonical_capabilities != '[]'""")
    cap_demand: dict[str, dict] = {}
    for row in rows:
        try:
            caps = json.loads(row["canonical_capabilities"])
        except:
            continue
        for cap in caps:
            if cap not in cap_demand:
                cap_demand[cap] = {"capability": cap, "open_opportunities": 0,
                                   "total_demand_usd": 0}
            cap_demand[cap]["open_opportunities"] += 1
            cap_demand[cap]["total_demand_usd"] += row.get("reward_usd", 0) or 0
    result = sorted(cap_demand.values(), key=lambda x: x["total_demand_usd"], reverse=True)
    for r in result:
        r["total_demand_usd"] = round(r["total_demand_usd"], 2)
    return result


def get_supply_deficit(worker_caps: list[str]) -> dict:
    """Compare worker capabilities against market demand.

    Returns which capabilities the worker has vs what the market wants.
    """
    demand = get_capability_demand()
    had = set(worker_caps)
    demanded = {d["capability"]: d for d in demand}

    matched = []
    missing = []
    for cap, info in demanded.items():
        if cap in had:
            matched.append(info)
        else:
            missing.append(info)

    total_demand = sum(d["total_demand_usd"] for d in demand)
    matched_demand = sum(d["total_demand_usd"] for d in matched)

    return {
        "worker_capabilities": worker_caps,
        "matched_demand_usd": round(matched_demand, 2),
        "missing_demand_usd": round(total_demand - matched_demand, 2),
        "demand_coverage": round(matched_demand / max(1, total_demand), 4),
        "matched": matched[:10],
        "missing": missing[:10],
    }


def get_training_opportunities(worker_caps: list[str]) -> list[dict]:
    """What training would unlock the most demand?

    For each missing capability, estimate the demand it would unlock.
    """
    demand = get_capability_demand()
    had = set(worker_caps)

    opportunities = []
    for d in demand:
        if d["capability"] not in had:
            opportunities.append({
                "capability": d["capability"],
                "demand_usd": d["total_demand_usd"],
                "open_jobs": d["open_opportunities"],
                "priority": "HIGH" if d["total_demand_usd"] > 10000 else "MEDIUM" if d["total_demand_usd"] > 1000 else "LOW",
            })

    return sorted(opportunities, key=lambda x: x["demand_usd"], reverse=True)
