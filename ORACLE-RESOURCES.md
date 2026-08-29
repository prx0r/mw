I did a broad current scan as of **August 28, 2026**. The landscape is substantially bigger than the 46-platform snapshot on gigs.sh: there is now a real layer of **agent-native job markets, bounty markets, service marketplaces, x402 directories, and agent registries**.

The key product insight is that Moltwork should not become another static list. It should become the **normalized live feed across all of them**.

## 1. The canonical seed: gigs.sh

[https://gigs.sh/](https://gigs.sh/?utm_source=chatgpt.com)

gigs.sh currently has **46 verified earning platforms** split into agent task markets, dev bounties, security bounties, competitions, hackathons, content monetization, and API monetization. More importantly, it already exposes structured interfaces rather than just HTML. ([gigs.sh][1])

Use:

```text
https://www.gigs.sh/api/v1/gigs
https://www.gigs.sh/api/openapi.json
https://www.gigs.sh/api/mcp
```

The JSON already contains excellent normalization fields:

```text
title
url
categories
paymentRails
agentAllowed
agentWelcomed
kycRequired
onboardingFriction
a2aProtocol
payoutLatency
minPayout
realisticEarning
officialAgentDocs
verifiedAt
credibility
```

That should be **adapter #1** in Moltwork. 

---

# 2. Actual autonomous-agent job markets

These are the most important category because there is a literal:

```text
discover work
→ decide whether capable
→ claim/bid
→ execute
→ submit
→ get paid
```

### MoltJobs

[https://moltjobs.io/](https://moltjobs.io/?utm_source=chatgpt.com)

Probably the cleanest current implementation. There are real open tasks, Base USDC escrow, eval/certification, CLI, MCP, REST API, Python SDK and TypeScript SDK. Current open jobs were visible during this search on August 28. ([MoltJobs][2])

Machine surface:

```text
GET https://api.moltjobs.io/v1/jobs?status=OPEN
MCP https://api.moltjobs.io/mcp

npm i -g @moltjobs/cli
npx @moltjobs/mcp
npm i @moltjobs/sdk
pip install moltjobs
```

An agent can autonomously search jobs, bid, heartbeat while working, submit results and manage its wallet. ([GitHub][3])

There is also a **separate project**:

[https://molt-jobs.com/](https://molt-jobs.com/?utm_source=chatgpt.com)

It similarly exposes REST, OpenAPI, webhooks and a `/skill.md`; do not accidentally deduplicate these just because of the name. ([MoltJobs][4])

### ClawGig

[https://clawgig.ai/](https://clawgig.ai/?utm_source=chatgpt.com)

This has become one of the strongest ones I found. The site currently reports hundreds of active agents and has live gigs across research, development, writing, design and data. Agents keep 90% of accepted payments. ([ClawGig][5])

Full REST API:

```text
https://clawgig.ai/api/v1

GET  /gigs
POST /gigs/{id}/proposals
GET  /services
POST /agents/register
```

It also has services, contracts, webhooks, files, wallets, autonomous hiring and MCP support. ([ClawGig][6])

This is a **tier-1 Moltwork source**.

### TaskForce

[https://www.task-force.app/](https://www.task-force.app/?utm_source=chatgpt.com)

“Upwork for AI agents & humans.” USDC, milestone escrow, explicit agent API. ([TaskForce][7])

Docs:

[https://www.task-force.app/docs/api](https://www.task-force.app/docs/api?utm_source=chatgpt.com)

Core loop:

```text
POST /api/agent/register
GET  /api/agent/tasks
POST /api/agent/tasks/{id}/apply
GET/POST messages
POST /api/agent/tasks/{id}/submit
```

Registration returns an API key and wallet. It also exposes notifications, polling, disputes and earnings/withdrawal surfaces. ([TaskForce][8])

Another tier-1 ingestion adapter.

### Clustly

[https://clustly.ai/](https://clustly.ai/?utm_source=chatgpt.com)

Designed explicitly so an LLM can self-register. USDC on Solana. ([gigs.sh][9])

```text
POST https://clustly.ai/api/v1/agent/register
GET  https://clustly.ai/api/v1/tasks/open
POST https://clustly.ai/api/v1/tasks/{id}/claim
POST https://clustly.ai/api/v1/tasks/{id}/submit
```

And:

```text
https://clustly.ai/llms.txt
```

This is almost the ideal autonomous-job-board interface.

### Agent Hansa

[https://www.agenthansa.com/](https://www.agenthansa.com/?utm_source=chatgpt.com)

Quest/competition-based rather than guaranteed work-for-pay.

Canonical machine entry point:

```text
https://www.agenthansa.com/llms-full.txt
POST https://www.agenthansa.com/api/agents/register
```

Agent registers, discovers quests, submits output and may receive USDC. ([gigs.sh][10])

### Daydreams TaskMarket

[https://market.daydreams.systems/](https://market.daydreams.systems/?utm_source=chatgpt.com)

Base USDC + ERC-8004 identity. Five useful job mechanisms: bounty, claim, pitch, benchmark and auction. ([gigs.sh][11])

Docs:

[https://docs-market.daydreams.systems/](https://docs-market.daydreams.systems/?utm_source=chatgpt.com)

CLI:

```text
taskmarket init
taskmarket task list --status open
```

Very good for accumulating portable agent reputation.

### BountyBook

[https://www.bountybook.ai/](https://www.bountybook.ai/?utm_source=chatgpt.com)

Base USDC bounty marketplace with automated verification. ([gigs.sh][12])

```text
https://www.bountybook.ai/llms.txt

GET  https://api.bountybook.ai/jobs
POST https://api.bountybook.ai/jobs/{id}/claim
POST https://api.bountybook.ai/jobs/{id}/submit
GET  https://api.bountybook.ai/agents/{address}
```

Excellent ingestion surface.

### AgentPact

[https://agentpact.xyz/](https://agentpact.xyz/?utm_source=chatgpt.com)

Interesting because it is genuinely **agent-to-agent labor**, not simply human → agent.

Agents publish offers and needs and negotiate deals. USDC escrow on Base. ([gigs.sh][13])

Interfaces:

```text
REST: https://api.agentpact.xyz
MCP:  https://mcp.agentpact.xyz/mcp
SDK:  @agentpact/sdk
```

Good Moltwork source for both:

```text
jobs wanted
services offered
```

### NEAR AI Agent Market

[https://market.near.ai/](https://market.near.ai/?utm_source=chatgpt.com)

Agent jobs/services with bidding and escrow. Current public pricing examples included roughly $12–$24 services, and the May snapshot showed thousands of historical jobs. ([gigs.sh][14])

Machine entry:

```text
https://market.near.ai/skill.md
```

### Augmi Marketplace

[https://augmi.world/](https://augmi.world/?utm_source=chatgpt.com)

This was **not in the gigs.sh May seed** and is worth adding.

Agents have ERC-8004 identities and can browse, claim, deliver and earn Base USDC bounties. ([Augmi][15])

Most important feed:

```text
GET https://augmi.world/api/marketplace/bounties?status=OPEN
```

It supports filtering:

```text
?status=OPEN&skills=code,research&minReward=20
```

And bounty creation/claim/submission/approval are programmable.

### AgentLux

[https://agentlux.ai/](https://agentlux.ai/?utm_source=chatgpt.com)

One of the more interesting new ones because it has **both services and bounties** plus ERC-8004 identity and payment-verified reputation. ([agentlux.ai][16])

Docs:

[https://docs.agentlux.ai/](https://docs.agentlux.ai/?utm_source=chatgpt.com)

Machine bootstrap:

```text
https://agentlux.ai/llms.txt
https://api.agentlux.ai/v1/agentlux/start
```

MCP:

```text
npx @agentlux/mcp-server
```

It currently explicitly subsidizes some first jobs, which is useful but should be marked `demand_type=platform_subsidized` rather than pretending it is organic demand. ([agentlux.ai][17])

### AgentWorld

[https://agentworld.me/](https://agentworld.me/?utm_source=chatgpt.com)

Very interesting technically because almost the entire economy is exposed as data.

MCP:

```text
https://agentworld.me/mcp/sse
```

It exposes a `browse_jobs` tool as well as `claim_job` and `submit_job`. ([AgentWorld][18])

Useful public data:

```text
GET https://agentworld.me/api/agentworld/economy
GET https://agentworld.me/api/agentworld/agents
GET https://agentworld.me/api/agentworld/agents/{id}
```

And a research API:

```text
https://agentworld.me/api/data
https://agentworld.me/api/data/openapi.json
```

([AgentWorld][19])

For Moltwork I would ingest the **jobs and economic activity only**, not every unrelated feature the wider site offers.

### Atelier

[https://useatelier.ai/](https://useatelier.ai/?utm_source=chatgpt.com)

Fiverr-like service marketplace where only agents provide the work. Humans or other agents purchase services. USDC on Solana/Base. ([Atelier][20])

Self-onboarding:

```text
https://useatelier.ai/skill.md
```

Provider contract:

```text
GET  /agent/profile
GET  /agent/services
POST /agent/execute
GET  /agent/portfolio
```

That standardization is particularly interesting for Moltwork because you could eventually make a generated Moltwork specialist expose this interface automatically. ([Atelier][21])

### CLAWORK

[https://www.clawork.online/](https://www.clawork.online/?utm_source=chatgpt.com)

Base, ERC-8004 and x402; agents and humans can take work. It emphasizes machine-readable agent profiles and on-chain work reputation. ([CLA Work][22])

Currently the jobs web view requires a wallet, so this is weaker as a public aggregator source than ClawGig/TaskForce/MoltJobs. ([CLA Work][23])

There is also an unrelated/earlier ecosystem project using:

[https://clawork.xyz/](https://clawork.xyz/?utm_source=chatgpt.com)

with:

```text
https://clawork.xyz/api/v1
```

which indexes jobs posted through other agent social networks. Don't merge the `.online` and `.xyz` projects without entity resolution. ([GitHub][24])

### AgentMarket

[https://useagentmarket.xyz/](https://useagentmarket.xyz/?utm_source=chatgpt.com)

ERC-8183/Base agent-work marketplace.

Technically interesting, but during the indexed snapshot it showed **zero jobs and zero volume**, so ingest it but score liquidity close to zero. ([useagentmarket.xyz][25])

### Rentr

[https://www.rentr.live/](https://www.rentr.live/?utm_source=chatgpt.com)

Different model: owners host preconfigured agents and **rent access to them**, earning USDC rather than chasing jobs. Discovery includes skills, pricing, uptime and real-time availability. ([Rentr][26])

This should be normalized as:

```text
opportunity_type = agent_rental
```

rather than a job.

---

# 3. Developer/bounty markets agents can work

gigs.sh currently tracks seven major dev-bounty surfaces: **Algora, boss.dev, Dework, Opire, Stacker News, Superteam Earn and Drips Wave**. ([gigs.sh][27])

| Platform       | URL                                                                               | Agent usefulness                               |
| -------------- | --------------------------------------------------------------------------------- | ---------------------------------------------- |
| Algora         | [https://algora.io/](https://algora.io/?utm_source=chatgpt.com)                   | GitHub issue → PR → bounty. Public API exists. |
| boss.dev       | [https://www.boss.dev/](https://www.boss.dev/?utm_source=chatgpt.com)             | GitHub issue bounties.                         |
| Dework         | [https://dework.xyz/](https://dework.xyz/?utm_source=chatgpt.com)                 | DAO/Web3 bounties.                             |
| Opire          | [https://opire.dev/](https://opire.dev/?utm_source=chatgpt.com)                   | GitHub-native bounty automation.               |
| Stacker News   | [https://stacker.news/](https://stacker.news/?utm_source=chatgpt.com)             | Public bounty posts, including software work.  |
| Superteam Earn | [https://earn.superteam.fun/](https://earn.superteam.fun/?utm_source=chatgpt.com) | Particularly important: explicit AI Agent API. |
| Drips          | [https://www.drips.network/](https://www.drips.network/?utm_source=chatgpt.com)   | PR-based development reward waves.             |

Superteam deserves special treatment. Its agent interface has:

```text
POST /api/agents
GET  /api/agents/listings/live
POST /api/agents/submissions/create
```

and explicitly exposes `AGENT_ONLY` listings. ([gigs.sh][28])

This is probably one of the highest-value non-agent-native feeds to add.

For any platform with account, payout, identity or age requirements, the operator has to meet those rules; Moltwork should never try to automate around them.

---

# 4. Hackathons and competitions

These aren't autonomous recurring jobs, but they're genuine money opportunities that an oracle should expose.

gigs.sh currently maps:

**Hackathons:** Devpost, Encode Club, ETHGlobal and lablab.ai. ([gigs.sh][29])

**Competitions:** AIcrowd, DrivenData, Topcoder Marathon Matches, Zindi and Kaggle/ARC Prize. ([gigs.sh][30])

Canonical roots:

| Site        | URL                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------- |
| Devpost     | [https://devpost.com/](https://devpost.com/?utm_source=chatgpt.com)                               |
| Encode Club | [https://www.encode.club/](https://www.encode.club/?utm_source=chatgpt.com)                       |
| ETHGlobal   | [https://ethglobal.com/](https://ethglobal.com/?utm_source=chatgpt.com)                           |
| lablab.ai   | [https://lablab.ai/](https://lablab.ai/?utm_source=chatgpt.com)                                   |
| AIcrowd     | [https://www.aicrowd.com/](https://www.aicrowd.com/?utm_source=chatgpt.com)                       |
| DrivenData  | [https://www.drivendata.org/](https://www.drivendata.org/?utm_source=chatgpt.com)                 |
| Topcoder    | [https://www.topcoder.com/](https://www.topcoder.com/?utm_source=chatgpt.com)                     |
| Zindi       | [https://zindi.africa/](https://zindi.africa/?utm_source=chatgpt.com)                             |
| Kaggle      | [https://www.kaggle.com/competitions](https://www.kaggle.com/competitions?utm_source=chatgpt.com) |

I would model these separately as:

```text
opportunity_type = competition
expected_value = prize × estimated_win_probability
deadline
eligibility
submission_requirements
build_time_estimate
```

rather than mixing them with guaranteed-price jobs.

---

# 5. Sell the agent itself: API/service marketplaces

This category may ultimately be more important than gigs.

Instead of:

```text
find job → work → submit
```

you get:

```text
deploy capability once
→ publish
→ agents discover it
→ calls arrive
→ earn automatically
```

### the402

[https://the402.ai/](https://the402.ai/?utm_source=chatgpt.com)

Extremely relevant.

It supports data APIs, automated services, human services, subscriptions and digital products. Providers get webhooks and earnings tracking. ([the402][31])

**Best public ingestion endpoint:**

```text
GET https://api.the402.ai/v1/services/catalog
```

Search/filter:

```text
?q=
?category=
?service_type=
?max_price=
?provider=
?min_reputation=
?limit=
?offset=
```

It exposes pricing, provider reputation, completion metrics and deliverable schemas. ([the402][31])

Also:

```text
https://api.the402.ai/.well-known/the402.json
npx @the402/mcp-server
```

Fantastic source.

### AgenticTrade

[https://agentictrade.io/](https://agentictrade.io/?utm_source=chatgpt.com)

Providers publish a callable capability and get USDC per invocation. ([AgenticTrade][32])

```text
GET  https://agentictrade.io/api/v1/services
GET  https://agentictrade.io/api/v1/discover
POST https://agentictrade.io/api/v1/agents/onboard
MCP  https://agentictrade.io/api/v1/mcp
```

Excellent ingestion target.

### APIHub

[https://apihub.io/](https://apihub.io/?utm_source=chatgpt.com)

This one is especially valuable to Moltwork because it is already behaving like a **meta-index**.

Current marketplace showed hundreds of services and external x402 endpoints. ([APIHub][33])

Public APIs:

```text
GET  https://api.apihub.io/v1/services
GET  https://api.apihub.io/v1/services/{slug}
GET  https://api.apihub.io/v1/external
POST https://api.apihub.io/v1/search
```

`/v1/external` is particularly useful: it indexes external services discovered from x402 activity. ([APIHub][34])

### Circle Agent Marketplace / Agent Stack

[https://www.circle.com/agent-stack](https://www.circle.com/agent-stack?utm_source=chatgpt.com)

Institutional agent marketplace + payment stack. Developers can expose endpoints and earn per call from agent customers. ([Circle][35])

I would ingest its marketplace but also use it as a signal that `x402-paid API` is becoming a proper revenue primitive rather than a hackathon novelty.

### Skyfire

[https://skyfire.xyz/](https://skyfire.xyz/?utm_source=chatgpt.com)

Docs:

[https://docs.skyfire.xyz/](https://docs.skyfire.xyz/?utm_source=chatgpt.com)

Explicit buyer/seller agent accounts. Seller agents publish APIs/services; buyer agents discover and purchase them programmatically. ([Skyfire Developer Portal][36])

### AuraGate

[https://www.auragate.app/](https://www.auragate.app/?utm_source=chatgpt.com)

Newer x402/Circle marketplace for data and APIs.

Machine catalog:

```text
https://www.auragate.app/api/agent
```

It currently exposes usage/revenue metrics on the site as well. ([Auragate][37])

### req402

[https://www.req402.com/](https://www.req402.com/?utm_source=chatgpt.com)

Wrap any API, set price, publish and receive USDC per request. Discovery is explicitly programmatic. ([Req402][38])

### GigSoul

[https://gigsoul.com/](https://gigsoul.com/?utm_source=chatgpt.com)

Brand new this week.

Publish an HTTP endpoint and earn per agent call.

Machine/payment docs:

```text
https://gigsoul.com/x402
```

([GigSoul][39])

### Agent Bazaar

[https://www.agent-bazaar.com/](https://www.agent-bazaar.com/?utm_source=chatgpt.com)

Pay-per-use **skills**, not just APIs. Seller lists a skill, agent buyers discover and purchase it via x402. ([Agent Bazaar][40])

This is particularly relevant to the Moltwork idea of selling specialized configurations/capabilities.

### tools402

[https://tools402.dev/](https://tools402.dev/?utm_source=chatgpt.com)

Docs:

[https://docs.tools402.dev/](https://docs.tools402.dev/?utm_source=chatgpt.com)

Host HTTPS API → list → collect USDC calls. Supports several chains and multiple facilitators. ([Tools402 Docs][41])

### FiatDock

[https://fiatdock.com/](https://fiatdock.com/?utm_source=chatgpt.com)

Specifically markets itself as an **MCP marketplace**: developers publish MCP services, agents discover them and pay per call using x402. ([FiatDock][42])

This is a very good place to distribute a Moltwork-generated specialist tool.

### 402bazaar

[https://402bazaar.com/](https://402bazaar.com/?utm_source=chatgpt.com)

Agents can search, compare and buy APIs; sellers list endpoints and receive USDC. Includes machine JSON, MCP and schema-driven discovery. ([402 Bazaar][43])

### x402 Bazaar independent marketplace

[https://www.x402bazaar.org/](https://www.x402bazaar.org/?utm_source=chatgpt.com)

Different from Coinbase's canonical Bazaar.

It has over 100 APIs indexed and provides a CLI/MCP/SDK stack. ([x402 Bazaar][44])

### XDC AI

Docs:

[https://docs.xdcai.tech/](https://docs.xdcai.tech/?utm_source=chatgpt.com)

Agent-native API marketplace; service providers list an API and receive USDC calls. ([XDC AI Docs][45])

### RelAI

[https://relai.fi/](https://relai.fi/?utm_source=chatgpt.com)

More infrastructure-heavy, but includes a marketplace where API operators can publish x402 endpoints and get paid across multiple networks. ([Relai][46])

### Agoragentic

[https://agoragentic.com/](https://agoragentic.com/?utm_source=chatgpt.com)

Agent marketplace + Agent OS, Base USDC, x402. Agents can sell callable capabilities. ([gigs.sh][47])

### FAL

[https://fal.ai/](https://fal.ai/?utm_source=chatgpt.com)

Much less “agent economy”-branded but established: model/API creators can host inference and potentially monetize through its marketplace. gigs.sh includes it as an API-monetization surface. ([gigs.sh][48])

---

# 6. The most important meta-source: Coinbase x402 Bazaar

This may be the most important discovery I would encode into Moltwork.

Coinbase now exposes a **free machine-readable index of x402 endpoints**.

Documentation:

[https://docs.cdp.coinbase.com/x402/bazaar](https://docs.cdp.coinbase.com/x402/bazaar?utm_source=chatgpt.com)

Full catalog:

```text
GET https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources
```

It supports up to **1,000 resources per request**, with pagination. No API key is required for the read-only discovery API. ([Coinbase Developer Documentation][49])

Semantic search:

```text
GET https://api.cdp.coinbase.com/platform/v2/x402/discovery/search
```

Filters include:

```text
query
network
asset
payTo
maxUsdPrice
scheme
extensions
```

And there is an MCP server:

```text
https://api.cdp.coinbase.com/platform/v2/x402/discovery/mcp
```

with:

```text
search_resources
proxy_tool_call
```

([Coinbase Developer Documentation][49])

**This should be one of your canonical ingestion backbones.**

You do not need to manually discover every x402 directory if the underlying endpoint is already in Bazaar.

---

# 7. ERC-8004 discovery: 8004scan

[https://8004scan.io/](https://8004scan.io/?utm_source=chatgpt.com)

This isn't itself a job marketplace, but it's hugely valuable for the Moltwork graph.

Public API:

```text
GET https://8004scan.io/api/v1/public/agents
GET https://8004scan.io/api/v1/public/agents/search?q=code+review
GET https://8004scan.io/api/v1/public/agents/{chainId}/{tokenId}
```

Also:

```text
feedback
owners
chains
stats
semantic agent search
OpenAPI
```

Anonymous API usage is supported. ([8004scan][50])

So Moltwork can map:

```text
marketplace job
        ↓
required capability
        ↓
known agents
        ↓
ERC-8004 identity
        ↓
reputation
        ↓
historical completed jobs
```

That is much more useful than a dumb job board.

---

# 8. Security-bounty markets

gigs.sh tracks nine major ones:

**Code4rena, Bugcrowd, Google OSS VRP, HackenProof, HackerOne/Cantina, huntr, Immunefi, Intigriti and Sherlock.** ([gigs.sh][51])

I would ingest these, but classify them as:

```text
agent_mode = assisted
human_verification_required = true
```

rather than allowing an autonomous worker to spray submissions. These platforms strongly penalize poor-quality or unverifiable reports. ([gigs.sh][51])

HackenProof is particularly interesting because gigs.sh reports that it already ships an agent MCP interface. ([gigs.sh][51])

---

# 9. What I would actually build into Moltwork

Don't build:

```text
Yet Another Agent Job Directory
```

Build:

```text
                MOLTWORK OPPORTUNITY ORACLE

                     ┌─ gigs.sh
                     ├─ MoltJobs
                     ├─ ClawGig
                     ├─ TaskForce
                     ├─ Clustly
                     ├─ Superteam
                     ├─ Augmi
                     ├─ AgentLux
                     ├─ AgentWorld
                     ├─ BountyBook
                     ├─ Daydreams
                     ├─ AgentPact
                     ├─ NEAR
                     ├─ Dev bounty feeds
                     ├─ Hackathons
                     ├─ Competitions
                     │
Internet ─────────────┤
                     │
                     ├─ Coinbase x402 Bazaar
                     ├─ APIHub
                     ├─ the402
                     ├─ AgenticTrade
                     ├─ Circle marketplace
                     ├─ Skyfire
                     ├─ FiatDock
                     ├─ tools402
                     ├─ Agent Bazaar
                     └─ 8004scan
                              │
                              ▼
                     NORMALIZATION LAYER
                              │
                              ▼
                         OPPORTUNITY DB
                              │
                 ┌────────────┼─────────────┐
                 ▼            ▼             ▼
              $ jobs       services       contests
                 │            │             │
                 └────────────┼─────────────┘
                              ▼
                         MATCHING ENGINE
                              │
                     can my agent do it?
                              │
                probability of acceptance
                              │
                       expected profit
                              │
                       expected runtime
                              │
                       trust / liquidity
                              ▼
                           QUEUE
```

## Canonical schema

I would normalize every opportunity into something roughly like:

```json
{
  "id": "source:native_id",
  "source": "clawgig",
  "source_url": "...",
  "type": "task|bounty|service_demand|competition|hackathon|api_market",
  "title": "...",
  "description": "...",

  "reward": {
    "amount": 25,
    "currency": "USDC",
    "guaranteed": true
  },

  "requirements": {
    "skills": ["research", "python"],
    "deliverables": [],
    "deadline": "...",
    "verification": "human|oracle|tests|merge|leaderboard"
  },

  "agent": {
    "explicitly_allowed": true,
    "fully_autonomous": true,
    "registration_required": true,
    "api_available": true,
    "mcp_available": true,
    "skill_md": null
  },

  "economics": {
    "platform_fee_pct": 10,
    "estimated_cost": 0.31,
    "estimated_runtime_minutes": 18,
    "estimated_success_probability": 0.74,
    "expected_profit": 18.27
  },

  "market": {
    "liquidity_score": 0.72,
    "competition_score": 0.45,
    "trust_score": 0.81
  },

  "retrieved_at": "...",
  "raw": {}
}
```

Then the killer derived value is:

```text
EXPECTED VALUE =
    payout
  × probability(agent succeeds)
  × probability(work accepted)
  × probability(payment occurs)
  - inference cost
  - API/tool cost
  - transaction fees
  - expected human-escalation cost
```

Now we're no longer building an agent job search engine.

We're building:

> **“Given this exact agent, where on the entire internet can it deploy its capabilities for the highest expected return right now?”**

That is far more compelling.

## The initial canonical adapters I would ship

For an MVP I would **not** build 60 bespoke connectors. Start with these because together they give enormous coverage:

```text
01 gigs.sh
   https://www.gigs.sh/api/v1/gigs

02 Coinbase x402 Bazaar
   https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources

03 APIHub
   https://api.apihub.io/v1/services
   https://api.apihub.io/v1/external

04 MoltJobs
   https://api.moltjobs.io/v1/jobs?status=OPEN

05 ClawGig
   https://clawgig.ai/api/v1/gigs

06 TaskForce
   https://task-force.app/api/agent/tasks

07 Clustly
   https://clustly.ai/api/v1/tasks/open

08 Augmi
   https://augmi.world/api/marketplace/bounties?status=OPEN

09 BountyBook
   https://api.bountybook.ai/jobs

10 the402
   https://api.the402.ai/v1/services/catalog

11 Superteam Earn
   /api/agents/listings/live

12 AgenticTrade
   https://agentictrade.io/api/v1/services

13 8004scan
   https://8004scan.io/api/v1/public/agents
```

Those alone give you **jobs + bounties + paid services + x402 demand + agent identity/reputation + a meta-directory of another 46 earning platforms**.

That is the canonical foundation I would give the coding agent first. The next layer is a discovery worker continuously finding new markets and automatically generating candidate adapters, because the most striking part of this research is how many of these launched only in the last few months. 

One compliance point: where a marketplace requires operator identity, age verification, KYC, tax forms, or a human claim step, Moltwork should expose that requirement explicitly and never attempt to bypass it.

[1]: https://www.gigs.sh/ "gigs.sh — The agent-native internet"
[2]: https://moltjobs.io/?utm_source=chatgpt.com "MoltJobs: AI Agent Job Marketplace - Get Paid in USDC"
[3]: https://github.com/Moltjobs?utm_source=chatgpt.com "Moltjobs · GitHub"
[4]: https://www.molt-jobs.com/?utm_source=chatgpt.com "MoltJobs - Work for yourself. Get paid."
[5]: https://clawgig.ai/?utm_source=chatgpt.com "ClawGig — The Freelance Marketplace for AI Agents | ClawGig"
[6]: https://clawgig.ai/docs?utm_source=chatgpt.com "API Documentation — ClawGig AI Agent REST API Reference | ClawGig"
[7]: https://www.task-force.app/?utm_source=chatgpt.com "TaskForce - Work Marketplace for AI Agents & Humans"
[8]: https://www.task-force.app/docs/api?utm_source=chatgpt.com "TaskForce - Work Marketplace for AI Agents & Humans"
[9]: https://www.gigs.sh/p/clustly "Clustly — agent earning guide | gigs.sh"
[10]: https://www.gigs.sh/p/agent-hansa "Agent Hansa — agent earning guide | gigs.sh"
[11]: https://www.gigs.sh/p/daydreams-taskmarket "Daydreams TaskMarket — agent earning guide | gigs.sh"
[12]: https://www.gigs.sh/p/bountybook "BountyBook — agent earning guide | gigs.sh"
[13]: https://www.gigs.sh/p/agent-pact "AgentPact — agent earning guide | gigs.sh"
[14]: https://www.gigs.sh/p/near-ai-agent-market "NEAR AI Agent Market — agent earning guide | gigs.sh"
[15]: https://augmi.world/blog/augmi-marketplace-tutorial?utm_source=chatgpt.com "How to Use the Augmi Agent Marketplace: Register, Post Bounties, and Earn USDC | Augmi Blog"
[16]: https://agentlux.ai/?utm_source=chatgpt.com "AgentLux: Give Your AI Agent a Face and a Track Record"
[17]: https://agentlux.ai/start?utm_source=chatgpt.com "Start — Give This to Your Agent | AgentLux"
[18]: https://agentworld.me/mcp?utm_source=chatgpt.com "AgentWorld MCP — Developer Hub"
[19]: https://agentworld.me/agent-dashboard?utm_source=chatgpt.com "Agent Dashboard — AgentWorld Control Panel for AI Agents"
[20]: https://useatelier.ai/docs?utm_source=chatgpt.com "Introduction | Atelier"
[21]: https://useatelier.ai/blog/how-to-build-ai-agent-that-earns-money?utm_source=chatgpt.com "How to Build an AI Agent That Earns Money on Atelier"
[22]: https://www.clawork.online/?utm_source=chatgpt.com "CLAWORK — Hire AI agents. Get work done."
[23]: https://www.clawork.online/jobs?utm_source=chatgpt.com "CLAWORK — Hire AI agents. Get work done."
[24]: https://github.com/dvcrn/openclaw-skills-marketplace/blob/main/plugins/mapessaprince--clawork/skills/clawork/SKILL.md?utm_source=chatgpt.com "openclaw-skills-marketplace/plugins/mapessaprince--clawork/skills/clawork/SKILL.md at main · dvcrn/openclaw-skills-marketplace · GitHub"
[25]: https://useagentmarket.xyz/?utm_source=chatgpt.com "AgentMarket — AI Task Marketplace on Base"
[26]: https://www.rentr.live/?utm_source=chatgpt.com "Rentr — Rent AI Agents Instantly | USDC on Base"
[27]: https://www.gigs.sh/c/dev-bounty "Dev bounties (7) for AI agents — gigs.sh"
[28]: https://www.gigs.sh/p/superteam-earn?utm_source=chatgpt.com "Superteam Earn — agent earning guide | gigs.sh"
[29]: https://www.gigs.sh/c/hackathon "Hackathons (4) for AI agents — gigs.sh"
[30]: https://www.gigs.sh/c/competition "Competitions (5) for AI agents — gigs.sh"
[31]: https://the402.ai/docs/?utm_source=chatgpt.com "Documentation — the402"
[32]: https://agentictrade.io/docs/getting-started?utm_source=chatgpt.com "Getting Started — AgenticTrade | AI Agent Service Marketplace"
[33]: https://apihub.io/marketplace?utm_source=chatgpt.com "API Marketplace - APIHub"
[34]: https://apihub.io/docs/api-reference?utm_source=chatgpt.com "APIHub - The MCP Marketplace for AI Agent APIs"
[35]: https://www.circle.com/agent-stack?utm_source=chatgpt.com "Circle Agent Stack | Agentic AI Tools for Financial Services | Circle"
[36]: https://docs.skyfire.xyz/?utm_source=chatgpt.com "Developer Documentation"
[37]: https://www.auragate.app/?utm_source=chatgpt.com "AuraGate — The gateway for AI agents to move value."
[38]: https://www.req402.com/?utm_source=chatgpt.com "req402 - Monetize APIs and AI Agents with Crypto Micropaymen"
[39]: https://gigsoul.com/?utm_source=chatgpt.com "GigSoul — The Soul of AI"
[40]: https://www.agent-bazaar.com/?utm_source=chatgpt.com "Agent Bazaar — AI Skills Marketplace | x402 Pay-Per-Use"
[41]: https://docs.tools402.dev/?utm_source=chatgpt.com "Welcome · tools402 docs"
[42]: https://www.fiatdock.com/mcp-marketplace.html?utm_source=chatgpt.com "The MCP marketplace for AI agents — discover & pay for MCP services | FiatDock"
[43]: https://402bazaar.com/?utm_source=chatgpt.com "402bazaar.com — The Marketplace Where Agents Shop"
[44]: https://www.x402bazaar.org/?utm_source=chatgpt.com "x402 Bazaar — The API Marketplace for AI Agents"
[45]: https://docs.xdcai.tech/?utm_source=chatgpt.com "Overview | XDC AI Docs"
[46]: https://relai.fi/?utm_source=chatgpt.com "RelAI — Payment infrastructure for autonomous AI agents"
[47]: https://gigs.sh/p/agoragentic?utm_source=chatgpt.com "Agoragentic — agent earning guide | gigs.sh"
[48]: https://www.gigs.sh/c/api-monetization?utm_source=chatgpt.com "API monetization (6) for AI agents — gigs.sh"
[49]: https://coinbase-cloud.mintlify.app/x402/bazaar?utm_source=chatgpt.com "x402 Bazaar (Discovery Layer) - Coinbase Developer Documentation"
[50]: https://8004scan.io/developers?utm_source=chatgpt.com "Developers | 8004scan"
[51]: https://www.gigs.sh/c/security-bounty "Security bounties (9) for AI agents — gigs.sh"
