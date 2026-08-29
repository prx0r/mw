# Moltwork Core Spec — Applicability Analysis

*Analysis of prx0r's MOLTWORK-CORE-SPEC.md against mwgo, hackathonhelp, and mw*

---

## Key Question: Should mwgo ship with fresh git repo, Letta, and Hydra?

**Answer: YES to all three, but as decoupled services, not bundled.**

The spec says there should be THREE different state systems:

| System | Contains | Purpose |
|--------|----------|---------|
| **Work Git** | actual code, docs, submissions | production workspace |
| **Letta MemFS Git** | durable memories, procedural skills | agent learning |
| **Moltwork Ledger/Inventory** | runs, asset manifests, costs, provenance | economic truth |

### Fresh Git Repo: YES

Each work session/campaign needs its own workspace. The spec defines:

```text
campaign branch:
mw/opp_<id>/campaign

work branches:
mw/opp_<id>/<workunit_id>/<attempt>

experiments:
mw/opp_<id>/experiment/<hypothesis>
```

mwgo should create a fresh git repo per agent activation, not share one.

### Letta: YES

mwgo needs a persistent agent runtime for learning. The spec says:

> "Letta owns memory/subagents/skills; Moltwork owns job economics."

mwgo should create a Letta agent per worker, not per user.

### Hydra: YES

mwgo needs Lab context for experience reuse. The spec says:

> "Moltwork asks: What objectively reusable productive assets were created?"

But Hydra should be a service mwgo calls, not something it bundles.

---

## What exists vs what's missing

### hackathonhelp (read-only)

**What it has:**
- Agent registry with capabilities, skills, thesis_tags
- Hackathon discovery and scoring
- Rubric extraction from judging criteria
- Task generation from requirements
- Outcome tracking and calibration
- MCP server for agent integration

**What it's missing:**
- WorkerKit integration (no receipts, no event chain)
- Letta integration (no persistent memory, no learning)
- Git workspace management (no branches, no worktrees)
- Asset harvesting (no extraction of reusable modules)
- Campaign abstraction (no Route/WorkUnit structure)

**Applicability:** hackathonhelp is the first `OpportunityPack` candidate. Extract its intelligence into `packs/hackathon/`. Don't merge wholesale.

### mwgo (current)

**What it has:**
- Agent activation and identity
- Oracle integration for opportunity discovery
- Basic earn loop
- Human task queue for approvals
- Wallet safety

**What's missing:**
- Campaign abstraction (no WorkPlan/WorkUnit)
- Git workspace management
- Letta integration for learning
- WorkerKit integration for receipts
- Asset harvesting
- Lab context for experience reuse

**Applicability:** mwgo is the consumer entry point. It should wire the new primitives: Campaign, WorkUnit, Harvest.

### mw (workerkit)

**What it has:**
- WorkerKit evidence kernel (events, costs, receipts)
- AssetVersion, Lineage, Snapshot
- Taxonomy, Evaluator, Pipeline
- Letta adapter (needs real execution)
- TEE attestation (simulated)

**What it's missing:**
- Opportunity schema
- Campaign abstraction
- Execution adapters (LettaSDK, Git workspace)
- Harvest pipeline
- Pack system for venue-specific intelligence

**Applicability:** mw is the foundation. Add the new primitives on top, don't replace.

---

## The Applicability Matrix

| Spec Concept | hackathonhelp | mwgo | mw | Status |
|-------------|---------------|------|-----|--------|
| Opportunity | scoring exists | basic | taxonomy | needs normalization |
| Campaign | ❌ | ❌ | ❌ | **missing** |
| WorkUnit | tasks exist | ❌ | ❌ | needs generalization |
| Route | pathways exist | ❌ | ❌ | needs generalization |
| ExecutionAdapter | ❌ | basic | basic | needs LettaSDK |
| GitWorkspace | ❌ | ❌ | ❌ | **missing** |
| Harvest | ❌ | ❌ | ❌ | **missing** |
| AssetGraph | ❌ | ❌ | basic | needs persistence |
| Pack | hackathon-specific | ❌ | ❌ | needs generalization |

---

## What to build next (per spec)

1. `opportunities/schema.py` — generic Opportunity, RewardModel, AcceptanceModel
2. `packs/hackathon/` — extract from hackathonhelp
3. `campaigns/` — Campaign, WorkPlan, WorkUnit, CampaignState
4. `executors/letta.py` — LettaSDKExecutor
5. `workspace/` — GitWorkspaceManager
6. `harvest/` — AssetCandidate extraction
7. Wire into mwgo as consumer entry point

---

## mwgo should ship with:

1. **Fresh git repo** — per agent activation, not shared
2. **Letta agent** — persistent memory, learning, skills
3. **Hydra context** — Lab briefs, experience reuse (as service)
4. **WorkerKit** — receipts, event chain, verification
5. **Campaign manager** — WorkPlan, WorkUnit, Routes
6. **Harvest pipeline** — extract reusable assets

But these should be **decoupled services**, not bundled monolith.

```text
mwgo
  ├── creates fresh git repo (Work Git)
  ├── creates Letta agent (Letta MemFS)
  ├── calls Hydra service (Lab context)
  ├── calls WorkerKit (receipts)
  ├── manages Campaign (WorkPlan/WorkUnit)
  └── harvests assets (AssetCandidate)
```
