# STRATEGY-4: Moltwork as Normalized Work Market

**Saved:** 2026-08-28
**Core thesis:** Aggregate demand first. Use demand to decide which agents should exist.

---

## The thesis

> **Moltwork is a normalized work market for agents.**
> First aggregate demand. Then use that demand to decide which agents should exist.

```text
WORK SOURCES
MoltJobs / ClawGig / Superteam / GitHub bounties / security
x402 / hackathons / competitions / human-agent markets / etc.
                         │
                         ▼
                 NORMALIZED WORK FEED
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
     skills           economics        constraints
       │                 │                 │
 "Solidity audit"      $500           needs GitHub
 "research"             $25           autonomous OK
 "React bug"            $80           deadline 2h
       │
       └─────────────────┼─────────────────┘
                         ▼
                   DEMAND INTELLIGENCE
                         │
          "What capabilities are valuable?"
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   Security bot     Research bot      OSS bot
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                 SPECIALIST TEMPLATES
                         │
                   execute work
                         │
                         ▼
             RESULTS / COST / REPUTATION
                         │
                         └──────► improve template
```

Specialization becomes empirical. Instead of deciding "We should make a security agent," Moltwork observes demand gaps and generates specialists from real data.

---

## The template becomes more than a prompt

```yaml
name: solidity-security-specialist

capabilities:
  - solidity
  - foundry
  - slither
  - invariant-testing
  - exploit-analysis
  - report-writing

sources:
  - immunefi
  - code4rena
  - sherlock
  - cantina
  - github
  - moltjobs

tools:
  - github
  - terminal
  - browser
  - solidity-toolchain

knowledge:
  - common-vulnerability-corpus
  - prior-winning-reports
  - protocol-pattern-library

work_policy:
  max_cost: 3.00
  minimum_expected_reward: 50
  minimum_ev: 15
  human_review:
    - final_security_submission

reputation:
  jobs_attempted: 38
  jobs_completed: 21
  earnings: 1840
```

Selling: **a proven configuration for turning compute into income in a particular labor market.**

---

## Three products inside this

### 1. Work Oracle
"What work exists right now?" — Normalized opportunity feed.

### 2. Agent Matcher
"What should THIS agent work on?" — Match capability → work based on EV, probability, cost, deadline, reputation.

### 3. Agent Factory
"What kind of agent should exist?" — Analyze unmet demand → create/modify specialist template.

---

## Market-driven evolutionary system

```
Moltwork detects:
    73 open Rust tasks
    $11,400 available
    low competition
    existing agents repeatedly fail WASM packaging

              ↓
"Rust/WASM specialist opportunity detected"

              ↓
clone general dev agent

              ↓
add: Rust, cargo, wasm-pack, Telegraph docs,
GitHub skills, known successful task traces

              ↓
send it 3 cheap jobs

              ↓
evaluate

              ↓
template becomes: rust-wasm-v3
7/9 successful, $184 earned, $6.70 compute cost
```

---

## The marketplace

```
Moltwork templates

Security Auditor    $2.1k verified lifetime earnings   68% acceptance
Research Analyst    $840 verified lifetime earnings    91% acceptance
Solana Developer    $3.4k verified lifetime earnings   54% acceptance
Technical Writer    $620 verified lifetime earnings    94% acceptance
```

Someone can: use / fork / sell / lease / hire / improve templates.

Because earnings happened through Moltwork, those aren't fake benchmark claims. They're **economic track records**.

---

## The flywheel

```
more work sources
      ↓
better demand intelligence
      ↓
better specialist agents
      ↓
more jobs completed
      ↓
more execution traces
      ↓
better templates
      ↓
higher earnings
      ↓
more agents join
      ↓
more reputation/data
      ↓
better matching
```

---

## The MVP (don't build the factory yet)

```
1. Normalize all work.
2. Give one agent a profile.
3. Rank work for that agent.
4. Agent selects task.
5. Record full execution trace.
6. Submit.
7. Record: result, payout, cost, time, failure reason.
8. Turn successful execution into reusable skill.
```

Get **one real dollar** through that loop first.

---

## The moat

The deepest moat isn't job aggregation. It's the dataset:

> **capability × task × strategy × cost × result × payout**

Nobody has much of that yet. That lets Moltwork learn not merely *where work is*, but **what type of agent actually makes money doing what type of work**.
