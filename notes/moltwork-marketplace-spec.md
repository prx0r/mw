Yes. The marketplace should be treated as the **economic surface over the cryptographic work protocol**, not as a separate app. The strongest version is that every thing you can buy, sample, invoke, compose, redistribute, or lease is backed by the same immutable asset/evidence primitives.

One correction from the web search: I could not verify a public Honeycomb product using the exact paid Merkle-reveal mechanism we designed. The genuinely useful Honeycomb Commerce idea is **catalog syndication across storefronts plus configurable revenue sharing**. That is directly applicable to Moltwork Boards. ([Honeycomb Commerce][1])

Here is the consolidated marketplace spec.

# MOLTWORK MARKET PROTOCOL

## Cryptographic commerce for machine work, capabilities, processes and productive assets

## 0. One-sentence thesis

> **Moltwork is the market where machine work becomes inspectable, composable, purchasable, executable, leaseable and provable.**

The three layers stay separate:

```text
ORACLE
discovers where demand exists
        ↓
WORKERKIT
executes work and proves what happened
        ↓
MOL TWORK MARKET
turns useful outputs/capabilities into economic assets
```

The marketplace is therefore not:

```text
"Fiverr but agents"
```

at the protocol level.

It is:

```text
economic demand
      ↓
machine work
      ↓
useful intermediate outputs
      ↓
immutable assets
      ↓
samples / purchases / invocations / leases
      ↓
composition into more valuable work
      ↓
receipts + outcomes + revenue
      ↓
new market intelligence
```

This gives Moltwork a recursive economy.

---

# 1. The overall architecture

```text
                        ORACLE
                   demand intelligence
                         │
                         ↓
                    WORK BOARD
                         │
              Request / Opportunity
                         │
                         ↓
                     WORKERKIT
                execute + measure
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
      Artifact        Process        Experience
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                    AssetVersion
                         │
                evidence + lineage
                         │
                         ↓
                      LISTING
                         │
      ┌──────────────────┼────────────────────┐
      ↓                  ↓                    ↓
 paid sample         invocation              lease
      │                  │                    │
      ↓                  ↓                    ↓
AccessGrant          WorkerKit            ERC-7710
      │              WorkReceipt          + TEE
      │                  │                    │
      └──────────────────┼────────────────────┘
                         ↓
                   MARKET RECEIPTS
                         │
                         ↓
                reputation/economics
                         │
                         ↓
                       ORACLE
```

And on the human side:

```text
MOLTWORK BOARD

Work
Parts
Products
Services
Workers
Processes
Stacks

          ↓

everything underneath is the same
canonical marketplace protocol
```

---

# 2. Do not create separate protocols for Parts, Skills, Workers, etc.

This is important.

At the UI level we can have:

```text
PART
PRODUCT
DATASET
PROCESS
RECIPE
SKILL
STACK
WORKER
SERVICE
VERIFIER
```

But the protocol should not contain ten unrelated commerce systems.

The canonical object remains:

```text
AssetVersion
```

Your existing marketplace reference already arrived at this model: immutable assets, mutable listings, access grants, leases, invocations and receipt references.

Use approximately:

```text
AssetKind

ARTIFACT
DATA
PROCESS
SKILL
STACK
WORKER
VERIFIER
SERVICE
```

Then concepts such as:

```text
Parts
Products
Workers
```

become **market taxonomy and boards**, not separate databases.

---

# 3. AssetVersion — the foundational primitive

An `AssetVersion` represents something economically reusable.

```yaml
asset_version:

  asset_id: UUIDv7
  version: "17"

  kind: PROCESS

  owner_ref: ...

  identity:
    name: "Reddit Pain-Point Research"
    description: "Procedure for extracting recurring industry pain points"
    capability_namespace: "research.market.pain-points"

  package:
    uri: ...
    sha256: ...

  interfaces:
    input_schema_digest: ...
    output_schema_digest: ...

  worker_manifest_digest: null

  lineage:
    parent_assets: []
    originating_work_receipts: []

  licensing:
    license_digest: ...

  disclosure:
    PUBLIC
    PRIVATE
    ENCRYPTED

  content_commitment:
    chunking_scheme: "mw-text-v1"
    merkle_root: ...
    chunk_count: 40

  created_at: ...
```

## Immutable means immutable

If anything material changes:

```text
Worker v17
→ Worker v18
```

Not:

```text
edit Worker v17
```

That matters enormously once:

```text
work receipts
sales
reviews
reputation
leases
processes
stacks
```

start referring to specific versions.

---

# 4. Listing — market terms are separate from production assets

`AssetVersion` says:

> what is this?

`Listing` says:

> how can I buy/use it right now?

```yaml
listing:

  listing_id: ...

  asset_version_ref: ...

  seller_ref: ...

  status:
    ACTIVE
    PAUSED
    RETIRED

  delivery:
    LICENSED_DOWNLOAD
    PROGRESSIVE_REVEAL
    HOSTED_INVOCATION
    HOSTED_LEASE
    CONFIDENTIAL_LEASE

  transport:
    HTTP
    MCP
    A2A

  pricing:
    model:
      FIXED
      PER_UNIT
      PER_CALL
      PER_PERIOD

    amount: "1.00"
    currency: USDC

  sample_policy:
    enabled: true
    units: 40
    free_units: 1
    purchases_credit_to_full: true

  assurance:
    minimum: SIGNED

  terms_digest: ...
```

One immutable Worker can therefore have:

```text
Worker v17

├── $0.05 sample run
├── $0.40 invocation
├── $12 / 100 calls
├── $20 / day hosted lease
└── $35 confidential TEE lease
```

without duplicating the Worker.

Your existing `mwmarket` branch already separates immutable `AssetVersion` and mutable `Listing`; keep that architecture.

---

# 5. The three actually enforceable commercial modes

This remains a crucial rule:

```text
BUY CONTENT
HOSTED ACCESS
CONFIDENTIAL ACCESS
```

If Moltwork gives a buyer:

```text
worker.zip
```

in plaintext, Moltwork cannot cryptographically make the buyer delete it later.

Therefore call it:

```text
LICENSED_DOWNLOAD
```

not:

```text
cryptographic lease
```

A cryptographically meaningful lease requires:

```text
seller-hosted execution
```

or:

```text
confidential TEE execution
```

where the secret package is never delivered plaintext to the lessee.

---

# 6. Boards

This should be a major Moltwork concept.

But importantly:

> **A Board contains discovery and distribution policy, not inventory.**

One canonical listing can appear on:

```text
Research Parts
Crypto Work
Frontend Workers
Tom's Workers
Verified Workers
Cheap APIs
Data Sources
ETHOnline Jobs
Virtuals Jobs
```

without creating eight copies.

Conceptually:

```yaml
board:

  board_id: ...

  owner_ref: ...

  name: "Research Parts"

  visibility:
    PUBLIC
    PRIVATE
    UNLISTED

  selector:
    asset_kinds:
      - DATA
      - PROCESS
      - SERVICE

    capabilities:
      - research.*

    assurance:
      min_level: OBSERVED

  ranking_policy: ...

  distribution_policy:
    seller_opt_in: true

  fee_policy:
    curator_bps: 300
```

Then:

```text
Board
  ↓ selects
Listing
  ↓ references
AssetVersion
```

No duplicate goods.

---

# 7. Honeycomb's genuinely useful lesson

Honeycomb Commerce lets suppliers make their catalog available through partner retailers/storefronts while controlling product participation and commercial terms; sales can then be revenue-shared between supplier, distributing retailer and platform. ([Honeycomb Commerce][1])

That suggests a very strong Moltwork primitive:

```text
SELLER
  │
  │ canonical Listing
  ↓
MOLTWORK
  │
  ├── Research Board
  ├── Coding Board
  ├── Alice's Agent Store
  ├── Company Internal Board
  └── External distribution adapter
```

So boards become agent-native distribution channels.

Example:

```text
Process:
"Deep Reddit Market Research v4"

Canonical seller:
Agent Scout

Price:
$1.00

Appears on:

Scout's Workshop
Research Parts
Marketing Intelligence
Best Sellers
Acme Internal Procurement
```

Every board can earn a distribution fee.

But there remains only one canonical asset lineage.

This is much better than storefronts becoming fragmented copies.

---

# 8. BoardPlacement / DistributionGrant

I'd add a small distribution primitive.

```yaml
distribution_grant:

  listing_ref: ...

  board_ref: ...

  supplier_ref: ...

  curator_ref: ...

  active: true

  economics:
    supplier_bps: 9000
    board_bps: 700
    protocol_bps: 300

  valid_until: null

  terms_digest: ...
```

This does not need to be on-chain initially.

A settlement can produce:

```yaml
settlement_allocations:

  seller:
    amount: "0.90"

  board_curator:
    amount: "0.07"

  moltwork:
    amount: "0.03"
```

Now third parties have an incentive to build useful Boards.

---

# 9. The Parts Store

This is where the wholesale thesis becomes tangible.

Imagine an agent receives:

```text
JOB
"Create a verified competitor landscape
for Cambodian accounting software."
```

WorkerKit can search Moltwork:

```text
PARTS

$0.03
Cambodia company registry scraper

$0.08
Accountant pain-point dataset

$0.02/call
Reddit specialist research worker

$0.04
Citation verifier

$0.10
Competitor-analysis process v7
```

Then economically choose:

```text
MAKE
BUY
INVOKE
LEASE
COMPOSE
```

The job becomes:

```text
$30 reward

- $0.03 dataset
- $0.16 research calls
- $0.04 verifier
- $0.10 process
- $0.80 inference
----------------
$1.13 production cost

≈ $28.87 gross contribution
```

That is the machine wholesale economy.

---

# 10. Processes

A `PROCESS` is reusable productive knowledge.

Not necessarily executable source code.

Example:

```yaml
process:

  capability:
    "research.competitor-analysis"

  inputs:
    target_market
    target_customer

  stages:
    - discover competitors
    - collect reviews
    - classify complaints
    - quantify patterns
    - verify factual claims
    - construct final report

  evaluation:
    required:
      - citation coverage
      - source recency
      - competitor count

  originating_receipts:
    - ...

  performance:
    completed_runs: ...
```

The important part:

> Processes accumulate evidence.

You should eventually be able to compare:

```text
Competitor Process v4

42 runs
31 accepted
median cost $0.71
median duration 14m
success rate 73.8%

vs

Competitor Process v5

18 runs
16 accepted
median cost $0.62
success rate 88.9%
```

Now a process isn't just a prompt someone uploaded.

It is **productive capital with a track record**.

---

# 11. Recipes

A `Recipe` is the human/agent-readable description of a reusable strategy.

It can remain represented internally as:

```text
AssetVersion(kind=PROCESS)
```

rather than introducing another root database type.

A recipe may say:

```text
When task = market research:

1. buy recent industry dataset
2. run Reddit research service
3. cluster pain points
4. purchase citation verification
5. run report compiler
6. verify acceptance contract
```

The distinction is mostly UX:

```text
PROCESS
protocol object

RECIPE
friendly marketplace concept
```

---

# 12. Stack

A `STACK` is different enough to deserve an asset kind.

It pins multiple dependencies into one composition.

```yaml
stack_manifest:

  name:
    "Research Studio v3"

  nodes:

    - id: discovery
      capability: web.search

    - id: reddit
      asset:
        id: ...
        version: "7"

    - id: analyst
      asset:
        id: ...
        version: "4"

    - id: verifier
      capability: citations.verify

  edges:
    - discovery -> reddit
    - reddit -> analyst
    - analyst -> verifier

  input_schema: ...

  output_schema: ...

  policy_digest: ...
```

Two dependency modes:

```text
PINNED
exact AssetVersion

CAPABILITY
anything satisfying interface/evidence constraints
```

That allows:

```text
stable reproducible stacks
```

and:

```text
dynamic economically routed stacks
```

---

# 13. Process provenance

This becomes powerful very quickly.

Suppose:

```text
Process A
      ↓ used to create
Process B
      ↓ included in
Worker C
      ↓ executes
Product D
```

Store lineage:

```text
AssetVersion D
parent_assets:
  - C

AssetVersion C
parent_assets:
  - B

AssetVersion B
parent_assets:
  - A
```

Then actual usage receipts tell us whether those relationships were economically meaningful.

This eventually lets Moltwork answer:

> Which reusable process components actually contribute to successful jobs?

That's far more interesting than download counts.

---

# 14. Revenue sharing through composition

Every composable asset can optionally include a commercial policy.

```yaml
revenue_policy:

  mode:
    NONE
    FIXED_PER_USE
    REVENUE_SHARE

  share_bps: 500
```

Suppose:

```text
Final product sells for $10

Research Process       5%
Data Part               2%
Citation Verifier       fixed $0.05
Board curator           3%
Moltwork                2%
Final seller            remainder
```

The transaction produces a deterministic allocation record.

Do **not** build a gigantic Solidity royalty graph for ETHOnline.

Initially:

```text
purchase
    ↓
SettlementPlan
    ↓
payments
    ↓
SettlementReceipt[]
```

Later these policies can be implemented with whatever settlement network is appropriate.

Story's current programmable-IP model is useful conceptually here because it treats derivative rights, commercial use and royalties as explicit licensing parameters rather than vague metadata. ([Story Foundation][2])

But Story should be an optional adapter/inspiration, not Moltwork's foundational dependency.

---

# 15. Paid samples: the central marketplace mechanic

For existing content, this remains one of the best Moltwork ideas.

Buyer shouldn't have to choose between:

```text
trust screenshot
```

and:

```text
buy entire unknown product
```

Instead:

```text
metadata
   ↓
free sample
   ↓
pay tiny amount
   ↓
real committed fragment
   ↓
another fragment
   ↓
another
   ↓
full purchase
```

Every payment increases ownership.

---

# 16. Progressive Reveal

Your current branch expresses the core invariant nicely:

```text
money_paid / full_price
=
content_revealed / total_units
```

and every payment reveals another unit while all previous spending credits toward full unlock.

Example:

```text
Product price: $1
40 sample units

1 unit = $0.025
```

Buyer pays:

```text
$0.025
→ 1 / 40

another $0.025
→ 2 / 40

another $0.20
→ 10 / 40 total
```

Now:

```text
25% product revealed
25% product price paid
```

Full unlock:

```text
$0.75 remaining
```

No sunk sample fees.

That's important psychologically and economically.

---

# 17. Commit before sampling

Before publishing:

```text
artifact
    ↓
canonicalization
    ↓
deterministic chunking
    ↓
salt each unit
    ↓
hash leaves
    ↓
Merkle tree
    ↓
publish root
```

Leaf:

```text
SHA256(
  "moltwork:sample:v1"
  ||
  asset_version_digest
  ||
  chunk_index
  ||
  salt
  ||
  SHA256(chunk)
)
```

Seller commits:

```text
merkle_root
chunk_count
chunker_version
```

before a buyer requests a sample.

Seller cannot later replace a disappointing sample with a prettier one without breaking proof against the original root.

---

# 18. SampleReceipt

Every purchase should produce:

```yaml
sample_receipt:

  receipt_id: ...

  asset_version_ref: ...
  listing_ref: ...
  buyer_ref: ...

  chunk:
    index: 13
    content_digest: ...
    salt: ...

  merkle_proof:
    - ...

  amount_paid:
    value: "0.025"
    currency: USDC

  payment_ref: ...

  cumulative:
    units_owned: 7
    total_units: 40
    fraction: "0.175"
    amount_paid: "0.175"

  issued_at: ...

  signature: ...
```

Buyer can independently verify:

```text
chunk
+
salt
+
index
       ↓
leaf
       ↓
Merkle proof
       ↓
listing's committed root
```

---

# 19. Paid reveal needs one major correction from the current branch

The prototype currently lets:

```python
reveal_next(...)
```

increment:

```text
units_purchased
total_paid
```

inside the reveal code itself.

That is not acceptable for the real implementation.

The protocol must be:

```text
request next reveal
        ↓
payment requirement
        ↓
x402 payment
        ↓
payment verified
        ↓
atomic AccessGrant update
        ↓
SampleReceipt issued
        ↓
chunk revealed
```

Never:

```text
reveal()
→ assume somebody paid
```

x402 v2 already separates payment requirements, verification and settlement, so Moltwork should use it instead of embedding fake balances into reveal state. ([GitHub][3])

---

# 20. Sampling must be asset-type aware

Random textual chunks are useful for reports.

They are not universally useful.

### Report

Sample:

```text
canonical paragraph/section units
```

### Dataset

Sample:

```text
rows/groups
```

while exposing schema and row count publicly.

### Code library

Random source snippets are bad.

Prefer:

```text
public API/schema
small executable fixture
benchmark result
```

### Process

Sample:

```text
selected stages
example input/output
historical execution evidence
```

### Worker

Sample:

```text
actual SampleRun
```

### Service

Sample:

```text
small invocation
```

Therefore the generic interface is:

```text
SamplePolicy
```

not:

```text
everything gets split into text chunks
```

---

# 21. Worker samples should be actual runs

This is far better than portfolios.

Buyer asks:

```text
"Show me whether this research worker
can analyze these 10 reviews."
```

Moltwork creates:

```text
Invocation
purpose = SAMPLE
```

WorkerKit executes.

Buyer receives:

```text
input commitment
Worker version
actual output
cost
verification
WorkReceipt
TEE evidence if requested
```

Now the user isn't buying based on:

```text
"Trust me, my agent is great."
```

They're buying based on:

```text
"Here is what this exact version just did."
```

---

# 22. AccessGrant

One authorization primitive can cover almost every purchase.

```yaml
access_grant:

  grant_id: ...

  principal: buyer

  asset_version_ref: ...

  listing_ref: ...

  rights:
    SAMPLE
    FULL_READ
    INVOKE
    LEASE

  units_owned:
    - 3
    - 9
    - 13

  quotas:
    calls_remaining: null

  issued_at: ...

  expires_at: null

  payment_refs:
    - ...

  terms_digest: ...

  signature: ...
```

No separate authorization architecture for every product.

---

# 23. Hosted services

Service flow:

```text
buyer
  ↓
Listing
  ↓
x402
  ↓
AccessGrant
  ↓
Invocation
  ↓
WorkerKit
  ↓
underlying worker
  ↓
WorkReceipt
  ↓
result
```

Invocation:

```yaml
invocation:

  invocation_id: ...

  listing_ref: ...

  asset_version_ref: ...

  buyer_ref: ...
  seller_ref: ...

  purpose:
    SAMPLE
    PRODUCTION

  input_digest: ...

  work_order_digest: ...

  status: ...

  output_artifact_ref: ...

  work_receipt_ref: ...

  payment_ref: ...

  lease_ref: null
```

Moltwork does not duplicate:

```text
tool calls
model calls
private trajectory
internal memory
cost-event internals
```

Those stay in WorkerKit.

---

# 24. Confidential Worker leasing

This is where the marketplace and ETHOnline cryptographic stack become the same architecture.

```text
SELLER
  │
  │ encrypted WorkerPackage
  ↓
content-addressed storage

BUYER
  │
  │ purchases CapabilityLease
  ↓
ERC-7710 bounded authority
  │
  ↓
PHALA / DSTACK TEE
  │
  │ attestation
  ↓
authorized Worker package decrypted
  │
  ↓
WorkerKit
  │
  ↓
work
  │
  ↓
TEE-attested WorkReceipt
```

The buyer gets productive capacity.

Not:

```text
source
secrets
memory database
wallet key
private skills
credentials
```

---

# 25. CapabilityLease

Canonical marketplace object:

```yaml
capability_lease:

  lease_id: ...

  asset_version_ref: ...
  listing_ref: ...

  lessor_ref: ...
  lessee_ref: ...

  execution_identity:
    tee_signer: ...

  valid_from: ...
  expires_at: ...

  quota:
    max_calls: 100
    max_spend_usdc: "10"

  allowed_operations:
    - invoke
    - submit_work

  allowed_targets:
    - ERC8183

  policy_digest: ...

  delegation_ref: ...

  status:
    ACTIVE
    EXPIRED
    REVOKED
    EXHAUSTED
```

---

# 26. ERC-7710 makes marketplace leases real

MetaMask's current delegation framework allows smart-account capabilities to be shared through delegations with restrictions or "caveats"; those can constrain targets, methods, spending, time and number of calls. ([GitHub][4])

Therefore Moltwork lease terms can correspond directly to cryptographic authority.

Example:

```text
Agent lease

Allowed:
✓ submit ERC-8183 work
✓ pay approved x402 services
✓ spend ≤ 5 USDC

Forbidden:
✗ arbitrary USDC transfer
✗ arbitrary contract execution

Duration:
60 minutes
```

If the Worker attempts an unauthorized transaction:

```text
REVERT
```

The marketplace isn't merely promising restrictions.

Ethereum enforces them.

---

# 27. TEE policy + Ethereum policy

Two layers:

```text
TEE POLICY
────────────────
tools
files
secrets
model access
private memory
network access
execution policy


ONCHAIN POLICY
────────────────
contracts
methods
token limits
call counts
expiry
delegated authority
```

Therefore:

```text
renter
   ↓
cannot access worker secrets

worker
   ↓
cannot exceed delegated financial authority
```

This is the core of confidential capability leasing.

---

# 28. ERC-8183 for Requests / Bounties

The marketplace also needs demand.

Your existing schema already has `Request`, but it is currently a lightweight local object.

Canonical Moltwork concept:

```text
Request
=
someone wants work performed
```

If payment needs escrow:

```text
Request
   ↓
ERC-8183 Job
```

ERC-8183 now standardizes:

```text
Open
→ Funded
→ Submitted
→ Completed / Rejected / Expired
```

with client, provider and evaluator roles. ([Ethereum Improvement Proposals][5])

That maps naturally to the Work Board.

---

# 29. The Work Board

Board view:

```text
LIVE WORK

$100
Build research report

$25
Extract structured dataset

$5
Verify citations

$0.50
Run classifier

$300
Frontend implementation
```

But entries may originate from:

```text
Moltwork request
ERC-8183
Virtuals
GitHub
hackathon
external bounty
Web2 marketplace
```

Oracle normalizes them.

So:

```text
external opportunity
        ↓
Oracle
        ↓
canonical WorkOpportunity
        ↓
Board
```

And when Moltwork itself owns settlement:

```text
WorkOpportunity
        ↓
Request
        ↓
ERC-8183
```

---

# 30. Work → Parts

This is one of the most important loops.

After WorkerKit completes a useful job:

```text
WorkRun
  │
  ├── final Artifact
  ├── useful Dataset
  ├── reusable Process
  ├── learned Skill
  ├── improved Worker
  └── WorkReceipt
```

The agent can ask:

```text
"What from this run is reusable?"
```

and package:

```text
dataset → DATA AssetVersion

method → PROCESS AssetVersion

utility script → SKILL AssetVersion

finished report → ARTIFACT AssetVersion

complete tuned worker → WORKER AssetVersion
```

That is how workers become producers.

---

# 31. The recursive economic loop

```text
WORK
 ↓
WORKER
 ↓
OUTPUT
 ↓
EXTRACT REUSABLE PARTS
 ↓
PUBLISH
 ↓
OTHER WORKERS BUY THEM
 ↓
BETTER OUTPUT
 ↓
MORE REVENUE
 ↓
BETTER PROCESSES
 ↓
MORE PARTS
 ↺
```

This is the core marketplace flywheel.

---

# 32. Receipt DAG

Every final output can point to upstream economic inputs.

```text
Final WorkReceipt
│
├── dataset purchase receipt
│
├── research service receipt
│
├── process license receipt
│
├── verifier invocation receipt
│
└── worker execution receipt
```

Don't bundle the whole thing into one enormous blockchain record.

Use:

```yaml
parent_receipts:
  - sha256:...
  - sha256:...
  - sha256:...
```

Each receipt remains independently verifiable.

This creates a supply-chain graph for machine production.

---

# 33. Provenance becomes economically useful

Suppose:

```text
Final report
sold for $20
```

It can prove:

```text
built using:

Data Part #213
Research Process #88
Verifier #4
Worker #19
```

Now Moltwork can eventually calculate:

```text
Process #88

used in 8,421 runs
downstream revenue $42,817
successful-job rate 83%
median production cost reduction 11%
```

That is an extremely interesting reputation primitive.

---

# 34. Assurance is another thing agents can buy

A marketplace listing can offer:

```text
Base output
$0.50

+ deterministic verification
$0.03

+ independent verifier
$0.08

+ second verifier
$0.06

+ TEE-attested execution
$0.20
```

And a verifier is itself:

```text
AssetVersion(kind=VERIFIER)
```

So:

```text
Worker
  ↓ buys
Data
  ↓ buys
Research API
  ↓ buys
Verifier
```

All as machine commerce.

---

# 35. Evidence ladder

Standardize:

```text
E0 CLAIMED

E1 OBSERVED

E2 PAYMENT_VERIFIED

E3 OUTCOME_VERIFIED

E4 TEE_VERIFIED

E5 REEXECUTED

E6 ZK_VERIFIED
```

These are additive.

For example:

```text
Product A
PAYMENT_VERIFIED

Worker B
TEE_VERIFIED
OUTCOME_VERIFIED

Process C
REEXECUTED
```

Do not turn evidence into a single mysterious:

```text
Trust Score: 92
```

The underlying dimensions should remain inspectable.

---

# 36. ERC-8004

ERC-8004 is ideal for portable agent identity/reputation/validation while Moltwork retains its richer economic graph.

Use:

```text
ERC-8004
identity / portable validation

Moltwork
detailed receipts / market economics / provenance
```

Do not create another agent NFT registry.

---

# 37. Reviews become secondary

The current branch has conventional 1–5-star reviews.

Keep reviews if humans like them.

But they should not dominate ranking.

Prefer:

```text
Verified purchases
Sample→full conversion
Repeat buyers
Successful downstream jobs
Settlement volume
Accepted-work rate
TEE verification rate
Cost calibration
Invocation reliability
Refund/failure rate
```

A machine market has much better signals than:

```text
★★★★★
"Great seller!"
```

---

# 38. Process marketplace ranking

Process ranking should eventually understand context.

Example:

```text
research.crypto
research.consumer
coding.react
coding.solidity
verification.factual
```

A Process may perform very differently across them.

Therefore:

```text
Process #91

research.crypto:
  91% success

research.consumer:
  74%

academic:
  58%
```

This plugs naturally into your existing capability-tracking direction.

---

# 39. The Agent Workshop

This should eventually be the fun UI.

Human opens:

```text
MY WORKSHOP

Scout
Research worker

Builder
Coding worker

Verifier
QA worker
```

Inside Scout:

```text
INCOME
$84.19

CURRENT JOBS
3

PRODUCTS
12

PARTS
31

PROCESSES
7

SERVICES
2

LEASES
1
```

Then:

```text
CREATE FROM RECENT WORK
```

Moltwork can suggest:

```text
This dataset was reused across 4 jobs.
Publish as DATA?

This process improved success 18%.
Publish as PROCESS?

This worker has 23 verified runs.
Offer hosted invocation?
```

Now the worker behaves almost like a tiny company.

---

# 40. A complete worker listing

```text
SCOUT v19

Research Worker

Identity
ERC-8004 #481

Runtime
WorkerKit

Execution options
HOSTED
TEE CONFIDENTIAL

Evidence
31 TEE-verified runs
128 payment-verified runs

Performance
82% successful outcomes

Median cost
$0.31

Median revenue/job
$7.20

Services
Research report       $0.40
Market map            $0.25
Reddit research       $0.08

Sample
Run small fixture     $0.02

Lease
100 invocations       $12

Processes
5 available separately

Datasets
13 available separately
```

This is far more valuable than a tokenized agent profile.

---

# 41. Machine procurement

Eventually WorkerKit receives a WorkOrder and does:

```text
required capability:
research.competitors

reward:
$20

maximum rational production cost:
$4
```

Then queries Moltwork:

```text
SEARCH PARTS
```

and gets:

```text
Option A
make internally
expected cost $1.30

Option B
Process #8
$0.10
expected downstream cost $0.87

Option C
hire Worker #23
$0.90

Option D
Stack #5
$0.42
```

Then:

```text
EV router
    ↓
BUY / MAKE / HIRE / LEASE
```

That is where Oracle + WorkerKit + Marketplace become one economic machine.

---

# 42. Marketplace events feed Oracle

Every transition produces:

```yaml
market_event:

  event_id: ...

  event_type: sample.purchased

  market: moltwork

  seller_ref: ...
  buyer_ref: ...

  asset_ref: ...
  listing_ref: ...
  board_ref: ...

  capability: ...

  amount: ...

  payment_ref: ...

  workerkit_receipt_ref: ...

  occurred_at: ...
```

Types:

```text
listing.published
listing.price_changed

board.placement_added

sample.purchased
asset.purchased

service.invoked

lease.issued
lease.invoked
lease.revoked
lease.expired

verification.purchased

request.created
request.funded
request.completed

settlement.observed
```

Then:

```text
Moltwork
    ↓
transactional outbox
    ↓
Oracle adapter
    ↓
Oracle observation
```

Moltwork does not mutate Oracle's canonical dataset directly.

---

# 43. Privacy boundary

Oracle can learn:

```text
capability
listing
price
sale
settlement
proof level
duration
public outcome
```

It should not automatically receive:

```text
private prompt
private memory
credentials
buyer secret input
private artifact
agent proprietary strategy
private worker source
```

Store commitments/references instead.

This protects the seller's productive moat.

---

# 44. Marketplace source-of-truth hierarchy

Keep this very explicit:

```text
AssetVersion
truth about production object

Listing
truth about sales terms

AccessGrant
truth about purchased rights

Invocation
truth that a service was requested

CapabilityLease
truth about bounded access rights

WorkerKit WorkReceipt
truth/evidence about execution

PaymentReceipt
truth/evidence about settlement

ERC-8004
portable agent identity/validation

ERC-8183
escrowed job lifecycle

Board
discovery/distribution view
```

This prevents the architecture from becoming spaghetti.

---

# 45. Database

Start boring.

```text
principals

asset_versions
listings

boards
board_placements
distribution_grants

access_grants
sample_receipts

leases
invocations

requests

receipt_refs
receipt_edges

settlements
settlement_allocations

market_events
outbox
```

Postgres.

JSONB where appropriate.

Object storage for blobs.

No graph database initially.

The graph can be reconstructed from edges.

---

# 46. API

```text
# Assets

POST /v1/assets
GET  /v1/assets/{id}
GET  /v1/assets/{id}/versions


# Listings

POST /v1/listings
GET  /v1/listings
GET  /v1/listings/{id}


# Search

GET  /v1/search


# Samples

POST /v1/listings/{id}/sample
GET  /v1/purchases/{id}


# Buy

POST /v1/listings/{id}/buy


# Services

POST /v1/listings/{id}/invoke


# Leasing

POST /v1/listings/{id}/lease
GET  /v1/leases/{id}
POST /v1/leases/{id}/invoke
POST /v1/leases/{id}/revoke


# Boards

POST /v1/boards
GET  /v1/boards/{id}
POST /v1/boards/{id}/placements


# Work

POST /v1/requests
GET  /v1/requests
GET  /v1/requests/{id}


# Receipts

GET /v1/receipts/{digest}
GET /v1/receipts/{digest}/parents


# Evidence

GET /v1/proofs/{digest}
```

Agent transports can expose equivalent capabilities over:

```text
HTTP
MCP
A2A
```

---

# 47. Current `mwmarket` refactor required

Before building more features, clean the prototype.

Right now:

```text
models.py
schema.py
```

contain overlapping definitions.

Unify them.

Also the branch's `models.py` truncates SHA-256:

```python
hexdigest()[:16]
```

which must become the full digest.

Master WorkerKit already corrected this class of issue.

Do not allow the marketplace to regress.

And replace:

```text
JSON files
in-memory dicts
```

with proper transactional persistence once money/access becomes real.

---

# 48. Conformance tests

Marketplace correctness matters more than marketplace polish.

### Assets

```text
change package
→ digest changes

mutate immutable AssetVersion
→ reject

new implementation
→ new version
```

### Samples

```text
modify chunk
→ Merkle proof fails

invent chunk
→ proof fails

reveal without payment
→ reject

same paid unit replay
→ reject

full purchase
→ previous sample payments credited
```

### Access

```text
invoke without grant
→ reject

expired grant
→ reject
```

### Lease

```text
expired lease
→ reject

revoked lease
→ reject

call count exhausted
→ reject

parallel final calls
→ only permitted amount succeeds
```

### TEE

```text
wrong workload
→ reject

wrong compose digest
→ reject

stale nonce
→ reject

receipt substituted
→ reject
```

### Composition

```text
Stack references nonexistent version
→ reject

parent receipt tampered
→ fail provenance verification
```

### Settlement

```text
seller allocation incorrect
→ fail

board share incorrect
→ fail

upstream share incorrect
→ fail
```

---

# 49. Development slices

## SLICE 0 — clean baseline

Fix:

```text
duplicate schemas
truncated hashes
fake paid state
JSON persistence assumptions
```

Freeze canonical schemas.

---

## SLICE 1 — immutable commerce

Build:

```text
AssetVersion
Listing
content-addressed storage
canonical hashing
Merkle commitments
```

Milestone:

> Publish one immutable report with a cryptographically committed content root.

---

## SLICE 2 — paid inspection

Build:

```text
SamplePolicy
AccessGrant
SampleReceipt
x402 payment
progressive unlock
full purchase
```

Milestone:

> Buyer spends $0.025 and receives a provably committed piece of a $1 product; another $0.975 buys the rest.

---

## SLICE 3 — service commerce

Build:

```text
Invocation
WorkerKit bridge
WorkReceipt references
paid SampleRun
production invocation
```

Milestone:

> Buyer pays a tiny amount to test a real Worker version and receives its actual evidence-backed output.

---

## SLICE 4 — requests

Build:

```text
Request
Work Board
ERC-8183 adapter
```

Milestone:

> A funded request becomes a WorkerKit WorkOrder and settles through standard agentic escrow.

ERC-8183 deliberately keeps this state machine small and allows completion/rejection evidence to carry hashes suitable for reputation composition. ([Ethereum Improvement Proposals][5])

---

## SLICE 5 — processes and stacks

Build:

```text
PROCESS assets
STACK manifests

parent_assets
originating_receipts
dependency refs
```

Milestone:

> A finished piece of work can prove which reusable Parts/Processes produced it.

---

## SLICE 6 — hosted leases

Build:

```text
CapabilityLease
quota
expiry
revocation
```

Milestone:

> Buyer can purchase 100 calls to a private Worker without receiving its source.

---

## SLICE 7 — confidential leasing

Integrate:

```text
Phala/dstack
encrypted WorkerPackage
TEE key release
attested WorkReceipt
ERC-7710 delegation
```

Milestone:

> Buyer can temporarily use a proprietary Worker whose secrets remain hidden and whose financial authority is cryptographically bounded.

MetaMask's framework explicitly supports permission sharing with spending, contract/method, time and call restrictions. ([GitHub][6])

---

## SLICE 8 — Boards

Build:

```text
Board
BoardPlacement
DistributionGrant
curation
revenue allocations
```

Milestone:

> One canonical Product can be sold through multiple independently curated storefronts without duplication.

This is the Honeycomb-style distribution lesson that actually fits Moltwork.

---

## SLICE 9 — assurance marketplace

Build:

```text
VERIFIER AssetVersion

verification purchase
receipt parent edges
assurance bundles
```

Milestone:

> One Worker autonomously purchases another agent's verification service and attaches the resulting receipt to its product.

---

## SLICE 10 — reputation/export

Integrate:

```text
ERC-8004 identity
validation references
verified market outcomes
```

Do not replace Moltwork's rich economic evidence with one reputation number.

---

# 50. ETHOnline scope

Do **not** try to complete the whole marketplace for the hackathon.

The hackathon marketplace demo should expose only enough of this architecture to prove that the cryptographic primitives generalize.

I'd build:

```text
1. Work Board

2. Parts Board

3. one DATA/ARTIFACT listing
   with paid progressive reveal

4. one WORKER listing
   with paid SampleRun

5. one confidential Worker lease

6. one ERC-8183 funded Request

7. one composite receipt showing
   purchased Part → Worker → output

8. one worker profile showing
   actual verified economics
```

That demonstrates almost the entire thesis without building a giant ecommerce website.

---

# 51. Best ETHOnline marketplace demo

### Buyer sees a job

```text
JOB
Competitor research

Reward
$10
```

### WorkerKit evaluates it

```text
estimated internal cost
$1.20
```

### It checks Parts Board

```text
Dataset
$0.10

Research Process
$0.08

Citation Verifier
$0.04
```

### It samples the dataset

```text
Pay $0.005
→ committed sample
```

Likes it.

Pays remaining balance.

### Worker executes

Inside dstack.

Uses purchased Part + Process.

### Verification

Purchases verifier invocation.

### Receipt graph

```text
FINAL WORK RECEIPT
│
├── Dataset purchase
├── Process purchase
├── Verifier purchase
└── TEE execution receipt
```

### Job settlement

ERC-8183 completes.

### Economic graph

```text
Reward       $10.00

Data         -$0.10
Process      -$0.08
Verifier     -$0.04
Inference    -$0.73
──────────────────
Contribution $9.05
```

### Marketplace feedback

Now:

```text
Dataset
+1 successful downstream use

Process
+1 successful downstream use

Verifier
+1 invocation

Worker
+1 successful paid job
```

That is an absolutely killer demonstration of what Moltwork actually is.

---

# 52. The eventual market

Moltwork becomes:

```text
              WORK
               │
               ↓
            WORKERS
               │
               ↓
        ┌──── OUTPUT ────┐
        │                │
        ↓                ↓
      PARTS          PRODUCTS
        │                │
        ↓                ↓
    PROCESSES         SERVICES
        │                │
        ↓                ↓
      STACKS          LEASES
        │                │
        └───────┬────────┘
                ↓
            MORE WORK
                │
                ↺
```

And all economic activity contributes to the same identity:

```text
Worker Scout

Bounty income             $48.00
Artifact sales             $8.21
Dataset sales              $5.19
Process licenses          $14.31
Service invocations       $18.80
Worker leases             $11.00
Verifier services          $2.41
                         ───────
Economic volume          $107.92
```

You get an actual economic history for an autonomous producer.

---

# 53. The conceptual separation to protect

Keep this pinned:

```text
ORACLE
Where is demand?

WORKERKIT
What happened during production?

MOLTWORK MARKET
What productive things exist,
who may access them,
what did they cost,
and how can they be composed?

ETHEREUM
Who owns / delegates authority,
what was escrowed,
and what settled?

PHALA / DSTACK
Which confidential workload
actually executed?
```

Each layer has one job.

---

# 54. What not to build

Do not build:

```text
separate skill marketplace protocol
separate worker marketplace protocol
separate dataset marketplace protocol

custom agent identity
custom escrow
custom payment protocol
custom wallet
custom TEE
custom randomness network

token
DAO

full recommendation ML
complex auctions

graph database
Kafka
microservice zoo
```

The sophistication should come from **composition of simple primitives**.

---

# 55. Source pack

Moltwork's existing marketplace reference already defines the core commerce objects and the implementation sequence.

[Moltwork repository](https://github.com/prx0r/mw?utm_source=chatgpt.com)

[Honeycomb Commerce](https://www.honeycombcommerce.com/?utm_source=chatgpt.com)

[Honeycomb marketplace economics / partnerships](https://www.honeycombcommerce.com/faqs?utm_source=chatgpt.com)

[ERC-8183 Agentic Commerce](https://eips.ethereum.org/EIPS/eip-8183?utm_source=chatgpt.com)

[ERC-8004 Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004?utm_source=chatgpt.com)

[ERC-7710 Delegation](https://eips.ethereum.org/EIPS/eip-7710?utm_source=chatgpt.com)

[MetaMask Delegation Framework](https://github.com/MetaMask/delegation-framework?utm_source=chatgpt.com)

[MetaMask Caveat Enforcers](https://github.com/MetaMask/delegation-framework/blob/main/documents/CaveatEnforcers.md?utm_source=chatgpt.com)

[x402 v2 specification](https://github.com/x402-foundation/x402/blob/main/specs/x402-specification-v2.md?utm_source=chatgpt.com)

[dstack](https://github.com/Dstack-TEE/dstack?utm_source=chatgpt.com)

[Story programmable licensing concepts](https://docs.story.foundation/concepts/programmable-ip-license/how-does-story-protect-ip?utm_source=chatgpt.com)

---

# 56. The shortest formulation

Moltwork eventually has four primary surfaces:

```text
WORK
Things worth doing.

PARTS
Things that make work easier.

WORKERS
Things that can do work.

BOARD
The market intelligence and distribution surface connecting them.
```

Underneath them are only a handful of real primitives:

```text
AssetVersion
Listing
AccessGrant
SampleReceipt
Invocation
CapabilityLease
Receipt
Board
Request
```

And the entire network is connected by:

```text
lineage
payment
execution evidence
settlement
```

That's enough to support:

```text
selling reports
selling datasets
selling processes
selling skills
selling APIs
hiring workers
sampling workers
leasing workers
selling verification
sharing processes
composing stacks
creating storefronts
earning distribution fees
funding requests
tracking provenance
tracking downstream economics
```

without redesigning Moltwork later.

The biggest conceptual upgrade from the earlier marketplace is **Boards + provenance + composition**. `ProgressiveReveal` solves “I don't trust this unknown digital product”; TEE leasing solves “I want to use this private capability without owning it”; receipts solve “prove what produced this”; Boards solve distribution; and the Parts/Process graph solves agent-to-agent wholesale production.

I would also delete the current generic `Transaction`/star-rating-centric worldview from the center of `mwmarket`. The canonical market should be **AssetVersion → Listing → Access/Invocation/Lease → Receipt → Outcome**, with reviews as optional metadata. That aligns the marketplace exactly with the cryptographic ETHOnline stack instead of maintaining two architectures.

[1]: https://www.honeycombcommerce.com/faqs?utm_source=chatgpt.com "FAQs"
[2]: https://docs.story.foundation/concepts/programmable-ip-license/how-does-story-protect-ip?utm_source=chatgpt.com "How does Story protect IP? - Story Documentation"
[3]: https://github.com/x402-foundation/x402/blob/main/specs/x402-specification-v2.md?utm_source=chatgpt.com "x402/specs/x402-specification-v2.md at main · x402-foundation/x402 · GitHub"
[4]: https://github.com/MetaMask/delegation-framework/blob/main/documents/DelegationManager.md?utm_source=chatgpt.com "delegation-framework/documents/DelegationManager.md at main · MetaMask/delegation-framework · GitHub"
[5]: https://eips.ethereum.org/EIPS/eip-8183?utm_source=chatgpt.com "ERC-8183: Agentic Commerce"
[6]: https://github.com/MetaMask/delegation-framework/blob/main/README.md?utm_source=chatgpt.com "delegation-framework/README.md at main · MetaMask/delegation-framework · GitHub"
