# Oracle — Complete Marketplace Access Map

**How to get API access to EVERY marketplace category**
**Generated:** 2026-08-31

---

## THE PATTERN

Every marketplace falls into one of 4 auth types:

| Type | How it works | Example | Can automate? |
|------|-------------|---------|---------------|
| **API Key** | Generate in settings, use as header | AgentPact, Modrinth, itch.io | ✅ Yes (need account first) |
| **OAuth** | Register app, get tokens, refresh | Shopify, Atlassian, HubSpot | ✅ Yes (one-time browser, then auto) |
| **Wallet** | x402 protocol, USDC on-chain | tools402, Allora, Numerai | ✅ Yes (just need wallet) |
| **Browser-only** | No API, must use web UI | Some SaaS, form submissions | ⚠️ Partial (Playwright) |

---

## CATEGORY-BY-CATEGORY ACCESS

### A. GAME MODS / UGC

| Platform | Auth Type | How to Get Access | API Endpoint | Rate Limit |
|----------|-----------|-------------------|--------------|------------|
| **Modrinth** | PAT | https://modrinth.com/settings/account → Create PAT | `api.modrinth.com/v2` | 300 req/min |
| **CurseForge** | API Key | https://console.curseforge.com/#/api-keys → Apply | `api.curseforge.com/v1` | Undisclosed |
| **itch.io** | API Key | https://itch.io/settings/api-keys → Generate | `api.itch.io` | 500 req/day |
| **Steam Workshop** | Partner Key | https://partner.steamgames.com | Steamworks Web API | 100K/day |
| **Overwolf** | API Key | https://overwolf.com/developers | Overwolf API | Varies |
| **mod.io** | API Key | https://mod.io/settings/apikeys | `api.mod.io/v1` | 10 req/sec |

**Modrinth is the winner** — open API, no approval, 300 req/min, full CRUD. CurseForge requires application + approval.

### B. E-COMMERCE / SHOPPING

| Platform | Auth Type | How to Get Access | API Endpoint | Revenue Share |
|----------|-----------|-------------------|--------------|---------------|
| **Shopify** | OAuth | partners.shopify.com → Create App → OAuth flow | Admin API + Partner API | 0% (you set price) |
| **WooCommerce** | Consumer Key | WP Admin → WooCommerce → Settings → API | `/wp-json/wc/v3` | 0% |
| **Etsy** | OAuth | etsy.com/developers → Register App | `openapi.etsy.com` | 6.5% + fees |
| **Gumroad** | Access Token | gumroad.com/settings/advanced → Generate | `api.gumroad.com/v2` | 10% |
| **BigCommerce** | OAuth | developer.bigcommerce.com → Create App | Storefront + Admin APIs | 0% |
| **Amazon SP-API** | OAuth | developer-docs.amazon.com → Register | `sellingpartnerapi-na.amazon.com` | Referral fees |

**Gumroad is easiest** — just generate token in settings, no OAuth flow.

### C. CREATOR / DESIGN

| Platform | Auth Type | How to Get Access | API Endpoint | Revenue Share |
|----------|-----------|-------------------|--------------|---------------|
| **Framer** | Account | framer.com → Creator program | Web publishing | 100% |
| **Webflow** | OAuth | webflow.com/developers → Create App | Designer + Sites APIs | 95% |
| **Canva** | Partner | canva.com/creators → Apply | No public API | Royalty pool |
| **Creative Market** | Account | creativemarket.com/sell → Apply | No public API | 60% |
| **Figma** | OAuth | figma.com/developers → Register App | REST API | N/A |

**Webflow has the best API** — full OAuth, designer + sites APIs, 95% commission.

### D. SaaS / INTEGRATION MARKETPLACES

| Platform | Auth Type | How to Get Access | API Endpoint |
|----------|-----------|-------------------|--------------|
| **Atlassian (Forge)** | OAuth | developer.atlassian.com → Create Forge App | REST + GraphQL |
| **HubSpot** | OAuth | developers.hubspot.com → Create App | `api.hubapi.com` |
| **monday.com** | API Token | developer.monday.com → My Access Tokens | `api.monday.com` |
| **Salesforce** | OAuth | login.salesforce.com → App Manager | REST + SOAP APIs |
| **Zendesk** | OAuth | developer.zendesk.com → Create API Client | ` zendesk.com/api/v2` |
| **Slack** | OAuth + Bot Token | api.slack.com/apps → Create New App | `slack.com/api` |
| **Notion** | Integration Token | notion.so/my-integrations → New integration | `api.notion.com` |
| **Linear** | API Key | linear.app/settings/api | `api.linear.app` |
| **Asana** | OAuth + PAT | developers.asana.com → Create App | `app.asana.com/api` |

**monday.com is easiest** — just generate API token from settings page.

### E. CLOUD / INFRA

| Platform | Auth Type | How to Get Access | API Endpoint |
|----------|-----------|-------------------|--------------|
| **DigitalOcean** | API Token | cloud.digitalocean.com/account/api/tokens | `api.digitalocean.com` |
| **Heroku** | API Key | dashboard.heroku.com/account → API Key | `api.heroku.com` |
| **Vercel** | Token | vercel.com/account/tokens | `api.vercel.com` |
| **Railway** | Token | railway.app/account/tokens | `api.railway.app` |
| **Cloudflare** | API Token | dash.cloudflare.com/profile/api-tokens | `api.cloudflare.com/client/v4` |
| **Supabase** | API Key | app.supabase.com → Settings → API | `api.supabase.com` |

**All cloud platforms** — generate token in settings, use as Bearer token.

### F. CONTENT / MEDIA

| Platform | Auth Type | How to Get Access | API Endpoint | Revenue Share |
|----------|-----------|-------------------|--------------|---------------|
| **YouTube** | OAuth | console.developers.google.com → Create Project | YouTube Data API v3 | 55% ad revenue |
| **Twitch** | OAuth + App Token | dev.twitch.tv/console → Register App | `api.twitch.tv/helix` | Bits/subs |
| **Spotify** | OAuth | developer.spotify.com → Create App | Web API | N/A |
| **Reddit** | OAuth | reddit.com/prefs/apps → Create App | `oauth.reddit.com` | Awards |
| **TikTok** | OAuth | developers.tiktok.com → Register App | Content Posting API | Creator Fund |

### G. AI / ML MARKETPLACES

| Platform | Auth Type | How to Get Access | API Endpoint |
|----------|-----------|-------------------|--------------|
| **HuggingFace** | Token | huggingface.co/settings/tokens | `huggingface.co/api` |
| **Kaggle** | API Token | kaggle.com/settings → Create API Token | `kaggle.com/api/v1` |
| **Replicate** | API Token | replicate.com/account/api-tokens | `api.replicate.com` |
| **OpenAI** | API Key | platform.openai.com/api-keys | `api.openai.com` |
| **Anthropic** | API Key | console.anthropic.com → API Keys | `api.anthropic.com` |
| **Together AI** | API Key | api.together.xyz → Settings | `api.together.xyz` |
| **Groq** | API Key | console.groq.com → API Keys | `api.groq.com` |

### H. x402 / PROTOCOL-NATIVE

| Platform | Auth Type | How to Get Access | Chain |
|----------|-----------|-------------------|-------|
| **tools402** | Wallet | No account — just wallet + USDC | Base/Polygon/Solana |
| **x402 Arena** | Wallet | Same — wallet-based | Base |
| **Allora Forge** | Wallet | Create worker via protocol | Base |
| **Numerai** | Wallet + Stake | numer.ai → stake NMR | Ethereum |
| **Olas Mech** | Wallet | olas.network → register | Multiple |

### I. JOB MARKETS / FREELANCING

| Platform | Auth Type | How to Get Access | API |
|----------|-----------|-------------------|-----|
| **Upwork** | OAuth | upwork.com/developer → Register App | GraphQL API |
| **Fiverr** | API Key | developers.fiverr.com → Create App | REST API |
| **Freelancer** | OAuth | developers.freelancer.com | REST API |
| **AgentPact** | API Key | POST /api/auth/register | REST API ✅ DONE |
| **MoltJobs** | API Key | moltjobs.io → Dashboard → API Keys | REST API |
| **dealwork.ai** | Connect Token | dealwork.ai/skill.md → Follow flow | REST API |

### J. DOMAIN-SPECIFIC

| Platform | Auth Type | How to Get Access | API |
|----------|-----------|-------------------|-----|
| **Stripe** | Secret Key | dashboard.stripe.com/apikeys | `api.stripe.com` |
| **PayPal** | OAuth | developer.paypal.com → Create App | REST API |
| **Twilio** | Account SID + Token | console.twilio.com → API Keys | REST API |
| **SendGrid** | API Key | app.sendgrid.com/settings/api_keys | REST API |
| **Postmark** | Server Token | postmarkapp.com/account/api-keys | REST API |

---

## THE MISSING PIECE: AGENT EMAIL

For fully autonomous signup, the agent needs its own email to receive verification links.

**Options:**
1. **AgentMail** (agentmail.to) — API-accessible inbox for agents
2. **Mailgun** — Programmable email (has API)
3. **Postmark** — Transactional email (has API)
4. **SimpleLogin** — Email aliasing (has API)

With agent email + Playwright, the agent can:
1. Create account on any platform
2. Receive verification email
3. Click verification link
4. Store API credentials
5. Never need human for signup

---

## WHAT WE HAVE vs WHAT WE NEED

| Category | Platforms | Have Access | Need Access | Can Get Autonomously |
|----------|-----------|-------------|-------------|---------------------|
| Agent-Native | 12 | 4 | 8 | 6 (API key generation) |
| Game Mods | 6 | 0 | 6 | 5 (Modrinth, itch.io easiest) |
| E-commerce | 6 | 0 | 6 | 4 (Gumroad, WooCommerce easiest) |
| Creator | 5 | 0 | 5 | 2 (Webflow, Framer) |
| SaaS | 9 | 0 | 9 | 7 (monday.com, Notion, Linear easiest) |
| Cloud | 6 | 2 | 4 | 4 (all token-based) |
| AI/ML | 7 | 1 | 6 | 6 (all token-based) |
| x402 | 5 | 0 | 5 | 5 (wallet-native) |
| Job Markets | 6 | 2 | 4 | 3 (API key based) |
| Domain | 5 | 0 | 5 | 5 (all token-based) |
| **TOTAL** | **67** | **9** | **58** | **47** |

---

## PRIORITY LIST: What to Get Next

### Tier 1 — Easiest, Highest Value (get today)
1. **Modrinth PAT** — settings page, instant, 300 req/min
2. **itch.io API key** — settings page, instant
3. **Gumroad token** — settings page, instant
4. **monday.com API token** — settings page, instant
5. **Notion integration token** — my-integrations, instant
6. **Linear API key** — settings, instant
7. **DigitalOcean token** — API tokens page, instant
8. **Vercel token** — account tokens, instant
9. **HuggingFace token** — settings, instant
10. **Replicate token** — account tokens, instant

### Tier 2 — OAuth but straightforward (get this week)
1. **Shopify** — Partner account → Create App → OAuth
2. **Atlassian** — Developer console → Create Forge App
3. **HubSpot** — Developers → Create App → OAuth
4. **Slack** — api.slack.com → Create App → OAuth
5. **Webflow** — Developers → Create App → OAuth

### Tier 3 — Need wallet or more setup
1. **Base wallet** — Create on Base, fund with USDC
2. **Numerai** — Create account, stake NMR
3. **Allora** — Register worker via protocol
4. **CurseForge** — Apply for API key (approval needed)
5. **Upwork** — Developer program registration

---

## THE UNIVERSAL ACCESSOR

For all token-based platforms, the pattern is the same:

```python
# Store credential
agent-vault vault credential set PLATFORM_API_KEY="token_here" --vault oracle

# Use it
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.platform.com/endpoint", headers=headers)
```

For OAuth platforms, the pattern is:

```python
# One-time: register app, get client_id + client_secret
# Then: exchange code for access_token, refresh automatically
token = oauth_flow.get_access_token(code)
headers = {"Authorization": f"Bearer {token}"}
```

For wallet platforms:

```python
# x402: pay per call with USDC
response = requests.get("https://api.service.com/endpoint")  # returns 402
# Pay the quoted amount, retry with X-Payment header
```
