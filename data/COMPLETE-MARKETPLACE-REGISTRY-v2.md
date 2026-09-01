# Oracle — Master Marketplace Registry v2

**Generated:** 2026-08-31 (updated with 100 Gmail emails + R2 bucket data)
**Sources:** oracle repo adapters/marketplaces, 100 Gmail Oracle Market Unlocks + Agent Money Scout emails, R2 bucket (oracle-moltwork, agentlandscape, 402molt), ORACLE-UNLOCKS-2026-08-31.md

---

## Executive Summary

| Category | Total | Code Exists | Docs Only | From Gmail | Not Started |
|----------|------:|------------:|-----------:|-----------:|------------:|
| Creative / Digital Goods | 23 | 5 | 12 | 1 | 5 |
| Developer / SaaS Marketplaces | 67 | 0 | 0 | 67 | 0 |
| E-commerce / Merchant | 18 | 0 | 0 | 18 | 0 |
| Agent-Native / x402 | 111 | 20 | 0 | 91 | 0 |
| HR / Workforce | 8 | 0 | 0 | 8 | 0 |
| Travel / Hospitality | 4 | 0 | 0 | 4 | 0 |
| Cloud / Infra | 9 | 0 | 1 | 8 | 0 |
| Content / Creator | 25 | 0 | 0 | 25 | 0 |
| Gaming / UGC | 15 | 2 | 0 | 13 | 0 |
| Finance / Accounting | 12 | 0 | 0 | 12 | 0 |
| Integration / Automation | 14 | 0 | 0 | 14 | 0 |
| Browser / Extension | 4 | 0 | 0 | 4 | 0 |
| Enterprise / Industry | 35 | 0 | 0 | 35 | 0 |
| Training / Lab Targets | 6 | 0 | 0 | 6 | 0 |
| **TOTAL** | **351+** | **27** | **13** | **226+** | **5** |

---

## A. CREATIVE / DIGITAL GOODS MARKETPLACES

### With Code (5)

| # | Marketplace | Revenue | API | Code Location |
|---|-------------|---------|-----|---------------|
| 1 | **Roblox** | 100% net | Open Cloud + Studio MCP | `marketplaces/__init__.py` |
| 2 | **Gumroad** | 95%+ | REST API | `marketplaces/__init__.py` |
| 3 | **itch.io** | 90%+ | REST API | `marketplaces/__init__.py` + `marketplaces/itchio.md` |
| 4 | **Adobe Stock** | 33-35% | Contributor API | `marketplaces/__init__.py` + `marketplaces/adobe.md` |
| 5 | **x402 Bazaar** | 95% | x402 protocol | `marketplaces/__init__.py` + `marketplaces/x402-bazaar.md` |

### Docs Only (12)

| # | Marketplace | Revenue | API | Doc |
|---|-------------|---------|-----|-----|
| 6 | **Fab** | 88% | Web only | `marketplaces/fab.md` |
| 7 | **Unity Asset Store** | 70% | Publisher Portal | `marketplaces/unity.md` |
| 8 | **Canva** | Royalty pool | No public API | `marketplaces/canva.md` |
| 9 | **Figma** | N/A | Community API | `marketplaces/figma.md` |
| 10 | **Creative Market** | 60% | No public API | `marketplaces/creativemarket.md` |
| 11 | **Apple** | — | App Store Connect | `marketplaces/apple.md` |
| 12 | **Google Play** | — | Play Developer API | `marketplaces/googleplay.md` |
| 13 | **Discord** | — | Bot/Activity API | `marketplaces/discord.md` |
| 14 | **TikTok** | — | Developer API | `marketplaces/tiktok.md` |
| 15 | **Wix** | — | Partner API | `marketplaces/wix.md` |
| 16 | **YouTube** | — | YouTube Partner API | `marketplaces/youtube.md` |
| 17 | **AWS** | — | Marketplace API | `marketplaces/aws.md` |

### From Gmail (1)

| # | Marketplace | Revenue | Source | Notes |
|---|-------------|---------|--------|-------|
| 18 | **Framer** | 100% | Oracle Unlocks 31 Aug | Templates, $753k/mo creator payouts |

### Additional Discovered (5)

| # | Marketplace | Revenue | Source | Notes |
|---|-------------|---------|--------|-------|
| 19 | **Creative Fabrica** | Royalty | Oracle Unlocks Run 11 | Fonts, graphics, creator marketplace |
| 20 | **Second Life** | — | Oracle Unlocks Run 11 | Virtual marketplace, avatar items |
| 21 | **IMVU** | — | Oracle Unlocks Run 11 | Creator catalog, virtual goods |
| 22 | **Civitai** | — | Gmail | AI model marketplace |
| 23 | **MyMiniFactory** | Creator share | Gmail | 3D printing models |

---

## B. DEVELOPER / SAAS MARKETPLACES (67 total)

### From Oracle Unlocks — 31 Aug 2026 Report 1 (10)

| # | Marketplace | Score | H-Level | Revenue | API |
|---|-------------|------:|---------|---------|-----|
| 1 | **Atlassian Marketplace** | 9.3 | H1 | 100%→83% after $1M | Forge CLI + REST |
| 2 | **monday.com Marketplace** | 9.2 | H1-H2 | 85/15 after $200k | GraphQL + REST |
| 3 | **GitHub Marketplace** | 9.1 | H1 | Flat-rate/per-seat | GitHub Apps API |
| 4 | **Chrome Web Store** | 9.0 | H1 | External billing | Chrome Web Store API v2 |
| 5 | **Reddit Devvit** | 8.9 | H1 | Dev Funds up to $167k | Devvit platform |
| 6 | **Miro Marketplace** | 8.4 | H2 | Stripe/Salable | Web SDK, llms.txt |
| 7 | **WooCommerce Marketplace** | 8.3 | H2 | 70% vendor | WP extension API |
| 8 | **HubSpot App Marketplace** | 8.2 | H2 | External SaaS | Projects CLI, App Cards |
| 9 | **JetBrains Marketplace** | 8.1 | H1-H2 | Subscriptions | Plugin API |
| 10 | **Minecraft Marketplace** | 7.3 | H2-H3 | Partner revenue | Partner Program |

### From Oracle Unlocks — 1 Sep 2026 Report 2 (20)

| # | Marketplace | Score | H-Level | Revenue | API |
|---|-------------|------:|---------|---------|-----|
| 11 | **DigitalOcean Marketplace** | 24 | H1 | 75% vendor | REST + Vendor portal |
| 12 | **AppDirect/AppDistribution** | 24 | H1-H2 | Channel distribution | REST + GraphQL |
| 13 | **Vendasta Marketplace** | 23 | H1-H2 | White-label reseller | Marketplace APIs |
| 14 | **Visma App Store** | 23 | H1-H2 | Per-country sales | llms.txt + Developer Portal |
| 15 | **Travelport Marketplace** | 22 | H2 | Agency product sales | Universal API + Smartpoint |
| 16 | **SuiteCRM Store** | 22 | H1 | 70% vendor | License server + webhooks |
| 17 | **Plesk Extensions** | 22 | H1 | Paid/freemium | Extensions Catalog |
| 18 | **Personio Marketplace** | 22 | H2 | HR integration sales | REST API |
| 19 | **Creatio Marketplace** | 22 | H1-H2 | CRM app sales | Developer portal |
| 20 | **Keap Marketplace** | 22 | H1-H2 | Infusionsoft apps | REST API |
| 21 | **Exact Online App Center** | 21 | H2 | Accounting apps | REST API |
| 22 | **Sabre Red App Centre** | 21 | H2 | Travel agent tools | Red SDK |
| 23 | **SugarCRM Marketplace** | 21 | H1-H2 | CRM extensions | REST API |
| 24 | **Kintone Plug-in Marketplace** | 21 | H1-H2 | Business app plugins | Plug-in API |
| 25 | **Greenhouse Partner** | 21 | H2 | HRtech integrations | Partner API |
| 26 | **Lever Partner** | 21 | H2 | Recruiting integrations | Partner API |
| 27 | **BambooHR Marketplace** | 20 | H2 | HR integrations | REST API |
| 28 | **Mailchimp Integration Directory** | 20 | H1-H2 | Marketing integrations | Marketing API |
| 29 | **CloudBlue Connect** | 20 | H2 | Distribution ecosystem | Connect API |
| 30 | **Epic Showroom** | 19 | H3 | Unreal marketplace | Publisher portal |

### From Oracle Unlocks — 31 Aug 2026 Report 3 (18)

| # | Marketplace | Score | H-Level | Revenue | API |
|---|-------------|------:|---------|---------|-----|
| 31 | **ActiveCampaign App Marketplace** | 24 | H1 | Integration apps | MCP Server + REST |
| 32 | **Duda App Store** | 22 | H1 | White-label agency | Site APIs + App Store |
| 33 | **Walmart Marketplace App Store** | 22 | H1-H2 | Seller tools | OAuth 2.0 + SP-API |
| 34 | **SHOPLINE App Store** | 22 | H1 | B2B merchant apps | OAuth + REST/GraphQL |
| 35 | **Amazon Selling Partner Appstore** | 21 | H1-H2 | Seller tools (1M+) | SP-API + Appstore |
| 36 | **Asana App Directory** | 21 | H1 | Workflow utilities | llms.txt + OpenAPI |
| 37 | **Lightspeed eCom App Market** | 21 | H1 | Merchant integrations | REST API |
| 38 | **Leanpub Store** | 21 | H1-H2 | Technical books | Publish API |
| 39 | **Twitch Extensions** | 20 | H1-H2 | Bits monetization | Extensions API |
| 40 | **Zazzle Creator** | 20 | H1-H2 | Personalized products | Create-a-Product API |
| 41 | **Klaviyo App Marketplace** | 20 | H2 | Email marketing apps | REST API |
| 42 | **Sage Marketplace** | 20 | H2 | Accounting adapters | Sage API |
| 43 | **MYOB App Marketplace** | 20 | H2 | Business tools | API marketplace |
| 44 | **eBay Seller Ecosystem** | 19 | H2 | Niche storefronts | Sell APIs + MCP |
| 45 | **Ghost Theme Marketplace** | 19 | H2 | Publication themes | Ghost API |
| 46 | **Glide Template Store** | 18 | H2 | Operational app templates | Glide API |
| 47 | **ZEPETO Studio Items** | 17 | H2 | Fashion/accessory items | Studio API |
| 48 | **n8n Workflow Library** | 17 | H1-H2 | Workflow templates | n8n API |

### From Oracle Unlocks — 1 Sep 2026 Run 11 (20 new)

| # | Marketplace | Score | H-Level | Revenue | API |
|---|-------------|------:|---------|---------|-----|
| 49 | **Railway Template Marketplace** | 24 | H1 | 25% commission on deploys | Deploy API + OSS Partner |
| 50 | **Tiendanube/Nuvemshop App Store** | 24 | H1-H2 | App subscriptions | NubeSDK + REST |
| 51 | **Aircall App Marketplace** | 23 | H1-H2 | Contact-center apps | Developer API + MCP |
| 52 | **Paddle Apps Marketplace** | 23 | H1 | Billing/revenue apps | OAuth + Marketplace |
| 53 | **PointClickCare Marketplace** | 22 | H2 | Healthcare admin | Developer API |
| 54 | **FreshBooks App Store** | 22 | H1-H2 | Freelancer finance | REST API |
| 55 | **api0.app API Marketplace** | 22 | H1 | API-as-product | x402 protocol |
| 56 | **Mindbody Partner Store** | 21 | H2 | Fitness/wellness | Partner API |
| 57 | **Jumpseller App Store** | 21 | H1 | LATAM ecommerce | REST API |
| 58 | **Zuora Marketplace** | 21 | H2 | Subscription billing | REST API |
| 59 | **Simpro Marketplace** | 21 | H2 | Field service | Partner API |
| 60 | **Dialpad App Marketplace** | 21 | H1-H2 | Communications | Developer API |
| 61 | **Constant Contact Marketplace** | 20 | H1-H2 | Marketing apps | API |
| 62 | **Synology Package Center** | 20 | H2 | NAS utilities | Package API |
| 63 | **Merkado AI App Marketplace** | 20 | H1 | AI agent apps | API |
| 64 | **Cin7 ISV Partner Market** | 19 | H2 | Inventory/ecommerce | Partner API |
| 65 | **Second Life Marketplace** | 17 | H2 | Virtual goods | Creator API |
| 66 | **IMVU Creator Catalog** | 16 | H2 | Virtual fashion | Creator API |
| 67 | **Core Games Perks** | 15 | H2-H3 | Game economy | Perks API |

### Additional From Gmail (not in numbered reports)

| # | Marketplace | Source | Notes |
|---|-------------|--------|-------|
| 68 | **Zendesk Marketplace** | Gmail | Support apps |
| 69 | **Zoho Marketplace** | Gmail | Business apps |
| 70 | **Pipedrive Marketplace** | Gmail | Sales apps |
| 71 | **Foundry VTT Marketplace** | Gmail | Tabletop RPG |
| 72 | **QuickBooks App Marketplace** | Gmail | Accounting |
| 73 | **Intercom App Store** | Gmail | Messaging |
| 74 | **Freshworks Marketplace** | Gmail | Support/sales |
| 75 | **Autodesk Design and Make** | Gmail | 3D/CAD |
| 76 | **Grafana Marketplace** | Gmail | Observability |
| 77 | **Stripe App Marketplace** | Gmail | Payments |
| 78 | **Adobe Creative Cloud** | Gmail | Creative tools |
| 79 | **Microsoft AppSource** | Gmail | Enterprise |
| 80 | **Whop App Store** | Gmail | Digital products |
| 81 | **SketchUp Extension Warehouse** | Gmail | 3D design |
| 82 | **Adobe Commerce Marketplace** | Gmail | E-commerce |
| 83 | **Square App Marketplace** | Gmail | POS/payments |
| 84 | **Clover App Market** | Gmail | POS/payments |
| 85 | **Concrete CMS Marketplace** | Gmail | CMS |
| 86 | **WHMCS Marketplace** | Gmail | Hosting billing |
| 87 | **Statamic Marketplace** | Gmail | CMS |
| 88 | **October CMS Marketplace** | Gmail | CMS |
| 89 | **UiPath Marketplace** | Gmail | RPA |
| 90 | **Google Workspace Marketplace** | Gmail | Productivity |
| 91 | **Squarespace Extensions** | Gmail | Website builder |
| 92 | **Mendix Marketplace** | Gmail | Low-code |
| 93 | **Okta Integration Network** | Gmail | Identity |
| 94 | **WeWeb Marketplace** | Gmail | Web apps |
| 95 | **Procore App Marketplace** | Gmail | Construction |
| 96 | **ADP Marketplace** | Gmail | HR/payroll |
| 97 | **Trimble Marketplace** | Gmail | Construction |
| 98 | **ServiceTitan App Marketplace** | Gmail | Field service |
| 99 | **NetSuite SuiteApp.AI** | Gmail | ERP |
| 100 | **Genesys AppFoundry** | Gmail | Contact center |
| 101 | **VTEX App Store** | Gmail | E-commerce |
| 102 | **Mews Marketplace** | Gmail | Hospitality |
| 103 | **Samsara App Marketplace** | Gmail | Fleet/IoT |
| 104 | **Microsoft Security Store** | Gmail | Security |
| 105 | **Siemens Xcelerator** | Gmail | Industrial |
| 106 | **AppFolio Stack Marketplace** | Gmail | Property mgmt |
| 107 | **Geotab Marketplace** | Gmail | Fleet |
| 108 | **Motive App Marketplace** | Gmail | Fleet |
| 109 | **Boomi Marketplace** | Gmail | Integration |
| 110 | **Zyla API Hub** | Gmail | API marketplace |
| 111 | **DroneDeploy App Market** | Gmail | Drones/GIS |
| 112 | **QuickNode Marketplace** | Gmail | Blockchain |
| 113 | **AppHighway MCP Tool Marketplace** | Gmail | MCP tools |
| 114 | **Shoplazza App Store** | Gmail | E-commerce |
| 115 | **Bitrix24 Market** | Gmail | CRM |
| 116 | **Replit Extensions Store** | Gmail | Developer |
| 117 | **mod.io Marketplace** | Gmail | Game mods |
| 118 | **Fortnox Marketplace** | Gmail | Swedish accounting |
| 119 | **Gorgias App Store** | Gmail | E-commerce support |
| 120 | **Front App Store** | Gmail | Email |
| 121 | **Adalo Component Marketplace** | Gmail | No-code |
| 122 | **Crisp Marketplace** | Gmail | Chat |
| 123 | **Chargebee Marketplace** | Gmail | Billing |
| 124 | **Teamwork.com Integrations** | Gmail | Project mgmt |
| 125 | **Aircall App Marketplace** | Gmail | Phone |
| 126 | **Paddle Apps Marketplace** | Gmail | Billing |
| 127 | **PointClickCare Marketplace** | Gmail | Healthcare |
| 128 | **FreshBooks App Store** | Gmail | Accounting |
| 129 | **Setapp Marketplace** | Gmail | Mac apps |
| 130 | **Thinkific App Store** | Gmail | Courses |
| 131 | **Webasyst Store** | Gmail | Web apps |
| 132 | **BricsCAD Application Catalog** | Gmail | CAD |
| 133 | **Huawei AppGallery** | Gmail | Mobile |
| 134 | **XenForo Resource Manager** | Gmail | Forum add-ons |
| 135 | **D2L Brightspace IntegrationHub** | Gmail | Education |
| 136 | **Clio App Directory** | Gmail | Legal |
| 137 | **Cloudbeds Marketplace** | Gmail | Hospitality |
| 138 | **RingCentral App Gallery** | Gmail | Communications |
| 139 | **Talkdesk AppConnect** | Gmail | Contact center |
| 140 | **Five9 CX Marketplace** | Gmail | Contact center |
| 141 | **Kustomer App Marketplace** | Gmail | CRM |
| 142 | **NiCE CXexchange** | Gmail | Contact center |
| 143 | **Jobber App Marketplace** | Gmail | Field service |
| 144 | **Housecall Pro App Store** | Gmail | Field service |
| 145 | **Buildium Marketplace** | Gmail | Property mgmt |
| 146 | **RealPage Exchange** | Gmail | Property mgmt |
| 147 | **Lodgify Marketplace** | Gmail | Vacation rental |
| 148 | **Hostfully Integration Zone** | Gmail | Vacation rental |
| 149 | **Hostaway Marketplace** | Gmail | Vacation rental |
| 150 | **Toast Partner Ecosystem** | Gmail | Restaurant |
| 151 | **Workday Marketplace** | Gmail | HR/finance |
| 152 | **Infor Marketplace** | Gmail | Enterprise |
| 153 | **SAP Store** | Gmail | Enterprise |
| 154 | **Oracle Marketplace** | Gmail | Enterprise |
| 155 | **Appian AppMarket** | Gmail | Low-code |
| 156 | **Cisco Networking App Marketplace** | Gmail | Networking |
| 157 | **Jamf Marketplace** | Gmail | Apple MDM |
| 158 | **CrowdStrike Marketplace** | Gmail | Security |
| 159 | **Cortex XSOAR Marketplace** | Gmail | Security |
| 160 | **Coupa App Marketplace** | Gmail | Procurement |
| 161 | **Docusign App Center** | Gmail | E-signatures |
| 162 | **Dropbox App Center** | Gmail | Storage |
| 163 | **Box App Center** | Gmail | Enterprise storage |
| 164 | **Braze Partner Marketplace** | Gmail | Marketing |
| 165 | **Airtable Interface Extensions** | Gmail | Database |
| 166 | **Carrd Maker Program** | Gmail | Website builder |
| 167 | **DoliStore** | Gmail | ERP |
| 168 | **Frappe Cloud Marketplace** | Gmail | ERP |
| 169 | **Celigo integrator.io** | Gmail | Integration |
| 170 | **Acumatica Marketplace** | Gmail | ERP |
| 171 | **RingCentral App Gallery** | Gmail | Communications |
| 172 | **Lunchbox OPEN Integrations** | Gmail | Restaurant |

---

## C. E-COMMERCE / MERCHANT MARKETPLACES (18)

| # | Marketplace | Region | API | Source |
|---|-------------|--------|-----|--------|
| 1 | **Shopify App Store** | Global | Partner API + Order MCP | Gmail |
| 2 | **Shopify Theme Store** | Global | Theme API | Gmail |
| 3 | **WooCommerce** | Global | REST API | Oracle Unlocks |
| 4 | **BigCommerce** | Global | Stencil + API | Gmail |
| 5 | **Magento/Adobe Commerce** | Global | Marketplace API | Gmail |
| 6 | **PrestaShop Marketplace** | EU/Global | Addons API | Gmail |
| 7 | **Shopware Store** | EU | Store API | Gmail |
| 8 | **OpenCart Marketplace** | Global | Extension API | Gmail |
| 9 | **CS-Cart Marketplace** | Global | Marketplace API | Gmail |
| 10 | **Ecwid App Market** | Global | REST API | Gmail |
| 11 | **Walmart Marketplace** | US | SP-API (OAuth 2.0) | Oracle Unlocks |
| 12 | **Amazon Selling Partner** | Global | SP-API | Oracle Unlocks |
| 13 | **Etsy** | Global | Open API v3 + MCP | Gmail |
| 14 | **eBay** | Global | Sell APIs + MCP | Oracle Unlocks |
| 15 | **Tiendanube/Nuvemshop** | LATAM | NubeSDK + REST | Oracle Unlocks Run 11 |
| 16 | **Jumpseller** | LATAM | REST API | Oracle Unlocks Run 11 |
| 17 | **SHOPLINE** | Global | OAuth + REST/GraphQL | Oracle Unlocks |
| 18 | **Shoplazza** | Global | REST API | Gmail |

---

## D. AGENT-NATIVE / x402 MARKETPLACES (95 total)

### Wired into Oracle Feeds (20 active)

| # | Marketplace | Type | Protocol | Status |
|---|-------------|------|----------|--------|
| 1 | SuperTeam | Work bounties | Web scraping | Active |
| 2 | GitHub Issues | Bounties | GitHub API | Active |
| 3 | BountyBook | Work bounties | REST/MCP | Active |
| 4 | AgentHansa | Work bounties | Web | Active |
| 5 | Daydreams/Lucid | Task market | Web | Active |
| 6 | RentAHuman | Human tasks | MCP + REST | Active |
| 7 | NEAR AI Agent Market | Agent work | REST + OpenAPI | Active |
| 8 | OpenServ | Ideaboard | Web | Active |
| 9 | Apify | Services | Store API | Active |
| 10 | x402engine | x402 services | Web | Active |
| 11 | x402-list | x402 services | Web | Active |
| 12 | PayAPI Market | Pay-per-call | API | Active |
| 13 | the402 | x402 services | Web | Active |
| 14 | 402index | x402 index | Web | Active |
| 15 | Smithery | MCP servers | Registry | Active |
| 16 | MCP Registry | MCP servers | Registry | Active |
| 17 | OpenRouter | LLM models | API | Active |
| 18 | HuggingFace | ML models | API | Active |
| 19 | Bittensor | Compute | Subnet API | Active |
| 20 | Virtuals ACP | Agent economy | ACP protocol | Active |

### Adapter Exists, NOT Wired (7)

| # | Marketplace | File | Status |
|---|-------------|------|--------|
| 21 | TaskForce | `taskforce.py` | Not wired |
| 22 | AgentHire | `agenthire.py` | Not wired |
| 23 | Toll402 | `toll402.py` | Not wired |
| 24 | Coinbase Bazaar | `bazaar.py` | Not wired |
| 25 | Olas Network | `olas_adapter.py` | Not wired |
| 26 | gigs.sh | `gigs.py` | Not wired |
| 27 | Valoria | `valoria.py` | Not wired |

### From Agent Money Scout (verified economics)

| # | Marketplace | URL | Verified Volume | H-Level | Source |
|---|-------------|-----|----------------|---------|--------|
| 28 | AgentPact | agentpact.xyz | 200 Needs, $5-25/ea | H0 | Money Scout |
| 29 | dealwork.ai | dealwork.ai | 2.5K workers, 264 completed | H0 | Money Scout |
| 30 | OpenAnt | openant.ai | $34.4K paid, 646 settled | H0 | Money Scout |
| 31 | WorkProtocol | workprotocol.ai | 1,325 USDC settled | H0 | Money Scout |
| 32 | ClawHunt | clawhunt.store | 75% payout, escrow | H0 | Money Scout |
| 33 | MoltMarket | moltbotmarket.com | $5+ bounties, 95% (unproven) | H0 | Money Scout |
| 34 | req402 | req402.com | $0.002/req, 120K requests | H0 | Money Scout |
| 35 | A2A Colony | a2acolony.com | 126 skills, £9.99-10/use | H0 | Money Scout |
| 36 | HYRVE AI | github.com/ertugrulakben | 85% creator share | H0 | Money Scout |
| 37 | Magneto | magnetoapp.io | Deployable agents/skills | H0 | Money Scout |
| 38 | tools402 | docs.tools402.dev | Self-custodial, multi-chain | H0 | Money Scout |
| 39 | Agentic Swarm | agentic-swarm-marketplace.com | x402 XRPL/Base/Celo | H0 | Money Scout |
| 40 | agentsbay.ai | agentsbay.ai | 774 jobs, $1.5K escrow | H0 | Money Scout |
| 41 | Agent Wonderland | agentwonderland.com | 15% fee, Stripe Connect | H0 | Money Scout |
| 42 | AgentJob | agent-job.ai | 10K+ agents, per-message | H0 | Money Scout |
| 43 | DeskCrew | deskcrew.io | 85% share, USDC | H0 | Money Scout |
| 44 | x402 Arena | x402arena.gg | 339 agents, $109 total | H0 | Money Scout |
| 45 | Agent402 | agent402.tools | 5,727 payments, $80 total | H0 | Money Scout |
| 46 | Agent Bounties | agentbounties.app | 1 USDC bounties, Base | H0 | Money Scout |
| 47 | AgentLancer | agentlancer.io | Zero verified earnings | H0 | Money Scout |
| 48 | Molty Cash | synthesis.mandate.md | x402 gigs on Base | H0 | Money Scout |
| 49 | Execution Market | agent-tools.cloud | A2A agent tasks | H0 | Money Scout |
| 50 | AiScale | agent-tools.cloud | Per-request intelligence | H0 | Money Scout |
| 51 | AgentDataHub | agent-tools.cloud | 150+ x402 endpoints | H0 | Money Scout |
| 52 | AgentReader | agent-tools.cloud | 11 paid HTTP endpoints | H0 | Money Scout |
| 53 | Skill-audit | agent-tools.cloud | Security scanning | H0 | Money Scout |
| 54 | APIMesh | agent-tools.cloud | Tiny paid APIs | H0 | Money Scout |
| 55 | ToolTrust/Smithery | tooltrust.dev | Paid MCP discovery | H0 | Money Scout |
| 56 | Complete Codes | complete.codes | Funded GitHub sprints | H0 | Money Scout |
| 57 | Toku.agency | toku.agency | 130+ jobs, $5-25, Stripe | H0 | Money Scout |
| 58 | OpenJobs | openjobs.bot | USDC/WAGE jobs | H0 | Money Scout |
| 59 | Opire | app.opire.dev | GitHub bounties | H0 | Money Scout |
| 60 | TaskBounty | taskbounty | USDC bounties | H0 | Money Scout |

### Still Active from Prior Runs

| # | Marketplace | Status |
|---|-------------|--------|
| 61 | SporeAgent | Active but zero open tasks |
| 62 | Clawlancer | Active task market |
| 63 | MoltJobs | Active, concrete funded jobs |
| 64 | Mercatai | Active |
| 65 | AgentGigs | Active |
| 66 | ClawGig | Active |
| 67 | ClawFreelance | Active |
| 68 | AgentBazaar | Passive capability-sale |
| 69 | AgentPay Store | Passive capability-sale |
| 70 | PayanAgent | Passive capability-sale (24K+ x402 services) |
| 71 | Agoragentic | Passive capability-sale |
| 72 | Atelier | Passive capability-sale |

### Additional Discovered

| # | Marketplace | Source | Notes |
|---|-------------|--------|-------|
| 73 | AgentCab | Gmail | Agent marketplace |
| 74 | AgentGrind.fun | Gmail | Agent marketplace |
| 75 | AgentMP | Gmail | Agent marketplace |
| 76 | AgentMart | Gmail | Agent marketplace |
| 77 | AgentSwarmWork | Gmail | Agent marketplace |
| 78 | AgentWorld | Gmail | Agent marketplace |
| 79 | AgenticEra | Gmail | Agent marketplace |
| 80 | AgenticInvictus | Gmail | Agent marketplace |
| 81 | AgenticTrade | Gmail | Agent marketplace |
| 82 | Agora402 | Gmail | x402 marketplace |
| 83 | AiPayGen | Gmail | Agent marketplace |
| 84 | Amnt | Gmail | Agent marketplace |
| 85 | AnyTasks | Gmail | Task marketplace |
| 86 | Atrium | Gmail | Agent marketplace |
| 87 | AuraGate | Gmail | Agent marketplace |
| 88 | BNB Agent Studio v2 | Gmail | BNB chain |
| 89 | BTNOMB Bounty Board | Gmail | Bounty board |
| 90 | BotBounty | Gmail | Bot marketplace |
| 91 | BotBounty.ai | Gmail | Bot marketplace |
| 92 | BotGuild | Gmail | Bot marketplace |
| 93 | BotHire | Gmail | Bot marketplace |
| 94 | BotWork | Gmail | Bot marketplace |
| 95 | Bounty Bureau | Gmail | Bounty board |
| 96 | BountyOS | Gmail | Bounty system |
| 97 | CLAWORK | Gmail | Agent marketplace |
| 98 | Claw Earn | Gmail | Agent marketplace |
| 99 | Claw Jobs | Gmail | Agent marketplace |
| 100 | ClawTasks | Gmail | Agent marketplace |
| 101 | ClawdGigs | Gmail | Agent marketplace |
| 102 | Clawget | Gmail | Agent marketplace |
| 103 | Cliver | Gmail | Agent marketplace |
| 104 | Code Bounty | Gmail | Code bounties |
| 105 | CrewHub | Gmail | Agent marketplace |
| 106 | CrewPort | Gmail | Agent marketplace |
| 107 | Drips Waves | Gmail | Agent marketplace |
| 108 | EXVIV x402 Radar | Gmail | x402 intelligence |
| 109 | Emerging Tech Center | Gmail | Agent gigs |
| 110 | FiatDock | Gmail | Agent marketplace |
| 111 | FlowRuns | Gmail | Agent marketplace |
| 112 | GetAgentic | Gmail | Agent marketplace |
| 113 | GitGig | Gmail | Git bounties |
| 114 | GitProduct | Gmail | Git marketplace |
| 115 | Go Agents Go | Gmail | Agent marketplace |
| 116 | Graded.sh | Gmail | Agent marketplace |
| 117 | Graph Hacks | Gmail | Hack marketplace |
| 118 | HackenProof | Gmail | Security bounties |
| 119 | HireAIStaffs | Gmail | Agent marketplace |
| 120 | Hudle | Gmail | Agent marketplace |
| 121 | HumanPing | Gmail | Human-in-the-loop |
| 122 | IndieHash | Gmail | Indie marketplace |
| 123 | IssueHunt | Gmail | Issue bounties |
| 124 | KONIO | Gmail | Agent marketplace |
| 125 | Laguna Network MCP | Gmail | MCP marketplace |
| 126 | MCPize | Gmail | MCP marketplace |
| 127 | MOLTIFY | Gmail | Agent marketplace |
| 128 | MindAgents | Gmail | Agent marketplace |
| 129 | Molt4Hire | Gmail | Agent marketplace |
| 130 | Molted | Gmail | Agent marketplace |
| 131 | Molted.work | Gmail | Agent marketplace |
| 132 | Moltify | Gmail | Agent marketplace |
| 133 | Moltjiji | Gmail | Agent marketplace |
| 134 | MoltyBounty | Gmail | Agent marketplace |
| 135 | Morpheus Protocol | Gmail | Agent marketplace |
| 136 | OKX AI | Gmail | OKX chain |
| 137 | OpenPod | Gmail | Agent marketplace |
| 138 | OpenTask | Gmail | Task marketplace |
| 139 | PayTheAgent.ai | Gmail | Agent marketplace |
| 140 | Project Hunter | Gmail | Agent marketplace |
| 141 | QuestBoard | Gmail | Quest marketplace |
| 142 | RevolutionAI | Gmail | Agent marketplace |
| 143 | Runaway | Gmail | Agent marketplace |
| 144 | SeekClaw | Gmail | Agent marketplace |
| 145 | SLIX.work | Gmail | Agent marketplace |
| 146 | SoraJobs | Gmail | Agent marketplace |
| 147 | Stacker News | Gmail | Bounty/rewards |
| 148 | SYNMERCO | Gmail | Agent marketplace |
| 149 | T2000 | Gmail | Agent marketplace |
| 150 | Taskmarket | Gmail | Task marketplace |
| 151 | Tetto | Gmail | Agent marketplace |
| 152 | The Colony | Gmail | Agent marketplace |
| 153 | Tollbooth | Gmail | x402 marketplace |
| 154 | true402 | Gmail | x402 marketplace |
| 155 | uGig | Gmail | Gig marketplace |
| 156 | workpnp | Gmail | Agent marketplace |
| 157 | Zentience marketplace | Gmail | Agent marketplace |
| 158 | boss.dev | Gmail | Developer marketplace |
| 159 | pay.sh | Gmail | Payment rail |
| 160 | 402.rest | Gmail | x402 marketplace |
| 161 | 0xWork | Gmail | Agent marketplace |
| 162 | Atelier x402 | Gmail | x402 marketplace |
| 163 | PROXIES.SX | Gmail | Service marketplace |
| 164 | Telegram Mini Apps | Gmail | Mini app marketplace |
| 165 | WordPress MCP | Gmail | MCP marketplace |
| 166 | Discord Premium Apps | Gmail | Discord marketplace |

---

## E. HR / WORKFORCE MARKETPLACES (8)

| # | Marketplace | Score | H-Level | API | Source |
|---|-------------|------:|---------|-----|--------|
| 1 | BambooHR Marketplace | 20 | H2 | REST API | Oracle Unlocks |
| 2 | Personio Marketplace | 22 | H2 | REST API | Oracle Unlocks |
| 3 | Greenhouse Partner | 21 | H2 | Partner API | Oracle Unlocks |
| 4 | Lever Partner | 21 | H2 | Partner API | Oracle Unlocks |
| 5 | Rippling App Shop | — | H2 | Platform API | Gmail |
| 6 | HiBob Marketplace | — | H2 | REST API | Gmail |
| 7 | ADP Marketplace | — | H2 | Partner API | Gmail |
| 8 | Workday Marketplace | — | H2 | Partner API | Gmail |

---

## F. TRAVEL / HOSPITALITY MARKETPLACES (4)

| # | Marketplace | Score | H-Level | API | Source |
|---|-------------|------:|---------|-----|--------|
| 1 | Travelport Marketplace | 22 | H2 | Universal API + Smartpoint | Oracle Unlocks |
| 2 | Sabre Red App Centre | 21 | H2 | Red SDK | Oracle Unlocks |
| 3 | Guesty Marketplace | — | H2 | PMS API | Gmail |
| 4 | Mews Marketplace | — | H2 | PMS API | Gmail |

---

## G. CLOUD / INFRASTRUCTURE MARKETPLACES (9)

| # | Marketplace | Revenue | API | Source |
|---|-------------|---------|-----|--------|
| 1 | DigitalOcean Marketplace | 75% vendor | REST + Vendor portal | Oracle Unlocks |
| 2 | AWS Marketplace | — | Marketplace API | Gmail |
| 3 | Heroku Add-ons | — | Add-ons API | Gmail |
| 4 | Railway Templates | 25% commission | Deploy API | Oracle Unlocks Run 11 |
| 5 | Plesk Extensions | — | Extensions Catalog | Oracle Unlocks |
| 6 | QNAP App Center | — | Package API | Gmail |
| 7 | Synology Package Center | — | Package API | Oracle Unlocks Run 11 |
| 8 | Google Cloud Marketplace | — | API | Gmail |
| 9 | QuickNode Marketplace | — | API | Gmail |

---

## H. CONTENT / CREATOR MARKETPLACES (25)

| # | Marketplace | Revenue | API | Source |
|---|-------------|---------|-----|--------|
| 1 | Envato Market | Author earnings | Author API | Gmail |
| 2 | Placeit | 20% net revenue | Template upload | Gmail |
| 3 | Creative Fabrica | Royalty | Designer API | Oracle Unlocks Run 11 |
| 4 | TurboSquid | Artist share | Publisher API | Gmail |
| 5 | CGTrader | Artist share | API | Gmail |
| 6 | RenderHub | Artist share | — | Gmail |
| 7 | Cubebrush | Artist share | — | Gmail |
| 8 | Pond5 | Artist share | API | Gmail |
| 9 | ArtStation | Artist share | — | Gmail |
| 10 | MyMiniFactory | Creator share | — | Gmail |
| 11 | Cults3D | Creator share | — | Gmail |
| 12 | Thangs | Creator share | API | Gmail |
| 13 | Redbubble | Artist share | API | Gmail |
| 14 | Displate | Artist share | — | Gmail |
| 15 | Threadless | Artist share | — | Gmail |
| 16 | Spoonflower | Designer share | API | Gmail |
| 17 | Freepik Contributor | Contributor share | API | Gmail |
| 18 | Shutterstock Contributor | Contributor share | API | Gmail |
| 19 | Vecteezy | Contributor share | API | Gmail |
| 20 | IconScout | Contributor share | API + licensing | Gmail |
| 21 | MotionElements | Creator share | — | Gmail |
| 22 | Storyblocks | Contributor share | — | Gmail |
| 23 | Fontspring | Foundry share | — | Gmail |
| 24 | MyFonts | Designer share | — | Gmail |
| 25 | DAZ 3D | Artist share | — | Gmail |

---

## I. GAMING / UGC MARKETPLACES (15)

| # | Marketplace | Revenue | API | Source |
|---|-------------|---------|-----|--------|
| 1 | Roblox | 100% net | Open Cloud + Studio MCP | Code |
| 2 | Fortnite/UEFN | 100% V-Bucks (2026) | Verse + UEFN MCP | Gmail |
| 3 | Minecraft Marketplace | Partner revenue | Partner Program | Oracle Unlocks |
| 4 | Unity Asset Store | 70% | Publisher Portal | Docs |
| 5 | Fab | 88% | Web only | Docs |
| 6 | itch.io | 90%+ | REST API | Code |
| 7 | Galaxy Store | — | Seller API | Gmail |
| 8 | CurseForge | — | API | Gmail |
| 9 | Modrinth | — | API | Gmail |
| 10 | Nexus Mods | — | API | Gmail |
| 11 | Foundry VTT | — | API | Gmail |
| 12 | Roll20 | — | API | Gmail |
| 13 | Fantasy Grounds Forge | — | — | Gmail |
| 14 | GmodStore | — | — | Gmail |
| 15 | Dota 2 Item Workshop | — | Steam API | Gmail |
| 16 | Core Games Perks | — | Perks API | Oracle Unlocks Run 11 |
| 17 | Second Life Marketplace | — | Creator API | Oracle Unlocks Run 11 |
| 18 | IMVU Creator Catalog | — | Creator API | Oracle Unlocks Run 11 |
| 19 | VRChat Avatar Marketplace | — | Creator Economy | Gmail |
| 20 | War Thunder Revenue Share | — | — | Gmail |
| 21 | Warframe TennoGen | — | — | Gmail |
| 22 | The Sims 4 Maker Marketplace | — | — | Gmail |
| 23 | Construct Asset Store | — | — | Gmail |
| 24 | GameDev Market | — | — | Gmail |
| 25 | SpigotMC Premium Resources | — | — | Gmail |
| 26 | Polymart | — | — | Gmail |
| 27 | Food4Rhino | — | — | Gmail |
| 28 | BeatStars Marketplace | — | — | Gmail |
| 29 | Overwolf Appstore | — | — | Gmail |
| 30 | Elgato Stream Deck Marketplace | — | — | Gmail |
| 31 | BuiltByBit Hytale | — | — | Gmail |
| 32 | Superhive (Blender Market) | — | — | Gmail |
| 33 | TensorArt | — | — | Gmail |
| 34 | Patreon Shops | — | — | Gmail |
| 35 | Printables Store/Clubs | — | — | Gmail |

---

## J. FINANCE / ACCOUNTING MARKETPLACES (12)

| # | Marketplace | Score | H-Level | API | Source |
|---|-------------|------:|---------|-----|--------|
| 1 | Visma App Store | 23 | H1-H2 | llms.txt + Developer Portal | Oracle Unlocks |
| 2 | SuiteCRM Store | 22 | H1 | License server + webhooks | Oracle Unlocks |
| 3 | Exact Online App Center | 21 | H2 | REST API | Oracle Unlocks |
| 4 | Sage Marketplace | 20 | H2 | Sage API | Oracle Unlocks |
| 5 | MYOB App Marketplace | 20 | H2 | API marketplace | Oracle Unlocks |
| 6 | Xero App Store | — | H2 | Xero API | Gmail |
| 7 | QuickBooks App Marketplace | — | H2 | Intuit API | Gmail |
| 8 | FreshBooks App Store | 22 | H1-H2 | REST API | Oracle Unlocks Run 11 |
| 9 | Fortnox Marketplace | — | H2 | API | Gmail |
| 10 | Zuora Marketplace | 21 | H2 | REST API | Oracle Unlocks Run 11 |
| 11 | Chargebee Marketplace | — | H2 | API | Gmail |
| 12 | DoliStore | — | H2 | API | Gmail |

---

## K. INTEGRATION / AUTOMATION MARKETPLACES (14)

| # | Marketplace | Revenue | API | Source |
|---|-------------|---------|-----|--------|
| 1 | Zapier MCP | — | MCP + 9K apps, 40K actions | Gmail |
| 2 | ActiveCampaign | Integration apps | MCP Server + REST | Oracle Unlocks |
| 3 | HubSpot | External SaaS | Projects CLI + App Cards | Oracle Unlocks |
| 4 | Mailchimp | Marketing integrations | Marketing API | Oracle Unlocks |
| 5 | Klaviyo | Email marketing apps | REST API | Oracle Unlocks |
| 6 | Make (Integromat) | — | API | Gmail |
| 7 | n8n | Workflow templates | API | Oracle Unlocks |
| 8 | Boomi Marketplace | — | API | Gmail |
| 9 | Celigo integrator.io | — | API | Gmail |
| 10 | Mendix Marketplace | — | API | Gmail |
| 11 | Appian AppMarket | — | API | Gmail |
| 12 | UiPath Marketplace | — | API | Gmail |
| 13 | Constant Contact Marketplace | — | API | Oracle Unlocks Run 11 |
| 14 | Braze Partner Marketplace | — | API | Gmail |

---

## L. BROWSER / EXTENSION MARKETPLACES (4)

| # | Marketplace | Revenue | API | Source |
|---|-------------|---------|-----|--------|
| 1 | Chrome Web Store | External billing | Chrome Web Store API v2 | Oracle Unlocks |
| 2 | Firefox Add-ons | — | AMO API | Gmail |
| 3 | Edge Add-ons | — | Partner Center API | Gmail |
| 4 | Obsidian Community | — | Plugin API | Gmail |

---

## M. ENTERPRISE / INDUSTRY MARKETPLACES (35)

| # | Marketplace | Industry | Source |
|---|-------------|----------|--------|
| 1 | Salesforce AppExchange | CRM | Gmail |
| 2 | ServiceNow Store | ITSM | Gmail |
| 3 | Zoho Marketplace | Business | Gmail |
| 4 | Pipedrive Marketplace | Sales | Gmail |
| 5 | Freshworks Marketplace | Support | Gmail |
| 6 | Zendesk Marketplace | Support | Gmail |
| 7 | Intercom App Store | Messaging | Gmail |
| 8 | Asana App Directory | Project mgmt | Oracle Unlocks |
| 9 | monday.com Marketplace | Operations | Oracle Unlocks |
| 10 | Atlassian Marketplace | Dev tools | Oracle Unlocks |
| 11 | Duda App Store | Agency | Oracle Unlocks |
| 12 | SHOPLINE App Store | E-commerce | Oracle Unlocks |
| 13 | Lightspeed eCom | POS/E-commerce | Oracle Unlocks |
| 14 | Bitrix24 Market | CRM | Gmail |
| 15 | Microsoft AppSource | Enterprise | Gmail |
| 16 | Google Workspace Marketplace | Productivity | Gmail |
| 17 | SAP Store | Enterprise | Gmail |
| 18 | Oracle Marketplace | Enterprise | Gmail |
| 19 | Infor Marketplace | Enterprise | Gmail |
| 20 | Cisco Networking App Marketplace | Networking | Gmail |
| 21 | Jamf Marketplace | Apple MDM | Gmail |
| 22 | CrowdStrike Marketplace | Security | Gmail |
| 23 | Cortex XSOAR Marketplace | Security | Gmail |
| 24 | Coupa App Marketplace | Procurement | Gmail |
| 25 | Docusign App Center | E-signatures | Gmail |
| 26 | Dropbox App Center | Storage | Gmail |
| 27 | Box App Center | Enterprise storage | Gmail |
| 28 | Airtable Interface Extensions | Database | Gmail |
| 29 | Siemens Xcelerator | Industrial | Gmail |
| 30 | Samsara App Marketplace | Fleet/IoT | Gmail |
| 31 | Microsoft Security Store | Security | Gmail |
| 32 | Procore App Marketplace | Construction | Gmail |
| 33 | NetSuite SuiteApp.AI | ERP | Gmail |
| 34 | Genesys AppFoundry | Contact center | Gmail |
| 35 | VTEX App Store | E-commerce | Gmail |

---

## N. TRAINING / LAB TARGETS — From R2 `oracle-moltwork`

Markets with **machine-readable training signals** — where the agent can measure improvement objectively.

### Priority Ranking

| # | Market | Training Signal | H-Level | Economic Value | Evaluator Kind | Primary Metric |
|---|--------|----------------|---------|----------------|----------------|----------------|
| 1 | **Metaculus forecasting** | Excellent | H0 + bootstrap | 10/10 | delayed_resolution | tournament_score |
| 2 | **Roblox micro-studio** | Very good | H0-ish + bootstrap | 9.5/10 | production_telemetry | retained_player_value |
| 3 | **OSS security patches** | Excellent | H0 work / H2 claim | 9/10 | hidden_regression | patch_acceptance |
| 4 | **Vesuvius progress prizes** | Excellent | H0 work / H2 submit | 8.5/10 | heldout_scientific | domain-specific |
| 5 | **TCG AI (Pokémon/YGO)** | Exceptional | H0 (simulator) | 8.5/10 | episodic_simulator | meta_win_rate |
| 6 | **Fortnite UEFN** | Good | H0 build / H2 publish | 8/10 | production_telemetry | retained_player_value |

---

### N1. Metaculus — Cleanest Moltwork Job on Earth

**Program:** Summer FutureEval tournament (closes Sep 6, 2026, $50K prize pool, 328 questions)
**Recurring:** ~$1K MiniBench rounds every 2 weeks, 300-500 questions per seasonal tournament
**API:** `POST /api/questions/forecast/` — official bot template exists
**H-Level:** H0 after one-time account/token/tournament bootstrap
**Training value:** exceptional — proper scoring rules give objective improvement signal

**Venue:** `MetaculusVenue` — discover → inspect → forecast → POST → status → score → Hydra
**World:** `ForecastingWorld` — binary, numeric, multiple_choice, conditional, sequential_update scenarios
**Verifier:** proper_forecast_score - malformed_penalty - excessive_compute_penalty + calibration_error + Brier/log_score

**Skills to accumulate:**
- forecast-resolution-parsing
- reference-class-selection
- base-rate-estimation
- numeric-tail-calibration
- evidence-independence-check
- source-timestamp-check
- forecast-aggregation
- disagreement-crux-search

**API docs:** https://github.com/Metaculus/metac-bot-template
**Source:** https://www.metaculus.com/tournament/summer-futureeval-2026/

---

### N2. Roblox — Shockingly Agent-Native Micro-Studio

**Program:** Creator economy (DevEx monetization, engagement payouts)
**API:** Studio MCP + Open Cloud REST + Place Publishing API + StudioTestService
**H-Level:** H0-compatible once creator account + API credentials + experience shell exist
**Training value:** very good — progressive curriculum with deterministic tests

**Venue:** `RobloxVenue` — code/build → playtest → multiplayer test → publish → monitor → iterate
**World:** `RobloxStudioWorld` — 6-school curriculum:
- School 0: atomic Luau mechanics (door, inventory, checkpoint, currency, shop, NPC, quest, leaderboard)
- School 1: microgames (4-player arena, score, respawn, mobile)
- School 2: UI/onboarding (VirtualInput simulation)
- School 3: adversarial multiplayer (disconnect, late join, spam, bad network)
- School 4: economy design (100K synthetic player-days)
- School 5: live experiment (A/B deployment, real telemetry)

**Execution steps:**
```text
code/build       MCP                 H0
playtest         Studio APIs/MCP     H0
multiplayer test StudioTestService   H0
device testing   Studio APIs         H0
publish update   REST API            H0*
monitor          Open Cloud          H0
iterate          WorkerKit           H0
```

**Skills to accumulate:**
- roblox-round-loop, roblox-datastore-safe, roblox-mobile-ui
- roblox-obby-movement, roblox-matchmaking, roblox-shop-economy
- roblox-multiplayer-race-condition-testing

**API docs:** https://create.roblox.com/docs/ai/accelerated-workflows
**Source:** https://create.roblox.com/docs/cloud

---

### N3. OSS Security Patches — Superb Harbor Task Family

**Program:** Google Patch Rewards (up to $500 / $2K / $7.5K / $15K, 2× memory-safety, 3× core parser through end 2026)
**H-Level:** H0 work / H2 external security claim
**Training value:** excellent — hidden regression tests give objective pass/fail

**Venue:** `GoogleOSSPatchVenue` — discover → clone → investigate → patch → test → PR → respond to CI
**World:** `OSSSecurityPatchWorld` — curriculum:
- known bug + obvious failing test
- known CVE + hidden test
- vulnerable commit without location
- generic hardening opportunity
- write fuzz harness → find crash → root cause → patch → regression test

**Verifier gates:**
```text
G0 compiles
G1 old tests pass
G2 hidden vulnerability reproduction no longer succeeds
G3 hidden variants fixed
G4 sanitizers clean
G5 no verifier/test tampering
G6 patch is reasonably minimal
```

**Skills to accumulate:**
- cpp-parser-hardening, rust-memory-safety-migration, integer-overflow-audit
- path-traversal-review, unsafe-deserialization-audit
- libfuzzer-harness-authoring, sanitizer-debugging, patch-regression-design

**Source:** https://bughunters.google.com/open-source-security/patch-rewards

---

### N4. Vesuvius — Scientific Contributions with Monthly Progress Economy

**Program:** $2.14M open ($1M 2027 Grand Prize, $500K First Letters, $590K/yr progress prizes including $20K/month for best OSS contribution)
**H-Level:** H0 research loop / H2 prize submission
**Training value:** excellent for technical subproblems

**Venue:** `VesuviusVenue` — discover → work → submit form/email → status → human review
**World:** 4 schools:
- `science.vesuvius.surface` — CT volume → surface/mesh (verifier: continuity, topology, intersections)
- `science.vesuvius.flatten` — 3D mesh → 2D mapping (verifier: distortion, fiber continuity)
- `science.vesuvius.ink` — CT surfaces → ink probability map (verifier: held-out labels, precision/recall)
- `science.vesuvius.tooling` — faster IO, Zarr tooling, dataset indexing, GPU optimization (start here)

**Compute:** streaming Zarr access, small local fixtures, remote GPU for real experiments

**Source:** https://vesuviuschallenge.org/

---

### N5. TCG AI — Best Pure Agent School

**Program:** Kaggle competitions (Pokémon TCG AI Battle Challenge — Simulation track locked Aug 16, Strategy track until Sep 13)
**H-Level:** H0 simulator / H3-H4 real human tournaments
**Training value:** exceptional — game engine gives logs, board state, legal actions

**Venue:** `KaggleVenue` — submit tournament-defined bundle via CLI/MCP
**World:** `YGOHarborWorld` — two agents:
- **Scientist worker** (Letta/Moltwork): develops game-playing policy using LLMs, experiments, Git, memory
- **Match policy**: submitted/evaluated program under simulator constraints

**Micro-worlds for dense training:**
- ygo.lethal_detection, ygo.interruption_timing, ygo.resource_preservation
- ygo.combo_selection, ygo.go_first, ygo.go_second
- ygo.side_deck, ygo.opponent_archetype_identification

**League training population:**
- frozen_baseline_v1, heuristic_control, historical_best_001/002
- aggressive_policy, control_policy, current_meta_A/B

**Scoring:** 0.45 weighted meta win rate, 0.20 frozen-baseline, 0.15 held-out robustness, 0.10 exploitability, 0.05 runtime, 0.05 legality

**Replace:** fake YGO World → `sbl1996/ygo-agent` (ygoenv + ygopro-core + Gym interface)

**Source:** https://github.com/sbl1996/ygo-agent

---

### N6. Fortnite/UEFN — Fantastic Build, Weaker Deploy

**Program:** Creator economy (engagement payouts, 100% V-Bucks incentive through 2026)
**API:** Unreal MCP server (UEFN v42, Aug 20, 2026) + Creator Portal
**H-Level:** H0 build / H2 publish (Creator Portal required, no official publishing API)
**Training value:** good — Unreal MCP enables full build/test cycle

**Venue:** `EpicFortniteVenue` — write Verse → compile → edit scene → place devices → build UI → test → PUBLISH REQUIRES HUMAN
**World:** `UEFNMicrogameWorld` — same curriculum as Roblox but Verse/C++ based

**Execution steps:**
```text
BUILD       official MCP       H0
TEST        UEFN              H0-ish
PUBLISH     Creator Portal    H2  ← human boundary
MODERATION  external          external
```

**Source:** https://dev.epicgames.com/documentation/fortnite/42-00-fortnite-ecosystem-updates-and-release-notes

---

## N7. Hackathons & Prize Competitions (from Agent Money Scout)

| # | Competition | Prize | Deadline | H-Level | Source |
|---|-------------|-------|----------|---------|--------|
| 1 | **Metaculus Summer FutureEval** | $50K | Sep 6, 2026 | H0 | oracle-moltwork |
| 2 | **Anakin Forge Hackathon** | $1K+ | Sep 7-14, 2026 | H0 | Money Scout |
| 3 | **Agents for Humans (Devpost)** | $40K | Sep 14, 2026 | H0 | Money Scout |
| 4 | **Vesuvius Progress Prizes** | $20K/month ongoing | Rolling | H0/H2 | oracle-moltwork |
| 5 | **Google Patch Rewards** | $500-$15K | Rolling | H0/H2 | oracle-moltwork |
| 6 | **Pokémon TCG AI (Kaggle)** | Varies | Strategy: Sep 13 | H0 (sim) | oracle-moltwork |

---

## N8. EarningProgram Schema (from oracle-moltwork)

New dataclass needed for markets with recurring program structure:

```python
@dataclass
class EarningProgram:
    id: str
    venue: str
    title: str
    reward_model: str           # "prize_pool", "per_use", "commission", "progress_prize"
    recurring: bool
    eligibility: list[str]
    objective_type: str         # maps to ObjectiveSpec.evaluator_kind
    feedback_latency_seconds: int | None
    action_surfaces: list[ActionSurface]
    simulator_available: bool
    replayable: bool
    training_allowed: bool | None
    data_use_notes: str
    source_evidence: dict
```

---

## N9. ObjectiveSpec Schema (from oracle-moltwork)

New dataclass for stateful performance evaluation:

```python
@dataclass
class ObjectiveSpec:
    evaluator_kind: str         # proper_score | episodic_simulator | hidden_regression | production_telemetry | heldout_metric | human_panel
    primary_metric: str
    direction: str              # maximize | minimize
    feedback_latency_seconds: int | None = None
    replayable: bool = False
    simulator_ref: str | None = None
    verifier_strength: float = 0.0
    sim_to_real_risk: float = 0.0
```

---

## N10. ExecutionStep Schema (from oracle-moltwork)

Interface by workflow stage, not opportunity-wide:

```python
@dataclass
class ExecutionStep:
    phase: str                  # discover | qualify | enter | work | submit | evaluate | settle | outcome
    actor: str                  # agent | human
    interface: str              # official_api | official_mcp | official_webmcp | cli | browser | desktop | email | human_queue
    human_dependency: HumanDependency | None
```

**Per-venue breakdown:**
```text
Metaculus:    discover=API, work=API, submit=API, settle=platform         → H0
Roblox:       build=MCP, test=MCP, publish=REST, monitor=REST            → H0-ish
Fortnite:     build=MCP, test=MCP, publish=browser(HUMAN)               → H2
Vesuvius:     discover=web, work=local/GPU, submit=form/email            → H2
OSS Patch:    discover=Git, work=local, submit=GitHub PR, claim=web      → H0/H2
```

---

## N11. H0 Semantics Fix (from oracle-moltwork)

```yaml
autonomy_level: H0
bootstrap_required: true
bootstrap_dependencies:
  - create_account
  - accept_terms
  - create_api_token
```

**H0 = no human involvement on a normal unit of work once provisioning is complete.**

| Venue | H-Level | Bootstrap | Why |
|-------|---------|-----------|-----|
| Metaculus | H0 | account + token + tournament | Native API submission |
| Roblox existing game | H0 | creator account + API key + experience | MCP + REST publishing |
| Fortnite | H2 | — | Creator Portal release is recurring human |
| OSS Patch | H0 work / H2 claim | — | PR is autonomous, security claim is human |
| Vesuvius | H0 work / H2 submit | — | Research is autonomous, submission is human |
| YGO Simulator | H0 | — | Full loop is simulator-based |

---

## O. API DOCUMENTATION QUICK REFERENCE

### Agent-Native APIs (60+)

| Platform | API Base | Auth | Docs |
|----------|----------|------|------|
| Upwork | api.upwork.com | OAuth 2.0 | upwork.com/developer |
| Roblox | apis.roblox.com | API Key | create.roblox.com/docs/cloud |
| Etsy | openapi.etsy.com | OAuth 2.0 | developers.etsy.com |
| Shopify | {store}.myshopify.com/admin | OAuth + Admin API | shopify.dev |
| GitHub | api.github.com | OAuth / Token | docs.github.com/en/apps |
| Atlassian | api.atlassian.com | OAuth 2.0 | developer.atlassian.com |
| monday.com | api.monday.com | API Token | developer.monday.com |
| Asana | app.asana.com/api | OAuth 2.0 | developers.asana.com |
| HubSpot | api.hubapi.com | OAuth 2.0 | developers.hubspot.com |
| Chrome Web Store | chrome.google.com/webstore | OAuth | developer.chrome.com/docs/webstore/api |
| Reddit | oauth.reddit.com | OAuth 2.0 | developers.reddit.com |
| Framer | api.framer.com | — | framer.com/creators |
| Webflow | api.webflow.com | OAuth 2.0 | webflow.com/developers |
| Miro | api.miro.com | OAuth 2.0 | developers.miro.com |
| WooCommerce | {store}/wp-json/wc/v3 | Consumer Key/Secret | developer.woocommerce.com |
| DigitalOcean | api.digitalocean.com | Bearer Token | docs.digitalocean.com/reference/api |
| Amazon SP-API | sellingpartnerapi-na.amazon.com | OAuth 2.0 | developer-docs.amazon.com/sp-api |
| Walmart | developer.walmart.com | OAuth 2.0 | developer.walmart.com |
| ActiveCampaign | {account}.api-us1.com | API Token | developers.activecampaign.com |
| JetBrains | plugins.jetbrains.com | API Token | plugins.jetbrains.com |
| SuiteCRM | {instance}/api/v8 | OAuth 2.0 | store.suitecrm.com |
| Plesk | {server}:8443/api | — | www.plesk.com/extensions |
| Travelport | {env}.travelport.com | OAuth 2.0 | developer.travelport.com |
| Sabre | api.sabre.com | OAuth 2.0 | developer.sabre.com |
| Personio | {company}.personio.de | API Token | developer.personio.com |
| BambooHR | {company}.bamboohr.com | API Key | bamboohr.com/api |
| Greenhouse | api.greenhouse.io | API Key | developers.greenhouse.io |
| Lever | api.lever.co | API Key | devs.lever.co |
| Mailchimp | {dc}.api.mailchimp.com | OAuth 2.0 | mailchimp.com/developer |
| Klaviyo | a.klaviyo.com | API Token | developers.klaviyo.com |
| Sage | {region}.sageone.com | OAuth 2.0 | developer.sage.com |
| Xero | api.xero.com | OAuth 2.0 | developer.xero.com |
| Exact | api.exactonline.com | OAuth 2.0 | developer.exactonline.com |
| MYOB | api.myob.com | OAuth 2.0 | developer.myob.com |
| SHOPLINE | api.shopline.com | OAuth 2.0 | developer.shopline.com |
| Lightspeed | {hostname}.lightspeedapp.com | OAuth 2.0 | developers.lightspeedhq.com |
| Duda | api.duda.co | API Key | developer.duda.co |
| AppDirect | {instance}.appdirect.com | OAuth 2.0 | developer.appdirect.com |
| Vendasta | {partner}.vendasta.com | OAuth 2.0 | developers.vendasta.com |
| Visma | {region}.vismaonline.com | OAuth 2.0 | docs.connect.visma.com |
| Kintone | {subdomain}.kintone.com | API Token | developer.kintone.com |
| Creatio | {instance}.creatio.com | OAuth 2.0 | developer.creatio.com |
| Keap | {account}.keap.com | OAuth 2.0 | developer.keap.com |
| SugarCRM | {instance}.sugarcrm.com | OAuth 2.0 | developer.sugarcrm.com |
| Leanpub | leanpub.com/api | API Key | leanpub.com/api |
| n8n | {instance}/api/v1 | API Key | docs.n8n.io/api |
| Ghost | {blog}/ghost/api | API Key | ghost.org/docs/api |
| Twitch | api.twitch.tv | OAuth 2.0 | dev.twitch.tv/docs/api |
| Aircall | api.aircall.io | OAuth 2.0 | developer.aircall.io |
| Paddle | api.paddle.com | OAuth 2.0 | developer.paddle.com |
| FreshBooks | api.freshbooks.com | OAuth 2.0 | developer.freshbooks.com |
| Tiendanube | api.tiendanube.com | OAuth 2.0 | dev.nuvemshop.com.br |
| Railway | railway.com/api | OAuth 2.0 | docs.railway.app |
| Mindbody | {site}.mindbodyonline.com | API Token | developers.mindbodyonline.com |
| Zuora | rest.zuora.com | OAuth 2.0 | zuora.github.io |
| Dialpad | {api}.dialpad.com | API Token | developers.dialpad.com |
| Constant Contact | api.constantcontact.com | OAuth 2.0 | developer.constantcontact.com |
| Cin7 | {instance}.cin7.com | API Token | docs.cin7.com |
| PointClickCare | developer.pointclickcare.com | OAuth 2.0 | developer.pointclickcare.com |

### x402 / Agent-Native APIs

| Platform | Protocol | Chain | Endpoint |
|----------|----------|-------|----------|
| x402 Bazaar | x402 | Base | x402bazaar.org |
| x402 Arena | x402 | Base | x402arena.gg |
| Agent402 | x402 + MPP | Multi-chain | agent402.tools |
| tools402 | x402 | Base/Polygon/Solana | docs.tools402.dev |
| req402 | x402 | Base | req402.com |
| Agent Wonderland | x402 + Stripe | — | agentwonderland.com |
| A2A Colony | A2A + Stripe | — | a2acolony.com |
| AgentPact | USDC escrow | Base | agentpact.xyz |
| dealwork.ai | Escrow | — | dealwork.ai |
| OpenAnt | USDC | — | openant.ai |
| WorkProtocol | USDC escrow | Base | workprotocol.ai |
| agentsbay.ai | Polygon USDC | Polygon | agentsbay.ai |
| DeskCrew | USDC | — | deskcrew.io |
| Agent Bounties | USDC escrow | Base | agentbounties.app |
| Molty Cash | USDC | Base | synthesis.mandate.md |
| ClawHunt | Escrow | — | clawhunt.store |
| MoltMarket | Stripe | — | moltbotmarket.com |
| Toku.agency | Stripe Connect | Fiat | toku.agency |
| Complete Codes | USDC | Base | complete.codes |
| OpenJobs | USDC/WAGE | — | openjobs.bot |
| Opire | GitHub bounties | — | app.opire.dev |
| AgentGigs | Stripe Connect | — | agentgigs.io |
| VoxPact | Stripe (EUR) | — | voxpact.com |
| 0xWork | USDC escrow | Base | 0xwork.org |
| BotWork | A2A/webhook | — | botwork.network |
| pact0 | Stripe | — | pact0.com |
| Hober | USDC escrow | Base | hober.dev |
| MoltyBounty | USDC | — | moltybounty.com |
| Atrest.ai | USDC | Base | atrest.ai |
| Agensi | Stripe Connect | — | agensi.io |
| Alysium AgentHub | Stripe Connect | — | alysium.ai |
| Obolos | USDC escrow | Base | obolos.tech |
| Clustly | USDC | Solana | clustly.ai |
| Suptho | ETH/SOL/USDC | — | suptho.ai |
| BugBountyAI | USDC/Arc | — | bugbountyai.online |
| Agoragentic | USDC | Base | agoragentic.com |
| VoxPact | Stripe (EUR) | — | voxpact.com |

---

## P. INFRASTRUCTURE / AUTOMATION ENABLERS

| # | Tool | What It Does | Impact |
|---|------|-------------|--------|
| 1 | **Zapier MCP** | 9K apps, 40K actions via MCP | Eliminates connector work |
| 2 | **Arcade** | OAuth on behalf of agents | H2 → H1 |
| 3 | **Composio** | Managed auth (OAuth2, bearer, API keys) | Alternative to Arcade |
| 4 | **Infisical** | Secrets manager | Secure credential storage |
| 5 | **Vault (HashiCorp)** | Dynamic secrets with leases | Enterprise secrets |
| 6 | **WebMCP** | Websites expose structured browser tools | H2 → H1 for forms |
| 7 | **RentAHuman** | Agent → human bridge via MCP/REST | H4 → agent-controllable |

---

## Q. ADAPTER GAP ANALYSIS

### HIGH PRIORITY — Adapter exists but NOT wired

| Adapter | File | Why Critical |
|---------|------|-------------|
| TaskForce | `taskforce.py` | Score 10/10 in INDEX.md |
| AgentHire | `agenthire.py` | Score 10/10 |
| gigs.sh | `gigs.py` | Meta-directory |
| Olas Network | `olas_adapter.py` | Tier 1 |
| Coinbase Bazaar | `bazaar.py` | x402 distribution |
| Toll402 | `toll402.py` | x402 marketplace |
| Valoria | `valoria.py` | Agent marketplace |

### HIGH PRIORITY — No adapter at all

| Source | Why |
|--------|-----|
| Clustly | Tier 1 agent-native |
| Agoragentic | Tier 1, passive capability-sale |
| Claw Earn | Tier 1 |
| TaskMarket (taskmarket.dev) | Agent work market |
| Gitcoin | Tier 2 |
| Immunefi | Tier 2 bug bounties |
| HackerOne | Tier 2 bug bounties |
| Dework | Tier 2 |
| Algora | Tier 2 |
| TaoStats | Tier 4 compute |
| Ocean Protocol | Tier 4 compute |
| TryBounty | Documented |
| 8004scan | Documented |

### From Gmail — New Agent Platforms Needing Adapters

| Platform | Priority | Source |
|----------|----------|--------|
| AgentPact | HIGH | Money Scout (verified) |
| dealwork.ai | HIGH | Money Scout (verified) |
| OpenAnt | HIGH | Money Scout (verified) |
| Complete Codes | HIGH | Money Scout (verified) |
| Toku.agency | HIGH | Money Scout (verified) |
| OpenJobs | MEDIUM | Money Scout |
| Opire | MEDIUM | Money Scout |
| TaskBounty | MEDIUM | Money Scout |
| SporeAgent | MEDIUM | Money Scout |
| Clawlancer | MEDIUM | Money Scout |
| MoltJobs | MEDIUM | Money Scout |
| DeskCrew | MEDIUM | Money Scout |
| x402 Arena | LOW | Money Scout (intelligence only) |
| Agent402 | LOW | Money Scout (intelligence only) |
| PayanAgent | LOW | Money Scout (24K+ services) |
| AgentGigs | HIGH | Full API lifecycle, 90% share, Stripe |
| VoxPact | HIGH | EUR Stripe escrow, MCP-native |
| 0xWork | HIGH | USDC bounties on Base, $AXOBOTL staking |
| BotWork | MEDIUM | TS SDK task market, 46 agents |
| pact0 | MEDIUM | Small paid tasks, Stripe, early access |
| Hober | MEDIUM | USDC escrow, MCP/SDK |
| MoltyBounty | MEDIUM | USDC bounties, leaderboard shows completions |
| Atrest.ai | HIGH | Agent-to-agent, $48K+ USDC transacted |
| Agensi | HIGH | Sell SKILL.md packages, 70% share, Stripe |
| Alysium AgentHub | MEDIUM | Paid specialist conversations, Stripe |
| Obolos | MEDIUM | Base USDC work protocol, escrowed |
| Clustly | HIGH | Solana USDC escrow, hashed acceptance |
| Suptho | LOW | Sell agent execution data, unproven buyers |
| BugBountyAI | MEDIUM | Security bounties, Arc/Circle |
| Agoragentic | MEDIUM | 97% seller share, 801 invocations, needs Interchange check |

### Evidence of Real Payouts (from Gmail Money Scout)

| Platform | Verified Payout Signal | Source |
|----------|----------------------|--------|
| Atrest.ai | $48K+ USDC transacted, 1,200+ tasks completed | Money Scout Sep 1 |
| Agensi | $2,235 all-time, $455 last 30 days (Stripe-verified) | Money Scout Aug 29 |
| Agoragentic | 801 invocations (settlement state unverified) | Money Scout Sep 1 |
| MoltyBounty | Leaderboard shows 4-12 completions per agent | Money Scout Sep 1 |
| AgentGigs | $5-10 indexed job budget, 90% share verified | Money Scout Sep 1 |
| Pact0 | Early access/pre-launch, Stripe payouts described | Money Scout Sep 1 |
| Suptho | No verified buyer/earnings data | Money Scout Sep 1 |
| BugBountyAI | No concrete current bounty amounts verified | Money Scout Sep 1 |
