# MOLTWORK MEGA AUDIT

**Date:** 2026-08-28
**Repos:** `/root/get-me-money` + `/root/repute`
**Strategy docs:** STRATEGY-1 (workerkit vision), STRATEGY-2 (work SDK + Moltbook)
**Purpose:** Honest review of everything that exists, what's good, what's broken, where the money is

---

## PART 1: THE THESIS

Nobody owns this path yet:

```
existing agent
  → install work layer
    → search all earning surfaces
      → choose best work
        → complete/submit externally
          → preserve verified WorkRun
            → turn successful work into reusable/sellable capability
```

The market is fragmented into pieces. That's the opportunity.

---

## PART 2: COMPETITIVE LANDSCAPE

### Layer Map

| Layer | Who | What they own | Threat to Moltwork |
|---|---|---|---|
| **Work discovery** | **gigs.sh** | Agent-readable directory of 46 earning platforms, MCP/API/OpenAPI | High — integrate, don't clone |
| **Agent job boards** | **MoltJobs**, Clustly, AgentBounty | Jobs, bidding, execution, verification, escrow | Supply sources, not enemies |
| **Work protocols** | **Work402**, **WorkProtocol**, x402 Hub | Claim → submit → settle; portable reputation | Important overlap with work history/proof |
| **Agent services** | **the402** | Agents/services discoverable and purchasable; x402 + reputation | Competes with eventual services market |
| **Agent/config assets** | **Soul.Markets** | Sell execution services or replicate `soul.md` expertise/config | Closest competitor to asset thesis |
| **Skill/config stores** | AIMX, MintSkills, Agensi, iUseAgent | Sell agents, skills, MCPs, prompts/configs | Don't compete as generic store |
| **Identity** | **Moltbook** | Portable authenticated agent identity/reputation | Perfect upstream identity provider |
| **Professional memory** | GBrain, Letta | Learning, memory, skill evolution | Underlying worker technology |
| **Runtime** | Hermes, Letta Code, others | Actually performs the work | Replaceable substrate |
| **SaaS access** | **Ampersand** | 150+ SaaS connectors through MCP/SDK | Useful capability provider, not competitor |

### The closest competitor: Soul.Markets

Soul.Markets says: "Infrastructure is commodity; an agent's judgment/expertise is the asset."

An agent publishes a `soul.md`, exposes paid services, lets another agent replicate that soul, transacts through x402.

But Soul.Markets starts here:

```
"I have expertise"
      ↓
publish it
      ↓
sell it
```

Moltwork can start:

```
real external bounty
       ↓
actual WorkRun
       ↓
actual artifact
       ↓
external verification
       ↓
actual acceptance/payment
       ↓
THIS configuration/skill produced it
       ↓
publish capability
```

That's a radically stronger provenance story.

### What to consume, not build

Don't invent Moltwork Reputation Protocol. Consume:

- WorkProtocol reputation
- ERC-8004 reputation
- Moltbook identity
- board-native reputation
- wallet receipts
- GitHub PR evidence

Then Moltwork says: "Here is everything this worker has demonstrably accomplished across the internet."

### What nobody else does

Everyone else wants to own a vertical:

- MoltJobs: "Do jobs **here**."
- Soul.Markets: "Sell capabilities **here**."
- the402: "Sell services **here**."
- Work402: "Execute jobs through **this protocol**."
- gigs.sh: "Discover earning sites."
- GBrain: "Become a better agent."
- Moltbook: "Maintain agent identity."

Moltwork can say: **"Use all of them."**

```
                    YOUR AGENT
                       │
                 Install Moltwork
                       │
        ┌──────────────┼───────────────┐
        ▼              ▼               ▼
    MoltJobs       AgentBounty       Work402
    Clustly        x402 Hub          future board
        │              │               │
        └──────────────┼───────────────┘
                       ▼
                    WORKRUN
                       │
              external acceptance
                       │
                       ▼
               capability proof
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
      profile       service        asset
                                      │
                             skill/config/build
```

Moltwork = **the work layer**. The marketplace is just where accumulated work becomes economically reusable.

---

## PART 3: THE FIVE REAL PROBLEMS

### 1. Opportunity routing

gigs.sh solves platform discovery. But someone still needs to turn many heterogeneous sources into:

```
find_work(
    worker=current_worker,
    objective="earn first dollar"
)
```

Moltwork should normalize enough fields to rank them, not build a universal ontology.

### 2. Portable worker state

```
seen → skipped → attempting → submitted → accepted → rejected → paid
```

Per worker/per opportunity. That's the memory that stops an agent rediscovering and redoing the same jobs.

### 3. Capability-aware selection

```
WORKER CAPABILITY
       ×
JOB REQUIREMENTS
       ×
PAYOUT / COMPETITION
       ↓
WHAT SHOULD I DO NEXT?
```

GBrain/Hermes/Letta know what the agent can do. Moltwork knows what jobs exist. The join is the product.

### 4. Proof lineage (the moat)

```
External Job #481
     │
     ├── Worker
     ├── Runtime/version
     ├── WorkerKit build
     ├── Skills + versions
     ├── WorkRun
     ├── Deliverable
     ├── Verification
     ├── Submission
     └── $25 payment
              ↓
       CAPABILITY PROOF
```

A buyer doesn't have to believe "Reddit Research Skill — amazing!!!"

They see: "Used on 19 external research jobs, 16 accepted, $412 earned."

### 5. What NOT to auto-publish

Don't automatically resell external artifacts. Some bounty work is confidential, buyer-assigned, or restrictively licensed.

Instead:

```
JOB COMPLETE
     ↓
always:
✓ record private WorkRun
✓ add permitted proof to profile

then determine:
○ artifact publishable?
○ methodology publishable?
○ skill publishable?
○ repeatable service publishable?
○ worker configuration publishable?
```

Even when `report.pdf` can't be sold, the worker can offer: "Commission a private report using the workflow that produced this accepted result."

---

## PART 4: THE KILLER WEDGE

**"Earn your agent's first $."**

One click.

```
Connect existing agent
       ↓
discover earning surfaces
       ↓
find easiest compatible real bounty
       ↓
do it
       ↓
verify
       ↓
submit
       ↓
show:
"Your first work is submitted."
```

Then sneak in the compounding behavior:

```
✓ Work added to Moltwork profile

This work also created:
Research capability evidence

Make reusable:
[ Offer this as a service ]
```

No leasing engine. No NFT. No complicated licensing architecture. No agent genome economy.

Just: **"You already did valuable work. Don't throw away what you learned."**

### MVP success metrics

1. Median time from `moltwork install` to first valid external submission
2. % of newly connected agents that submit one legitimate job within 24 hours
3. % that receive their first payment

---

## PART 5: THE TWO REPOS — FILE-BY-FILE AUDIT

### get-me-money (The Worker)

**Location:** `/root/get-me-money/`
**Lines:** ~3,400 Python
**Dead code:** ~1,040 lines (30%)
**Real executions:** 0 completed
**Blocked on:** Hermes LLM provider auth

#### BEST FILES (the ones that matter)

**`executor/__init__.py` — 167 lines, the core pipeline**
The 8-step lifecycle is the real product:
```
claim → build_job_profile → run_task → verify → submit → record_skill_performance → check_status → create_workrun
```
This is clean. It separates the controller (Moltwork) from the worker (Hermes). The controller owns economic decisions; Hermes only does work. That's the right architecture.

**`evaluator/__init__.py` — 100 lines, the money brain**
Cash-EV scoring with beta-binomial calibration. Estimates cost from category hours × token rate. Computes prior probability from payment_reliability, category, competition, verification_strength. Calibrates with Memory. Applies budget gates. This is the module that answers "should I take this job?"

**`broker/__init__.py` — 348 lines, the capability matcher**
Maps TaskCategory → skill bundles. Has TRUSTED_SKILLS catalog. `analyze_requirements()` determines needed skills. `build_job_profile()` creates isolated hermes home + workspace per job. Records skill performance. `best_bundle()` looks up historically best-performing skill combo. This is the closest thing to the "capability-aware selection" problem.

**`hermes_runtime.py` — 184 lines, the execution boundary**
Spawns `hermes -z <prompt> --usage-file <path>`. Writes TASK.md with security boundary. Parses output for artifacts, cost, submission data. Validates SUBMISSION.md exists. Sandboxes env. This is the clean separation between Moltwork and Hermes.

**`ledger/__init__.py` — 126 lines, the truth store**
Append-only JSONL with dedup, fsync, daily/lifetime spend tracking. Simple, correct, enough.

#### COOLEST FEATURES

1. **CapabilityBroker + Hermes isolation** — The broker creates a per-job Hermes home with isolated env vars. The worker never sees Moltwork's API keys. The controller never sees the worker's LLM keys. That's real security architecture.

2. **Beta-binomial calibration** — Memory doesn't just track win/loss. It uses Bayesian shrinkage so early lucky wins don't dominate probability estimates. With only 3 jobs, your estimate is pulled toward the prior. With 20 jobs, the data speaks. That's mathematically honest.

3. **Cash-EV evaluator** — Not "which job pays most." Which job has the highest `P(get_paid) × payout ÷ estimated_time` given THIS worker's track record. That's the right question.

4. **Independent verifier** — Blind to builder reasoning. Checks only artifacts and content. Category-specific rules (code gets different checks than research). That's the right separation.

5. **Append-only ledger with reconciliation** — Latest-record-wins for idempotent updates. Pragmatic for a single-writer system. No database to corrupt.

#### FLAWS

1. **30% dead code** — repute/__init__.py (787 lines), platforms/moltwork.py (154 lines), oracle.py (99 lines). All never called. The repute module is especially bad: it shadows the Outcome model, has its own _append() duplicating the ledger, and writes to 4 JSONL files that don't exist.

2. **No tests** — One smoke test (23 lines). No adapter tests, no CLI tests, no integration tests. The evaluator, broker, verifier, and executor have zero test coverage.

3. **Naming chaos** — pyproject.toml says "moltwork", package is "get_me_money", CLI uses "moltwork" prefix, systemd uses "gmm". One project, four names.

4. **Fabricated strategy data** — strategies.jsonl shows 100% win rates on 5 runs that never happened. dashboard.json is all zeros. The data lies about what the system has done.

5. **Shallow verification** — The verifier checks file existence and content length. It doesn't run tests, lint, build, or any real quality check. "Verified" means "has files and they're not empty."

6. **Platform adapter drift** — MoltJobs adapter uses Platform.CUSTOM instead of Platform.MOLTJOBS. Config enables algora/opire/clustly but no adapters exist. 14 Platform enum values, 4 adapters.

7. **Systemd entry point mismatch** — Services reference gmm-daemon/gmm-serve but pyproject.toml defines moltwork-daemon/moltwork-serve. The services won't start.

8. **.env credential exposure** — data/.env has OPENCODE_GO_API_KEY in plaintext. .gitignore covers data/config.json and data/*.jsonl but not data/.env.

#### CONFUSING THINGS

- Why does `repute/__init__.py` exist inside get-me-money? It's a 787-line rubric-based quality system that's never imported. It has its own Outcome, its own _append(), its own data files. It looks like a separate project that was dropped in and forgotten.

- Why does `platforms/moltwork.py` exist? The executor bypasses it and calls Moltwork directly. It's a post-job-hook adapter that was replaced by inline code.

- Why does `oracle.py` exist? It writes oracle-queue.json but nothing in the main path reads it. The dashboard shows the queue but it's always empty.

- The `human-tasks/` Cloudflare Worker (285 lines) has no integration with `get_me_money/human_tasks.py`. They're two separate implementations of the same concept.

---

### repute (The Marketplace)

**Location:** `/root/repute/`
**Lines:** ~1,800 Python/TS
**Dead code:** ~105 lines (6%)
**Tests:** 496 lines (real tests!)
**Status:** Early prototype, simulated payments

#### BEST FILES (the ones that matter)

**`server.py` — 1,364 lines, the entire application**
12 DB tables, 35+ routes, inline HTML SPA. Yes it's a monolith. But it WORKS. Every endpoint is tested. The data models are clean. The flow from publish → inspect → buy → unlock is complete. This is the most complete piece of code in either repo.

**`src/commitment.py` — 337 lines, the crypto core**
Merkle tree, chunking, artifact envelopes, HMAC-based Fisher-Yates shuffle for reveal order. Neither party controls reveal order — it's derived from a shared secret. That's cryptographically sound. No external crypto libs. Just hashlib.

**`src/reveal.py` — 231 lines, the money mechanism**
Progressive paid reveal: pay per chunk, every cent counts toward full ownership. In-memory state (lost on restart, but that's fixable). The reveal engine is the product's core innovation.

**`src/context_pack.py` — 250 lines, the product taxonomy**
9 product types with schemas, pricing oracle using comparables, demand signals with unfulfilled rates, composition chains. This is the "typed knowledge products" system. Well designed.

**`tests/test_core.py` — 264 lines, real tests**
Chunking, context packs, pricing, reveal, x402, MCP, Merkle proofs. All passing. This is what get-me-money doesn't have.

#### COOLEST FEATURES

1. **Progressive paid reveal** — Instead of "trust the seller or don't buy," you pay $0.025 per random 250-token chunk. Every cent counts toward full ownership. The reveal order is HMAC-derived — neither buyer nor seller can predict which chunks come first. That's a genuinely novel mechanism.

2. **Merkle commitment** — The seller commits to an artifact via SHA-256 Merkle tree. Every chunk has a proof. You can verify any chunk against the root without seeing the whole thing. That's real cryptographic commitment, not theater.

3. **Demand tracking** — `search_count`, `unique_buyers`, `attempted_spend`, `fulfilled_count`, `unfulfilled_rate`. The marketplace knows what people are looking for but can't find. That's valuable signal.

4. **Context packs** — Typed knowledge products with schemas: oracle, monitor, dataset, evidence_pack, context_pack, index, classifier, transformer, synthesis. Each type has required/optional fields, pricing heuristics, confidence scores. That's a real product taxonomy.

5. **Board/storefront system** — Specialist storefronts with product curation, standing orders, category filtering. Not just a flat listing. Workers can create branded presences.

6. **MCP integration** — 12 tools defined, 16 in the TypeScript shim. Any agent can interact with the marketplace via MCP. That's the right interface for an agent-native marketplace.

#### FLAWS

1. **Monolithic server.py** — 1,364 lines. All routes, DB init, caching, reputation, HTML frontend. Should be split into routers. One file is one merge conflict away from unmaintainable.

2. **No real encryption** — XOR "encryption" (line 292: `"Encrypt" (XOR with key for V1 -- real encryption would use AES-GCM)`). The code acknowledges this but it's still active. That's security theater.

3. **No authentication** — Anyone can create workers, publish, buy, refund. The `buyer_id` is caller-provided. No Moltbook integration yet (the `/api/agents/verify-moltbook` route is a stub that always returns `{"verified": True, "karma": 482}`).

4. **In-memory state loss** — ProgressiveReveal stores all purchase state in memory dicts. Server restart = all purchase states lost. Only envelope metadata persists in SQLite/JSONL.

5. **Broken MCP pool routes** — `moltwork_pools` hits `/api/pools` which doesn't exist. Should be `/api/requests`. The MCP shim is out of sync with the server.

6. **Cache invalidation bugs** — `board_storefront` (line 820) defines `"products"` key twice. Some caches load from DB at startup but don't sync after writes.

7. **No input validation** — `publish_context_pack` endpoint accepts `req: dict` (raw dict), bypassing Pydantic validation entirely.

8. **Hand-rolled test harness** — Uses custom `test()` functions instead of pytest. Tests delete the database file at module import time.

#### CONFUSING THINGS

- `server.py` is 1,364 lines but `src/` modules (commitment, reveal, context_pack, x402, mcp) are well-separated. Why wasn't server.py split into routers the same way?

- The `offers` table is created in init_db() but no endpoint reads or writes it. Who was this for?

- The `stacks` table and `stacks_cache` are loaded but no endpoint creates stacks. Dead schema.

- The `purchases` table is declared but never written. Purchase tracking is done in-memory via `ProgressiveReveal`. Why have the table?

- MCP shim registers `moltwork_pools` and `moltwork_pool` but server.py has no `/api/pools` routes. Was this renamed from pools to requests without updating the shim?

---

## PART 6: PRODUCT THREADS — WHAT'S SEPARATE, WHAT'S CONNECTED

### Thread 1: The Worker (get-me-money)
Purpose: Find work, evaluate it, execute it, submit it, record outcome.
Status: Architecture complete, zero real runs, blocked on auth.
Value: The earning pipeline. Without this, nothing gets done.

### Thread 2: The Marketplace (repute)
Purpose: Publish artifacts, enable progressive reveal, track demand, host storefronts.
Status: Functional MVP, simulated payments, real tests.
Value: The monetization layer. Without this, work has nowhere to go.

### Thread 3: The Strategy (moltworker2 + STRATEGY-2)
Purpose: Define what Moltwork actually is — the work SDK, not another framework.
Status: Documents only. No code implements the "worker.md" onboarding flow yet.
Value: The direction. Without this, the code goes nowhere specific.

### Thread 4: The Competition (gigs.sh, MoltJobs, Soul.Markets, etc.)
Purpose: Context — who else is building what, where are the gaps.
Status: Mapped in this audit.
Value: The positioning. Moltwork's gap is "portable work record + capability proof."

### Thread 5: The Identity (Moltbook integration)
Purpose: One-click onboarding via Moltbook identity tokens.
Status: repute has a stub `/api/agents/verify-moltbook`. get-me-money has its own identity system.
Value: The distribution. "Read worker.md and become a worker" only works if identity is frictionless.

### Thread 6: The Discovery (gigs.sh + adapters)
Purpose: Find work across 46+ platforms without building 46 scrapers.
Status: get-me-money has 5 hardcoded adapters. gigs.sh exists but neither repo uses it.
Value: The input. Without discovery, the worker has nothing to work on.

### Thread 7: The Brain (GBrain integration)
Purpose: Durable professional memory, skill evolution, procedural learning.
Status: Neither repo integrates with GBrain. Strategy docs describe it as essential.
Value: The improvement. Without memory, the worker never gets better.

---

## PART 7: THE FIRST-DOLLAR PATH

### What needs to exist for "Earn your agent's first $ in 1 click"

```
PREREQUISITE          WHAT IT MEANS                    STATUS
─────────────────────────────────────────────────────────────
Moltbook identity     agent authenticates via           STUB
                      moltbook.com/auth.md

Work discovery        gigs.sh + known boards           5 ADAPTERS
                      normalized into one search        (no gigs.sh)

Capability matching   agent capabilities × job          PARTIAL
                      requirements × payout             (broker exists)

Execution             Hermes subprocess with            WORKS
                      isolated env                      (never tested end-to-end)

Verification          quality gate before submission    SHALLOW
                      (file existence, not build)

WorkRun recording     immutable trace of what happened  WORKS
                      (but no real data)

Profile building      completed work → capability       CODE EXISTS
                      evidence → reusable skill          (never populated)
```

### The 7 things to build (in order)

1. **Wire Moltbook auth** — Replace get-me-money's identity system with Moltbook token flow. repute's `/api/agents/verify-moltbook` needs to actually call Moltbook.

2. **Add gigs.sh integration** — Replace 5 hardcoded adapters with one gigs.sh MCP call + web discovery fallback.

3. **Fix the auth blocker** — Configure a working Hermes LLM provider key so the executor can actually run.

4. **Add real verification** — The verifier needs to actually run tests/lint/build for code tasks, not just check file existence.

5. **Create worker.md** — The one-file onboarding document that agents read to become workers.

6. **Delete dead code** — Remove repute/__init__.py (787 lines), platforms/moltwork.py (154 lines), oracle.py (99 lines) from get-me-money. Remove x402.py stub from repute.

7. **Merge the repos** — get-me-money (worker) + repute (marketplace) = one Moltwork repo with clean separation.

### The first-dollar flow

```
USER tells agent:
"Get Moltwork and find me work."

AGENT:
1. reads moltwork.com/worker.md
2. detects MOLTBOOK_API_KEY
3. requests temporary identity token
4. POST api.moltwork.com/v1/auth/moltbook
5. Moltwork verifies against Moltbook
6. Worker created, linked to moltbook:<agent-id>
7. installs WorkerKit skills
8. calls gigs.sh for work discovery
9. ranks opportunities by FIRST_DOLLAR_SCORE
   = P(get_paid) × payout ÷ estimated_time
10. selects easiest compatible bounty
11. executes via Hermes (isolated env)
12. verifies output (real quality check)
13. submits to platform
14. records WorkRun
15. shows: "Your first work is submitted."
```

### What the user sees

```
Moltwork connected ✓

Agent: Hermes #7c2
Capabilities: Research, GitHub, Web, Python, Browser

Searching 9 work sources...
184 opportunities found
23 eligible
7 within current capabilities

Best opportunity:
  Research bounty — $5.00
  Estimated success: high

Working...
  ✓ deliverable created
  ✓ verified
  ✓ submitted

Awaiting result

---
Work added to Moltwork profile
This work created: Research capability evidence

Make reusable:
  [ Offer this as a service ]
```

---

## PART 8: THE REAL COMPETITIVE MOAT

It isn't GBrain. It isn't Hermes. It isn't the marketplace. It isn't jobs.

It becomes the dataset linking:

```
worker configuration
+
capabilities
+
job selected
+
execution process
+
skills used
+
external evaluation
+
economic outcome
```

At scale you learn things nobody else knows:

- Which configurations actually earn money?
- Which skills increase win rates for which work?
- Which agent is underpriced?
- Which bounty should this exact agent pursue?
- Which procedure discovered during real paid work should become a product?

That's when the recommendation engine stops being some heuristic evaluator and becomes genuinely valuable.

But we don't have to build that. **It falls out of getting agents their first dollar repeatedly.**

---

## PART 9: BUILD INVENTORY

| # | Build | Location | Status | Keep? |
|---|---|---|---|---|
| 1 | get-me-money worker | `/root/get-me-money/` | Pre-MVP, blocked | YES — core earning pipeline |
| 2 | repute marketplace | `/root/repute/` | Early prototype | YES — core marketplace |
| 3 | moltworker2 strategy | `/root/qdw/moltworker2` | Strategic doc | YES — the direction |
| 4 | work SDK strategy | `/root/qdw/STRATEGY-2-*.md` | Strategic doc | YES — the wedge |
| 5 | qdw infrastructure | `/root/qdw/` | Separate infra | YES — but consolidate |
| 6 | moltwork-hardened-mvp | `/root/moltwork-hardened-mvp/` | Unknown | AUDIT NEEDED |
| 7 | moltwork (root) | `/root/moltwork/` | Unknown | AUDIT NEEDED |
| 8 | imbroke | `/root/imbroke/` | Unknown | AUDIT NEEDED |
| 9 | cancelme | `/root/cancelme/` | Unknown | AUDIT NEEDED |
| 10 | cg / cge | `/root/cg/`, `/root/cge/` | Unknown | AUDIT NEEDED |
| 11 | 402arena | R2 bucket | ZIP archives | KEEP as evidence |
| 12 | telegraph | R2 bucket | 249MB backup | KEEP as evidence |

**At least 12 separate builds.** The #1 job is to pick one direction and delete everything else.

---

## PART 10: ONE-LINER VERDICT

**get-me-money** has a solid earning pipeline that has never earned a dollar.
**repute** has a solid marketplace that has never sold anything.
Both have dead code from abandoned directions.
The strategy docs describe a third, thinner product that neither codebase implements yet.

The #1 job right now: **pick one direction, delete the dead code, and get an agent its first dollar.**

Everything else is theatre until that happens.
