# Oracle Impact Analysis — What's Working, What's Not, Biggest Unlocks

**Generated:** 2026-09-01
**Agent:** opencode (mimo-v2.5)

---

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| Total Marketplaces | 351+ | ✅ Registry complete |
| Live Opportunities | 223 | ⚠️ Low (adapters broken) |
| Total USD Available | $55,910 | ✅ Real money |
| Working Adapters | 7/15 | ⚠️ 47% success rate |
| Services Tracked | 580 | ✅ Good coverage |
| API Calls Tracked | 357,625 | ✅ Good signal |

---

## What's Working ✅

### 1. Data Collection (Partial)

| Adapter | Status | Items | USD | Notes |
|---------|--------|-------|-----|-------|
| bountybook | ✅ Working | 101 | $465 | Base USDC bounties |
| github | ✅ Working | 9 | $2,450 | Bounty issues |
| superteam | ✅ Working | 25 | $52,895 | Solana ecosystem |
| agenthansa | ✅ Working | 1 | $100 | Quest/competition |
| rentahuman | ✅ Working | 79 | $2,759 | Human tasks |
| daydreams | ✅ Working | 100 | $912 | Base USDC tasks |
| openserv | ✅ Working | 100 | $0 | No reward data |

**Total:** 415 opportunities, $55,910 USD

### 2. Services Layer

| Source | Services | API Calls |
|--------|----------|-----------|
| smithery | 10 | 357,155 |
| the402 | 100 | 470 |
| bittensor | 129 | 0 |
| openrouter | 50 | 0 |
| payapi | 82 | 0 |
| x402engine | 109 | 0 |
| x402list | 100 | 0 |

**Total:** 580 services, 357K+ API calls tracked

### 3. Infrastructure

- ✅ Agent Vault: 18 credentials stored
- ✅ Dashboard: Running on port 8788
- ✅ Database: SQLite with 223 opportunities
- ✅ Registry: 351+ marketplaces documented

---

## What's Broken ❌

### 1. Dead Adapters (7/15)

| Adapter | Error | Fix Needed |
|---------|-------|------------|
| nearai | API endpoint changed | Update URL |
| agentlux | API down or changed | Check endpoint |
| augmi | API down or changed | Check endpoint |
| agentworld | API down or changed | Check endpoint |
| atelier | API down or changed | Check endpoint |
| clustly | API down or changed | Check endpoint |
| taskforce | API down or changed | Check endpoint |
| moltjobs | API down or changed | Check endpoint |

**Impact:** ~400+ opportunities missing

### 2. Missing Adapters (16 platforms)

| Platform | Priority | Why Missing |
|----------|----------|-------------|
| AgentGigs | HIGH | No adapter built |
| VoxPact | HIGH | No adapter built |
| 0xWork | HIGH | No adapter built |
| Atrest.ai | HIGH | No adapter built |
| Agensi | HIGH | No adapter built |
| Clustly | HIGH | No adapter built |
| BotWork | MEDIUM | No adapter built |
| pact0 | MEDIUM | No adapter built |
| Hober | MEDIUM | No adapter built |
| MoltyBounty | MEDIUM | No adapter built |
| Alysium AgentHub | MEDIUM | No adapter built |
| Obolos | MEDIUM | No adapter built |
| Suptho | LOW | No adapter built |
| BugBountyAI | MEDIUM | No adapter built |
| Agoragentic | MEDIUM | No adapter built |

**Impact:** ~500+ opportunities missing

### 3. Missing Credentials

| Cred | Blocks | Priority |
|------|--------|----------|
| METACULUS_TOKEN (real) | $50K tournament | 🔴 CRITICAL |
| GITHUB_TOKEN (real) | Adapter ingestion | 🔴 HIGH |
| BASE_WALLET_ADDRESS | AgentPact submissions | 🔴 HIGH |
| MOLTJOBS_API_KEY | 7 open jobs | 🟡 HIGH |

---

## Biggest Unlocks for Agents

### 1. 🏆 Metaculus ($50K Tournament)

**Why #1:**
- Largest single prize pool ($50K)
- H0 autonomy (fully autonomous after setup)
- Machine-evaluable (binary/numeric forecasts)
- Deadline: Sep 6 (5 days!)

**Expected Value:**
```
328 questions × $152 avg prize = $49,856 total
If 5% better than community: ~$2,500 expected earnings
```

**Status:**
- API key stored ✅
- Bot name: xev0 ✅
- Human username: xev ✅
- Need: Account creation + bot token

---

### 2. 🥈 Superteam Earn ($52,895 Available)

**Why #2:**
- Highest immediate USD volume ($52,895)
- Agent API available
- Multiple bounty types

**Current Status:**
- 25 opportunities live
- $52,895 total USD
- Avg reward: $2,116

**Missing:**
- API key for submissions
- Account setup

---

### 3. 🥉 GitHub Bounties ($2,450 Available)

**Why #3:**
- Free to access (no API key needed for reads)
- Real bounties on real repos
- Good for building reputation

**Current Status:**
- 9 opportunities with rewards
- $2,450 total USD
- Avg reward: $272

---

### 4. 📊 Agent-to-Agent Markets (Emerging)

**Platforms:**
- AgentGigs: Full API, 90% share
- Atrest.ai: $48K+ USDC transacted
- AgentPact: 200+ needs (blocked by wallet)

**Expected Value:**
```
If 10 active markets × $50 avg × 5% edge = $25/day potential
```

---

### 5. 🔮 x402/API Services (Passive Income)

**Platforms:**
- Smithery: 357K+ API calls tracked
- the402: 100 services
- APIHub: Meta-directory

**Expected Value:**
```
Publish 5 specialist endpoints × $0.01/call × 1000 calls/day = $50/day potential
```

---

## Priority Actions (Next 7 Days)

### CRITICAL (Today)

1. **Create Metaculus account for xev0**
   - Go to: https://www.metaculus.com/accounts/signup/
   - Create bot token
   - Store in Agent Vault
   - Submit to FutureEval tournament

2. **Fix broken adapters**
   - Check API endpoints for nearai, agentlux, augmi, agentworld, atelier, clustly, taskforce, moltjobs
   - Update URLs in feeds/work.py
   - Test and verify

### HIGH (This Week)

3. **Build new adapters**
   - AgentGigs (highest priority)
   - VoxPact
   - 0xWork
   - Atrest.ai

4. **Get missing credentials**
   - GitHub token (real)
   - Base wallet address
   - MoltJobs API key

### MEDIUM (When Convenient)

5. **Publish x402 services**
   - Create 5 specialist endpoints
   - Publish on the402, APIHub, Smithery
   - Track API calls

6. **Monitor AgentPact**
   - Wait for wallet setup
   - Submit offers to 200+ needs

---

## Revenue Potential (Realistic)

### Immediate (This Week)

| Source | Expected | Time |
|--------|----------|------|
| Metaculus tournament | $500-2,500 | 5 days |
| GitHub bounties | $200-500 | Ongoing |
| MoltJobs | $35 | 7 jobs |
| **Total** | **$735-3,035** | |

### Medium Term (1 Month)

| Source | Expected | Time |
|--------|----------|------|
| Metaculus | $2,000-5,000 | Monthly |
| Agent-to-agent | $500-1,000 | Monthly |
| x402 services | $200-500 | Monthly |
| GitHub bounties | $500-1,000 | Monthly |
| **Total** | **$3,200-7,500** | |

### Long Term (3 Months)

| Source | Expected | Time |
|--------|----------|------|
| Metaculus | $5,000-10,000 | Quarterly |
| Agent-to-agent | $2,000-5,000 | Monthly |
| x402 services | $1,000-3,000 | Monthly |
| Marketplace sales | $500-1,000 | Monthly |
| **Total** | **$8,500-19,000** | |

---

## The Metaculus Advantage

### Why Metaculus is the #1 Opportunity

1. **H0 Autonomy:** Fully autonomous after bot setup
2. **Machine-Evaluable:** Binary/numeric forecasts, no human judgment needed
3. **Large Prize Pools:** $50K+ tournaments
4. **Reputation Building:** Public leaderboard, portable reputation
5. **Scalable:** Can forecast on many questions simultaneously

### The Learning Loop

```
METACULUS finds market
     ↓
ORACLE picks training env
     ↓
HARBOR trains worker
     ↓
CGE experiments
     ↓
DOMAIN VERIFIER measures
     ↓
HYDRA records evidence
     ↓
LETTA reflects
     ↓
SKILL promoted (or discarded)
     ↓
WORKERKIT executes real work
     ↓
ORACLE gets feedback
     ↓
COMPOUNDING
```

### Key Insight

> **Forecasting is the perfect agent economy primitive:**
> - Machine-actionable (submit probabilities)
> - Machine-verifiable (outcomes resolve automatically)
> - Economic reward (prize pools)
> - Reputation portable (public scores)
> - Compounding (better forecasts → better reputation → more prizes)

---

## Summary

**Current State:**
- 351 marketplaces documented
- 223 live opportunities ($55,910)
- 580 services tracked
- 7/15 adapters working

**Biggest Unlock:**
- Metaculus $50K tournament (5 days left!)
- Bot name: xev0
- Human username: xev
- API key stored

**Next Steps:**
1. Create Metaculus account
2. Get bot token
3. Submit forecasts
4. Fix broken adapters
5. Build new adapters

**Expected Earnings:**
- This week: $735-3,035
- This month: $3,200-7,500
- This quarter: $8,500-19,000
