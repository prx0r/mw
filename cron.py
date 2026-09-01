"""Cron — continuous ingestion."""
from __future__ import annotations

import asyncio
import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from oracle.feeds.work import *
from oracle.feeds.svc import *
from oracle.feeds.sig import *
from oracle.store import upsert_opp, upsert_svc, upsert_sub, stats


def _record_obs(eid, src, metric, prev, curr):
    from oracle.store import conn
    c = conn()
    c.execute("INSERT INTO obs (entity_id,src,metric,prev_val,curr_val,observed) VALUES (?,?,?,?,?,?)",
        (eid, src, metric, json.dumps(prev), json.dumps(curr), time.strftime("%Y-%m-%dT%H:%M:%SZ")))
    c.commit(); c.close()


def _record_opp_obs(opp):
    """Record an observation for an opportunity (append-only)."""
    from oracle.store import conn
    c = conn()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    c.execute("""INSERT INTO oracle_opp_obs (opportunity_id, observed_at, status, reward_usd,
        applicant_count, submission_count, deadline_at, source_id)
        VALUES (?,?,?,?,?,?,?,?)""",
        (opp.get("id",""), now, opp.get("status",""), opp.get("reward",0) or 0,
         0, 0, opp.get("deadline",""), opp.get("src","")))
    c.commit(); c.close()


def _record_opp_event(opp, event_type, data=None):
    """Record an event for an opportunity (append-only)."""
    from oracle.store import conn
    c = conn()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    c.execute("""INSERT INTO oracle_opp_events (opportunity_id, event_type, occurred_at, observed_at, source_id, confidence)
        VALUES (?,?,?,?,?,?)""",
        (opp.get("id",""), event_type, now, now, opp.get("src",""), "observed"))
    c.commit(); c.close()


def _check_opp_changed(opp):
    """Check if opportunity has changed since last observation."""
    from oracle.store import conn
    c = conn()
    row = c.execute(
        "SELECT status, reward_usd FROM oracle_opp_obs WHERE opportunity_id=? ORDER BY observed_at DESC LIMIT 1",
        (opp.get("id",""),)).fetchone()
    c.close()
    if not row:
        return True  # New opportunity
    prev_status, prev_reward = row
    return (opp.get("status","") != prev_status or
            (opp.get("reward",0) or 0) != (prev_reward or 0))


def run_once():
    print(f"[{time.strftime('%H:%M:%S')}] Ingesting...")

    # Work feed
    work_fns = [bountybook, github, superteam, agenthansa, rentahuman, daydreams, openserv,
                nearai, agentlux, augmi, agentworld, atelier, clustly, taskforce, moltjobs,
                metaculus, immunefi, github_security_advisories, hackerone_programs]
    work_n = 0
    new_obs = 0
    for fn in work_fns:
        try:
            items = fn()
            for item in items:
                changed = _check_opp_changed(item)
                upsert_opp(item)
                work_n += 1
                if changed:
                    _record_opp_obs(item)
                    new_obs += 1
                    if new_obs <= 3:  # Log first few
                        _record_opp_event(item, "observed", {"reward": item.get("reward",0), "status": item.get("status","")})
        except: pass
    print(f"  Work: {work_n} ({new_obs} new observations)")

    # Service feed
    svc_fns = [x402engine, x402list, the402, payapi, apify, smithery, openrouter, bittensor,
               skyfire, apihub, agentictrade, fal]
    svc_n = 0
    for fn in svc_fns:
        try:
            items = fn()
            for item in items:
                upsert_svc(item)
                svc_n += 1
        except: pass
    print(f"  Svc: {svc_n}")

    # Signal feed
    sig_fns = [npm_downloads, hf_downloads, openrouter_models, agent_economy]
    sig_n = 0
    for fn in sig_fns:
        try:
            items = fn()
            sig_n += len(items)
        except: pass
    print(f"  Sig: {sig_n}")

    s = stats()
    print(f"  Total: {s['opp']} work + {s['svc']} svc + {s['obs']} obs")
    print(f"  Observations: {s.get('opp_obs',0)} opp_obs, {s.get('opp_events',0)} events")


import argparse
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--loop", action="store_true")
    p.add_argument("--interval", type=int, default=300)
    args = p.parse_args()
    if args.loop:
        while True: run_once(); time.sleep(args.interval)
    else:
        run_once()
