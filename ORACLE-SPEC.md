The closest formula is:

> **Moltwork Oracle = Lightcast’s labor-market semantics + DefiLlama’s open aggregation/distribution + Token Terminal’s metric discipline + CoinGlass’s live-market UX + a Dune-like query layer later.**

And yes: **Lightcast is probably the name you were trying to remember.** It has almost exactly the analytical primitives we need for jobs: raw postings normalized into skills/titles/occupations, then totals, time series, rankings, distributions, salary/demand analysis and projections. ([Lightcast][1])

# Moltwork Oracle v1

## Full Product, Data, API and Dashboard Specification

### 1. Product definition

**Moltwork Oracle is the canonical data layer for the machine-work economy.**

It answers:

> Where is work being offered, what does it pay, what capabilities does it require, how competitive is it, how quickly does it disappear, and what is changing across the market?

Initially it should be descriptive rather than predictive.

```text
SOURCE MARKETS
    │
    ├─ agent markets
    ├─ bounty platforms
    ├─ freelance markets
    ├─ protocol grants
    ├─ GitHub/open-source work
    ├─ x402 services/work
    └─ other machine-executable demand
          │
          ▼
     RAW OBSERVATIONS
          │
          ▼
       NORMALIZE
          │
      ┌───┴────┐
      │        │
    DEDUPE   CLASSIFY
      │        │
      └───┬────┘
          ▼
 CANONICAL WORK GRAPH
          │
     ┌────┼─────────┐
     ▼    ▼         ▼
 Dashboard API     Agents
```

The important word is **canonical**.

The long-term asset is not the dashboard.

It is the historical dataset underneath it.

---

# 2. What to copy from existing products

## DefiLlama: distribution + transparency

DefiLlama exposes a large free unauthenticated API alongside a paid higher-capacity API. Its free surface is organized around canonical entities plus overview, summary and historical endpoints across different metric verticals. Its UI then builds ranked tables, comparison pages, protocol pages and downloadable charts on top. 

Even more important: DefiLlama makes methodology and adapters inspectable and lets contributors add adapters through open-source repositories. ([GitHub][2])

**Copy:**

```text
free useful API
transparent methodology
source/adapter visibility
canonical identifiers
overview → entity → history hierarchy
sortable metric tables
comparison pages
CSV exports
```

Do not copy the sprawling navigation yet.

---

## Token Terminal: normalization + methodology

Token Terminal's strongest idea is not its dashboard.

It is:

> raw data → standardized metrics → documented methodologies.

Token Terminal explicitly uses an ELT/raw-first approach so it can reprocess history when schemas, protocols or metric definitions change. It also exposes a metric catalog, projects, project-level historical metrics, metric-across-project endpoints, aggregations and curated datasets. ([Token Terminal][3])

Its newer methodology system documents the source data and transformation path for a calculated metric. ([Token Terminal][4])

**This is exactly how Moltwork should treat work data.**

Never throw away the source observation after normalization.

---

## Lightcast: closest conceptual analogue

Lightcast is remarkably close to the Oracle problem.

Its job-postings products offer:

```text
totals
timeseries
rankings
distributions
individual postings
companies
skills
titles
occupations
salary information
skill growth
classification
```

Its postings API can filter and rank across company, occupation, skill, geography and other dimensions. Its skills/title/occupation taxonomies then give different source datasets a common language. ([Lightcast][1])

Lightcast's broader model also explicitly treats:

```text
postings = labor demand
profiles = labor supply
```

and combines them to study supply/demand gaps. ([Lightcast][5])

That eventually maps beautifully onto:

```text
Moltwork Oracle opportunities = demand

WorkerKit workers +
Marketplace capabilities       = supply
```

Do not build that join yet.

Design identifiers so it becomes possible.

---

## CoinGlass: live-market UX

CoinGlass's useful lesson is how it presents lots of noisy sources as **a market** rather than a database.

Its API exposes standardized current/historical data, rankings and many time-series views, while its UI heavily uses ranked tables, time-window selectors and heatmap-style displays. It also supports a live WebSocket interface. ([CoinGlass-API][6])

For Moltwork, the equivalent should be:

```text
market heatmaps
new-work feed
reward flows
opportunity velocity
competition
market activity
24h / 7d / 30d changes
```

---

## Dune: later analytical layer

Dune separates:

```text
query
execution
result
```

and allows saved queries, arbitrary SQL, filtering, pagination and downloadable results. Its API also supports data uploads, pipelines and materialized views. ([Dune Docs][7])

This is worth copying **later**.

Do not build a SQL playground before anyone cares about the dataset.

---

# 3. Architectural rule

Use:

```text
PostgreSQL
+
R2/S3 raw object storage
```

Nothing more initially.

No Kafka.

No ClickHouse.

No Neo4j.

No Elasticsearch cluster.

No dedicated time-series database.

Postgres is easily sufficient for the early Oracle.

Architecture:

```text
Crawler / Adapter
       │
       ▼
RAW BLOB ───────────────→ R2
       │
       ▼
raw_observation
       │
       ▼
Normalizer
       │
       ▼
Entity resolution
       │
       ▼
canonical opportunity
       │
       ▼
change detector
       │
       ├─ opportunity events
       └─ current projection
                │
                ▼
          metric rollups
                │
        ┌───────┴────────┐
        ▼                ▼
       API            Dashboard
```

---

# 4. Database schemas

Keep the Oracle under its own Postgres schema:

```text
oracle.*
```

WorkerKit and Marketplace should eventually remain:

```text
worker.*
market.*
```

Do not merge these conceptually.

## Core Oracle tables

```text
oracle.sources
oracle.ingest_runs
oracle.raw_observations

oracle.markets

oracle.opportunities
oracle.opportunity_sources
oracle.opportunity_observations
oracle.opportunity_events

oracle.skills
oracle.opportunity_skills

oracle.categories
oracle.opportunity_categories

oracle.metric_definitions
oracle.metric_points

oracle.daily_market_metrics
oracle.daily_skill_metrics
oracle.daily_category_metrics
```

---

# 5. `sources`

Represents where data came from.

```text
sources

id
slug
name

source_type
website_url

adapter_name
adapter_version

crawl_interval_seconds

enabled

last_success_at
last_attempt_at

freshness_status
error_rate_24h

created_at
updated_at

metadata JSONB
```

Example:

```text
superteam
virtuals-acp
algora
moltjobs
github
...
```

---

# 6. `ingest_runs`

Every crawler invocation.

```text
ingest_runs

id
source_id

started_at
finished_at

status

records_seen
records_created
records_changed
records_unchanged
records_failed

adapter_version

error_summary

metadata JSONB
```

This gives you a serious **source health dashboard** immediately.

---

# 7. Raw observations

This is one of the most important tables.

```text
raw_observations

id
source_id
ingest_run_id

external_id

observed_at

content_hash

raw_blob_uri

http_status
source_url

parser_version

metadata JSONB
```

Raw content itself should generally live in R2:

```text
/raw/{source}/{yyyy}/{mm}/{dd}/{hash}.json
```

Don't keep rewriting source records.

Keep history.

Token Terminal's raw-first approach is the right model because changing normalization rules should not require recollecting historical data. ([Token Terminal][3])

---

# 8. Canonical opportunity

```text
opportunities

id UUIDv7

canonical_title
canonical_description

market_id

status

category_id

execution_mode

reward_amount
reward_currency
reward_usd

reward_min_usd
reward_max_usd

deadline_at

source_created_at

first_seen_at
last_seen_at
closed_at

remote

human_allowed
agent_allowed

application_required

canonical_url

confidence

metadata JSONB

created_at
updated_at
```

Possible statuses:

```text
open
closed
filled
expired
cancelled
paid
unknown
```

Keep these deliberately small.

---

# 9. Multiple source records

One canonical opportunity may appear several times.

```text
opportunity_sources

opportunity_id
source_id
external_id

source_url

first_seen_at
last_seen_at

match_confidence

is_primary
```

Example:

```text
same GitHub bounty

→ direct GitHub
→ Algora
→ aggregator
```

should eventually become:

```text
ONE opportunity

THREE observations/sources
```

This is where your deduplication becomes valuable.

---

# 10. Opportunity observations

Each meaningful observation of an opportunity.

```text
opportunity_observations

id
opportunity_id

source_id

observed_at

status

reward_amount
reward_currency
reward_usd

deadline_at

applicant_count
submission_count

raw_observation_id

normalized_hash

metadata JSONB
```

This lets you answer later:

```text
10:00 reward $50
11:00 reward $50
12:00 2 submissions
13:00 5 submissions
15:00 closed
```

without storing five entire canonical objects.

---

# 11. Opportunity events

Generated when observations change.

```text
opportunity_events

id
opportunity_id

event_type

occurred_at
observed_at

old_value JSONB
new_value JSONB

source_id

confidence
```

Useful events:

```text
discovered
reward_changed
deadline_changed
status_changed
competition_changed
submission_added
closed
reopened
filled
payment_observed
expired
```

This event stream will become an extremely valuable dataset.

---

# 12. Skills taxonomy

Do not use random strings forever.

Lightcast's major advantage comes partly from forcing messy titles/skills into stable machine-readable taxonomies. Its current offering has tens of thousands of standardized skills and titles. ([Lightcast][8])

Moltwork doesn't need 35,000 skills.

Start with perhaps a few hundred.

```text
skills

id
slug
name
description

parent_id

aliases[]

taxonomy_version

created_at
deprecated_at
```

Examples:

```text
python
typescript
solidity
web-research
competitive-research
technical-writing
repo-analysis
image-generation
data-extraction
smart-contract-audit
```

Use aliases:

```text
"JS"
"Javascript"
"JavaScript programming"
        ↓
javascript
```

---

# 13. Categories

Higher-level than skills.

```text
software-development
research
data
design
content
security
blockchain
sales
marketing
operations
finance
```

Avoid hundreds of categories.

Skills provide granularity.

---

# 14. Metrics must themselves be data

Copy Token Terminal here.

```text
metric_definitions

metric_id

name
description

unit

grain

aggregation_method

methodology_version

source_requirements

missing_data_policy

experimental

created_at
updated_at
```

Example:

```text
active_opportunities
new_opportunities
advertised_reward_usd
median_reward_usd
```

Every chart should point to a metric definition.

---

# 15. Oracle v1 metric catalogue

## Market size

```text
active_opportunities
new_opportunities_24h
closed_opportunities_24h

advertised_open_reward_usd
new_advertised_reward_usd

markets_active
sources_active
```

Use **advertised** reward.

Don't imply money has actually been paid.

---

## Reward metrics

```text
median_reward_usd

p25_reward_usd
p75_reward_usd
p90_reward_usd

average_reward_usd

reward_distribution
```

Break these down by:

```text
market
category
skill
execution_mode
```

---

## Velocity metrics

```text
opportunity_creation_rate

opportunity_closure_rate

net_opportunity_change

median_open_duration

median_time_to_close

deadline_pressure
```

Example:

```text
new today       482
closed today    401
net              +81
```

This gives the market a pulse.

---

## Competition metrics

Only expose when actually observed.

```text
median_applicants
median_submissions

applications_per_opportunity

competition_change_24h
```

Never invent applicant counts for sources that don't expose them.

---

## Demand metrics

```text
demand_by_skill
demand_by_category

advertised_reward_by_skill

skill_share

skill_growth_7d
skill_growth_30d

category_growth_7d
category_growth_30d
```

This eventually becomes extremely interesting:

```text
Fastest-growing agent work skills

repo-analysis        +82%
research             +41%
Solidity             +30%
data-extraction      +27%
```

---

## Market-quality metrics

```text
source_freshness

source_coverage

reward_coverage

deadline_coverage

competition_data_coverage

payment_data_coverage
```

Then later:

```text
verified_payment_rate
median_payment_delay
dispute_rate
```

but **only once actual settlement evidence exists**.

---

# 16. Distinguish observed from inferred metrics

Every metric should have:

```text
measurement_type:
    observed
    derived
    estimated
```

Example:

```text
reward_usd
observed/derived from advertised reward + FX

verified_payout_usd
observed from payment evidence

expected_value
estimated
```

I would not publish `expected_value` in Oracle v1.

That comes after WorkerKit.

---

# 17. Public REST API

Base:

```text
https://api.moltwork.com/v1
```

Keep V1 primarily read-only.

---

## Discovery / metadata

```text
GET /health

GET /meta

GET /coverage

GET /sources

GET /sources/{source_id}

GET /sources/{source_id}/health

GET /metrics

GET /metrics/{metric_id}

GET /skills

GET /skills/{skill_id}

GET /categories

GET /markets
```

These should be free.

Token Terminal explicitly recommends maintaining a cached catalog of available projects and metrics; Moltwork should similarly make its entity/metric catalogs easy to enumerate. ([Token Terminal][9])

---

# 18. Opportunity API

```text
GET /opportunities

GET /opportunities/{id}

GET /opportunities/{id}/history

GET /opportunities/{id}/events

GET /opportunities/{id}/sources
```

Main query endpoint:

```text
GET /opportunities
```

Filters:

```text
?status=open

&market=algora

&category=software-development

&skills=python,github

&skills_mode=all

&min_reward_usd=5

&max_reward_usd=100

&deadline_before=...

&deadline_after=...

&first_seen_after=...

&changed_since=...

&execution_mode=agent

&q=research

&sort=reward_usd

&order=desc

&limit=100

&cursor=...
```

Cursor pagination, not offset pagination.

---

# 19. Example response

```json
{
  "data": [
    {
      "id": "019...",
      "title": "Implement API integration",
      "market": {
        "id": "algora",
        "name": "Algora"
      },
      "status": "open",
      "reward": {
        "amount": 50,
        "currency": "USD",
        "usd": 50
      },
      "skills": [
        "python",
        "api-integration"
      ],
      "first_seen_at": "...",
      "last_seen_at": "...",
      "deadline_at": "...",
      "source_url": "...",
      "confidence": 0.98
    }
  ],
  "meta": {
    "as_of": "...",
    "count": 100,
    "next_cursor": "...",
    "coverage": {
      "sources": 17
    }
  }
}
```

Every API response should include an `as_of`.

Data products become confusing quickly without one.

---

# 20. Analytical API

This is where I would copy Lightcast heavily.

Instead of building hundreds of endpoints, expose generic analytical primitives.

## Totals

```text
POST /analytics/totals
```

Example:

```json
{
  "filter": {
    "status": ["open"],
    "skills": ["python"],
    "when": {
      "start": "2026-08-01",
      "end": "2026-08-29"
    }
  },
  "metrics": [
    "active_opportunities",
    "advertised_reward_usd",
    "median_reward_usd"
  ]
}
```

---

## Time series

```text
POST /analytics/timeseries
```

```json
{
  "filter": {
    "market": ["algora", "superteam"]
  },
  "metrics": [
    "new_opportunities",
    "advertised_reward_usd"
  ],
  "interval": "day"
}
```

Return:

```text
timestamp
metric
value
```

---

## Rankings

```text
POST /analytics/rankings/{facet}
```

Facets:

```text
market
skill
category
source
execution_mode
```

Example:

```text
POST /analytics/rankings/skill
```

Rank by:

```text
active_opportunities
new_opportunities
advertised_reward_usd
median_reward_usd
growth_7d
```

This copies the extremely useful Lightcast ranking primitive. ([Lightcast][10])

---

# 21. Distributions

```text
POST /analytics/distributions/{facet}
```

Examples:

```text
/distributions/reward_usd
/distributions/open_duration
/distributions/submission_count
```

Return configurable buckets or percentiles.

This is much more useful than returning averages everywhere.

---

# 22. Metric-first API

Also provide a simpler Token-Terminal-style interface:

```text
GET /metrics/{metric_id}/series
```

Example:

```text
GET /metrics/active_opportunities/series
    ?market=algora,superteam
    &start=2026-08-01
    &end=2026-08-29
    &interval=day
```

That becomes convenient for dashboards and developers.

---

# 23. Market endpoints

```text
GET /markets

GET /markets/{id}

GET /markets/{id}/opportunities

GET /markets/{id}/metrics

GET /markets/{id}/history
```

Market response should eventually include:

```text
open opportunities
open reward
new 24h
closed 24h
median reward
median open duration

skills
categories

source health
coverage

history
```

Think DefiLlama protocol page, except the entity is a work market.

---

# 24. Skill endpoints

```text
GET /skills

GET /skills/{skill}

GET /skills/{skill}/opportunities

GET /skills/{skill}/metrics

GET /skills/{skill}/history

GET /skills/{skill}/related
```

Eventually:

```text
GET /skills/{skill}/markets
```

This becomes:

> Python demand across machine-work markets.

---

# 25. Change feed

This is extremely important for agents.

```text
GET /events
```

Example:

```text
/events
?since=2026-08-29T10:00:00Z
&types=discovered,reward_changed,closed
```

Agents should not have to continuously re-download every opportunity.

---

# 26. Live stream

CoinGlass uses live subscription infrastructure for changing market data. Moltwork should eventually provide the machine-work equivalent. ([CoinGlass-API][11])

V1 can simply use SSE:

```text
GET /stream/opportunities
```

Events:

```text
opportunity.created

opportunity.updated

opportunity.closed

reward.changed
```

SSE is easier than WebSockets.

Add WebSockets only if required.

---

# 27. Bulk export

Absolutely have:

```text
GET /exports/opportunities.csv

GET /exports/metrics.csv
```

or simply:

```text
?format=csv
```

Later:

```text
Parquet
```

Token Terminal and Dune both treat downloadable/queryable data as part of the product rather than locking it inside charts. ([Token Terminal][12])

---

# 28. API response metadata

Every analytical response should ideally contain:

```text
generated_at

as_of

methodology_version

data_start

data_end

sources_used

coverage

warnings
```

Example:

```json
{
  "meta": {
    "as_of": "2026-08-29T05:01:00Z",
    "methodology_version": "reward-volume-v1",
    "coverage": 0.74,
    "warnings": [
      "Applicant counts unavailable for 3 markets"
    ]
  }
}
```

This is very important.

A market-data company is fundamentally selling **trust**.

---

# 29. Dashboard information architecture

Keep the site very small initially.

```text
Overview

Opportunities

Markets

Skills

Categories

Trends

Compare

Sources

Methodology

API
```

That's enough.

---

# 30. Overview dashboard

This is your DefiLlama home page.

Header:

```text
MOLTWORK ORACLE

The machine-work economy
```

Top cards:

```text
OPEN OPPORTUNITIES

4,829


ADVERTISED REWARD

$286,410


NEW 24H

712


CLOSING 24H

181


ACTIVE MARKETS

24


MEDIAN REWARD

$31.20
```

Again: label it **advertised reward**, not “money available.”

---

# 31. Main overview chart

Default:

```text
ACTIVE OPPORTUNITIES
```

Time selectors:

```text
24H
7D
30D
90D
1Y
ALL
```

Metric selector:

```text
Active opportunities

New opportunities

Advertised reward

Median reward

Opportunity velocity
```

Exactly the kind of simple metric-switching interaction that crypto terminals use effectively.

---

# 32. Main ranked market table

This should be the centerpiece.

```text
Market

Open

Open Reward

New 24h

Closed 24h

Median Reward

7D Δ

Median Lifetime

Freshness
```

Sortable by every numeric field.

This is the machine-work equivalent of a DefiLlama chains/protocol table.

---

# 33. Activity heatmap

Borrow the useful visual concept from market terminals without copying their domain.

Rows:

```text
markets
```

Columns:

```text
categories
```

Cell:

```text
new opportunities
or
advertised reward
```

Example:

```text
             DEV   RESEARCH   DATA   DESIGN

Algora        ███      ██       █      ░

Superteam      ██      ███      ██     ██

Market X        █       █       ███     ░
```

Click a cell:

```text
market=Algora
category=Research
```

and open filtered opportunities.

---

# 34. New-work tape

Have a live side panel:

```text
JUST IN

12 sec
$45
Python API integration
Algora

34 sec
$120
Protocol research report
...

1 min
$18
Dataset cleanup
...
```

This makes Oracle feel alive.

---

# 35. Opportunities page

This should be fast and dense.

Columns:

```text
Opportunity

Market

Reward

Skills

Age

Deadline

Competition

Status
```

Filters down the left/top:

```text
market

category

skill

reward

deadline

age

execution mode

status
```

No huge cards.

Data tool, not social network.

---

# 36. Opportunity detail

Every opportunity gets a permanent Moltwork URL:

```text
moltwork.com/oracle/opportunity/{id}
```

Show:

```text
title

reward

market

description

required skills

deadline

source

current status
```

Then:

```text
HISTORY

10:03 discovered

10:52 reward changed
$35 → $50

12:13 2 submissions observed

15:41 closed
```

And:

```text
SOURCE EVIDENCE

original URL
first observed
last observed
source
raw observation hash
```

This transparency becomes valuable.

---

# 37. Market page

Example:

```text
ALGORA
```

Key metrics:

```text
Open jobs
Open reward
New 24h
Median reward
Median lifetime
```

Charts:

```text
open opportunities over time

new vs closed opportunities

advertised reward over time

reward distribution
```

Rankings:

```text
top skills

top categories
```

Then current opportunities.

Also include:

```text
coverage

source freshness

methodology
```

---

# 38. Skills page

This may become one of the most valuable parts of the entire product.

Main ranking:

```text
Skill

Open Work

Reward

Median Reward

7D Demand

30D Demand
```

Skill detail:

```text
PYTHON

Open opportunities       781

Advertised reward    $42,119

Median reward            $48

30d demand              +19%
```

Charts:

```text
demand over time

reward over time

market share

category distribution
```

Later WorkerKit adds:

```text
worker supply
success rates
actual cost
```

But not yet.

---

# 39. Trends page

Very useful relatively early.

Sections:

```text
FASTEST-GROWING SKILLS

FASTEST-GROWING CATEGORIES

FASTEST-GROWING MARKETS

BIGGEST REWARD INCREASES

NEW MARKETS

UNUSUAL ACTIVITY
```

No AI required initially.

Simple statistical changes are enough.

---

# 40. Compare

Copy DefiLlama/Token Terminal.

User selects:

```text
Algora
Superteam
Virtuals
...
```

or:

```text
Python
Solidity
Research
```

Then overlays:

```text
opportunities

reward

median reward

growth
```

DefiLlama explicitly exposes chain comparison pages while Token Terminal's product centers heavily on comparable standardized metrics. ([DefiLlama][13])

---

# 41. Sources page

This should be public.

```text
Source

Last Update

Status

Opportunities

Freshness

Coverage
```

Example:

```text
Algora       2m ago   Healthy     381

Superteam    4m ago   Healthy     192

Market X    31m ago   Delayed      48
```

This is operational transparency and builds trust.

---

# 42. Methodology pages

Every important metric gets a real methodology page.

Example:

```text
Advertised Open Reward

Definition
──────────
USD value of advertised compensation
associated with currently open canonical
opportunities.

Included
────────
Fixed-price rewards

Excluded
────────
Unknown compensation
equity-only compensation

Calculation
───────────
...

Currency conversion
───────────────────
...

Missing data
────────────
...

Methodology version
───────────────────
1.2

Last updated
────────────
...
```

Token Terminal is especially good inspiration here: metric definitions plus project/metric-specific source information are first-class data. ([Token Terminal][14])

---

# 43. Allow incorrect-data reports

Every page should eventually have:

```text
Report incorrect data
```

because your normalization will be wrong sometimes.

DefiLlama visibly exposes methodology/source code and incorrect-data reporting on protocol pages. ([DefiLlama][15])

---

# 44. Adapter system

This could become a serious distribution advantage.

Internal interface:

```text
interface SourceAdapter {
    discover(): RawOpportunity[]

    normalize(raw): NormalizedOpportunity

    health(): SourceHealth
}
```

Every source adapter declares:

```text
source id

version

polling interval

supported fields

field reliability

terms / provenance information
```

Eventually publish an adapter SDK:

```text
@moltwork/oracle-adapter
```

and allow marketplaces to submit integrations themselves.

This is very DefiLlama-like and potentially powerful.

---

# 45. Agent-native API matters more than human API

Humans want:

```text
tables
charts
compare
```

Agents want:

```text
give me everything changed since timestamp X

give me open Python jobs >$10

give me newly posted work

give me source confidence

give me canonical IDs

don't make me scrape HTML
```

So prioritize:

```text
changed_since

stable identifiers

cursor pagination

SSE

machine-readable taxonomies

deterministic JSON
```

over flashy frontend work.

---

# 46. MCP surface

Once REST works, MCP is trivial.

Expose maybe:

```text
find_opportunities

get_opportunity

market_overview

market_rankings

skill_demand

changes_since
```

Example:

```text
find_opportunities(
    skills=["python"],
    min_reward_usd=10,
    status="open"
)
```

The MCP should remain a very thin wrapper over REST.

Don't implement separate business logic.

---

# 47. Search

V1:

Postgres full-text search.

```text
q="python research"
```

Later:

```text
semantic search
```

via embeddings.

Do not make semantic search part of the fundamental canonical model.

---

# 48. Dedupe

This deserves proper engineering early.

Candidate generation:

```text
same source external_id

same URL

normalized title similarity

description similarity

same reward

same deadline

same organization
```

Then calculate:

```text
duplicate_confidence
```

Never permanently merge low-confidence candidates.

Maintain:

```text
canonical opportunity

↕ aliases/source records
```

so merges can later be undone.

---

# 49. Time semantics

Always distinguish:

```text
source_created_at

first_seen_at

observed_at

last_seen_at

closed_at

deadline_at
```

Those are not interchangeable.

The entire future time-to-fill / opportunity-lifetime dataset depends on getting this right now.

---

# 50. Data quality flags

Every canonical record can expose:

```text
quality: {
    identity_confidence,
    reward_confidence,
    status_confidence,
    deadline_confidence,
    duplicate_confidence
}
```

You don't need to show all of them prominently in the UI.

But store them.

---

# 51. Don't hide missing data

Return:

```text
null
```

rather than:

```text
0
```

when something isn't observed.

Huge difference:

```text
submission_count = 0
```

means:

> we know nobody submitted.

Whereas:

```text
submission_count = null
```

means:

> source doesn't tell us.

This distinction will matter enormously for later models.

---

# 52. Data coverage should become a metric itself

Example:

```text
Reward coverage        83%

Deadline coverage      61%

Competition coverage   19%

Settlement coverage     4%
```

That immediately tells users how much confidence to place in analytics.

---

# 53. Market snapshots

Generate immutable periodic snapshots:

```text
hourly_market_snapshot

daily_market_snapshot
```

Example:

```text
date

market_id

active_opportunities

new_opportunities

closed_opportunities

advertised_reward_usd

median_reward_usd
```

This makes dashboard queries extremely cheap.

---

# 54. Materialized views

Postgres materialized views are enough initially:

```text
mv_market_current

mv_market_daily

mv_skill_daily

mv_category_daily

mv_global_daily
```

Refresh incrementally/on schedule.

Do not calculate 30-day skill trends over millions of raw observations on every page request.

---

# 55. Caching

Public popular calls:

```text
/markets

/skills

/analytics/totals

/metrics/.../series
```

can sit behind CDN caching.

Opportunity feeds need much shorter TTL.

No complicated cache system needed initially.

---

# 56. API philosophy

I would copy DefiLlama's distribution strategy more than Token Terminal's gated strategy initially.

DefiLlama currently has a useful no-auth free API and a paid higher-capacity/expanded API, whereas Token Terminal's API is subscription-based. 

For Moltwork:

```text
FREE

current opportunities
markets
skills
basic history
basic metrics
reasonable API limits


LATER PAID

higher limits
longer/full history
bulk dumps
live feeds
webhooks
advanced analytics
possibly WorkerKit-derived intelligence
```

You need distribution more than API revenue initially.

---

# 57. Dataset versioning

Have:

```text
dataset_version

taxonomy_version

adapter_version

methodology_version
```

They solve different problems.

Never overload one global version string.

---

# 58. Changelog

Public:

```text
/api/changelog

/methodology/changelog

/taxonomy/changelog
```

If:

```text
Research → Market Research
```

changes classification rules, users should be able to know.

---

# 59. Machine-readable schema

Publish:

```text
/openapi.json
```

DefiLlama explicitly publishes OpenAPI specifications for its API. 

Also publish:

```text
/schema/opportunity.json
/schema/metric.json
```

Make integration extremely easy.

---

# 60. SDKs

Not immediately.

REST + OpenAPI first.

Generate SDKs later:

```text
Python

TypeScript
```

Don't hand-maintain five language SDKs.

---

# 61. Alerts

Useful shortly after V1.

Humans:

```text
"Tell me when a Python bounty >$50 appears."
```

Agents:

```text
webhook filters
```

API:

```text
POST /alerts

POST /webhooks
```

But this is after the feed works.

---

# 62. Watchlists

Again, simple:

```text
watch market

watch skill

watch category
```

The equivalent of watchlists on financial-data tools.

Low engineering cost.

Useful retention.

---

# 63. Saved screens

Eventually let users save:

```text
Python
reward > $20
agent executable
deadline > 2 days
```

as:

```text
"My Python jobs"
```

Again: build only once filtering itself is solid.

---

# 64. User-created dashboards

Do **not** build initially.

Token Terminal Studio and Dune dashboards show this can become valuable when a dataset gets sufficiently rich. Token Terminal lets users create custom charts/dashboards and fork existing charts. ([Token Terminal][16])

But that's later.

For now:

```text
API + CSV
```

is enough customization.

---

# 65. SQL/data explorer

Also later.

Eventually:

```text
SELECT
  skill,
  AVG(reward_usd)
FROM opportunities
...
```

could be excellent.

But Dune's query/execution/result infrastructure is an entire product by itself. ([Dune Docs][7])

Do not clone Dune now.

---

# 66. Interesting Oracle datasets that emerge

Once enough history exists, build curated datasets analogous to Token Terminal's screeners/cohort datasets. Token Terminal exposes datasets such as screeners and cohort analyses in addition to raw metric endpoints. ([Token Terminal][17])

Moltwork examples:

```text
fastest-growing-skills

highest-paying-markets

new-markets

market-reliability

opportunity-lifetime

reward-distributions

competition-index

agent-executable-opportunities

market-activity-screener
```

These should mostly be **saved analytical queries**, not entirely new infrastructure.

---

# 67. Market screener

Eventually this could be excellent:

```text
MARKET SCREENER

                         Open   Reward   7d Δ   Lifetime

Algora                    381   $32k     +18%     3.2d

Superteam                 211   $91k      +4%     5.6d

Virtuals                   ...   ...      ...      ...
```

Filter:

```text
minimum market activity

minimum reward coverage

category

agent executable

growth
```

Very DefiLlama/Token-Terminal-like.

---

# 68. Skill screener

Potentially even better:

```text
SKILL SCREENER

Skill       Jobs   Reward   Med. Pay   30d Demand

Python       731    $61k       $55        +21%

Research     489    $38k       $34        +18%

Solidity     171    $41k      $120         +9%
```

Later:

```text
worker supply
completion rate
estimated production cost
```

This is when Oracle + WorkerKit becomes extremely interesting.

---

# 69. Demand versus supply is the eventual killer page

Not V1.

But architect for:

```text
                 DEMAND         SUPPLY

Python             █████████      █████

Research           ████████       ██

Design             ███            ███████

Solidity           █████          █
```

Where:

```text
Demand
=
Oracle

Supply
=
WorkerKit + Marketplace
```

Then Moltwork can identify:

```text
capability shortages
oversupplied skills
valuable agent upgrades
```

Lightcast already does analogous supply/demand analysis for human labor. ([Revelio Labs][18])

This will be one of Moltwork's most valuable long-term views.

---

# 70. Then WorkerKit adds outcome intelligence

Eventually the schema connects:

```text
oracle.opportunity_id
        │
        ▼
worker.run
        │
        ▼
worker.outcome
```

Now Oracle gains metrics impossible from scraping:

```text
attempt rate

completion rate

acceptance rate

verified payout

actual agent cost

profitability

worker success by skill
```

But keep those stored under WorkerKit.

Oracle consumes aggregated versions.

---

# 71. Marketplace completes the graph

Eventually:

```text
opportunity
      │
      ▼
   work run
      │
      ├── used skill X
      ├── bought verifier Y
      └── used process Z
      │
      ▼
    outcome
```

Then Moltwork knows:

```text
what work exists

what agents try

what they buy

what process they use

what succeeds

what gets paid
```

That is the actual moat.

---

# 72. What to ship now

The first production milestone should be brutally constrained:

```text
RAW INGESTION

canonical opportunities

history/events

skills/categories

dedupe

Postgres rollups

public REST API

simple overview dashboard

opportunity table

market pages

skill pages

source health page

methodology page
```

That's enough for a real product.

---

# 73. What not to ship yet

Do not spend time on:

```text
SQL explorer

AI market commentary

complex forecasts

custom dashboards

social features

marketplace

portfolio management

fancy embeddings

graph database

complex alert builder

paid API billing system

50 dashboard pages
```

Collecting clean history is worth considerably more than those features right now.

---

# 74. Exact MVP dashboard

If I were freezing the frontend today, it would contain exactly:

```text
/

overview cards
active opportunities chart
markets ranking
skill ranking
activity heatmap
recent opportunities


/opportunities

filterable table


/markets

market ranking


/market/{id}

market metrics
history
skills
opportunities


/skills

skill ranking


/skill/{id}

skill history
markets
opportunities


/sources

collector health


/methodology

definitions


/api

docs
```

That is enough.

---

# 75. The most important data-engineering invariant

Never do:

```text
source
   ↓
normalized row
   ↓
throw source away
```

Do:

```text
immutable raw observation
        ↓
versioned parser
        ↓
canonical interpretation
        ↓
metric methodology
```

so that six months from now you can say:

> our old definition of “open opportunity” was wrong.

and recompute the entire historical dataset.

That principle is directly supported by how mature data products such as Token Terminal structure their pipelines. ([Token Terminal][3])

---

# 76. The second invariant

**The dashboard should never know special business logic.**

Bad:

```text
dashboard computes active Algora rewards
```

Good:

```text
dashboard
    ↓
/metrics/advertised_open_reward_usd
```

One metric implementation powers:

```text
API

dashboard

MCP

CSV

future SDK

future reports
```

---

# 77. The third invariant

**An opportunity is an entity. An observation is evidence about that entity.**

Keep those separate.

That single distinction is what allows:

```text
history

dedupe

corrections

provenance

confidence

longitudinal analysis
```

to work properly.

---

# 78. The product hierarchy

The clean mental model is:

```text
              MOLTWORK ORACLE

RAW LAYER
What did the source actually say?

         ↓

CANONICAL LAYER
What real-world opportunity does this represent?

         ↓

METRIC LAYER
What can we measure from these opportunities?

         ↓

ANALYTICS LAYER
What is happening across the market?

         ↓

DECISION LAYER — LATER
What should this particular worker do?
```

You are currently building the first four.

**Do not jump to the fifth yet.**

---

# 79. One-sentence positioning

For developers:

> **One API for the machine-work economy.**

For humans:

> **See where agents can make money.**

For the deeper company thesis:

> **Moltwork maps the supply, demand and production of machine work.**

---

# 80. Final recommendation

Build Oracle in this order:

```text
immutable raw ingestion
        ↓
canonical Opportunity schema
        ↓
dedupe / identity resolution
        ↓
observation + event history
        ↓
skill/category normalization
        ↓
metric registry
        ↓
daily/hourly rollups
        ↓
REST API
        ↓
simple DefiLlama-style dashboard
        ↓
dogfood with WorkerKit agents
```

The important compounding asset begins at **the very first raw observation**.

The dashboard is just the first useful window into it.

The part I would be most strict about is **not starting with the UI**. The backend should first make `raw observation → canonical opportunity → events/history → standardized metric` completely trustworthy. Then the dashboard becomes almost trivial.

The strongest synthesis from the research is that Moltwork should initially look **more like DefiLlama than Dune**, but its underlying taxonomy and analytical model should look **more like Lightcast than either of them**. Once WorkerKit starts generating real economic outcomes, it gains a dataset neither category has: not merely *labor demand*, but **machine productivity against that demand**. ([DefiLlama][19])

[1]: https://docs.lightcast.io/lightcast-api/reference/overview-global-job-postings?utm_source=chatgpt.com "Overview - Job Postings Global"
[2]: https://github.com/DefiLlama/defillama-adapters?utm_source=chatgpt.com "GitHub - DefiLlama/DefiLlama-Adapters · GitHub"
[3]: https://tokenterminal.com/docs/data-approach?utm_source=chatgpt.com "Our data approach - Token Terminal Docs"
[4]: https://tokenterminal.com/resources/articles/launching-methodologies?utm_source=chatgpt.com "Launching methodologies | Token Terminal"
[5]: https://docs.lightcast.io/lightcast-api/docs/market-expansion?utm_source=chatgpt.com "Market Expansion"
[6]: https://docs.coinglass.com/reference/endpoint-overview?utm_source=chatgpt.com "🔍 Endpoint Overview"
[7]: https://docs.dune.com/api-reference/executions/execution-object?utm_source=chatgpt.com "Overview - Dune Docs"
[8]: https://lightcast.io/our-data/api/access?utm_source=chatgpt.com "Get API Access"
[9]: https://tokenterminal.com/docs/api-reference/best-practices?utm_source=chatgpt.com "Best practices - Token Terminal Docs"
[10]: https://docs.lightcast.io/lightcast-api/reference/us-postings-use-cases?utm_source=chatgpt.com "Use Cases"
[11]: https://docs.coinglass.com/reference/ws-getting-started?utm_source=chatgpt.com "Getting Started"
[12]: https://tokenterminal.com/docs/explorer?utm_source=chatgpt.com "Introduction - Token Terminal Docs"
[13]: https://defillama.com/compare-chains?chainFees=true&chainRevenue=true&chains=Ethereum&chains=Solana&volume=true&utm_source=chatgpt.com "Chain Comparison - TVL, Fees & Activity - DefiLlama"
[14]: https://tokenterminal.com/docs/explorer/metrics?utm_source=chatgpt.com "Metrics - Token Terminal Docs"
[15]: https://defillama.com/protocol/parallel-protocol-v3?utm_source=chatgpt.com "Parallel Protocol V3 TVL, Fees & Revenue"
[16]: https://tokenterminal.com/docs/studio/charts?utm_source=chatgpt.com "Charts - Token Terminal Docs"
[17]: https://tokenterminal.com/docs/api-reference/datasets/list-all-datasets?utm_source=chatgpt.com "List all datasets - Token Terminal Docs"
[18]: https://www.reveliolabs.com/products/terminal?utm_source=chatgpt.com "Workforce Analytics: Labor Market Data & Insights | Revelio Labs"
[19]: https://defillama.com/about?utm_source=chatgpt.com "About DefiLlama - DeFi Dashboard & Crypto Analytics"
