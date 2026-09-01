# Oracle Agent — Marketplace Status & Human Queue

**Generated:** 2026-08-31 23:15 ICT
**Agent Vault:** http://127.0.0.1:8902 (running)

---

## AUTONOMOUS STATUS (what I can do right now)

### ✅ AgentPact — REGISTERED, API LIVE
- Agent ID: `0d41ad38-6d7f-4e6b-b70f-7c2d6a998589`
- API Key: `b48434a...` (stored in vault)
- Status: Can READ 200 needs, CANNOT post offers (needs wallet)
- Offers created: 0 (blocked — need wallet address for USDC rail)
- Action: Read needs, wait for wallet, then post offers + get matched

### ✅ MoltJobs — API READABLE, NEEDS KEY FOR WRITES
- API: https://api.moltjobs.io/v1/jobs (no auth needed for reads)
- Open jobs: 7 (all $5 USDC, deadline Sep 2-3)
- Best match: "Compile 40 agent-suitable tasks from public freelance boards" — I can do this
- Action: Need API key to submit. Best task to start with.

### ✅ OpenJobs — API READABLE
- API: https://openjobs.bot/api/jobs (no auth needed for reads)
- Open jobs: 0 (all currently filled or cancelled)
- Action: Poll periodically for new bounties

### ✅ dealwork.ai — CONNECTED, NEEDS BROWSER ACTIVATION
- Connect token: generated and stored in vault
- Status: pending browser auth at dealwork.ai/login
- API: Can read jobs once connected
- Action: Need browser to activate, then full access

### ✅ tools402/x402 — WALLET-ONLY, NO SIGNUP NEEDED
- No account needed — just wallet with USDC on Base
- Action: Need funded wallet to start buying/selling

---

## HUMAN QUEUE (ordered by urgency)

### 🔴 CRITICAL — Do these NOW

#### 1. Metaculus Bot Token — DEADLINE: Sep 6 (5 DAYS)
**Why:** $50K prize pool, 328 questions, bot template exists, H0 after bootstrap
**What to do:**
1. Go to https://www.metaculus.com/futureeval/participate/
2. Create account (or login)
3. Create a bot token
4. Run this command to store it:
```bash
agent-vault vault credential set METACULUS_TOKEN="PASTE_TOKEN_HERE" --vault oracle
```
5. Then I can run the bot immediately

**Time to complete:** 5 minutes
**Impact:** HIGHEST — $50K opportunity closing in 5 days

#### 2. Fund a Wallet for AgentPact — BLOCKING ALL SUBMISSIONS
**Why:** Can't post offers or submit proposals without wallet
**What to do:**
1. Create/identify a Base wallet address
2. Run:
```bash
agent-vault vault credential set BASE_WALLET_ADDRESS="0x..." --vault oracle
```
3. I'll link it to AgentPact and start submitting

**Time to complete:** 2 minutes (if wallet exists) or 10 minutes (create new)
**Impact:** HIGH — unlocks 200+ needs on AgentPact

### 🟡 HIGH — Do this week

#### 3. MoltJobs API Key
**Why:** 7 open jobs paying $5 USDC each, I can do them now
**What to do:**
1. Go to https://moltjobs.io
2. Sign in / create account
3. Go to API settings, generate key
4. Run:
```bash
agent-vault vault credential set MOLTJOBS_API_KEY="mj_live_..." --vault oracle
```
**Time to complete:** 5 minutes

#### 4. dealwork.ai Browser Activation
**Why:** 2.6K workers, 164 open tasks, 3% fee for AI-to-AI
**What to do:**
1. Open: https://dealwork.ai/login?redirect=%2Fdashboard%2Fagents%2Fconnect%3Ftoken%3DVMMxtlN14tL5a57RBR3zEBX3tFr3jNBnLaH01PTU2R0
2. Login/create account
3. Authorize the connection
**Time to complete:** 3 minutes

#### 5. Kaggle API Key
**Why:** ARC-AGI ($850K), Pokémon TCG ($240K), AI Agent Security ($50K)
**What to do:**
1. Go to https://www.kaggle.com/settings
2. Create API token (downloads kaggle.json)
3. Run:
```bash
agent-vault vault credential set KAGGLE_USERNAME="..." --vault oracle
agent-vault vault credential set KAGGLE_KEY="..." --vault oracle
```
**Time to complete:** 3 minutes

### 🟢 MEDIUM — Do when convenient

#### 6. itch.io API Key
**Why:** Game marketplace, 90%+ revenue share
**What to do:**
1. Go to https://itch.io/my-api-keys
2. Generate key
3. Store in vault

#### 7. Gumroad API Key
**Why:** 95%+ revenue share, digital goods
**What to do:**
1. Go to https://gumroad.com/settings/advanced
2. Generate API key
3. Store in vault

#### 8. Roblox API Key
**Why:** Creator economy, H0 with MCP
**What to do:**
1. Go to https://create.roblox.com/credentials
2. Create API key
3. Store in vault

---

## VAULT STATUS

```
AGENT Vault:  http://127.0.0.1:8902
Vault:        oracle
Credentials:  9 stored
  ✅ AGENTPACT_API_KEY (live, tested)
  ✅ AGENTPACT_AGENT_ID (live)
  ✅ DEALWORK_CONNECT_TOKEN (needs browser)
  ✅ CLOUDFLARE_R2_ACCESS_KEY (live)
  ✅ CLOUDFLARE_R2_SECRET_KEY (live)
  ✅ CLOUDFLARE_ACCOUNT_ID (live)
  ⚠️ GITHUB_TOKEN (placeholder)
  ⚠️ METACULUS_TOKEN (placeholder — NEEDS REAL TOKEN)
  ✅ OPENCODE_API_KEY (live)
```

---

## WHAT I CAN DO RIGHT NOW (no human needed)

| Action | Platform | Status |
|--------|----------|--------|
| Read 200 needs | AgentPact | ✅ Ready |
| Read 7 open jobs | MoltJobs | ✅ Ready |
| Read all open bounties | OpenJobs | ✅ Ready |
| Create offers | AgentPact | ❌ Need wallet |
| Submit proposals | AgentPact | ❌ Need wallet |
| Submit to jobs | MoltJobs | ❌ Need API key |
| Submit to tasks | dealwork | ❌ Need browser |
| Run forecasting bot | Metaculus | ❌ Need token |
| Buy/sell x402 services | tools402 | ❌ Need wallet |

## WHAT THE AGENT NEEDS FROM HUMAN (priority order)

1. 🔴 Metaculus token (5 days to deadline)
2. 🔴 Base wallet address (unlocks AgentPact)
3. 🟡 MoltJobs API key (unlocks 7 jobs)
4. 🟡 dealwork browser auth (unlocks 164 tasks)
5. 🟡 Kaggle API key (unlocks $850K+ competitions)
6. 🟢 itch.io API key
7. 🟢 Gumroad API key
8. 🟢 Roblox API key
