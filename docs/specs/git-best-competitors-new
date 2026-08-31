Yes. I would freeze the architecture now. The important discovery from this deeper pass is that we can delete a surprising amount of planned Moltwork/CGE engineering.

The strongest version is:

```text
                           ORACLE
                             │
                      economic demand
                             │
                             ▼
                        MOLTWORK
                 campaign + scientist layer
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
       LETTA              HARBOR              GEPA/
 persistent worker        WORLDS           OpenEvolve
 cognition/memory         evaluators       search/evolution
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                         WorkerRun
                             │
                     WorkerKit evidence
                             │
                       Trajectory
                             │
                       evaluation
                             │
                             ▼
                         HYDRADB
                   empirical experience graph
                             │
                             ▼
                         MOLTING
                 ┌───────────┼───────────┐
                 ▼           ▼           ▼
              Memory       Skill       Process
                 │           │           │
                 └───────────┼───────────┘
                             ▼
                         Git branch
                             │
                       evaluate again
                             │
                      promote / reject
```

And the really important philosophy is:

> **A WorkerRun is an online search process over ways of solving the job.**
>
> The Lab remembers which parts of that search worked. Future runs start from increasingly specific priors instead of starting from scratch.

That compounds indefinitely.

---

# Frozen decision 1: Letta owns the worker

Do not wrap Letta in our own pseudo-agent framework.

The new Agent SDK is explicitly designed around creating a persistent agent once and resuming that same identity across conversations, models and machines. `memfs: true` attaches the Git-backed memory system. It supports local, cloud and self-hosted backends through the same interface.

Letta Code already gives us:

| Need                       | Letta primitive                |
| -------------------------- | ------------------------------ |
| Persistent identity        | Agent                          |
| One task attempt           | Conversation/session           |
| Durable cognition          | MemFS                          |
| Versioned cognition        | Git                            |
| Procedures                 | Skills                         |
| Reflection                 | Dreaming/background reflection |
| Different worker roles     | Subagents                      |
| Harness modification       | Mods                           |
| Search prior conversations | Message/history search         |
| Portable transcript        | `@letta-ai/trajectory`         |
| Portable checkpoint        | `.af`                          |
| Shared skills              | Git-native Skills repositories |

Current Letta explicitly describes MemFS as Git-tracked context, Skills as dynamically loaded capabilities, and Mods as trusted local code able to register tools, lifecycle events, permission overlays, model providers and UI behavior. ([GitHub][1])

### Therefore our `WorkerVersion` should be mostly references

```yaml
worker_version: researcher-03/v12

letta:
  agent_id: agent_91df...
  memory_commit: 19fe287
  model: anthropic/...
  reasoning_effort: medium

skills:
  repo_commit: f8d271c

mods:
  moltwork: d192ea1

process:
  repo: process://technical-submission
  commit: 712bd29

parent: researcher-03/v11
```

No duplicated Moltwork memory system.

---

# Frozen decision 2: official Trajectory is our interchange format

This is stronger than I realized.

`@letta-ai/trajectory` now normalizes transcripts from:

```text
Letta Code
Claude Code
Codex
OpenCode
OpenHands
Gemini CLI
Cursor
Copilot CLI
Hermes
Deep Agents
...
```

into one deterministic format containing messages, reasoning, tool calls and tool results. ([GitHub][2])

This means Moltwork eventually doesn't even need to be Letta-exclusive at the evidence layer.

Letta can remain the canonical first worker, while:

```text
WorkerKit
    +
Trajectory
```

becomes the universal run evidence boundary.

That gives us:

```text
Letta worker    ─┐
Claude worker   ─┤
Codex worker    ─┤
OpenHands       ─┼─► Trajectory ─► Hydra
Hermes          ─┤
OpenCode        ─┘
```

Excellent for future experiments.

Don't create `mw.Trajectory`.

---

# Frozen decision 3: CGE should sit on Harbor rather than replacing Harbor

This is probably the largest architecture improvement from the research.

Harbor is already almost exactly the **open Git World ecosystem** we had just designed.

It supports arbitrary agents, custom shareable benchmarks/environments, containerized execution, huge parallel experiments, RL rollout generation and a public Harbor Hub. ([GitHub][3])

A Harbor task already looks like:

```text
task/
├── instruction.md
├── task.toml
├── environment/
│   └── Dockerfile
├── solution/
│   └── solve.sh
└── tests/
    └── test.sh
```

and supports arbitrary metadata, CPU/RAM/GPU constraints, network restrictions, multi-step tasks and separate verifier containers. ([GitHub][4])

That is basically `WorldPack`.

## So redefine CGE

CGE should **not** implement environments.

CGE becomes:

```text
CGE
=
scientific extensions to Harbor tasks
```

Specifically:

```text
ontology mapping
+
experiment treatments
+
paired baselines
+
secret suite policy
+
statistical promotion
+
fork/replay
+
WorldValidityClaims
+
CapabilityClaims
```

Conceptually:

```text
Harbor Task
    =
"Here is a reproducible world."

CGE Experiment
    =
"Here is the scientifically controlled
 comparison we're conducting in that world."
```

Much cleaner.

---

# Frozen decision 4: use Harbor Reward Kit for evaluators

This may eliminate most of the evaluator infrastructure we were planning.

Reward Kit already lets a verifier evaluate:

```text
programmatic checks
LLM judges
agent judges
files
commands
JSON
CSV
HTTP
images
trajectories
```

with multiple criteria evaluated independently and in parallel. It is intentionally designed for Git sharing and reuse. ([Harbor][5])

That's almost exactly our proposed assessor structure.

A Campaign-specific evaluator can be:

```text
tests/
├── hard-gates/
│   └── checks.py
│
├── requirements/
│   └── judge.toml
│
├── novelty/
│   └── judge.toml
│
├── technical/
│   └── judge.toml
│
├── sponsor-integration/
│   ├── checks.py
│   └── judge.toml
│
└── test.sh
```

and emit:

```json
{
  "hard_gates": 1.0,
  "requirements": 0.91,
  "novelty": 0.76,
  "technical": 0.88,
  "sponsor_integration": 0.93,
  "reward": 0.867
}
```

Harbor already supports multi-dimensional `reward.json`. ([GitHub][4])

### Important security rule

Always use:

```toml
[verifier]
environment_mode = "separate"
```

for serious hidden evaluation.

There has already been a documented Harbor issue where shared-mode multi-step verifiers could leak prior verifier files to the next agent step. ([GitHub][6])

So Moltwork's policy should be:

```text
research/dev worlds:
shared verifier allowed

promotion/secret worlds:
separate verifier mandatory
```

That's a useful CGE-level invariant.

---

# Frozen decision 5: Letta Evals and Harbor have different jobs

We should use both.

### Harbor

Best for:

```text
World execution
containerized tasks
real environments
hidden verifier
cross-harness comparisons
shareable public benchmarks
large-scale parallel execution
```

### Letta Evals

Best for:

```text
stateful-worker evaluation
memory behavior
Letta config comparisons
model comparisons
per-sample agent construction
memory workspace experiments
repeated trials
cached trajectory regrading
```

Letta Evals already gives:

```text
Dataset
 → Target
 → Extractor
 → Grader
 → Reward
 → Result
```

plus repeated runs, custom graders, custom agent factories, memory workspaces and Modal sandboxes. Most importantly, it can **re-grade saved trajectories without rerunning the worker**, which becomes critical when our assessors evolve.

So:

```text
CGE
├── Harbor backend
└── Letta-Evals backend
```

rather than CGE implementing either runner.

---

# Frozen decision 6: GEPA should be our first search/evolution engine

This is extremely aligned with the WorkerRun idea.

GEPA isn't merely prompt optimization anymore. Its current `optimize_anything` API explicitly supports:

```text
prompts
code
agent architectures
configurations
textual specs
```

and it uses full execution traces and diagnostic feedback to propose mutations rather than reducing everything to a scalar reward. ([GitHub][7])

Its loop is almost our loop:

```text
candidate
   ↓
execute
   ↓
evaluator
   ↓
full trace + diagnostic feedback
   ↓
reflection
   ↓
targeted mutation
   ↓
Pareto selection
   ↓
candidate
```

GEPA calls the rich diagnostic signal **Actionable Side Information**.

That's exactly what Moltwork's evaluator should produce.

Don't merely return:

```json
{"score": 0.72}
```

Return:

```json
{
  "score": 0.72,

  "diagnostics": {
    "requirements": "Strong.",
    "novelty": "Derivative of existing x402 routers.",
    "sponsor_depth":
      "Uses payment primitive but not settlement data.",
    "demo":
      "Architecture described but invocation evidence absent."
  }
}
```

Now GEPA can actually search intelligently.

---

# WorkerRun idea exploration therefore becomes GEPA-native

Imagine the first ideation stage.

Initial candidate:

```text
Idea A
```

Evaluator says:

```text
novelty=.61
sponsor_fit=.88
feasibility=.92

feedback:
"Strong feasibility but essentially a router.
Explore applications where payment state changes
the agent's reasoning rather than merely paying API calls."
```

GEPA proposes:

```text
Idea B
Idea C
```

Then another round.

Eventually:

```text
                     seed
                      │
               ┌──────┴──────┐
               ▼             ▼
              A1            A2
               │             │
          feedback       feedback
               │             │
         ┌─────┴────┐    ┌──┴─────┐
         ▼          ▼    ▼        ▼
        B1         B2   B3       B4
         │
       Pareto
      frontier
         │
        ...
```

That's considerably better than us implementing our own ideation evolutionary loop.

---

# Frozen decision 7: OpenEvolve handles the broader diversity/search problem

GEPA should not be the only optimizer.

OpenEvolve has mature machinery for:

```text
MAP-Elites
quality diversity
island populations
migration
Pareto/multi-objective evaluation
artifact feedback
diff mutations
stagnation recovery
```

and is designed explicitly around evolving code/algorithms against an evaluator. ([GitHub][8])

This maps beautifully onto CGE's old ideas.

Remember our:

```text
optimize
expand
diversify
compose
prove
```

decision tree?

OpenEvolve already handles much of:

```text
diversify
explore broad space
maintain niches
avoid premature convergence
```

### Use GEPA when

```text
we have rich evaluator feedback
and a fairly understandable artifact
to improve.
```

Examples:

```text
submission strategy
rubric
skill
process
system instruction
research procedure
assessor prompt
```

### Use OpenEvolve when

```text
the search space is broader
and diversity itself matters.
```

Examples:

```text
20 different hackathon architectures
different multi-agent processes
different workflow structures
code algorithms
different evaluator compositions
```

That gives Lab:

```text
optimizer:
  reflective → GEPA
  evolutionary-diverse → OpenEvolve
```

No need to write CGE's old 14 evolution recipes initially.

---

# Frozen decision 8: Agent Lightning is later-stage worker training

This one changed significantly **this month**.

Agent Lightning v1.0 was released/refactored in August 2026 and now trains agents **using their real harnesses** through a model proxy, keeping tools, context, control flow and environments intact. Its architecture is now essentially:

```text
Trainer
API Gateway
Rollout Controller
```

and their released coding pipeline reports a Qwen3.5-9B SWE-bench Verified gain from 41.8% to 56.4%. ([Microsoft GitHub][9])

This is strategically important for Moltwork.

Not now.

But eventually:

```text
Letta worker
   ↓
thousands of validated WorkerRuns
   ↓
CGE reward
   ↓
Agent Lightning
   ↓
actual model/policy training
```

Then Moltwork's progression is:

```text
Level 1
context learning

Level 2
memory learning

Level 3
skill/process learning

Level 4
harness/config learning

Level 5
weight/policy learning
```

We can reach 1–4 without GPUs.

Agent Lightning gives us an existing path to 5.

Excellent long-term integration.

---

# Frozen decision 9: Trace2Skill should become the default post-run skill candidate generator

This is an extremely direct match.

Trace2Skill takes a pool of execution trajectories, analyzes successes and failures in parallel, generates trajectory-local lessons, then hierarchically consolidates them into a conflict-free skill directory. ([GitHub][10])

That is almost literally our **Molter**.

Instead of writing:

```text
mw/lab/synthesis.py
```

we should have:

```text
Trajectory pool
      ↓
Trace2Skill adapter
      ↓
candidate skill tree
      ↓
Git worktree
      ↓
CGE evaluation
      ↓
promote/reject
```

And it distinguishes:

```text
skill deepening
```

from:

```text
skill creation from scratch
```

which is useful.

### Important: don't let Trace2Skill write production directly

Use:

```text
runs
 ↓
Trace2Skill
 ↓
skills-candidate/E91
 ↓
paired hidden evaluation
 ↓
merge
```

not:

```text
runs
 ↓
Trace2Skill
 ↓
production
```

---

# Frozen decision 10: Letta dreaming becomes another treatment

Letta itself already has background reflection agents maintaining memory between turns, and its reflection instructions explicitly differentiate durable memory from reusable Skills. ([GitHub][11])

So do not recreate sleep-time learning.

Instead test:

```text
T0 no post-run learning

T1 Letta dreaming

T2 Trace2Skill

T3 GEPA memory patch

T4 dreaming + Trace2Skill

T5 Hydra-guided reflection
```

Then find out what actually works for each task family.

Eventually Hydra might say:

```text
competition.idea_generation
    Trace2Skill > dreaming

customer_support
    dreaming > Trace2Skill

coding.debugging
    Trace2Skill + GEPA best
```

That's where specialization becomes empirical rather than ideological.

---

# Frozen decision 11: A-MEM / Memory-R1 are research arms, not architecture

A-MEM dynamically creates structured notes and links memories as a graph-like Zettelkasten system. ([GitHub][12])

Memory-R1 goes further and trains a memory manager to choose:

```text
ADD
UPDATE
DELETE
NOOP
```

plus a separate answer-memory distillation step. ([GitHub][13])

These are useful ideas.

But don't put either underneath Letta.

Instead use them to inspire experiments like:

```text
memory mutation policy:

native-letta
ace-delta
A-MEM linking
Memory-R1 CRUD
```

Same worker/world.

Measure them.

---

# Frozen decision 12: Letta Skills already prove our Git-asset thesis

Look at Letta's own public Skills repository.

It describes itself as:

> a community knowledge base where AI agents learn from each other's experience.

Skills are plain Git directories containing:

```text
SKILL.md
references/
scripts/
assets/
```

and agents dynamically discover/install them. ([GitHub][14])

That's extraordinarily close to Moltwork.

So our innovation isn't:

> “Agents should share skills on Git.”

Letta is already doing it.

Our addition is:

> **Skills should accumulate empirical capability evidence from WorkerRuns.**

Meaning:

```text
github.com/foo/sponsor-research-skill
             │
             │
             ▼
        SkillVersion
             │
       Hydra evidence
             │
       ┌─────┴───────┐
       ▼             ▼
Experiment E7    Experiment E19
+8% score         +11% score
       │             │
       └──────┬──────┘
              ▼
       real campaign win
```

That's the Moltwork layer.

---

# Frozen decision 13: `.af` is basically the eventual worker asset format

Agent File already serializes a Letta stateful agent including:

```text
model configuration
message history
system prompt
memory blocks
tool rules
tool definitions
environment configuration
```

and is explicitly intended for checkpointing, sharing and version control. ([GitHub][15])

They even already have a GitHub directory where people submit trained agents.

So again:

**do not create a Moltwork agent bundle format.**

Instead later:

```text
WorkerAsset
=
.af
+
Git refs
+
CapabilityClaims
+
WorkerKit receipts
+
Hydra evidence refs
```

Moltwork adds the empirical/economic certificate around the open format.

---

# The technical WorkerRun can now be frozen

I would define the actual Campaign pipeline like this.

```text
══════════════════════════════════════════════
0. INGEST OPPORTUNITY
══════════════════════════════════════════════

Oracle opportunity
        ↓
ontology mapping
        ↓
Campaign Git repo/branch


══════════════════════════════════════════════
1. BUILD SUCCESS MODEL
══════════════════════════════════════════════

Letta research agent
        ↓
official rules
docs
past winners
prior Hydra campaigns
        ↓
success-model.yaml
        ↓
public strategy
+
hidden assessor specification


══════════════════════════════════════════════
2. COMPILE WORLD
══════════════════════════════════════════════

success-model
        ↓
Harbor task(s)
        ↓
RewardKit verifier

requirements
novelty
technical
evidence
presentation
domain-specific criteria


══════════════════════════════════════════════
3. RECALL EXPERIENCE
══════════════════════════════════════════════

Hydra

similar:
opportunities
worlds
processes
workers
skills
assessors
outcomes

        ↓
LabBrief


══════════════════════════════════════════════
4. DECIDE SEARCH MODE
══════════════════════════════════════════════

winning formula exists?
       │
   ┌───┴───┐
   yes     no
    │       │
 exploit  explore
    │       │
 process   GEPA
          OpenEvolve
          research


══════════════════════════════════════════════
5. IDEATION SEARCH
══════════════════════════════════════════════

N cheap candidates

GEPA/OpenEvolve
      ↓
RewardKit scores
      ↓
diagnostic feedback
      ↓
successive halving

20
 ↓
8
 ↓
3
 ↓
1


══════════════════════════════════════════════
6. EXECUTION
══════════════════════════════════════════════

persistent Letta Worker
fresh conversation

MemFS
Skills
LabBrief
selected process

        ↓
artifact


══════════════════════════════════════════════
7. ITERATIVE REVIEW
══════════════════════════════════════════════

artifact
  ↓
Harbor/RewardKit
  ↓
diagnostics
  ↓
repair
  ↓
re-grade
  ↓
repair

until:
threshold
deadline
or marginal EV says stop


══════════════════════════════════════════════
8. FREEZE RUN
══════════════════════════════════════════════

Git commits
+
WorkerKit receipt
+
@letta-ai/trajectory
+
WorkerVersion
+
WorldVersion
+
AssessorVersion
+
artifact digest


══════════════════════════════════════════════
9. EXTERNAL SUBMISSION
══════════════════════════════════════════════

real opportunity
       ↓
accepted / rejected
rank
judge comments
revenue


══════════════════════════════════════════════
10. HYDRA PROJECTION
══════════════════════════════════════════════

project every relationship
into empirical graph


══════════════════════════════════════════════
11. MOLT
══════════════════════════════════════════════

Trajectory pool
  │
  ├─ memory candidates
  ├─ Trace2Skill
  ├─ GEPA process mutation
  ├─ evaluator improvement
  ├─ world improvement
  └─ reusable code/assets


══════════════════════════════════════════════
12. TEST MOLTS
══════════════════════════════════════════════

Git worktrees
       ↓
control vs candidate
       ↓
Harbor / Letta Evals
       ↓
CGE paired statistics


══════════════════════════════════════════════
13. PROMOTE
══════════════════════════════════════════════

validated:
merge + tag

not validated:
discard branch
retain negative evidence in Hydra


══════════════════════════════════════════════
14. NEXT OPPORTUNITY
══════════════════════════════════════════════

repeat from a stronger prior
```

That is the frozen loop.

---

# The search hierarchy is one of the most important details

Your observation about becoming more specific is exactly right.

At the start Hydra knows:

```text
technical submissions generally
```

After some data:

```text
hackathon submissions
```

Then:

```text
crypto hackathons
```

Then:

```text
Ethereum sponsor tracks
```

Then:

```text
TEE/privacy sponsor tracks
```

Then possibly:

```text
Phala sponsor tracks judged on
actual confidential execution
```

So experience is hierarchical:

```text
global prior
  ↓
task-family prior
  ↓
domain prior
  ↓
market prior
  ↓
specific opportunity-family prior
```

The Lab should select the **most specific prior with enough evidence**.

For example:

```text
Phala submissions
n=1
→ weak evidence

TEE hackathons
n=7
→ useful

crypto hackathons
n=31
→ strong

all technical competitions
n=108
→ very strong but less specific
```

Combine them hierarchically rather than throwing away general knowledge.

That is a place where Hydra + shrinkage statistics from CGE1 become valuable.

---

# We should formalize the “search object”

Every exploration should mutate a typed thing.

```yaml
SearchSpec:

  target:
    type: idea
    # idea | process | memory | skill |
    # worker-config | assessor | world | code

  objective:
    world_ref: ...
    assessor_ref: ...

  optimizer:
    kind: gepa
    # gepa | openevolve | random | human

  budget:
    max_candidates: 20
    max_cost_usd: 2.00

  constraints:
    model_fixed: true
    worker_fixed: true

  dimensions:
    - novelty
    - feasibility
    - sponsor_fit
```

Now Hydra records the search itself.

That's valuable because later it can answer:

> Which *search strategies* work?

---

# Hydra's graph should include search lineage, not just worker lineage

This is new and important.

```text
Search
  │
  ├─[:SEEDED_WITH]→ Candidate A
  │
  ├─[:MUTATED_TO]→ Candidate B
  │
  ├─[:MUTATED_TO]→ Candidate C
  │
  └─[:SELECTED]→ Candidate D
```

And:

```text
Candidate D
  -[:BECAME]->
Artifact
  -[:SUBMITTED_TO]->
Opportunity
  -[:RESULTED_IN]->
Win
```

Now months later:

```text
Which ideation strategy produced
our economically successful ideas?
```

That's far richer than merely remembering the final submission.

---

# We should retain failures at every layer

This is central.

```text
bad ideas
bad process mutations
bad memory commits
bad skills
bad worlds
bad assessors
bad worker configs
```

should all survive as evidence.

But not as active Letta memory.

Hydra gets:

```text
Candidate C17
rejected because:
high novelty
low feasibility
```

Letta gets distilled:

```text
In this task family, novelty without a
credible implementation path has repeatedly
underperformed.
```

That is a critical difference.

---

# The strongest new split: online optimization vs offline learning

I would make this explicit.

### During the Campaign

Optimize the **artifact**.

```text
ideas
architecture
implementation
submission
```

Fast loop.

### After Campaign

Optimize the **worker**.

```text
memory
skills
process
harness
world
assessor
```

Slow scientific loop.

Never mix them too much.

Otherwise a worker changes its own cognition halfway through a run and you lose experimental provenance.

So:

```text
WorkerVersion frozen
for Campaign run

Artifact allowed to evolve
during Campaign
```

Then post-run:

```text
create WorkerVersion candidate
```

This is a very important invariant.

---

# The same applies to the assessor

During Campaign:

```text
AssessorVersion fixed
```

You can iteratively improve submission against it.

After real outcome:

```text
Assessor wrong?
   ↓
fork assessor
   ↓
re-grade cached trajectories
   ↓
validate against historical outcomes
   ↓
new AssessorVersion
```

This prevents:

```text
worker changes
+
exam changes
+
score improves
```

and us pretending we learned something.

---

# What not to build now

This is probably as important as what to build.

| Do NOT build                     | Use                           |
| -------------------------------- | ----------------------------- |
| New agent runtime                | Letta                         |
| New memory DB                    | MemFS                         |
| New skill format                 | Agent Skills                  |
| New agent bundle                 | `.af`                         |
| New trajectory schema            | Letta Trajectory              |
| New eval runner                  | Letta Evals                   |
| New world container framework    | Harbor                        |
| New verifier framework           | Reward Kit                    |
| New prompt/process optimizer     | GEPA                          |
| New broad evolutionary optimizer | OpenEvolve                    |
| New skill distillation engine    | Trace2Skill                   |
| New RL trainer                   | Agent Lightning               |
| New graph DB                     | HydraDB                       |
| New sandbox service              | Harbor providers / Modal etc. |

What remains genuinely Moltwork/CGE:

```text
Oracle ontology integration

Campaign abstraction

SuccessModel compiler

search policy:
exploit vs explore vs expand

CGE experimental semantics

Git version/branch conventions

WorkerKit evidence

Hydra ontology/projectors

hierarchical capability estimates

post-run Molter

promotion policy

economic allocation

WorldValidityClaim

CapabilityClaim
```

That is a much smaller and more defensible core.

---

# The first serious repo layout

I would now make the ecosystem roughly:

```text
prx0r/mw
  economic Lab
  Oracle client
  Campaign manager
  Hydra projector
  Letta integration
  Molter
  asset inventory

prx0r/cge
  experimental semantics
  Harbor adapter
  Letta-Evals adapter
  paired statistics
  search specs
  promotion
  claims
  ontology bindings

private/lab-researcher
  Letta MemFS Git repository

private/worlds
  custom Harbor tasks

private/schools
  curriculum/world collections

private/campaigns
  actual economic work

HydraDB
  disposable/rebuildable empirical graph
```

And upstream dependencies:

```text
letta-ai/*
harbor-framework/*
gepa-ai/gepa
algorithmicsuperintelligence/openevolve
Qwen-Applications/Trace2Skill
microsoft/agent-lightning   # later
```

---

# The first checkpoint is now even clearer

Don't test generic benchmark performance yet.

Build enough plumbing for one **real submission Campaign** to create this history:

```text
Opportunity
  ↓
SuccessModel v1
  ↓
Idea World v1
  ↓
20 ideas
  ↓
GEPA search
  ↓
3 finalists
  ↓
selected idea
  ↓
Letta Worker v1
  ↓
build
  ↓
RewardKit review
  ↓
repair
  ↓
submission
  ↓
real result
  ↓
Hydra
  ↓
Trace2Skill / memory candidates
  ↓
Process v2
  ↓
World v2
  ↓
next Campaign
```

Then the second Campaign should visibly start differently because Hydra can say:

```text
Last time:

GEPA branch family B dominated idea quality.

Process P3 produced the best artifact.

Technical review caught 4 issues.

Presentation review had little effect.

Skill S9 appears useful but only n=1.

Assessor overestimated novelty.

Start here.
```

That is the first moment where Moltwork has genuinely **learned how to work**, rather than simply remembering a previous chat.

And from there the granularity can recurse indefinitely:

```text
how to win submissions
 ↓
how to win hackathons
 ↓
how to win crypto hackathons
 ↓
how to win sponsor tracks
 ↓
how to win TEE sponsor tracks
 ↓
how researcher-v12 specifically wins TEE tracks
```

while still backing off to broader evidence when the specific sample size is too small.

That hierarchical, empirically grounded accumulation is the part I would now treat as the actual Moltwork thesis.

[1]: https://github.com/letta-ai/letta-code/blob/main/README.md?utm_source=chatgpt.com "letta-code/README.md at main · letta-ai/letta-code · GitHub"
[2]: https://github.com/letta-ai/trajectory/blob/main/README.md?utm_source=chatgpt.com "trajectory/README.md at main · letta-ai/trajectory · GitHub"
[3]: https://github.com/harbor-framework/harbor?utm_source=chatgpt.com "GitHub - harbor-framework/harbor: Harbor is a framework for running agent evaluations and creating and using RL environments. · GitHub"
[4]: https://github.com/harbor-framework/harbor/blob/main/docs/content/docs/tasks/index.mdx?utm_source=chatgpt.com "harbor/docs/content/docs/tasks/index.mdx at main · harbor-framework/harbor · GitHub"
[5]: https://www.harborframework.com/docs/rewardkit?utm_source=chatgpt.com "Reward Kit"
[6]: https://github.com/harbor-framework/harbor/issues/1960?utm_source=chatgpt.com "Multi-step SHARED verifier mode leaks `/tests` and `/logs/verifier` into the next step's agent phase · Issue #1960 · harbor-framework/harbor · GitHub"
[7]: https://github.com/gepa-ai/gepa?utm_source=chatgpt.com "GitHub - gepa-ai/gepa: Optimize prompts, code, and more with AI-powered Reflective Text Evolution · GitHub"
[8]: https://github.com/algorithmicsuperintelligence/openevolve?utm_source=chatgpt.com "GitHub - algorithmicsuperintelligence/openevolve: Open-source implementation of AlphaEvolve · GitHub"
[9]: https://microsoft.github.io/agent-lightning/latest/?utm_source=chatgpt.com "Agent Lightning v1.0"
[10]: https://github.com/Qwen-Applications/Trace2Skill?utm_source=chatgpt.com "GitHub - Qwen-Applications/Trace2Skill: Official codebase of the paper -- Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills · GitHub"
[11]: https://github.com/letta-ai/letta-code/blob/main/src/agent/prompts/letta.md?utm_source=chatgpt.com "letta-code/src/agent/prompts/letta.md at main · letta-ai/letta-code · GitHub"
[12]: https://github.com/agiresearch/A-mem?utm_source=chatgpt.com "GitHub - agiresearch/A-mem: A-MEM: Agentic Memory for LLM Agents · GitHub"
[13]: https://github.com/yansikuan/memory-r1/?utm_source=chatgpt.com "GitHub - yansikuan/memory-r1 · GitHub"
[14]: https://github.com/letta-ai/skills/blob/main/README.md?utm_source=chatgpt.com "skills/README.md at main · letta-ai/skills · GitHub"
[15]: https://github.com/letta-ai/agent-file?utm_source=chatgpt.com "GitHub - letta-ai/agent-file: Agent File (.af): An open file format for serializing stateful AI agents with persistent memory and behavior. Share, checkpoint, and version control agents across compatible frameworks. · GitHub"
