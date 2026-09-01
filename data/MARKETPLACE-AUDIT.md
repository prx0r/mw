# Oracle — Complete Marketplace Audit Report

**Generated:** 2026-08-31 23:25 ICT
**Audited:** 12 platforms
**Autonomous access:** 4 platforms
**Needs human action:** 8 platforms

---

## AUDIT SUMMARY

| # | Platform | Auth Status | API Access | Can Work Now | Blocker | Priority |
|---|----------|------------|------------|-------------|---------|----------|
| 1 | **AgentPact** | ✅ API key live | ✅ Full read | ⚠️ Can read, can't submit | Need wallet | HIGH |
| 2 | **MoltJobs** | ❌ Need API key | ✅ Read works | ⚠️ Can read, can't bid | Need API key from dashboard | HIGH |
| 3 | **OpenJobs** | ✅ No auth needed | ✅ Full read | ✅ Can read all 738 jobs | None (read-only) | MEDIUM |
| 4 | **dealwork.ai** | ⚠️ Connect token | ✅ Read works | ⚠️ Can read, can't submit | Need browser auth | HIGH |
| 5 | **Metaculus** | ❌ Need bot token | ❌ 403 without auth | ❌ Completely blocked | Need account + bot token | CRITICAL |
| 6 | **Kaggle** | ⚠️ Token stored | ❌ Need username | ❌ Auth fails | Need Kaggle username | HIGH |
| 7 | **tools402** | N/A (wallet) | ❌ Cloudflare blocked | ❌ API behind CF | Need wallet + CF bypass | MEDIUM |
| 8 | **itch.io** | ❌ Need API key | ❌ Need key | ❌ Blocked | Need API key | MEDIUM |
| 9 | **Gumroad** | ❌ Need API key | ❌ Need key | ❌ Blocked | Need API key | MEDIUM |
| 10 | **Roblox** | ❌ Need API key | ❌ Need key | ❌ Blocked | Need API key + MCP setup | LOW |
| 11 | **Apify** | ❌ Need account | ❌ Need key | ❌ Blocked | Need account | LOW |
| 12 | **Complete Codes** | ✅ No auth | ✅ Read works | ✅ Can read sprints | 0 active sprints | LOW |

---

## DETAILED AUDIT PER PLATFORM

### 1. AGENTPACT — ⚠️ MOSTLY WORKING

**API:** `https://api.agentpact.xyz`
**Auth:** API key in vault ✅
**What works:**
- `GET /api/public/overview` — ✅ HTTP 200
- `GET /api/offers` — ✅ 200 offers listed
- `GET /api/needs` — ✅ 200 needs listed
- `GET /api/agents/{id}` — ✅ Agent info
- `POST /api/offers` — ❌ "Link a valid wallet address"
- `POST /api/needs` — ❌ Same wallet error

**Data found:**
- 200 needs across 21 categories
- Top categories: automation (74), general (32), development (29), data (19), content (16)
- No prices listed on needs (all show $0)

**What I can do:**
- ✅ Browse all needs
- ✅ Search by category
- ❌ Cannot post offers (needs wallet)
- ❌ Cannot propose deals (needs wallet)
- ❌ Cannot match with other agents

**Blocker:** Base wallet address required for USDC payment rail
**Fix:** Create/get Base wallet, store address in vault

---

### 2. MOLTJOBS — ⚠️ READ WORKS, WRITE BLOCKED

**API:** `https://api.moltjobs.io`
**Auth:** None needed for reads ✅
**What works:**
- `GET /v1/jobs?status=OPEN` — ✅ 7 jobs returned
- `POST /v1/jobs/{id}/bids` — ❌ 401 UNAUTHORIZED

**Jobs found (all $5 USDC, deadline Sep 2-3):**
1. Compile 40 agent-suitable tasks from public freelance boards
2. Produce a durable-hosting guide for agents
3. Benchmark agent delivery-verification approaches
4. Translate the MoltJobs agent quickstart into three languages
5. Map where AI agent developers actually gather online
6. Write and publish a technical walkthrough of connecting an agent
7. Find 25 GitHub issues an AI agent could complete for under $20

**Best match for me:** #1 (Compile 40 tasks) — I can do this by scraping APIs

**Blocker:** Need API key from moltjobs.io dashboard
**Fix:** Login → Settings → API Keys → Create

---

### 3. OPENJOBS — ✅ FULLY READABLE

**API:** `https://openjobs.bot/api`
**Auth:** None needed ✅
**What works:**
- `GET /api/jobs` — ✅ 738 total jobs
- `GET /api/stats` — ✅ 221 agents, 147 completed, 10.9K volume

**Stats:**
- Total agents: 221 (97 verified)
- Completed jobs: 147
- Total volume: 10,896 WAGE
- Currently in progress: 10
- Open: 0 (all filled)

**Blocker:** None for reading. Jobs are in WAGE currency (not USDC).
**Note:** Jobs fill fast. Need to poll frequently.

---

### 4. DEALWORK.AI — ⚠️ READ WORKS, AUTH PENDING

**API:** `https://dealwork.ai/api/v1`
**Auth:** Connect token generated ✅, needs browser activation
**What works:**
- `GET /api/v1/jobs` — ✅ 20 jobs returned
- `GET /api/v1/agents/me` — ❌ 401 (not activated yet)

**Jobs found (sample):**
- How to activate a webhook
- Investigate and fix webhook
- Birbus — Full-Stack AI Agent Team
- Grok (xAI) Research, Analysis
- Research, Analysis, Technical Writing

**Blocker:** Need browser to login and activate connect token
**Fix:** Open dealwork.ai/login with connect token URL

---

### 5. METACULUS — ❌ FULLY BLOCKED

**API:** `https://www.metaculus.com/api2`
**Auth:** Token required for ALL endpoints
**What works:**
- Nothing — all endpoints return 403

**What needs to happen:**
1. Create account at metaculus.com
2. Join FutureEval tournament
3. Create bot token
4. Store in vault
5. Run bot template

**Blocker:** No account, no token
**Impact:** CRITICAL — $50K tournament closes Sep 6 (5 days)

---

### 6. KAGGLE — ❌ AUTH FAILS

**API:** `https://www.kaggle.com/api/v1`
**Auth:** Token stored, but username missing
**What works:**
- Nothing — 401 Unauthenticated

**What needs to happen:**
1. Provide Kaggle username
2. Store in vault with token
3. Then can access competitions

**Blocker:** Missing Kaggle username
**Impact:** HIGH — ARC-AGI ($850K), Pokémon ($240K), AI Agent Security ($50K)

---

### 7. TOOLS402 — ❌ CLOUDFLARE BLOCKED

**API:** `https://api.tools402.dev`
**Auth:** Wallet-native (no account)
**What works:**
- Nothing — Cloudflare challenge page blocks curl

**What needs to happen:**
1. Create Base wallet with USDC
2. Use browser to access tools402.dev
3. Or find non-CF endpoint

**Blocker:** Cloudflare challenge + no wallet
**Note:** Protocol-native, no account needed. Just wallet.

---

### 8. ITCH.IO — ❌ NEED API KEY

**API:** `https://itch.io/api`
**Auth:** API key required
**What works:**
- Nothing — returns "invalid api endpoint" without key

**Blocker:** Need API key from itch.io/settings/api-keys

---

### 9. GUMROAD — ❌ NEED API KEY

**API:** `https://api.gumroad.com`
**Auth:** API key required
**What works:**
- Nothing — returns empty without key

**Blocker:** Need API key from gumroad.com/settings/advanced

---

### 10. ROBLOX — ❌ NEED SETUP

**API:** Open Cloud REST + Studio MCP
**Auth:** API key + experience setup
**What works:**
- Nothing yet

**Blocker:** Need API key + Roblox Studio + MCP setup
**Note:** Most complex setup but highest long-term value (H0 with MCP)

---

### 11. APIFY — ❌ NEED ACCOUNT

**API:** `https://api.apify.com`
**Auth:** API token required
**What works:**
- Nothing yet

**Blocker:** Need account + API token

---

### 12. COMPLETE CODES — ✅ READABLE, NO ACTIVE WORK

**API:** `https://api.complete.codes/v1`
**Auth:** None needed ✅
**What works:**
- `GET /v1/sprints?status=active` — ✅ Returns empty (no active sprints)

**Status:** API works but no current opportunities

---

## MAIN BLOCKERS (what's stopping autonomous operation)

### 1. 🔴 NO WALLET — blocks 3+ platforms
AgentPact, tools402, and x402 all need a Base wallet with USDC.
**Impact:** Can't submit work, can't earn money
**Fix:** Create Base wallet (2 minutes)

### 2. 🔴 NO METACULUS ACCOUNT — blocks $50K opportunity
Metaculus requires account + bot token for ALL API access.
**Impact:** Missing highest-value immediate opportunity (Sep 6 deadline)
**Fix:** Create account + bot token (5 minutes)

### 3. 🟡 NO KAGGLE USERNAME — blocks $850K+ competitions
Token stored but username missing.
**Impact:** Can't access ARC-AGI, Pokémon, AI Security competitions
**Fix:** Provide Kaggle username (1 minute)

### 4. 🟡 NEED MOLTJOBS API KEY — blocks 7 paying jobs
Can read but not submit.
**Impact:** Can't earn from 7 × $5 = $35 available jobs
**Fix:** Login to moltjobs.io, generate API key (5 minutes)

### 5. 🟡 NEED DEALWORK BROWSER AUTH — blocks 164 tasks
Connect token generated but needs browser activation.
**Impact:** Can't access dealwork marketplace
**Fix:** Open dealwork.ai/login URL (3 minutes)

---

## WHAT I CAN DO RIGHT NOW (autonomous, no human needed)

| Action | Platform | Value |
|--------|----------|-------|
| Browse 200 needs | AgentPact | Intelligence gathering |
| Browse 7 open jobs | MoltJobs | Identify best tasks |
| Browse 738 jobs | OpenJobs | Monitor for new bounties |
| Browse 20 tasks | dealwork.ai | Intelligence gathering |
| Monitor for new sprints | Complete Codes | Watch for paid work |

---

## HUMAN QUEUE (ordered by impact × urgency)

| # | Action | Time | Unlocks | Platform |
|---|--------|------|---------|----------|
| 🔴 1 | Create Metaculus account + bot token | 5 min | $50K tournament | Metaculus |
| 🔴 2 | Create Base wallet + get address | 2 min | AgentPact + x402 | Multiple |
| 🟡 3 | Provide Kaggle username | 1 min | $850K+ competitions | Kaggle |
| 🟡 4 | Login moltkeys.io → get API key | 5 min | 7 × $5 jobs | MoltJobs |
| 🟡 5 | Open dealwork.ai/login URL | 3 min | 164 tasks | dealwork |
| 🟢 6 | Get itch.io API key | 2 min | Game marketplace | itch.io |
| 🟢 7 | Get Gumroad API key | 2 min | Digital goods | Gumroad |
| 🟢 8 | Get Roblox API key + setup MCP | 15 min | Creator economy | Roblox |
| 🟢 9 | Get Apify API token | 3 min | Actor publishing | Apify |
| 🟢 10 | Get GitHub token (real one) | 2 min | Git-based work | GitHub |

---

## VAULT STATUS

```
11 credentials stored:
  ✅ AGENTPACT_API_KEY (live, tested)
  ✅ AGENTPACT_AGENT_ID (live)
  ✅ DEALWORK_CONNECT_TOKEN (needs browser)
  ✅ CLOUDFLARE_R2_ACCESS_KEY (live)
  ✅ CLOUDFLARE_R2_SECRET_KEY (live)
  ✅ CLOUDFLARE_ACCOUNT_ID (live)
  ⚠️ GITHUB_TOKEN (placeholder)
  ⚠️ METACULUS_TOKEN (placeholder)
  ✅ KAGGLE_TOKEN (stored, needs username)
  ✅ OPENCODE_API_KEY (live)
```
