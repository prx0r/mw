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


def run_once():
    print(f"[{time.strftime('%H:%M:%S')}] Ingesting...")

    # Work feed
    work_fns = [bountybook, github, superteam, agenthansa, rentahuman, daydreams, openserv]
    work_n = 0
    for fn in work_fns:
        try:
            items = fn()
            for item in items:
                upsert_opp(item)
                work_n += 1
        except: pass
    print(f"  Work: {work_n}")

    # Service feed
    svc_fns = [x402engine, x402list, the402, payapi, apify, smithery, openrouter, bittensor]
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
