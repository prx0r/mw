## Yes — but build on **dstack**, not on “Phala” as a dependency

For Moltwork specifically, **dstack + Phala Cloud is the strongest starting point I can find right now**.

The distinction matters:

* **dstack** = open-source confidential-compute framework.
* **Phala Cloud** = convenient first infrastructure provider running dstack.
* **Moltwork** = protocol above dstack defining what an agent identity, lease, job, execution receipt, proof and reputation signal actually mean.

dstack already gives you the annoying TEE plumbing: Docker-native confidential VMs, reproducible OS measurements, application measurement via the compose hash, deterministic per-application keys, KMS, attestation, RA-TLS, TDX, Nitro and emerging SEV-SNP support, plus NVIDIA confidential GPU attestation. ([GitHub][1])

Crucially, its current API is already moving in exactly the direction we want: `/v1/Attest`, `/v1/GetKey`, `/v1/IssueCert`, GPU evidence and a versioned cross-platform attestation format rather than forcing you to consume raw Intel quotes. ([GitHub][2])

[dstack GitHub](https://github.com/Dstack-TEE/dstack?utm_source=chatgpt.com)
[dstack examples](https://github.com/Dstack-TEE/dstack-examples?utm_source=chatgpt.com)

### Why I wouldn't start with the alternatives

| Stack                             | Moltwork fit | Comment                                                                                                                                                                    |
| --------------------------------- | -----------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **dstack + Phala**                |   **9.5/10** | Agent-friendly, Docker-native, keys + attestations + GPU + multi-provider                                                                                                  |
| Confidential Containers / Trustee |         8/10 | Excellent neutral CNCF infrastructure, but much more Kubernetes/platform engineering than Moltwork needs initially                                                         |
| Marlin Oyster                     |         8/10 | Very interesting crypto-native alternative; includes KMS, attestation and even RISC Zero attestation-verification work, but more infrastructure/operator-market complexity |
| Gramine/SGX                       |         6/10 | Excellent primitive, but considerably lower level                                                                                                                          |
| Raw AWS Nitro                     |         6/10 | Strong hardware/root of trust, but you build much more orchestration and portability yourself                                                                              |

Oyster is worth supporting later. Its open-source monorepo is particularly interesting because it contains a RISC Zero attestation verifier alongside KMS and enclave infrastructure. ([GitHub][3])

The correct architecture is therefore:

```text
                MOLTWORK PROTOCOL
                        │
        ┌───────────────┼────────────────┐
        │               │                │
     Identity         Leases          Work
        │               │                │
        ├──────────── Receipts ──────────┤
        │               │                │
        └──── Reputation / Validation ───┘
                        │
              Moltwork TEE Adapter
                        │
                 dstack Guest API
                        │
        ┌───────────────┼────────────────┐
        │               │                │
   Phala Cloud       GCP TDX          AWS Nitro
                                         │
                              later: bare metal/SNP
```

That boundary is extremely important. **Never make `phalaDeploymentId` a fundamental Moltwork identity.**

---

# The cryptographic layer Moltwork should own

I'd call the package something boring like **`moltwork-evidence`** rather than marketing it as another blockchain.

There are seven actual primitives worth building.

## 1. Attested Workload Identity

An agent has two identities:

**Economic identity**

```text
Agent
├─ ERC-8004 agentId
├─ owner
├─ profile
├─ reputation
└─ payment addresses
```

**Execution identity**

```text
Workload
├─ source commit
├─ container digest
├─ compose/config hash
├─ WorkerKit version
├─ policy hash
├─ TEE measurement
└─ attested signing key
```

Don't conflate them.

Agent `#413` can upgrade from WorkerKit 0.4 → 0.5 while retaining its marketplace identity, but users can see exactly which workload produced each result.

Create a canonical:

```text
WorkloadManifestV1
{
    agent_id
    source_repository
    source_commit
    image_digests[]
    workerkit_version
    config_hash
    skills_hash
    policy_hash
    model_policy_hash
}
```

Then:

```text
workload_id = hash(canonical(WorkloadManifestV1))
```

dstack already measures the application compose configuration into its attestation and requires SHA-256-pinned container images, so we're extending rather than duplicating its root of trust. ([GitHub][4])

---

# 2. Attested Agent Keys

This is where dstack gets especially useful.

It can deterministically derive a private key bound to the application's identity, and return a signature chain proving that key was derived through its TEE-backed KMS. ([GitHub][5])

Define explicit key domains:

```text
/moltwork/v1/agent/evm
/moltwork/v1/receipts
/moltwork/v1/checkpoints
/moltwork/v1/oracle
```

Never use one key for everything.

For ETHOnline I'd use **secp256k1** for the main protocol signatures because Ethereum verifies it cheaply.

The important relationship becomes:

```text
Agent #413
    ↓ owns/authorizes
Workload 0xabc...
    ↓ attestation proves
TEE execution
    ↓ controls
0xTEE_SIGNER
```

Now an agent signature means:

> this message was produced by the private key belonging to this measured workload.

That's materially stronger than:

> some server with the agent's API key signed this.

---

# 3. Fresh attestation + confidential job delivery

This should be a first-class Moltwork handshake.

Client generates:

```text
nonce = random(32 bytes)
```

Worker generates an ephemeral encryption key:

```text
K_session
```

Then bind the job session to the TEE:

```text
report_data =
    SHA256(
        "moltwork-attestation-v1" ||
        nonce ||
        session_public_key ||
        workload_id
    )
```

Call:

```text
dstack.Attest(report_data)
```

The verifier checks:

```text
hardware signature
TCB status
boot measurements
OS measurements
compose hash
container digests
KMS binding
fresh nonce
workload_id binding
GPU evidence if required
```

dstack's security model already exposes the hardware → boot → OS → application → KMS chain, while the caller-controlled `report_data` provides the freshness/challenge binding we need. ([GitHub][4])

Only **after** verification does the client encrypt its private job payload to `K_session`.

So Moltwork can legitimately offer:

> Send secrets to an agent without the Moltwork operator, machine administrator or compute host being able to read them.

That's much more compelling than just a little green “TEE verified” badge.

---

# 4. Work Commitments

Before the agent works, both sides need an immutable definition of *what the job actually was*.

Define an EIP-712 structure:

```text
WorkOrderV1 {
    jobId
    buyer
    agentId

    specificationHash
    inputCommitment
    artifactPolicyHash

    rewardAsset
    rewardAmount
    maxExecutionCost

    deadline
    requiredTrustPolicy

    nonce
}
```

Buyer signs it.

Agent signs:

```text
WorkAcceptanceV1 {
    workOrderHash
    workloadId
    executionKey
    acceptedAt
}
```

EIP-712 is exactly the right primitive here because it gives structured, domain-separated Ethereum signatures rather than signing arbitrary byte strings. ([Ethereum Improvement Proposals][6])

Now disputes aren't:

> “that's not what I asked it to do.”

They're:

```text
WorkOrder hash = 0xc83...
Receipt workOrderHash = 0xc83...
```

---

# 5. **Agent Leases**

This is potentially one of Moltwork's strongest primitives.

Don't define “leasing an agent” as giving somebody its private key.

Define it as **leasing cryptographically restricted authority**.

```text
AgentLeaseV1 {
    leaseId

    principal
    agentId
    delegate

    validAfter
    validUntil

    allowedChains
    allowedTargets
    allowedSelectors

    maxTotalSpend
    maxTransactionSpend

    allowedJobTypesHash
    policyHash

    nonce
    revocationEpoch
}
```

`delegate` is the **attested TEE execution signer**.

The owner signs the lease.

Then the worker can autonomously act within exactly those limits.

### Example

You could issue:

```text
Agent: Moltwork Research Worker #21

Valid:
29 Aug → 5 Sep

May:
✓ buy x402 endpoints
✓ spend ≤ $10 total
✓ spend ≤ $0.25/request
✓ submit jobs
✓ collect bounty payments

May not:
✗ transfer arbitrary wallet funds
✗ call unknown contracts
✗ change its owner
✗ create another delegation
```

The beautiful part is that **the restrictions must be enforced by the account/contract**, not merely trusted to WorkerKit.

Initially build:

```text
AgentVault.sol
```

with:

```text
executeWithLease(...)
revokeLease(...)
incrementLeaseEpoch(...)
remainingAllowance(...)
isLeaseValid(...)
```

Later turn the execution layer into an ERC-7579 smart-account module.

Ethereum's emerging delegation standards already give us interoperability targets. ERC-7710 defines delegation as authority granted to another address for specific actions, while ERC-7715 standardizes requesting scoped wallet execution permissions with restrictions such as expiry and allowances. ([Ethereum Improvement Proposals][7])

So Moltwork should create a **higher-level AgentLease schema that can compile into ERC-7710/7715 permissions**.

That is much better than inventing a competing wallet standard.

---

# 6. Verifiable Run Receipts

This is the centerpiece.

Every WorkerKit execution should end with:

```text
RunReceiptV1 {
    runId
    agentId

    workOrderHash
    workloadId
    leaseHash

    inputCommitment
    outputCommitment

    artifactRoot
    traceRoot

    modelPolicyHash
    toolPolicyHash

    startedAt
    completedAt

    tokensUsed
    executionCost

    paymentReference

    attestationHash

    status
}
```

TEE key signs the receipt.

Therefore:

```text
             WORK ORDER
                 │
                 ▼
        ┌─────────────────┐
        │ Attested Worker │
        │      TEE        │
        └─────────────────┘
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
    models     tools     APIs
       │         │         │
       └─────────┼─────────┘
                 ▼
              output
                 │
                 ▼
          RUN RECEIPT
                 │
             TEE SIGN
                 │
                 ▼
       independently verifiable
```

This connects directly to WorkerKit's economic telemetry.

Instead of merely saying:

> “We think this job cost roughly $0.09.”

you get:

```text
job reward        $1.00
model spend       $0.041
API spend         $0.012
x402 spend        $0.006
total run cost    $0.059
gross margin      $0.941
```

signed into the run's provenance.

---

# 7. Trace commitments

Do **not** publish the full chain-of-thought or every private payload.

Instead every material event gets a record:

```text
TraceEvent {
    sequence
    type
    requestHash
    responseHash
    provider
    cost
    timestamp
}
```

Build a Merkle tree:

```text
traceRoot = MerkleRoot(traceEvents)
```

The receipt contains only:

```text
traceRoot
```

Later, if someone disputes one event, WorkerKit can selectively reveal:

```text
event
+
Merkle proof
```

without revealing the entire private execution.

This also becomes extremely useful for proving which oracle snapshot the worker saw, which API it bought, which model produced an intermediate artifact, etc.

---

# Transparency log instead of putting everything onchain

Do **not** shove every receipt onto Ethereum.

Maintain an append-only Moltwork evidence log:

```text
receipt
receipt
receipt
receipt
   ↓
Merkle tree
   ↓
CheckpointV1 {
    epoch
    root
    receiptCount
    previousRoot
}
   ↓
Ethereum
```

Anchor a root periodically.

You get:

* cheap execution;
* permanent tamper evidence;
* inclusion proofs;
* receipt privacy;
* public marketplace verification.

This is enough cryptography. No Moltwork blockchain required.

---

# ERC-8004 fits Moltwork unusually well

This is worth adopting aggressively, but **as an adapter rather than making our internal architecture depend on a draft ERC**.

ERC-8004 defines:

1. **Identity Registry**
2. **Reputation Registry**
3. **Validation Registry**

and explicitly calls out **TEE attestations**, zkML and re-execution as interchangeable validation mechanisms. It also explicitly treats payments such as x402 as orthogonal. ([Ethereum Improvement Proposals][8])

That's practically Moltwork's architecture.

[ERC-8004 specification](https://eips.ethereum.org/EIPS/eip-8004?utm_source=chatgpt.com)

So:

```text
Moltwork agent
      │
      ├── ERC-8004 Identity
      │
      ├── x402 payment endpoint
      │
      ├── TEE Workload Identity
      │
      ├── Work Receipts
      │
      └── ERC-8004 Validation
              │
              └── RunReceipt evidence
```

A marketplace review can then be:

```text
★★★★★ 0.93

17 paid jobs
15 cryptographically verified runs
14 buyer-confirmed successes
1 disputed
0 unverifiable
```

rather than meaningless star ratings.

---

# The trust ladder

TEE should **not** equal “this answer is true.”

A TEE proves that a particular measured workload ran under the claimed environment. Bad code can still run securely and produce rubbish.

So Moltwork should expose levels:

| Level             | Meaning                                       |
| ----------------- | --------------------------------------------- |
| `SIGNED`          | Agent key signed the result                   |
| `ATTESTED`        | Key + code identity are TEE-attested          |
| `TRACE_COMMITTED` | Inputs/output/tool activity committed         |
| `REPRODUCED`      | Independent worker reproduced result          |
| `VALIDATED`       | Domain-specific validator accepted output     |
| `ZK_VERIFIED`     | Particular deterministic claim has a ZK proof |

That makes the system intellectually honest.

And it gives Lagrange/RISC Zero/etc. a natural place **later**, without pretending zkML is necessary for every agent call.

---

# What I would actually put in the repo

```text
moltwork/
│
├── packages/
│   ├── evidence/
│   │   ├── workload.ts
│   │   ├── work-order.ts
│   │   ├── receipt.ts
│   │   ├── trace.ts
│   │   └── checkpoint.ts
│   │
│   ├── tee/
│   │   ├── interface.ts
│   │   ├── dstack.ts
│   │   └── verifier.ts
│   │
│   ├── leases/
│   │   ├── schema.ts
│   │   ├── signer.ts
│   │   └── policy.ts
│   │
│   └── erc8004/
│       └── adapter.ts
│
├── contracts/
│   ├── AgentVault.sol
│   ├── LeaseVerifier.sol
│   ├── EvidenceAnchor.sol
│   └── ERC8004Validator.sol
│
├── services/
│   └── verifier/
│
└── workerkit/
    └── evidence/
```

And give every deployment:

```text
GET /.well-known/moltwork.json
GET /v1/attestation
GET /v1/workload
GET /v1/receipts/:id
POST /v1/jobs
POST /v1/jobs/:id/verify
```

---

# Build order

For the hackathon, I would be ruthless:

**Phase A — TEE foundation**

```text
WorkerKit container
→ dstack
→ Phala TDX
→ derive signing key
→ generate fresh attestation
→ independently verify it
```

**Phase B — Moltwork evidence**

```text
WorkloadManifest
WorkOrder
RunReceipt
EIP-712 signatures
traceRoot
```

**Phase C — killer demo**

User submits private job:

```text
verify TEE
→ encrypt job to attested worker
→ worker runs
→ worker buys/API-calls something
→ produces artifact
→ returns signed receipt
→ verifier says VALID
```

**Phase D — Agent Lease**

```text
give agent $1 spending authority
→ enforce max budget cryptographically
→ worker autonomously purchases x402 resource
→ receipt proves what happened
```

**Phase E — ERC-8004**

Register agent and make the verified receipt usable as an ERC-8004 validation/reputation artifact.

**Phase F — marketplace**

Now the Moltwork board isn't merely a UI for jobs.

It becomes a market for:

> **agents whose identity, authority, execution history, costs and outputs can be cryptographically inspected.**

---

## This is the architecture I'd commit to

The core Moltwork cryptographic stack should therefore be:

```text
ERC-8004                 discovery / reputation
     │
Moltwork Agent Identity
     │
Moltwork Workload Identity
     │
dstack Attestation ───── hardware provenance
     │
Attested Agent Key
     │
AgentLease ───────────── delegated authority
     │
WorkOrder ────────────── intent commitment
     │
WorkerKit execution
     │
Trace Merkle Root
     │
RunReceipt ───────────── execution provenance
     │
Evidence Log
     │
Ethereum root anchor
```

**Phala/dstack handles “prove what machine/code holds this key.”**

**Moltwork handles “what was this agent authorized to do, what work did it agree to perform, what actually happened, what did it cost, and can I trust its history?”**

That second layer is the actual Moltwork protocol, and it's meaningfully different from Virtuals or simply deploying an agent inside a TEE. The most distinctive primitive in it is probably **`AgentLease + WorkOrder + Attested RunReceipt`**. I would build those three before touching more marketplace UI. ([Ethereum Improvement Proposals][8])

[1]: https://github.com/dstack-TEE/dstack?utm_source=chatgpt.com "GitHub - Dstack-TEE/dstack: Open framework for confidential AI · GitHub"
[2]: https://github.com/Dstack-TEE/dstack/blob/next/sdk/curl/api.md?utm_source=chatgpt.com "dstack/sdk/curl/api.md at next · Dstack-TEE/dstack · GitHub"
[3]: https://github.com/marlinprotocol/oyster-monorepo?utm_source=chatgpt.com "GitHub - marlinprotocol/oyster-monorepo: Monorepo for the Oyster project · GitHub"
[4]: https://github.com/Phala-Network/dstack-cloud/blob/master/docs/security/security-model.md?utm_source=chatgpt.com "dstack-cloud/docs/security/security-model.md at master · Phala-Network/dstack-cloud · GitHub"
[5]: https://github.com/Dstack-TEE/dstack/blob/master/sdk/python/README.md?utm_source=chatgpt.com "dstack/sdk/python/README.md at master · Dstack-TEE/dstack · GitHub"
[6]: https://eips.ethereum.org/EIPS/eip-712?utm_source=chatgpt.com "EIP-712: Typed structured data hashing and signing"
[7]: https://eips.ethereum.org/EIPS/eip-7710?utm_source=chatgpt.com "ERC-7710: Smart Contract Delegation"
[8]: https://eips.ethereum.org/EIPS/eip-8004?utm_source=chatgpt.com "ERC-8004: Trustless Agents"

Yes. I found several things that materially change the Moltwork cryptographic design. The strongest result is that we should **stop thinking of this as “add Phala attestations to WorkerKit”** and instead assemble an existing chain of standards into something much harder:

```text
Git commit
   ↓
SLSA / in-toto provenance
   ↓
Cosign-signed container
   ↓
dstack AppAuth approves workload
   ↓
TEE KMS releases agent identity key
   ↓
fresh workload attestation
   ↓
ERC-7710 scoped delegation
   ↓
committed execution plan
   ↓
tool / inference / HTTP / payment evidence
   ↓
Moltwork Job Receipt
   ↓
ERC-8004 validation + reputation
```

The **novel Moltwork layer is the composition**, especially turning all of those artifacts into a single verifiable work record.

## 1. The biggest thing to steal: dstack's ACI protocol

This was the best discovery.

dstack now has an open-source **Private AI Gateway** implementing a draft protocol called **Attested Confidential Inference (ACI)**. It is OpenAI-compatible, but every request can have a cryptographic evidence trail. It publishes workload attestation, verifies the confidential inference provider before sending the prompt, and signs request receipts. ([GitHub][1])

Their verifier can check something roughly like:

```text
fresh nonce
   ↓
gateway TEE attestation
   ↓
workload keyset digest
   ↓
provider verification event
   ↓
request hash
   ↓
response hash
   ↓
signed receipt
```

This is almost exactly the **inner loop** we wanted for Moltwork.

So I would **not invent `InferenceReceiptV1`**.

Instead:

```text
MoltworkJobReceipt
├── WorkOrder
├── Lease
├── workloadAttestation
│
├── events[]
│   ├── ACI inference receipt
│   ├── ACI inference receipt
│   ├── HTTP evidence
│   ├── x402 settlement
│   ├── tool invocation
│   └── artifact production
│
└── eventMerkleRoot
```

ACI becomes the standard proof format for an individual inference. Moltwork defines the proof format for an **entire economically useful agent run**.

The ACI gateway already supports multiple upstreams including Tinfoil, NEAR AI, Chutes, SecretAI, PhalaDirect and generic OpenAI-compatible services. That gives WorkerKit a very attractive inference abstraction rather than wiring Phala inference directly. ([GitHub][2])

This is extremely high-priority.

---

# 2. Use dstack's KMS authorization much harder

The more interesting dstack feature isn't actually quote generation.

It's **conditional key release**.

dstack's KMS runs in its own TEE, verifies workloads before releasing deterministic application keys, and can enforce authorization using smart contracts. Their deployment stack has `auth-eth`, while `DstackKms` / `DstackApp` govern things such as acceptable OS images, application registrations and compose hashes. ([GitHub][3])

This means Moltwork can make this guarantee:

```text
agent private key
       │
       X  operator cannot obtain it
       │
       X  modified WorkerKit cannot obtain it
       │
       X  unapproved container cannot obtain it
       │
       ▼
ONLY approved measured Moltwork workload
```

That is much more powerful than:

> Here's an attestation saying WorkerKit is currently running.

We can make identity itself inaccessible to unapproved code.

### Moltwork upgrade governance

Imagine:

```text
Agent #842
    │
    └── permitted workloads
          ├── WorkerKit 0.7.2 hash
          └── WorkerKit 0.7.3 hash
```

An upgrade PR builds a container.

The container provenance is checked.

Its digest gets approved.

Only then can dstack KMS release:

```text
/moltwork/agents/842/signing
/moltwork/agents/842/wallet
/moltwork/agents/842/receipt
```

to that workload.

An operator pushing:

```text
evil-workerkit:latest
```

gets **no agent key**.

dstack's examples already include an upgrades tutorial built around extending `AppAuth.sol` with custom authorization logic. ([GitHub][4])

This should absolutely become part of Moltwork.

---

# 3. Close the massive TEE supply-chain hole with Sigstore + SLSA + in-toto

This is probably the most important thing missing from our earlier design.

TEE attestation proves:

> image `sha256:ABC` is running.

It doesn't inherently prove:

> image `sha256:ABC` was produced from Git commit `1234` using the reviewed WorkerKit source.

Use existing software supply-chain standards rather than inventing this.

**SLSA provenance** records where/how software was produced and is itself expressed as an in-toto attestation predicate. ([GitHub][5])

**in-toto** gives a generic authenticated statement format:

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{
    "name": "workerkit",
    "digest": {
      "sha256": "..."
    }
  }],
  "predicateType": "...",
  "predicate": {}
}
```

([GitHub][6])

And **Sigstore/Cosign** lets CI sign the resulting container using a short-lived key associated with the GitHub Actions/OIDC build identity, with the signing event witnessed in Rekor's append-only transparency log. ([Sigstore][7])

So Moltwork verification becomes:

```text
GitHub repo
commit 93a28...
     │
     ▼
GitHub Actions
     │
     ├─ tests
     ├─ build
     ├─ SLSA provenance
     └─ Cosign signature
             │
             ▼
       image sha256:ABC
             │
             ▼
      dstack measurement
             │
             ▼
        TEE attestation
```

Now we can actually say:

> This run came from this publicly auditable source revision.

That's an enormous credibility improvement.

And importantly, **don't build another transparency log for build artifacts**. Rekor already exists. Moltwork's own Merkle log should contain *work receipts*, which is a different thing.

---

# 4. AgentLease should compile to ERC-7710, not be its own wallet

This changes my earlier recommendation.

I would probably **delete most of `AgentVault.sol`**.

MetaMask's open-source Delegation Framework is almost absurdly aligned with our lease primitive. It's built around ERC-7710 and lets an account issue an off-chain delegation to another account while attaching **Caveat Enforcers** controlling what that delegate may do. ([GitHub][8])

Existing caveats already cover things like target restrictions, balance changes, nonces/revocations and payment conditions. They explicitly support re-delegation where restrictions accumulate down the delegation chain. ([GitHub][9])

So:

```text
Moltwork AgentLease
         │
         ▼
   policy compiler
         │
         ▼
ERC-7710 Delegation
         │
    CaveatEnforcers
    ├─ AllowedTargets
    ├─ AllowedMethods
    ├─ SpendingLimit
    ├─ ValidAfter
    ├─ ValidUntil
    ├─ LimitedCalls
    ├─ Nonce
    └─ Moltwork custom caveat
```

Then Moltwork's contribution is **a high-level agent permission language**.

For example:

```yaml
agent: 842
expires: 2026-09-05T00:00:00Z

permissions:
  x402:
    max_total_usd: 5
    max_request_usd: 0.20

  contracts:
    allow:
      - target: 0x...
        methods:
          - claim(...)
          - submit(...)

  jobs:
    categories:
      - research
      - code-review

require:
  tee_workload: 0xabc...
```

Compile that into standard delegations.

This gives Moltwork interoperability instead of a bespoke custody scheme.

One warning: MetaMask explicitly says audited versions are tags and `main` is development, and there are active August 2026 PRs fixing subtle CaveatEnforcer interactions. So use audited releases and write strong integration/fuzz tests rather than copying current `main`. ([GitHub][10])

---

# 5. ERC-8196 is basically someone else circling our AgentLease idea

This one is fascinating.

**ERC-8196: AI Agent Authenticated Wallet** was created March 14, 2026 and describes:

> policy-bound transaction execution and verifiable credential delegation for autonomous AI agents.

It uses EIP-712 policy-bound actions and explicitly proposes a **hash-chained audit trail**. It also proposes entropy commitments to make manipulation of probabilistic agent execution harder. ([Ethereum Improvement Proposals][11])

Even more interesting: one of the authors is from **Virtuals**.

So there is clear convergence happening here.

However, I **wouldn't make Moltwork depend on ERC-8196 yet**.

It mandates ERC-8126 verification/risk scoring, which is considerably more opinionated than what we need. It's also still a draft.

What I would steal is:

```text
policyHash bound into actions
+
hash-chained audit
+
expiration / nonce
+
explicit agent identity
+
entropy commitment where useful
```

Then expose an ERC-8196 compatibility adapter if the standard gains adoption.

So ERC-8196 validates the direction; ERC-7710/7579 gives us the more mature machinery to implement it now.

---

# 6. ERC-8257 means we shouldn't build a proprietary Moltwork tool registry

This is another major find.

**ERC-8257 Agent Tool Registry**, created April 2026, proposes an on-chain permissionless registry for AI agent tools. ([Ethereum Improvement Proposals][12])

It's surprisingly thoughtful.

A tool registration commits:

```text
metadata URI
+
manifest content hash
+
creator
+
endpoint origin
+
pricing hints
+
optional access predicate
```

And the manifest must be served under the tool endpoint's own origin using a `.well-known` path.

This prevents somebody simply registering:

```text
MOLTWORK OFFICIAL SUPER TOOL
→ attacker.example
```

and pretending it's yours.

Most importantly for us, pricing is protocol-independent.

Meaning a tool can essentially advertise:

```text
protocol: x402
token: USDC
chain: Base
price: ...
```

without ERC-8257 itself becoming the payment mechanism.

That's almost perfect.

### Moltwork's role changes

Instead of:

```text
Moltwork owns tool database
```

do:

```text
ERC-8257
canonical tool identity/discovery
        │
        ▼
Moltwork Oracle
availability
performance
cost histories
quality
reputation
successful job usage
        │
        ▼
WorkerKit Router
```

This fits the broader architecture much better.

Moltwork becomes the **intelligence layer over standardized registries**, rather than yet another registry.

---

# 7. Phala already built an ERC-8004 TEE agent. Fork the processes, not the product

Phala's own `erc-8004-tee-agent` repo is effectively a ready-made compatibility test for us.

It already has:

```text
dstack / Intel TDX
TEE-derived keys
ERC-8004 identity
ERC-8004 reputation
agent registration metadata
A2A agent card
tool calling
signatures
attestation endpoint
```

([GitHub][13])

That repo's structure is worth absorbing directly:

```text
src/agent/
├── base.py
├── chat_agent.py
├── code_executor.py
├── registry.py
├── tee_auth.py
├── agent_card.py
└── chain_config.py
```

And it exposes:

```text
GET /agent.json
GET /.well-known/agent-card.json
GET /.well-known/agent-registration.json
GET /api/tee/attestation
```

We should make **a Moltwork WorkerKit instance pass the same interoperability flow**.

But don't clone their product. They've essentially demonstrated:

> agent + TEE + 8004.

Our interesting addition is:

> agent + TEE + 8004 + delegation + economic execution + evidence graph + verified work history.

That's materially deeper.

---

# 8. Steal PlanBound's spending process almost wholesale

This was the best ETHGlobal project I found for **process design**.

PlanBound's key idea is that an agent doesn't ask:

> Can I spend $5?

It first shops around and creates:

```text
ExecutionPlan
├── step A
│   ├── provider
│   ├── live quote
│   └── $0.03
├── step B
│   ├── provider
│   ├── live quote
│   └── $0.07
└── total ceiling $0.10
```

Only *then* does the person approve it.

Crucially, they distinguish a **real 402 quote** from an estimated price, and they re-check the quote immediately before purchasing. If reality differs from the approved plan, execution stops even if the wallet technically contains enough funds. ([ETHGlobal][14])

That should go straight into WorkerKit.

Our earlier:

```text
projected cost → run → actual cost
```

becomes:

```text
DISCOVER
    ↓
QUOTE
    ↓
PLAN
    ↓
COMMIT
    ↓
AUTHORIZE
    ↓
EXECUTE
    ↓
RE-QUOTE EACH PURCHASE
    ↓
STOP ON PLAN DRIFT
    ↓
RECEIPT
```

And this detail is excellent:

> their approval UI is rendered by their trusted server, not by the agent, because an agent that controls the approval description can manipulate what the person thinks they're approving. ([ETHGlobal][14])

That's a genuinely good security boundary.

Their code is MIT licensed and unusually well documented, including exact files implementing x402 discovery, live quoting, the spending gate, settlement reconciliation and MCP/OAuth. ([GitHub][15])

I would study this repo closely.

---

# 9. Clawback has a fantastic `WorkOrder` trick

Another ETHGlobal project, Clawback, has a clever architecture for x402 delivery.

They use an **EIP-3009 authorization nonce as the deal ID**.

That same signed authorization commits:

```text
buyer
seller
amount
dispute window
spec hash
validity
salt
```

So one signature:

```text
authorizes money
+
identifies job
+
commits job terms
```

Then the x402 settlement hook hashes the **actual response body** returned by the seller and records that as the delivered artifact. ([ETHGlobal][16])

That is excellent.

Moltwork could generalize:

```text
WorkOrderHash
      │
      ├── payment authorization
      ├── agent lease
      ├── input commitment
      └── receipt
```

Everything references one job identity.

Clawback also separates:

```text
ephemeral agent reputation
        +
persistent principal reputation
```

so somebody can't wipe all their economic history simply by rotating an agent key. ([ETHGlobal][16])

That's another pattern I'd take.

I wouldn't put escrow on every Moltwork interaction because it destroys the cheap/simple flow. But for high-value/untrusted work:

```text
DIRECT
SIGNED
ATTESTED
ESCROWED
ESCROWED + VALIDATED
```

can become increasing trust modes.

---

# 10. Preflight contains the missing "capability drift" primitive

This may be the most useful hackathon idea for the marketplace.

Preflight hashes an agent's **live MCP tool surface** when it evaluates it.

Then when someone later tries to hire that agent, it checks the surface *again*.

If:

```text
evaluated tools hash
!=
current tools hash
```

it refuses.

That's important because an agent could earn a great reputation running:

```text
tools:
  github_read
  web_search
```

and then silently add:

```text
arbitrary_wallet_execution
```

after being reviewed.

Preflight calls this a capability fingerprint and explicitly fails closed when the current tool surface no longer matches what was graded. ([GitHub][17])

Put this in Moltwork:

```text
WorkloadManifest
├── imageDigest
├── composeHash
├── sourceCommit
├── modelPolicyHash
├── MCPManifestHash
├── skillSetHash
└── capabilityHash
```

Now reputation attaches not just to:

```text
Agent 842
```

but effectively:

```text
Agent 842
running capability version 0xABC
```

A capability change doesn't necessarily delete its old reputation, but it makes the change visible and can trigger revalidation.

Preflight also signs and hash-chains its decision receipts, and records evidence separately from its verdict. ([GitHub][17])

Very useful design.

---

# 11. Use zkTLS selectively for the Oracle

This is where the Oracle gets properly cryptographic.

TEE attestation proves:

> WorkerKit says it received "$173.42".

It doesn't independently prove:

> api.example actually returned "$173.42".

For important HTTP-derived evidence, use **zkTLS / MPC-TLS**.

TLSNotary lets a prover make a real TLS request while cooperating cryptographically with a verifier, then selectively reveal authenticated portions of the returned response. The prover cannot independently forge the server response. ([tlsnotary.org][18])

So:

```text
Moltwork Oracle
      │
      ▼
 HTTPS source
      │
      ▼
 TLSNotary proof
      │
      ▼
 SourceEvidence
      │
      ▼
 Worker reasoning
      │
      ▼
 RunReceipt
```

That's a huge difference from an ordinary oracle.

For quick implementation, **Reclaim's `zk-fetch`** is more plug-and-play: it wraps a fetch and returns a third-party-verifiable proof, supports private credentials and selective response disclosure. ([GitHub][19])

I'd make this optional because proving every web request would be stupidly expensive/slow.

Something like:

```text
evidence_mode:

NONE
HASHED
TEE
TLS_PROVEN
MULTI_SOURCE
```

WorkerKit chooses stronger evidence for higher-value claims.

TLSNotary itself explicitly warns it's still under active development, so I wouldn't make it an availability-critical dependency yet. ([GitHub][20])

---

# 12. ERC-8033 gives us the validation process for difficult work

We don't need to adopt the whole contract.

Steal the protocol flow.

ERC-8033 defines separate:

```text
Info Agents
vs
Judge Agents
```

with:

```text
request
→ commit
→ reveal
→ judge
→ aggregate
→ result
```

and optional bonds, disputes and higher-trust adjudication. ([Ethereum Improvement Proposals][21])

Commit/reveal matters because if five agents submit answers publicly one after another, agents two through five can simply copy agent one.

So Moltwork evaluation can become:

```text
job
 │
 ├─ worker A → H(outputA || saltA)
 ├─ worker B → H(outputB || saltB)
 └─ worker C → H(outputC || saltC)

submission window closes

A reveals
B reveals
C reveals

       ↓

independent JudgeAgent

       ↓

ValidationReceipt
```

This fits the Oracle and later marketplace peer-review system extremely well.

It is much more robust than:

> ask another LLM whether the first LLM did a good job.

---

# 13. ERC-7857 is potentially wild for the eventual marketplace

Not now.

But remember this one.

ERC-7857 is explicitly for AI agents with **private metadata** and supports verifiable transfer/cloning of encrypted agent information, with verifier abstractions that can use TEEs or ZKPs. ([Ethereum Improvement Proposals][22])

Imagine Moltwork later sells:

```text
Winning Upwork Research Agent
```

but its valuable assets are private:

```text
memory
recipes
evaluation history
fine-tune
private prompts
workflow DAGs
customer knowledge
```

You don't want buying it to mean:

> download this plaintext JSON and copy it forever.

ERC-7857 points toward:

```text
encrypted agent asset
       ↓
ownership / usage authorization
       ↓
sealed TEE executor
       ↓
buyer can USE capability
without receiving raw internals
```

That's much closer to genuine agent IP licensing.

It's endgame material, but it fits the marketplace surprisingly well.

---

# The architecture I'd now implement

I'd revise our previous cryptographic architecture to this:

```text
                 MOLTWORK AGENT
                       │
                ERC-8004 identity
                       │
                       ▼
              SOURCE PROVENANCE
       Git commit → SLSA → in-toto
                       │
                    Cosign
                       │
                       ▼
             WORKLOAD IDENTITY
              container digest
              capability hash
              compose hash
                       │
                       ▼
              DSTACK APP AUTH
                       │
             approved workload?
                 YES / NO
                       │
                      YES
                       ▼
                DSTACK KMS
              releases TEE keys
                       │
                       ▼
                  ATTESTATION
                       │
             ACI workload keyset
                       │
                       ▼
                 AGENT LEASE
              ERC-7710 delegation
                  + caveats
                       │
                       ▼
                EXECUTION PLAN
          PlanBound-style live quotes
             + WorkOrder commitment
                       │
                       ▼
                 WORKERKIT RUN
                       │
       ┌───────────────┼─────────────────┐
       │               │                 │
      LLM            HTTP              tools
       │               │                 │
   ACI receipt     zkTLS proof      ERC-8257 ID
       │               │                 │
       └───────────────┼─────────────────┘
                       │
                    x402
                       │
               settlement proof
                       │
                       ▼
                EVENT MERKLE TREE
                       │
                       ▼
              MOLTWORK JOB RECEIPT
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
  ERC-8004 Validation            Evidence log
       │                               │
       ▼                               ▼
  Reputation                    periodic root
                                     │
                                     ▼
                                  Ethereum
```

That is starting to look like a **real protocol**, rather than a hackathon collection of crypto components.

## What I would actually adopt vs merely study

| Primitive/project                            | Decision                  | What Moltwork gets                     |
| -------------------------------------------- | ------------------------- | -------------------------------------- |
| **dstack**                                   | **CORE**                  | TEE workload identity + KMS            |
| **dstack ACI**                               | **CORE**                  | inference receipts                     |
| **dstack AppAuth/auth-eth**                  | **CORE**                  | code-governed secret/key release       |
| **ERC-8004**                                 | **CORE interface**        | agent identity/reputation/validation   |
| **ERC-7710 + MetaMask Delegation Framework** | **CORE**                  | AgentLease enforcement                 |
| **ERC-8257**                                 | **CORE interoperability** | tool discovery/identity                |
| **SLSA + in-toto + Sigstore**                | **CORE**                  | source→binary provenance               |
| **PlanBound patterns**                       | **COPY PROCESS**          | plan→approve→execute budget discipline |
| **Preflight patterns**                       | **COPY PROCESS**          | capability fingerprint + revalidation  |
| **Clawback patterns**                        | **COPY PROCESS**          | deal commitment + delivery hashes      |
| **TLSNotary / zkFetch**                      | **OPTIONAL evidence**     | external web-data provenance           |
| **ERC-8033 patterns**                        | **VALIDATION**            | commit/reveal + independent judges     |
| **ERC-8196**                                 | **WATCH / adapter**       | emerging agent-wallet compatibility    |
| **ERC-7857**                                 | **LATER**                 | private agent IP/licensing             |
| zkVM everything                              | **NOT NOW**               | complexity without enough benefit      |

There's one more Phala/dstack trick I would absolutely exploit: their examples already run **Helios, an Ethereum light client, inside the enclave**. ([GitHub][4])

That means eventually WorkerKit doesn't even need to trust its RPC provider when checking:

```text
Was my lease revoked?
Was this job funded?
Did this x402 payment settle?
Is this workload version authorized?
```

It can verify Ethereum state **from inside the TEE**.

That completes a rather beautiful chain:

```text
don't trust host
don't trust RPC
don't trust model provider
don't trust claimed source image
don't trust agent's own logs
don't trust marketplace star rating

verify each boundary differently.
```

That is the direction I would take Moltwork now. **Phala/dstack is the execution root; Ethereum standards are the authority/identity layer; Sigstore/in-toto is the software provenance layer; ACI/zkTLS/x402 are evidence producers; Moltwork is the protocol that binds all of them into a verifiable economic work receipt.**

And that is sufficiently different from “Virtuals but with a TEE” to be genuinely interesting.

[1]: https://github.com/Dstack-TEE/private-ai-gateway?utm_source=chatgpt.com "GitHub - Dstack-TEE/private-ai-gateway: Private AI Gateway for Attested Confidential Inference · GitHub"
[2]: https://github.com/Dstack-TEE/private-ai-gateway/blob/main/README.md?utm_source=chatgpt.com "private-ai-gateway/README.md at main · Dstack-TEE/private-ai-gateway · GitHub"
[3]: https://github.com/dstack-TEE/dstack?utm_source=chatgpt.com "GitHub - Dstack-TEE/dstack: Open framework for confidential AI · GitHub"
[4]: https://github.com/dstack-tee/dstack-examples?utm_source=chatgpt.com "GitHub - Dstack-TEE/dstack-examples: examples and utilities of dstack applications · GitHub"
[5]: https://github.com/slsa-framework/slsa/blob/main/spec/build-provenance.md?utm_source=chatgpt.com "slsa/spec/build-provenance.md at main · slsa-framework/slsa · GitHub"
[6]: https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md?utm_source=chatgpt.com "attestation/spec/v1/statement.md at main · in-toto/attestation · GitHub"
[7]: https://docs.sigstore.dev/cosign/signing/overview/?utm_source=chatgpt.com "Overview - Sigstore"
[8]: https://github.com/MetaMask/delegation-framework/blob/main/documents/DelegationManager.md?utm_source=chatgpt.com "delegation-framework/documents/DelegationManager.md at main · MetaMask/delegation-framework · GitHub"
[9]: https://github.com/MetaMask/delegation-framework/blob/main/documents/CaveatEnforcers.md?utm_source=chatgpt.com "delegation-framework/documents/CaveatEnforcers.md at main · MetaMask/delegation-framework · GitHub"
[10]: https://github.com/MetaMask/delegation-framework?utm_source=chatgpt.com "GitHub - MetaMask/delegation-framework: The contracts that power the Delegation Framework · GitHub"
[11]: https://eips.ethereum.org/EIPS/eip-8196?utm_source=chatgpt.com "ERC-8196: AI Agent Authenticated Wallet"
[12]: https://eips.ethereum.org/EIPS/eip-8257?utm_source=chatgpt.com "ERC-8257: Agent Tool Registry"
[13]: https://github.com/Phala-Network/erc-8004-tee-agent "GitHub - Phala-Network/erc-8004-tee-agent: An ERC-8004 Compliant TEE Agent with a TEE Registry Extension for Secure & Verifiable Trustless Agents in a CVM on Phala Cloud · GitHub"
[14]: https://ethglobal.com/showcase/planbound-wqxy5 "PlanBound | ETHGlobal"
[15]: https://github.com/idoamram/planbound "GitHub - idoamram/planbound · GitHub"
[16]: https://ethglobal.com/showcase/clawback-vpmw2 "ethglobal.com"
[17]: https://github.com/RubenSousaDinis/preflight "GitHub - RubenSousaDinis/preflight · GitHub"
[18]: https://tlsnotary.org/docs/intro/?utm_source=chatgpt.com "Introduction | TLSNotary"
[19]: https://github.com/reclaimprotocol/zk-fetch?utm_source=chatgpt.com "GitHub - reclaimprotocol/zk-fetch · GitHub"
[20]: https://github.com/tlsnotary/tlsn?utm_source=chatgpt.com "GitHub - tlsnotary/tlsn: Rust implementation of the TLSNotary protocol · GitHub"
[21]: https://eips.ethereum.org/EIPS/eip-8033?utm_source=chatgpt.com "ERC-8033: Agent Council Oracles"
[22]: https://eips.ethereum.org/EIPS/eip-7857?utm_source=chatgpt.com "ERC-7857: AI Agents NFT with Private Metadata"

