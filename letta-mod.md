Yes. After looking at the 2025–2026 memory work, the current Letta stack, BEAM v2, HydraDB, and the newer procedural-memory work, I think there is a much cleaner direction:

> **Moltwork should become a Letta-native experimental lab, not another agent framework and not another memory framework.**

The thing Moltwork should uniquely own is the **scientific loop around persistent workers**: choosing real tasks, freezing experimental conditions, comparing worker versions, independently assessing outputs, tracking causal provenance, and promoting only interventions that measurably improve future work.

## 1. The frontier strongly supports the architecture we already wanted

There are several fairly consistent findings now.

BEAM v2 was last revised on **February 21, 2026**. Its LIGHT architecture separates **episodic memory, working memory, and a scratchpad**, and its ablations show the pieces are complementary; reported gains over strong baselines vary from roughly 3.5% to 12.69%. ([arXiv][1]) I also inspected the implementation: it literally constructs separate scratchpad, episodic-memory and recent-working-memory representations rather than treating memory as one vector store.

But the newer continual-learning evidence adds an important warning. A 2026 study found that **abstract procedural memories transfer more reliably than detailed trajectories**, while retrieving inappropriate old experiences can create severe negative transfer. Another empirical study found that selective memory addition/deletion improved performance over naïve unlimited accumulation. ([arXiv][2]) EvoMemBench likewise finds there is no universally best memory architecture and that long-context baselines remain surprisingly competitive; memory becomes especially valuable when context is insufficient and when procedural experience matches the task structure. ([arXiv][3])

That means the goal is emphatically **not**:

```text
save everything
→ retrieve everything vaguely similar
→ hope worker improves
```

It is:

```text
experience
   ↓
determine what was causally useful
   ↓
decide what representation deserves persistence
   ↓
memory / skill / workflow / harness intervention
   ↓
controlled evaluation
   ↓
retain or delete
```

That is essentially the Moltwork Lab.

---

# 2. Letta now solves most of the worker side for us

Current Letta is far more aligned with this than its older architecture was.

The August 2026 Agent SDK gives one TypeScript interface for persistent agents running locally, self-hosted or on Letta's cloud. Letta Code itself has MemFS, Git-versioned context, agent-owned skills, subagents, dreaming/reflection, message search, hooks, Mods and harness-level self-modification. ([Letta][4])

Context Repositories are particularly important. Letta deliberately uses **real Git repositories and Git worktrees for memory evolution**. Reflection subagents can work independently in worktrees and merge memory changes; memory defragmentation and skill maintenance are already built around this design. ([Letta][5])

So I would not build:

| Problem                          | Moltwork should do                   |
| -------------------------------- | ------------------------------------ |
| Persistent worker identity       | **Letta**                            |
| Memory filesystem                | **Letta MemFS**                      |
| Git-versioned memory             | **Letta**                            |
| Conversation/session persistence | **Letta**                            |
| Recall of old sessions           | **Letta**                            |
| Scratch/reference memory         | **MemFS conventions**                |
| Skills                           | **Letta/Agent Skills**               |
| Reflection/dreaming              | **Letta**, experimentally controlled |
| Subagents                        | **Letta**                            |
| Harness customization            | **Letta Mods**                       |
| Portable experience format       | **`@letta-ai/trajectory`**           |
| Evaluation runner                | **`letta-evals`**                    |
| Portable agent snapshots         | **`.af` where useful**               |

Letta's own current system prompt makes essentially our distinction: memory is for durable future judgment; skills are reusable procedural knowledge; Mods/hooks/configuration are for deterministic changes to the execution environment. ([GitHub][6])

That's extremely useful because it gives the Lab **three fundamentally different mutation classes**:

```text
COGNITIVE MUTATION
Memory / context

PROCEDURAL MUTATION
Skill

HARNESS MUTATION
Mod / tool / permission / model / hook
```

We shouldn't collapse those into generic "agent memory."

---

# 3. The most interesting Moltwork implementation may actually be a Letta Mod

This is the direction I would take now.

Build something like:

```text
@moltwork/letta-lab
```

as a Letta Mod.

Mods can register tools, commands, lifecycle events, permission overlays, model providers, panels and other deterministic harness behavior. ([GitHub][7])

So the worker itself gets a tiny native interface:

```text
oracle_search()
oracle_get_opportunity()

lab_brief()
lab_recall_experiment()
lab_get_capability_claim()

budget_remaining()

assessor_preflight()
assessor_request_review()

moltwork_submit()
```

And lifecycle hooks silently witness:

```text
session.started
tool.called
model.used
artifact.created
git.commit
memory.commit
skill.loaded
review.requested
submission.created
session.completed
```

Those become WorkerKit events.

This removes an enormous amount of our current adapter scaffolding.

Conceptually:

```text
┌─────────────────────────────────────────────────┐
│                  LETTA CODE                     │
│                                                 │
│ Persistent worker                              │
│ MemFS                                          │
│ skills                                         │
│ subagents                                      │
│ dreaming                                       │
│ workspace                                      │
│ trajectories                                   │
│                                                 │
│        ┌────────────────────────────┐           │
│        │     MOLTWORK LAB MOD       │           │
│        │                            │           │
│        │ Oracle tools               │           │
│        │ Lab/Hydra tools            │           │
│        │ budget controls            │           │
│        │ assessor gates             │           │
│        │ WorkerKit hooks            │           │
│        └────────────────────────────┘           │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
              external Lab
```

That's much more attractive than Python pretending to be a Letta runtime.

---

# 4. BEAM/LIGHT should become a benchmark, not another subsystem

LIGHT has exactly the conceptual components we were talking about, but I would **not port LIGHT wholesale into Moltwork**.

Letta already has analogous primitives:

```text
LIGHT                          LETTA

working memory             → current context/session
episodic memory            → conversation/trajectory recall
scratchpad                 → MemFS working/reference files
long-term refinement       → reflection/dreaming
procedural knowledge       → Skills
```

BEAM is valuable because it gives us an external benchmark with ten distinct memory abilities including knowledge update, temporal reasoning, contradiction resolution, abstention, event ordering, instruction following and summarization. ([GitHub][8])

So make **BEAM-128K a Moltwork integration test**.

Something like:

```text
letta-evals run evals/beam/letta-native.yaml
letta-evals run evals/beam/letta-dreaming.yaml
letta-evals run evals/beam/letta-lab-context.yaml
```

We then know whether our modifications are making Letta's memory better or accidentally making it worse.

That gives us an external sanity check independent of our own Lab.

---

# 5. ACE is almost exactly how memory promotion should work

ACE is extremely aligned.

Instead of repeatedly rewriting an entire context—which causes information collapse—it uses:

```text
Generator
    ↓
Reflector
    ↓
Curator
    ↓
small ADD / UPDATE / REMOVE deltas
```

Its central idea is **grow-and-refine rather than rewrite-and-compress**, and it reports meaningful gains on agent tasks while using natural execution feedback. ([arXiv][9])

I would not introduce ACE as another runtime.

Instead, steal its **memory mutation protocol**.

After a group of runs:

```text
Letta trajectories
       ↓
Lab Reflector
       ↓
CandidateMemoryPatch

ADD:
  "Always extract sponsor-specific requirements before ideation."

UPDATE:
  "Don't treat README presence as evidence of integration;
   require invocation evidence."

REMOVE:
  obsolete assumption
```

Apply those patches to a **candidate worker memory branch**, not production memory.

Then test.

ACE becomes an algorithm inside Moltwork Lab, while MemFS remains the storage/runtime mechanism.

---

# 6. Trace2Skill is even more directly reusable

This is one project I would actually clone.

Trace2Skill's official Qwen implementation does:

```text
trajectory pool
      ↓
parallel trajectory analysts
      ↓
trajectory-local lessons
      ↓
hierarchical consolidation
      ↓
conflict-free SKILL directory
```

and the paper specifically reports cross-model and OOD transfer of the resulting declarative skills. ([arXiv][10])

[Qwen Trace2Skill repository](https://github.com/Qwen-Applications/Trace2Skill?utm_source=chatgpt.com)

That's practically built for us.

Rather than maintaining our current toy:

```text
lab/synthesis.py
```

we should probably wrap Trace2Skill around official Letta trajectory data.

```text
@letta-ai/trajectory
          ↓
Moltwork trajectory adapter
          ↓
Trace2Skill
          ↓
candidate SKILL.md
          ↓
candidate Letta worker
          ↓
letta-evals
          ↓
promote/reject
```

This is much better than us reimplementing trajectory-to-skill synthesis.

MemP and Agent Workflow Memory reinforce the same direction: reusable procedural representations extracted from previous executions can improve both success and efficiency, including transferring between task distributions. ([arXiv][11])

[MemP repository](https://github.com/zjunlp/MemP?utm_source=chatgpt.com)

[Agent Workflow Memory repository](https://github.com/zorazrw/agent-workflow-memory?utm_source=chatgpt.com)

But I would use those mostly as **algorithms/baselines**. Letta Skills + Trace2Skill already give us the production representation.

---

# 7. A-MEM, Memory-R1 and AtomMem should initially be experiments, not dependencies

A-MEM dynamically creates structured notes and links related memories; Memory-R1 and AtomMem go further by treating memory CRUD as a learned decision process. ([GitHub][12])

Interesting research.

Wrong thing to put underneath Letta today.

Otherwise we end up with:

```text
Letta memory manager
    inside
Moltwork memory manager
    inside
A-MEM memory manager
    beside
Hydra memory manager
```

and we'll never know what caused anything.

Use them as Lab arms later:

```text
M0  Letta native
M1  Letta + dreaming
M2  Letta + ACE-style curated deltas
M3  Letta + Trace2Skill
M4  Letta + A-MEM-derived retrieval
```

Same tasks. Same model. Same budget.

Then *measure* which actually helps.

This recovers the point of our older Cogym memory experiments, but now the experimental variable is **memory policy**, not a completely different agent stack.

---

# 8. HydraDB is the experimental memory, not the worker memory

I checked the actual OSS HydraDB rather than treating "HydraDB" generically.

The open-source `hydra-db/hydradb` is a proper distributed Rust graph database built on SlateDB, with snapshot-consistent OpenCypher queries, GraphBLAS traversal, Bolt compatibility, HTTP APIs and object-store durability. ([GitHub][13])

The HydraDB hosted memory layer additionally exposes automatic ingestion, inference and graph-enriched recall. ([GitHub][14])

For Moltwork, I want the first one conceptually:

```text
Letta MemFS
= what Worker-03 remembers

HydraDB
= what Lab knows ABOUT Worker-03
```

That distinction is crucial.

### Hydra should contain relationships, not copies of giant memories

For example:

```text
(:WorkerVersion {id:"researcher-v7"})
   -[:MEMORY_STATE]->
(:MemoryCommit {git:"31fa..."})

(:WorkerVersion)
   -[:USED_SKILL]->
(:SkillVersion {git:"8cc1..."})

(:Run)
   -[:EXECUTED_BY]->
(:WorkerVersion)

(:Run)
   -[:TARGETED]->
(:Opportunity)

(:Run)
   -[:PRODUCED]->
(:Artifact)

(:Artifact)
   -[:ASSESSED_BY]->
(:AssessorRun)

(:AssessorRun)
   -[:SCORED]->
(:Criterion {name:"sponsor-integration"})

(:Run)
   -[:RESULTED_IN]->
(:Outcome {won:true})

(:LearningProposal)
   -[:SUPPORTED_BY]->
(:Run)

(:WorkerVersionV8)
   -[:MUTATION_OF]->
(:WorkerVersionV7)
```

Then genuinely interesting queries become possible:

```text
What memory revisions precede
improvements in rubric compliance?

Which skills transfer across
different opportunity families?

Which models improve quality
enough to justify their extra cost?

Which reusable assets contribute
to multiple winning artifacts?

Which learning proposals helped
on held-out tasks but failed in reality?

What paths connect a previous
failed submission to a later win?
```

That's where HydraDB earns its place.

And because the actual artifact, trajectory, memory and workspace are in Git/content-addressed storage, Hydra stores references and relationships rather than becoming a second messy blob store.

---

# 9. Git becomes the substrate for the entire experiment

This is where Letta × Git × Hydra gets particularly strong.

Think of every meaningful experimental object as having a Git identity:

```text
WorkerVersion
  memory_commit

SkillVersion
  skill_commit

Workspace
  workspace_commit

AssessorPack
  assessor_commit

OpportunityResearchPack
  research_commit

Experiment
  experiment_spec_commit
```

Then Hydra connects those commits.

WorkerKit attests which commits were actually used.

That makes a run approximately:

```text
Run R91

worker:
  researcher-03

worker_version:
  v7

memory:
  31faa7...

skills:
  c291da...

workspace_start:
  a13d2c...

opportunity_pack:
  abf921...

assessor:
  d39c10...

trajectory:
  sha256:...

artifact:
  sha256:...

cost:
  $0.38
```

This is exceptionally good experimental hygiene.

And later it naturally becomes the foundation for selling or leasing inventory because you already know exactly:

> what this worker is, how it was trained through experience, what artifacts it produced, which skills it contains, and what empirical evidence supports its capability.

But we don't need to build the marketplace now.

---

# 10. The missing hard problem is exactly what you identified: the assessor

This is probably **the most important Moltwork-specific thing to build**.

Suppose Oracle gives us:

```text
ETHOnline Sponsor Prize X
```

Before generating anything, the Lab should construct an independent model of:

> **What would actually maximize the probability of winning this?**

That can't just be the worker asking itself.

We need an `OpportunityResearchPack` and an `AssessorPack`.

```text
                 OFFICIAL SOURCES
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       rules        API docs    judging criteria
       FAQs         examples    past winners
          │            │            │
          └────────────┼────────────┘
                       ▼
             Opportunity Research
                       │
              evidence-grounded
                       ▼
             OpportunityResearchPack
                    /         \
                   /           \
                  ▼             ▼
          PUBLIC STRATEGY    HIDDEN EVAL
               PACK             PACK
                  │             │
                  ▼             │
               WORKER           │
                  │             │
                  ▼             │
               ARTIFACT ────────┘
```

The worker can see:

```text
requirements
public rubric
technical docs
known judging priorities
previous patterns
recommended strategy
```

It **must not see** all of the hidden checks the assessor will run.

That is how we avoid evaluation gaming.

---

# 11. Don't build the evaluation runner: use Letta Evals

This discovery substantially simplifies the plan.

`letta-ai/letta-evals` already supports:

* private JSONL datasets;
* programmatically created Letta agents;
* deterministic graders;
* rubric-based LLM graders;
* multiple graders and gates;
* multiple models;
* repeated runs with statistics;
* cached trajectories for re-grading;
* custom extractors/graders;
* isolated sandbox execution;
* CI integration. ([GitHub][15])

[Letta Evals repository](https://github.com/letta-ai/letta-evals?utm_source=chatgpt.com)

This is basically 60–70% of what our `cg` experimental execution layer wanted.

So instead of:

```text
Moltwork builds:
runner
dataset format
grader interface
sandbox
multi-run system
results
gates
```

we do:

```text
Moltwork Lab
     ↓
generates Letta Eval Suite
     ↓
letta-evals
     ↓
results
     ↓
Hydra
```

Our `cg` layer becomes primarily:

```text
ExperimentPlanner
TreatmentGenerator
AssessorBuilder
PromotionPolicy
CapabilityEstimator
```

Much smaller and much more interesting.

---

# 12. The assessor should have several independent layers

I would make it structurally similar to Telegraph's verifier philosophy, but **WASM is only useful for deterministic components**.

```text
ARTIFACT
   │
   ├────► G0: deterministic requirements
   │
   ├────► G1: technical execution
   │
   ├────► G2: evidence verification
   │
   ├────► G3: blinded rubric panel
   │
   ├────► G4: blinded pairwise comparisons
   │
   └────► G5: real-world outcome
```

### G0 — deterministic

Examples:

```text
required file exists
tests pass
API actually invoked
correct network used
required sponsor primitive present
deployment reachable
submission format valid
deadline/eligibility satisfied
```

These are excellent WASM candidates.

Freeze something like:

```text
assessor/
  manifest.json
  gates/
    requirements.wasm
    integration.wasm
    artifact.wasm
```

Run with Wasmtime, no network.

Content hash everything.

### G1 — technical evaluator

Can run repository tests, inspect logs, API traces, receipts and deployment state.

Again largely deterministic.

### G2 — evidence verifier

Every submission claim should become:

```json
{
  "claim": "Uses sponsor API for live retrieval",
  "evidence": ["trace:evt-821", "src:foo.ts:91"],
  "verified": true
}
```

A judge should not award points for unsupported claims.

### G3 — rubric jury

This is where LLM judges become necessary.

But don't trust one.

---

# 13. Modern LLM-as-judge research tells us how not to fool ourselves

2026 work shows rubric judges exhibit score-position bias; balanced permutations of rubric score positions improve agreement with human judgments. Other work finds substantial style biases and shows debiasing effectiveness differs across judge models. ([arXiv][16])

And simply adding lots of judges isn't sufficient: RoPoLL shows ordinary panel averaging can remain badly biased when even a minority of judges fails systematically, and proposes robust aggregation instead. ([arXiv][17])

So our judging protocol should be:

```text
Candidate identity hidden
Worker identity hidden
Worker version hidden

Judge A: model family 1
Judge B: model family 2
Judge C: model family 3

rubric score order permuted
candidate order permuted

pointwise evaluation
+
pairwise evaluation
+
evidence citations

then robust aggregation
```

An open evaluator like Prometheus can also provide a **pinned reproducible judge** alongside frontier API judges; Prometheus supports both absolute rubric grading and pairwise ranking. ([GitHub][18])

That's valuable because a cloud judge silently changing versions could otherwise contaminate months of experiments.

---

# 14. Even the assessor itself must be evaluated

This is important.

Suppose our Lab predicts:

```text
submission A = 84
submission B = 71
```

and B actually wins.

That's evidence that the **assessor is wrong**.

So Hydra should model:

```text
AssessorVersion
       ↓
predicted ranking
       ↓
real competition result
       ↓
calibration error
```

Eventually we learn:

```text
assessor-v3

technical quality:
  highly predictive

visual polish:
  underweighted

novelty:
  overestimated

sponsor API depth:
  strongly predictive

README score:
  almost useless
```

The Lab is therefore learning two things simultaneously:

```text
how to create better work
AND
how to judge work better
```

But critically, **worker and assessor evolution stay separate**.

A frozen assessor version evaluates Worker v7 → v8.

Only after that experiment closes can we update the assessor.

Otherwise we change the exam while changing the student.

---

# 15. The first real Moltwork experiment should be submission quality

This is a better checkpoint than generic memory QA.

Pick a repeatable task family:

```text
competitive technical submission
```

For example:

```text
given:
  competition docs
  sponsor requirements
  API docs
  judging rubric
  time/budget constraint

produce:
  strategy
  implementation proposal
  technical artifact
  submission narrative
```

Then construct:

```text
TRAINING OPPORTUNITIES
T01–T10

SEALED HELD-OUT OPPORTUNITIES
H01–H05
```

The Lab can let one persistent worker do T01–T10.

From those trajectories:

```text
raw trajectories
      │
      ├── ACE memory proposals
      ├── Trace2Skill skill proposals
      ├── failure patterns
      └── Lab/Hydra observations
```

Then create:

```text
researcher-v1
researcher-v2
```

And **only then** evaluate both independently on H01–H05.

---

# 16. A proper v1 → v2 experiment

Something like:

```text
                    BASE WORKER
                         │
                     researcher-v1
                         │
             ┌───────────┴───────────┐
             │                       │
          CONTROL               TRAINING RUNS
             │                       │
             │                 trajectories
             │                       │
             │             ┌─────────┴──────────┐
             │             ▼                    ▼
             │          ACE memory         Trace2Skill
             │           patches             skill
             │             └─────────┬──────────┘
             │                       ▼
             │                  researcher-v2
             │                       │
             └───────────┬───────────┘
                         ▼
                  SEALED TASK H01
                         │
                   same assessor
                         │
                  H02 H03 H04 H05
                         │
                         ▼
                  paired comparison
```

Hold constant:

```text
model
temperature
budget
tool permissions
research pack
deadline
assessor version
```

Change only:

```text
validated memory
validated skills
```

Now if v2 improves, we can actually say something.

---

# 17. Then start the factorial experiments

Once basic v1/v2 works, recover the more ambitious memory experiments we designed earlier.

Not different frameworks. Same Letta worker, different treatments:

```text
A
Letta native
no Lab context
no learning

B
Letta native
+ Hydra Lab brief

C
Letta native
+ validated learned memory/skills

D
Letta native
+ Lab brief
+ validated learned memory/skills
```

Which gives:

```text
           LAB OFF     LAB ON

V1           A            B

V2           C            D
```

That tells us separately:

```text
Does organizational memory help?

Does individual learning help?

Do they complement each other?
```

That was the much better version of our earlier loop.

---

# 18. Then test dreaming instead of assuming it works

Letta is itself pushing **sleep-time compute/dreaming** as a central continual-learning mechanism, where background reasoning converts raw context into learned context. ([Letta][19])

Excellent.

But Moltwork should be one of the places where we actually test:

```text
v1
no dreaming

v2
native Letta dreaming

v3
ACE curator

v4
Trace2Skill

v5
dreaming + Trace2Skill

v6
dreaming + Hydra organizational brief
```

Then measure:

```text
submission quality
requirements coverage
technical correctness
judge preference
cost
latency
real win rate
```

This is exactly the kind of experimentation Letta's ecosystem itself makes possible but doesn't solve for our economic domain.

---

# 19. The first checkpoint I would now define

Not marketplace.

Not five workers.

Not TEE.

Not autonomous money-making.

The checkpoint is:

> **One persistent Letta worker gets measurably better at competitive technical submissions through experience, and we can prove which persistent changes caused the improvement.**

A passing demo looks like:

```text
1. Oracle returns opportunity.
2. Moltwork freezes official opportunity evidence.
3. Lab produces StrategyPack + hidden AssessorPack.
4. researcher-v1 gets a fresh Letta session.
5. Worker produces submission.
6. WorkerKit records complete run.
7. @letta-ai/trajectory records experience.
8. letta-evals independently evaluates artifact.
9. Hydra records the complete relationship graph.
10. Repeat training tasks.
11. Trace2Skill/ACE produce candidate changes.
12. Candidate changes live in Git-backed Letta memory/skills.
13. researcher-v2 is instantiated.
14. v1 and v2 independently run sealed tasks.
15. Frozen assessor evaluates them blindly.
16. v2 wins paired evaluation materially.
17. Change is promoted.
18. New Oracle opportunity arrives.
19. v2 does real work.
20. Actual external result updates both worker capability and assessor calibration.
```

That is already a very serious private agent-learning laboratory.

---

# 20. The repo stack I'd actually study/clone

These are the ones I think materially matter rather than filling `/vendor` with cool projects:

| Project                                                                                          | Role                                                               |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| [letta-ai/letta-code](https://github.com/letta-ai/letta-code?utm_source=chatgpt.com)             | **Master this.** Harness, MemFS, dreaming, skills, subagents, Mods |
| [letta-ai/letta-agent-sdk](https://github.com/letta-ai/letta-agent-sdk?utm_source=chatgpt.com)   | Programmatic worker control                                        |
| `@letta-ai/trajectory`                                                                           | Canonical experience representation ([Letta][20])                  |
| [letta-ai/letta-evals](https://github.com/letta-ai/letta-evals?utm_source=chatgpt.com)           | Experimental execution/evaluation                                  |
| [letta-ai/mods](https://github.com/letta-ai/mods?utm_source=chatgpt.com)                         | Pattern for making Moltwork native to Letta                        |
| [mohammadtavakoli78/BEAM](https://github.com/mohammadtavakoli78/BEAM?utm_source=chatgpt.com)     | Long-memory benchmark + LIGHT                                      |
| [Qwen Trace2Skill](https://github.com/Qwen-Applications/Trace2Skill?utm_source=chatgpt.com)      | Trajectory → transferable skill                                    |
| [ACE](https://github.com/ace-agent/ace?utm_source=chatgpt.com)                                   | Context mutation/curation algorithm                                |
| [MemP](https://github.com/zjunlp/MemP?utm_source=chatgpt.com)                                    | Procedural-memory research baseline                                |
| [Agent Workflow Memory](https://github.com/zorazrw/agent-workflow-memory?utm_source=chatgpt.com) | Workflow induction baseline                                        |
| [HydraDB](https://github.com/hydra-db/hydradb?utm_source=chatgpt.com)                            | Lab experience/provenance graph                                    |
| [Prometheus Eval](https://github.com/prometheus-eval/prometheus-eval?utm_source=chatgpt.com)     | Pinned open judge                                                  |

I would **not** integrate Mem0/A-MEM/GraphRAG-style memory into production yet. I would not build our own trajectory format. I would not build a separate Skills abstraction. I would not build another eval runner. I would not make HydraDB the agent's recall mechanism by default. And I definitely would not build another orchestration framework around Letta.

The highest-leverage engineering now is to go deep enough into Letta that **Moltwork looks almost like an advanced experimental extension of Letta Code**.

That architecture also naturally gives us the later inventory thesis:

```text
real work
   ↓
trajectories
   ↓
validated lessons
   ↓
skills / memory / mods
   ↓
better WorkerVersion
   ↓
reusable code/assets/processes
   ↓
empirically valued inventory
```

Only after that do we have something worth packaging, leasing or selling.

I can monitor new Letta SDK releases, agent-memory papers, Trace2Skill/BEAM updates and HydraDB changes as this stack moves extremely quickly.

[1]: https://arxiv.org/abs/2510.27246 "[2510.27246] Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs"
[2]: https://arxiv.org/abs/2604.27003?utm_source=chatgpt.com "When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents"
[3]: https://arxiv.org/abs/2605.18421?utm_source=chatgpt.com "EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective"
[4]: https://www.letta.com/blog/introducing-the-letta-agent-sdk/?utm_source=chatgpt.com "Letta Agents SDK: An SDK for stateful agents | Letta"
[5]: https://www.letta.com/blog/context-repositories/?utm_source=chatgpt.com "Introducing Context Repositories: Git-based Memory for Coding Agents | Letta"
[6]: https://github.com/letta-ai/letta-code/blob/main/src/agent/prompts/letta.md?utm_source=chatgpt.com "letta-code/src/agent/prompts/letta.md at main · letta-ai/letta-code · GitHub"
[7]: https://github.com/letta-ai/mods?utm_source=chatgpt.com "GitHub - letta-ai/mods: Letta Code mod packages and examples · GitHub"
[8]: https://github.com/mohammadtavakoli78/BEAM?utm_source=chatgpt.com "GitHub - mohammadtavakoli78/BEAM: [ICLR 2026] Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs · GitHub"
[9]: https://arxiv.org/abs/2510.04618?utm_source=chatgpt.com "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models"
[10]: https://arxiv.org/abs/2603.25158?utm_source=chatgpt.com "Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills"
[11]: https://arxiv.org/abs/2508.06433?utm_source=chatgpt.com "Memp: Exploring Agent Procedural Memory"
[12]: https://github.com/WujiangXu/A-mem?utm_source=chatgpt.com "GitHub - WujiangXu/A-mem: The code for NeurIPS 2025 paper \"A-Mem: Agentic Memory for LLM Agents\" · GitHub"
[13]: https://github.com/hydra-db/hydradb/blob/main/README.md?utm_source=chatgpt.com "hydradb/README.md at main · hydra-db/hydradb · GitHub"
[14]: https://github.com/hydra-db/hydradb-mcp?utm_source=chatgpt.com "GitHub - hydra-db/hydradb-mcp: MCP server enabling HydraDB memory operations (store, recall, search) in AI coding tools · GitHub"
[15]: https://github.com/letta-ai/letta-evals?utm_source=chatgpt.com "GitHub - letta-ai/letta-evals: Evaluation kit for testing stateful agents · GitHub"
[16]: https://arxiv.org/abs/2602.02219?utm_source=chatgpt.com "Am I More Pointwise or Pairwise? Revealing Position Bias in Rubric-Based LLM-as-a-Judge"
[17]: https://arxiv.org/abs/2606.30931?utm_source=chatgpt.com "RoPoLL: Robust Panel of LLM Judges"
[18]: https://github.com/prometheus-eval/prometheus-eval?utm_source=chatgpt.com "GitHub - prometheus-eval/prometheus-eval: Evaluate your LLM's response with Prometheus and GPT4 💯 · GitHub"
[19]: https://www.letta.com/blog/sleep-time-compute/?utm_source=chatgpt.com "Sleep-time Compute | Letta"
[20]: https://www.letta.com/blog/trajectory/?utm_source=chatgpt.com "Trajectory: A Standard Format for Agent Experience Data | Letta"
