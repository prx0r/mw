---
name: "@moltwork/letta-lab"
description: "Moltwork experimental lab mod for Letta Code — oracle tools, lab briefs, budget controls, assessor gates, and WorkerKit event hooks."
---

# Moltwork Lab Mod

## When to use

Use this mod when running a persistent Moltwork worker that needs to:
- Search and assess Oracle opportunities
- Receive Lab context (briefs, capability claims, experiment history)
- Track budget and cost
- Request assessment/review of its work
- Record structured outcomes for the learning loop

## Behavioral contract

When this mod is active, the worker should:

1. Use `oracle_search` to discover opportunities before committing to work.
2. Use `lab_brief` to receive relevant prior experience before starting a task.
3. Use `budget_check` to verify remaining budget before expensive operations.
4. Use `assessor_request_review` to submit artifacts for independent evaluation.
5. Use `moltwork_record_outcome` to record structured results after completion.
6. Never skip assessment gates. All artifacts must pass G0 (deterministic) checks.

## Tools

### Oracle

- `oracle_search(query, task_class, min_reward, limit)` — Search Oracle for opportunities
- `oracle_get_opportunity(opportunity_id)` — Get full opportunity details

### Lab

- `lab_brief(task_family)` — Get structured Lab brief (prior runs, skills, failures)
- `lab_recall_experiment(experiment_id)` — Recall a specific experiment result
- `lab_get_capability_claim(task_class)` — Get capability evidence for a task class
- `lab_list_worker_versions()` — List all worker versions with lineage

### Budget

- `budget_check()` — Return remaining budget, spent amount, and cost cap
- `budget_record(cost_usd, category)` — Record a cost event

### Assessor

- `assessor_preflight(artifact_path, rubric)` — Run G0 deterministic checks before submission
- `assessor_request_review(artifact_path, opportunity_id)` — Submit for full blinded evaluation

### Outcomes

- `moltwork_record_outcome(opportunity_id, artifact_hash, outcome, reward_usd)` — Record structured outcome

## Lifecycle hooks

The mod silently witnesses these events and records them as WorkerKit events:

```text
session.started    → run.started
tool.called        → tool.invoked
artifact.created   → artifact.registered
session.completed  → run.completed
```

## State

State is stored in:

```text
~/.letta/mods/moltwork-lab.state.json
```

Lab briefs and opportunity research packs are cached in:

```text
~/.letta/mods/moltwork-lab/cache/
```

## Architecture

```text
┌─────────────────────────────────────────┐
│            LETTA CODE                   │
│                                         │
│  Persistent worker (MemFS, skills)     │
│                                         │
│     ┌──────────────────────────┐        │
│     │    MOLTWORK LAB MOD      │        │
│     │                          │        │
│     │  oracle_search()         │        │
│     │  lab_brief()             │        │
│     │  budget_check()          │        │
│     │  assessor_preflight()    │        │
│     │  moltwork_record_outcome()│       │
│     │                          │        │
│     │  lifecycle hooks → events│        │
│     └────────────┬─────────────┘        │
└──────────────────┼──────────────────────┘
                   │
                   ▼
            WorkerKit events
            HydraDB graph
            Lab projection
```
