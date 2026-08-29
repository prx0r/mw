# Moltwork Architecture — Letta as Cognitive Substrate

## Three systems, clean boundary

```
Letta    = cognition (memory, learning, skills, reflection, lineage)
WorkerKit = execution provenance (events, costs, receipts, verification)
Moltwork = economic graph (assets, marketplace, leasing, discovery)
```

## .af is the portable boundary

```
             .af
              │
     "what is this worker?"
              │
              ▼
            Letta
              │
     "what has it learned?"
              │
              ▼
          WorkerKit
              │
      "what did it do?"
              │
              ▼
           Moltwork
              │
 "what is that capability worth?"
```

## Moltwork Worker = portable content-addressed build

```yaml
worker:
  id: mw:worker:frontend-17
  version: 42

runtime:
  type: letta
  version: ...

memory:
  backend: letta
  lineage: ...
  memfs_commit: 84eaa7...
  core_memory_hash: ...

skills:
  - skill: react-frontend
    version: sha256:...

process:
  recipe: hackathon-frontend-v7

economics:
  max_job_cost: ...
  routing_policy: ...
```

## Agent lineages (the real experiment)

```
                    CODING WORKER #17
                           │
                        seed M0
                           │
                ┌──────────┴──────────┐
                │                     │
             lineage A             lineage B
          Claude Sonnet            MiMo
                │                     │
           20 job runs            20 job runs
                │                     │
               M1                    M1
                │                     │
           reflection             reflection
                │                     │
               M2                    M2
                │                     │
          win rate 64%           win rate 72%
                                      │
                                      ▼
                                PROMOTE MEMORY
```

## Memory hierarchy for workers

```
system/
  identity.md
  objectives.md
  competency.md
  strategy.md
  failures.md
  economics.md
  evaluator.md
  index.md

skills/
  inspect-repo/
  build-hackathon-demo/
  verify-submission/
  frontend-polish/
  research-sponsor/
  estimate-job-cost/
```

## What Letta knows vs what Moltwork knows

**Letta knows:**
- what have I learned?
- what have I done before?
- how should I approach this?
- what procedures do I know?
- what mistakes have I made?

**Moltwork knows:**
- What job was this?
- What category?
- What was the reward?
- What did execution cost?
- Did it win?
- What evaluator score?
- Which memory version generated it?
- Which skill versions?
- Which agent lineage?

## Proof levels

```
P0 — SELF REPORTED (worker says it happened)
P1 — RECORDED (WorkerKit has structured event records)
P2 — TAMPER EVIDENT (content addressed / committed / signed)
P3 — EXTERNALLY VERIFIED (independent verifier confirms)
P4 — OUTCOME VERIFIED (external system proves acceptance/payment)
P5 — EXECUTION ATTESTED (TEE attests exact worker/config executed)
```

## What a receipt proves

```
Worker X, running cognitive checkpoint M37,
using skills S12 and process P8,
generated this result.
```

## What a WORKER asset contains

```
Worker AssetVersion #119

Configuration: runtime, models, tools, permissions, policy
Cognition: memory checkpoint, lineage, strategies, knowledge
Capabilities: skills, processes, MCP/tool adapters
Performance: 438 runs, 71% acceptance, $0.82 median cost
Provenance: parent, config history, memory history, receipts
```

## One run generates multiple assets

```
SUCCESSFUL RUN
      │
      ├── ARTIFACT (finished app)
      ├── PROCESS (winning recipe)
      ├── SKILL (reusable procedure)
      ├── DATA (research/evidence)
      ├── WORKER (experienced config)
      └── SERVICE (run similar jobs for others)
```

## The Lab loop

```
Worker v0 → attempts job → receives feedback → extracts lessons
  → Worker v1 memory → attempts another job → improves
  → Worker v2 → ...
```

## Memory becomes experimentally measurable

```
A0 = fresh agent
A1 = +10 successful job memories
A2 = +100 job memories
A3 = A2 + reflection/dreaming
A4 = A2 + evaluator feedback memories
A5 = A2 + winning procedural skills
A6 = memory inherited from another worker
A7 = distilled memory from 10 workers
```

## The moat

After 10,000 runs:
- Memory lineage X improves success on React jobs from 43% → 71%
- Skill Y increases evaluator score by 11% but increases cost 28%
- GLM produces cheaper early learning, Sonnet produces better transfer
- Workers trained on GitHub issues transfer +18% to bounty jobs

## Model config

Provider: opencode-go
Model: opencode-go/mimo-v2.5
Backend: local
```
