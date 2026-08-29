# ETHOnline 2026 Plan — Moltwork Verified Worker

## The Shared Ontology

The category system makes every new Run comparable to every previous Run. That is the compounding analytics moat.

## Canonical Classification Object

```json
{
  "taxonomy_version": "mw-taxonomy-v1",
  "task_family_id": "research.ideation.technical",
  "task_family_path": ["research", "ideation", "technical"],
  "economic_surface": "BOUNTY",
  "autonomy_level": "H1",
  "capabilities": ["technical-research", "divergent-ideation", "novelty-ranking", "requirements-analysis"],
  "evaluation_modes": ["subjective-review", "requirements-check"],
  "revenue_model": "FIXED_REWARD"
}
```

The Oracle creates this. WorkerKit copies it into the WorkOrder. RunReceipt binds it. Hydra projects it. School exercises use it. Marketplace assets advertise it.

## H-Level (Autonomy Axis Only)

| Level | Meaning |
|-------|---------|
| H0 | Fully autonomous, deterministic/machine-verifiable |
| H1 | Mostly autonomous, bounded ambiguity, light human escalation |
| H2 | Human-in-the-loop, substantive judgment/review required |
| H3 | Human-led work with AI assistance |
| H4 | Primarily human, currently not practically automatable |

## Binary Proof Matrix (P0-P11)

### Must demonstrate at ETHOnline
- P0: Shared taxonomy — task_family_id survives WorkOrder → Run → Receipt → Lab
- P1: Persistent Worker — one Moltwork Worker maps to one real Letta agent
- P2: WorkerVersion — exact state commitments produce reproducible digest
- P3: WorkReceipt — hash-chained events, artifact digest, cost, evaluation
- P4: Real TEE — dstack with is_simulated=false, externally verifiable attestation
- P5: Receipt ↔ TEE binding — attestation commits to WorkerVersion + WorkOrder + root
- P6: Bounded lease — second principal invokes Worker without receiving private state
- P7: Portable identity — onchain agent identity resolves to service/trust endpoints
- P8: Validation — WorkReceipt independently validated, references exact Worker/run
- P9: Experience reuse — later Run retrieves previous Lab experience

### Strong bonus
- P10: Demonstrable learning — candidate WorkerVersion beats parent on held-out suite
- P11: Reusable capital — Run produces AssetVersion purchased/reused by later Run

## Budget Split

```
35% Real Letta Worker
30% Real dstack/receipt proof
15% Lease + identity/validation
10% Category/data spine
10% Learning/Lab demo
```

## ETHOnline 2026 Dates
September 4–16, 2026. Sponsors: The Graph ($15k), Hedera ($15k), Arc ($10k), World ($7k), 1inch ($7k), ENS ($5k), Uniswap ($5k), Ledger ($5k), Privy ($5k), Chainlink ($3k).

## Demo Story (3 minutes)

1. Oracle: Opportunity discovered with category, autonomy, reward
2. Lab: Researcher-03 evidence, skills, Briefings
3. Lease: Another wallet leases 3 calls, $1 spend ceiling
4. Worker: Persistent Letta Worker in dstack, receives Lab Brief + Skill
5. Proof: Receipt with WorkerVersion, MemFS commit, Artifact, Event root, TEE VERIFIED, Simulator FALSE
6. Ethereum: ERC-8004 identity, Validation 100/PASS
7. Lab learns: Dashboard shows category evidence, quality ↑, cost ↓

## Taxonomy Dimensions

```
Worker × WorkerVersion × TaskFamily × H-level × ProcessVersion
× Skill × Briefing × Reviewer × Model × Tool × Market × Time
    ↓
quality × cost × latency × outcome × revenue
```
