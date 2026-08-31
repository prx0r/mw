Yes. **Harbor is much closer to the missing execution substrate than I realized.** The striking part is not just that it runs benchmarks; it is already converging on many of the primitives we independently arrived at: Git-addressed tasks, Git skills, exact run locks, portable trajectories, isolated verifiers, artifact capture, regrading, multi-step continual-learning tasks, arbitrary agents, remote rollouts, RL, and a registry for sharing Worlds. ([Harbor][1])

I would now frame the stack like this:

```text
                    ORACLE
              what work matters?
                    │
                    ▼
                 MOLTWORK
       what should we try/learn next?
                    │
        ┌───────────┼────────────┐
        ▼           ▼            ▼
      LETTA       HARBOR        CGE
     worker       world       scientist
   cognition    execution     semantics
        │           │            │
        └───────────┼────────────┘
                    ▼
                WORKERRUN
                    │
              evidence/results
                    ▼
                 HYDRADB
          what actually happened?
                    │
                    ▼
                  GIT
      what versions do we keep?
```

The key change is:

> **Harbor should probably become Moltwork's default World execution layer. CGE becomes the scientific protocol above Harbor, rather than implementing its own environments.**

## Why Harbor is such a good fit

A Harbor task is already essentially the concrete version of our `WorldPack`:

```text
Task
├── instruction
├── sandbox environment
├── resources
├── agent constraints
├── verifier
└── reward
```

Tasks can declare CPU/RAM/storage/GPU needs, network access or allowlists, MCP servers, separate verifier environments and arbitrary metadata. ([Harbor][2])

A dataset is then a versioned composition of tasks. Crucially, Harbor supports:

```text
local dataset
registry dataset
Git repository dataset
```

and Git repos can be revision-pinned. Published datasets themselves point to tasks by SHA-256 digest. ([Harbor][3])

That is extremely close to:

```text
CGE School
=
versioned collection of Worlds
```

We don't need to invent the packaging layer.

---

# 1. The Git support is deeper than simply “the task lives on GitHub”

This is one of the biggest synergies.

Harbor already supports **Git skills**:

```bash
harbor run \
  --skill org/repo@v1.2 \
  ...
```

It resolves the source to an exact commit and records in the job lock:

```text
skill name
source
content digest
git URL
resolved commit SHA
```

([Harbor][4])

That's essentially our proposed provenance scheme already implemented.

A locked Harbor trial can therefore say:

```yaml
subject:
  worker: researcher-03/v8

world:
  task_digest: sha256:91fa...

skills:
  - repo: org/sponsor-research
    commit: 72bd19
    digest: sha256:...

agent:
  version: ...

model:
  ...

environment:
  ...
```

So I would **use Harbor's `lock.json` as one execution input manifest**, and have WorkerKit add the economic/cryptographic evidence Harbor doesn't know about.

Do not create another parallel lock format unless necessary.

---

# 2. Harbor + Letta solves an interesting tension

Harbor expects:

> give me an agent and a reproducible environment.

Letta expects:

> give me a persistent identity that continues learning across tasks.

Those are complementary.

The important integration is:

```text
                     PERSISTENT
                       LETTA
                       AGENT
                         │
                         │ stable identity
                         ▼
                  Harbor Adapter
                         │
      ┌──────────────────┼──────────────────┐
      ▼                  ▼                  ▼
  World W1           World W2           World W3
 fresh session      fresh session      fresh session
      │                  │                  │
      └──────────────────┼──────────────────┘
                         ▼
                 persistent memory
```

The environment is ephemeral.

The worker identity is not.

That's exactly what we wanted.

Harbor supports custom agent integrations through its own `BaseAgent`/installed-agent interfaces, and Hosted Harbor also supports custom ACP agents sourced directly from GitHub with a pinned repository commit. ([Harbor][5])

So we'd make:

```text
harbor-letta/
```

very thin.

Its job is basically:

```text
Harbor instruction
      ↓
create/resume appropriate Letta session
      ↓
give Letta access to Harbor environment
      ↓
run
      ↓
export trajectory/session refs
```

The persistent Letta agent stays outside the disposable benchmark environment.

---

# 3. Harbor multi-step tasks are almost made for Letta memory research

This feature is particularly relevant.

Harbor lets a task consist of sequential steps with:

* persistent shared environment;
* separate instruction per step;
* separate verifier per step;
* step-specific setup;
* per-step rewards;
* early stopping. ([Harbor][6])

Even more importantly, the run can switch between:

```text
fresh agent context each step
```

and:

```text
resume same agent trajectory between steps
```

([Harbor][6])

That means we immediately get memory experiments like:

```text
World: support-agent-learning

STEP 1
customer teaches policy correction

        ↓

STEP 2
unrelated interaction

        ↓

STEP 3
situation requiring corrected policy

        ↓

STEP 4
contradictory outdated instruction

        ↓

STEP 5
transfer problem
```

Treatments:

```text
A fresh context every step

B conversation continuity

C Letta persistent memory

D Letta + dreaming

E Letta + validated Skill

F Letta + Hydra Lab context
```

Same Harbor World.

This is an excellent successor to our CG memory experiments.

---

# 4. Harbor has a second trajectory format we should deliberately keep

This was a subtle discovery.

Harbor has **ATIF**, the Agent Trajectory Interchange Format. It is high fidelity and designed for:

```text
benchmarking
debugging
replay
SFT
RL
```

It contains token/cost metrics, structured tool payloads, environment observations, subagent trajectories and even RL fields. Recent versions include exact prompt/completion token IDs specifically to avoid RL retokenization drift. ([GitHub][7])

Letta's `trajectory` project explicitly discusses Harbor ATIF and says the two formats have different goals:

**Harbor ATIF**

```text
full fidelity
benchmark/replay/training
```

**Letta Trajectory**

```text
token-efficient
agent-readable
memory formation/dreaming
```

Letta reports roughly ~5× token reduction in sampled sessions from its compact representation. ([Letta][8])

This is fantastic architecture.

Don't choose one.

Use both:

```text
                  WorkerRun
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      Harbor ATIF          Letta Trajectory
          │                     │
    scientific record       learning record
    full fidelity           compressed
          │                     │
          ▼                     ▼
       HYDRADB              LETTA/MOLTER
```

WorkerKit retains factual receipts.

This gives us three deliberately different representations of one run.

---

# 5. Harbor's trajectory loading opens up cross-agent experimental inheritance

Harbor can already load a prior trajectory into another run.

Native trajectories can resume the same harness losslessly.

More interestingly, an **ATIF trajectory from one agent can seed another agent**, with Harbor translating it into the receiving agent's session representation. ([Harbor][9])

Imagine:

```text
Claude Code wins World X
       │
       ▼
ATIF trajectory
       │
       ▼
Letta researcher studies/resumes context
       │
       ▼
attempts World X variant
```

Or:

```text
worker A
expert trajectory
      ↓
worker B
student
```

Now CGE's old A–F transmission experiments become practical:

```text
A no experience

B final solution only

C compact Letta trajectory

D full ATIF

E generated Skill

F persistent Letta memory
```

Then measure transfer.

That's exactly the kind of science we wanted.

---

# 6. Regrade is probably one of Harbor's most important features for us

This is a big one.

Harbor can take a completed trial and **run a newer verifier against the old artifacts without running the agent again**. It preserves the original agent configuration/cost/identity, produces a derived trial and records provenance back to the source trial. ([Harbor][10])

So:

```text
300 historical WorkerRuns

Assessor v1
      │
      ▼
we discover v1 underweights feasibility
      │
      ▼
Assessor v2
      │
      ▼
HARBOR REGRADE

same 300 outputs
zero new worker inference
      │
      ▼
compare v1 vs v2
against actual outcomes
```

This is exactly how the **World itself evolves**.

And Harbor essentially describes a regrade as a fork of a past trial.

That's eerily aligned with CGE.

---

# 7. Artifact collection solves another piece of WorkerKit

Every trial can automatically preserve `/logs/artifacts/`, or configured arbitrary paths such as:

```text
/app/final-submission.md
/workspace/repo/
/data/research.json
/logs/screenshots/
```

across local and many cloud sandbox providers. ([Harbor][11])

Therefore a WorkerRun naturally produces:

```text
Harbor trial
├── lock.json
├── result.json
├── agent/
│   ├── trajectory.json
│   └── sessions/
├── verifier/
│   └── ...
└── artifacts/
    ├── source/
    ├── submission/
    ├── research/
    └── evidence/
```

This is almost exactly our desired run archive.

WorkerKit can hash and attest this instead of implementing another artifact gathering system.

---

# 8. Reward Kit is even more important than I initially thought

Reward Kit doesn't just look at the final text.

It can inspect:

```text
workspace
files
commands
JSON
CSV
HTTP endpoints
images
documents
trajectory
```

and it supports LLM **or full agent judges**, with independent criteria executed in parallel. ([Harbor][12])

So our hackathon evaluator can become:

```text
tests/
├── eligibility/
│   └── deterministic.py
│
├── sponsor-usage/
│   ├── invocation.py
│   └── judge.toml
│
├── novelty/
│   └── judge.toml
│
├── feasibility/
│   └── judge.toml
│
├── evidence/
│   └── source-check.py
│
├── code-quality/
│   └── judge.toml
│
├── presentation/
│   └── judge.toml
│
└── trajectory-quality/
    └── process.py
```

That last category is interesting:

> We can score not merely **what** the agent produced, but **how it worked**.

For instance:

```text
Did it inspect requirements before building?

Did it verify API behavior?

Did it test its implementation?

Did it ignore reviewer warnings?

Did it repeatedly make the same failed move?
```

That could become extremely valuable for post-run molting.

---

# 9. Evaluators themselves become composable Git assets

Reward Kit's own design emphasizes criteria as simple Git-shareable directories. ([Harbor][13])

This means the actual marketplace object may not need to be an entire World.

You could have:

```text
github.com/alice/evals/
  sponsor-depth/
  technical-feasibility/
  source-quality/
  UX-quality/
  novelty/
```

Then a Campaign builds:

```yaml
assessor:
  criteria:
    - git://alice/sponsor-depth@abc
    - git://bob/technical-feasibility@123
    - local://phala-specific
```

The composition itself can be another versioned asset.

That gives an evaluator supply chain.

---

# 10. Harbor already has a real “World marketplace”

The Harbor registry supports both public and private tasks/datasets. Packages can have tags and immutable content digests; datasets can compose locally developed tasks and already-published ones. ([Harbor][14])

Harbor Hub currently includes things such as:

* Frontier-Bench;
* Terminal-Bench;
* Harbor Index;
* SWE-bench;
* Android benchmarks. ([Harbor Hub][15])

So CGE doesn't need to make:

> “GitHub for benchmarks.”

Harbor is explicitly trying to become that.

Their roadmap literally says they want a hosted storage layer described as **“PyPI for Harbor tasks”**, including versioning, sharing, metrics, and private registries.

This changes Moltwork's opportunity.

Don't compete.

**Add economic/capability semantics to that ecosystem.**

---

# 11. The Oracle ontology is what Harbor lacks

Harbor metadata can be arbitrary, but Harbor isn't trying to answer:

> Which benchmark is economically relevant to this worker right now?

That's our layer.

We could define a tiny `moltwork` metadata convention inside `task.toml`:

```toml
[metadata.moltwork]
ontology_version = "1"

task_family = "competition.idea_generation"

capabilities = [
  "requirements.extract",
  "research.web",
  "idea.generate",
  "technical.feasibility"
]

economic_surfaces = [
  "hackathon",
  "bounty"
]

evaluation_type = "subjective-rubric"

difficulty = 0.74
```

Then Oracle says:

```text
task family demand ↑
competition.idea_generation
```

and Moltwork can search Harbor/Git:

```text
find Worlds covering:
competition.idea_generation
```

That's a real missing layer.

---

# 12. CGE then becomes much smaller and much stronger

Old CGE:

```text
environment
runner
agent
scheduler
evaluator
memory
evolution
science
graph
```

New CGE:

```text
CGE
├── ontology/
├── experiments/
├── treatments/
├── statistics/
├── search/
├── claims/
└── harbor/
```

Harbor executes.

CGE asks scientific questions.

For example:

```yaml
experiment:
  hypothesis:
    "Requirements extraction improves submission quality."

  world:
    harbor: moltwork/hackathon-submission@v3

  control:
    worker: researcher/v8

  treatment:
    worker: researcher/v8
    skill: requirements-extraction@91af

  controls:
    same_model: true
    same_budget: true
    same_world: true
    same_assessor: true

  promotion:
    paired_bootstrap: true
    min_delta: 0.05
    no_regression:
      requirements: true
      cost: 0.15
```

CGE compiles that into Harbor jobs.

That's enough.

---

# 13. Multi-container Worlds open some wild possibilities

Harbor supports Docker Compose sidecars, including MCP servers and other services. ([Harbor][16])

So a World can simulate an actual workplace:

```text
              Harbor World

 ┌────────────────────────────────────┐
 │                                    │
 │ Letta worker                       │
 │      │                             │
 │      ├── CRM MCP                   │
 │      ├── support database          │
 │      ├── fake Stripe               │
 │      ├── email server              │
 │      ├── customer simulator        │
 │      └── company docs              │
 │                                    │
 │ hidden verifier                    │
 └────────────────────────────────────┘
```

Now your `customer-support-school` isn't just some prompts.

It's a **miniature synthetic company**.

This is where the School concept gets serious.

---

# 14. Simulated users + multi-turn tasks could create proper job Schools

Harbor Cookbook already has a `simulated-user` recipe where an agent must discover requirements through interaction rather than receiving everything upfront. ([GitHub][17])

Combine that with multi-step tasks:

```text
customer-support school

DAY 1
normal customer

DAY 2
policy correction

DAY 3
angry customer

DAY 4
ambiguous refund

DAY 5
fraud attempt

DAY 6
service outage

DAY 7
new policy superseding old policy
```

The same persistent Letta worker progresses.

Now we test:

```text
policy learning
memory hygiene
conflict resolution
escalation judgment
transfer
customer satisfaction
```

This becomes an actual **agent apprenticeship**.

---

# 15. The production → World direction is already on Harbor's roadmap

This is significant.

Harbor explicitly lists:

> **Task creation tooling — Capture production agent state and map it to tasks.**

on its roadmap.

This is precisely where Moltwork is headed:

```text
real WorkerRun fails
       ↓
capture failure state
       ↓
minimize/reproduce
       ↓
turn into Harbor World
       ↓
future workers train/test against it
```

This can become automatic.

Example:

```text
real support worker failed
because user had:
subscription paused
+
refund requested
+
legacy billing plan
```

Post-run Molter says:

```text
novel failure case
```

and proposes:

```text
new Harbor scenario:
legacy-paused-refund
```

Now every future support worker must pass it.

That is **production experience becoming curriculum**.

---

# 16. Failed real work can literally grow the benchmark

This creates a powerful loop:

```text
          REALITY
            │
         failure
            │
            ▼
      reproducible World
            │
            ▼
      Harbor registry
            │
            ▼
         training
            │
            ▼
     stronger workers
            │
            ▼
          REALITY
```

If you squint, this is how mature engineering teams work already:

```text
production bug
→ regression test
→ fix
→ never regress
```

Moltwork generalizes that concept:

> **economic failure → agent regression test.**

That's an extremely powerful framing.

---

# 17. Git Schools become “test suites + curricula + skills”

Harbor already lets Git repositories inject `SKILL.md` skill directories into runs, with provenance locking. ([Harbor][4])

So a School repository might literally be:

```text
support-school/
├── skills/
│   ├── refund-policy/
│   └── escalation/
│
├── tasks/
│   ├── refund-basic/
│   ├── refund-ambiguous/
│   ├── angry-user/
│   └── fraud/
│
├── dataset.toml
│
├── curriculum.yaml
│
└── claims/
```

Run without the Skills:

```text
baseline
```

Train/add Skill.

Run held-out tasks.

You immediately have measurable teaching value.

---

# 18. Worlds can also be composed into role-specific exams

Harbor datasets can combine tasks from different benchmarks. ([Harbor][3])

So Hydra can discover that a worker role requires:

```text
Research Agent certification

20% source verification
20% web research
15% summarization
15% technical analysis
20% idea generation
10% writing
```

CGE builds:

```text
research-agent-certification-v4
```

from six different Harbor datasets.

Then:

```text
Worker Asset
researcher-v19

validated on:
research-agent-certification-v4
score=.83
```

Now “hire this agent” has some actual meaning.

---

# 19. Harbor Index shows another thing we should steal: World selection itself needs science

Harbor Index was distilled from **more than 6,000 candidate tasks** to roughly 80 high-signal tasks using repeated model runs, automated broken-task identification, human audits, and reward-hacking supervision. ([GitHub][18])

That's a major lesson.

A School should not become:

```text
800 random mediocre test cases
```

Instead:

```text
candidate Worlds
      ↓
run worker population
      ↓
remove:
broken
ambiguous
redundant
too easy
unreliable
hackable
      ↓
keep discriminative Worlds
```

Now benchmarks themselves evolve under selection pressure.

That brings us right back to CG's co-evolution thesis.

---

# 20. Regrade + real outcomes gives us evaluator evolution basically for free

Consider:

```text
Assessor A
predicts:
A > B > C
```

Real competition:

```text
B > C > A
```

We create:

```text
Assessor B
```

Then Harbor:

```text
harbor job regrade historical-runs \
   with Assessor B
```

No workers rerun. ([Harbor][10])

Hydra calculates:

```text
A rank correlation: .42
B rank correlation: .73
```

Promote B.

This is *exactly* how the marketplace can eventually rank evaluators.

---

# 21. Harbor's separate verifier environment is our pre-TEE evaluator architecture

This matters for the TEE roadmap.

Harbor supports a verifier in a **different container** from the agent. It only receives explicitly collected artifacts. Separate verifier mode is already recommended and is expected to become the default. ([Harbor][10])

That's exactly the abstraction we need before TEE:

```text
Agent environment
      │
explicit artifacts
      ▼
Verifier environment
```

Later replace:

```text
ordinary verifier sandbox
```

with:

```text
Phala confidential verifier
```

without changing the conceptual World interface.

So TEE becomes a provider/deployment implementation of the existing verifier boundary—not a special parallel evaluator system.

Much cleaner.

---

# 22. Remote rollouts mean Lab experiments can scale without us building fleet infrastructure

Harbor integrates with many sandbox providers—Daytona, Modal, E2B, Runloop, Tensorlake, Blaxel, EC2, Beam, Hyperbrowser and others—and recommends horizontal scaling because agent experiments are usually I/O bound. ([Harbor][19])

Hosted jobs already support large concurrency settings; Harbor's documented config accepts up to 1,000 concurrent trials. ([Harbor][20])

Therefore our scientist can eventually say:

```text
experiment budget: $20

WorkerVersions:
8

Worlds:
25

repeats:
3
```

and Harbor executes:

```text
600 trials
```

We don't need Kubernetes scheduling in Moltwork.

This is exactly the stuff old CGE was overbuilding.

---

# 23. Harbor is already connecting evals → optimization → RL

The official Cookbook includes:

```text
Harbor + GEPA
Harbor + Tinker RL
Harbor + Prime RL
Harbor + SkyRL
```

([GitHub][17])

Harbor itself describes its scope as:

> evals, post-training and prompt optimization using agentic environments. ([Harbor][21])

And its roadmap includes further Tinker and SkyRL integration.

So the direction is basically:

```text
World
 ↓
evaluation
 ↓
trajectory
 ↓
optimization
 ↓
training
```

Exactly where we want to be.

---

# 24. This suggests an eventual “continuous agent development” platform

Normal software:

```text
write code
 ↓
unit tests
 ↓
CI
 ↓
production
 ↓
error
 ↓
new regression test
```

Moltwork/Harbor/Letta:

```text
configure worker
 ↓
Harbor Worlds
 ↓
CGE evaluation
 ↓
real economic work
 ↓
failure/outcome
 ↓
new World
 ↓
memory/Skill/process mutation
 ↓
CGE evaluation
 ↓
better worker
```

This is basically:

> **CI/CD for continually learning agents.**

But with economic feedback attached.

---

# 25. GitHub PRs could become experiments

This is a nice concrete UX.

Imagine a Letta reflection process proposes:

```text
memory change
```

It creates:

```text
PR #71
"Add requirement-matrix procedure"
```

CI runs:

```text
Harbor smoke Worlds
Harbor transfer Worlds
CGE paired experiment
```

PR gets:

```text
Capability impact

technical_submission:
 +8.1%

requirements:
 +13.7%

research:
 +0.8%

cost:
 +3.2%

regressions:
 none

evidence:
 E81
```

Then merge.

That is an incredible Git-native mental model.

**A memory PR has tests.**

---

# 26. The same applies to Skills and evaluators

### Skill PR

```text
"Improve customer escalation skill"

CI:
support school
customer satisfaction World
policy compliance World
```

### World PR

```text
"Add adversarial refund scenario"

CI:
oracle solution passes
known-bad agent fails
high-quality agents discriminate
```

### Assessor PR

```text
"Increase feasibility weighting"

CI:
regrade 300 historical trajectories
compare against real outcomes
```

### Process PR

```text
"Research before ideation"

CI:
20 paired campaigns
```

Every intellectual asset becomes testable software.

That is the Git thesis in its strongest form.

---

# 27. Hydra becomes the intelligence layer Harbor deliberately doesn't have

Harbor's results viewer can compare jobs, inspect trajectories, costs, verifier outputs and generate failure summaries. ([GitHub][22])

But Harbor does not try to construct a longitudinal model like:

```text
Memory M17
  influenced
Worker V12
  which used
Skill S4
  following
Process P7
  on
World W9
  producing
Artifact A18
  graded by
Assessor E3
  which predicted
Outcome O41
```

That's Hydra.

Harbor has **trials**.

Hydra has **history across trials**.

---

# 28. One new Hydra object: `HarborLock`

Don't parse all Harbor configuration into custom Moltwork schemas immediately.

Store the original lock identity:

```text
(:HarborTrial)
  task_digest
  dataset_digest
  lock_digest
  trajectory_ref
  result_ref
```

Then project semantic entities:

```text
(:WorkerVersion)
(:WorldVersion)
(:SkillVersion)
(:AssessorVersion)
```

Each points back to the exact Harbor lock.

Thus:

```text
Hydra interpretation
      │
      ▼
Harbor immutable-ish evidence
```

If our ontology changes, rebuild the graph from the locks.

---

# 29. The trajectory duality is potentially huge for Hydra

Store:

```text
ATIF
```

as the evidence-grade trace.

Generate:

```text
Letta trajectory
```

for agent reasoning.

Then Hydra nodes can point to selectively summarized episodes.

For example:

```text
Decision D181
  raw evidence:
    ATIF step 47–61

  agent-readable:
    Letta trajectory fragment

  derived finding:
    "Agent ignored feasibility warning"
```

That's much better than storing a single giant transcript in the graph.

---

# 30. Harbor can become the universal execution plane, not just a Letta tool

This is strategically important.

Our first worker is Letta.

But Harbor already supports:

```text
Claude Code
Codex
Gemini
OpenHands
Copilot
Mini-SWE-Agent
...
```

([Harbor][23])

So later:

```text
World:
hackathon ideation

Subjects:
Letta Opus
Letta GPT
Claude Code
Codex
OpenHands
```

Same evaluator.

Hydra learns:

```text
For task family X:
Letta is best.

For Y:
Codex is best.

For Z:
Claude + Skill S beats all.
```

Moltwork then becomes harness-neutral economically, despite Letta being our preferred persistent-learning runtime.

That is stronger architecture.

---

# 31. Cross-agent experience inheritance becomes a fascinating research program

Because ATIF can seed compatible agents, and Letta Trajectory can normalize sessions across harnesses, we could ask:

```text
Can Worker B learn from Worker A's successes?
```

Example:

```text
Codex wins coding World
       ↓
ATIF
       ↓
Letta Molter
       ↓
Trace2Skill
       ↓
Skill
       ↓
Letta worker improves
```

Or:

```text
Claude fails
Codex succeeds

compare trajectories
       ↓
difference extraction
       ↓
candidate process
       ↓
test on Letta
```

That's basically **cross-species cultural evolution for agents**.

And all primitives already exist.

---

# 32. Harbor + Hydra could discover “minimal curricula”

Schools don't necessarily need 500 tasks.

Suppose Hydra sees:

```text
W1 teaches capability A
W2 teaches capability A+B
W3 teaches B+C
W4 teaches C
...
```

and capability gain plateaus.

The Lab can optimize:

```text
smallest set of Worlds
that yields same held-out capability gain
```

Now Schools become cheaper and more effective.

Potential product:

```text
Customer Support School Lite
12 Worlds
$0.38 training cost
+17% held-out score
```

versus:

```text
Full School
81 Worlds
$3.90
+21%
```

Now training itself becomes economically routable.

---

# 33. Harbor tasks can eventually become autonomous “lessons from failures”

This may be the most visionary practical feature.

After a bad real run:

```text
Molter:
"Was this failure novel?"
```

If yes:

```text
WorldBuilder Letta agent
       ↓
Harbor create-task Skill
       ↓
captures:
environment
state
instruction
expected outcome
failure trigger
       ↓
RewardKit verifier
       ↓
oracle validation
       ↓
candidate World PR
```

Harbor already publishes an extensive `create-task` Agent Skill specifically instructing coding agents how to build tasks and verifiers. ([GitHub][24])

So even **World creation is already agentizable**.

That is massive.

---

# 34. Imagine every expensive failure automatically creating a regression World

```text
REAL LOSS
   │
   ▼
failure analysis
   │
   ▼
minimal reproducible scenario
   │
   ▼
Harbor World
   │
   ▼
Git commit
   │
   ▼
School curriculum
```

Eventually your lab contains:

```text
10,000 mistakes
```

but not as giant chat histories.

As **10,000 executable lessons**.

That is much more powerful.

---

# 35. Where Harbor itself is heading

Their published roadmap makes the direction quite clear:

* adapt major benchmarks into one registry;
* create new agent benchmarks;
* help companies build/share internal benchmarks;
* multi-turn simulated-user evaluation;
* capture **production agent state and turn it into tasks**;
* more training integrations;
* better snapshot/debugging infrastructure;
* “PyPI for Harbor tasks”;
* managed rollout infrastructure.

So yes, I would call it frontier infrastructure.

The broader ecosystem is converging on:

```text
portable Worlds
portable Skills
portable trajectories
portable agent configs
standard sandboxes
standard evaluators
post-training from real agent rollouts
```

The missing layer is increasingly **not runtime infrastructure**.

It's:

```text
What should this agent learn?
What experience matters?
Which World is predictive?
Which process actually improves outcomes?
Which asset transfers?
Which experiment is worth spending money on?
```

That is Moltwork.

---

# 36. I would now modify the frozen architecture slightly

Previously:

```text
Moltwork
  +
CGE Worlds
  +
Letta
```

Now:

```text
                    MOLTWORK
                economic scientist
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
       ORACLE                   HYDRA
   market selection       empirical knowledge
          │                       │
          └───────────┬───────────┘
                      ▼
                     CGE
              experiment protocol
                      │
                      ▼
                   HARBOR
          universal execution plane
          /        |        \
       Letta     Codex     Other
         │
     persistent
      learning
```

Harbor is the missing **physical laboratory**.

CGE is the experimental method.

Hydra is the lab notebook/knowledge graph.

Letta is the organism being evolved.

Oracle is the environment supplying real-world selection pressure.

Git is the genome/version-control substrate running through all of them.

That metaphor is surprisingly exact.

---

## The one integration I would build first

A real:

```text
harbor agent = letta
```

where a Harbor job can specify:

```yaml
agents:
  - name: letta

    worker:
      agent_id: researcher-03

    state:
      memory_commit: ...

    session:
      fresh: true

    learning:
      production_mutations: false
```

Then run:

```text
Harbor Task
      ↓
persistent Letta identity
      ↓
fresh task session
      ↓
ATIF + Letta Trajectory
      ↓
RewardKit
      ↓
WorkerKit receipt
      ↓
Hydra projection
```

Once **that one path** is robust, the rest becomes extraordinarily composable.

And I think the real long-term thesis becomes:

> **Harbor turns work into reproducible environments. Git turns experience into versioned assets. Hydra turns runs into empirical knowledge. Letta turns that knowledge back into cognition. Moltwork decides which experiments are economically worth conducting.**

That is substantially bigger—and cleaner—than the original idea of an autonomous job agent.

[1]: https://www.harborframework.com/docs?utm_source=chatgpt.com "Motivation"
[2]: https://www.harborframework.com/docs/tasks?utm_source=chatgpt.com "Task Structure"
[3]: https://www.harborframework.com/docs/datasets?utm_source=chatgpt.com "Datasets"
[4]: https://www.harborframework.com/docs/run-jobs/skills?utm_source=chatgpt.com "Skills"
[5]: https://www.harborframework.com/docs/hosted-harbor/custom-agents?utm_source=chatgpt.com "Custom Agents"
[6]: https://www.harborframework.com/docs/tasks/multi-step?utm_source=chatgpt.com "Multi-step Tasks"
[7]: https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md?utm_source=chatgpt.com "harbor/rfcs/0001-trajectory-format.md at main · harbor-framework/harbor · GitHub"
[8]: https://www.letta.com/blog/trajectory/?utm_source=chatgpt.com "Trajectory: A Standard Format for Agent Experience Data | Letta"
[9]: https://www.harborframework.com/docs/run-jobs/load-trajectory?utm_source=chatgpt.com "Loading Trajectories"
[10]: https://www.harborframework.com/docs/run-jobs/regrade?utm_source=chatgpt.com "Regrade"
[11]: https://www.harborframework.com/docs/run-jobs/results-and-artifacts?utm_source=chatgpt.com "Artifact Collection"
[12]: https://www.harborframework.com/docs/rewardkit?utm_source=chatgpt.com "Reward Kit"
[13]: https://www.harborframework.com/docs/rewardkit/motivation?utm_source=chatgpt.com "Motivation & Design"
[14]: https://www.harborframework.com/docs/tasks/publishing?utm_source=chatgpt.com "Publishing a task"
[15]: https://hub.harborframework.com/?utm_source=chatgpt.com "Harbor Hub"
[16]: https://www.harborframework.com/docs/tutorials/mcp-server-task?utm_source=chatgpt.com "MCP Server Task"
[17]: https://github.com/harbor-framework/harbor-cookbook?utm_source=chatgpt.com "GitHub - harbor-framework/harbor-cookbook: Realistic examples of building evals and optimizing agents with Harbor · GitHub"
[18]: https://github.com/harbor-framework/harbor-index?utm_source=chatgpt.com "GitHub - harbor-framework/harbor-index: A compact high-signal benchmark for evaluating frontier agents · GitHub"
[19]: https://www.harborframework.com/docs/run-jobs/cloud-sandboxes?utm_source=chatgpt.com "Sandboxes"
[20]: https://www.harborframework.com/docs/hosted-harbor/cli?utm_source=chatgpt.com "CLI"
[21]: https://www.harborframework.com/docs/getting-started?utm_source=chatgpt.com "Getting Started"
[22]: https://github.com/harbor-framework/harbor/blob/main/docs/content/docs/run-jobs/run-evals.mdx?utm_source=chatgpt.com "harbor/docs/content/docs/run-jobs/run-evals.mdx at main · harbor-framework/harbor · GitHub"
[23]: https://www.harborframework.com/docs/agents?utm_source=chatgpt.com "Agents"
[24]: https://github.com/harbor-framework/harbor/blob/main/skills/create-task/SKILL.md?utm_source=chatgpt.com "harbor/skills/create-task/SKILL.md at main · harbor-framework/harbor · GitHub"
