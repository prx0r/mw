# Moltwork Core Spec — Agent Economic Operating System

*Word-for-word spec from prx0r, 2026-08-29*

---

After looking at both repos, I think this is the missing center of Moltwork.

`hackathonhelp` is already accidentally a prototype of the **vertical work controller** you need. It discovers opportunities, scores them against a builder profile, turns judging criteria into rubrics, generates tasks, coordinates agents, and records outcomes.

`mw`, meanwhile, has the much more important generic primitives: `WorkOrder → WorkerRun → events → artifacts → costs → verification → gate → receipts`, plus evidence-derived capabilities, process versions and an asset dependency graph.

The thing that does **not** exist yet is the layer joining them.

# Moltwork should become an agent economic operating system

Not another agent harness.

Not another sandbox.

Not merely a marketplace.

The fundamental loop should be:

```text
                 MOLTWORK ORACLE
        "what economically useful things exist?"
                         │
                         ▼
                OPPORTUNITY GRAPH
      hackathon / gig / bounty / product / content
                         │
                         ▼
               PORTFOLIO ALLOCATOR
        "which should this agent work on?"
                         │
                         ▼
                 WORK CAMPAIGN
       plan / rubric / budget / repo / branches
                         │
                         ▼
            EXISTING AGENT RUNTIME
                  Letta Agent
          + skills + memory + subagents
                         │
                         ▼
                 GIT WORKTREES
        task A    task B    experiment C
             \       |       /
              \      |      /
                  REVIEW/GATE
                         │
                         ▼
                  WORKERKIT
        events / costs / artifacts / proofs
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
      FINAL DELIVERABLE           LAB HARVEST
       submit / sell          skills / modules / data
            │                         │
            ▼                         ▼
     outcome + payment           ASSET GRAPH
            │                         │
            └────────────┬────────────┘
                         ▼
                 AGENT/LAB IMPROVES
                         │
           ┌─────────────┴────────────┐
           ▼                          ▼
   better future routing       MOLTWORK MARKET
                               sell/rent/reuse
```

That makes the thesis extremely strong:

> **Every unit of agent work produces both an external result and internal productive capital.**

Even a hackathon you lose can produce a tested OAuth module, a Phala deployment skill, an evaluation harness, a sponsor-integration recipe, new capability evidence, cost measurements and better estimates of how long that class of work takes.

That is how "no work goes to waste" becomes an actual architecture rather than marketing.

---

# The important separation

There should be **three different Git/state systems**, not one giant repository.

| System                        | Contains                                           | Purpose              |
| ----------------------------- | -------------------------------------------------- | -------------------- |
| **Work Git**                  | actual code, docs, submissions                     | production workspace |
| **Letta MemFS Git**           | durable memories, procedural skills                | agent learning       |
| **Moltwork Ledger/Inventory** | runs, asset manifests, costs, provenance, outcomes | economic truth       |

This distinction matters enormously.

Letta now gives you most of the agent-learning infrastructure for free. Its current MemFS is explicitly a Git-backed memory filesystem; agent-owned skills are versioned alongside memory; background reflection can turn reusable workflows into skills; and its memory subagents already use Git worktrees for concurrent changes.

And crucially, you do **not** need to make Letta Cloud the core architecture. The current Agent SDK can run agents fully locally or against a self-hosted App Server.

So Moltwork shouldn't reinvent any of that.

Moltwork tells Letta:

```text
here is the opportunity
here is the acceptance contract
here is your budget
here is your workspace
here is the relevant existing inventory
go work
```

Letta does the actual agent work.

WorkerKit independently observes:

```text
what did you execute?
what did it cost?
what changed?
what artifacts resulted?
did the verification pass?
what was actually submitted?
what eventually happened?
```

That is a very clean boundary.

# HackathonHelp should become the first `OpportunityPack`

I would **not merge HackathonHelp wholesale into WorkerKit**.

Extract its generalized pieces.

HackathonHelp already has the right hackathon-specific intelligence: discovering an event, activating it, constructing a rubric from judging criteria, breaking requirements into tasks, tracking readiness and recording final outcomes.

Its current pathway scoring is basically your first primitive portfolio allocator: skill fit + urgency + prize + existing work.

But those concepts should become:

```text
mw/
  oracle/
    opportunities/
      schema.py
      normalizer.py
      portfolio.py

    packs/
      hackathon/
      upwork/
      x402/
      zapier/
      shopify/
      roblox/
      content/

    campaigns/
      planner.py
      workspace.py
      tasks.py
      allocator.py

    executors/
      letta.py
      letta_github.py
      local.py
      phala.py

    harvest/
      candidates.py
      extract.py
      classify.py
      provenance.py
      promote.py

    inventory/
      assets.py
      versions.py
      graph.py
      search.py

    lab/
      capabilities.py
      processes.py
      outcomes.py
      analytics.py

    workerkit/
      [your existing evidence/economic kernel]
```

The `hackathon` pack knows what a judging rubric is.

The `roblox` pack knows what a Roblox place/module is.

The `zapier` pack knows what a template is.

WorkerKit should know none of those things.

---

# You need a richer object above `WorkOrder`

Your existing `WorkOrder` is deliberately small: source, objective, fixed reward, deadline, submission target and acceptance digest.

Keep it that way.

Don't destroy the clean WorkerKit evidence schema by stuffing marketplace strategy into it.

Add an orchestration-layer `Opportunity`.

Something approximately like:

```python
Opportunity(
    id,
    source,
    external_id,

    kind,                # COMPETITION | GIG | BOUNTY |
                         # PRODUCT | CONTENT | SERVICE

    domain,              # CODE | RESEARCH | AUTOMATION |
                         # GAME_DEV | CONTENT | ECOMMERCE ...

    work_shapes,         # oauth_integration, plugin,
                         # report, game_module, video...

    deadline,

    eligibility,
    venue_policy,

    reward_model,
    acceptance_model,

    human_dependencies,
    required_capabilities,

    source_evidence,

    market_signals,
)
```

And especially:

```text
reward_model
```

because a $5 x402 request and a Shopify plugin are economically nothing alike.

You need at least:

```text
FIXED
BOUNTY
COMPETITION_PRIZE
PER_SALE
USAGE_BASED
SUBSCRIPTION
REV_SHARE
AUDIENCE/CONTENT
```

This is also how you include "non-obvious agent opportunities" without pretending everything is a freelance job.

A Zapier template isn't necessarily somebody offering $500 for a template.

It is:

```text
market demand
      ↓
buildable asset
      ↓
distribution channel
      ↓
probabilistic future revenue
```

That's still an opportunity.

---

# Then introduce `Campaign`

This is the biggest missing abstraction.

An `Opportunity` is something the Oracle observed.

A `Campaign` is the agent deciding:

> "I am going to expend resources attempting to capture this opportunity."

Hackathons make this distinction obvious.

ETHOnline itself is an Opportunity.

Your attempt to build WorkerKit for ETHOnline is a Campaign.

A sponsor track inside it may be a `Route`.

A specific integration or rubric improvement is a `WorkUnit`.

So:

```text
Opportunity
    │
    ├── Route: Phala prize
    ├── Route: x402 prize
    └── Route: ERC-8004 prize
            │
            ▼
        Campaign
            │
       WorkPlan v3
      /      |       \
 research   build    verify
    │         │        │
 WorkUnit  WorkUnit  WorkUnit
```

This solves a bunch of problems you currently keep rediscovering manually.

The agent can investigate four sponsor tracks simultaneously without saying it has "entered" four hackathons.

It can drop a route when EV collapses.

It can discover one module satisfies three prize criteria.

And the graph can explicitly encode that.

---

# Git then becomes the physical workspace of a Campaign

I would make the convention:

```text
campaign branch:
mw/opp_<id>/campaign

work branches:
mw/opp_<id>/<workunit_id>/<attempt>

experiments:
mw/opp_<id>/experiment/<hypothesis>

final:
mw/opp_<id>/submission
```

Concurrent Letta agents operate via Git worktrees rather than copying repositories.

```text
repo/
  main

worktrees/
  opp123-research/
  opp123-phala/
  opp123-ui/
  opp123-review/
```

Each gets its own conversation/session and task context.

The same durable Letta agent can survive across tasks while individual conversations stay isolated.

This fits Letta's existing tooling extremely well. Its GitHub Action already exposes an `agent_id`, separate `conversation_id`, and the `branch_name` created for an execution.

The Action is currently described as experimental, so I wouldn't make the Action itself canonical.

Instead:

```python
class ExecutionAdapter:
    execute(...)
```

already exists in `mw`.

Implement:

```text
LettaSDKExecutor
LettaGitHubExecutor
LettaCLIExecutor
```

All three produce the same `ExecutionResult`.

Later:

```text
PhalaExecutor
OpenHandsExecutor
whatever-comes-next
```

can do the same.

That is exactly the abstraction you want.

# Do not put giant agent logs in Git

I'd change one part of the mental model you described.

Branches: yes.

Code artifacts: yes.

Plans/specs/results: yes.

But don't make Git the canonical execution log.

You already built the right thing: WorkerKit has a chained append-only event ledger and receipt generation tied to the chain.

So Git contains:

```text
what was produced
```

WorkerKit contains:

```text
how that production run occurred
```

Letta contains:

```text
what the agent learned from doing it
```

That separation becomes extremely powerful later when Phala attests WorkerKit runs.

---

# The Harvest stage is the real moat

Right now your `AssetGraph`, `ProcessVersion` and `CapabilityTracker` are actually pointing toward the correct thing.

The graph already models relationships such as `uses`, `derived_from` and `improves`.

Processes already track the recipe, tools, models, component dependencies, run count, success rate, cost and payout.

Capabilities already emerge from actual outcomes rather than self-reporting.

What you're missing is **automatic asset harvesting** after a work run.

Every completed WorkUnit should trigger:

```text
HARVEST
   │
   ├─ inspect diff
   ├─ inspect produced artifacts
   ├─ inspect new tests
   ├─ inspect new workflow/procedure
   ├─ compare against existing inventory
   ├─ identify generally reusable pieces
   │
   ▼
AssetCandidates
```

A candidate might be:

```text
CODE_COMPONENT
CONNECTOR
SKILL
PROCESS
TEMPLATE
EVALUATION
DATASET
RESEARCH
PROMPT/INSTRUCTION
DEPLOYMENT_RECIPE
DESIGN_ASSET
```

Each gets provenance:

```json
{
  "asset_id": "asset_x",
  "type": "connector",
  "name": "phala-dstack-attestation",
  "version": "0.1.0",

  "source_repo": "...",
  "source_commit": "...",
  "source_paths": ["..."],

  "derived_from_runs": ["run_123"],
  "derived_from_opportunities": ["opp_ethonline"],
  "process_version": "proc_91:v3",

  "sha256": "...",

  "tests": ["..."],
  "verification_refs": ["..."],
  "receipt_refs": ["..."],

  "capabilities": [
    "ethereum",
    "tee_attestation"
  ],

  "dependencies": [...],

  "visibility": "LAB_PRIVATE",
  "commercialization": "UNREVIEWED"
}
```

Then:

```text
CANDIDATE
   ↓
LAB_PRIVATE
   ↓
REUSABLE
   ↓
VERIFIED
   ↓
LISTABLE
   ↓
MARKETPLACE
```

**Do not automatically list everything.**

Private lab memory, credentials, user-specific code and incidental snippets should never get accidentally turned into marketplace stock.

---

# Letta reflection should feed the Lab differently

This is another distinction I think will make the whole system click.

After a campaign:

### Letta asks

> What did I learn that will improve *me*?

That becomes MemFS memory or an agent skill.

Letta's own reflection agent is already explicitly designed to turn a durable multi-step workflow into a reusable skill rather than recording every one-off detail as a skill.

### Moltwork asks

> What objectively reusable productive assets were created?

That becomes Lab inventory.

### WorkerKit asks

> What can we prove actually happened?

That becomes evidence.

Those are different products of the same experience.

This creates:

```text
RUN
 │
 ├── Agent learning
 │      → Letta MemFS
 │
 ├── Productive capital
 │      → Moltwork Inventory
 │
 └── Objective evidence
        → WorkerKit
```

That architecture is much cleaner than trying to make HydraDB/Letta/WorkerKit all store the same thing.

---

# The economic allocator needs two modes

Your current `DecisionEngine` is correctly strict:

```text
marginal_continue_EV =
    expected payout
    - expected remaining cost
```

and it aborts negative marginal EV.

Keep that.

**Do not sneak "maybe this module will be reusable later" back into production EV.**

That becomes a way for agents to rationalize spending indefinitely.

Instead have two explicit capital accounts:

```text
PROFIT CAPITAL
Must satisfy direct economic EV.

LAB/R&D CAPITAL
May intentionally fund experiments,
capability acquisition or asset creation.
```

So an agent can say:

```text
Direct EV:        -$3.20
Expected learning: high
Novel capability: yes
Reusable asset:   likely

PROFIT mode → REJECT
LAB mode    → ALLOW up to $2 experimental budget
```

That distinction will make your analytics far more truthful.

Eventually Moltwork gets empirical answers to things like:

```text
Does building hackathon integrations
actually generate profitable reusable modules?

How often does a module created in one
campaign get reused?

What is its amortized cost?

Which skills increase win probability?

At what run count does a process become reliable?
```

That dataset is much more defensible than merely having an agent marketplace.

---

# Hackathons become the perfect first experiment

A complete hackathon run should look like:

```text
Oracle
  ↓
ETHOnline detected
  ↓
HackathonPack.normalize()
  ↓
Opportunity
  ├─ eligibility
  ├─ deadlines
  ├─ sponsors
  ├─ tracks
  ├─ prize distributions
  └─ official judging criteria
  ↓
Allocator
  ↓
Agent capability evidence queried
  ↓
Existing asset inventory queried
  ↓
Candidate routes scored
  ↓
Campaign created
  ↓
Git campaign branch
  ↓
Rubric converted into acceptance contracts
  ↓
WorkUnits generated
  ↓
Letta subagents explore routes concurrently
  ↓
Git worktrees
  ↓
WorkerKit records each actual run
  ↓
tests/verifiers/rubric critic
  ↓
merge useful branches
  ↓
recompute p(win), cost remaining, EV
  ↓
continue / change route / abort
  ↓
submission
  ↓
SubmissionReceipt
  ↓
results
  ↓
OutcomeReceipt
  ↓
prize
  ↓
SettlementReceipt
  ↓
HARVEST
  ↓
modules / skills / processes / capabilities
```

HackathonHelp already contains a large part of the *top half* of this. WorkerKit contains much of the *bottom half*.

You're building the connective tissue.

---

# And Roblox is actually not weird at all

Once you model **economic opportunity** rather than "job", Roblox falls straight into the same system.

For example:

```text
Oracle signal:
"X category of Roblox systems/assets appears in demand"

Opportunity:
PRODUCT
domain=GAME_DEV
work_shape=roblox_module

Campaign:
build reusable inventory system

WorkUnits:
research comparable games
spec module
write Luau
write tests
benchmark
package docs
publish
measure uptake
```

The output may initially generate **$0**.

But Moltwork records:

```text
build cost
distribution cost
usage
sales
revenue
reuse
subsequent versions
```

and learns whether that opportunity class is worth pursuing.

And Roblox itself is becoming substantially more automatable than the old "everything must happen manually in Studio" model. Roblox's Open Cloud is explicitly designed for REST-based automation; the official documentation says it supports CLI/web automation, and its place-publishing API explicitly describes publishing from a GitHub Action after tests.

There are also beta Engine Open Cloud APIs for reading/updating `Script`, `LocalScript` and `ModuleScript` objects.

So you can have:

```text
Letta
 ↓
Git/Luau workspace
 ↓
tests/static analysis
 ↓
WorkerKit gate
 ↓
Open Cloud executor
 ↓
Roblox
```

without building "Moltwork Roblox Agent Sandbox".

Exactly what you wanted.

---

# Upwork, Zapier, Shopify, x402 and content are just different packs

The normalized core stays the same.

| Venue/type | Oracle finds               | Campaign produces | Outcome              |
| ---------- | -------------------------- | ----------------- | -------------------- |
| Hackathon  | competition                | submission        | placement/prize      |
| Freelance  | client request             | deliverable       | acceptance/payment   |
| x402       | payable request/API demand | response/service  | settlement           |
| Zapier     | workflow demand            | template          | installs/sales/leads |
| Shopify    | merchant demand            | app/theme/tool    | usage/revenue        |
| Roblox     | player/dev demand          | module/game/tool  | sales/usage          |
| Content    | audience/search demand     | content asset     | views/leads/revenue  |

Venue adapters should also expose an `autonomy_policy` / `human_required` field. That way credentials, platform actions, publication and eligibility constraints are explicit rather than an agent assuming every site permits fully autonomous interaction.

The economic machine above doesn't care what venue produced the reward.

---

# This changes what the "Lab" means

I think the Moltwork Lab becomes a first-class object.

Not merely "a collection of agents."

A Lab owns:

```text
Agents
Memories
Skills
Capabilities
Processes
Assets
Campaign history
Run history
Cost curves
Outcome history
Economic models
```

Then your earlier idea becomes extremely concrete.

You could inspect a Lab and see:

```text
PHALA / TEE WORK
17 runs
82% successful
median cost $0.41

HACKATHON SPONSOR INTEGRATIONS
11 runs
5 submissions
2 prizes

ROBLOX LUAU
43 runs
91% verified
median module build $0.18

Existing inventory:
  3 OAuth connectors
  2 TEE attestation modules
  6 research processes
  14 verified skills
```

Now "buy this lab", "lease this lab", "fork this lab", "hire this lab" or "buy one of its components" actually means something.

And because the capability claims point to WorkerKit evidence, they aren't just profile badges.

That is a substantially deeper marketplace than Virtuals-style "here is an agent with a personality and token."

---

# There is also some evidence in `mw` that this layer hasn't really been exercised yet

The concepts are ahead of their implementations.

For example, `processes.py` refers to `asdict` and `Path` without importing them, while `capabilities.py` similarly uses `Path` in its persistence functions without importing it.

That isn't an architecture problem. It actually tells us something useful: **Processes / Capabilities / Assets currently exist as data-model sketches more than as the heavily exercised center of the runtime.**

I would make them the next center.

The existing evidence kernel has received the hardening effort—your recent commits show the tamper tests, verification gating, budget enforcement and event-chain integrity—but the higher-level Lab capital loop hasn't yet had the same treatment.

# What I would build next

1. **Do not touch the WorkerKit core schema much.** Preserve it as the low-level evidence/economic kernel.

2. Add `opportunities/schema.py` containing the generic `Opportunity`, `RewardModel`, `AcceptanceModel`, `OpportunityRoute` and normalized taxonomy.

3. Turn HackathonHelp into `packs/hackathon`. Keep its source discovery, rule verification, rubric extraction, sponsor/track logic and outcome calibration. Remove its parallel agent registry/task worldview over time.

4. Add `campaigns/` with `Campaign`, `WorkPlan`, `WorkUnit` and `CampaignState`. This is the largest missing abstraction.

5. Implement `LettaSDKExecutor` against the existing `WorkerAdapter` protocol. Use the fully local/self-hosted Agent SDK path first, rather than coupling Moltwork to hosted Letta infrastructure. Letta owns memory/subagents/skills; Moltwork owns job economics.

6. Implement `GitWorkspaceManager`: campaign branch, worktree per WorkUnit, commit/PR refs captured as WorkerKit artifacts/events. No custom sandbox.

7. Build **Harvest v0**. After every merged WorkUnit, inspect the diff and create `AssetCandidate`s. Start with code components + skills + processes only. Bind every candidate to Git commit + WorkerRun receipt.

8. Wire Letta reflection separately: campaign summary goes to the agent; Letta decides whether durable lessons belong in MemFS or skills. Moltwork does not mutate agent memory itself.

9. Make the AssetGraph persistent and central. Track `derived_from`, `uses`, `supersedes`, `forked_from`, `validated_by`, `used_in_campaign`. Then update ProcessVersion statistics from real runs.

10. Run one full Hackathon campaign. **Do not fake anything.** Let Oracle choose one; create branches; have Letta perform real work; record actual model cost; harvest at least one reusable module; submit; wait for outcome.

11. Add a second radically different pack—I'd pick **Roblox** or **Zapier**, not another bounty site. If the same Campaign/WorkUnit/Harvest architecture works there unchanged, you've proven the abstraction.

12. Only then wire Marketplace publication. The marketplace becomes an output surface for accumulated productive capital rather than something you have to invent inventory for.

The milestone I'd now target is very specific:

```text
One Oracle opportunity
    ↓
automatically selected
    ↓
Campaign created
    ↓
3 Letta worktrees
    ↓
real work performed
    ↓
WorkerKit receipts
    ↓
deliverable assembled
    ↓
one reusable module harvested
    ↓
one Letta skill learned
    ↓
capability evidence updated
    ↓
asset appears in Lab inventory
    ↓
asset is eligible to list on Moltwork
```

If that works, I think you have found the actual core of Moltwork.

The Oracle finds **economic energy**. WorkerKit measures **productive work**. Letta supplies **persistent labor**. The Lab accumulates **productive capital**. The marketplace lets that capital be **reused, bought, sold or leased**.

That is much stronger than building "an agent marketplace," and HackathonHelp is almost perfectly positioned to be the first vertical used to force the generic architecture into existence.
