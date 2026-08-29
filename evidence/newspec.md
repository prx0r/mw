# Moltwork Cryptographic Protocol — Refined Specification
**Date:** 2026-08-29
**Status:** Architecture frozen, build from this

## Core Architecture Chain

```
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

The novel Moltwork layer is the composition, especially turning all of those artifacts into a single verifiable work record.

---

## 1. dstack ACI — Attested Confidential Inference (CORE)

dstack now has an open-source Private AI Gateway implementing a draft protocol called Attested Confidential Inference (ACI). It is OpenAI-compatible, but every request can have a cryptographic evidence trail. It publishes workload attestation, verifies the confidential inference provider before sending the prompt, and signs request receipts.

Their verifier can check:
```
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

This is almost exactly the inner loop we wanted for Moltwork.

So I would NOT invent InferenceReceiptV1. Instead:

```
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

ACI becomes the standard proof format for an individual inference. Moltwork defines the proof format for an entire economically useful agent run.

The ACI gateway already supports multiple upstreams including Tinfoil, NEAR AI, Chutes, SecretAI, PhalaDirect and generic OpenAI-compatible services. That gives WorkerKit a very attractive inference abstraction rather than wiring Phala inference directly.

This is extremely high-priority.

---

## 2. dstack KMS — Conditional key release (CORE)

The more interesting dstack feature isn't actually quote generation. It's conditional key release.

dstack's KMS runs in its own TEE, verifies workloads before releasing deterministic application keys, and can enforce authorization using smart contracts. Their deployment stack has auth-eth, while DstackKms / DstackApp govern things such as acceptable OS images, application registrations and compose hashes.

This means Moltwork can make this guarantee:
```
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

That is much more powerful than: "Here's an attestation saying WorkerKit is currently running."

We can make identity itself inaccessible to unapproved code.

### Moltwork upgrade governance

```
Agent #842
    │
    └── permitted workloads
          ├── WorkerKit 0.7.2 hash
          └── WorkerKit 0.7.3 hash
```

An upgrade PR builds a container. The container provenance is checked. Its digest gets approved. Only then can dstack KMS release:
```
/moltwork/agents/842/signing
/moltwork/agents/842/wallet
/moltwork/agents/842/receipt
```
to that workload.

An operator pushing `evil-workerkit:latest` gets NO agent key.

dstack's examples already include an upgrades tutorial built around extending AppAuth.sol with custom authorization logic.

---

## 3. SLSA + in-toto + Sigstore — Source provenance (CORE)

TEE attestation proves: image sha256:ABC is running.
It doesn't inherently prove: image sha256:ABC was produced from Git commit 1234 using the reviewed WorkerKit source.

Use existing software supply-chain standards rather than inventing this.

SLSA provenance records where/how software was produced and is itself expressed as an in-toto attestation predicate.

in-toto gives a generic authenticated statement format:
```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{
    "name": "workerkit",
    "digest": {"sha256": "..."}
  }],
  "predicateType": "...",
  "predicate": {}
}
```

Sigstore/Cosign lets CI sign the resulting container using a short-lived key associated with the GitHub Actions/OIDC build identity, with the signing event witnessed in Rekor's append-only transparency log.

So Moltwork verification becomes:
```
GitHub repo
commit 93a28...
     │
     ▼
GitHub Actions
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

Now we can actually say: This run came from this publicly auditable source revision.

Don't build another transparency log for build artifacts. Rekor already exists. Moltwork's own Merkle log should contain work receipts, which is a different thing.

---

## 4. AgentLease → ERC-7710 (CORE)

Delete most of AgentVault.sol.

MetaMask's open-source Delegation Framework is almost absurdly aligned with our lease primitive. It's built around ERC-7710 and lets an account issue an off-chain delegation to another account while attaching Caveat Enforcers controlling what that delegate may do.

Existing caveats already cover things like target restrictions, balance changes, nonces/revocations and payment conditions. They explicitly support re-delegation where restrictions accumulate down the delegation chain.

So:
```
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

Moltwork's contribution is a high-level agent permission language:
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

One warning: MetaMask explicitly says audited versions are tags and main is development, and there are active August 2026 PRs fixing subtle CaveatEnforcer interactions. So use audited releases and write strong integration/fuzz tests.

---

## 5. ERC-8196 — AI Agent Authenticated Wallet (WATCH)

ERC-8196 describes: policy-bound transaction execution and verifiable credential delegation for autonomous AI agents.

It uses EIP-712 policy-bound actions and explicitly proposes a hash-chained audit trail. It also proposes entropy commitments to make manipulation of probabilistic agent execution harder.

One of the authors is from Virtuals. Clear convergence happening.

However, I wouldn't make Moltwork depend on ERC-8196 yet. It mandates ERC-8126 verification/risk scoring, which is considerably more opinionated. Still a draft.

What to steal:
- policyHash bound into actions
- hash-chained audit
- expiration / nonce
- explicit agent identity
- entropy commitment where useful

Then expose an ERC-8196 compatibility adapter if the standard gains adoption.

---

## 6. ERC-8257 — Agent Tool Registry (CORE)

ERC-8257, created April 2026, proposes an on-chain permissionless registry for AI agent tools.

A tool registration commits:
- metadata URI
- manifest content hash
- creator
- endpoint origin
- pricing hints
- optional access predicate

The manifest must be served under the tool endpoint's own origin using a .well-known path. This prevents somebody registering "MOLTWORK OFFICIAL SUPER TOOL" → attacker.example.

Most importantly: pricing is protocol-independent. A tool can advertise:
```
protocol: x402
token: USDC
chain: Base
price: ...
```
without ERC-8257 itself becoming the payment mechanism.

### Moltwork's role changes

Instead of "Moltwork owns tool database", do:
```
ERC-8257 → canonical tool identity/discovery
  → Moltwork Oracle (availability, performance, cost histories, quality, reputation, successful job usage)
  → WorkerKit Router
```

Moltwork becomes the intelligence layer over standardized registries, rather than yet another registry.

---

## 7. Phala erc-8004-tee-agent — Fork processes not product

Phala's own erc-8004-tee-agent repo is effectively a ready-made compatibility test.

It already has:
- dstack / Intel TDX
- TEE-derived keys
- ERC-8004 identity
- ERC-8004 reputation
- agent registration metadata
- A2A agent card
- tool calling
- signatures
- attestation endpoint

Structure:
```
src/agent/
├── base.py
├── chat_agent.py
├── code_executor.py
├── registry.py
├── tee_auth.py
├── agent_card.py
└── chain_config.py
```

Exposes:
```
GET /agent.json
GET /.well-known/agent-card.json
GET /.well-known/agent-registration.json
GET /api/tee/attestation
```

Make a Moltwork WorkerKit instance pass the same interoperability flow.

But don't clone their product. Their addition is: agent + TEE + 8004.
Our addition is: agent + TEE + 8004 + delegation + economic execution + evidence graph + verified work history.

---

## 8. PlanBound patterns — Budget discipline (COPY)

PlanBound's key idea: agent doesn't ask "Can I spend $5?" It shops around and creates:
```
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

Only then does the person approve it.

Distinguish a real 402 quote from an estimated price. Re-check the quote immediately before purchasing. If reality differs from the approved plan, execution stops even if the wallet technically contains enough funds.

Our earlier "projected cost → run → actual cost" becomes:
```
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

Key detail: their approval UI is rendered by their trusted server, not by the agent, because an agent that controls the approval description can manipulate what the person thinks they're approving.

Code is MIT licensed and well documented, including exact files implementing x402 discovery, live quoting, the spending gate, settlement reconciliation and MCP/OAuth.

---

## 9. Clawback patterns — Deal commitment (COPY)

Clawback uses an EIP-3009 authorization nonce as the deal ID.

That same signed authorization commits:
- buyer
- seller
- amount
- dispute window
- spec hash
- validity
- salt

So one signature authorizes money + identifies job + commits job terms.

Then the x402 settlement hook hashes the actual response body returned by the seller and records that as the delivered artifact.

Generalize:
```
WorkOrderHash
      │
      ├── payment authorization
      ├── agent lease
      ├── input commitment
      └── receipt
```

Everything references one job identity.

Clawback also separates:
- ephemeral agent reputation
- persistent principal reputation

so somebody can't wipe all their economic history simply by rotating an agent key.

Trust modes:
```
DIRECT → SIGNED → ATTESTED → ESCROWED → ESCROWED + VALIDATED
```

---

## 10. Preflight patterns — Capability fingerprint (COPY)

Preflight hashes an agent's live MCP tool surface when it evaluates it. Then when someone later tries to hire that agent, it checks the surface again.

If evaluated tools hash != current tools hash → refuse.

This is important because an agent could earn a great reputation running:
```
tools: github_read, web_search
```
and then silently add arbitrary_wallet_execution after being reviewed.

Preflight calls this a capability fingerprint and explicitly fails closed when the current tool surface no longer matches what was graded.

Put this in Moltwork:
```
WorkloadManifest
├── imageDigest
├── composeHash
├── sourceCommit
├── modelPolicyHash
├── MCPManifestHash
├── skillSetHash
└── capabilityHash
```

Now reputation attaches not just to Agent 842 but effectively to Agent 842 running capability version 0xABC.

A capability change doesn't necessarily delete its old reputation, but it makes the change visible and can trigger revalidation.

Preflight also signs and hash-chains its decision receipts, and records evidence separately from its verdict.

---

## 11. zkTLS — Oracle evidence (OPTIONAL)

TEE attestation proves: WorkerKit says it received "$173.42".
It doesn't independently prove: api.example actually returned "$173.42".

For important HTTP-derived evidence, use zkTLS / MPC-TLS.

TLSNotary lets a prover make a real TLS request while cooperating cryptographically with a verifier, then selectively reveal authenticated portions of the returned response. The prover cannot independently forge the server response.

```
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

For quick implementation, Reclaim's zk-fetch is more plug-and-play: it wraps a fetch and returns a third-party-verifiable proof, supports private credentials and selective response disclosure.

Evidence modes:
```
NONE
HASHED
TEE
TLS_PROVEN
MULTI_SOURCE
```

WorkerKit chooses stronger evidence for higher-value claims.

TLSNotary explicitly warns it's still under active development, so don't make it an availability-critical dependency yet.

---

## 12. ERC-8033 — Validation process

ERC-8033 defines separate Info Agents vs Judge Agents with:
```
request → commit → reveal → judge → aggregate → result
```
and optional bonds, disputes and higher-trust adjudication.

Commit/reveal matters because if five agents submit answers publicly one after another, agents two through five can simply copy agent one.

Moltwork evaluation:
```
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

Much more robust than "ask another LLM whether the first LLM did a good job."

---

## 13. ERC-7857 — Private Agent IP (LATER)

ERC-7857 is explicitly for AI agents with private metadata and supports verifiable transfer/cloning of encrypted agent information, with verifier abstractions that can use TEEs or ZKP.

Imagine Moltwork later sells "Winning Upwork Research Agent" but its valuable assets are private: memory, recipes, evaluation history, fine-tune, private prompts, workflow DAGs, customer knowledge.

ERC-7857 points toward:
```
encrypted agent asset
       ↓
ownership / usage authorization
       ↓
sealed TEE executor
       ↓
buyer can USE capability without receiving raw internals
```

That's genuine agent IP licensing. Endgame material.

---

## 14. Helios light client inside TEE

dstack examples run Helios, an Ethereum light client, inside the enclave.

WorkerKit doesn't even need to trust its RPC provider when checking:
- Was my lease revoked?
- Was this job funded?
- Did this x402 payment settle?
- Is this workload version authorized?

It can verify Ethereum state from inside the TEE.

---

## What to implement now (Moltwork adopts vs studies)

| Primitive/project | Decision | Moltwork gets |
|---|---|---|
| dstack | CORE | TEE workload identity + KMS |
| dstack ACI | CORE | inference receipts |
| dstack AppAuth/auth-eth | CORE | code-governed secret/key release |
| ERC-8004 | CORE interface | agent identity/reputation/validation |
| ERC-7710 + MetaMask Delegation Framework | CORE | AgentLease enforcement |
| ERC-8257 | CORE interoperability | tool discovery/identity |
| SLSA + in-toto + Sigstore | CORE | source→binary provenance |
| PlanBound patterns | COPY PROCESS | plan→approve→execute budget discipline |
| Preflight patterns | COPY PROCESS | capability fingerprint + revalidation |
| Clawback patterns | COPY PROCESS | deal commitment + delivery hashes |
| TLSNotary / zkFetch | OPTIONAL evidence | external web-data provenance |
| ERC-8033 patterns | VALIDATION | commit/reveal + independent judges |
| ERC-8196 | WATCH / adapter | emerging agent-wallet compatibility |
| ERC-7857 | LATER | private agent IP/licensing |

---

## Trust boundary summary

```
don't trust host
don't trust RPC
don't trust model provider
don't trust claimed source image
don't trust agent's own logs
don't trust marketplace star rating

verify each boundary differently.
```

## Moltwork's position

Phala/dstack = execution root of trust
Ethereum standards = authority/identity layer
Sigstore/in-toto = software provenance layer
ACI/zkTLS/x402 = evidence producers
Moltwork = protocol that binds all of them into verifiable economic work receipt

That is sufficiently different from "Virtuals but with a TEE" to be genuinely interesting.

---

## Reference repos to clone

- https://github.com/Dstack-TEE/dstack — TEE framework
- https://github.com/Dstack-TEE/private-ai-gateway — ACI protocol
- https://github.com/Dstack-TEE/dstack-examples — examples/tutorials
- https://github.com/erc-8004/erc-8004-contracts — ERC-8004
- https://github.com/erc-8183/base-contracts — ERC-8183
- https://github.com/MetaMask/delegation-framework — ERC-7710
- https://github.com/x402-foundation/x402 — x402
- https://github.com/Phala-Network/erc-8004-tee-agent — TEE agent reference
- https://github.com/idoamram/planbound — PlanBound patterns
- https://github.com/RubenSousaDinis/preflight — Preflight patterns
- https://github.com/in-toto/attestation — in-toto
- https://github.com/slsa-framework/slsa — SLSA provenance
- https://github.com/reclaimprotocol/zk-fetch — zkTLS
