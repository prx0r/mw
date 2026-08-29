# Letta MVP Plan — Real Learning Loop

## The Narrow Proof

> A persistent Letta worker performs a family of tasks, accumulates usable experience, receives Lab context from previous runs, adopts one validated memory/skill/process improvement, and subsequently performs better on unseen tasks.

```
Worker v1
   │
   ├── baseline evaluation on hidden tasks (NO Lab context)
   │
   ├── 5–10 training runs
   │       ↓
   │    artifacts + evaluations + reviews + trajectories + outcomes
   │       ↓
   │    Hydra Lab experience
   │
   ├── Letta reflection
   │       ↓
   │    LearningProposal
   │
   ├── cg validates proposal
   │
   └── Worker v2
           ↓
      SAME held-out distribution
           ↓
      compare v1 vs v2
```

If `v2 > v1` on genuinely unseen tasks and you can point to **what changed**, you have the first real Moltwork result.

---

## Phase A — Baseline

Create `Researcher-v1`. Run on 8 hidden/evaluation tasks. Save artifact, requirements score, novelty score, evidence score, diversity score, overall gate result, cost, trajectory. Do NOT give it historical Lab context. Call this BASELINE.

## Phase B — Experience

Give the same persistent Worker 5–10 training tasks. For every one: execute → evaluator → reviewer → structured feedback → Hydra.

## Phase C — Context-only test

Before mutating memory, re-evaluate the worker with same persistent Worker v1 + Lab Brief on fresh tasks. This tells you: does organizational retrieval itself improve performance?

## Phase D — Learned Worker

Let Letta examine training trajectories + reviews. Propose one memory/Skill change. Run cg. If validated: Researcher-v2.

## Phase E — Held-out comparison

Evaluate Researcher-v1 + Lab vs Researcher-v2 + Lab on the same fresh held-out suite. Now you separately measure VALUE OF LAB CONTEXT and VALUE OF PERSISTENT LEARNING.

---

## Use the current Letta stack

Do NOT build against the old Python/REST Letta server. Letta's old `letta-ai/letta` repository is officially maintenance-mode. Active work is in **Letta Code**, and applications should use the new **TypeScript Letta Agent SDK**.

Current Agent SDK gives you:
- Agent = persistent identity + memory
- Conversation = one thread belonging to that agent
- Session = active connection/execution environment

`createSession(agentId)` creates a new conversation while retaining the same persistent agent; `resumeSession()` restores an existing conversation.

## For MVP: use Letta `backend: "local"`

```bash
node --version  # needs 22.19+
npm install @letta-ai/letta-agent-sdk @letta-ai/trajectory tsx typescript
```

Local Agent SDK execution requires Node 22.19+ and runs the Letta harness/App Server on the current computer. No Letta account is needed.

```ts
const client = new LettaAgentClient({ backend: "local" });
const agentId = await client.createAgent({
  model: configuredModel,
  memory: [
    { label: "persona", value: "You are a specialist Moltwork research worker." },
    { label: "moltwork", value: "Use evidence. Follow task requirements exactly. Treat Lab context as evidence, not ground truth." }
  ]
});
```

Persist: `moltwork_worker_id → letta_agent_id`. Never pick the first Letta agent from `/agents`.

## Every Moltwork Run gets a new Letta session

Don't reuse one giant conversation. For every WorkOrder:

```ts
const session = client.createSession(agentId, {
    cwd: runWorkspace,
    toolset: { base: "none", include: ["Read", "LS", "Glob", "Grep"] },
    allowedTools: ["Read", "LS", "Glob", "Grep", "moltwork__*"]
});
```

WorkOrder policy translates → Letta execution policy.

## Give Letta Moltwork as a tiny tool surface

For MVP:
- `moltwork_lab_context`
- `moltwork_run_budget`
- `moltwork_get_artifact_requirements`
- `moltwork_request_review`
- `moltwork_record_candidate`

Use SDK client tools / direct app integration rather than MCP for the first version.

## MemFS is where Worker learning should live

All current Letta agents use MemFS, a git-backed memory repository. Files under `system/` are always loaded. Files elsewhere are progressively disclosed.

```
MemFS/
  system/
    identity.md
    operating-principles.md
  research/
    source-quality.md
    task-patterns.md
  failures/
    recurring-failures.md
  skills/
    requirements-audit/SKILL.md
    evidence-research/SKILL.md
```

## Letta's learning distinction

- durable fact/correction → MEMORY
- repeatable multi-step workflow → SKILL

Reflection instructions say Skills should only be created for reusable durable multi-step procedures, whereas individual facts/corrections belong in memory.

## Don't enable uncontrolled learning initially

v0: completed training Runs → normalized trajectories → reflection session → LearningProposal

No memory mutation yet. Letta proposes → cg validates → Moltwork promotes.

## Use Letta Trajectory for feeding previous experience back

Letta's `trajectory` package normalizes transcripts from different harnesses into a consistent format intended for memory formation, dreaming, evaluation and analysis.

WorkerKit records canonical economic/evidence. Trajectory is what a future Letta worker can conveniently examine.

## Lab should store summaries + references, not dump trajectories

After each run Hydra should know: Run, WorkerVersion, TaskFamily, Artifact, EvaluatorScores, Cost, ProcessVersion, Skills, Briefings, Reviewer, Outcome, TrajectoryRef.

## Use one very narrow task family

Competitive technical ideation/submission tasks. Each fixture varies: topic, constraints, required technologies, target customer, judging criteria, number of outputs, reward weighting. But the underlying process remains similar.

## Tests in order

| Test | Must prove |
|------|-----------|
| `letta_create_worker` | Worker ID maps permanently to one Letta agent ID |
| `letta_new_session_same_worker` | Two job sessions share persistent memory |
| `letta_memory_persists` | Lesson from run 1 is retrievable in run 2 |
| `letta_model_swap` | Same Worker survives changing underlying model |
| `workerkit_letta_real` | Real Letta artifact enters WorkerKit, no stub |
| `run_trajectory_export` | Every run produces normalized trajectory |
| `lab_projection` | Run appears correctly in Lab/Hydra |
| `lab_brief_retrieval` | New run receives relevant prior experience |
| `learning_proposal` | Letta proposes a structured durable change |
| `learning_not_auto_promoted` | Proposal cannot mutate production Worker without evaluation |
| `candidate_worker_version` | Approved patch creates distinct WorkerVersion |
| `heldout_ablation` | v1 vs v2 actually execute same hidden suite |
| `improvement_report` | Outputs per-dimension quality/cost deltas |
| `restart_persistence` | Kill runtime, restart, same Worker state survives |

Hard safety invariant: NO LETTA SERVER → RUN FAILS. Never `ok=True "[letta-stub]"`.

## First demo output

```
Researcher-03

Training experience: 7 runs

Learned proposal:
"Construct explicit requirement matrix before idea generation"

Promoted: yes

Worker v1 → Worker v2

Held-out tasks: 10

                    v1       v2
requirements       .68      .91
diversity          .77      .83
technical          .82      .84
overall            .74      .86

median cost        $.21     $.23

Lab context uplift:     +7 points
persistent learning:    +5 points

MemFS: commit abc123 → def456

Evidence: 10 RunReceipts, 10 trajectories, 20 artifacts
```

## Advanced Letta features to use in MVP

Use now: persistent Agent, fresh Conversation per Run, MemFS, Git memory versions, agent-owned Skills, session-scoped tools, subagents, Trajectory, recall of previous conversations, model swapping.

Defer: automatic dreaming promotion, Mods, large multi-agent teams, shared Letta repositories, channels, mobile UI, schedules, full .af marketplace export.

## After this succeeds

- Oracle feeds real tasks into it
- Hydra becomes the real organizational graph
- Market starts attributing Briefing/Skill/Reviewer effects
- Phala can attest actual accumulated worker state

## Official Letta links

- Letta Agent SDK: https://github.com/letta-ai/letta-agent-sdk
- Agent SDK quickstart: https://docs.letta.com/letta-agent-sdk/quickstart
- Letta Code: https://github.com/letta-ai/letta-code
- Letta docs: https://docs.letta.com/
- MemFS docs: https://docs.letta.com/concepts/memfs
- Memory and dreaming: https://docs.letta.com/configuration/memory
- Context Repositories: https://www.letta.com/blog/context-repositories/
- Trajectory: https://github.com/letta-ai/trajectory
- Agent File: https://github.com/letta-ai/agent-file
- OSS UI: https://github.com/letta-ai/letta-oss-ui
- Agent SDK examples: https://github.com/letta-ai/letta-agent-sdk/tree/main/examples
- App Server deployment: https://github.com/letta-ai/letta-app-server-deployment
- Docs markdown mirror: https://github.com/letta-ai/letta-docs-md
