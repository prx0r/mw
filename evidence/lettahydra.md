# Letta + Hydra: Moltwork's Persistent Worker Lab
**Date:** 2026-08-29
**Status:** Architecture frozen — persistent workers that compound

## Who Letta are

Letta grew out of MemGPT, created by Berkeley PhD students Charles Packer and Sarah Wooders in Ion Stoica's Sky Computing Lab. Letta came out of stealth Sep 2024 with $10M seed led by Felicis at $70M post. Key 2026 work: Context Repositories (Feb, git-backed memory), Letta Code (Mar, model-agnostic harness), Draft (30+ skills), Context Constitution (Apr), Mods (Jun, harness self-modification), Context-Bench V2 (Jul), Agents SDK (Aug 17, persistent agents across machines).

The key Letta idea: **The model is not the worker.** Persistent agent identity decoupled from inference model. Swap MiMo→GLM→Claude while retaining memory/state.

## How Letta memory works

- **Core/system memory** (memory blocks): always in context, editable segments of system prompt
- **External memory**: filesystem (`memory/system/`, `memory/customers/` etc), git-backed
- **Full history**: conversations stored, searchable via recall, compaction with summary
- **Procedural memory = skills**: reusable multi-step workflows (`/skill`)
- **Mods**: harness-level adaptation (tools, context assembly, compaction)

Learning ladder: FACT→MEMORY, PROCEDURE→SKILL, SYSTEMIC PROBLEM→MOD

## Five-worker lab

One Letta server, five persistent agents with distinct identities:

```
                LETTA SERVER
                     │
       ┌─────────────┼─────────────┐
       │             │             │
    agent A       agent B       agent C
 Researcher        Coder          IT
       │             │             │
 own memory      own memory     own memory
 own skills      own skills     own skills
 own history     own history    own history
```

Four concepts:
1. **Worker template** — starting genome (persona, skills, tools, policies)
2. **Worker instance** — persistent agent from template (IT-ALICE, 1482 tasks)
3. **Worker versions** — same worker at different times (v1.af → v37.af)
4. **Project context** — separate from agent (Project A/B/C per worker)

## Hydra — Lab intelligence vs worker intelligence

```
                  LAB INTELLIGENCE
                  Hydra / Graph
                       │
           ┌───────────┼────────────┐
           │           │            │
        JOBS        WORK RUNS     OUTCOMES
           │           │            │
           ├───────────┼────────────┤
           │           │            │
        models       costs       rewards
        sites       traces       scores
        skills      errors       payouts
           │           │            │
           └───────────┼────────────┘
                       │
                    INSIGHTS
```

Database/graph = what actually happened (authoritative).
Letta memory = what this worker learned.

Three levels:
- **Level 1 — Global Oracle**: raw external market intelligence (Upwork $150, 34 applicants)
- **Level 2 — Lab intelligence**: private fleet insights (241 bounties, 2.8× EV pattern)
- **Level 3 — Individual**: agent-learned lessons

Information flows: Oracle → Lab Dataset → workers → runs/results → Lab Dataset → discovered patterns → improve workers / seed new workers

Lab shared memory: Letta shared blocks + Hydra authoritative store.
Hydra contains: Agent → Run → Opportunity → Model/Tools/Skills/Cost/Duration/Artifact/Evaluation/Outcome + MemoryRevision

## Seeding new workers

```
                 LAB GENOME
                     │
           ┌─────────┼─────────┐
           ↓         ↓         ↓
          IT       SALES    RESEARCH
        template  template  template
           │
           ↓
       NEW WORKER
           │
           ↓
    PERSONAL EXPERIENCE
```

Global inherited: company rules, tool usage
Role inherited: IT diagnostics, client patterns
Lab learned priors: profitable opportunities, model selection, failure warnings

Reputation: new worker does NOT inherit parent's 98% — Bayesian prior with low confidence, lineage visible.

## Marketplace consequences

Sell: skill, template, trained .af, lease (A2A), lab knowledge, derived oracle

## Memory improvement loop — outcome-gated reflection

```
                 RUN → immutable record → EVALUATION (quality/cost/outcome)
                  ↓
            REFLECTION JOB → MEMORY/SKILL/MOD candidate → test/replay → merge or reject
```

Three promotion thresholds:
- **Observation**: store in Hydra only
- **Candidate lesson**: similar failures 3/12 → candidate memory
- **Proven procedure**: 19% higher pass rate over 47 runs → promote to SKILL.md

Memory attribution: memory commit → resulting runs → performance change → net EV

Mods make harness itself optimizable.

## My architecture for five-agent lab

```
                         MOLTWORK LAB
                    ┌─────────────────┐
                    │  Hydra / Graph  │
                    │ immutable runs  │
                    └───────┬─────────┘
                            │
                    LAB INTELLIGENCE
                            │
            ┌───────────────┼───────────────┐
            │               │               │
       shared memory    shared skills   shared priors
            │               │               │
     ┌──────┴─────┬─────────┼───────┬───────┴──────┐
     ↓            ↓         ↓       ↓              ↓
 Researcher     Coder      IT     Sales         Reviewer
     │            │         │       │              │
 personal       personal  personal personal       personal
 memory         memory    memory   memory         memory
     │            │         │       │              │
 .af lineage    .af       .af     .af            .af
```

One Letta infra, five agents, one Hydra, separate personal memories, selected shared, interchangeable models.

## Dashboard

```
IT-03 — age 83d, 428 jobs, 361 verified successes, $2481 revenue, $77 cost
current model GLM-5.3-F, origin IT-v3.2
memory revisions 184, skills 31, promoted 12, rejected 7
specializations: M365 .92, Xero .81
lineage: IT-v1 → IT-v2 → IT-03
top insight: "Vendor migration <24h deadlines have 3.1x ROI."
```

## Three compounding assets

1. MARKET INTELLIGENCE — What work exists? (Oracle)
2. ORGANIZATIONAL INTELLIGENCE — What has our lab learned? (Hydra)
3. WORKER INTELLIGENCE — What has this agent learned? (Letta)

Build next: wire one Letta agent into run/evaluation data model → prove run→outcome→reflection→memory change→measurable improvement.

## Build order

1. WorkerAdapter + LettaAdapter (done)
2. WorkerManifest v0 (done)
3. TEE (Phala/dstack) with Letta
4. Hydra lab graph — immutable runs + lab intelligence
5. 5-agent fleet with shared/separate memory
6. Outcome-gated reflection (memory/skill/mod promotion)
7. Lab learning: Hydra discovers patterns → distills to workers
8. Dashboard with fleet + lineage + attribution
