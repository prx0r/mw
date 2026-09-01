# Oracle — Skill Families v2: Process-First Categorization

**Principle:** Don't categorize by what the marketplace sells. Categorize by **what the agent literally does, step by step, with what tools.**

Two markets that both need "code" can have completely different processes:
- Writing a Roblox obby = Luau + Studio MCP + visual QA + multiplayer test + publish via REST
- Writing a Chrome extension = manifest.json + DOM injection + Playwright test + screenshot QA + Web Store API
- Writing a x402 endpoint = HTTP handler + schema + deploy + monitor

Those aren't the same skill. They share "write code" but the tools, environments, verification, and feedback loops are entirely different.

---

## The 18 Skill Families (Process-First)

### F1. API ENDPOINT / MICRO-SERVICE
**What the agent literally does:** Define HTTP schema → implement handler → deploy → monitor → monetize
**Tools:** HTTP framework, schema validator, deployment platform, wallet
**Environment:** Local dev → cloud deploy
**Verifier:** endpoint responds correctly, schema valid, latency acceptable
**Feedback loop:** seconds (call endpoint, check response)

**Markets:** x402 Bazaar, x402 Arena, req402, tools402, Agent Wonderland, Apify actors, AgentDataHub, AgentReader, APIMesh, 402.rest, pay.sh
**Training env:** API test fixture — given schema spec, build working endpoint
**Reusability:** VERY HIGH — one "build API endpoint" skill serves 15+ markets

**Sub-schools:**
- F1a: Simple CRUD endpoint (GET/POST, JSON)
- F1b: Streaming endpoint (SSE, websockets)
- F1c: Authenticated endpoint (API keys, OAuth)
- F1d: Paid endpoint (x402 middleware, settlement)
- F1e: Webhook receiver (event-driven, idempotent)

---

### F2. BROWSER EXTENSION
**What the agent literally does:** Design manifest → build popup/options → inject content scripts → test DOM interaction → screenshot QA → publish
**Tools:** Chrome APIs, Playwright, screenshot comparison, Web Store API
**Environment:** Browser test harness
**Verifier:** manifest valid, content script runs, popup renders, screenshots match, no console errors
**Feedback loop:** minutes (load extension, run tests, check screenshots)

**Markets:** Chrome Web Store, Firefox Add-ons, Edge Add-ons, Overwolf, Elgato Stream Deck
**Training env:** Browser test world — given a target site, build extension that interacts with it
**Reusability:** HIGH — DOM interaction, manifest, screenshot QA transfer across all extension markets

**Sub-schools:**
- F2a: Content script (inject into page, extract data)
- F2b: Popup UI (React/Svelte, state management)
- F2c: Background service worker (alarms, storage, messaging)
- F2d: DevTools panel (inspect, debug)
- F2e: Cross-browser compatibility (Chrome + Firefox + Edge)

---

### F3. SaaS APP / MARKETPLACE INTEGRATION
**What the agent literally does:** Register OAuth app → build API integration → create fixture tenant → test CRUD → build UI cards → list in marketplace
**Tools:** OAuth flow, REST/GraphQL APIs, database, frontend framework
**Environment:** Sandbox/test tenant provided by platform
**Verifier:** OAuth completes, API calls succeed, UI renders, marketplace listing valid
**Feedback loop:** minutes-hours (depends on platform sandbox availability)

**Markets:** Atlassian Forge, HubSpot, monday.com, ActiveCampaign, Asana, Klaviyo, Mailchimp, Keap, Creatio, Pipedrive, Zoho, Freshworks, Zendesk, Intercom, Salesforce AppExchange, ServiceNow, NetSuite, SAP, Oracle
**Training env:** SaaS integration world — given API docs + sandbox, build working app
**Reusability:** HIGH — OAuth, CRUD, webhook, UI card patterns repeat across all SaaS marketplaces

**Sub-schools:**
- F3a: OAuth registration + token lifecycle
- F3b: CRUD integration (create/read/update/delete via API)
- F3c: Webhook listener (event subscription, idempotent processing)
- F3d: UI card/widget (React App Card, Forge Jira panel, etc.)
- F3e: Marketplace listing (description, screenshots, pricing)
- F3f: Multi-tenant data isolation

---

### F4. E-COMMERCE APP / PLUGIN
**What the agent literally does:** Study platform API → build extension/plugin → test with fixture store → handle checkout flow → list in app store
**Tools:** Platform-specific SDK, checkout API, test store
**Environment:** Developer sandbox store
**Verifier:** plugin installs, checkout works, order data correct, no theme breakage
**Feedback loop:** hours (need to test with real store simulation)

**Markets:** Shopify App Store, WooCommerce, BigCommerce, Magento, PrestaShop, Shopware, OpenCart, CS-Cart, Ecwid, SHOPLINE, Lightspeed, Walmart, Amazon SP-API, Etsy, eBay, VTEX, Shoplazza, Wix, Squarespace
**Training env:** Commerce world — fixture store with products, orders, customers; build integration
**Reusability:** HIGH — OAuth + webhook + checkout flow patterns repeat across all commerce platforms

**Sub-schools:**
- F4a: Product/catalog sync
- F4b: Order processing + fulfillment
- F4c: Inventory management
- F4d: Payment/checkout integration
- F4e: Analytics/reporting
- F4f: Multi-store/multi-platform

---

### F5. GAME DEV — ROBLOX
**What the agent literally does:** Write Luau → Studio MCP → test in Studio → run multiplayer (StudioTestService) → device simulation → publish via REST → monitor Open Cloud
**Tools:** Studio MCP, Luau, StudioTestService, Open Cloud REST, Place Publishing API
**Environment:** Roblox Studio (MCP-accessible)
**Verifier:** Luau compiles, server boots, 4-client session works, no errors, mobile compatible
**Feedback loop:** minutes (MCP → build → test → results)

**Markets:** Roblox creator economy
**Training env:** Roblox Studio World — 6-school curriculum (atomic mechanics → microgames → UI → adversarial → economy → live)
**Reusability:** MEDIUM — Luau + Studio MCP is Roblox-specific, but game dev patterns transfer

**Sub-schools:**
- F5a: Atomic mechanics (door, inventory, checkpoint, currency, shop, NPC, quest)
- F5b: Microgame (round loop, scoring, matchmaking, respawn)
- F5c: UI/onboarding (VirtualInput simulation)
- F5d: Adversarial multiplayer (disconnect, late join, spam, bad network)
- F5e: Economy design (100K synthetic player-days simulation)
- F5f: Live experiment (A/B deployment, real telemetry)

---

### F6. GAME DEV — FORTNITE/UEFN
**What the agent literally does:** Write Verse → Unreal MCP → compile → edit scene → place devices → build UI → test session → PUBLISH REQUIRES HUMAN (Creator Portal)
**Tools:** Unreal MCP, Verse, UEFN, Creator Portal
**Environment:** UEFN local + remote play session
**Verifier:** Verse compiles, devices work, session runs, no errors
**Feedback loop:** minutes (MCP → build → test) but publish is H2

**Markets:** Fortnite UEFN islands + in-island items
**Training env:** UEFN Microgame World — similar curriculum to Roblox but Verse/C++
**Reusability:** MEDIUM — game dev patterns transfer, Verse is Epic-specific

**Sub-schools:**
- F6a: Verse basics (devices, state, events)
- F6b: Round loops (start → play → end → restart)
- F6c: UI (HUD, menus, mobile)
- F6d: Player state (inventory, progress, persistence)
- F6e: Multiplayer (server-authoritative, anti-cheat)
- F6f: Performance/memory optimization

---

### F7. GAME DEV — UNITY/UNREAL (GENERAL)
**What the agent literally does:** Write C#/C++ → build in editor → test with fixtures → package → submit to asset store
**Tools:** Unity Editor API, Unreal Editor API, asset pipeline
**Environment:** Game engine editor
**Verifier:** code compiles, prefab works, no errors, package valid
**Feedback loop:** hours (editor build + test cycle)

**Markets:** Unity Asset Store, Unreal Marketplace, Fab, itch.io (game assets)
**Training env:** Game engine world — fixture project, build component, test, package
**Reusability:** MEDIUM — C#/C++ patterns transfer, engine-specific APIs don't

**Sub-schools:**
- F7a: Editor extension (custom inspector, window, tool)
- F7b: Shader/VFX (HLSL, Shader Graph)
- F7c: Scripted asset (runtime behavior, configuration)
- F7d: Multi-platform build (Windows, Mac, Linux, Mobile)
- F7e: Documentation + screenshots + listing

---

### F8. WEB SCRAPING / DATA EXTRACTION
**What the agent literally does:** Identify target → build parser → handle anti-bot → normalize output → deploy → monitor
**Tools:** HTTP client, HTML parser, headless browser, proxy rotation, schema validator
**Environment:** Local dev → cloud deploy
**Verifier:** data extracted correctly, schema valid, no errors on sample pages
**Feedback loop:** minutes (run scraper on test URLs, check output)

**Markets:** Apify actors, x402 data services, AgentDataHub, data pipelines, research services
**Training env:** Scraping world — given target site, build robust extractor
**Reusability:** VERY HIGH — parsing, anti-bot, normalization transfer across all data work

**Sub-schools:**
- F8a: Static HTML parsing (BeautifulSoup, cheerio)
- F8b: Dynamic SPA scraping (Playwright, Puppeteer)
- F8c: API reverse-engineering (network inspection, schema inference)
- F8d: Anti-bot handling (CAPTCHA, rate limiting, fingerprinting)
- F8e: Data normalization (schema mapping, deduplication, validation)
- F8f: Monitoring + change detection

---

### F9. RESEARCH / ANALYSIS
**What the agent literally does:** Understand question → gather evidence → analyze → synthesize → structured output
**Tools:** Web search, document parsing, data analysis, report generation
**Environment:** Open-ended (web + local files)
**Verifier:** claims sourced, logic valid, conclusion supported, format correct
**Feedback loop:** minutes-hours (depends on research depth)

**Markets:** Upwork research jobs, dealwork, AgentPact, Toku.agency, Metaculus (forecasting variant), consulting gigs
**Training env:** Research world — given question + time budget, produce sourced analysis
**Reusability:** VERY HIGH — research → structured output is the most transferable skill

**Sub-schools:**
- F9a: Competitive analysis (market research, landscape mapping)
- F9b: Technical research (paper review, technology assessment)
- F9c: Due diligence (company/product evaluation)
- F9d: Market sizing (TAM/SAM/SOM estimation)
- F9e: Trend analysis (signal detection, forecasting inputs)
- F9f: Report writing (structured, sourced, actionable)

---

### F10. FORECASTING / PREDICTION
**What the agent literally does:** Read question → gather evidence → form probability distribution → submit → wait for resolution → score
**Tools:** Metaculus API, calibration tools, evidence aggregation
**Environment:** Metaculus platform
**Verifier:** proper scoring rule (Brier/log score), calibration error
**Feedback loop:** days-months (question resolution) but training uses historical questions

**Markets:** Metaculus tournaments, prediction markets (Polymarket, Manifold)
**Training env:** ForecastingWorld — historical questions with hidden resolutions
**Reusability:** MEDIUM — calibration and evidence-gathering transfer, but domain-specific

**Sub-schools:**
- F10a: Binary questions (yes/no, base rate estimation)
- F10b: Numeric distributions (ranges, medians, tails)
- F10c: Categorical (which outcome, ranked)
- F10d: Sequential updating (new evidence → revised forecast)
- F10e: Cross-question aggregation (portfolio forecasting)
- F10f: Crux identification (what would change the forecast?)

---

### F11. SECURITY / AUDIT
**What the agent literally does:** Clone repo → analyze code → find vulnerability → write patch → run tests → submit PR
**Tools:** Git, compilers, sanitizers, fuzzer, test frameworks
**Environment:** Local codebase (historical CVEs, authorized repos)
**Verifier:** old tests pass, vulnerability no longer reproduces, no regressions
**Feedback loop:** hours (build + test + verify)

**Markets:** Google Patch Rewards, Immunefi, HackerOne, Algora, bug bounties, AgentBounties
**Training env:** OSSSecurityPatchWorld — historical CVEs with hidden regression tests
**Reusability:** HIGH — audit → patch → test patterns transfer across languages and vuln classes

**Sub-schools:**
- F11a: Known bug + obvious failing test (easiest)
- F11b: Known CVE + hidden test
- F11c: Vulnerable commit without location
- F11d: Generic hardening opportunity
- F11e: Fuzz harness → find crash → root cause → patch
- F11f: Regression test design

---

### F12. TEMPLATE / THEME CREATION
**What the agent literally does:** Identify gap → design system → build responsive layout → screenshot QA → submit listing
**Tools:** Design system, responsive framework, screenshot tool, browser test
**Environment:** Design tool + browser
**Verifier:** responsive at breakpoints, screenshots match design, no broken elements
**Feedback loop:** minutes-hours (build + screenshot + iterate)

**Markets:** Framer, Webflow, Shopify Themes, Ghost Themes, Squarespace, Wix, WordPress, ThemeForest
**Training env:** Template world — given design spec, build responsive template
**Reusability:** HIGH — responsive design, component systems, screenshot QA transfer

**Sub-schools:**
- F12a: Layout system (grid, flexbox, responsive breakpoints)
- F12b: Component library (reusable blocks)
- F12c: CMS integration (content modeling, dynamic data)
- F12d: E-commerce template (product pages, cart, checkout)
- F12e: Screenshot QA (visual regression, cross-device)
- F12f: Listing optimization (descriptions, screenshots, SEO)

---

### F13. WORKFLOW AUTOMATION
**What the agent literally does:** Identify trigger → build action chain → handle errors → test with fixtures → deploy → monitor
**Tools:** n8n/Make/Zapier, API integrations, error handling, monitoring
**Environment:** Automation platform (n8n, Make, etc.)
**Verifier:** trigger fires, actions execute, error paths work, data flows correctly
**Feedback loop:** minutes (test workflow with sample data)

**Markets:** n8n workflow library, Zapier, Make, workflow automation services, n8n production hardening
**Training env:** Automation world — given business process, build reliable workflow
**Reusability:** VERY HIGH — trigger → action → error → retry patterns universal

**Sub-schools:**
- F13a: Simple trigger-action (webhook → API call)
- F13b: Multi-step chain (trigger → transform → conditional → action)
- F13c: Error handling (retry, dead letter, alerting)
- F13d: Authentication management (OAuth refresh, token rotation)
- F13e: Monitoring + alerting (health checks, drift detection)
- F13f: Cost optimization (rate limiting, batching, caching)

---

### F14. 3D ASSET / CREATIVE
**What the agent literally does:** Model geometry → texture → UV unwrap → optimize LOD → screenshot → submit
**Tools:** Blender (Python API), 3D preview, texture tools, LOD optimizer
**Environment:** 3D modeling tool + render preview
**Verifier:** geometry valid, textures applied, LOD levels work, screenshots look correct
**Feedback loop:** hours (modeling is slow, even automated)

**Markets:** Fab, TurboSquid, CGTrader, RenderHub, ArtStation, MyMiniFactory, Cults3D, Thangs, Cubebrush, Pinshape
**Training env:** 3D asset world — given spec, produce valid asset
**Reusability:** LOW-MEDIUM — 3D fundamentals transfer, but taste/quality is hard to automate

**Sub-schools:**
- F14a: Hard-surface modeling (props, weapons, furniture)
- F14b: Organic modeling (characters, creatures)
- F14c: Texturing (PBR materials, UV mapping)
- F14d: Optimization (LOD, poly reduction, format conversion)
- F14e: Documentation (screenshots, descriptions, tags)
- F14f: Packaging (zip structure, license files, readme)

---

### F15. SCIENTIFIC / ML
**What the agent literally does:** Understand problem → build pipeline → train/evaluate → measure metrics → submit results
**Tools:** Python, ML frameworks, Jupyter, experiment tracking
**Environment:** GPU compute, dataset access
**Verifier:** metrics improve over baseline, code reproducible, results valid
**Feedback loop:** hours-days (training runs, evaluation)

**Markets:** Vesuvius Challenge, Kaggle competitions, scientific computing bounties
**Training env:** Scientific world — given dataset + problem, build and evaluate pipeline
**Reusability:** MEDIUM — ML pipeline patterns transfer, domain-specific features don't

**Sub-schools:**
- F15a: Data pipeline (load, transform, validate)
- F15b: Model training (architecture, hyperparameters, regularization)
- F15c: Evaluation (metrics, ablation, statistical significance)
- F15d: Reproducibility (versioning, seeding, documentation)
- F15e: Optimization (speed, memory, distributed)
- F15f: Submission (format, documentation, results)

---

### F16. HR / CRM INTEGRATION
**What the agent literally does:** Study platform API → build connector → sync data → handle permissions → test edge cases → list
**Tools:** Platform REST API, OAuth, data mapping, conflict resolution
**Environment:** Sandbox/test account
**Verifier:** data syncs correctly, permissions respected, no duplicates, edge cases handled
**Feedback loop:** minutes-hours (API testing)

**Markets:** BambooHR, Personio, Greenhouse, Lever, Rippling, HiBob, Salesforce, HubSpot, Zoho, Pipedrive
**Training env:** CRM/HR world — given API docs, build reliable data sync
**Reusability:** HIGH — OAuth + CRUD + sync patterns transfer across all HR/CRM platforms

**Sub-schools:**
- F16a: OAuth + permission scoping
- F16b: Contact/employee sync
- F16c: Pipeline/deal tracking
- F16d: Reporting/metrics
- F16e: Multi-system reconciliation
- F16f: Compliance/audit trail

---

### F17. FINANCE / ACCOUNTING
**What the agent literally does:** Study accounting API → build integration → handle money carefully → reconcile → test with fixtures → list
**Tools:** Accounting API, ledger, reconciliation engine, audit logging
**Environment:** Sandbox/test company
**Verifier:** balances correct, transactions reconcile, audit trail complete, no data loss
**Feedback loop:** hours (need to verify financial accuracy)

**Markets:** Xero, QuickBooks, Sage, MYOB, Visma, Exact Online, FreshBooks, Fortnox, Zuora, Chargebee, NetSuite
**Training env:** Accounting world — given API + test company, build reliable integration
**Reusability:** HIGH — ledger, reconciliation, audit patterns transfer across accounting platforms

**Sub-schools:**
- F17a: Invoice creation + reconciliation
- F17b: Expense categorization
- F17c: Tax export
- F17d: Multi-entity consolidation
- F17e: Audit trail + compliance
- F17f: Migration (old system → new)

---

### F18. MARKETPLACE DISTRIBUTION
**What the agent literally does:** Package product → optimize listing → cross-list → monitor reviews → iterate
**Tools:** App store APIs, ASO tools, review monitoring, A/B testing
**Environment:** Multiple marketplace platforms
**Verifier:** listing live, reviews positive, installs/sales growing
**Feedback loop:** days-weeks (marketplace cycles are slow)

**Markets:** ALL marketplaces (this is the meta-skill of distributing TO marketplaces)
**Training env:** Distribution world — given product + marketplace list, optimize presence
**Reusability:** VERY HIGH — ASO, cross-listing, review management transfer everywhere

**Sub-schools:**
- F18a: Listing optimization (title, description, screenshots, tags)
- F18b: Cross-listing (same product → multiple marketplaces)
- F18c: Review monitoring + response
- F18d: Pricing optimization
- F18e: Update management (versioning, changelogs)
- F18f: Analytics + iteration

---

## The Key Insight

The 335 marketplaces map to **18 skill families**, and many of those families share sub-schools:

```
SHARED FOUNDATIONS:
├── OAuth/Authentication     → F3, F4, F16, F17 (SaaS, e-commerce, HR, finance)
├── CRUD + API integration   → F1, F3, F4, F16, F17 (API, SaaS, commerce, HR, finance)
├── Webhook handling         → F1, F3, F4, F13 (API, SaaS, commerce, automation)
├── Screenshot QA            → F2, F7, F12, F14 (extension, game, template, 3D)
├── Error handling/retry     → F1, F8, F13 (API, scraping, automation)
├── Marketplace listing      → F18 (meta-skill, serves ALL)
└── Structured output        → F9, F10, F15 (research, forecasting, scientific)

UNIQUE PER FAMILY:
├── F5: Luau + Studio MCP (Roblox only)
├── F6: Verse + Unreal MCP (Fortnite only)
├── F10: Proper scoring + calibration (forecasting only)
├── F11: Vulnerability analysis + patch (security only)
├── F14: 3D geometry + textures (creative only)
└── F15: ML pipeline + GPU (scientific only)
```

## The Training Priority Stack

Based on: markets served × verifier quality × training env availability × economic surface

| Priority | Family | Markets Served | Verifier | Training Env | Economic Surface |
|----------|--------|---------------|----------|-------------|-----------------|
| **1** | F1: API Endpoint | 15+ | Deterministic | API test fixture | Pay-per-call ($0.001-$0.10) |
| **2** | F9: Research/Analysis | 20+ | Sourced claims | Research world | Bounty $5-$250 |
| **3** | F13: Workflow Automation | 10+ | Deterministic | Automation world | Service $50-$500 |
| **4** | F5: Roblox Game Dev | 1 (but high value) | MCP + test | Studio MCP | DevEx revenue |
| **5** | F3: SaaS App | 20+ | OAuth + API test | SaaS integration world | Subscription MRR |
| **6** | F8: Web Scraping | 10+ | Data validation | Scraping world | Pay-per-call |
| **7** | F4: E-commerce Plugin | 18+ | Checkout test | Commerce world | App store revenue |
| **8** | F11: Security Patch | 5+ | Test suite | CVE world | $500-$15K per patch |
| **9** | F10: Forecasting | 3+ | Proper scoring | ForecastingWorld | Prize pools |
| **10** | F2: Browser Extension | 5+ | Browser test | Browser world | External billing |
| **11** | F18: Distribution | ALL | Sales metrics | Distribution world | Commission |
| **12** | F12: Template/Theme | 8+ | Screenshot QA | Template world | Product sales |
| **13** | F16: HR/CRM | 8+ | API sync test | CRM world | App revenue |
| **14** | F17: Finance | 10+ | Ledger reconciliation | Accounting world | App revenue |
| **15** | F15: Scientific | 3+ | Metrics + reproducibility | Scientific world | Prize pools |
| **16** | F6: Fortnite/UEFN | 1 (high value) | MCP + test | UEFN world | Engagement payouts |
| **17** | F7: Unity/Unreal | 3+ | Editor test | Engine world | Asset sales |
| **18** | F14: 3D/Creative | 10+ | Geometry validation | 3D world | Asset sales |

## The Bridge to WorkerKit/Moltwork

```
ORACLE (registry + scoring)
    │
    │ "market X needs skill_family Y, sub_school Z"
    │
    ▼
WORLD SELECTOR
    │
    │ "given the skill family, which Harbor world do we build?"
    │
    ▼
HARBOR (training)
    │
    │ School N → baseline trials → CGE experiments → domain verifier
    │
    ▼
WORKERKIT (execution)
    │
    │ WorkVenue.discover() → .inspect() → .submit() → .status()
    │
    ▼
ORACLE (feedback)
    │
    │ "worker succeeded at F1 API endpoint, transfers to F3 SaaS app"
    │ "skill_X improved forecast accuracy by 12% on held-out set"
    │
    ▼
COMPOUNDING: skills build on skills, markets unlock markets
```

The 18 families aren't 18 separate projects. They're **18 lenses on the same underlying capabilities**:
- OAuth + CRUD serves F1, F3, F4, F16, F17 (5 families, 70+ markets)
- Structured output serves F9, F10, F15 (3 families, 25+ markets)
- API + testing serves F1, F8, F13 (3 families, 35+ markets)
- Visual QA serves F2, F7, F12, F14 (4 families, 25+ markets)

**Build the shared foundations first, then each family is a thin specialization layer on top.**
