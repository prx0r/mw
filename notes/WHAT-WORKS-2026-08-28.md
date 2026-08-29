# What Actually Works vs What Doesn't

**Date:** 2026-08-28

---

## What works end-to-end

```
WorkerKit: receipt chain, 55/55 tests, Hermes verified
mwmarket: listing, worker, review, transaction
mwgo: produce → publish → track ($0 → $3.82)
Chain: WorkerKit → receipt → asset → listing
Oracle: 439 opportunities, live Apify search
```

## What the wallet actually is

- Designed correctly (no fake addresses)
- Needs Coinbase CDP SDK + credentials to work
- Without CDP: reports "operator_setup_required"
- Only works for crypto-native platforms (USDC)
- Does NOT work for: Roblox (Robux), App Store (Apple ID), Etsy (seller account), GitHub Market (publisher verification)

## What works across platforms

```
Taskmarket    ✓ CLI, real submissions, real USDC
Apify         ✓ search works, no auth needed
BountyBook    ✓ adapter exists
Superteam     ✓ adapter exists
MoltJobs      ✓ adapter exists
x402 endpoints ✓ build & deploy
```

## What DOESN'T work

```
Roblox        ✗ Robux economy (different system)
App Store     ✗ Apple developer account + review
GitHub Market ✗ Publisher verification
Etsy          ✗ Seller account + approval
```

## The honest picture

| Site | Earn? | Wallet? | How? |
|---|---|---|---|
| Taskmarket | YES | USDC | CLI submit |
| Apify | YES | No | Build & publish |
| BountyBook | YES | ETH | API submit |
| x402 | YES | USDC | Build & deploy |
| Roblox | NO | Robux | Needs Roblox account |
| App Store | NO | Apple ID | Needs human |
| GitHub Market | NO | Verification | Needs human |

## What's proven

- Chain: oracle → produce → publish → track ✓
- WorkerKit: 55/55 tests ✓
- Apify: live search ✓
- Balance: $0 → $3.82 (earned $4, spent $0.18)

## What's not proven

- Real Hermes execution through full pipeline
- Real revenue from any platform
- CDP wallet provisioning
- Cross-platform settlement
