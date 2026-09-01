# AGENTS.md — WorkerKit

> **Part of Tom's Lab.** Read `/root/AGENTS.md` for credentials, box rules, and full context.

## What This Is

WorkerKit is the execution kernel. It does the work and records receipts.

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

### Cypher Syntax (limited — read this)

HydraDB implements a **deliberate subset** of OpenCypher. Key constraints:

| Feature | Support |
|---------|---------|
| `MATCH` | Yes, with id/label/property predicate required |
| `MERGE` | Yes, matched on id |
| `CREATE` | Relationship paths only (not nodes) |
| `RETURN` | `<binding>.<property>` or `count(*)` only |
| `DELETE` | Yes, after MATCH |
| `WHERE` | Boolean combos of property comparisons |
| Properties | integer, float, boolean, string literals only |

**Working patterns:**

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
for r in result:
    print(r['id'])

# Count
result = session.run('MATCH (n:Run) RETURN count(*) AS count')
print(result.single()['count'])

# Delete
session.run('MATCH (n:Run) DETACH DELETE n')
```

**Broken patterns (DO NOT USE):**

```python
# ❌ RETURN n (must use n.property)
session.run('MATCH (n) RETURN n')

# ❌ RETURN count(n) (must use count(*))
session.run('MATCH (n) RETURN count(n) AS c')

# ❌ CREATE node (use MERGE)
session.run('CREATE (n:Run {id: "x"})')

# ❌ CREATE with RETURN
session.run('CREATE (n:Run) RETURN n')
```

### Restart

```bash
docker restart hydradb
# Or recreate:
docker run -d --name hydradb \
  -p 7687:7687 -p 8443:8443 -p 9090:9090 \
  -v /root/workerkit/data/hydradb/data:/data \
  -e GRAPH_ALLOW_PLAINTEXT=true \
  -e GRAPH_AUTH_TOKEN_FILE=/data/auth-token \
  ghcr.io/hydra-db/hydradb:latest
``` This repo contains:

- **Venues** — platform adapters (Metaculus, GitHub, Moltwork, Virtuals)
- **Adapters** — worker adapters (Letta, direct, pydantic)
- **Campaigns** — create/run/grade/regrade lifecycle
- **MW LabKit** — FakeWorkerRuntime, MockHarbor, RunBinding
- **Providers** — BATS routing, model registry
- **Orchestration** — automation resolver, market packs

## API Keys (stored in /root/workerkit/.env)

```bash
# View keys (never commit these)
cat /root/workerkit/.env

# Available providers:
OPENCODE_API_KEY=sk-fv9...    # opencode-go/mimo-v2.5 (free)
GROQ_API_KEY=gsk_1J...        # groq models (paid, cheap)
CF_API_TOKEN=cfat_A...        # cloudflare R2 storage
HARBOR_API_KEY=sk-harbor...   # harbor framework
```

## Provider Registry (code access)

```python
from providers.registry import ProviderRegistry

reg = ProviderRegistry()
key = reg.get_key("opencode-go")  # returns API key
pricing = reg.get_pricing("groq/llama-3.3-70b-versatile")
cost = reg.estimate_cost(model, prompt_tokens, completion_tokens)
```

## LiveLLM (real-time pricing)

```bash
# Start LiveLLM
cd /root/livellm && npm run serve

# Query pricing
curl http://localhost:3847/v1/market
curl http://localhost:3847/v1/economics/GPT-4o
```

## BATS (budget-aware routing)

```python
from providers.bats import BATS, BudgetState

bats = BATS(reg)
budget = BudgetState(total_usd=0.10, remaining_usd=0.10)
decision = bats.select_model("coding", budget, uncertainty=0.7)
# → {"model": "groq/llama-3.3-70b-versatile", "reason": "high_uncertainty"}
```

## Key Files

| File | What |
|------|------|
| `venues/base.py` | WorkVenue protocol (discover, inspect, submit, status, settle) |
| `venues/metaculus.py` | **TO BUILD** — Metaculus venue adapter |
| `campaign.py` | Campaign lifecycle |
| `regrade.py` | v0/v1/v2 with calibration |
| `lab_brief.py` | Empirical memory for workers |
| `automation.py` | API→MCP→WebMCP→human ladder |
| `market_packs.py` | Platform configurations |
| `ontology.py` | Shared types |

## Model selection priority

1. Free models (opencode-go/mimo-v2.5) for routine tasks
2. Cheap models (groq) for medium uncertainty
3. Strong models (claude, gpt-4o) only for high-stakes decisions
4. Always check BATS before using paid models

## Current Priority: MetaculusVenue

The `venues/` directory has base protocol + 3 adapters. Need `venues/metaculus.py`
implementing WorkVenue:

- `discover()` → open tournament questions from Metaculus API
- `inspect()` → question details + community prediction
- `submit()` → POST forecast (binary/numeric/multiple_choice)
- `status()` → resolution check + Brier score
- `settle()` → (automatic — tournament prizes)
