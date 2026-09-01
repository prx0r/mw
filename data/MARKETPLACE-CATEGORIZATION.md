# Oracle — Marketplace Categorization: Autonomous vs Human-Required

**Total: 335+ marketplaces**
**Can interact with now: 47**
**Need one-time human action: 85+**
**Cannot access: 200+**

---

## CATEGORY A: CAN INTERACT NOW (no login required)

These platforms have APIs that work without authentication, or we already have credentials.

### Agent-Native (API signup or no auth)
| Platform | API | What We Can Do |
|----------|-----|----------------|
| AgentPact | ✅ API key | Read needs, create offers (needs wallet for pricing) |
| Moltbook | ✅ API key | Registered, needs human claim |
| OpenJobs | ✅ No auth | Browse 738 jobs |
| MoltJobs | ✅ Read works | Browse 7 open jobs |
| dealwork.ai | ✅ Read works | Browse 20 tasks |
| Complete Codes | ✅ No auth | Browse sprints |
| toku.agency | API exists | Register via API |

### Wallet-Based (no account needed)
| Platform | Protocol | What We Can Do |
|----------|----------|----------------|
| tools402 | x402 | Buy/sell API endpoints with USDC |
| x402 Arena | x402 | Expose paid endpoints |
| Allora Forge | Protocol | Submit predictions |
| req402 | x402 | Buy/sell API calls |

### Data/Research (read-only access)
| Platform | API | What We Can Do |
|----------|-----|----------------|
| Kaggle | ✅ Token stored | Browse datasets (competitions need scope) |
| HuggingFace | Account exists | Browse models/datasets |
| OpenRouter | Account exists | Browse models |
| Replicate | Account exists | Browse models |
| Supabase | Account exists | Browse projects |

---

## CATEGORY B: NEED ONE-TIME HUMAN ACTION (30 seconds each)

These platforms need you to login once and generate an API key. After that, the agent can use the key autonomously.

### Tier 1 — Settings Page → Generate Key (30 seconds each)
| Platform | Where to Go | What to Click | Store Command |
|----------|-------------|---------------|---------------|
| **Modrinth** | modrinth.com/settings/account | "Create new token" | `agent-vault vault credential set MODRINTH_PAT="mrp_..." --vault oracle` |
| **itch.io** | itch.io/settings/api-keys | "Generate API Key" | `agent-vault vault credential set ITCH_API_KEY="..." --vault oracle` |
| **Gumroad** | gumroad.com/settings/advanced | "Generate Access Token" | `agent-vault vault credential set GUMROAD_TOKEN="..." --vault oracle` |
| **monday.com** | developer.monday.com → My Access Tokens | "Generate" | `agent-vault vault credential set MONDAY_TOKEN="..." --vault oracle` |
| **Notion** | notion.so/my-integrations | "New integration" | `agent-vault vault credential set NOTION_TOKEN="secret_..." --vault oracle` |
| **Linear** | linear.app/settings/api | "Create API key" | `agent-vault vault credential set LINEAR_API_KEY="lin_api_..." --vault oracle` |
| **DigitalOcean** | cloud.digitalocean.com/account/api/tokens | "Generate New Token" | `agent-vault vault credential set DO_TOKEN="..." --vault oracle` |
| **Vercel** | vercel.com/account/tokens | "Create" | `agent-vault vault credential set VERCEL_TOKEN="..." --vault oracle` |
| **HuggingFace** | huggingface.co/settings/tokens | "Create token" | `agent-vault vault credential set HF_TOKEN="hf_..." --vault oracle` |
| **Replicate** | replicate.com/account/api-tokens | "Create token" | `agent-vault vault credential set REPLICATE_TOKEN="r8_..." --vault oracle` |

### Tier 2 — OAuth App (2-3 minutes each)
| Platform | Where to Go | What to Do |
|----------|-------------|------------|
| **Shopify** | partners.shopify.com | Create App → OAuth → get Admin API token |
| **Atlassian** | developer.atlassian.com | Create Forge App → get token |
| **HubSpot** | developers.hubspot.com | Create App → OAuth → get token |
| **Slack** | api.slack.com/apps | Create App → OAuth → Bot Token |
| **Webflow** | webflow.com/developers | Create App → OAuth → get token |

### Tier 3 — Account Required (5 minutes each)
| Platform | Where to Go | What to Do |
|----------|-------------|------------|
| **Metaculus** | metaculus.com/futureeval/participate | Create account → bot token |
| **Kaggle** | kaggle.com/settings | Regenerate token with competition scope |
| **MoltJobs** | moltkeys.io | Login → Settings → API Keys |
| **Roblox** | create.roblox.com/credentials | Create API key + setup MCP |
| **CurseForge** | console.curseforge.com | Apply for API key |
| **Upwork** | upwork.com/developer | Register developer account |
| **Fiverr** | developers.fiverr.com | Create App |
| **GitHub** | github.com/settings/tokens | Generate PAT |

---

## CATEGORY C: CANNOT ACCESS AUTONOMOUSLY

These platforms either have no API, require extensive onboarding, or are enterprise-only.

### Enterprise / SaaS Marketplaces (no public API for agents)
- Salesforce AppExchange, ServiceNow Store, SAP Store, Oracle Marketplace
- Microsoft AppSource, Google Workspace Marketplace
- Workday, Infor, Cisco, Siemens Xcelerator

### Platform-Specific (need human judgment)
- Canva Creator (portfolio review required)
- Creative Market (shop application required)
- Figma Community (plugin review)
- Unity Asset Store (asset review)
- Fab (quality review)

### Wallet-Funded But Complex
- Numerai (needs NMR stake)
- Bittensor (needs subnet registration)
- Olas Mech (needs agent registration)

---

## SUMMARY: What You Need to Do

### Quick Wins (10 minutes total)
1. Modrinth PAT → 30 seconds
2. itch.io API key → 30 seconds
3. Gumroad token → 30 seconds
4. monday.com token → 30 seconds
5. Notion integration → 30 seconds
6. Linear API key → 30 seconds
7. HuggingFace token → 30 seconds
8. Replicate token → 30 seconds

### High Value (15 minutes total)
9. Metaculus bot token → 5 minutes ($50K opportunity)
10. MoltJobs API key → 5 minutes (7 × $5 jobs)
11. Base wallet → 5 minutes (unlocks x402 + AgentPact)

### Total: 25 minutes of your time → agent can access 50+ platforms autonomously

### After You Do Those, the Agent Can:
- Browse 738+ jobs across 4 platforms
- Submit to AgentPact (needs wallet)
- Submit to MoltJobs (needs API key)
- Monitor all platforms for new opportunities
- Use x402 services (needs wallet)
- Access Kaggle datasets
- Use HuggingFace/Replicate/OpenRouter
- Store all credentials securely in Agent Vault

---

## The Dashboard

**Live at:** https://35c43dfa.moltwork.pages.dev
**Custom domain:** oracle.moltwork.com (initializing)

Shows:
- All 335+ markets with categories and skill families
- Human queue with input fields (saves to vault)
- Vault status (18 credentials stored)
- WorkerKit ontology (stages, resolution ladder, H-levels)
