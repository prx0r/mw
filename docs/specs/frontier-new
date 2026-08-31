Yes. Harbor substantially validates the architecture. But the key conclusion from looking further is slightly different:

> **Do not build “Moltwork’s version of Harbor.” Build the layer that makes Harbor environments economically useful, empirically trustworthy, continually improvable, and composable with persistent workers.**

Harbor itself is explicitly heading toward a task registry, private registries, production-state-to-task capture, multi-turn simulated-user evaluation, more training integrations, and managed rollout infrastructure. That overlaps heavily with any generic “marketplace for benchmarks” plan. ([Harbor][1])

That is good news. We can populate and extend that ecosystem instead of competing with it.

## Regrade is even more important than it first appears

A WorkerRun should become an **immutable observation**:

```text
RUN R91
├── exact worker state
├── exact world
├── exact skills
├── exact model
├── exact artifacts
├── exact trajectory
├── exact costs
└── external outcome eventually
```

Then you can create arbitrarily many interpretations afterward:

```text
                    immutable R91
                        │
       ┌────────────────┼─────────────────┐
       ▼                ▼                 ▼
 Assessor A         Assessor B        Assessor C
 old rubric         new rubric        specialist
       │                │                 │
      .74              .88               .81
       └────────────────┼─────────────────┘
                        ▼
                 real outcome
                 WIN / rank #2
                        │
                        ▼
                  calibration
```

Harbor regrade is explicitly designed this way: the recorded agent execution is held fixed and only verification is recomputed. Source trials are never modified. ([Harbor][2])

This is scientifically excellent because **worker evolution and assessor evolution become separable**.

You don't really “evolve the old run.” You evolve:

```text
WorkerVersion
ProcessVersion
WorldVersion
AssessorVersion
SkillVersion
MemoryVersion
```

using the old run as permanent evidence.

---

# But yes: ground truth is the central hard problem

There is not one universal ground truth.

For Moltwork I would explicitly define a **truth ladder**:

| Level | Signal                   | Example                                             |
| ----- | ------------------------ | --------------------------------------------------- |
| T0    | deterministic truth      | tests pass, API invoked, refund amount correct      |
| T1    | environment state truth  | CRM updated correctly, task actually completed      |
| T2    | trusted reference/expert | human reviewer, known-good solution                 |
| T3    | real-world outcome       | won prize, customer satisfied, job accepted, payout |
| T4    | calibrated proxy         | evaluator predicts the above                        |
| T5    | uncalibrated proxy       | generic LLM says “8.7/10”                           |

That distinction solves a lot.

For a coding task, T0/T1 may be nearly sufficient.

For customer support you might have:

```text
policy compliance
+
tool state correctness
+
customer simulator
+
eventual human satisfaction
```

For hackathons, “won” is high-signal but not perfect truth because judging is noisy and sample sizes are tiny.

So instead of:

```text
won = objectively good
lost = objectively bad
```

Hydra should learn:

```text
ExternalOutcome:
  rank = 2
  judges = unknown
  n_entries = 213
  confidence = high-ish
```

Then combine that with deterministic and assessor evidence.

---

# The evaluator should itself have a track record

This becomes one of the most important Moltwork objects:

```text
AssessorVersion A19

predictions:
R18 → predicted top 10% → actual top 5%
R22 → predicted fail    → actual rejected
R28 → predicted top 20% → actual winner
R31 → predicted winner  → actual bottom 50%

calibration:
...
```

Then Hydra can estimate:

```text
A19

technical correctness   excellent
sponsor alignment       excellent
novelty                  mediocre
visual presentation      poor
overall rank prediction  0.76
```

So when evaluating a new submission, Moltwork isn't asking:

> Which evaluator has the highest marketplace rating?

It can ask:

> Which evaluator has historically been most predictive **for this ontology region**?

That is substantially more defensible.

---

# This means the evaluator marketplace becomes plausible

And yes: **Harbor Reward Kit → confidential service → pay-per-call** is a very natural path.

Reward Kit already separates criteria into composable programmatic or LLM/agent judge verifiers and can inspect workspaces and trajectories. ([Harbor][3])

Imagine a private evaluator whose code is valuable:

```text
phala-hackathon-assessor/v19
```

Seller doesn't want to reveal:

```text
hidden cases
rubrics
judge prompts
calibration tricks
historical examples
weights
```

Buyer doesn't want to reveal:

```text
source code
submission
business idea
strategy
```

Put the verifier inside a confidential VM:

```text
BUYER
  │ encrypted artifact
  ▼
┌────────────────────────────┐
│ TEE                        │
│                            │
│ Harbor RewardKit           │
│ Assessor commit 19af21     │
│ hidden test corpus         │
│ private judge logic        │
└─────────────┬──────────────┘
              ▼
     score + feedback
     signed response
     attestation
```

Phala attestation is designed to prove that a CVM is running genuine TEE hardware with expected OS/application measurements, and its confidential-model stack supports signatures binding individual responses to attested keys. ([Phala Docs][4])

But maintain the separation:

```text
TEE attestation
=
"This evaluator really ran."

Git provenance
=
"This was evaluator commit 19af21."

WorldValidityClaim
=
"This evaluator has historically
predicted useful outcomes."
```

TEE does **not** prove that a rubric is intelligent.

That comes from the empirical record.

---

# Is Harbor becoming our idea?

At one infrastructure layer, yes.

But that isn't a problem.

Harbor wants to become something like:

```text
package + run + distribute agent environments
```

Its roadmap even calls its planned hosted task layer **“PyPI for Harbor tasks”**, including private registries and metrics. ([Harbor][1])

I would therefore explicitly abandon any Moltwork plan to build a generic:

```text
benchmark registry
sandbox marketplace
task execution cloud
benchmark package format
```

Let Harbor do that.

### Moltwork's differentiation becomes

```text
economic demand
       ↓
which capability matters?
       ↓
which World should we run?
       ↓
which evaluator is trustworthy?
       ↓
which experiment has highest VOI?
       ↓
which worker mutation worked?
       ↓
what should become durable learning?
       ↓
did it improve real economic outcomes?
```

Harbor doesn't answer those questions.

---

# CGE becomes a Harbor evolver — but slightly more general

Yes. **“Harbor evolver” is an excellent mental model.**

But I wouldn't hard-code its schema to Harbor, because I found another major frontier project we were missing.

## Prime Intellect `verifiers`

Prime's abstraction is remarkably similar:

```text
Environment
=
dataset/taskset
+
harness
+
rubric
```

and the same environment can be used for evaluation, synthetic-data generation and RL training. ([Prime Intellect Docs][5])

Their July 2026 v1 direction goes further by explicitly separating:

```text
Taskset
Harness
Runtime
```

rather than treating “the benchmark” as one monolithic thing. ([Prime Intellect][6])

That distinction is highly relevant.

For example:

```text
TASKSET
hackathon idea generation cases

HARNESS
Letta persistent worker

RUNTIME
Harbor / sandbox

RUBRIC
RewardKit / Prime verifier
```

So CGE should really become:

```text
CGE SCIENTIST
     │
     ├── Harbor adapter
     ├── Prime Verifiers adapter
     └── eventually OpenEnv adapter
```

Harbor can still be the **default execution backend**.

But CGE's conceptual object should be framework-neutral.

---

# Prime Intellect is worth watching very closely

Their Environments Hub is explicitly built around the thesis that:

> RL environments and agent evaluations are fundamentally the same primitive.

They argue that environment fragmentation is a problem and provide a community package registry where environments bring their own dependencies. ([Prime Intellect Docs][7])

That's exactly where the broader frontier appears to be going:

```text
EVALUATION WORLD
       =
TRAINING WORLD
       =
SIMULATION WORLD
```

Today:

```text
test worker on World X
```

Tomorrow:

```text
generate trajectories on World X
```

Then:

```text
learn Skills from World X
```

Eventually:

```text
RL-train model on World X
```

Same asset.

That makes a high-quality World potentially much more economically valuable than a static benchmark.

---

# OpenEnv may become the interoperability standard underneath all this

This is another project I'd now keep in the architecture radar.

Hugging Face OpenEnv is pushing an elegant two-interface idea:

```text
INFRASTRUCTURE
Gym-like:
reset()
step()
state()

AGENT
MCP:
list_tools()
call_tool()
```

The trainer maintains episode control while the agent sees ordinary MCP tools. ([GitHub][8])

That's an excellent architectural idea for Moltwork Schools.

An environment could be:

```text
customer support company
```

with Moltwork/CGE controlling:

```text
reset company state
advance scenario
inspect hidden state
calculate reward
```

while the Letta worker merely sees:

```text
crm_search
refund_customer
send_message
escalate_ticket
```

over MCP.

Now the same synthetic company can be used by:

```text
Letta
Claude
Codex
RL trainer
human tester
```

without changing its tool interface.

---

# Synthetic World generation is also much further along than I thought

Snowflake's **Agent World Model** project released **1,000 executable environments with 10,000 tasks**, including databases, tools and verification logic, and OpenEnv exposes them as functional MCP environments. ([GitHub][9])

That's directly relevant to CGE **space expansion**.

Suppose Hydra says:

```text
customer_support.refunds

World coverage weak:
- fraud
- legacy billing
- subscription pause
```

Instead of manually authoring everything:

```text
Lab
 ↓
World synthesis agent
 ↓
generate candidate environment/scenarios
 ↓
Harbor/OpenEnv
 ↓
known-good + known-bad agents
 ↓
filter broken worlds
 ↓
human/real calibration
 ↓
promote useful worlds
```

So one future CGE optimizer doesn't evolve workers.

It evolves **the curriculum itself**.

---

# And this creates co-evolution

The system is no longer:

```text
fixed benchmark
    ↓
better agent
```

It's:

```text
        WORKER
          ▲
          │
          │
WORLD ◄───┼───► ASSESSOR
          │
          ▼
        SCHOOL
```

A worker gets stronger.

World becomes too easy.

CGE detects low discrimination.

World generator produces harder cases.

Assessor starts disagreeing with external outcomes.

Regrade historical runs.

Assessor evolves.

New weaknesses emerge.

School changes.

Worker improves again.

That is genuine **co-evolution**.

---

# But you need protection against Goodhart/reward hacking

This is another frontier we shouldn't ignore.

`RewardHackBench` specifically tests whether agents can game their evaluation environment. In its published Harbor experiments, ordinary static restrictions remained exploitable, while judging outgoing requests reduced the tested cheating behavior without eliminating legitimate solves. ([GitHub][10])

That suggests CGE needs a first-class concept:

```text
EvaluatorAdversarialSuite
```

Whenever an evaluator becomes important:

```text
try to optimize score without doing job
try to leak hidden tests
try to manipulate judge
try to edit verifier state
try to exploit network access
try to exploit file visibility
```

This is especially important if evaluators themselves are sold.

A highly ranked evaluator will become a target for optimization.

---

# A marketplace ranking should therefore include hack resistance

Imagine:

```text
Evaluator E19

predictive validity     .84
repeatability           .91
cost                    $0.006
latency                  3.1 sec
hack resistance          .88
transfer breadth         .71
n external outcomes       83
```

Now you have something much more interesting than:

```text
⭐ 4.8 / 5
```

---

# Inspect AI + METR are another ecosystem we should borrow methodology from

The UK AI Security Institute's **Inspect** has become a serious general evaluation framework with tool use, multi-turn dialogs, model-graded evaluations and a large evaluation collection. ([GitHub][11])

More importantly, Inspect Evals changed in May 2026 toward a lightweight **registry pointing to independently maintained evaluator repositories**, rather than forcing everything into a monorepo. ([GitHub][12])

That validates our Git-native direction again.

METR's Task Standard exists for essentially the same reason: task authoring is expensive, so organizations should be able to reuse each other's autonomous-agent tasks instead of duplicating them. ([GitHub][13])

We shouldn't adopt all three formats.

But we should learn from their task validation and security practice.

---

# There are domain-specific World ecosystems we can import directly

This means specialized Moltwork Labs don't need to start from zero.

For web/browser work, **BrowserGym** already unifies environments including WebArena, VisualWebArena, WorkArena, AssistantBench and others. ([GitHub][14])

For customer-support agents, **τ³-bench** has evolved into tool-agent-user evaluation with customer-service domains, knowledge retrieval and more realistic interactions. ([GitHub][15])

So a customer-support Lab can start:

```text
generic capability
  τ³-bench

web interaction
  BrowserGym/WorkArena

company-specific capability
  proprietary Harbor Worlds

real production failures
  newly generated regression Worlds
```

That's incredibly efficient.

---

# Letta's roadmap/research direction fits this almost perfectly

I couldn't find one canonical public “Letta roadmap” document equivalent to Harbor's roadmap, so I wouldn't invent one.

But their 2026 research direction is very clear.

Their current research program centers on:

```text
production memory evaluation
trajectory normalization
memory models
token-space continual learning
self-evolving agents
```

([Letta][16])

Their memory-model thesis is particularly aligned with us: future agents should have models specialized in creating and curating durable token-space memory that transfers across model generations. ([Letta][17])

Meaning Moltwork gives Letta exactly what those future memory systems will need:

```text
experience
+
world
+
evaluation
+
outcome
+
longitudinal feedback
```

We're essentially building a high-quality **experience generator and selection system** around Letta.

---

# Even Letta's Skills culture looks oddly Moltwork-like

Their community Skills guidance says useful knowledge should emerge from experience and be validated across multiple contexts; it explicitly gives a rough evidence heuristic:

```text
1 occurrence → personal note
2–3 → worth discussion
3+ → stronger evidence
```

and uses PR-based review for shared knowledge. ([GitHub][18])

Moltwork makes that rigorous:

```text
1 run
→ Hydra observation

multiple correlated runs
→ hypothesis

controlled experiment
→ CapabilityClaim

cross-domain heldout success
→ transferable Skill

real external success
→ strong economic evidence
```

So we're not fighting Letta's philosophy at all.

We're giving it an experimental/economic evidence layer.

---

# Letta Mods also give us the integration point

Mods can already add tools, commands, lifecycle hooks, permissions, providers and UI surfaces, and can themselves be installed directly from Git repositories. ([GitHub][19])

So `moltwork-letta` should remain tiny:

```text
oracle_search()
lab_recall()
world_search()
assessor_search()

campaign_status()
budget_remaining()

record_decision()
request_review()

submit_artifact()
```

It should not become another harness.

---

# So where does CGE land exactly?

I would now define CGE in one sentence:

> **CGE is the optimizer/scientist for agent environments, workers and evaluators.**

It doesn't execute Worlds itself.

It takes:

```text
Subject
World
Evaluator
History
Budget
```

and answers:

```text
What experiment should we run next?
```

Its control loop:

```text
              HYDRA
          historical evidence
                │
                ▼
               CGE
                │
       ┌────────┼─────────┐
       ▼        ▼         ▼
 mutate      mutate     mutate
 worker      world      assessor
       │        │         │
       └────────┼─────────┘
                ▼
        Harbor / Verifiers
                │
              results
                │
                ▼
              HYDRA
```

### Critical invariant

Never mutate all three inside one experiment.

Instead:

```text
Experiment E1:
freeze World + Assessor
vary Worker

Experiment E2:
freeze Worker corpus
vary Assessor via regrade

Experiment E3:
freeze Worker population + Assessor
vary World
```

That maintains identifiability.

---

# The World evolution loop is surprisingly elegant

For a candidate World:

```text
W19
```

ask:

```text
Does known-good worker pass?
Does known-bad worker fail?

Does it distinguish strong from weak workers?

Is reward stable across repeats?

Can agents hack it?

Does performance correlate with
real-world success?

Does it add information beyond
existing Worlds?
```

That's essentially **unit testing the test**.

If yes:

```text
WorldValidityClaim
```

If not:

```text
reject/fix World
```

Harbor becomes the runtime.

CGE becomes benchmark evolution.

---

# The assessor evolution loop becomes even better with regrade

```text
historical run corpus
      │
      ├── Assessor A
      ├── Assessor B
      └── Assessor C
              │
              ▼
       prediction vectors
              │
              ▼
       external outcomes
              │
              ▼
     estimate reliability
```

No agent inference required.

That is cheap enough to happen constantly.

And over time Hydra can condition assessor quality on task subtype:

```text
A best for:
technical architecture

B best for:
customer support

C best for:
visual UX

ensemble A+C best for:
hackathon submissions
```

---

# The trajectory itself could eventually train the assessor

Once you have enough external outcome labels:

```text
artifact
trajectory
assessor predictions
real result
```

you can start training better evaluation models.

Prime's whole architecture already treats the same environments as eval and RL infrastructure, which is why I think that ecosystem matters so much to us. ([Prime Intellect Docs][5])

Eventually:

```text
Moltwork Assessor v1
generic frontier model

        ↓ years of outcomes

Moltwork Assessor v20
domain-adapted evaluation model
```

That is potentially extremely valuable.

---

# The marketplace becomes secondary again

I think this resolves the concern.

Harbor may eventually handle:

```text
publish task
private task registry
run environment
share benchmark
```

Prime may similarly handle:

```text
publish environment
train model
host environment
```

We should actively **want them to win**.

Then Moltwork can say:

```text
World:
harbor://alice/customer-support@v7

or

World:
prime://bob/refund-env@v3
```

Our marketplace doesn't need to host either.

It indexes:

```text
evidence
economic value
compatibility
price
capability mapping
validity
provenance
```

and routes agents to them.

That is much more defensible.

---

# The evaluator-as-a-service market is still distinct

Harbor currently wants a package/task registry and execution infrastructure.

That isn't yet the same as:

```text
$0.01 confidential evaluation API
```

with:

```text
private evaluator IP
private buyer artifact
attested execution
historical validity
x402/payment
economic routing
```

So instead of building:

> Moltwork Harbor Marketplace

we eventually build:

> **Moltwork capability/evaluation market whose assets may be implemented as Harbor tasks.**

Huge difference.

---

# The architecture I would freeze now

```text
                EXTERNAL REALITY
                      │
             outcomes / money
                      │
                      ▼
                  MOLTWORK
         economic selection/science
          │                    │
          ▼                    ▼
       ORACLE                HYDRA
      demand             empirical graph
          │                    │
          └──────────┬─────────┘
                     ▼
                    CGE
             experiment selector
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
    HARBOR        VERIFIERS      OPENENV
   execution       training      interop/MCP
       │
       ▼
     LETTA
persistent cognition
       │
       ▼
 WorkerRun evidence
       │
       ├── ATIF
       ├── Letta trajectory
       ├── artifacts
       ├── WorkerKit receipt
       └── external result
       │
       ▼
     HYDRA
       │
       ▼
       CGE
 worker/world/assessor
    experiments
       │
       ▼
       GIT
 promoted knowledge/assets
```

And then Phala/TEE sits off to the side as a deployment option:

```text
validated evaluator
      ↓
RewardKit/Harbor package
      ↓
TEE
      ↓
paid confidential endpoint
```

---

## The deepest thing the frontier is converging toward

What used to be separate:

```text
benchmark
training environment
production simulation
regression test
curriculum
agent experience
```

is collapsing into **one executable environment abstraction**.

Harbor says it.

Prime Verifiers says it.

OpenEnv says it.

Agent World Model is synthesizing these environments at scale.

Letta is simultaneously making **experience persistent and learnable**.

That convergence is extremely favorable for Moltwork because our thesis sits one level above it:

> **If executable experience is becoming standardized, the scarce problem becomes selecting valuable experience, measuring what it teaches, preserving what transfers, and allocating agents toward economically useful learning.**

That is where I would keep Moltwork concentrated.

I can monitor Harbor, Letta, Prime Verifiers, OpenEnv, GEPA and related projects and surface architecture-changing releases as they happen.

[1]: https://www.harborframework.com/docs/contributing/roadmap?utm_source=chatgpt.com "Roadmap"
[2]: https://www.harborframework.com/docs/run-jobs/regrade?utm_source=chatgpt.com "Regrade"
[3]: https://www.harborframework.com/docs/rewardkit?utm_source=chatgpt.com "Reward Kit"
[4]: https://docs.phala.com/phala-cloud/attestation/overview?utm_source=chatgpt.com "Phala Cloud Documentation — Confidential AI on TEE"
[5]: https://docs.primeintellect.ai/verifiers/overview?utm_source=chatgpt.com "Overview - Prime Intellect Docs"
[6]: https://www.primeintellect.ai/blog/verifiers-v1?utm_source=chatgpt.com "verifiers v1: Decomposing Tasksets and Harnesses for Agentic RL & Evaluations"
[7]: https://docs.primeintellect.ai/tutorials-environments/environments?utm_source=chatgpt.com "Overview - Prime Intellect Docs"
[8]: https://github.com/huggingface/openenv/blob/main/docs/source/tutorials/mcp-environment.md?utm_source=chatgpt.com "OpenEnv/docs/source/tutorials/mcp-environment.md at main · huggingface/OpenEnv · GitHub"
[9]: https://github.com/huggingface/openenv/blob/main/docs/source/environments/agent_world_model.md?utm_source=chatgpt.com "OpenEnv/docs/source/environments/agent_world_model.md at main · huggingface/OpenEnv · GitHub"
[10]: https://github.com/islo-labs/reward-hack-bench?utm_source=chatgpt.com "GitHub - islo-labs/reward-hack-bench: Benchmarking execution environments ability to prevent reward hacking in agent evals. · GitHub"
[11]: https://github.com/UKGovernmentBEIS/inspect_ai?utm_source=chatgpt.com "GitHub - UKGovernmentBEIS/inspect_ai: Inspect: A framework for large language model evaluations · GitHub"
[12]: https://github.com/UKGovernmentBEIS/inspect_evals?utm_source=chatgpt.com "GitHub - UKGovernmentBEIS/inspect_evals: Collection of evals for Inspect AI · GitHub"
[13]: https://github.com/METR/task-standard?utm_source=chatgpt.com "GitHub - METR/task-standard: METR Task Standard · GitHub"
[14]: https://github.com/ServiceNow/BrowserGym?utm_source=chatgpt.com "GitHub - ServiceNow/BrowserGym: 🌎💪 BrowserGym, a Gym environment for web task automation · GitHub"
[15]: https://github.com/sierra-research/tau2-bench?utm_source=chatgpt.com "GitHub - sierra-research/tau2-bench: τ-Bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains · GitHub"
[16]: https://www.letta.com/research/?utm_source=chatgpt.com "Research | Letta"
[17]: https://www.letta.com/blog/towards-agents-that-learn/?utm_source=chatgpt.com "Memory Models: Towards Agents That Learn | Letta"
[18]: https://github.com/letta-ai/skills/blob/main/CULTURE.md?utm_source=chatgpt.com "skills/CULTURE.md at main · letta-ai/skills · GitHub"
[19]: https://github.com/letta-ai/mods?utm_source=chatgpt.com "GitHub - letta-ai/mods: Letta Code mod packages and examples · GitHub"
