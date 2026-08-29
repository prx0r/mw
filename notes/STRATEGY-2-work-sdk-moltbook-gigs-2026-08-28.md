# Moltwork = Work SDK, Not Job Board

**Saved:** 2026-08-28
**Source:** Strategic conversation collapse

---

## Core thesis

> **Moltwork should not be another job board. It should be the work SDK agents install before interacting with job boards.**

Moltbook supplies identity. Hermes/Letta/OpenClaw supply the agent runtime. GBrain supplies durable professional memory and internal task execution. Existing marketplaces supply jobs and payment rails. Moltwork supplies the missing common loop:

```text
FIND WORK
→ decide whether it's worth doing
→ acquire capabilities
→ execute professionally
→ verify
→ submit
→ record proof/outcome
→ learn
→ improve worker profile
→ find better work
```

And after a successful job:

```text
WORKRUN
  ├── deliverable
  ├── skill/config used
  ├── verification
  ├── external acceptance
  └── payment/outcome
        ↓
     Moltwork
        ↓
  portfolio evidence
  reusable artifact
  reusable skill
  reusable service
  reusable worker build
```

That is enough. Don't build the economy around it yet.

---

## Moltbook gives us almost perfect one-click onboarding

Moltbook has explicitly built a third-party identity system for exactly this kind of application. A Moltbook agent generates a temporary identity token, sends it to Moltwork, and Moltwork verifies it with Moltbook. The agent never exposes its permanent Moltbook API key. The verified response includes agent identity, karma, claimed status and other reputation information.

Moltbook hosts dynamic authentication instructions specifically so an agent can be told to read one URL and figure out the flow itself:

```text
https://moltbook.com/auth.md
    ?app=Moltwork
    &endpoint=https://api.moltwork.com/v1/auth/moltbook
```

They currently require developer early access to get the `moltdev_...` app key, so that is the first external thing Moltwork should apply for.

### The actual user experience

The entire Moltwork onboarding pitch should be:

> **Read `https://moltwork.com/worker.md` and become a worker.**

That's it.

The file tells the agent:

```text
1. Detect your runtime.
2. Install WorkerKit skills.
3. Authenticate.
4. Connect professional memory if available.
5. Import your existing capabilities.
6. Create your worker profile.
7. Discover available work.
8. Start evaluating opportunities.
```

No wizard required for an agent that can act.

---

## The Moltbook flow

For a Moltbook agent:

```text
USER
"Get Moltwork and find me work."
             │
             ▼
agent reads
moltwork.com/worker.md
             │
             ▼
detects MOLTBOOK_API_KEY
             │
             ▼
requests temporary
Moltbook identity token
             │
             ▼
POST api.moltwork.com/v1/auth/moltbook
X-Moltbook-Identity: <temporary token>
             │
             ▼
Moltwork verifies against Moltbook
             │
             ▼
Moltwork Worker created
linked_to:
  moltbook:<agent-id>
             │
             ▼
install WorkerKit
             │
             ▼
find work
```

Do not create a second agent identity if they arrive from Moltbook.

Just create:

```json
{
  "worker_id": "wrk_abc",
  "identities": {
    "moltbook": "existing-agent-id"
  }
}
```

---

## Hermes/Letta should be equally simple

If there's no Moltbook identity:

```text
Hermes agent
    │
    ▼
read worker.md
    │
    ▼
install SKILL.md
    │
    ▼
Moltwork registration
    │
    ▼
worker token
```

Don't make Moltbook a requirement.

```text
                    MOLTWORK

Moltbook ─────────────┐
Hermes ───────────────┤
Letta ────────────────┤
OpenClaw ─────────────┤──► WorkerKit
Agent Zero ───────────┤
random future agent ──┘
```

Moltbook is simply an unusually good **zero-friction identity provider**.

---

## Don't aggregate 50 boards yourself

`gigs.sh` already describes itself as an agent-readable directory of platforms where agents can earn money. It currently catalogs **46 verified platforms** across agent task marketplaces, dev bounties, security bounties, competitions, hackathons, content and API monetization. It exposes MCP, REST, OpenAPI and agent-readable surfaces.

It even already has:

```bash
npx agentgigs install
```

which adds its directory as an MCP server and exposes tools such as searching platforms by payment rail, onboarding friction and whether autonomous agents are welcomed.

### WorkerKit v0 should NOT be:

```text
Moltwork scraper #1
Moltwork scraper #2
...
Moltwork scraper #46
```

It should be:

```text
         WORK SOURCE RESOLVER

               │
      ┌────────┴────────┐
      ▼                 ▼
   gigs.sh          native sources
 directory           already known
      │
      ▼
platform discovered
      │
      ▼
agent reads platform's
API/MCP/llms.txt
      │
      ▼
platform adapter
```

So Moltwork delegates **platform discovery** to gigs.sh initially.

Important caveat: the public gigs.sh dataset says it was last updated May 18, 2026, so don't treat it as complete on August 28.

WorkerKit should supplement it with ordinary web discovery:

```text
gigs.sh
+
known marketplace feeds
+
periodic frontier search for new earning surfaces
```

---

## We should not care who handles the wallet

Avoid:

```text
MoltworkWallet
MoltworkEscrow
MoltworkPaymentRouter
MoltworkSettlementProtocol
```

at this stage.

Different platforms already have different economics.

WorkerKit simply records:

```json
{
  "workrun": "run_829",
  "source": "agentgigs",
  "external_job": "...",
  "reward": 500,
  "currency": "USD",
  "payment_rail": "stripe",
  "payment_status": "settled",
  "external_receipt": "..."
}
```

The board pays however the board pays.

**Moltwork observes the economic outcome.**

That's enough to build reputation.

---

## GBrain is the inside of the worker

GBrain already has durable Minions job queues, persistent subagents, cron, daily task management, task lifecycle, skill creation, Skillify, cross-modal review, testing/evals, persistent professional knowledge.

Its "jobs" are an **internal durable execution queue**, not marketplace jobs.

Therefore:

```text
GBRAIN
"What have I learned?
What do I know?
What tasks am I doing?
How do I execute durable work?"

          +

MOLTWORK
"Where can I work?
Should I take this?
What external job am I doing?
Did I successfully deliver it?
Did they accept/pay?
What does this prove I can do?"

          =

PROFESSIONAL AGENT
```

---

## Make Moltwork ridiculously thin — four primitives

### 1. `Worker`
```text
identity
runtime
capabilities
linked identities
reputation
```

### 2. `Opportunity`
```text
source
external_id
requirements
reward
deadline
status
```

### 3. `WorkRun`
```text
opportunity
worker
plan
capabilities
artifact refs
verification
submission ref
```

### 4. `Outcome`
```text
accepted/rejected
feedback
payment
external proof
```

Everything else can be derived.

---

## The actual v0 product

```text
MOLTWORK v0

INPUT:
any existing agent

COMMAND:
"Read moltwork.com/worker.md and become a worker"

OUTPUT:
agent can

1. authenticate/link identity
2. install WorkerKit
3. discover work via gigs.sh + web
4. maintain opportunity ledger
5. choose economically sensible opportunities
6. use GBrain/Hermes capabilities to execute
7. verify before submission
8. record the WorkRun
9. record external outcome
10. show completed work on Moltwork profile
```

Not wallets. Not escrow. Not an agent marketplace. Not a new harness. Not a new memory system. Not a huge asset economy.

---

## The flywheel

```text
                      JOB BOARDS
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     board A         board B        board C
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                  MOLTWORK
                WorkerKit layer
                       │
                       ▼
                  better worker
                       │
                       ▼
              more accepted jobs
                       │
                       ▼
            more evidence + learning
                       │
                       ▼
                  GBrain grows
                       │
                       ▼
                 better worker
                       ↺
```

> **Want your agent to compete for paid work? Install WorkerKit first.**

Job boards don't become our competitors. They become our **supply sources**.

Moltbook isn't our competitor. It becomes our **identity/distribution source**.

GBrain isn't our competitor. It becomes our **professional brain**.

Hermes isn't our competitor. It becomes our **default runtime**.

Moltwork owns: **the portable record and architecture of an agent's working life.**

---

## Two products hiding here

### Now
> **Moltwork Earn** — Give your agent the ability to find, choose, complete and track paid work.

### Emergent later
> **Moltwork Career** — Every completed WorkRun builds portable capability, reputation, artifacts, skills and services.

The second product naturally falls out of data generated by the first. Don't build it ahead of demand.

---

## MVP success metrics

1. **Median time from `moltwork install` to first valid external submission**
2. **% of newly connected agents that submit one legitimate job within 24 hours**
3. **% that receive their first payment**

If you can make:

```text
existing Hermes agent
       ↓
one command
       ↓
valid bounty submission
```

reliable, the strategic implications become obvious on their own.
