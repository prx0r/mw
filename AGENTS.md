# AGENTS.md — Oracle

> **Part of Tom's Lab.** Read `/root/AGENTS.md` for credentials, box rules, and full context.

## What This Is

Oracle is the market intelligence layer. It finds work, tracks opportunities.

## HydraDB — The Graph Database

**HydraDB is live.** Rust graph database on SlateDB, running in Docker.

```bash
# Status
docker ps | grep hydradb
# Ports: 7687 (Bolt), 8443 (HTTP), 9090 (Admin)

# Auth token
cat /root/workerkit/data/hydradb/auth-token
# → private-lab-hydradb-token-2026-secure
```

### Connection

```python
from neo4j import GraphDatabase

token = open('/root/workerkit/data/hydradb/auth-token').read().strip()
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', token))
```

### Cypher Syntax (limited)

```python
# Create node (use MERGE, not CREATE)
session.run('MERGE (n:Run {id: $id})', id='run-001')

# Create relationship
session.run('''
    MATCH (a:Run {id: $a_id}), (b:Run {id: $b_id})
    CREATE (a)-[:DEPENDS_ON]->(b)
''', a_id='run-001', b_id='run-002')

# Query with label
result = session.run('MATCH (n:Run) RETURN n.id AS id')

# Count
result = session.run('MATCH (n:Run) RETURN count(*) AS count')
```

### Restart

```bash
docker restart hydradb
```

- **Feeds** — crawlers for marketplaces (Metaculus, GitHub, MoltJobs, AgentPact, etc.)
- **API** — DeFiLlama-style REST endpoints (27 endpoints, port 8788)
- **MCP** — Model Context Protocol server (14 tools)
- **Store** — SQLite with 35 tables, append-only observations
- **Marketplace docs** — per-platform strategy, API docs, lab setup

## Architecture

```
SOURCE MARKETS → RAW OBSERVATIONS → NORMALIZE → CANONICAL WORK GRAPH
                                                          │
                                                 ┌────────┼────────┐
                                                 ▼        ▼        ▼
                                             Dashboard  API    Agents
```

## Key Files

| File | What |
|------|------|
| `api.py` | 27 REST endpoints (legacy + v1) |
| `feeds/work.py` | Normalizers for all marketplace feeds |
| `feeds/work.py:metaculus()` | Metaculus question feed (1220+ open) |
| `store.py` | Full schema + canonical functions |
| `cron.py` | Ingestion with observation tracking |
| `mcp.py` | MCP server — 14 tools |
| `models.py` | 12 core entity models |
| `dashboard.html` | Human queue GUI |
| `dashboard_server.py` | Backend API |
| `marketplaces/04-forecasting/metaculus/` | Metaculus strategy + bot |

## Run Commands

```bash
# Start API
python3 -m uvicorn oracle.api:app --host 0.0.0.0 --port 8788

# Query overview
curl http://localhost:8788/v1/totals

# Query Metaculus opportunities
curl "http://localhost:8788/v1/opportunities?market=metaculus"

# Run ingestion
python3 oracle/cron.py
```

## Current Priority: Metaculus Integration

Oracle discovers Metaculus questions. MWGym trains on them. WorkerKit submits.
The feed (`feeds/work.py:metaculus()`) normalizes questions to opportunity schema.

See `/root/AGENTS.md` §6 for the full pipeline.
