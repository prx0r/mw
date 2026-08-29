Yes. I think the architecture has now converged enough that I would **deliberately narrow the build**.

For v0/v1, I would build Moltwork around exactly three things:

> **Letta = the worker**
> **HydraDB = the lab brain**
> **`cg` = the scientist that decides whether the worker actually improved**

Everything else becomes optional integration later.

And that changes what Moltwork is. It is no longer merely an oracle with a worker attached, but I still would **not** describe it as another generic agent framework. The interesting primitive is a **learning lab**: persistent workers whose behavior is changed only when empirical evidence shows that the change improves real work.

## The architecture I would lock

```text
                         MOLTWORK LAB
                private to one user/company
                           │
       ┌───────────────────┼────────────────────┐
       │                   │                    │
       ▼                   ▼                    ▼

    LETTA                HYDRADB                CG
  WORKERS              LAB BRAIN           SCIENTIST
     │                    │                    │
identity              jobs/runs            experiments
memory                outcomes             evaluation
skills                workers              mutation
mods                  skills               replay
history               models               selection
context               costs                attribution
     │                    │                    │
     └──────────────┬─────┴────────────┬───────┘
                    │                  │
                    ▼                  ▼
               WORK EXECUTION      LEARNING
                    │                  │
                    ▼                  │
                 OUTCOME ──────────────┘
                    │
                    ▼
               LAB GETS BETTER
```

That is substantially more coherent than assembling OpenClaw + Hermes + GBrain + Letta + five other things.

Letta itself has now explicitly committed to being a **memory-first, model-agnostic agent harness** with computer use, subagents, skills and self-improvement; they've moved away from several of their older server-side abstractions to focus on this architecture. ([Letta][1])

So yes: **use Letta rather than reproducing Letta.**

---

# 1. What HydraDB should mean by a user's “Lab”

This distinction is crucial:

**Letta remembers as an individual worker.**

**Hydra remembers as an organization.**

Say someone has:

```text
Tom's Lab

Researcher
Coder
IT Worker
Sales Worker
Reviewer
```

I would create **one Lab graph**, not five separate graphs.

Conceptually:

```text
Lab: lab_tom
│
├── Worker: researcher-01
├── Worker: coder-01
├── Worker: it-01
├── Worker: sales-01
└── Worker: reviewer-01

and

Opportunities
Runs
Submissions
Models
Skills
MemoryVersions
Evaluations
Outcomes
Clients
TaskFamilies
Insights
Experiments
```

Every worker contributes experience into the same empirical graph.

That's how organizational intelligence emerges.

### Hydra actually maps naturally onto this

Its hosted system has hierarchical tenancy:

```text
tenant_id
    = organization/lab

sub_tenant_id
    = isolated project/client/team
```

and the default subtenant acts as organization-wide storage. Importantly, Hydra says cross-subtenant querying is deliberately restricted, so **I would not make every agent a subtenant**. You'd lose the very cross-worker learning we want. ([HydraDB SDK][2])

Instead:

```text
tenant = moltwork_lab_123

DEFAULT
    shared lab intelligence

client_acme
    private client knowledge

project_secret_x
    isolated project context
```

Workers themselves are graph entities inside the shared Lab.

With the OSS database rather than Hydra's hosted API, the equivalent can be represented using graph namespaces/scopes.

---

# 2. There are actually two HydraDBs to think about

This was the biggest clarification from digging deeper.

### HydraDB OSS

`hydra-db/hydradb` is a real distributed graph database written in Rust. It stores canonical graph records on SlateDB/object storage, supports OpenCypher/Bolt/HTTP, snapshot-consistent reads, immutable graph indexes plus WAL overlays, and GraphBLAS-accelerated graph traversal. Its compute/cache nodes are disposable while durable state sits on S3-compatible object storage.

This is the thing `cg` is talking to.

It is your:

> **structured empirical graph engine.**

### Hydra hosted memory system

Their higher-level product adds:

* memory ingestion
* automatic entity extraction
* graph enrichment
* semantic search
* keyword search
* graph retrieval
* metadata filters
* multi-tenancy
* graph-enriched context returned to agents

all behind a much simpler memory API. ([HydraDB SDK][3])

That is more like:

> **agent/company memory as a product.**

I would **not make the hosted automatic-memory layer foundational to Moltwork**.

Use the graph explicitly for important facts.

For example:

```text
Run 927
cost = $0.183
reward = $50
submission_score = .87
worker = researcher-03
model = GLM-5.3-Flash
outcome = WON
```

Do **not** feed a paragraph saying this happened to an LLM and hope it infers the right graph.

Write it deterministically.

But something fuzzy such as:

> “The client seems to prefer concise, evidence-heavy reports.”

can go through an inference/memory layer with:

```text
confidence=.71
source_runs=[...]
provenance=[...]
```

So I would actually make two logical parts of the graph:

```text
                 LAB GRAPH

        VERIFIED / EMPIRICAL
        ────────────────────
        Run
        Cost
        Submission
        Outcome
        Payout
        Evaluation
        Model
        Worker Version

                 +

        INFERRED / EPISTEMIC
        ────────────────────
        Insight
        Hypothesis
        Pattern
        Preference
        Suggested Strategy
```

That's a very powerful separation.

---

# 3. `cg` already has the right philosophy

This is where your existing work suddenly becomes extremely useful.

Your current `cg` README already defines it as a **deterministic agentic evolution laboratory** where worlds are replayable, runs are content-addressed proofs, quality gates are constraints and an experience graph records what happened.

And the existing spec already includes:

* hard quality gates
* dev / validation / secret evaluation suites
* Wilson/bootstrap statistics
* typed mutation spaces
* 33 reasoning styles
* MAP-Elites / quality-diversity
* model-response caching
* replay
* counterfactual forks
* `evolve.step(objective, budget)`
* CapabilityClaims
* Hydra experience storage

among other pieces.

You basically accidentally built the **scientific method component Moltwork now needs**.

Even better, the design already says Hydra should be a **derived experience store**, while local receipts/findings remain canonical and Hydra can be completely rebuilt.

I would preserve that exact principle.

## Never make Hydra your sole source of truth

Use:

```text
Canonical event ledger
        │
        │ immutable
        ▼
RunReceipt / Events / Outcomes
        │
        ├──────► Hydra projection
        │
        ├──────► Analytics
        │
        └──────► cg experiments
```

If Hydra disappears:

```text
replay events
→ reconstruct graph
```

That's excellent architecture.

It also insulates Moltwork from Hydra being relatively young. The current OSS repository is still early-stage enough that I would treat it as an advanced engine rather than the irreplaceable ledger beneath your company. ([GitHub][4])

---

# 4. Letta and Hydra should NOT compete over “memory”

At first this looks duplicative:

> Letta has memory.

> Hydra has memory.

But they should serve different purposes.

### Letta memory asks:

> “What does **this worker** need inside its cognition to perform well?”

### Hydra asks:

> “What does **this lab know** from everything that has happened?”

That's a huge difference.

The clean hierarchy is:

```text
CURRENT JOB
─────────────────────────────
Letta context / conversation
temporary files

WORKER MEMORY
─────────────────────────────
Letta MemFS
core identity
personal lessons
skills
mods
worker-specific history

PROJECT KNOWLEDGE
─────────────────────────────
Hydra scoped project data
documents
client state
historical work

LAB INTELLIGENCE
─────────────────────────────
Hydra Lab graph
all workers
all runs
all outcomes
all experiments

GLOBAL INTELLIGENCE
─────────────────────────────
Moltwork Oracle
market data
opportunities
platform statistics
```

That solves the memory confusion.

---

# 5. Letta's MemFS is where this gets really interesting

Their 2026 Context Repositories work is substantially more advanced than simple vector memory.

The agent's durable context is represented as a **Git-backed filesystem**. It can progressively expose context, rewrite files itself, launch memory subagents working in separate Git worktrees, periodically reflect on history in the background, and run a defragmentation process that reorganizes accumulated memory. Every memory change gets versioned in Git. ([Letta][5])

That gives you:

```text
worker/researcher-03/memory/

system/
    identity.md
    principles.md

knowledge/
    research-methods.md
    source-quality.md

lessons/
    hackathons.md
    api-research.md

clients/
    ...

strategies/
    ...

failures/
    ...
```

But the really important property is:

```text
commit a17df4
→ worker believed X

commit b8192a
→ worker learned Y

commit c30199
→ procedure changed Z
```

Now combine that with Moltwork outcomes.

Suddenly we can ask:

> **Did memory commit `b8192a` actually make the worker better?**

That is much more interesting than ordinary agent memory.

---

# 6. Moltwork can perform memory attribution

Suppose a Letta worker learns:

> Always make an explicit requirements checklist before preparing a submission.

Letta writes that into memory.

Git gives:

```text
memory_commit = 23af71
```

Hydra records:

```text
(WorkerVersion)-[:HAS_MEMORY]->(MemoryCommit:23af71)

MemoryCommit
  ├─ introduced_at
  ├─ parent_commit
  ├─ changed_files
  └─ candidate_lesson
```

Future runs link against it:

```text
Run 100 → USED_MEMORY → 23af71
Run 101 → USED_MEMORY → 23af71
Run 102 → USED_MEMORY → 23af71
```

`cg` can compare them with suitably matched previous runs.

Eventually:

```text
MEMORY CHANGE 23af71

before
quality       .72
pass rate     63%
cost          $0.31

after
quality       .84
pass rate     78%
cost          $0.34

n = 47
confidence = ...
```

Now:

> **memory itself becomes an experimentally evaluated component.**

That is one of the strongest things you could build here.

---

# 7. This is better than unrestricted self-improvement

I would **not** do:

```text
job fails
→ agent reflects
→ agent changes itself permanently
```

That's how you accumulate nonsense and superstition.

Instead:

```text
                         EXPERIENCE
                              │
                              ▼
                     candidate lesson
                              │
                ┌─────────────┼──────────────┐
                │             │              │
              memory         skill          mod
              change         change        change
                │             │              │
                └─────────────┼──────────────┘
                              ▼
                           CG LAB
                              │
                       replay old work
                              │
                       hidden examples
                              │
                     counterfactual tests
                              │
                    ┌─────────┴─────────┐
                    │                   │
                IMPROVES            REGRESSES
                    │                   │
                 merge                 kill
                    │
                    ▼
              LETTA WORKER
```

Letta **proposes learning**.

`cg` **decides whether learning survives**.

Hydra **remembers the evidence**.

That is the loop.

---

# 8. Your submission idea is exactly where I would begin

Don't start by evolving an entire agent.

That's much too large a search space.

Treat the **submission as phenotype**.

A job arrives:

```text
task
 ↓

Letta creates:
 A
 B
 C
 D

 ↓

cg evaluates:
 requirements
 correctness
 evidence
 completeness
 rubric alignment
 presentation
 novelty
 cost
 other task-specific properties

 ↓

Reviewer critiques

 ↓

repair candidates

 ↓

select submission
```

You already have hard gates + lexicographic/multiobjective selection machinery in `cg`, which is much safer than reducing everything to one “quality = 8.72” number.

Then after enough jobs, start asking:

> **Which processes tend to produce the winning submission?**

That's where evolution moves upstream.

---

# 9. What eventually becomes optimizable

Initially:

```text
SUBMISSION
```

Then:

```text
SUBMISSION
+
PLAN
```

Then:

```text
SUBMISSION
+
PLAN
+
SKILLS USED
+
MEMORY CONTEXT
```

Eventually the candidate genome becomes:

```text
WorkerStrategy {
    planning_policy
    context_pack
    memory_version
    skills[]
    mods[]
    model_route
    tool_route
    research_depth
    candidate_count
    reviewer_policy
    repair_policy
    stopping_rule
}
```

And the result is:

```text
WorkerStrategy
       │
       ▼
  Submission
       │
       ▼
   Evaluation
       │
       ▼
 real-world Outcome
```

Now you're doing **empirical process optimization**.

Not prompt tweaking.

---

# 10. There are three learning loops, not one

This is how I'd structure it.

```text
LOOP A — WITHIN ONE JOB

task
→ generate variants
→ evaluate
→ repair
→ submit best

minutes


LOOP B — WORKER LEARNING

many jobs
→ examine successes/failures
→ propose memory/skill/mod changes
→ replay/test changes
→ promote validated changes

days/weeks


LOOP C — LAB LEARNING

all workers
→ identify cross-worker patterns
→ model job economics
→ improve opportunity scoring
→ discover task-family strategies
→ create better templates
→ seed new workers

weeks/months
```

This is where the “Lab” concept becomes much bigger than agent memory.

---

# 11. Hydra gives you relational questions that Letta shouldn't answer

For example:

```text
Which worker has best ROI
on API-integration bounties?

Which skills correlate
with winning frontend jobs?

Does GLM outperform MiMo
when the requirements exceed 10 items?

Which markets are becoming
less profitable for our lab?

Which memory changes
caused regressions?

Which reviewer policy
best predicts actual payout?

Which task families have
high quality but low win rate?

Which worker systematically
underestimates cost?
```

Those are **analytics over experience**.

They don't belong in a prompt.

Hydra is a much more natural representation.

---

# 12. Hydra's graph itself can become extremely rich

I'd use a schema broadly along these lines:

```text
Lab
 │
 ├── HAS_WORKER ─────► Worker
 │                       │
 │                       ├── VERSION ─────► WorkerVersion
 │                       ├── LEARNED ─────► SkillVersion
 │                       └── MEMORY ──────► MemoryRevision
 │
 ├── OBSERVED ────────► Opportunity
 │                       │
 │                       └── FAMILY ──────► TaskFamily
 │
 ├── EXECUTED ────────► Run
 │                       │
 │                       ├── MODEL ───────► Model
 │                       ├── USED ────────► Skill
 │                       ├── PRODUCED ────► Submission
 │                       ├── COST ────────► Cost
 │                       └── OUTCOME ─────► Outcome
 │
 └── TESTED ──────────► Experiment
                         │
                         ├── HYPOTHESIS
                         ├── VARIANT
                         └── FINDING
```

Then layer explicit relationships like:

```text
MUTATED_FROM
IMPROVED_ON
REGRESSED_ON
SIMILAR_TO
DERIVED_FROM
VALIDATED_BY
PROMOTED_TO
INHERITED_FROM
CORRECTS
CONTRADICTS
```

This is where graph memory genuinely makes sense rather than being used because graphs sound cool.

---

# 13. Hydra has some unusually good advanced primitives for this

The raw database architecture's **pinned snapshots** are useful for reproducible analytics: one query sees one internally consistent graph state. Its object-store architecture also separates durable graph state from disposable compute/index caches.

The hosted layer adds hybrid retrieval across semantic, keyword, graph and metadata signals. ([HydraDB SDK][6])

Its MCP integration can also return **graph-enriched context**, not merely vector matches, and can automatically perform knowledge-graph extraction for unstructured material. ([HydraDB SDK][3])

And their larger architectural bet is append-only/temporal agent state rather than destructive “current memory only” storage. That's their own product framing, so I'd treat the exact implementation/performance claims as vendor claims, but the underlying principle is exactly right for us. ([HydraDB][7])

---

# 14. However, do not dump Hydra directly into every Letta prompt

We need a **context broker**.

Imagine a $75 API research job arrives.

The worker asks:

```text
lab.prepare_context(
    worker=researcher-03,
    task=job,
    budget_tokens=6000
)
```

The broker queries Hydra:

```text
similar successful runs
relevant failures
best known skill
model economics
task-family priors
lab warnings
client context
```

and returns something compact:

```text
LAB BRIEF

Task family:
  API research

Similar lab runs:
  37

Historical success:
  62%

Strongest procedure:
  api-research-v7

Useful observations:
  - first-party documentation improves evaluator score
  - >3 Reddit sources correlates with lower factual score
  - GLM gives higher quality; MiMo higher ROI under $40

Failure warning:
  4 prior submissions omitted pricing evidence

Recommended skill:
  api-research-v7

Confidence:
  medium/high
```

That's what Letta sees.

Not 37 full trajectories.

This is **progressive disclosure across organizational memory**.

It lines up beautifully with Letta's own context-repository philosophy of retaining lots of memory while exposing only what is currently useful. ([Letta][5])

---

# 15. Then the worker contributes back

At the end:

```text
Letta
 ↓
personal reflection

Moltwork
 ↓
raw events + outcome

Hydra
 ↓
structured experience

cg
 ↓
tests proposed lessons

validated worker learning
 ↓
Letta MemFS / skill / mod

validated cross-worker learning
 ↓
Lab Insight
```

So you get bidirectional intelligence:

```text
                 HYDRA LAB
                 ↑       ↓
          experience   priors
                 ↑       ↓
             LETTA WORKERS
                 ↑       ↓
          adaptation   work
                 ↑       ↓
                    CG
             tests changes
```

That's the engine.

---

# 16. New agents become much more interesting

Suppose you've run an IT Lab for two years.

Your Lab has accumulated:

```text
13,482 work runs
1,093 clients/jobs
72 promoted skills
214 rejected hypotheses
31,000 evaluations
model-cost history
vendor patterns
failure patterns
job-selection models
```

You spawn:

```text
it-worker-27
```

It doesn't need to start dumb.

But don't clone all of worker-03's messy personal memory.

Instead:

```text
LAB
 │
 ├── distilled operating principles
 ├── best IT skills
 ├── high-confidence failure warnings
 ├── task-family priors
 ├── model-routing knowledge
 └── opportunity scoring knowledge
       │
       ▼
     TEMPLATE
       │
       ▼
   NEW LETTA AGENT
       │
       ▼
new private personal experience
```

That is much closer to **organizational culture / training**.

---

# 17. And yes, lineage belongs in the marketplace

You had the right intuition about parent reputation, but keep the scores separate.

A spawned agent could show:

```text
Worker
IT-27

Personal verified runs
12

Personal success rate
83%

Template
Acme IT Worker v8

Template evidence
3,819 historical runs

Lab
Acme Agent Lab

Lab verified work
14,921 runs

Inherited capabilities
M365
Xero
Networking
Helpdesk

Parent
IT-03 v41
```

But it should **not inherit IT-03's 98% personal reputation**.

Instead the marketplace can calculate:

```text
personal evidence       high weight as it grows
template prior          declining weight
lab prior               declining weight
lineage evidence        context
```

This gives new agents a sensible prior without reputation laundering.

---

# 18. This creates a “lab moat” automatically

Two users can see identical Oracle data:

```text
Moltwork Oracle:
job X
$120
API integration
deadline 4h
```

Lab A sees:

```text
general opportunity score
0.73
```

Your Lab might calculate:

```text
private EV score
0.96

because:

researcher-03 has won 7/8 similar
client has paid twice before
api-research-v9 is a strong fit
GLM cost estimate $0.42
submission expected 38 minutes
competition historically low at this hour
```

That transformation is **not public Moltwork intelligence anymore**.

It's the accumulated private intelligence of the Lab.

That's much more defensible than a generic agent harness.

---

# 19. `cg` should optimize those private transformations too

Eventually `cg` can test:

```text
job scoring formula A
vs
job scoring formula B

worker assignment rule A
vs B

GLM escalation threshold .6
vs .8

3 candidate submissions
vs 5

review once
vs adversarial review

memory pack A
vs memory pack B
```

Then evaluate:

```text
quality
cash cost
latency
win probability
actual payout
human intervention
```

The Lab can evolve not only agents but **operating policy**.

That's organizational learning.

---

# 20. MAP-Elites is particularly useful here

You already specced quality-diversity into `cg`.

I would retain it.

You do **not** necessarily want:

> one globally best worker strategy.

Different strategies dominate under different constraints.

Imagine the archive:

```text
                   COST

           cheap     medium      high
         ┌────────┬──────────┬──────────┐
research │ MiMo   │ GLM      │ deep     │
         │ fast   │ +review  │ research │
         ├────────┼──────────┼──────────┤
coding   │ MiMo   │ GLM      │ premium  │
         │ patch  │ iterate  │ multi-ag │
         ├────────┼──────────┼──────────┤
design   │ fast   │ visual   │ thorough │
         └────────┴──────────┴──────────┘
```

Then when the Lab sees:

```text
reward = $15
```

it chooses a cheap elite.

When:

```text
reward = $1,000
```

it selects a much more expensive strategy.

That's exactly the right use of quality-diversity.

---

# 21. The closest research I've found is almost eerily aligned

A May 2026 paper called **EXG: Self-Evolving Agents with Experience Graphs** proposes storing agent successes and failures in a relational experience graph, growing that graph online during work and reusing it offline to improve future task performance. Their experiments report better performance/efficiency than simpler reflection- and memory-based baselines. ([arXiv][8])

That's essentially:

```text
experience
 ↓
graph
 ↓
future improvement
```

Your version adds:

```text
Letta persistent identities
+
economic outcomes
+
cg experimental validation
+
worker/lab hierarchy
+
marketplace
```

So there is real research support for the central idea.

I couldn't find a mature public project already combining **Letta + HydraDB specifically** into this architecture. That isn't proof nobody has tried it, but I did search for the pairing directly.

---

# 22. Letta themselves are moving toward the same learning problem

Their current research program explicitly includes:

**Trajectory**, a normalized format for experience data across Letta Code, Claude Code, Codex and other harnesses; memory-model research; skill learning; and evaluations for whether agents actually generate and use memory effectively. ([Letta][9])

This is important.

I would look very closely at their **Trajectory format** before inventing a Moltwork trajectory schema.

You can potentially have:

```text
Letta trajectory
      │
      ▼
Moltwork RunReceipt
      │
      ├─ economics
      ├─ opportunity
      ├─ outcome
      ├─ evidence
      └─ hashes
```

Again, extend a standard rather than fight it.

---

# 23. Hindsight is probably the strongest alternative we were missing

This deserves serious attention.

Hindsight was presented at ACL 2026 and organizes memory into four conceptual networks:

* world
* experience
* observation
* opinion

with `retain`, `recall`, and `reflect`, combining vector retrieval, keyword matching, graph traversal and temporal filtering over PostgreSQL/pgvector. ([ACL Anthology][10])

Its newer **Mental Models** are especially relevant. Rather than re-synthesizing hundreds of memories every time, it maintains persistent higher-order models that are refreshed as new evidence arrives. ([hindsight.vectorize.io][11])

That maps almost absurdly well to:

```text
World
    Oracle / clients / task facts

Experiences
    worker runs

Observations
    recurring empirical patterns

Mental Models
    "How our lab wins API jobs"
```

If Hydra becomes painful, **Hindsight is the first alternative I would benchmark**.

It's less of a distributed graph-engine bet and more of a purpose-built memory server.

---

# 24. Cognee is closer to us than I previously realized too

Cognee 1.0 is explicitly pitching itself as an open shared-memory layer for agent fleets. ([Cognee][12])

More importantly, their recent work discusses taking decision traces, compressing repeated patterns into context graphs, and **behaviorally validating** whether memory changes actually improve agent performance. Their `improve()` operation can also use feedback to alter the importance of graph elements and promote session knowledge into persistent memory. ([Cognee][13])

That's getting quite close to our “experience → validated organizational knowledge” loop.

But `cg` gives you something stronger:

> explicit experimental selection rather than merely memory enrichment.

---

# 25. GBrain has one architectural lesson worth stealing

GBrain explicitly separates:

```text
world knowledge
        GBrain

agent operational state
        agent memory

current interaction
        session context
```

([GitHub][14])

That separation is correct.

Our version simply adds another type:

```text
WORLD KNOWLEDGE
Hydra project/company graph

LAB EMPIRICAL KNOWLEDGE
Hydra run/outcome graph

WORKER KNOWLEDGE
Letta

CURRENT STATE
Letta session
```

I would **not** spend time competing with GBrain on generic people/meetings/company-pages knowledge.

Let GBrain/cognee/etc. own that category.

Moltwork's brain should be obsessive about:

> **what did we do, what happened, what did it cost, why did it work, and what should change?**

That's much more distinctive.

---

# So are we competing with AutoClaw now?

**At the product surface, yes.**

A Moltwork user might see:

```text
Create Worker
Give it a role
Connect tools
Give it jobs
See it work
Schedule it
Watch it learn
```

That absolutely overlaps AutoClaw.

But underneath, we are still following the earlier rule:

> **do not build another generic agent harness.**

AutoClaw builds a harness.

We use Letta's harness.

The thing **we** build is:

```text
              AUToclaw-like layer

execution / tools / memory / subagents
                   │
                   │ LETTA handles this
                   ▼

              MOLTWORK LAYER

jobs
economics
run recording
experimental evaluation
worker evolution
lab intelligence
capability lineage
market performance
```

So the product can compete without the infrastructure duplicating them.

That's a completely legitimate strategy.

---

# I would actually ignore the other frameworks for v1

Not delete the possibility forever.

Just stop integrating them.

Keep one tiny interface:

```text
WorkerRuntime
    execute()
    cancel()
    snapshot()
    restore()
    inspect()
```

Then implement:

```text
LettaRuntime
```

and **nothing else** initially.

Don't build:

```text
HermesAdapter
OpenClawAdapter
OpenHandsAdapter
CrewAIAdapter
LangGraphAdapter
```

yet.

Every extra runtime multiplies:

```text
memory semantics
trace formats
tool semantics
state handling
failure handling
testing
```

and distracts from the differentiated loop.

Letta can already orchestrate subagents, skills and computer-use workflows. Their direction is explicitly toward the general-purpose harness role. ([Letta][1])

---

# One important `.af` correction

Don't define a modern Moltwork Worker as merely:

```text
worker.af
```

`.af` is useful, but modern Letta Code's Git-based MemFS/skills environment has become richer than what Agent File alone represents.

I would define:

```text
Moltwork Worker Bundle

worker.json
agent.af
memory/
    git commit/repository
skills/
mods/
runtime.lock
```

with hashes:

```text
agent_file_hash
memfs_commit
skills_root
mods_root
runtime_version
template_parent
```

That gives you a proper worker genotype/snapshot.

Then:

```text
Worker v1
   │
 mutation
   ▼
Worker v2
   │
 mutation
   ▼
Worker v3
```

can be tied directly into `cg`.

---

# The coolest product primitive might be the **Worker School**

For every useful job family:

```text
API research
React bugfix
SEO audit
customer support
Xero reconciliation
MSP ticket triage
hackathon submission
```

you accumulate previous jobs.

Turn them into a `cg` worldpack:

```text
api-research-school/

training/
validation/
hidden/

evaluator.py
rubric.yaml
fixtures/
historical-runs/
```

Then:

```text
spawn fresh worker
      ↓
run school
      ↓
identify weaknesses
      ↓
Letta reflects / creates skills
      ↓
cg tests changes
      ↓
repeat
      ↓
certified worker
```

Now Moltwork literally has:

> **schools for agents.**

And real work keeps producing new training/evaluation material.

That's a beautiful flywheel:

```text
REAL JOBS
   │
   ▼
EXPERIENCE
   │
   ▼
SCHOOL DATA
   │
   ▼
BETTER WORKERS
   │
   ▼
MORE JOBS
```

---

# You can also have overnight “evolution”

Letta already has the concept of background reflection / sleep-time memory work. ([Letta][5])

Combine it with `cg`:

```text
during day:
worker does real work

overnight:
Letta examines trajectories
        ↓
proposes:
memory changes
skill changes
mods
strategies
        ↓
cg forks them
        ↓
replays historical work
        ↓
hidden eval
        ↓
winning variants survive
        ↓
new worker version
```

That's much more rigorous than:

> “agent reflects while you're asleep.”

It becomes:

> **agent runs R&D on itself while idle.**

That's excellent.

---

# And then Hydra becomes an R&D graph

You can literally visualize:

```text
Researcher-03 v12
      │
      ├── mutation → v13
      │                │
      │                └── REGRESSED_ON → API Research
      │
      └── mutation → v14
                       │
                       ├── IMPROVED_ON → API Research
                       ├── IMPROVED_ON → Market Research
                       └── REGRESSED_ON → Coding
```

MAP-Elites prevents you throwing v12 away simply because v14 exists.

Maybe:

```text
v14 = best researcher

v12 = cheaper

v9 = unusually good at financial extraction
```

You retain a **population of specialists**.

Now the Lab begins to resemble ecology rather than a chatbot.

---

# This is the product I'd build

I would call the primitives:

```text
WORKER
persistent Letta professional

LAB
private Hydra experience graph

SCHOOL
cg task-family evaluation environment

GENOME
worker bundle/version

RUN
one real or replayed task execution

OUTCOME
external result / evaluator result / economics

LESSON
candidate memory change

SKILL
validated repeatable procedure

MUTATION
candidate worker change

LINEAGE
evidence-backed worker ancestry

LAB MODEL
private derived organizational insight
```

That's enough conceptual vocabulary to build the whole thing.

---

# Concrete implementation order

I would resist adding anything else until this single pipeline works:

1. **Freeze a `Lab`, `Worker`, `Run`, `Submission`, `Evaluation`, `Outcome`, `MemoryRevision`, `SkillVersion` schema.** Keep canonical events outside Hydra and project them into Hydra.
2. **Upgrade `cg`'s Hydra integration against the current Hydra build.** Your existing association-node fallback was designed around an older image with limited mutation support; keep the capability probe, but use newer graph operations when available rather than permanently encoding the workaround.
3. **Create one persistent Letta worker.** Not five. Give it one job family—hackathon/research submission is perfect because we already understand how to assess it.
4. **Connect `LabContext` as a tiny tool surface.** `recall_similar_runs`, `get_task_priors`, `get_failure_patterns`, `get_best_skill`, `record_observation`. Do not expose raw Cypher to the worker by default.
5. **Generate several submission candidates for each exemplar job.** Feed them through `cg` quality gates and selection.
6. **Record every run and worker version.** Tie Letta MemFS Git commit + skills + model + tool policy to the RunReceipt.
7. **Implement post-run learning.** Letta proposes a memory/skill change; `cg` replays it on earlier tasks and hidden tasks; only statistically credible/non-regressing changes get promoted.
8. **Add real outcomes.** `won`, `lost`, score, payout, reviewer feedback. This becomes the strongest learning signal in the graph.
9. **Create task-family Lab Models.** Automatically derive things such as “what predicts success on API hackathons?” but always preserve underlying evidence/provenance.
10. **Only after one worker demonstrably improves, spawn five.** Then implement lab inheritance, worker matching, private Oracle scoring and lineage reputation.

The proof-of-concept success metric shouldn't be:

> “The agent remembers things.”

It should be:

> **Worker v7 measurably beats Worker v1 on held-out jobs after learning from prior work, and we can show exactly which memories/skills/process changes caused the improvement.**

If you demonstrate that, you've got something much more interesting than another AutoClaw clone.

## The strongest positioning

I think the project has moved from:

> **“economic operating system for agents”**

to a more concrete implementation of that vision:

> **Moltwork is a learning lab for autonomous workers. Workers retain individual experience with Letta; the Lab accumulates organizational experience in an evidence graph; `cg` experimentally determines which memories, skills and strategies actually improve performance.**

The Oracle then becomes the source of **real curriculum**.

The marketplace becomes where proven outputs of that learning process get sold:

```text
skill
template
trained worker
lab model
verified capability
hosted worker
```

And Phala/dstack can still slot underneath later to attest **which exact worker genome/runtime produced a run**. Nothing about this architecture invalidates the TEE layer; it actually gives the TEE something much more meaningful to attest.

The nearest systems I found cover pieces—EXG covers experience graphs, Hindsight covers structured learning memory, Cognee covers graph memory plus feedback, GBrain covers organizational knowledge, Letta covers persistent learning workers—but **I didn't find an established system combining persistent worker identity + organization-wide empirical graph + controlled experimental evolution + economic outcomes** in quite this way. ([arXiv][8])

That intersection is the part I would build.

This stack is moving very quickly, so I can track Letta, HydraDB, Hindsight, Cognee and self-evolving-agent research for anything that should change the architecture.

[1]: https://www.letta.com/blog/our-next-phase/?utm_source=chatgpt.com "Letta's Next Phase | Letta"
[2]: https://docs.hydradb.com/essentials/multi-tenant?utm_source=chatgpt.com "Multi-Tenant Support - HydraDB SDK"
[3]: https://docs.hydradb.com/plugins/mcp?utm_source=chatgpt.com "HydraDB MCP - HydraDB SDK"
[4]: https://github.com/hydra-db/hydradb?utm_source=chatgpt.com "GitHub - hydra-db/hydradb: HydraDB - fast graph database on object storage · GitHub"
[5]: https://www.letta.com/blog/context-repositories/?utm_source=chatgpt.com "Introducing Context Repositories: Git-based Memory for Coding Agents | Letta"
[6]: https://docs.hydradb.com/index?utm_source=chatgpt.com "Introduction - HydraDB SDK"
[7]: https://hydradb.com/blog/ai-agent-memory-context-database-problem?utm_source=chatgpt.com "AI Agent Memory Is a Database Problem - HydraDB"
[8]: https://arxiv.org/abs/2605.17721?utm_source=chatgpt.com "EXG: Self-Evolving Agents with Experience Graphs"
[9]: https://www.letta.com/research/?utm_source=chatgpt.com "Research | Letta"
[10]: https://aclanthology.org/2026.acl-demo.27/?utm_source=chatgpt.com "Hindsight: Structured Agent Memory that Retains, Recalls, and Reflects - ACL Anthology"
[11]: https://hindsight.vectorize.io/blog/2026/06/05/mental-models-deep-dive?utm_source=chatgpt.com "How Hindsight Learns: A Deep Dive Into Mental Models | Hindsight"
[12]: https://www.cognee.ai/cognee-1-0-announcement?utm_source=chatgpt.com "cognee 1.0: The Open-Source Memory Platform for AI Agents | Cognee"
[13]: https://www.cognee.ai/context-graphs-world-models-and-behavioral-validation?utm_source=chatgpt.com "Agent Memory: From Decision Traces to Predictive World Models"
[14]: https://github.com/liucunguang/gbrain?utm_source=chatgpt.com "GitHub - liucunguang/gbrain: Garry's Opinionated OpenClaw/Hermes Agent Brain - Mirror · GitHub"
