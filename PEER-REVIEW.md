# Peer review verdict

`mw` is the correct foundation. I would **not** move the `repute/oracle` code wholesale.

The distinction is:

* **`mw/oracle` has the better ontology and product boundary.**
* **`repute/oracle` has substantially better data-engineering depth.**
* **WorkerKit on `mw/master` has substantially better verification discipline than either oracle implementation.**
* The next move is to combine those strengths into one trunk.

`mw/oracle` already defines the right broad graph: Source, Market, Actor, Capability, Opportunity, Service, IncentiveMarket, Observation, Submission, Outcome, Payment, Prediction, plus WorkerKit receipt references.  Its own README already states the correct thesis: “the map of machine-work markets,” normalizing demand/supply and feeding WorkerKit/mwmarket.

But at the moment it is much more of a **normalized scraper with an analyst API** than a genuine DefiLlama-grade economic data system.

The biggest thing I would change is therefore:

> **Do not “pad out” `mw` with features. Pad out its historical evidence layer.**
>
> Current state → historical observations → outcomes/payments → derived metrics → WorkerKit feedback → market intelligence.

That is where the moat is.

---

# 1. The biggest architectural problem first: stop using branches as components

Right now `mw` effectively contains separate products as branches:

* `master` = WorkerKit
* `oracle` = Oracle
* `mwmarket` = marketplace
* `ethonline-2026` = protocol/TEE/ERC work

Your own handover describes exactly this state.

The ETHOnline branch additionally contains the protocol pieces—ERC-8004, ERC-8183, delegation, evidence, commitments, Phala/dstack TEE components—that are absent from `master`.  The `mwmarket` branch independently contains commitment/reveal/context-pack machinery.

This is going to become painful extremely quickly.

Make one canonical tree:

```text
mw/
├── workerkit/
│   ├── core/
│   ├── economics/
│   ├── verify/
│   ├── capabilities/
│   └── processes/
│
├── oracle/
│   ├── domain/
│   ├── events/
│   ├── ingestion/
│   ├── adapters/
│   ├── warehouse/
│   ├── analytics/
│   ├── resolution/
│   ├── api/
│   └── mcp/
│
├── protocol/
│   ├── attestations/
│   ├── commitments/
│   ├── erc8004/
│   ├── erc8183/
│   ├── delegation/
│   └── tee/
│
├── market/
│   ├── commitments/
│   ├── reveal/
│   ├── listings/
│   └── settlement/
│
├── web/
│   ├── app/
│   ├── components/
│   ├── charts/
│   ├── tables/
│   └── api/
│
├── tests/
├── docs/
└── pyproject.toml
```

There should be exactly one canonical `Opportunity`, one canonical receipt schema, one canonical event model, and one canonical definition of every public identifier.

Branches become branches again—not package managers.

---

# 2. What is actually better in `repute`

There are five important ideas in `repute/oracle` that `mw` should recover.

## A. Immutable events + versioned payloads

This is probably the biggest regression in the cleaned-up version.

`repute` has a proper `EventEnvelope` containing:

* event ID
* event type
* schema/version
* source
* native source ID
* observed timestamp
* effective timestamp
* subject
* payload
* provenance
* raw hash

It also has explicit confidence classifications such as on-chain verified, source verified, directly observed, derived, inferred, user reported, and unknown.

That is excellent.

The current `mw` model has `Observation` and `raw_latest`, but that is not enough.

You need to distinguish:

```text
SOURCE SAID:
reward = 500 USDC

ORACLE DERIVED:
reward_usd = $498.72

WORKERKIT OBSERVED:
actual cost = $1.83

CHAIN VERIFIED:
actual payout = $500

ORACLE INFERRED:
estimated net EV = $83.14
```

Those are fundamentally different types of knowledge.

### Bring this concept back.

But make it smaller and more disciplined than the `repute` version.

---

## B. Observation intervals

This is possibly the most valuable code in `repute`.

A scraper usually sees:

```text
10:00 proposals = 0
10:15 proposals = 4
```

It **doesn't** know the first proposal occurred at 10:07.

`repute` correctly models that change as occurring between two observations instead of fabricating an exact timestamp. It stores `interval_after` and `interval_before`, diffs fields, and derives things like:

* time to first bid
* time to claim
* time to completion
* proposal velocity
* competition at claim

This is exactly the sort of data that turns Moltwork from:

> “here are some jobs”

into:

> “Here is how autonomous-work markets actually behave.”

Bring this back almost immediately.

---

## C. The richer economic opportunity specification

The old `OpportunitySpec` models much more than reward:

* capabilities
* deliverables
* credentials
* hardware
* evaluation method
* reward model
* entry fee
* gas
* capital required
* capital at risk
* lock time
* competitors
* slots
* estimated compute
* API spend
* estimated human intervention
* submission mechanism
* probability of award/acceptance
* expected payout
* expected net value

It also defines a very useful conceptual platform lifecycle:

```text
discover
→ hydrate
→ preflight
→ enter
→ submit
→ status
→ outcome
→ settlement
```

Don't bring the giant dataclass back verbatim.

Instead split it into:

```text
Opportunity
OpportunityRequirements
OpportunityEconomics
OpportunityCompetition
OpportunityExecution
OpportunityPrediction
```

That avoids turning `Opportunity` into a 70-field monster.

---

## D. Source breadth

`repute` accumulated adapters for a much broader ecosystem: x402 directories, agent marketplaces, GitHub, Superteam-style work, NEAR, Olas, Virtuals, Bittensor, API/service markets and others.

The source research itself is useful.

The architecture of those adapters is less useful.

Bring over:

* URLs/API knowledge
* authentication notes
* source peculiarities
* sample responses
* normalization mappings
* pagination knowledge
* lifecycle semantics

Then rewrite adapters under one strict interface.

---

## E. Merkle batching — idea yes, implementation no

The old code builds Merkle roots and inclusion proofs over observation/event hashes.

That idea fits Moltwork extremely well.

But **do not copy its `get_checkpoint_for_event()` implementation**.

It attempts to determine whether a cryptographic hash lies inside a batch by treating hashes as an integer range between the first and last hash. Cryptographic hashes have no meaningful ordering like that, so this cannot prove membership.

Your new design should store explicit membership:

```text
checkpoint
  batch_id
  root_hash
  start_sequence
  end_sequence
  created_at
  anchor_tx

checkpoint_leaf
  batch_id
  event_id
  leaf_index
  content_hash
```

Then produce a real Merkle proof by leaf index.

And because WorkerKit already has hash-linked event chains and receipt evidence, the Oracle should reuse the same canonical hashing code rather than inventing another subtly different canonicalizer.

---

# 3. Where `mw/oracle` is currently weak

There is some deceptively serious technical debt hiding inside the clean implementation.

## P0 — “Append-only” isn't actually append-only

`store.py` calls itself:

> `SQLite storage — append-only.`

But `opp`, `svc`, etc. are updated through `INSERT OR REPLACE`.

That's fine for **current-state projections**.

It is not fine as your historical source of truth.

You want:

```text
immutable events
      ↓
current-state projections
      ↓
materialized analytics
```

Not:

```text
scrape
→ overwrite latest row
→ hope observations captured enough
```

Current tables should be explicitly named projections.

For example:

```text
oracle_events            append-only source of truth

opportunity_current      mutable projection
service_current          mutable projection
actor_current            mutable projection

metric_hourly            derived
metric_daily             derived
```

---

# 4. Current observations aren't sufficient

`upsert_opp()` only records an observation when the opportunity is first inserted—and then only initial status and reward. Subsequent replacements don't perform a general old/new diff.

That means you're throwing away precisely the history that becomes valuable later.

You should track changes in:

```text
status
reward
reward asset
deadline
proposal count
submission count
claimed worker
views/activity
winner
actual payout
payment status
requirements
slots
service price
service usage
provider reputation
market participation
```

Anything useful enough to display should generally have history behind it.

---

# 5. Your “metrics” aren't yet economic metrics

The six families are a good taxonomy:

* Demand
* Supply
* Transactions
* Outcomes
* Economics
* Efficiency

But the implementation is thin.

For example:

**Transactions** currently means roughly “opportunities with a reward.”

That isn't a transaction.

**Outcomes** mostly means opportunity status counts.

**Efficiency** mostly means open rate versus close rate.

Keep the taxonomy; completely deepen the implementation.

---

# 6. Adapter reliability needs a real substrate

Current feed modules repeatedly do approximately:

```python
try:
    urllib.request...
except:
    return None
```

This occurs throughout the current work/service/signal feeds.

That makes it impossible to distinguish:

```text
source has zero opportunities
```

from:

```text
our parser broke
```

from:

```text
source returned 429
```

from:

```text
their API changed
```

from:

```text
DNS exploded
```

For a data product, that's a major problem.

---

# 7. Your API is becoming another god-file

`api.py` is already doing:

* request handling
* window parsing
* SQL
* aggregation
* JSON decoding
* business logic
* analytics

all directly in routes.

This is exactly how you eventually end up with `repute/oracle/api.py` at ~71 KB.

Stop it now while `mw` is still clean.

---

# 8. Repo hygiene has regressed on the Oracle branch

The `oracle` branch contains:

* `__pycache__`
* `oracle.db`
* `oracle.db-shm`
* `oracle.db-wal`

Meanwhile your current WorkerKit master explicitly cleaned generated DB/cache state from git.

Fix this while integrating the branches.

Fixtures belong in `tests/fixtures/`; runtime databases don't.

---

# 9. The important thing `mw` already gets right

Do **not** compromise WorkerKit to accommodate Oracle.

Your current handover gets the relationship right:

```text
Oracle opportunity
       ↓
Economics
       ↓
WorkerKit
       ↓
Receipt / proof
       ↓
Outcome / settlement
       ↓
Oracle learns
```

Oracle should never become part of WorkerKit's trusted execution kernel.

Instead:

```text
Oracle → suggestion / external evidence
WorkerKit → controlled execution evidence
Market → transaction evidence
Chain → settlement evidence

              ↓

        Oracle warehouse
```

This separation is extremely good.

---

# 10. The target Moltwork architecture

I would formalize the system into four truth layers.

```text
                    MOLTWORK DATA PLANE

┌─────────────────────────────────────────────────────────────┐
│ L0 — RAW EVIDENCE                                           │
│ source responses, chain events, WorkerKit receipts          │
│ immutable, content-addressed                                │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ L1 — EVENTS                                                 │
│ opportunity.observed                                       │
│ reward.changed                                             │
│ submission.observed                                        │
│ outcome.observed                                           │
│ payment.observed                                           │
│ workerkit.run.completed                                    │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ L2 — CURRENT GRAPH                                          │
│ Opportunity / Market / Actor / Service / Capability         │
│ Submission / Outcome / Payment                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ L3 — INTELLIGENCE                                           │
│ metrics, trends, EV, competition, capability economics      │
│ forecasts + confidence                                     │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
                    BOARD / API / MCP
```

That is the DefiLlama-like data architecture you actually want.

---

# 11. Canonical Event v1

This should be one of the very next PRs.

```python
OracleEvent(
    event_id,
    sequence,

    event_type,
    schema_version,

    source_id,
    source_record_id,

    subject_type,
    subject_id,

    observed_at,
    effective_at,

    interval_after,
    interval_before,

    confidence,

    payload,
    provenance,

    raw_hash,
    content_hash,
)
```

### Confidence

Use an enum approximately:

```text
UNKNOWN
USER_REPORTED
INFERRED
DERIVED
OBSERVED
SOURCE_VERIFIED
PAYMENT_VERIFIED
TEE_VERIFIED
REEXECUTED
ZK_VERIFIED
```

This also lines up beautifully with the evidence hierarchy you have already specified for the protocol.

Do **not** wrap every primitive value inside a gigantic `Evidence[T]` structure.

Event-level provenance is sufficient for most data.

Use explicit field provenance only for important transformed values such as:

* USD conversion
* payout
* identity
* status
* reputation
* verification

---

# 12. Raw evidence store

Create:

```text
raw_blob
---------
hash PK
source_id
content_type
encoding
size_bytes
retrieved_at
storage_uri
```

For small deployments, blobs can initially just be gzipped files:

```text
data/raw/sha256/ab/cd/abcdef...
```

Then `OracleEvent.raw_hash` points to it.

Eventually R2/S3/IPFS/etc. is trivial.

This gives you:

* reproducible normalization
* adapter debugging
* parser regression testing
* independent verification
* backfills
* evidence trails

That is vastly more useful than keeping `raw_latest` inside a current opportunity row.

---

# 13. Source registry

Every source gets a first-class record.

```text
Source
  id
  name
  homepage
  source_type

  domains[]
  chains[]
  markets[]

  authentication
  machine_accessible

  discovery_mode
  polling_interval_class

  adapter_version
  schema_version

  expected_freshness
  rate_limit_notes

  supports:
    discover
    hydrate
    competition
    outcome
    payment
    actors
    submissions

  status
```

And operational state:

```text
SourceRun
  run_id
  source_id
  started_at
  finished_at
  status

  requested
  received
  inserted
  updated
  unchanged
  rejected

  http_2xx
  http_4xx
  http_5xx

  parse_errors
  normalization_errors

  cursor_before
  cursor_after

  error_type
  error_message
```

This single addition will make `/data-health` genuinely useful.

---

# 14. One strict adapter contract

Replace giant `work.py`, `svc.py`, etc. with one adapter per source.

```python
class OracleAdapter(Protocol):

    source: SourceDefinition

    async def discover(
        self,
        cursor: Cursor | None
    ) -> DiscoveryPage:
        ...

    async def hydrate(
        self,
        native_id: str
    ) -> RawRecord:
        ...

    def normalize(
        self,
        raw: RawRecord
    ) -> list[OracleEvent]:
        ...

    async def reconcile(
        self,
        known: CurrentState
    ) -> list[OracleEvent]:
        ...
```

Optional capabilities:

```text
get_actor
get_competition
get_submissions
get_outcome
get_settlement
```

Never require an adapter to pretend it supports something it doesn't.

---

# 15. Shared HTTP client

One implementation for every web adapter.

It needs:

* explicit timeouts
* retry policy
* `Retry-After`
* rate limiting
* structured errors
* compression
* conditional requests (`ETag`, `Last-Modified`)
* request IDs
* response metadata
* caching
* user agent
* bounded payload size
* JSON/content-type validation

Every source run needs to know exactly why it failed.

A broken adapter should degrade one source—not silently turn the market into zero.

---

# 16. Lifecycle reconciliation

This is a huge missing capability.

Suppose an opportunity was previously visible but disappears.

Don't immediately say:

```text
status = closed
```

You don't know that.

Use states like:

```text
OPEN
CLAIMED
SUBMISSION_OPEN
SUBMITTED
AWARDED
COMPLETED
PAID
REJECTED
EXPIRED

SOURCE_MISSING
UNKNOWN
```

And distinguish:

```text
source explicitly reports CLOSED
```

from:

```text
our poll didn't find it
```

After N successful full reconciliations without the item, you can derive likely closure with `DERIVED` confidence.

This matters massively once people use the data to allocate actual agent effort.

---

# 17. Canonical entity resolution

You'll inevitably see the same thing in multiple sources.

Add:

```text
entity
entity_alias
entity_relation
resolution_candidate
```

Example:

```text
entity_alias:
  source = github
  native_id = owner/repo#123

→ opportunity:mw_abc123
```

Don't fuzzy merge automatically.

Use deterministic keys first:

* contract
* transaction
* URL
* GitHub repo + issue
* canonical source ID
* wallet
* ERC-8004 identifier

Then fuzzy matching merely proposes aliases.

---

# 18. Canonical taxonomy

Current `/demand` directly compares work `skills` against service `cat` strings.

That won't scale.

Make one real capability tree.

```text
research
├── web-research
├── scientific-research
└── market-research

software
├── python
├── typescript
├── solidity
├── rust
└── frontend

content
├── writing
├── image
└── video

data
├── scraping
├── extraction
├── classification
└── analysis
```

And relations:

```text
Opportunity REQUIRES Capability
Service PROVIDES Capability
Actor DEMONSTRATED Capability
Process USES Capability
Artifact DEMONSTRATES Capability
```

That creates an actual knowledge graph rather than comparing tags.

---

# 19. WorkerKit becomes the highest-quality first-party feed

This is where the whole architecture gets powerful.

WorkerKit already records controlled economic evidence and content-addressed receipts. Your handover explicitly says Oracle currently needs to consume the lifecycle outputs without being embedded inside WorkerKit.

Have it emit:

```text
workerkit.run.started
workerkit.cost.observed
workerkit.artifact.created
workerkit.verification.completed
workerkit.submission.committed
workerkit.outcome.observed
workerkit.settlement.observed
```

Then join:

```text
Oracle Opportunity
      ↓
Prediction
      ↓
WorkerKit Run
      ↓
Submission
      ↓
Outcome
      ↓
Payment
```

This yields something extraordinarily useful:

```text
predicted cost       $0.82
actual cost          $1.04

predicted p_accept   0.68
actual               accepted

predicted net EV     $12.40
realized net         $18.96
```

Now you can improve the predictor from actual experience.

---

# 20. Build the prediction calibration dataset now

Don't worry initially about fancy ML.

Store every prediction before execution:

```text
PredictionSnapshot
  prediction_id
  opportunity_id
  worker_id

  model_version

  estimated_cost
  estimated_duration
  p_enter
  p_finish
  p_accept
  p_paid

  expected_gross
  expected_net

  confidence_low
  confidence_high

  computed_at
```

Never mutate it after the result.

Later attach:

```text
PredictionEvaluation
  actual_cost
  actual_duration
  actual_accept
  actual_paid
  actual_net

  cost_error
  payout_error
  probability_calibration
```

This becomes a genuine economic-routing dataset.

---

# 21. Metrics v2 — this is the real Oracle

Your existing six families are worth preserving.

Completely upgrade what lives inside them.

## A. Demand

```text
open_opportunities
open_reward_pool_usd

new_opportunities_24h
new_reward_usd_24h

median_reward
p25 / p75 / p95 reward

reward by capability
reward by market
reward by chain
reward by human level

opportunity creation velocity
reward creation velocity
```

## B. Supply

```text
active_agents
active_verified_agents

available_services
service calls

agents by capability
verified capability supply

compute/service price distributions

agent utilization
service utilization
```

## C. Transactions

This should mean actual economic activity:

```text
submissions
awards
acceptances
payments

gross payment volume
verified payment volume

average transaction value
median transaction value

volume by market
volume by worker
volume by capability
```

Not “listings containing rewards.”

## D. Outcomes

```text
submission → award rate
award → acceptance rate
acceptance → payment rate

overall paid rate

failure rate
expiry rate

median rank
average evaluation score

time to outcome
time to payment
```

## E. Economics

```text
advertised reward
realized payout

compute spend
API spend
gas spend
human cost estimate

gross margin
net margin

predicted EV
realized EV

cost per accepted submission
cost per dollar earned

agent earnings
buyer spend
```

## F. Market Efficiency

This is where Moltwork becomes interesting:

```text
median time to first proposal
proposal velocity

time to claim
time to submission
time to fill
time to settlement

competition per opportunity

reward / competitor
reward / required capability

fill rate

unfilled high-value demand

supply/demand ratio by capability

market concentration

automation-ready share
verified-work share
```

---

# 22. Add a seventh metric family: Data Quality

DefiLlama can implicitly rely on its reputation for data quality.

Moltwork is early and aggregating much stranger sources.

Make the uncertainty explicit.

```text
coverage
freshness
completeness
source success rate
observation density
verified share
payment-verified share

last successful poll
median ingest lag

field completeness
unknown-status share

normalization rejection rate
```

This should be visible publicly.

It is not embarrassing.

It actually makes the product credible.

---

# 23. Materialized timeseries

A DefiLlama-style board cannot compute everything from raw rows on every request.

Create:

```text
metric_hourly
metric_daily
```

Generic structure:

```text
timestamp
metric
scope_type
scope_id
value
sample_count
confidence
```

Examples:

```text
2026-08-29T13:00
open_reward_usd
GLOBAL
*
184392.32

2026-08-29T13:00
median_reward_usd
MARKET
superteam
400

2026-08-29T13:00
paid_volume_usd
CAPABILITY
research
1832
```

This single abstraction makes arbitrary dashboard overlays easy.

---

# 24. Metrics catalog

Also create:

```json
{
  "id": "paid_volume_usd",
  "name": "Paid Volume",
  "description": "Observed completed payments...",
  "unit": "usd",
  "aggregation": "sum",
  "periods": ["1h", "24h", "7d", "30d"],
  "confidence_requirement": "source_verified",
  "available_scopes": [
    "global",
    "market",
    "capability",
    "agent"
  ]
}
```

This powers:

* dashboard metric picker
* MCP
* API documentation
* CSV export
* custom dashboards

from the same definition.

That is exactly the kind of architecture which prevents frontend/backend drift.

---

# 25. API v1

Stop growing the existing short routes directly.

Keep them temporarily as compatibility wrappers.

New interface:

```text
GET /v1/overview

GET /v1/metrics
GET /v1/metrics/catalog
GET /v1/series

GET /v1/markets
GET /v1/markets/{id}

GET /v1/opportunities
GET /v1/opportunities/{id}

GET /v1/services
GET /v1/services/{id}

GET /v1/agents
GET /v1/agents/{id}

GET /v1/capabilities
GET /v1/capabilities/{id}

GET /v1/submissions
GET /v1/outcomes
GET /v1/payments

GET /v1/workerkit/runs
GET /v1/workerkit/receipts/{digest}

GET /v1/events
GET /v1/sources
GET /v1/sources/{id}/health

GET /v1/rankings/markets
GET /v1/rankings/agents
GET /v1/rankings/capabilities

GET /v1/search
```

Filters become consistent:

```text
?window=30d
&source=
&market=
&chain=
&capability=
&status=
&human_level=
&confidence=
&min_reward=
&cursor=
&limit=
```

---

# 26. API engineering requirements

Every endpoint should have:

* Pydantic response models
* versioned schema
* cursor pagination
* sane upper limits
* consistent error envelopes
* stable IDs
* query metadata
* freshness metadata
* source/provenance metadata where appropriate
* caching headers
* OpenAPI examples

Don't return arbitrary SQLite rows to clients.

---

# 27. MCP should become first class

This is another lesson worth taking from DefiLlama.

DefiLlama now exposes its data through an MCP interface alongside its web/API surfaces and maps its metrics into agent-oriented tools. ([DefiLlama][1])

Moltwork should do exactly that for machine work.

Instead of 40 arbitrary endpoints exposed as MCP tools, use perhaps:

```text
search_opportunities
get_opportunity

rank_opportunities
compare_markets
get_market_metrics

find_services
find_agents

get_capability_demand
get_capability_supply

estimate_opportunity_economics

get_worker_history
get_verified_receipt

get_source_health
```

And make `search_opportunities` extremely good.

That is probably your most important external integration surface.

---

# 28. Now the dashboard: don't clone DefiLlama's skin

Clone its **information architecture**.

Current DefiLlama has:

* a broad metric/domain navigation system
* scope filters
* one headline market number
* key metrics underneath
* configurable chart metrics
* export/embed controls
* dense searchable rankings
* timeframe switches
* configurable table columns and metric families

([DefiLlama][2])

Its metrics directory also separates a large number of metric surfaces while keeping them searchable rather than trying to put everything on one homepage. ([DefiLlama][3])

That's the important part.

Your board should feel like:

> **a terminal for machine labor**

not:

> a crypto marketplace landing page.

---

# 29. Proposed Moltwork navigation

```text
MOL TWORK

OVERVIEW
  Market Overview

WORK
  Opportunities
  Markets
  Bounties
  Incentives
  Services

INTELLIGENCE
  Demand
  Supply
  Economics
  Outcomes
  Capabilities
  Trends

PARTICIPANTS
  Agents
  Buyers
  Sellers

VERIFICATION
  WorkerKit Runs
  Receipts
  Attestations
  Settlements

DATA
  Sources
  Data Health
  Methodology

TOOLS
  Compare
  Watchlist
  Export
  API
  MCP
```

Chain filters then sit above content:

```text
All | Ethereum | Base | Solana | NEAR | Bittensor | Web2 | ...
```

And source filters:

```text
All | GitHub | Superteam | BountyBook | x402 | Virtuals | ...
```

These are facets, not separate architectures.

---

# 30. The new overview page

## Header

Very restrained.

```text
Machine Work Overview

All markets · All chains · Confidence ≥ Observed
Last updated 34s ago
```

Then ONE main headline:

```text
OPEN MACHINE-PAYABLE WORK

$184,392
+8.2% 24h
```

Don't show twelve giant gradient cards.

---

# 31. Key metrics row

Six compact cells:

| Metric             |  Value | Change |
| ------------------ | -----: | -----: |
| New Work 24h       | $18.4K |   +14% |
| Paid Volume 7d     | $42.1K |    +6% |
| Open Opportunities |  1,284 |    +9% |
| Median Reward      |   $125 |    -3% |
| Automation Ready   |    63% |    +2% |
| Verified Outcomes  |    418 |   +18% |

Then small secondary information:

```text
Markets 31
Sources healthy 27/29
Verified agents 412
Payments observed 2,193
```

Dense. Not oversized.

---

# 32. Main chart

This should be a major piece of the screen.

```text
Open Work USD
────────────────────────────────────

[24H] [7D] [30D] [90D] [1Y] [ALL]

+ Add metric

Currently:
● Open Work USD
● Paid Volume USD
```

Metric picker:

```text
Demand
  Open reward pool
  New work
  Opportunity count

Economics
  Paid volume
  Median reward
  Agent costs
  Net earnings

Outcomes
  Acceptance rate
  Payment rate

Efficiency
  Competition
  Time to fill

Verification
  Verified runs
  Attested settlements
```

DefiLlama's current overview similarly allows adding metrics to its main chart and exposes CSV/image/embed tooling. ([DefiLlama][2])

Steal that interaction.

---

# 33. The most important homepage component: Market Rankings

This should occupy a huge proportion of the page.

```text
MARKET RANKINGS

Search markets...

[Demand] [Outcomes] [Economics] [Efficiency] [Quality]

                 Open       New      Paid       Median   Competition
Market           Work       24h      7d         Reward   Index
────────────────────────────────────────────────────────────────────
Superteam        $82K       $9K      $12K        $500       4.2
GitHub           $41K       $3K       $8K        $240       2.7
BountyBook       $22K       $5K       $11K       $120       1.4
...
```

Time switch:

```text
1d | 7d | 30d
```

Column chooser.

CSV.

Search.

Sort everything.

Pin/watch.

Compare.

DefiLlama's protocol rankings use essentially this dense table model with search, horizons, metric toggles and configurable columns. ([DefiLlama][2])

This will instantly make Moltwork feel much more substantial.

---

# 34. Opportunities explorer

Another proper terminal-like table:

```text
Title
Market
Reward
Net EV
Cost
P(Paid)
Competition
Human
Deadline
Confidence
Freshness
```

Example filters:

```text
Reward ≥ $50
EV > 0
H0-H1
Python
Deadline > 24h
Confidence ≥ observed
Competition < 5
```

This is where the Oracle connects directly to WorkerKit.

Click:

```text
Evaluate with WorkerKit
```

And get:

```text
estimated cost
available capabilities
missing credentials
estimated duration
historical comparable runs
estimated net EV
```

Not auto-execute. Just prepare a WorkOrder.

---

# 35. Opportunity detail page

This can become extremely good.

Top:

```text
BUILD SOLIDITY INDEXER

Superteam
$1,500 USDC
Open
H1
Source verified
Last observed 41s ago
```

Metrics:

```text
Reward        $1,500
Est. cost     $7.20
Est. net      $492
P(accept)     0.33

Entries        9
Bid velocity   0.8/h
Age            3d
Deadline       4d
```

Then:

```text
[Overview]
[Requirements]
[Competition]
[History]
[Runs]
[Evidence]
```

History shows:

```text
created
↓
reward changed
↓
proposals 0 → 3
↓
proposals 3 → 9
↓
...
```

Every event links to provenance.

That is fantastic demo material.

---

# 36. Market detail page

Equivalent of a DefiLlama protocol page.

```text
SUPERTEAM

Open Work                  $82,183
Paid Volume 30d            $41,982
Median Reward              $500
Fill Rate                  62%
Median Time to First Bid   3h 14m
Automation Ready           71%
```

Chart.

Then:

```text
Demand
Outcomes
Capabilities
Participants
Historical data
Source health
```

And table of current opportunities.

---

# 37. Capability detail page

This could become one of Moltwork's coolest unique surfaces.

Example:

```text
PYTHON

Demand                     $43,210
New Demand 7d              +18%
Opportunities              184
Verified Workers           82
Demand/Supply              2.24
Median Reward              $310
Median Agent Cost          $1.83
Observed Paid Volume       $18,420
```

Charts:

```text
reward demand vs worker supply
median reward
verified success rate
```

Tables:

```text
top markets buying Python
top verified workers
best-performing processes
related capabilities
```

This gives you something DefiLlama doesn't have an analogue for because you're mapping labor rather than capital.

---

# 38. Agent pages

Do not make these social-media profiles.

Make them analytical profiles.

```text
AGENT 8004:0x...

Verified runs       142
Paid outcomes        61
Gross earned         $4,832
Execution spend      $418
Net earned           $4,414

Acceptance rate      72%
Settlement rate      98%
Median cost/run      $0.93
```

Capability matrix:

```text
Research       ████████  high confidence
Python         ██████
Solidity       ███
Design         █
```

Everything derived from evidence.

No meaningless “AI agent rating: 9.8/10”.

---

# 39. WorkerKit page

This is what makes the board more than another scraper.

```text
VERIFIED MACHINE WORK

Verified runs        18,283
Artifacts            42,182
Total execution cost $31,812
Settlements          $183,281
```

Recent runs:

```text
run
worker
opportunity
process
cost
verification
outcome
receipt
attestation
```

And a receipt explorer.

Eventually:

```text
Evidence
✓ WorkerKit chain
✓ Artifact digest
✓ TEE attestation
✓ ERC-8004 identity
✓ ERC-8183 settlement
```

That will look excellent in an ETHOnline demo because the cryptographic work has an understandable UI.

---

# 40. Source Health page

This is essential.

```text
SOURCE HEALTH

Source       Status   Last Sync   Lag    Records  Errors   Coverage
────────────────────────────────────────────────────────────────────
GitHub       ●        22s         31s    8,413    0.1%     93%
Superteam    ●        48s         51s      821    0.0%     96%
Foo          ●        7m          8m       118    1.8%     71%
BrokenAPI    ●        2h          2h        31   81.2%     22%
```

Click source:

```text
API method
adapter version
schema version
successful runs
response latency
field completeness
last errors
records/day
raw examples
methodology
```

This gives Moltwork a transparent “open data” feel.

---

# 41. Evidence should be part of the visual language

Every number can optionally expose:

```text
● Chain verified
● TEE verified
● Source verified
● Observed
● Derived
● Inferred
```

You don't need giant badges everywhere.

Tiny icon/chip + hover details.

Example:

```text
Paid Volume 7d
$41,208
◉ 96% payment verified
```

This is a genuinely distinctive design system for Moltwork.

---

# 42. Global command/search

Press `/` or `Cmd-K`:

```text
Search Moltwork

> python

Capabilities
  Python

Opportunities
  Python scraper bounty — $800
  Python API integration — $240

Agents
  Agent 0xa1... — 84 verified Python runs

Markets
  ...

Metrics
  Python paid volume
  Python demand/supply
```

The data graph makes this easy once entity resolution exists.

---

# 43. Frontend implementation

I don't see a meaningful dashboard/frontend implementation in the `master`, `oracle`, `mwmarket`, or `ethonline-2026` trees I inspected, so I wouldn't try to preserve a current frontend architecture merely for continuity. The Oracle branch itself is backend/API/feed code.

For the actual board, keep it boring technically:

```text
React + TypeScript
TanStack Query
TanStack Table
TanStack Virtual
ECharts
Radix primitives or equivalent
```

Use custom Moltwork CSS/design tokens.

Avoid making it look like default shadcn.

The UI identity should come from:

* typography
* spacing
* table density
* chart styling
* evidence notation
* data hierarchy

not decorative components.

If you already have a React frontend elsewhere, keep the framework and apply this information architecture rather than doing a rewrite for its own sake.

---

# 44. Dashboard backend endpoints

Build these before spending serious time on CSS:

```text
/v1/overview
/v1/series
/v1/rankings/markets
/v1/rankings/capabilities
/v1/rankings/agents
/v1/opportunities
/v1/search
/v1/sources/health
```

The entire first useful dashboard can be built from those eight endpoints.

That's intentional.

---

# 45. Ordered implementation plan

This is the order I would actually give the coding agent.

## P0 — Converge the repo

**Do this before adding more features.**

1. Merge Oracle into `/oracle`.
2. Merge market into `/market`.
3. Bring protocol/TEE/chain code from `ethonline-2026` into `/protocol`.
4. Keep WorkerKit isolated under `/workerkit`, or preserve root temporarily with compatibility imports.
5. Delete committed `__pycache__`.
6. Delete committed Oracle DB/WAL/SHM.
7. Expand `.gitignore`.
8. Add fixture directory.
9. Establish a single package/import layout.
10. Run WorkerKit's invariant suite after every move.

**Done when:** one checkout contains the entire product and WorkerKit invariants still pass.

---

# P1 — Freeze identifiers and schema boundaries

11. Define canonical IDs:

* `src_*`
* `mkt_*`
* `opp_*`
* `actor_*`
* `svc_*`
* `run_*`
* `evt_*`

12. Define canonical lifecycle enums.
13. Define evidence/confidence enum.
14. Define currency semantics.
15. Define timestamp conventions.
16. Define capability taxonomy version.
17. Define source-native alias rules.
18. Create schema version registry.
19. Add migration framework.
20. Write `docs/DATA-MODEL.md`.

**Do not proceed to massive adapter migration until these are stable.**

---

# P2 — Build OracleEvent

21. Implement canonical serialization.
22. Full SHA-256 content hashes.
23. Immutable events table.
24. Deduplication by content hash/source semantics.
25. Subject identity.
26. observed/effective times.
27. uncertainty intervals.
28. provenance.
29. raw hash.
30. correction events.
31. event query API.
32. brutal tamper/canonicalization tests.

Reuse the discipline already established in WorkerKit.

---

# P3 — Raw evidence

33. Implement content-addressed raw store.
34. Store source responses before normalization.
35. Hash responses.
36. Link event → raw blob.
37. Compression.
38. retention policy.
39. fixture exporter.
40. replay normalizer against old raw blobs.

**Done when:** changing an adapter parser allows historical raw records to be re-normalized without contacting the original source.

---

# P4 — Ingestion runtime

41. Source registry.
42. Adapter registry.
43. adapter protocol.
44. shared HTTP client.
45. structured adapter errors.
46. source runs.
47. cursors.
48. retries.
49. rate limiting.
50. concurrent ingestion with bounded workers.
51. health metrics.
52. adapter version logging.
53. cron/scheduler.
54. manual backfill command.
55. replay command.

At this point you have a data platform instead of a collection of scraper functions.

---

# P5 — Current-state projectors

56. `opportunity_current`.
57. `service_current`.
58. `actor_current`.
59. `market_current`.
60. `payment_current`.
61. `submission_current`.
62. `outcome_current`.

Project these from events.

Your mutable current tables are now disposable caches: delete them and rebuild from the event log.

That is an extremely useful invariant.

---

# P6 — Observation/diff engine

63. Generalized field diff.
64. uncertainty intervals.
65. status transition events.
66. reward changes.
67. competition changes.
68. worker assignment.
69. payout changes.
70. disappearance/reconciliation.
71. source-native lifecycle mappings.
72. observation-derived metrics.

Implement the good part of `repute/observations.py` here.

---

# P7 — Port adapters carefully

Do not start with 27.

Start with sources that exercise different types of markets.

### Wave A

73. GitHub — general work.
74. Superteam — structured bounties.
75. BountyBook — agent-oriented work.
76. x402 registry/service source — service economy.
77. Bittensor — incentive market.

### Wave B

78. Virtuals ACP.
79. Olas.
80. NEAR agent-market source.
81. AgentHansa.
82. TaskMarket/Daydreams.
83. OpenServ.
84. Apify.
85. Smithery.
86. OpenRouter.

### Wave C

Port remaining useful `repute` adapters only when they contribute **new economic information**.

Don't celebrate “50 adapters.”

Celebrate:

```text
20 sources
18 healthy
14 outcomes observable
9 payments observable
7 competition observable
```

Much better metric.

---

# P8 — Entity resolution + capability graph

87. alias table.
88. deterministic entity matching.
89. candidate matcher.
90. manual resolution overrides.
91. taxonomy normalization.
92. source-tag → capability mappings.
93. Opportunity → Capability edges.
94. Service → Capability edges.
95. Agent → evidenced Capability edges.
96. Process → Capability edges.

This is where your existing WorkerKit `CapabilityTracker` becomes very useful.

---

# P9 — Wire WorkerKit

97. `Opportunity → WorkOrder` translator.
98. persist prediction snapshot.
99. consume run events.
100. consume cost events.
101. consume ArtifactRef.
102. consume VerificationResult.
103. consume SubmissionReceipt.
104. consume OutcomeReceipt.
105. consume SettlementReceipt.
106. join run back to Oracle opportunity.
107. export capability evidence.
108. expose receipt through Oracle API.

**Milestone:**

```text
external opportunity
→ prediction
→ real execution
→ actual cost
→ verification
→ submission
→ result
→ payment
→ Oracle history
```

Your handover already identifies precisely this as the important economic experiment.

---

# P10 — Metrics engine v2

109. metric registry.
110. dimension/scope system.
111. hourly materializer.
112. daily materializer.
113. demand metrics.
114. supply metrics.
115. transaction metrics.
116. outcome metrics.
117. economics metrics.
118. efficiency metrics.
119. data-quality metrics.
120. historical rebuild.
121. metric unit tests.
122. fixture-based expected results.

---

# P11 — Prediction/evaluation loop

123. immutable predictions.
124. realized outcomes.
125. cost forecast error.
126. payout forecast error.
127. probability calibration.
128. per-market calibration.
129. per-capability calibration.
130. per-worker calibration.
131. model version comparisons.

Only after enough real outcomes should you get clever with models.

The dataset is the valuable part.

---

# P12 — API v1

132. split route modules.
133. service/query layer.
134. response schemas.
135. cursor pagination.
136. unified filters.
137. metrics endpoint.
138. series endpoint.
139. rankings.
140. global search.
141. evidence endpoint.
142. source-health endpoint.
143. exports.
144. compatibility wrappers for old `/work`, `/pulse`, etc.
145. OpenAPI documentation.
146. caching.

---

# P13 — Dashboard skeleton

147. persistent navigation.
148. global scope/filter bar.
149. URL-driven filter state.
150. global search.
151. generic MetricCard.
152. generic TimeseriesChart.
153. metric picker.
154. dense generic DataTable.
155. column picker.
156. timeframe selector.
157. CSV export.
158. loading/error/empty states.
159. confidence/freshness indicator.

Do not build twenty different bespoke card components.

Build the primitives once.

---

# P14 — DefiLlama-quality overview

160. headline open-work metric.
161. key metric strip.
162. configurable hero chart.
163. market rankings.
164. latest high-signal opportunities.
165. capability demand rankings.
166. verified-work activity.
167. data-health indicator.
168. responsive layout.
169. keyboard shortcuts.

At this stage the current “2-minute dashboard” should be deleted, not incrementally beautified.

---

# P15 — Detail surfaces

170. Market detail.
171. Opportunity detail.
172. Capability detail.
173. Agent detail.
174. Service detail.
175. Source detail.
176. WorkerKit run detail.
177. Receipt explorer.
178. Payment/settlement detail.
179. event/provenance timeline.

---

# P16 — Intelligence surfaces

180. market comparison.
181. capability comparison.
182. demand/supply gaps.
183. unfilled high-value demand.
184. fastest-growing capabilities.
185. low-competition work.
186. automation-ready opportunities.
187. realized-EV rankings.
188. prediction-vs-outcome report.
189. market efficiency report.

These are derived surfaces over the same data. Don't create separate pipelines for them.

---

# P17 — MCP

190. semantic tool names.
191. structured search.
192. market metrics.
193. opportunity ranking.
194. service selection.
195. capability intelligence.
196. receipt lookup.
197. source-health lookup.
198. MCP contract tests.
199. examples for Hermes/OpenClaw/etc.

This is where agents themselves begin consuming your wholesale intelligence layer.

---

# P18 — Data integrity / verification

200. Merkle batches.
201. explicit batch membership table.
202. real inclusion proof.
203. checkpoint manifests.
204. canonical hash code shared with protocol layer.
205. optional Ethereum anchoring.
206. Phala attestation references.
207. settlement verification.
208. confidence upgrades as evidence arrives.

Example:

```text
INFERRED
  ↓ source API confirms
SOURCE_VERIFIED
  ↓ payment observed
PAYMENT_VERIFIED
  ↓ TEE receipt matched
TEE_VERIFIED
```

Evidence can improve without rewriting historical facts.

---

# P19 — Reliability

209. adapter fixture tests.
210. adapter contract tests.
211. schema tests.
212. projector replay tests.
213. dedup tests.
214. data corruption tests.
215. source outage tests.
216. pagination tests.
217. stale-source tests.
218. currency conversion tests.
219. full rebuild test.
220. WorkerKit integration test.

Golden invariant:

> **Deleting every projection and rebuilding from immutable events produces exactly the same canonical state.**

---

# P20 — Operations

221. structured logging.
222. ingest metrics.
223. source alerts.
224. latency histograms.
225. queue depth.
226. DB size.
227. raw storage size.
228. API latency.
229. cache hit rate.
230. source-specific dashboards.
231. backup/restore.
232. deterministic DB rebuild.

---

# 46. What I would explicitly NOT build yet

This is important because it's very easy to bury the good idea underneath impressive-looking machinery.

Do **not** prioritize:

* elaborate social features
* marketplace messaging
* custom token
* bespoke identity system
* custom chain
* complicated governance
* giant recommendation ML
* arbitrary agent framework
* dozens of marketplace categories
* “AI reputation scores”
* ZK everything
* multiple databases just because they're fashionable
* Kafka
* Kubernetes
* GraphQL
* a vector DB for data that is fundamentally relational
* a Neo4j migration for your graph
* a complicated data lake

SQLite is actually okay for now.

You can get enormously far with:

```text
SQLite/Postgres
+ append-only events
+ content-addressed raw files
+ materialized metrics
+ FastAPI
+ React
```

The model matters vastly more than infrastructure prestige.

---

# 47. What to physically steal from `repute`

I would make a temporary migration checklist:

| `repute` concept           | Action                             |
| -------------------------- | ---------------------------------- |
| EventEnvelope              | **Reimplement immediately**        |
| Confidence/evidence levels | **Reimplement immediately**        |
| observation intervals      | **Port concept immediately**       |
| diff + observation logic   | **Rewrite cleanly**                |
| OpportunitySpec            | **Split into smaller MW models**   |
| adapter lifecycle          | **Formalize as protocol**          |
| source docs                | **Preserve under `/docs/sources`** |
| old adapters               | **Port source-by-source**          |
| raw hash handling          | **Preserve concept**               |
| Merkle batching            | **Rewrite correctly**              |
| source breadth             | **Use as backlog**                 |
| giant `api.py`             | **Do not port**                    |
| giant `server.py`          | **Do not port**                    |
| checked-in DB/cache        | **Delete**                         |
| scattered research runtime | **Separate**                       |
| old duplicate schemas      | **Do not port**                    |

That gives you the completeness of `repute` without bringing back the mess.

---

# 48. The single dashboard screen I would build first

If you want the coding agent to make the project suddenly look legitimate, don't tell it “redesign the dashboard.”

Tell it to build **exactly this screen**:

```text
┌───────────────┬─────────────────────────────────────────────────────────┐
│ MOLTWORK      │ Machine Work                         All Markets ▾      │
│               │ Updated 31s ago                     30D ▾              │
│ Overview      ├─────────────────────────────────────────────────────────┤
│ Work          │ OPEN MACHINE-PAYABLE WORK                             │
│ Markets       │ $184,392       +8.2% 24h                              │
│ Agents        ├─────────────────────────────────────────────────────────┤
│ Capabilities  │ New Work │ Paid 7d │ Median │ Auto │ Verified │ Markets│
│ Economics     │ $18.4K     $42.1K    $125     63%    78%        31     │
│ Outcomes      ├─────────────────────────────────────────────────────────┤
│               │ Open Work USD                        + Add Metric       │
│ Verification  │                                                         │
│ Runs          │                 TIMESERIES                              │
│ Receipts      │                                                         │
│               ├─────────────────────────────────────────────────────────┤
│ Data          │ MARKET RANKINGS                    1D  7D  30D          │
│ Sources       │ Search...                Demand Outcomes Economics     │
│ Methodology   │                                                         │
│               │ Market    Open$   New$   Paid$   Median   Comp  Fill   │
│ API / MCP     │ ─────────────────────────────────────────────────────── │
│               │ ...                                                     │
│               │                                                         │
└───────────────┴─────────────────────────────────────────────────────────┘
```

That alone changes the perceived product by an order of magnitude.

DefiLlama's homepage today follows almost exactly that hierarchy: market-level headline, compact key metrics, configurable time-series, then a dense ranking table with metric/time controls rather than a pile of disconnected cards. ([DefiLlama][2])

---

# 49. The deeper thesis

This is the part I think your current architecture has finally made possible.

DefiLlama answers:

> **Where is capital, and what is it doing?**

Moltwork can answer:

> **Where is machine-payable work, who can perform it, what does it cost to perform, what actually gets accepted, and where does autonomous labor earn money?**

That means the Oracle should eventually know:

```text
WHERE demand exists
WHAT capabilities it requires
WHO can satisfy it
HOW competitive it is
HOW expensive it is to execute
HOW often submissions win
HOW often winners get paid
HOW long settlement takes
WHICH processes work
WHICH models/tools were economical
WHICH claims are independently verified
```

WorkerKit is what lets you collect the latter half without guessing.

That is much stronger than just building a marketplace.

---

# 50. The immediate order I would execute

Forget the last 200 items for a second. The **next sequence** should be:

1. **Merge the four `mw` component branches into one coherent tree.**
2. **Implement `OracleEvent` + confidence + raw evidence.**
3. **Implement proper diff/observation intervals.**
4. **Build source registry + source-run health.**
5. **Migrate five excellent adapters onto the new adapter protocol.**
6. **Create current-state projectors from the immutable event stream.**
7. **Wire WorkerKit receipts/outcomes/costs back into Oracle.**
8. **Implement real Demand / Outcomes / Economics / Efficiency metrics.**
9. **Implement `/v1/overview`, `/v1/series`, rankings and search.**
10. **Replace the current dashboard with the single DefiLlama-style Overview screen above.**
11. **Build Market → Opportunity → Capability → Agent drilldowns.**
12. **Then expand source coverage.**
13. **Then MCP.**
14. **Then Merkle/TEE/on-chain evidence visualizations.**
15. **Then prediction calibration and smarter economic routing.**

That order keeps the thing extremely grounded.

The resulting system isn't “a more comprehensive Oracle.” It becomes the **historical economic data plane of Moltwork**, while WorkerKit is the verified execution/evidence plane. That division is considerably cleaner than `repute`, and much more defensible than simply resurrecting its 70 KB API and pile of adapters.

[1]: https://defillama.com/mcp "https://defillama.com/mcp"
[2]: https://defillama.com/ "https://defillama.com/"
[3]: https://defillama.com/metrics "https://defillama.com/metrics"
