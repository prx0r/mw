Yes. The Git-native direction becomes much more coherent if we define a strict rule:

> **Git stores versions of things. Hydra stores evidence about interactions between those versions. Letta turns selected evidence into future cognition. CGE/worlds provide controlled environments that generate the evidence.**

That means Hydra is not replacing Git and it is not replacing Letta memory.

```text id="5whdnb"
                    GIT
       "what exactly was this thing?"
                     │
        commits / diffs / branches
                     │
       ┌─────────────┼──────────────┐
       ▼             ▼              ▼
 Letta MemFS      WorldPack       Assessor
  + Skills        + School         + Rubric
       │             │              │
       └─────────────┼──────────────┘
                     ▼
                  EXPERIMENT
                     │
                   Letta
                     │
              WorkerKit events
                     │
                Trajectory
                     │
                  Evaluator
                     │
               external result
                     │
                     ▼
                  HYDRADB
      "what happened when these versions met?"
                     │
              Lab scientist
                     │
        hypothesis / attribution
                     │
                     ▼
             candidate change
                     │
          Git branch / worktree
                     │
                     ▼
             controlled re-test
                     │
            promote or reject
                     │
                     ▼
             Letta learns v+1
```

That is the loop.

## 1. Git should be treated as the experimental substrate

Letta has independently arrived at almost the same idea for memory. Its Context Repositories put agent memory in a real Git-backed filesystem; reflection and memory-management subagents use Git worktrees so they can mutate memory independently and merge changes later. ([Letta][1])

This means we don't need to invent an abstraction for worker versions.

A **WorkerVersion** can literally be something like:

```yaml id="bact0o"
worker_id: researcher-03
letta_agent_id: agent-123

memory_commit: 2e71f4a
skill_tree_commit: 2e71f4a

harness:
  letta_code: 0.x
  mod_commit: 398bbc1

runtime:
  model: anthropic/...
  reasoning_effort: medium
  toolset: research-v2

parent_worker_version: researcher-03/v7
```

Letta explicitly distinguishes memory, procedural Skills and harness-level changes/Mods, which is exactly the mutation taxonomy we need. Its current harness also gives runtime controls around model, cwd, allowed tools, permissions and dreaming. ([GitHub][2])

So a worker mutation is no longer vague:

```text id="j188rg"
v7
 |
 +-- memory commit changed
 |
 +-- skill changed
 |
 +-- model changed
 |
 +-- Mod changed
 |
 +-- retrieval policy changed
 |
 +-- Lab briefing changed
```

Each can be isolated.

---

# 2. A World should work exactly the same way

A WorldVersion is simply:

```yaml id="g6pq7q"
world: hackathon.idea-generation
repo: github.com/foo/hackathon-ideation-world
commit: 7ca182e

ontology:
  task_family: research.ideation.technical
  capabilities:
    - requirements.extract
    - source.verify
    - solution.ideate
    - technical.feasibility
    - submission.communicate
```

And the repository might be:

```text id="qo65mf"
hackathon-ideation-world/
├── world.yaml
├── README.md
│
├── public/
│   ├── task.md
│   ├── rubric.md
│   ├── docs/
│   └── examples/
│
├── scenarios/
│   ├── dev.jsonl
│   └── validation.jsonl
│
├── graders/
│   ├── requirements.py
│   ├── evidence.py
│   ├── technical.py
│   └── rubric.py
│
├── rewards.py
│
└── .github/
    └── workflows/
        └── evaluate.yml
```

That repository is immediately useful to another person.

They fork it.

Change the rubric.

Add scenarios.

Run their Letta worker.

Compare.

PR improved scenarios upstream.

That's already a viable ecosystem without a marketplace.

---

# 3. The secret evaluator must **not** live in that public Git history

This is important.

Once hidden labels or secret tasks enter a public Git repository, removing them later does not make them genuinely secret because Git history preserves old objects.

So:

```text id="v4ajhu"
PUBLIC WORLD REPO
├── schemas
├── dev set
├── public rubric
├── deterministic checks
└── examples

PRIVATE EVAL REPO / DATASET
├── sealed scenarios
├── hidden rubrics
├── adversarial cases
└── calibration corpus
```

Letta Evals already supports private datasets and commit-pinned datasets, custom graders, agent factories, isolated sandbox runs, repeated runs and cached re-grading. ([GitHub][3])

That is perfect for this split.

So someone can open-source:

```text id="l3ke8n"
support-agent-school
```

while retaining:

```text id="20udmi"
support-agent-school-secret
```

as their proprietary evaluation asset.

---

# 4. This is where “World” turns naturally into “School”

I think you're right.

A World answers:

> Can this agent do X?

A School answers:

> How do I make an agent better at X?

The School is basically:

```text id="01zo4y"
School
├── ontology mapping
│
├── curriculum
│   ├── easy
│   ├── medium
│   ├── hard
│   └── adversarial
│
├── WorldPacks
│
├── assessor
│
├── feedback interpreter
│
├── known failure taxonomy
│
├── reference materials
│
└── optional skill/process seeds
```

That distinction is valuable.

For example:

```text id="ypx1zf"
WORLD
customer-support/refunds-v2

tests:
"Can you handle refunds correctly?"
```

versus:

```text id="pjppeu"
SCHOOL
customer-support-agent-v4

curriculum:
refunds
angry customers
policy ambiguity
fraud indicators
escalation
tool failures
long conversations

feedback:
why failures occurred

promotion:
sealed policy suite
```

The evaluator becomes valuable precisely because the school author has accumulated knowledge about what actually distinguishes good workers.

---

# 5. There are three obvious publishing models

You don't actually need marketplace infrastructure to test any of them.

| Model            | Public Git                | Private                   |
| ---------------- | ------------------------- | ------------------------- |
| Open benchmark   | everything except secrets | hidden suite              |
| Open-core school | basic worlds + grader     | advanced curriculum/evals |
| Private school   | interface/schema/demo     | entire useful corpus      |

The public Git repository builds reputation and makes the school discoverable.

The valuable private thing can eventually be:

```text id="20f6bg"
hidden evaluator
premium scenarios
curriculum
validated skill bundle
teacher agent
historical outcome corpus
```

And the strongest credential for selling it isn't marketing copy.

It is:

```text id="vwi8yt"
School v4

Worker baseline: 0.61
After curriculum: 0.79

Held-out world:
+0.16 paired improvement

Real competitions:
3/8 → 6/8 top quartile

receipts:
...
```

That is where Moltwork's eventual inventory marketplace gets interesting.

---

# 6. HydraDB's role is much more specific than “memory”

HydraDB itself doesn't ingest Git automatically.

It is a graph database with OpenCypher queries, typed relationships, indexes and native graph traversal. Its durable truth lives in object storage; queries operate against pinned snapshots, and its traversal indexes are accelerators rather than canonical truth. ([GitHub][4])

So we build:

```text id="vcc94k"
GitProjector
RunProjector
EvalProjector
OutcomeProjector
```

They feed Hydra.

### GitProjector

Turns:

```text id="jge1w8"
repo
commit
parent
branch
tag
diff
```

into graph entities.

### RunProjector

Consumes:

```text id="fy7fwa"
WorkerKit
@letta-ai/trajectory
Letta session metadata
```

Letta's Trajectory project is explicitly intended as a standardized agent-readable representation of experience across harnesses, including Letta Code, Claude Code and Codex. ([Letta][5])

### EvalProjector

Consumes Letta Evals results:

```text id="mi186c"
grader scores
reward
rubric dimensions
failure categories
judge metadata
```

### OutcomeProjector

Eventually adds:

```text id="op7ypj"
competition ranking
accepted/rejected
customer satisfaction
payout
production metrics
human review
```

Hydra can then answer questions spanning all four.

---

# 7. The Hydra schema is the really interesting bit

I'd make the graph substantially richer than our current `lab_runs` SQLite projection.

```text id="k1l2oz"
(:Repo)

(:Commit)
(:Branch)
(:Tag)

(:Worker)
(:WorkerVersion)
(:MemoryCommit)
(:SkillVersion)
(:ModVersion)

(:World)
(:WorldVersion)
(:Scenario)
(:School)
(:SchoolVersion)

(:Experiment)
(:Treatment)
(:Run)
(:Decision)
(:Trajectory)

(:Artifact)
(:Asset)

(:Assessor)
(:AssessorVersion)
(:Evaluation)
(:Criterion)

(:Opportunity)
(:Outcome)

(:LearningProposal)
(:CapabilityClaim)
(:WorldValidityClaim)
```

Then edges:

```text id="gpp56h"
Commit
  -[:PARENT_OF]-> Commit

WorkerVersion
  -[:MUTATION_OF]-> WorkerVersion

WorkerVersion
  -[:USES_MEMORY]-> MemoryCommit

WorkerVersion
  -[:USES_SKILL]-> SkillVersion

Run
  -[:EXECUTED_BY]-> WorkerVersion

Run
  -[:IN_WORLD]-> WorldVersion

Run
  -[:TREATMENT_OF]-> Experiment

Run
  -[:GENERATED]-> Trajectory

Run
  -[:PRODUCED]-> Artifact

Run
  -[:CONTAINS]-> Decision

Evaluation
  -[:ASSESSED]-> Artifact

Evaluation
  -[:USED_ASSESSOR]-> AssessorVersion

Evaluation
  -[:SCORED]-> Criterion

Outcome
  -[:RESULT_OF]-> Run

LearningProposal
  -[:SUPPORTED_BY]-> Run

WorkerVersion
  -[:PROMOTED_BY]-> Experiment

CapabilityClaim
  -[:SUPPORTED_BY]-> Experiment

WorldValidityClaim
  -[:SUPPORTED_BY]-> Outcome
```

Now the graph starts becoming extremely powerful.

---

# 8. Hydra's native graph functionality is unusually well suited to this

HydraDB supports normal OpenCypher-style graph matching, filtering, relationships, aggregation and batched writes. More unusually, it has native snapshot-scoped path procedures:

```text id="blcwwk"
algo.SPpaths
one source → one target

algo.SSpaths
one source → reachable targets

algo.MSpaths
many sources → many targets
```

`MSpaths` is specifically optimized to resolve and traverse many source/target values together rather than forcing client-side query fan-out. ([GitHub][4])

That becomes useful once Moltwork has thousands of runs.

Imagine querying:

```text id="h5n31a"
[Memory commits]
       ↓
[Worker versions]
       ↓
[Runs]
       ↓
[Artifacts]
       ↓
[Evaluations]
       ↓
[Outcomes]
```

for 200 candidate memory revisions simultaneously.

Or:

```text id="mvfbck"
SkillVersion
   ↓
all processes containing it
   ↓
all task families
   ↓
all external outcomes
```

You can start asking:

> Does this skill actually transfer?

rather than:

> Did the agent say the skill was useful?

---

# 9. But be careful with the word “causal”

Hydra initially knows associations.

```text id="remw4e"
memory M
was used in
run R
which got
score .82
```

does **not** establish:

```text id="hrosnm"
memory M caused .82
```

Causal-ish evidence comes from CGE experiments:

```text id="bh1nvv"
same task
same model
same tools
same budget
same assessor

v7 without M
versus
v7 + M
```

Then Hydra can store:

```text id="4k9tqi"
(:Experiment {
  design:"paired",
  controlled:true
})

(:TreatmentA)
(:TreatmentB)

(:Finding {
  delta:.11,
  ci_low:.06,
  ci_high:.15
})
```

Only *then* should the Lab promote a strong claim.

That's why CGE remains critical.

---

# 10. Letta memory should consume **conclusions**, not Hydra

This boundary matters enormously.

Do NOT give a Letta worker:

```text id="rd3164"
entire Hydra graph
```

and say:

> Learn from this.

Instead:

```text id="ozqrzt"
HYDRA
   ↓
Lab query
   ↓
Experimentally supported finding
   ↓
Memory/Skill candidate
   ↓
held-out test
   ↓
promotion
   ↓
LETTA MemFS
```

For example Hydra sees:

```text id="a7ts3i"
12 submission runs.

8 failures involved:
missing explicit sponsor requirement.

Requirement-extraction Skill:
baseline pairwise score .67
candidate score .81

held-out:
+0.12
```

The Lab produces:

```text id="0lbju1"
Candidate Skill:
"Before ideation, extract every explicit
 judging/sponsor requirement and map the
 proposed solution to each requirement."
```

Then test it.

Only after validation does that become Letta procedural memory.

---

# 11. This aligns with Letta's latest memory research almost perfectly

Letta now explicitly evaluates **memory usage** separately from **memory generation**.

Memory usage includes:

```text id="p4vyw5"
retrieval
adherence
```

Memory generation includes:

```text id="irxp6w"
generalization
hygiene
```

Their July 2026 production-memory benchmark found that simply accumulating corrections is a failure mode: better agents generalize repeated observations into durable rules and maintain clean memory rather than piling up stale/duplicated notes. ([Letta][6])

That gives our Lab four first-class worker capabilities:

```text id="1b2ows"
memory.retrieve
memory.adhere
memory.generalize
memory.hygiene
```

We should measure them separately.

Because a worker could be:

```text id="pclrz9"
excellent at writing memory
terrible at retrieving it
```

or vice versa.

---

# 12. Letta's own reflection rules are a good boundary for Schools too

Their current reflection subagent is instructed to put durable facts/corrections into memory, and create or update a Skill only when a reusable multi-step workflow genuinely generalizes beyond the current session. ([GitHub][7])

That's exactly how Moltwork should distinguish:

```text id="d053wa"
experience
→ memory

repeatable procedure
→ skill

deterministic invariant
→ Mod/harness

test of capability
→ World

series of tests + curriculum
→ School
```

This gives us a nice ontology of Git-native artifacts.

---

# 13. Git has several underused primitives that fit this almost absurdly well

This is where I think there's unexplored territory.

### Git worktrees = experimental treatment isolation

Letta already uses worktrees for concurrent memory reflection. Git supports several linked working trees attached to one repository, each with its own HEAD. ([Git][8])

We extend that:

```text id="szn07k"
worker memory main
       │
       ├── worktree experiment/E81-control
       │
       ├── worktree experiment/E81-skill
       │
       └── worktree experiment/E81-dreaming
```

Run them all.

Discard losers.

Merge winner.

That is gorgeous.

---

# 14. Git notes may be perfect for empirical annotations

This one is particularly underused.

Git Notes can attach arbitrary metadata to an existing Git object **without changing the object itself**, and they live under separate refs such as `refs/notes/commits`. ([Git][9])

So imagine:

```text id="c8t0g0"
commit 31faa7
"added rubric extraction skill"
```

Then under:

```text id="xbxkto"
refs/notes/moltwork/evals
```

attach:

```json id="5wkh9v"
{
  "experiments": ["E81", "E89"],
  "paired_delta": 0.117,
  "n": 18,
  "status": "validated",
  "hydra_node": "skill:31faa7"
}
```

The source commit remains untouched.

Git says:

```text id="q05h9z"
what changed
```

Git Notes says:

```text id="sxvrko"
what we subsequently learned about it
```

Hydra gives the full queryable graph.

That's a very clean three-layer model.

I wouldn't make Notes canonical—the graph can contain much richer evolving evidence—but they are an excellent **portable annotation index**.

---

# 15. `git bisect` becomes agent-memory debugging

This might be one of the coolest consequences of Letta's Git memory architecture.

Git bisect can automatically binary-search commits to find the revision introducing a regression and can execute a test command with `git bisect run`. ([Git][10])

So:

```text id="52pilh"
worker v21:
benchmark score .81

worker v37:
benchmark score .66
```

Run:

```text id="j2cv9u"
git bisect
```

where the "test command" is:

```text id="3nd9kt"
moltwork eval world://support/refunds-smoke
```

and automatically find:

```text id="c1c9zn"
commit 8e19b22

reflection:
"always immediately reassure customer..."
```

introduced the regression.

Now the Lab has strong evidence:

```text id="vb34bh"
MemoryCommit 8e19b22
   -[:INTRODUCED_REGRESSION]->
Capability policy.compliance
```

That's a genuinely novel-feeling Git × agent-memory workflow.

---

# 16. Git tags become certification boundaries

A normal memory commit is:

```text id="xzr90h"
candidate state
```

An annotated/signed tag can represent:

```text id="0q3d6i"
validated worker release
validated school
validated world
```

Git supports cryptographically verifying signed tags. ([Git][11])

For example:

```text id="czac3g"
worker/researcher/v12
school/customer-support/v4
world/hackathon-ideation/v7
```

Only tag after passing promotion tests.

Branches are research.

Tags are claims.

---

# 17. GitHub artifact attestations add another useful proof layer

GitHub can produce Sigstore-backed artifact attestations linking a built artifact to the repository, commit SHA, workflow and triggering event. Public attestations are recorded through Sigstore's public transparency infrastructure. ([GitHub Docs][12])

So if a World contains:

```text id="nadg1q"
grader.wasm
```

GitHub Actions can build it and attest:

```text id="yzx9h4"
grader.wasm
built from commit 72faa8
using workflow evaluate-build.yml
```

Important:

> Attestation proves provenance, **not evaluator correctness**.

GitHub explicitly makes that distinction. ([GitHub Docs][12])

CGE/WorldValidityClaim proves empirical usefulness.

Attestation proves provenance.

Different things.

---

# 18. Git bundles could become a surprisingly elegant “School package”

Git bundles can package Git objects and refs into a portable file that can later be cloned or fetched without a live server. ([Git][13])

Later:

```text id="sxxssf"
customer-support-school-v4.bundle
```

could contain:

```text id="g0mguh"
curriculum history
world versions
grader versions
skill seeds
documentation
release refs
```

This is potentially a really elegant portable `.school` format without inventing a new package format.

The file could simply be a Git bundle plus a tiny manifest.

No need to implement this now, but it's worth remembering.

---

# 19. GitHub Actions can make every World executable by default

Each public World repo should ship a reusable evaluation workflow.

GitHub supports reusable workflows specifically so repositories can centralize deterministic repeatable logic and other repos can call it. ([GitHub Docs][14])

Imagine:

```text id="nt1q7b"
uses:
  moltwork/world-hackathon-ideas/
  .github/workflows/evaluate.yml@7e8fa21
```

Then every worker repository can have:

```text id="ptpvu1"
on:
  pull_request
```

and automatically receive:

```text id="yx0244"
Requirements       .91
Evidence           .82
Novelty            .76
Technical          .88
Overall            .84

baseline            .79
candidate delta    +.05
```

Now agent evolution starts looking like normal software CI.

That's an important design goal:

> **Benchmarks should feel like tests for workers.**

---

# 20. Cached trajectories create another excellent separation

Letta Evals can re-grade saved trajectories without re-running the worker. ([GitHub][3])

This matters a lot because we have **two things evolving**:

```text id="8cglge"
worker
assessor
```

Suppose Assessor v4 changes its rubric.

We don't want to spend money rerunning 300 workers.

Instead:

```text id="x8ggr3"
existing trajectories
      ↓
Assessor v3
Assessor v4
Assessor v5
      ↓
compare predictions
      ↓
real outcomes
```

Then Hydra can tell us which AssessorVersion best predicts reality.

That makes evaluator development itself cheap.

---

# 21. The actual full loop

This is the version I would implement.

```text id="5jga1m"
──────────────────────────────────────────────
1. MARKET OBSERVATION
──────────────────────────────────────────────

Oracle:
task_family = research.ideation.technical
demand ↑
reward available

              ↓

──────────────────────────────────────────────
2. CAPABILITY QUERY
──────────────────────────────────────────────

Hydra:

What evidence do we have for
researcher-03 on this task family?

Known:
requirements.extract = strong
source.verify = strong
idea.novelty = weak evidence
submission.communication = mediocre

              ↓

──────────────────────────────────────────────
3. WORLD DISCOVERY
──────────────────────────────────────────────

Find Git repos mapped to ontology:

technical-ideation-world
hackathon-world
sponsor-integration-world

Pin exact commits.

              ↓

──────────────────────────────────────────────
4. BASELINE
──────────────────────────────────────────────

WorkerVersion v7

MemFS commit
Skills commit
model
tools
Mod commit

fresh Letta session

              ↓

──────────────────────────────────────────────
5. EXECUTE WORLD
──────────────────────────────────────────────

Letta works task

WorkerKit witnesses:
tool calls
cost
commits
artifacts

Trajectory normalized.

              ↓

──────────────────────────────────────────────
6. ASSESS
──────────────────────────────────────────────

deterministic graders
rubric graders
pairwise judge
secret suite

Letta Evals produces results.

              ↓

──────────────────────────────────────────────
7. PROJECT INTO HYDRA
──────────────────────────────────────────────

WorkerVersion
WorldVersion
MemoryCommit
SkillVersion
Run
Trajectory
Artifact
Evaluation
Criterion

all connected.

              ↓

──────────────────────────────────────────────
8. SCIENTIST QUERY
──────────────────────────────────────────────

Across prior runs:

"Why is ideation weak?"

Hydra:
high novelty scores correlate with
explicit constraint decomposition.

Worker rarely performs it.

              ↓

──────────────────────────────────────────────
9. GENERATE HYPOTHESIS
──────────────────────────────────────────────

Hypothesis:

A constraint-decomposition skill
improves technical ideation.

              ↓

──────────────────────────────────────────────
10. FORK WORKER
──────────────────────────────────────────────

Git worktree:

control = v7
candidate = v7 + skill

              ↓

──────────────────────────────────────────────
11. CONTROLLED CGE EXPERIMENT
──────────────────────────────────────────────

same worlds
same model
same budgets
same evaluator

paired runs

              ↓

──────────────────────────────────────────────
12. STATISTICS
──────────────────────────────────────────────

paired delta
bootstrap CI
non-inferiority gates
cost impact

              ↓

──────────────────────────────────────────────
13. PROMOTION
──────────────────────────────────────────────

if validated:

merge worktree
commit memory/skill
tag WorkerVersion v8

otherwise:
discard branch
retain failed experiment in Hydra

              ↓

──────────────────────────────────────────────
14. REAL WORK
──────────────────────────────────────────────

v8 receives actual Oracle opportunity.

              ↓

──────────────────────────────────────────────
15. EXTERNAL OUTCOME
──────────────────────────────────────────────

ranked / won / rejected / paid
judge comments
human feedback

              ↓

──────────────────────────────────────────────
16. HYDRA UPDATE
──────────────────────────────────────────────

Did our assessor predict reality?

Did candidate improvement transfer?

Did this skill actually help economically?

              ↓

──────────────────────────────────────────────
17. LETTA LEARNING
──────────────────────────────────────────────

ONLY validated findings become:

memory
skill
shared context
Mod/harness policy

              ↓

repeat.
```

That's the Lab.

---

# 22. And Worlds evolve through exactly the same loop

This is the beautiful symmetry.

Suppose:

```text id="rcrr7h"
World v4 predicts:
Submission A > Submission B

real contest:
B > A
```

Hydra records an evaluator error.

Now:

```text id="l4wo4z"
WorldValidityClaim weakened.
```

The World developer investigates.

Maybe visual polish was underweighted.

Fork:

```text id="atx7i8"
world-v4
   ↓
world-v5
```

Re-grade cached trajectories.

Compare v4/v5 against historical external outcomes.

If v5 predicts better:

```text id="96kdl9"
promote world-v5
```

So we have:

```text id="9j3wgj"
WORKER EVOLUTION
        ↕
WORLD EVOLUTION
```

This was one of the strongest ideas in old CG, and Git makes it dramatically more practical.

---

# 23. Schools become the bridge between them

A successful school contains knowledge discovered through both sides:

```text id="9gjfav"
WORLD EVOLUTION
"what distinguishes good performance?"

          ↓

SCHOOL
"what sequence of experiences improves it?"

          ↓

WORKER EVOLUTION
"did learning actually transfer?"
```

So a school has an empirical lifecycle:

```text id="f2d3yc"
Worlds
  ↓
diagnose weaknesses
  ↓
curriculum
  ↓
worker experiences
  ↓
memory/skill changes
  ↓
held-out worlds
  ↓
capability improvement
```

That's much more defensible than selling a prompt pack.

---

# 24. I think there are five Git-native asset classes

This is what the eventual ecosystem should converge around:

| Asset        | Meaning                                 |
| ------------ | --------------------------------------- |
| **Worker**   | persistent Letta identity/config/memory |
| **Skill**    | reusable procedural capability          |
| **World**    | test of a capability                    |
| **School**   | process for improving a capability      |
| **Assessor** | model of what “good” means              |

Then Hydra provides the empirical layer connecting them:

```text id="zfnou2"
Skill S
improved
Worker W
on
World X

after
School Y

according to
Assessor A

and later correlated with
real Outcome O.
```

That graph is potentially the actual moat.

Not merely the marketplace.

Not merely the Oracle.

It's an **empirical graph of agent capability development**.

---

# 25. What I would build now

I would make the next checkpoint brutally narrow:

1. **Separate `cge` into the Git-native World/School protocol.** Keep WorldPack, ExperimentSpec, paired statistics, hidden-suite conventions, fork/replay and capability claims. Delete its agent/runtime/memory ambitions.
2. **Make Letta the only worker implementation.** Use Agent SDK + Letta Code + MemFS + Skills + Trajectory. A fresh conversation is one experimental task; a MemFS commit is part of WorkerVersion identity. ([GitHub][15])
3. **Build `moltwork-letta` as a tiny Mod/integration.** It exposes Oracle, Lab/Hydra lookups, budget/receipt hooks and experiment metadata to the worker.
4. **Build the Git projector.** Commit/fork/tag events → Hydra nodes. Do not mirror blob contents unless required; store repo + SHA + semantic metadata.
5. **Build the Run/Eval projector.** Letta Trajectory + WorkerKit + Letta Evals → Hydra.
6. **Create exactly one serious School:** `competition.technical_submission`. Include requirements extraction, research, ideation, technical feasibility, sponsor/API integration and submission communication.
7. **Run one persistent worker through it repeatedly.**
8. **Use Git worktrees for candidate memory/skill mutations.**
9. **Use CGE paired evaluation to promote changes.**
10. **Use one real opportunity as the external test.**
11. **When the assessor disagrees with reality, fork the World and improve the evaluator.**
12. **Only after this works, generalize to customer support, freelancing, research tasks, coding tasks, etc.**

If that works, the system has crossed the important threshold:

```text id="1bivyy"
Git isn't merely where the code lives.

Git represents the evolving
knowledge/capability objects themselves.

Hydra represents empirical knowledge
about their interactions.

Letta turns the strongest empirical
findings back into a better worker.
```

That is a substantially stronger architecture than “an agent with memory plus a database.” It gives us a reproducible experimental system in which **workers, memories, skills, worlds, assessors and schools all have lineage**, and real outcomes continuously determine which branches of that lineage are actually worth keeping.

[1]: https://www.letta.com/blog/context-repositories/?utm_source=chatgpt.com "Introducing Context Repositories: Git-based Memory for Coding Agents | Letta"
[2]: https://github.com/letta-ai/letta-code/blob/main/src/agent/prompts/letta.md?utm_source=chatgpt.com "letta-code/src/agent/prompts/letta.md at main · letta-ai/letta-code · GitHub"
[3]: https://github.com/letta-ai/letta-evals/blob/main/README.md?utm_source=chatgpt.com "letta-evals/README.md at main · letta-ai/letta-evals · GitHub"
[4]: https://github.com/hydra-db/hydradb/blob/main/architecture.md?utm_source=chatgpt.com "hydradb/architecture.md at main · hydra-db/hydradb · GitHub"
[5]: https://www.letta.com/blog/trajectory/?utm_source=chatgpt.com "Trajectory: A Standard Format for Agent Experience Data | Letta"
[6]: https://www.letta.com/blog/evaluating-memory-in-production-agents/?utm_source=chatgpt.com "Evaluating Memory in Production Agents | Letta"
[7]: https://github.com/letta-ai/letta-code/blob/main/src/agent/subagents/builtin/reflection.md?utm_source=chatgpt.com "letta-code/src/agent/subagents/builtin/reflection.md at main · letta-ai/letta-code · GitHub"
[8]: https://git-scm.com/docs/git-worktree.html?utm_source=chatgpt.com "Git - git-worktree Documentation"
[9]: https://git-scm.com/docs/git-notes "Git - git-notes Documentation"
[10]: https://git-scm.com/docs/git-bisect "Git - git-bisect Documentation"
[11]: https://git-scm.com/docs/git-verify-tag?utm_source=chatgpt.com "Git - git-verify-tag Documentation"
[12]: https://docs.github.com/en/actions/concepts/security/artifact-attestations?utm_source=chatgpt.com "Artifact attestations - GitHub Docs"
[13]: https://git-scm.com/docs/git-bundle "Git - git-bundle Documentation"
[14]: https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations?utm_source=chatgpt.com "Reusing workflow configurations - GitHub Docs"
[15]: https://github.com/letta-ai/letta-agent-sdk/blob/main/README.md?utm_source=chatgpt.com "letta-agent-sdk/README.md at main · letta-ai/letta-agent-sdk · GitHub"
