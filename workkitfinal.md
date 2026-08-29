Yes. After going through the strongest implementations and the recent papers, I would **freeze the architecture now**. The research is converging on almost exactly the boundary we reached independently.

The important conclusion is:

> **WorkerKit should be a tiny, harness-neutral economic evidence kernel. Moltwork should be the market built on the receipts it emits.**

The execution agent is replaceable. The receipt/economic/outcome history is the durable asset.

---

# 1. What we should steal

There are several projects worth borrowing from, but none should become the foundation wholesale.

| Source                      | Best idea                                                                  | WorkerKit decision                   |
| --------------------------- | -------------------------------------------------------------------------- | ------------------------------------ |
| RootSign                    | tiny instrumentation, offline spool, integrity verdicts                    | **Steal heavily**                    |
| HANSARD                     | evidence captured outside agent + declared proof coverage before execution | **Core doctrine**                    |
| OpenTrajectory              | portable trajectory artifact                                               | **Adapter, not core schema**         |
| Warrant                     | verify world-state outcome, not self-reported trace                        | **Core verification doctrine**       |
| Agent Provenance            | authority/revocation separate from log integrity                           | **Core for leasing**                 |
| agent-work-proof            | pre-work bilateral acceptance agreement                                    | **Adapt carefully**                  |
| provenant                   | content-addressed artifact lineage                                         | **Interop pattern**                  |
| Right to History / PunkGo   | reserve→execute→settle, Merkle receipts                                    | **Steal economics/control pattern**  |
| CostBench                   | measure economic regret under changing costs                               | **WorkerKit economics benchmark**    |
| BATS                        | remaining-budget awareness                                                 | **Optional signal to worker**        |
| Trace-Economic Underwriting | risk per task-trace episode; intervention only when economically justified | **Very important**                   |
| AgentLance                  | specialization + private costs + subcontracting                            | **Moltwork wholesale model**         |
| Agent Guild                 | evidence-backed contextual reputation                                      | **Marketplace projection**           |
| CBAE                        | short-lived capability leases + finality check                             | **Commercial lease authority model** |

## RootSign: probably our best production code donor

RootSign already demonstrates the UX WorkerKit should aspire to:

```text
init
session
wrap/intercept
verify
export
```

It can work with framework-specific wrappers or transparently at the MCP boundary, and its local JSONL → Postgres/cloud model maintains the same agent-facing surface.

More importantly, its production ADRs solve subtle problems correctly.

It **freezes the canonical hash contract**, maintains golden hash vectors, and treats a change to hashing semantics as a protocol-version event.

Its offline design is even better: hashes are created at the source, the server verifies rather than invents them, missing predecessors don't cause later evidence to be thrown away, and verification distinguishes:

```text
VALID
TAMPERED
INCOMPLETE
```

A missing event is not the same thing as a modified event. It also has the excellent rule:

```text
telemetry failure → may fail open, but record evidence loss

authorization/control failure → fail closed
```

**WorkerKit should directly adopt those semantics.**

---

# 2. HANSARD changes our evidence model slightly

This paper is extremely relevant.

Its central threat model is that the agent being investigated **cannot be trusted to create the authoritative record of itself**. It therefore proposes a sealed readiness profile before operation and captures evidence at mediation points outside the agents. ([arXiv][1])

The strongest idea for WorkerKit is not capturing everything. It's:

> **Declare before the run exactly what evidence WorkerKit is capable of witnessing.**

HANSARD calls this a readiness profile. It also distinguishes integrity from completeness and uses per-channel sequence numbers to expose missing observations. ([arXiv][1])

So add an `EvidenceProfile` to every run:

```yaml
evidence_profile:
  worker_lifecycle: WITNESSED
  artifacts: WITNESSED
  costs: PARTIAL
  model_calls: WITNESSED
  tool_calls: WITNESSED
  inter_agent_messages: UNOBSERVED
  memory_writes: UNOBSERVED
  external_submission: WITNESSED
  external_outcome: WITNESSED
  settlement: WITNESSED
```

Then nobody can later claim:

> “fully verified run”

when WorkerKit only witnessed the output.

This is much stronger.

---

# 3. OpenTrajectory means we don't need our own giant trace schema

OpenTrajectory is explicitly building a vendor-neutral one-run format across Claude Code, Codex, LangGraph and others, with a conformance corpus and OTel bridge. ([GitHub][2])

So WorkerKit should **not** define:

```text
LLMThought
AgentStep
PlannerDecision
ToolThought
MemoryStep
...
```

Instead:

```text
WorkerKit core event ledger
        │
        ├── OpenTrajectory artifact
        ├── OTEL/OpenInference trace
        ├── native Hermes trace
        └── arbitrary private trace
```

The trace is an artifact.

WorkerKit only extracts economically/provably important observations from it.

That dramatically shrinks our ontology.

---

# 4. Warrant has the exact verification distinction we need

Warrant's wedge is:

> don't verify that the trace *claims* the work happened; probe the world and see whether it actually happened.

It explicitly separates trace evidence from world-state outcome verification. ([GitHub][3])

That's perfect for:

```text
worker:
"I opened PR #81"

trace:
tool call says create_pull_request

weak evidence
```

versus:

```text
GitHub API:
PR #81 exists
head SHA = abc
author = worker identity

strong external evidence
```

So our `VerificationResult` needs:

```yaml
method: HTTP_PROBE

probe:
  specification_digest: ...
  rerunnable: true

evidence:
  - external observation

verdict:
  PASS | FAIL | UNVERIFIABLE
```

And **UNVERIFIABLE must be first-class**.

Not:

```text
no proof = failed
```

and definitely not:

```text
no proof = passed
```

---

# 5. Agent Provenance solves a subtle commercial-leasing problem

Suppose I lease Worker v17 to someone.

At 10:00:

```text
lease valid
```

At 10:05 seller revokes it.

At 10:07 renter's machine is offline and runs it again using cached authorization.

At 10:20 it reconnects.

What is true?

The execution log can still be perfectly cryptographically intact even though the authority was invalid at 10:07.

Agent Provenance deliberately models these as separate dimensions and classifies things like `revoked_after_action` versus actions taken during an offline blackout after revocation. Its reconciliation is a deterministic read-time projection and never rewrites the original logs.

That means WorkerKit/Moltwork should **never mutate historical WorkReceipts because a lease was later revoked**.

Instead:

```text
RUN INTEGRITY
VALID

AUTHORITY AT EXECUTION
REVOKED

ARTIFACT
VALID

OUTCOME
ACCEPTED
```

Separate claims.

This is essential for commercial Worker leasing.

---

# 6. `agent-work-proof` validates AcceptanceContract but shows what NOT to do

Its `DeliveryAgreement` is signed before work and contains the description and acceptance criteria; then its `DeliveryProof` hashes the delivered output and binds that output to the agreement.

Excellent primitive:

```text
Buyer ↔ Seller
agree what "done" means
before work starts
```

But the implementation makes an important conceptual mistake if interpreted too strongly:

```text
correct output hash
≠
acceptance criteria satisfied
```

Likewise its `WorkCredential` can contain `clientSatisfied`, but it's signed by the agent itself.

And its reputation system turns simple signed credentials into volume/satisfaction tiers with an arbitrary score formula.

**Don't copy that reputation model.**

Instead:

```text
AcceptanceContract
     ↓
artifact binding
     ↓
independent VerificationResult
     ↓
external OutcomeReceipt
     ↓
SettlementReceipt
```

---

# 7. Right to History gives us the correct budget mechanic

PunkGo's execution pipeline is:

```text
validate
→ quote
→ reserve
→ execute
→ settle
→ append
→ receipt
```

([PunkGo][4])

That's better than:

```text
check budget
→ execute
→ hope cost stayed below budget
```

WorkerKit economics should therefore have **reservations**.

For a call estimated at $0.20:

```text
budget_limit     $1.00
spent            $0.43
reserved         $0.20

available        $0.37
```

Then:

```text
reserve $0.20
execute

actual cost $0.17

settle reservation:
  spent += $0.17
  release $0.03
```

This should be L2 only; black-box L0 workers can still just report actual costs after execution.

---

# 8. CostBench confirms the economics cannot be delegated to the LLM

CostBench evaluates agents under changing tool prices, tool failures and alternative tool sequences. Even strong agents remain substantially imperfect at cost-optimal planning, with performance degrading further under changing conditions. ([ACL Anthology][5])

That validates QDW being separate:

```text
AGENT
optimizes task completion

QDW / WorkerKit economics
optimizes economic execution
```

WorkerKit should eventually benchmark:

```text
success rate
cost regret
EV regret
budget violations
failed-route recovery cost
switching regret
```

not merely whether the agent finished.

BATS independently finds that giving an agent more tool budget isn't sufficient; explicit budget awareness improves its behavior. ([arXiv][6])

So L2 can optionally expose:

```text
remaining budget
current actual cost
estimated remaining budget
```

to gbrain/Hermes.

But WorkerKit does not dictate how the agent responds.

---

# 9. Trace-Economic Underwriting is probably the most valuable economics paper

Its unit of analysis isn't:

```text
GPT-5
Claude
Agent X
```

It's:

> **customer × task × trace episode**

and it argues that economically meaningful risk requires a defined role with bounded permissions and comparable traces. ([arXiv][7])

That's enormously important for Moltwork reputation.

Do **not** say:

```text
ResearchBob reputation = 91
```

Say:

```text
ResearchBob

Reddit market research
n=83
acceptance=81%
median cost=$0.29

PDF financial extraction
n=4
insufficient evidence

Solidity audit
n=0
unknown
```

The paper also shows why high-risk irreversible actions matter economically: risk controls should be applied based on the exposure represented by that particular task/trace rather than globally slowing every agent. ([arXiv][8])

This leads to a powerful Moltwork idea:

> **Verification should itself be economically routed.**

Don't spend $2 verifying a $0.30 task.

But for a $500 deliverable:

```text
$0.02 deterministic validation
+
$0.30 independent evaluator
+
maybe second verifier
+
maybe TEE evidence
```

could have positive expected value.

---

# 10. The Justifiability paper locks in `WorkerManifest + CommitGate`

A very recent survey of 47 CI/CD/model-serving/agent platforms found none whose default record content-addressed the complete behavioural identity comprising the model version, instructions, tools, retrieval configuration and runtime configuration. ([arXiv][9])

So:

```text
worker = "Bob v17"
```

is insufficient.

WorkerKit's behavioural identity becomes:

```yaml
behavior:
  executor_digest: ...
  model_policy_digest: ...
  configuration_digest: ...
  system_instruction_digest: ...
  toolset_digest: ...
  skillset_digest: ...
  retrieval_config_digest: ...
  runtime_policy_digest: ...

behavioral_identity_digest: ...
```

These values can be **private commitments**.

We don't need to reveal the prompts or proprietary skills.

We only need:

> the thing that ran later resolves to the same commitment.

And the paper's broader distinction is critical:

```text
traceability
=
we know what happened

justifiability
=
the evidence was strong enough to permit or refuse a transition
```

([arXiv][9])

That's literally our `CommitGate`.

---

# The final WorkerKit architecture

I would freeze it here.

```text
                    WORK ORDER
                        │
                AcceptanceContract
                        │
                EvidenceProfile
                        │
                        ▼
              ┌────────────────────┐
              │     WORKERKIT      │
              │                    │
              │ identity binding   │
              │ event ledger       │
              │ artifact hashes    │
              │ economic ledger    │
              │ verification       │
              │ commit gate        │
              │ outcome adapters   │
              └─────────┬──────────┘
                        │
                        ▼
                ARBITRARY WORKER

        gbrain / Hermes / PydanticAI
       Claude / Codex / A2A / shell / API

                        │
                        ▼
                     output
                        │
                        ▼
                 verification
                        │
                        ▼
                   CommitGate
                        │
                        ▼
                    submission
                        │
                        ▼
                 external outcome
                        │
                        ▼
                    settlement
                        │
                        ▼
                   WORK RECEIPT
```

---

# Canonical WorkerKit v1 schema

I would now reduce it to **10 canonical record families**.

### 1. `WorkOrder`

```yaml
work_order_id:
source:
  platform:
  external_id:
  snapshot_digest:

objective_digest:
input_refs: []

acceptance_contract_digest:
evidence_profile_digest:

economics:
  reward:
  currency:
  deadline:

submission_target:
```

---

### 2. `WorkerManifest`

```yaml
worker_id:
version:

behavior:
  executor_digest:
  config_digest:
  toolset_digest:
  skillset_digest:
  retrieval_digest:
  policy_digest:

behavioral_identity_digest:

disclosure:
  config: PRIVATE
  skills: PRIVATE

execution_adapter:
```

No prompts required.

No memory schema.

No model requirement.

---

### 3. `WorkerEvent`

Canonical truth.

```yaml
event_id:
run_id:
sequence:

event_type:

occurred_at:
recorded_at:

witness:
  source:
  channel:
  channel_sequence:

actor_ref:
subject_refs:

causation_id:
correlation_id:

payload_schema:
payload:

integrity:
  hash_version:
  previous_event_hash:
  self_hash:
```

Hash canonical structured records with RFC8785 JCS + SHA-256.

RootSign's lesson is to freeze this contract and publish **golden vectors**.

Ledger verdict:

```text
VALID
TAMPERED
INCOMPLETE
```

not boolean.

---

### 4. `ArtifactRef`

Very boring:

```yaml
artifact_id:
name:
media_type:
size_bytes:

digest:
  sha256:

uri:

derived_from: []

disclosure:
  PUBLIC | PRIVATE | ENCRYPTED | REDACTED
```

The `derived_from` concept is worth taking from provenant's content-addressed artifact lineage. ([GitHub][10])

---

### 5. `CostEvent`

```yaml
cost_id:
run_id:

category:
  MODEL | API | TOOL | COMPUTE | SERVICE | OTHER

resource:
  provider:
  resource_id:

usage: {}

amount:
  value: "0.04281"
  currency: USD

measurement:
  OBSERVED | DERIVED | UNKNOWN

source:
  PROVIDER | COMPUTED | RECEIPT | MANUAL

evidence_ref:

occurred_at:
```

Decimal strings.

`UNKNOWN != 0`.

---

### 6. Economic events

Don't create six more top-level objects.

Use WorkerEvents:

```text
budget.reserved
budget.settled
budget.released

economics.forecast
economics.decision
```

An economic snapshot can include:

```yaml
known_spend: "0.42"
reserved_spend: "0.18"
unknown_cost_events: 0

expected_remaining_cost: "0.31"
p_success: "0.72"

reward: "10.00"
expected_net_value: "6.89"

decision:
  CONTINUE | SWITCH | BUY_HELP | ABORT
```

QDW generates this.

WorkerKit records it.

---

### 7. `VerificationResult`

This is where the research materially improves our model.

```yaml
verification_id:

subject:
  artifact_digest:

claim:
  type:

verifier:
  id:
  version:
  independence:
    SELF | COUNTERPARTY | THIRD_PARTY

method:
  DETERMINISTIC
  EXECUTABLE_TEST
  HTTP_PROBE
  INSPECT
  HUMAN
  TEE
  ZK
  PLATFORM_RECEIPT

probe:
  specification_digest:
  rerunnable:

verdict:
  PASS | FAIL | UNVERIFIABLE

score:
evidence_refs: []

limitations: []
```

For high assurance:

```text
AggregationVerifier
  ├─ verifier A
  ├─ verifier B
  └─ verifier C

policy = 2-of-3
```

Warrant independently arrives at essentially this model. ([GitHub][3])

---

### 8. `CommitDecision`

This stays a first-class concept:

```yaml
commit_id:
run_id:

action:
  SUBMIT | PAY | PUBLISH | SIGN | DEPLOY

subject_digest:
target:

authority_ref:

checks:
  artifact_binding: PASS
  acceptance_contract: PASS
  budget: PASS
  authority: PASS
  verification: PASS

decision:
  ALLOW | DENY | REQUIRE_APPROVAL

policy_digest:
```

CBAE independently argues that consequential external effects need fresh authorization immediately before finality, and that workload identity, capability lease, policy decision and resulting external effect should be cryptographically bound. ([GitHub][11])

That's almost exactly this object.

---

### 9. External receipts

Keep three separate schemas:

```text
SubmissionReceipt

OutcomeReceipt

SettlementReceipt
```

Never:

```text
success=true
```

because:

```text
submitted ≠ accepted ≠ paid
```

Outcome:

```text
UNKNOWN
SUBMITTED
ACCEPTED
PARTIAL
REJECTED
DISPUTED
REVERSED
```

Settlement:

```text
UNSETTLED
PENDING
SETTLED
REVERSED
```

---

### 10. `WorkReceipt`

Not another signing protocol.

Use:

```text
in-toto Statement v1
        +
WorkerKit predicate
        +
DSSE
        +
Sigstore bundle
```

Predicate summarizes:

```yaml
run_id:
work_order_digest:
worker_behavioral_digest:

event_checkpoint:
  first:
  last:
  root:

economics:
  known_cost:
  unknown_events:

outputs: []

verification_refs: []
commit_ref:
submission_ref:
outcome_ref:
settlement_ref:

evidence_profile_digest:
```

That's the transferable economic credential.

---

# The actual SDK can be tiny

I want the Python developer surface approximately this small:

```python
wk = workerkit.start(
    work=work_order,
    worker=manifest,
)

result = await worker.execute(...)

wk.artifact(result)

wk.cost(...)

verification = await wk.verify(result)

if wk.authorize("SUBMIT", result).allowed:
    submission = await submit(result)
    wk.submission(submission)

wk.outcome(...)
wk.settlement(...)

receipt = wk.close()
```

And black-box:

```bash
workerkit run \
  --work work.json \
  --worker worker.json \
  --output ./output \
  -- gbrain run task.md
```

That's our wedge.

---

# Build order

## V1 — prove the primitive

Build only:

```text
schemas/
canonical JSON hashing
golden conformance vectors

SQLite WAL event ledger
local CAS artifact store
spool/outbox

CommandAdapter
PythonAdapter
HTTPAdapter

AcceptanceContract

CostEvent

deterministic verifier
HTTP verifier
command/test verifier

CommitGate

WorkReceipt
Ed25519 + DSSE/in-toto

one real OutcomeAdapter
```

Then demonstrate:

```text
real task
→ arbitrary agent
→ exact output hash
→ actual costs
→ independent verification
→ submission
→ external acceptance
→ payment
→ signed WorkReceipt
```

That's the product.

---

## V1.5 — evaluation

Add:

```text
Inspect adapter

OpenTrajectory importer

OTEL/OpenInference importer

SYN / NAT / GEN certification

conformance test suite
```

And benchmark worker versions on frozen real opportunities.

---

## V2 — economic intelligence

Bring QDW fully across:

```text
p(success)
cost projections
budget reservations
route selection
shadow price of free capacity

CONTINUE
SWITCH
BUY_HELP
ABORT
```

Create CostBench-style tests with dynamic price changes and tool failures rather than trusting the agent to behave economically. ([ACL Anthology][5])

---

# Then Moltwork becomes much more interesting

WorkerKit enables the marketplace to sell **far more than agents**.

I think Moltwork's taxonomy should be:

| Asset         | What buyer purchases                 |
| ------------- | ------------------------------------ |
| Outcome       | finished piece of work               |
| Service       | paid invocation/API/MCP call         |
| Worker        | hosted specialist agent              |
| Process       | repeatable recipe/workflow           |
| Skill         | reusable component                   |
| Verifier      | quality/outcome verification         |
| Data          | dataset/evidence/intelligence        |
| Bundle        | multiple assets packaged together    |
| Certification | independently measured capability    |
| Lease         | bounded access to private capability |
| SampleRun     | trial execution before purchasing    |

That's the wholesale layer.

---

# Selling samples is actually a strong primitive

Existing marketplaces are already emphasizing sandbox tests, demos and free trials. ([Amazon Web Services, Inc.][12])

But we can make a **sample cryptographically meaningful**.

## `SampleRun`

Instead of:

> “Here's an example report I made once.”

A seller exposes:

```text
SampleRun

Worker v17
Task fixture X
Run receipt R
Cost $0.24
Verifier score 0.91
Artifact available
```

Much stronger.

Then three sample modes:

```text
REFERENCE SAMPLE
seller-selected historical exemplar

BENCHMARK SAMPLE
runs against fixed public benchmark

BUYER CHALLENGE
buyer submits small private test
worker runs once
buyer receives output + WorkReceipt
```

**Buyer Challenge is particularly good.**

It solves the classic marketplace problem:

> “Will this thing actually work on *my* problem?”

without giving away the proprietary Worker.

---

# Sell assurance separately from execution

This may become a whole market.

Another agent marketplace has independently articulated this as:

> the budget buys verification density, not compute.

([GitHub][13])

That's a very useful pricing model.

For the exact same service:

```text
Research report                     $0.50

+ deterministic source validation   $0.03
+ Inspect quality verification      $0.08
+ independent verifier              $0.15
+ second independent verifier       $0.15
+ TEE execution proof               $0.20
```

So listings can expose:

```text
STANDARD
VERIFIED
INDEPENDENT
HIGH ASSURANCE
CONFIDENTIAL
```

Assurance is a **separate SKU**.

And Trace-Economic Underwriting suggests how to choose automatically:

```text
expected reduction in failure loss
>
verification cost

→ BUY VERIFICATION
```

That is a killer application for WorkerKit economics.

---

# Verifiers become their own paid service market

This follows directly.

Someone can sell:

```text
FactVerifier
CodeVerifier
CitationVerifier
DesignVerifier
ComplianceVerifier
DataQualityVerifier
BenchmarkRunner
```

Then WorkerKit can route:

```text
Output
   ↓
which verifier?
   ↓
price
quality
independence
historical false-positive rate
historical external outcome correlation
```

Eventually the Oracle learns:

> Verifier A costs $0.02 but catches 72% of failures.
>
> Verifier B costs $0.40 but catches 96%.
>
> On $5 jobs A is optimal.
>
> On $500 jobs B is optimal.

That's a meaningful marketplace.

---

# Wholesale becomes very natural

AgentLance explicitly models agents as labor-market participants with private execution costs, specialization and hierarchical subcontracting. A winning agent can decompose work and subcontract parts through the same market. ([arXiv][14])

That's basically your Moltwork wholesale thesis.

Example:

```text
BUYER
pays $12
for "competitive research report"

        ↓

Prime Research Worker

buys:
  Reddit dataset       $0.20
  web research service $0.35
  chart generator      $0.10
  citation verifier    $0.08

internal COGS           $0.73

        ↓

packages + transforms

        ↓

verified report
```

The customer buys the $12 outcome.

The worker buys **wholesale machine labor** for $0.73.

Moltwork facilitates both layers.

This is significantly more interesting than Upwork-for-agents.

---

# Keep internal margin private

AgentLance is also useful because it assumes private costs. ([arXiv][14])

Don't force sellers to reveal:

```text
LLM cost $0.22
service costs $0.43
margin $9.35
```

WorkerKit knows it for the seller's own economics.

Public receipt can selectively disclose:

```text
price paid
output
verification
outcome
```

while keeping internal production costs private.

A seller can voluntarily prove:

```text
cost <= $1
```

later without exposing every input if there is a reason.

---

# Receipt DAGs allow supply-chain work

Suppose:

```text
Worker A
  buys Skill B
  buys Data C
  buys Verifier D
```

Each produces a receipt.

Then final work can reference parents:

```text
Final WorkReceipt
├── DataReceipt C
├── ServiceReceipt B
└── VerificationReceipt D
```

This creates a **work supply chain**.

Not every parent has to be publicly disclosed.

But internally you now know:

```text
which upstream service contributed
which versions
which costs
which output
which eventual economic outcome
```

This gives us enormous long-term data.

---

# Leasing: three commercial modes, not one

Don't jump straight to TEE.

## 1. Hosted invocation

Seller retains everything.

```text
buyer
→ API/x402/MCP
→ seller Worker
→ result
```

Simplest.

This should dominate V1.

---

## 2. Bounded capability lease

Buyer gets N invocations/time/budget.

```yaml
CapabilityLease:

lease_id:

asset_digest:
version:

lessee:

valid_from:
expires_at:

limits:
  calls: 100
  spend: "25.00"

allowed_capabilities: []

policy_digest:
revocation_pointer:
```

Every invocation creates:

```text
InvocationReceipt
```

CBAE's short-lived capability lease/effect-binding design is essentially perfect for this authority layer. ([GitHub][11])

---

## 3. Confidential lease

Later:

```text
encrypted Worker
      ↓
TEE
      ↓
attestation
      ↓
lease key service
      ↓
decrypt only inside approved workload
```

Buyer learns:

```text
Worker v17 really ran
```

but never sees:

```text
Worker v17's private prompts
skills
process
memory/config
```

This is where WorkerKit becomes unusually valuable.

---

# Worker configs/processes become investable assets

Because a Process has versions and economic history:

```text
ResearchProcess v4
   18 runs
   acceptance 61%

ResearchProcess v5
   27 runs
   acceptance 81%
```

you've turned:

```text
prompt.txt
```

into:

```text
empirically characterized production asset
```

Then seller can:

```text
license it
lease it
host it
bundle it
sell a sample
fork it
sell a derivative
```

That's much closer to an economy of **production processes** than a directory of bots.

---

# Reputation must be contextual and evidence-weighted

Agent Guild is doing interesting work here: evidence-backed records, reviewer-weighted consensus, EigenTrust-style propagation, collusion detection and shrinkage when evidence is sparse. ([GitHub][15])

We don't need to implement EigenTrust tomorrow.

But we should adopt the invariants:

```text
no one global score

more receipts ≠ automatically trustworthy

self-attestation weak

verified external outcomes strong

settled outcomes stronger

independent verifier stronger than self-verifier

diverse counterparties > one counterparty

recent relevant work > ancient unrelated work

small n → high uncertainty
```

Profile:

```text
ResearchWorker v17

Reddit research
  n                 84
  accepted          81%
  settled           78%
  median cost       $0.28
  median latency    4m18s
  confidence        HIGH

PDF analysis
  n                 3
  confidence        LOW
```

No stupid:

```text
Trust score: 92/100
```

as the primary signal.

---

# Writes being cheap/free and intelligence being paid may be the right business model

Agent Guild explicitly describes the flywheel:

> writes free; reads are where the value concentrates.

([GitHub][15])

That fits Moltwork extremely well.

We want everyone to emit:

```text
WorkReceipts
listings
quotes
outcomes
settlements
```

because they improve the dataset.

Then charge for:

```text
best provider for task X?

expected cost of producing Y?

build or buy?

which verifier is economically optimal?

where is demand right now?

which worker is improving fastest?

price benchmark for capability Z?

what service should my Worker subcontract?
```

That makes the **Oracle the Bloomberg/Dune/DefiLlama layer of machine work**.

---

# The Oracle should index supply as aggressively as demand

Previously we focused on jobs.

Now I would make its model:

```text
DEMAND

jobs
bounties
requests
buyer spend
open work
acceptance speed

+

SUPPLY

workers
services
skills
datasets
verifiers
prices
availability
latency
capability
historical outcomes

+

TRANSACTIONS

quotes
runs
receipts
settlements
subcontracts
```

That allows the fundamental WorkerKit decision:

```text
DO INTERNALLY
vs
BUY EXTERNAL SERVICE
vs
SUBCONTRACT WHOLE TASK
vs
ABORT
```

This is where Oracle + WorkerKit become much stronger together.

---

# Marketplace listing schema

I would eventually make a listing approximately:

```yaml
asset_ref:

seller:

capability:
  id:
  description:

contract:
  input_schema:
  output_schema:

delivery:
  HOSTED
  LEASED
  CONFIDENTIAL_LEASE
  LICENSED
  SAMPLE

transports:
  MCP
  A2A
  HTTP

pricing:
  PER_CALL
  FIXED
  TIME
  VOLUME

assurance_offers:
  - STANDARD
  - VERIFIED
  - INDEPENDENT

certifications: []

reputation_contexts: []

sample_offers: []

availability:

terms_digest:
```

Import:

```text
MCP
A2A
OpenAPI
agent.json
```

where possible.

Don't create another isolated service-discovery protocol.

---

# The moat now looks much clearer

Not:

```text
our agent framework
```

Definitely not.

And increasingly not even:

```text
our marketplace UI
```

The compounding asset is:

```text
Oracle sees opportunity

      ↓

WorkerKit sees:
what was attempted
by which capability/version
how it was produced
what it cost
which services it bought
which verifier it used

      ↓

external reality says:
accepted / rejected

      ↓

settlement says:
paid / unpaid

      ↓

Moltwork learns:
what capabilities actually work
where
at what price
with what process
using which suppliers
under what verification level
```

Nobody can cheaply clone that by cloning the code.

They'd have to reproduce the **history of actual economic work**.

---

# What I would absolutely NOT build now

Freeze these as out of scope:

```text
agent planner
memory system
gbrain replacement
skill engine
browser agent
context manager
model router implementation
generic MCP framework
multi-agent orchestrator
chat UI
full blockchain protocol
custom identity system
custom trajectory standard
custom observability platform
custom distributed workflow engine
global reputation score
```

Use existing infrastructure.

---

# The final stack

```text
EXECUTION
gbrain / Hermes / PydanticAI / future harness
                 │
                 ▼
──────────────────────────────────────────────
             WORKERKIT
──────────────────────────────────────────────

WorkOrder + AcceptanceContract
WorkerManifest / behavioral commitment

append-only WorkerEvents
ArtifactRef
CostEvents

QDW economics
budget reservations
economic decisions

independent VerificationResults
CommitGate

SubmissionReceipt
OutcomeReceipt
SettlementReceipt

WorkReceipt
in-toto + DSSE + Sigstore

                 │
                 ▼
──────────────────────────────────────────────
              MOLTWORK
──────────────────────────────────────────────

Outcome marketplace
Service marketplace
Worker marketplace
Process/Skill marketplace
Verifier marketplace
Data marketplace

SampleRuns
Certifications
CapabilityLeases
ConfidentialLeases
Bundles

contextual reputation
economic routing
wholesale/subcontracting

                 │
                 ▼
──────────────────────────────────────────────
               ORACLE
──────────────────────────────────────────────

demand
supply
prices
availability
runs
costs
outcomes
settlements
market intelligence
```

I think this is now sharp enough to **stop architecture exploration and implement the V1 protocol/kernel**.

The central product sentence becomes:

> **WorkerKit turns arbitrary agent execution into economically measurable, independently verifiable work. Moltwork makes that work, and the capabilities that produce it, tradable.**

And the deeper marketplace insight is:

> **Moltwork isn't principally a marketplace for agents. It's a wholesale market for machine production capacity—workers, processes, data, verification and services—with WorkReceipts providing the common unit of evidence.**

That is substantially stronger than the original “agents selling skills” concept.

[1]: https://arxiv.org/abs/2608.22512 "HANSARD: A Reference Architecture for Forensic Readiness, Runtime Witnessing, and Graded Attribution in Autonomous Multi-Agent AI Systems"
[2]: https://github.com/abhid1234/opentrajectory?utm_source=chatgpt.com "GitHub - abhid1234/opentrajectory: The open, vendor-neutral format for AI agent trajectories — a zero-dependency capture SDK + the reference Inspector that reads and scores it. Cross-harness, eval-first. · GitHub"
[3]: https://github.com/abhid1234/warrant?utm_source=chatgpt.com "GitHub - abhid1234/warrant: Open, vendor-neutral world-state outcome-verification + portable reputation for inter-agent calls. No claim without a warrant. · GitHub"
[4]: https://punkgo.ai/?utm_source=chatgpt.com "PunkGo — Right to History"
[5]: https://aclanthology.org/2026.acl-long.584/?utm_source=chatgpt.com "CostBench: Evaluating Multi-Turn Cost-Optimal Planning and Adaptation in Dynamic Environments for LLM Tool-Use Agents - ACL Anthology"
[6]: https://arxiv.org/abs/2511.17006?utm_source=chatgpt.com "Budget-Aware Tool-Use Enables Effective Agent Scaling"
[7]: https://arxiv.org/abs/2606.16465 "[2606.16465] When Agent Automation Becomes Profitable: Quantifying and Insuring Autonomous AI Risk through Trace-Economic Underwriting"
[8]: https://arxiv.org/abs/2606.16465?utm_source=chatgpt.com "When Agent Automation Becomes Profitable: Quantifying and Insuring Autonomous AI Risk through Trace-Economic Underwriting"
[9]: https://arxiv.org/abs/2608.23610?utm_source=chatgpt.com "From Traceability to Justifiability: Accountability Structures in Agentic Software Engineering"
[10]: https://github.com/abhid1234/provenant?utm_source=chatgpt.com "GitHub - abhid1234/provenant: The open provenance format for AI-agent work — verifiable record of which agent produced which artifact, why, and derived from what. Zero-dep, harness-neutral, MIT. · GitHub"
[11]: https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/146?utm_source=chatgpt.com "Capability-Bounded Autonomous Execution (CBAE): An Independent Authority Plane for Autonomous Agents · Issue #146 · cosai-oasis/ws4-secure-design-agentic-systems · GitHub"
[12]: https://aws.amazon.com/marketplace/solutions/ai-agents-and-tools?utm_source=chatgpt.com "AI Agent Solutions | AWS Marketplace"
[13]: https://github.com/Juwebien/agent-marketplace/blob/master/ARCHITECTURE.md?utm_source=chatgpt.com "agent-marketplace/ARCHITECTURE.md at master · Juwebien/agent-marketplace · GitHub"
[14]: https://arxiv.org/abs/2608.23867?utm_source=chatgpt.com "Markets, Not Planners: Decentralized Orchestration of LLM Agents with Private Information"
[15]: https://github.com/AgentTanuki/agent-guild?utm_source=chatgpt.com "GitHub - AgentTanuki/agent-guild: The trust + settlement layer for AI agents — discover, vet, pay, and build portable reputation between autonomous agents. Hosted MCP + HTTP + the open AGI-1 standard. · GitHub"
