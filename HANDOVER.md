# Oracle Handover — 2026-08-29 (Final)

## North Star

> **Build the best public dataset of autonomous economic activity on the internet.**

Moltwork = DefiLlama/Dune for economic work first, then execution layer, then production system market.

## What's Built

### Data (actually in the database)
```
440 canonical opportunities (oracle_opps)
441 legacy opportunities (opp)
576 services (svc)
626 skills (oracle_skills)
127 categories (oracle_categories)
552 opportunity observations (oracle_opp_obs)
447 opportunity events (oracle_opp_events)
882 legacy observations (obs)
```

### API (27 endpoints working)
```
Legacy: /pulse /work /svc /compare /history /observations /market-history
        /h-levels /work-receipts

V1 DeFiLlama-style:
  /v1/totals                    — overview metrics
  /v1/totals/by-market          — breakdown by market
  /v1/totals/by-category        — breakdown by category
  /v1/totals/by-skill           — breakdown by skill
  /v1/timeseries                — time-series data
  /v1/rankings                  — ranked tables
  /v1/opportunities             — filterable opportunity list
  /v1/opportunities/{id}        — single opportunity detail
  /v1/skills                    — skill taxonomy
  /v1/skills/trending           — trending skills
  /v1/categories                — category list
  /v1/sources                   — source health
  /v1/sources/{src}/opportunities — source opportunities
  /v1/events                    — event stream
  /v1/ingest/runs               — ingest run history
  /v1/rewards/distribution      — reward histogram
  /v1/compare                   — market comparison
```

### Database Schema (35 tables)
```
LEGACY TABLES
├── opp (441 rows) — opportunities
├── svc (576 rows) — services
├── sub (0 rows) — subnets
├── obs (882 rows) — observations
├── sig (0 rows) — signals
└── opp_obs, opp_events, market_snap, sources

ORACLE v1 TABLES
├── oracle_sources — data sources
├── oracle_ingest_runs — crawler invocations
├── oracle_raw_obs — immutable raw data
├── oracle_markets — marketplace registry
├── oracle_opps (440 rows) — canonical opportunities
├── oracle_opp_sources — multi-source mapping
├── oracle_opp_obs (552 rows) — append-only observations
├── oracle_opp_events (447 rows) — state change events
├── oracle_skills (626 rows) — skill taxonomy
├── oracle_opp_skills — opportunity-skill mapping
├── oracle_categories (127 rows) — category taxonomy
├── oracle_opp_categories — opportunity-category mapping
├── oracle_metric_defs — metric definitions
├── oracle_metric_points — raw metric data
├── oracle_daily_market — daily market rollups
├── oracle_daily_skill — daily skill rollups
└── oracle_daily_cat — daily category rollups

RELATED TABLES
├── actor, cap, sub_run, outcome, pay, pred
```

## Key Files

### Oracle (the data layer)
| File | Lines | Purpose |
|------|-------|---------|
| `store.py` | 450 | Full schema + canonical functions |
| `cron.py` | 90 | Ingestion with observation tracking |
| `api.py` | 730 | 27 REST endpoints (legacy + v1) |
| `models.py` | 150 | 12 core entity models |
| `mcp.py` | 200 | MCP server — 14 tools |
| `sdk.py` | 150 | Python SDK |
| `metrics.py` | 100 | O3 metrics |
| `ORACLE-SPEC.md` | 3126 | Full Oracle specification |
| `ORACLE-RESOURCES.md` | 1035 | Resource list for adapters |
| `ORACLE-DATA-MOAT.md` | 49 | Data moat architecture |
| `HANDOVER.md` | This file | Reference for fresh agent |

## How to Use

### Run Ingestion
```bash
cd /root
GITHUB_TOKEN="ghp_..." python3 oracle/cron.py
```

### Start API
```bash
cd /root
GITHUB_TOKEN="ghp_..." python3 -m uvicorn oracle.api:app --host 0.0.0.0 --port 8788
```

### Query Data (DeFiLlama-style)
```bash
# Overview metrics
curl http://localhost:8788/v1/totals

# Market comparison
curl http://localhost:8788/v1/totals/by-market

# Filter opportunities
curl "http://localhost:8788/v1/opportunities?market=superteam&min_reward=100"

# Skill rankings
curl http://localhost:8788/v1/rankings?kind=skill

# Reward distribution
curl http://localhost:8788/v1/rewards/distribution

# Event stream
curl "http://localhost:8788/v1/events?event_type=status_changed"
```

## Architecture

```
SOURCE MARKETS → RAW OBSERVATIONS → NORMALIZE → CANONICAL WORK GRAPH
                                                          │
                                                 ┌────────┼────────┐
                                                 ▼        ▼        ▼
                                             Dashboard  API    Agents
```

## Key Principle

```
append-only observations → current opportunity state
```

Never overwrite history. Record observations.

## What's Next

1. **Fix broken adapters** — Algora, MoltJobs, TOLL402, Coinbase Bazaar
2. **Add more GitHub repos** — expand beyond current 100
3. **Wire metric rollups** — populate daily_market, daily_skill, daily_cat
4. **Build SDK** — `from moltwork import Moltwork`
5. **Add Parquet export** — bulk data for researchers
6. **Algorand anchor** — Merkle root on-chain
