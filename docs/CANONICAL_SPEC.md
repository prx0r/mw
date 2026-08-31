Yes. The more this is mapped, the more it looks like there are **four separate kinds of state**, and Git is the thing that makes them composable instead of turning Moltwork into one giant database.

> **Git = versioned intellectual property.**
> **Hydra = empirical knowledge about that IP.**
> **Letta = cognition that consumes selected empirical knowledge.**
> **CGE = controlled worlds that tell us whether changes actually work.**

Then Moltwork is the system operating the flywheel between them.

## 1. The practical unit isn't a “job”; it's a Campaign

An Oracle opportunity should instantiate a Git-native **Campaign**.

```text
Oracle Opportunity
       │
       ▼
Campaign
├── opportunity snapshot
├── source evidence
├── success model
├── public rubric
├── hidden assessor
├── WorldPack(s)
├── worker refs
├── experiment branches
├── submissions
├── trajectories
├── evaluations
└── final outcome
```

For a hackathon:

```text
campaigns/
  ethonline-2026-phala-prize/
    campaign.yaml

    opportunity/
      rules.md
      sponsor.md
      api-docs/
      evidence.json

    strategy/
      success-model.md
      rubric.yaml
      assumptions.md

    worlds/
      idea-generation.lock
      sponsor-integration.lock
      submission-quality.lock

    experiments/
      E001/
      E002/
      E003/

    submissions/
      candidate-a/
      candidate-b/
      final/

    outcome/
      result.json
      feedback.md
```

Crucially, almost everything can be a **reference to another Git commit** rather than copied material.

```yaml
worlds:
  idea_generation:
    repo: github.com/foo/idea-world
    commit: 71a93cf

  technical_submission:
    repo: github.com/moltwork/submission-world
    commit: bb82a91

worker:
  repo: private/researcher
  commit: 19df9aa
```

So the Campaign itself becomes reproducible.

---

# 2. Phase zero should be: model “what would win?”

This is extremely important.

Before the worker starts solving anything, a separate process constructs:

```text
Opportunity
     ↓
Researcher
     ↓
SuccessModel
```

The SuccessModel should answer:

```text
What are hard requirements?

What are actual judging dimensions?

Which requirements are merely eligibility?

Which factors likely distinguish winners?

What has historically won similar opportunities?

What does deep API/sponsor integration mean?

What failure modes kill otherwise-good submissions?

What uncertainty remains?
```

For example:

```yaml
success_model:
  hard_gates:
    eligibility: true
    required_api_used: true
    functioning_demo: true

  dimensions:
    sponsor_native_depth: 0.25
    technical_execution: 0.20
    originality: 0.15
    problem_value: 0.15
    completeness: 0.10
    evidence: 0.10
    presentation: 0.05

  uncertainty:
    originality_weight: high
    presentation_weight: medium
```

That then **compiles into CGE worlds/evaluators**.

The worker sees the public success strategy.

The worker does not necessarily see every hidden test.

---

# 3. The agent first asks Hydra: “Have we solved anything like this?”

Before generating ideas from scratch:

```text
Opportunity
     ↓
ontology mapping
     ↓
Hydra query
```

Example ontology:

```text
task_family:
competition.technical_submission

capabilities:
requirements.extract
opportunity.research
idea.generate
solution.select
technical.architecture
sponsor.integrate
artifact.build
submission.communicate
```

Now Hydra can query all prior experience involving those capabilities.

The interesting queries are graph-shaped:

```text
Which previous campaigns
share this capability profile?

Which WorkerVersions did best?

Which Worlds predicted the real outcome?

Which Skills appeared in winning paths?

Which processes repeatedly failed?

Which assessor versions agreed with
the eventual external result?

Which assets from previous projects
were reused successfully?
```

Hydra is particularly appropriate because its current architecture has canonical property graphs, OpenCypher queries, relationship indexes and native path algorithms. Its `SPpaths`, `SSpaths`, and especially batched `MSpaths` procedures support traversing relationships among many source/target nodes under one pinned database snapshot.

So eventually Moltwork can ask across hundreds of prior assets:

```text
[all idea-generation skills]
            ↓
[WorkerVersions]
            ↓
[campaign runs]
            ↓
[technical submissions]
            ↓
[assessments]
            ↓
[actual competition outcomes]
```

without manually joining twelve relational tables.

---

# 4. But Hydra should never be the canonical thing

This invariant should be strict:

```text
Git / WorkerKit
      =
CANONICAL EVIDENCE

Hydra
      =
DERIVED KNOWLEDGE GRAPH
```

Hydra itself is designed with a similar principle internally: traversal indexes are accelerators, while canonical graph records remain the source of truth under pinned snapshots.

For Moltwork:

```text
git commit disappeared?
BAD

WorkerKit receipt disappeared?
BAD

Hydra database disappeared?
REBUILD IT
```

That is very healthy architecture.

---

# 5. Then the Campaign chooses between imitation and exploration

This is where the Lab gets interesting.

Suppose Hydra says:

```text
Similar campaign history:

C21 LOST
C26 LOST
C31 WON
C44 WON
```

And both winners shared:

```text
explicit requirement extraction
3 candidate ideas before selection
API proof before full build
external review before submission
```

Then the Lab can initially exploit:

```text
COPY WINNING PROCESS FAMILY
```

Not copy the submission.

Copy the **validated process**.

```text
Opportunity research
→ requirements matrix
→ divergent ideation
→ feasibility pruning
→ sponsor-native scoring
→ prototype
→ independent assessor
→ repair
→ final review
```

That process itself should be a Git asset:

```text
processes/
  hackathon-winning-loop/
    PROCESS.md
    pipeline.yaml
    world-bindings.yaml
```

If no winning history exists:

```text
INSUFFICIENT_EVIDENCE
       ↓
EXPAND SEARCH SPACE
```

Now the Lab might commission:

```text
arXiv research
GitHub research
past winner analysis
alternative ideation techniques
different models
different agent configurations
new World variants
```

This is essentially CGE's **space expansion** mechanism applied to real economic work.

---

# 6. Idea generation itself becomes an experimental search problem

Instead of one agent saying:

> “Here's my idea.”

Do:

```text
                    Idea World
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
  treatment A      treatment B      treatment C

  Letta v7          Letta v7         Letta v7
  normal            + skill          + Hydra brief

       │               │                │
       ▼               ▼                ▼
     ideas            ideas            ideas
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                 blind assessor
                       ↓
                 top candidates
                       ↓
                 deeper research
                       ↓
                 next round
```

This lets you use successive halving from CGE:

```text
20 cheap ideas
  ↓
8 decent ideas
  ↓
3 researched ideas
  ↓
2 prototypes
  ↓
1 submission
```

Much better economically than spending full coding effort on every idea.

---

# 7. The Campaign worker loop then becomes iterative review

Once a candidate is selected:

```text
BUILD
  ↓
ASSESS
  ↓
DIAGNOSE
  ↓
REPAIR
  ↓
ASSESS
  ↓
...
```

But each iteration is a meaningful Run:

```text
Run 17
WorkerVersion v8
Artifact commit 91ac...
WorldVersion 72fa...
AssessorVersion 8b13...
score .72

Run 18
Artifact commit e12c...
same worker/world/assessor
score .81
```

The campaign ends when either:

```text
all hard gates pass
AND
score >= submission threshold
AND
marginal improvement EV <= cost
```

or budget/deadline forces submission.

That last condition matters.

You don't want an infinite self-review loop.

---

# 8. Letta Evals fits very naturally inside this

Current Letta Evals already emits detailed per-sample results containing submissions, grades, rationale, full trajectories, agent IDs, model info, costs and token usage. ([Letta Docs][1])

It can also evaluate multi-turn behavior and directly inspect agent memory state rather than merely judging its visible response. ([Letta Docs][2])

That gives you two classes of World:

### Output Worlds

```text
Did it make a good submission?
Did the code work?
Was the strategy good?
```

### Learning Worlds

```text
Did it remember feedback?

Did it update an obsolete belief?

Did it generalize repeated corrections?

Did it retrieve the right prior experience?

Did it avoid a known failure?
```

That's important.

Because a worker may improve its artifact without improving its long-term cognition—or vice versa.

---

# 9. The end of submission is only half of the WorkerRun

This is where your “molting” concept gets good.

The WorkerRun lifecycle should be:

```text
PRE-WORK
↓
WORK
↓
EXTERNAL OUTCOME
↓
POST-WORK MOLTING
```

Post-work should explicitly ask:

```text
What did this Campaign create?

What should be retained?

What should become reusable?

What should change in the Worker?

What should change in the World?

What should change in the Assessor?

What was only temporary campaign state?
```

---

# 10. Molting should produce typed candidate assets

Not one generic “lesson.”

```text
Campaign
   ↓
Molter
   │
   ├── MemoryCandidate
   ├── SkillCandidate
   ├── ProcessCandidate
   ├── WorldCandidate
   ├── AssessorCandidate
   ├── SchoolCandidate
   ├── CodeAssetCandidate
   ├── ResearchAssetCandidate
   └── HarnessCandidate
```

Examples:

### Memory

> Judges in sponsor tracks care about actual invocation evidence, not merely architectural claims.

### Skill

```text
sponsor-requirements-extractor/
  SKILL.md
```

### Process

```text
3-stage-hackathon-idea-selection/
```

### Evaluator

```text
sponsor-native-depth-v3/
```

### School

```text
technical-hackathon-school/
```

### Code asset

```text
verified-x402-payment-module/
```

Each starts as a **candidate branch**.

Not instantly production.

---

# 11. Then CGE tests the molt

```text
parent WorkerVersion v8
          │
          ├──── control
          │
          └──── candidate + new asset
                         │
                         ▼
                    sealed Worlds
                         │
                         ▼
                 paired evaluation
```

If the candidate succeeds:

```text
merge
tag
update Hydra
```

If it fails:

```text
don't merge
BUT KEEP EXPERIMENT
```

That last part is critical.

Failed knowledge is knowledge.

Hydra should remember:

```text
Skill S17
looked promising
but failed:
competition.idea_generation
and increased cost 41%
```

The next Letta worker should not waste effort rediscovering that.

---

# 12. Letta should receive distilled conclusions, not raw runs

Letta's current philosophy is already compatible with this. Its docs explicitly frame agents as becoming more valuable with repeated use, retaining corrections and searching past conversations, while fresh conversations can share one persistent memory state. ([Letta Docs][3])

But Moltwork should put a scientific governor around that.

```text
RAW RUNS
    ↓
WorkerKit + Trajectory
    ↓
Hydra
    ↓
Lab analysis
    ↓
experiment
    ↓
validated finding
    ↓
Letta MemFS / Skill
```

Not:

```text
RAW RUN
 ↓
LLM reflection
 ↓
production memory
```

That distinction protects the worker from memory pollution.

---

# 13. Specialized Labs then make complete sense

A Lab can define a narrow domain ontology slice.

For example:

```text
LAB: customer-support
```

It follows:

```text
Oracle:
customer-support demand

Git:
support worlds
support schools
support skills
support workers
support assessors

Research agents:
latest papers
latest frameworks
real support failures
company policies

Hydra:
all internal support experience

Letta:
specialized durable support workers
```

Over months:

```text
generic support agent
       ↓
billing specialist
refund specialist
SaaS support specialist
technical escalation specialist
```

A different Lab might specialize in:

```text
hackathons
SEO
technical research
software freelancing
bookkeeping
QA
```

Specialization makes all experience denser and more transferable.

That's exactly how the lab itself becomes valuable.

---

# 14. Roles naturally emerge without hard-coding a “fleet”

Instead of saying:

> five agent types forever,

let the Lab create roles according to economic need.

You might eventually have:

```text
SCOUT
find opportunities

ANALYST
construct SuccessModels

WORLD BUILDER
build/maintain benchmarks

TEACHER
construct Schools

CAMPAIGN WORKER
do the actual work

REVIEWER
assess artifacts

SCIENTIST
design experiments

MOLTER
extract reusable assets

LIBRARIAN
maintain memory/skills

ASSET ENGINEER
package reusable code/processes
```

All can still be Letta agents.

And you can experimentally measure whether having a dedicated specialist is worth its cost.

---

# 15. This creates an interesting internal economy before any marketplace

Your private Lab can already pretend assets have prices.

Example:

```text
Evaluator E17
cost per call: $0.003

World W8
expected information value: $0.20

Reviewer agent
expected quality lift: +0.06
cost: $0.08

School S3
expected capability delta: +0.11
training cost: $1.20
```

Then campaign planning becomes:

```text
Do I spend another $0.30 improving this submission?

Do I pay for five more idea evaluations?

Do I retrain this worker first?

Do I use the premium evaluator?

Do I reuse the free local World?
```

This is where LiveLLM/cost intelligence later plugs in naturally.

---

# 16. The future evaluator marketplace is especially strong

I think your `$0.01 evaluator` idea is one of the clearest marketplace objects.

Imagine:

```text
Evaluator:
hackathon/sponsor-integration-v9

Price:
$0.01 / assessment

Validated on:
143 historical submissions

Pairwise agreement with actual rankings:
0.81

Recent calibration:
0.84

WorldValidityClaims:
18

Execution:
TEE attested
```

An agent doing a WorkerRun can simply decide:

```text
local evaluator      expected quality .68     free

public evaluator A   expected quality .74     $.002

premium evaluator B  expected quality .83     $.01
```

and select based on expected information value.

That's an actual agent economy rather than humans browsing a marketplace manually.

---

# 17. TEE is almost perfect for private evaluator IP

There are two opposing requirements:

### Evaluator seller wants:

```text
keep:
rubric secret
hidden cases secret
judge prompts secret
calibration logic secret
```

### Buyer wants:

```text
keep:
submission secret
code secret
strategy secret
```

TEE gives a plausible boundary.

```text
BUYER
 encrypted submission
       │
       ▼
┌─────────────────────────┐
│        TEE CVM          │
│                         │
│ Evaluator commit E91    │
│ Hidden rubric           │
│ private scenarios       │
│ judge logic             │
│                         │
│ Seller cannot inspect   │
│ plaintext execution     │
└───────────┬─────────────┘
            │
            ▼
 evaluation
 + signature
 + evaluator version
 + attestation
```

Phala's current stack can expose an application's remote attestation quote and VM/app configuration. The verifier can check that the CVM is running on genuine TEE hardware and that the expected application configuration/code measurement is loaded. ([Phala Docs][4])

Phala also documents per-response signatures for confidential model inference, where a response can be cryptographically tied to a signing key that is itself bound to attestation. ([Phala Docs][5])

So an eventual evaluator response could include:

```json
{
  "evaluator": "hackathon-native-depth",
  "version": "e91a17c",
  "score": 0.84,
  "feedback": {...},

  "input_digest": "sha256:...",
  "output_digest": "sha256:...",

  "tee_signature": "...",
  "attestation_ref": "...",
  "world_claim": "..."
}
```

---

# 18. But there are three different proofs

Do not collapse these.

### Git/GitHub attestation

Proves:

> **this artifact came from this source/commit/build.**

GitHub Artifact Attestations bind a built artifact to its repository, commit SHA, workflow and triggering event via Sigstore. GitHub explicitly warns that this does not prove the artifact itself is secure or correct. ([GitHub Docs][6])

### TEE attestation

Proves:

> **this particular code/environment ran confidentially and unmodified.**

Phala's attestation covers the hardware/OS/application measurement chain. ([Phala Docs][7])

### Moltwork WorldValidityClaim

Proves empirically:

> **this evaluator appears to predict something useful.**

Example:

```text
agreement with real judges
rank correlation
pairwise accuracy
false-positive rate
calibration
historical n
```

The third is the economically valuable proof.

---

# 19. Evaluator calibration itself should be continuous

The frontier research reinforces this.

Recent work on evaluator-feedback loops finds that evaluator biases can propagate into the strategies agents learn; probability calibration reduced that coupling in a controlled experiment. ([arXiv][8])

And February 2026 work on LLM juries found judge reliabilities vary substantially, proposing a judge-aware Bradley–Terry method that jointly estimates candidate ranking and judge reliability rather than simply averaging judges. ([arXiv][9])

This implies Hydra needs:

```text
AssessorVersion
  │
  ├── JudgeModel A
  ├── JudgeModel B
  ├── JudgeModel C
  │
  ├── Prediction P17
  ├── Prediction P18
  └── Prediction P19
            │
            ▼
      external outcomes
```

Then it learns:

```text
Judge A:
great technical discriminator
bad novelty judge

Judge B:
strong presentation ranking

Judge C:
poor calibration
```

This is much better than “three judges and average.”

---

# 20. Git gives you an incredible asset-development environment

There are several primitives I'd explicitly exploit.

### Worktrees = experimental variants

```text
main
├── worktree/control
├── worktree/memory-candidate
├── worktree/skill-candidate
└── worktree/process-candidate
```

Letta already uses Git-backed context/worktree concepts for memory evolution, so this fits its native architecture instead of fighting it.

### Bisect = regression finder

```text
Worker v12 score .88
Worker v24 score .69
```

Automatically binary-search memory/skills/config commits against a World.

This is one of the coolest unexplored uses.

### Notes = attach evolving empirical metadata

```text
commit e1912a

git note:
validated on:
W7 W9 W22

paired delta:
+.11

Hydra:
claim://C281
```

No need to rewrite the original object.

### Tags = promoted/certified releases

```text
worker/researcher/v9
world/idea-generation/v4
school/support/v3
assessor/hackathon/v7
```

Branches represent candidates.

Tags represent releases.

### Git bundles = portable paid asset delivery

Later, a purchased asset could literally be a Git bundle containing the selected refs and history.

No proprietary serialization needed.

---

# 21. Reusable GitHub workflows turn Worlds into agent CI

GitHub explicitly supports reusable workflows so other repos can call centrally maintained workflows rather than duplicating them. ([GitHub Docs][10])

So a World could ship:

```text
.github/workflows/evaluate.yml
```

A worker repo calls:

```text
hackathon-idea-world@v4
```

and gets:

```text
requirements       0.91
technical          0.84
novelty            0.73
evidence           0.88

overall             .83

baseline            .78
delta               +.05
```

This is powerful framing:

> **Worlds are unit tests for agent capabilities.**

Schools are training suites.

Campaigns are integration tests against economic reality.

---

# 22. Hydra becomes your internal “what actually works?” engine

Over time the graph contains:

```text
Opportunity
     │
Campaign
     │
Run
     ├──────── WorkerVersion
     │             │
     │          Memory
     │          Skills
     │          Process
     │          Model
     │
     ├──────── WorldVersion
     │
     ├──────── AssessorVersion
     │
     ├──────── Artifact
     │
     ├──────── Decisions
     │
     └──────── Outcome
```

Now the Lab can ask increasingly sophisticated questions:

```text
Which process is best for hackathons?

Which process works specifically
with researcher-v7?

Which skill only works with strong models?

Which memory causes regression on customer support?

Which School creates transferable gains?

Which evaluator predicts real customer satisfaction?

Which asset is repeatedly reused in paid work?

Which World no longer discriminates between workers?

Which agent configuration has highest expected
profit per dollar for this opportunity class?
```

That's the real compounding asset.

---

# 23. And then Hydra feeds Letta at three different time scales

I wouldn't just have one “Lab brief.”

### Immediate: Campaign context

```text
You are working opportunity X.

Relevant prior finding:
submission processes using requirement matrices
won 4/6 comparable tasks.

Use process P7.
```

Ephemeral. Doesn't change permanent memory.

### Medium-term: task-family briefing

```text
For competition.technical_submission:
known strengths...
known failures...
validated processes...
```

Retrieved when relevant.

### Long-term: worker cognition

Only validated, generalizable findings become:

```text
MemFS
Skills
Mods
```

This prevents the worker from turning into a junk drawer.

---

# 24. The complete flywheel is therefore bigger than “find job → do job”

It is:

```text
                    ORACLE
                       │
                       ▼
                 OPPORTUNITY
                       │
                       ▼
                  CAMPAIGN
                       │
               SuccessModel
                       │
               CGE Worlds
                       │
                       ▼
                HYDRA RECALL
                       │
        winning formula exists?
              /                \
            yes                 no
             │                  │
             ▼                  ▼
         exploit             explore
         process           expand space
             │                  │
             └─────────┬────────┘
                       ▼
                  LETTA WORKER
                       │
             idea/build/review
                       │
                       ▼
                 EVALUATORS
                       │
              repair / iterate
                       │
                       ▼
                   SUBMIT
                       │
                       ▼
              EXTERNAL OUTCOME
                       │
                       ▼
                    HYDRA
                       │
                POST-RUN MOLT
                       │
     ┌────────┬────────┼───────────┬────────┐
     ▼        ▼        ▼           ▼        ▼
   memory   skills   process     world    assessor
     │        │        │           │        │
     └────────┴────────┼───────────┴────────┘
                      ▼
               candidate branches
                      │
                      ▼
                CGE experiments
                      │
               promote/reject
                      │
                      ▼
                 Git releases
                      │
                      ▼
              BETTER NEXT RUN
```

That is the system.

## The deepest thesis

The marketplace doesn't need to invent things to sell.

The Lab continuously creates sellable things as a **by-product of doing work well**:

```text
worker configs
memories
skills
processes
evaluators
Worlds
Schools
code modules
research packs
validated combinations
```

And unlike normal prompt marketplaces, every asset can potentially accumulate evidence:

```text
Git provenance
+
WorkerKit receipts
+
CGE experiments
+
Hydra relationships
+
real economic outcomes
```

Then TEE execution gives private assets a way to remain proprietary while still being callable and verifiable.

So yes: this naturally supports a future where one specialized Lab may primarily earn by doing customer-support work, another primarily develops support evaluators, another specializes in training Schools, and another owns highly validated workers. Moltwork's marketplace simply makes those **Git-native capability assets economically composable**.

The immediate technical target should stay much narrower: get **one Campaign** through this entire lifecycle—opportunity → SuccessModel → World → Letta run → iterative assessment → submission → outcome → Hydra projection → molting → candidate Skill/World improvement. Once that works once, almost everything else in the larger vision is iteration rather than architecture.

[1]: https://docs.letta.com/guides/evals/results/overview/?utm_source=chatgpt.com "Understanding results | Letta Docs"
[2]: https://docs.letta.com/guides/development-tools/testing-evals/advanced/multi-turn-conversations?utm_source=chatgpt.com "Multi-turn conversations | Letta"
[3]: https://docs.letta.com/guides/ade/desktop/?utm_source=chatgpt.com "Quickstart | Letta Docs"
[4]: https://docs.phala.com/phala-cloud/attestation/get-attestation?utm_source=chatgpt.com "Phala Cloud Documentation — Confidential AI on TEE"
[5]: https://phalanetwork-1606097b.mintlify.app/phala-cloud/confidential-ai/confidential-model/api-reference/signature?utm_source=chatgpt.com "Phala Cloud Documentation — Confidential AI on TEE"
[6]: https://docs.github.com/en/actions/concepts/security/artifact-attestations?utm_source=chatgpt.com "Artifact attestations - GitHub Docs"
[7]: https://docs.phala.com/phala-cloud/attestation/overview?utm_source=chatgpt.com "Phala Cloud Documentation — Confidential AI on TEE"
[8]: https://arxiv.org/abs/2606.31371?utm_source=chatgpt.com "Calibrating the Evaluator: Does Probability Calibration Mitigate Preference Coupling in LLM Agent Feedback Loops?"
[9]: https://arxiv.org/abs/2602.16610?utm_source=chatgpt.com "Who can we trust? LLM-as-a-jury for Comparative Assessment"
[10]: https://docs.github.com/en/actions/concepts/workflows-and-actions/reusing-workflow-configurations?utm_source=chatgpt.com "Reusing workflow configurations - GitHub Docs"
