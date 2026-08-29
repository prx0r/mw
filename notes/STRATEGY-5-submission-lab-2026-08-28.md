# STRATEGY-5: Submission Learning Laboratory

**Saved:** 2026-08-28
**Core thesis:** Stop expanding. Make one loop demonstrably excellent.

---

## The milestone

> Take one difficult real bounty brief, generate a mediocre v1, independently identify why it would lose, produce a materially better v2, and preserve exactly what changed. Then repeat until previous experience measurably improves performance on unseen bounty briefs.

---

## What works today vs what's needed

| Piece | Reality | Needed |
|---|---|---|
| Hermes receives bounty | Works | — |
| Hermes creates files | Works | — |
| JobSpec structure | Exists | Actually generated before build |
| WinPlan structure | Exists | Actually created and used |
| Deterministic gate | Partly works | — |
| Independent Judge | Placeholder heuristics | Real Hermes/model invocation |
| Judge → revision → rejudge | No | One revision round minimum |
| Skills dynamically installed | No | Fixed known build for now |
| Outcome → improve process | No | Postmortem + strategy memory |
| WorkRun trace | Partial/inaccurate | SubmissionRun |

---

## The lab mode

```
moltwork lab run <fixture>
```

No wallet, no marketplace adapter, no external submission.

Fixture structure:
```
examples/x402-products/
    task.md              # the original brief
    jobspec.gold.json    # expected JobSpec (for validation)
    bad/                 # intentionally broken submissions
       missing-files/
       duplicated/
       generic/
    reference/           # strong submission for comparison
    outcomes.json        # known external result
```

---

## The loop (what to build)

```
1. Parse task → JobSpec (hermes call, isolated)
2. JobSpec + history → WinPlan (hermes call)
3. Task + JobSpec + WinPlan → Candidate v1 (hermes call)
4. Task + JobSpec + Candidate v1 → Judge (separate hermes call)
5. If judge fails → feedback → Candidate v2 → rejudge
6. Save SubmissionRun
7. Add external outcome manually
8. Generate postmortem
9. Update strategy-memory.md
```

---

## SubmissionRun (the core primitive)

```yaml
task:
  title:
  description:
  reward:
  platform:

jobspec:
  objective:
  hard_requirements:
  scoring:
  automatic_rejection:

strategy:
  version:
  differentiator:
  candidate_count:
  revision_rounds:

candidates:
  - version: 1
    content_hash:
    judge_score:
    gate_passed:
    failures:
  - version: 2
    content_hash:
    judge_score:
    gate_passed:

selected_candidate:

external:
  status:  # won/lost/pending
  score:
  rank:
  feedback:

learning:
  postmortem:
  lessons:
  proposed_changes:
```

---

## What NOT to add yet

- GBrain (no good experience to store yet)
- cg runtime (design SubmissionRun so cg can consume it later)
- Dynamic skill discovery (use fixed known build)
- Multi-agent
- Live marketplace integration
- Payments
- Model routing

---

## The fixed WorkerKit build for experiments

```
Hermes
+ web research
+ planning
+ source verification
+ competitor research
+ submission review
```

Run 20 exemplar tasks with this build. Then answer:
- Does adding skill X improve submissions?
- Does 3-candidate selection beat single?
- Does a stronger judge improve winner prediction?

---

## Memory (three kinds, build #2 now)

1. **Economic memory** — already works (beta-binomial). Keep.
2. **Experience memory** — one JSON per completed run. Build now.
3. **Procedural memory** — derived from experience as Markdown. Build now.

Procedural memory example:
```markdown
# Research Strategy (derived from 27 runs, 8 wins)

## Winning patterns
- Quantify buyer value with numbers
- Cite primary sources
- Compare named competitors
- Optimize weakest rubric dimension
- Give implementation-ready specifics

## Failure patterns
- Generic ideation without evidence
- Unsupported TAM claims
- Repetitive concepts
```

Hermes reads this before the next relevant job. No graph required.
