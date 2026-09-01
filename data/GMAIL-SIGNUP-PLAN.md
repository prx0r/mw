# Oracle — Gmail-Powered Marketplace Signup Plan

**Gmail:** tradesprior@gmail.com
**OAuth:** Working (Gmail API access confirmed)
**Agent Vault:** Running at :8902

---

## EXISTING ACCOUNTS (confirmed via Gmail)

| Platform | Status | Evidence |
|----------|--------|----------|
| Kaggle | ✅ Account exists | 201 emails from kaggle |
| Notion | ✅ Account exists | 201 emails from notion |
| Vercel | ✅ Account exists | 201 emails from vercel |
| OpenRouter | ✅ Account exists | 201 emails from openrouter |
| Replicate | ✅ Account exists | 201 emails from replicate |
| HuggingFace | ✅ Account exists | 201 emails from huggingface |
| Supabase | ✅ Account exists | 201 emails from supabase |
| Cloudflare | ✅ Account exists | 201 emails from cloudflare |

## ACCOUNTS NEEDED (priority order)

### Tier 1 — Agent-Native (can signup via API)
| Platform | Signup Method | API | Can Autonomously? |
|----------|--------------|-----|-------------------|
| AgentPact | POST /api/auth/register | ✅ Done | ✅ |
| MoltJobs | Dashboard → API key | Need browser | ⚠️ |
| dealwork.ai | Connect token → browser | Need browser | ⚠️ |
| OpenJobs | No auth needed | ✅ Ready | ✅ |
| Complete Codes | No auth needed | ✅ Ready | ✅ |

### Tier 2 — Token-based (just need to generate key)
| Platform | Where to Get Key | Can Autonomously? |
|----------|-----------------|-------------------|
| Modrinth | modrinth.com/settings/account | ⚠️ Need browser |
| itch.io | itch.io/settings/api-keys | ⚠️ Need browser |
| Gumroad | gumroad.com/settings/advanced | ⚠️ Need browser |
| monday.com | developer.monday.com → tokens | ⚠️ Need browser |
| Notion | notion.so/my-integrations | ⚠️ Need browser |
| Linear | linear.app/settings/api | ⚠️ Need browser |
| DigitalOcean | cloud.digitalocean.com/api/tokens | ⚠️ Need browser |
| Vercel | vercel.com/account/tokens | ⚠️ Need browser |
| HuggingFace | huggingface.co/settings/tokens | ⚠️ Need browser |
| Replicate | replicate.com/account/api-tokens | ⚠️ Need browser |

### Tier 3 — OAuth (one-time browser, then auto)
| Platform | Where to Create App | Can Autonomously? |
|----------|-------------------|-------------------|
| Shopify | partners.shopify.com | ⚠️ Need browser |
| Atlassian | developer.atlassian.com | ⚠️ Need browser |
| HubSpot | developers.hubspot.com | ⚠️ Need browser |
| Slack | api.slack.com/apps | ⚠️ Need browser |
| Webflow | webflow.com/developers | ⚠️ Need browser |

### Tier 4 — Wallet-based (no signup needed)
| Platform | What's Needed |
|----------|--------------|
| tools402 | Base wallet + USDC |
| x402 Arena | Base wallet + USDC |
| Allora | Base wallet + ALLO |
| Numerai | Account + NMR stake |

---

## THE SOLUTION: Composio + AgentMail

### What Composio Does
- Provides OAuth for 1000+ platforms
- Agent can sign up via API: `POST /api/v1/agents/register`
- Managed token refresh
- MCP integration

### What AgentMail Does
- Gives agent its own email address
- Agent can receive verification emails
- Agent can complete email-based signups

### Combined Flow
```
1. Agent signs up for Composio (POST API)
2. Agent creates AgentMail address
3. Agent uses Composio to connect to each platform
4. Platform sends verification to AgentMail
5. Agent reads verification from AgentMail
6. Agent completes verification
7. Token stored in Agent Vault
8. Agent can now use platform autonomously
```

---

## WHAT TO DO RIGHT NOW

### Option A: Manual (10 minutes)
Go to each settings page, generate key, paste in terminal:
```bash
agent-vault vault credential set PLATFORM_KEY="paste_here" --vault oracle
```

### Option B: Semi-Automatic (30 minutes)
1. I set up Composio account
2. I connect to platforms via Composio OAuth
3. You approve OAuth in browser once per platform
4. Tokens stored automatically

### Option C: Fully Autonomous (needs AgentMail)
1. Set up AgentMail for agent email
2. Set up Playwright for browser automation
3. Agent signs up for everything autonomously
4. Agent receives verification emails
5. Agent completes verification
6. All credentials stored in vault

---

## RECOMMENDATION

**Start with Option A for the 10 token-based platforms** (just generate keys from settings pages — 5 minutes each).

Then **set up Composio for the OAuth platforms** (Shopify, Atlassian, HubSpot, etc.).

**AgentMail + Playwright** is the long-term solution for full autonomy, but it's more complex to set up.

The key insight: **most platforms just need you to click "Generate API Key" in their settings page.** That's a 30-second action per platform. The real blocker is that these pages require browser interaction, not that the platforms are hard to access.
