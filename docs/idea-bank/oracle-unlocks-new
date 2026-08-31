Yes. We already had the correct abstraction, and my previous “A0–A5 agentability” suggestion would duplicate it.

**H0–H4 is already the autonomy/human-involvement axis.** The current taxonomy literally defines it that way: H0 fully autonomous, H1 mostly autonomous with bounded human escalation, through H4 primarily human.  The Oracle `Opportunity` already has `human_dependencies`, `eligibility`, `venue_policy`, capabilities, acceptance model and evidence fields.

The thing we're missing is not another classification. It is:

> **Decompose why an opportunity is H1/H2/H3, then continually search for existing infrastructure that removes those individual human dependencies.**

That is much better.

## Keep the existing primitives

I would freeze these meanings:

```text
Taxonomy
  task_family
  capabilities
  economic_surface
  evaluation_modes
  H0-H4

Opportunity
  "this particular piece of economic work"

Pack
  domain intelligence for unusual classes of work

Venue
  how we actually interact with the market

Campaign
  one attempt to exploit an opportunity

Human Queue
  fallback executor for steps that genuinely
  still need humans
```

Your existing `HackathonPack` already has the right purpose: it turns domain-specific raw information into normalized opportunities, routes, judging criteria and rubrics.

And `WorkVenue` already defines the operational lifecycle:

```text
discover
inspect
submit
status
settle
```

So don't invent `VenuePack`. Keep **Pack = intelligence** and **Venue = execution adapter**.

---

# What is actually missing: the execution-step graph

Today we might record:

```yaml
autonomy_level: H2

human_dependencies:
  - "needs account"
  - "needs manual submission"
```

That isn't granular enough to automate.

Instead the Pack research should produce:

```yaml
execution_plan:

  - stage: discover
    action: find_jobs
    actor: agent
    interface: API
    human_required: false

  - stage: qualify
    action: select_job
    actor: agent
    interface: internal
    human_required: false

  - stage: enter
    action: verify_identity
    actor: human
    interface: browser
    human_required: true
    reason: KYC
    recurrence: once_per_account

  - stage: authenticate
    action: authorize_account
    actor: human
    interface: OAuth
    human_required: true
    reason: consent
    recurrence: once_or_expiry

  - stage: work
    action: produce_artifact
    actor: agent
    interface: workspace
    human_required: false

  - stage: submit
    action: submit_proposal
    actor: agent
    interface: API
    human_required: false

  - stage: outcome
    action: retrieve_status
    actor: agent
    interface: API
    human_required: false
```

Then:

```text
ExecutionPlan
      ↓
derive H-level
```

rather than inventing another autonomy number.

An opportunity with one one-time OAuth consent is probably H1.

An opportunity needing subjective approval on every submission could be H2.

Something requiring a human to physically visit somewhere remains H4 for that specific step—but the **overall agent workflow can still be viable** because the human can be subcontracted.

---

# Humans should become another executor inside the Lab

This is where RentAHuman fits beautifully.

It already exposes MCP and REST interfaces allowing an agent to search humans, post bounties, book workers, communicate and manage task execution. ([RentAHuman][1])

So:

```text
Letta worker
    │
    ▼
ExecutionPlan
    │
    ├── agent step
    ├── agent step
    │
    ├── HUMAN REQUIRED
    │       │
    │       ▼
    │   Human Queue
    │       │
    │   ┌───┴─────────┐
    │   ▼             ▼
    │  you       RentAHuman MCP
    │
    ├── agent step
    ▼
complete
```

The human should still generate proper WorkerKit events:

```text
human_escalation.requested
human_escalation.accepted
human_action.completed
human_artifact.received
```

with:

```text
human cost
latency
reason
actor
result
evidence
```

Then Hydra learns things like:

> This market is nominally H2 but human intervention averages only 90 seconds once per account.

Or:

> This marketplace requires a human reviewer on every job and costs $7.80 on average; not economically useful for $5 jobs.

That's useful.

---

# This also fixes how we think about H0

H0 shouldn't necessarily mean:

> absolutely no human has ever interacted with anything.

It can mean:

> **after initial authorized provisioning, the execution loop itself is autonomous.**

That matches the definition we had been using.

So:

```text
human creates account once
human completes KYC once
human grants OAuth once

             ↓

future jobs:
discover → work → submit → collect outcome

             =
             H0-ish operationally
```

You may still retain the onboarding dependencies in the provenance.

---

# There is an immediate schema bug worth fixing

This research actually exposes a concrete bug in the current Oracle code.

`Opportunity` defines:

```text
eligibility
venue_policy
human_dependencies
source_evidence
market_signals
```

but its current `to_dict()` does **not serialize those fields**, and `from_dict()` doesn't restore them either.

That's especially bad now because those are exactly the fields Oracle needs to preserve.

So the coding agent should fix that immediately.

There's also duplication: `opportunities/schema.py` defines the canonical economic `Opportunity`, while `venues/base.py` defines another overlapping `Opportunity` dataclass.

Delete that conceptual duplication:

```text
venues/base.py
        ↓
imports
opportunities.schema.Opportunity
```

One opportunity schema.

---

# The big Oracle research loop should therefore be “human dependency reduction”

This is the part I think is genuinely powerful.

For every opportunity:

```text
Opportunity
     ↓
ExecutionPlan
     ↓
find HUMAN_REQUIRED steps
     ↓
search existing automation frontier
```

For each human blocker, search this ladder:

```text
1. Official API
2. Official OpenAPI
3. Official MCP
4. Official WebMCP
5. Existing approved integration
6. Zapier MCP / integration platform
7. Community MCP
8. compliant browser automation
9. Human Queue
```

And importantly:

```text
VENUE POLICY
```

sits above all of them.

We don't bypass a platform's intended restrictions just because browser automation technically works.

---

# Upwork is almost a perfect example

This is more agent-accessible than I realized.

Upwork's official developer platform currently exposes APIs around:

* job posts;
* search;
* proposals;
* contracts;
* reporting;
* user/team management. ([Upwork][2])

Their API terms explicitly give examples including allowing users to search job postings, manage contracts and **apply to jobs** through approved applications. ([Upwork][3])

So the execution graph isn't:

```text
Upwork
= human marketplace
= H4
```

It's more like:

```text
ACCOUNT SETUP
human

IDENTITY VERIFICATION
human

API KEY APPROVAL
human

             ↓ once provisioned

JOB DISCOVERY
agent / official API

JOB QUALIFICATION
agent

PROPOSAL GENERATION
agent

PROPOSAL SUBMISSION
potentially official API

MESSAGING
API

CONTRACT MANAGEMENT
API
```

Upwork also explicitly warns that unauthorized automation/browser bots can cause restrictions and says compliant automation should go through approved API access. ([Upwork Support][4])

Perfect Oracle data:

```yaml
autonomy_level: H1

human_dependencies:
  account_setup:
    recurrence: once
  identity_verification:
    recurrence: once_or_requested
  api_approval:
    recurrence: once
```

There's even an open-source Upwork MCP server already exposing a discover → score → propose → manage → communicate workflow on top of the API. ([GitHub][5])

We shouldn't blindly trust or deploy it, but Oracle should absolutely discover it as an **automation candidate**.

---

# Roblox is an even bigger unlock

This one is now spectacularly aligned.

Roblox has an **official Studio MCP server built directly into Roblox Studio**.

It lets an MCP-compatible agent:

* inspect the game structure;
* edit scripts;
* insert models;
* execute Luau;
* control play mode/test the game. ([GitHub][6])

That's not a community hack. It's official Roblox infrastructure.

Then Open Cloud gives REST APIs for external automation, including assets, game resources and more. ([Creator Hub][7])

The Assets API can upload/update assets programmatically instead of manually importing them into Studio. ([Creator Hub][8])

And Creator Store currently has beta APIs to:

```text
create product
get product
update product
search assets
```

([Creator Hub][9])

That changes the practical execution plan enormously:

```text
Roblox work circa old assumption

human opens Studio
human edits project
human tests
human exports
human uploads
human publishes
```

versus:

```text
2026

Letta
  ↓
official Roblox Studio MCP
  ↓
edit/build/debug/playtest
  ↓
Open Cloud
  ↓
asset management
  ↓
Creator Store APIs
  ↓
publishing/management
```

There will still be account/security/platform-review steps.

But this potentially collapses a large class of work from H2/H3 toward H1.

**This is exactly what the Oracle should notice.**

---

# Etsy is similar

Etsy's official Open API supports inventory, sales-order and shop-management workflows, including creating/managing listings. ([Etsy Developers][10])

Interesting nuance: Etsy now has an official MCP server, but today it is a **developer documentation MCP**, not an action server—it exposes knowledge of its 90+ endpoints rather than actually calling Etsy. ([Etsy Developers][11])

But community MCP implementations already wrap the actual API and expose actions like:

```text
create listing
publish listing
update inventory
upload image/file
manage orders
```

([GitHub][12])

So Oracle records:

```text
Official direct API: YES
Official action MCP: NO
Official docs MCP: YES
Community action MCP: YES
OAuth required: YES
Human initial consent: YES
```

Again: no need to build anything unless using it proves worthwhile.

---

# Shopify is already going agent-native too

Shopify's Partner API exposes Partner Dashboard data including **Experts Marketplace opportunities** to participating partners. ([Shopify][13])

And Shopify now has official commerce-oriented MCP surfaces. Its Order MCP lets agents retrieve and manage order lifecycle state in its UCP ecosystem, with short-lived access tokens and capability negotiation. ([Shopify][14])

So Pack research might discover:

```text
Shopify Experts opportunities
        +
Partner API
        +
merchant APIs
        +
MCP/UCP
```

and ask precisely:

> Which remaining stages actually require a person?

That's the right question.

---

# Zapier MCP might eliminate a ridiculous amount of connector work

This is perhaps the biggest practical shortcut.

As of August 26, Zapier MCP advertises access to **9,000+ apps and 40,000+ actions**, with Zapier handling app connections, credentials and rate limits. ([Zapier Help][15])

And Zapier added an MCP Client beta allowing workflows to call external remote MCP servers too. ([Zapier Help][16])

So our integration ladder should seriously include:

```text
Do we really need to write Venue adapter?

        ↓

Can Zapier MCP already perform
the relevant action?
```

This fits the “dumb as rocks” philosophy perfectly.

---

# WebMCP should become an automatic human-step reduction check

WebMCP is valuable, but with an important boundary.

Chrome's current design lets websites register structured browser tools with names, descriptions and JSON schemas. The browser exposes those to the agent so the agent can act more reliably than by manipulating pixels/DOM. Chrome explicitly says the user remains involved for permission/confirmation. ([Chrome for Developers][17])

So WebMCP doesn't magically turn:

```text
mandatory human judgment
```

into:

```text
autonomous
```

But it absolutely can turn:

```text
human needs to fill awkward form
```

into:

```text
agent invokes structured tool
```

And Chrome already ships a WebMCP tooling repo containing:

* a tool inspector;
* WebMCP eval CLI;
* polyfill;
* demos. ([GitHub][18])

So add to every Pack research process:

```text
if website:
    detect WebMCP
    enumerate tools
    compare with human dependencies
```

Conceptually:

```text
human_dependencies:

  - submit_form
  - upload_artifact
  - choose_category
  - confirm_entry
```

Website now exposes:

```text
webmcp:
  submitEntry(...)
  uploadArtifact(...)
```

Oracle can infer:

```text
submit_form    RESOLVED_BY webmcp.submitEntry
upload         RESOLVED_BY webmcp.uploadArtifact
choose         still agent/browser
confirm        human approval required
```

Autonomy moves:

```text
H2 → H1
```

without inventing new taxonomy.

---

# Make human dependencies normalized IDs

This is the piece I would add.

Today they're freeform strings.

Make them things like:

```text
human.account_create
human.identity_verify
human.oauth_consent
human.api_key_provision
human.payment_setup

human.subjective_approval
human.legal_acceptance
human.captcha

human.manual_form
human.manual_upload
human.browser_navigation

human.voice_call
human.video_call

human.physical_presence
human.physical_delivery
```

Then Oracle can discover patterns across markets.

Suppose:

```text
1,847 opportunities

312 blocked by:
human.manual_upload
```

A new WebMCP/API integration resolves that dependency for a marketplace containing $400k of opportunity.

That is a measurable unlock.

---

# This gives Oracle a very valuable frontier query

Instead of merely:

> Find new opportunities.

Ask:

> **What human dependency, if eliminated, unlocks the most valuable currently inaccessible opportunity?**

For example:

```text
                VALUE BLOCKED

human.manual_submission      $820k
human.api_key_provision      $510k
human.oauth_consent          $420k
human.kyc                    $1.1m
human.physical_action        $300k
```

But:

```text
AUTOMATABILITY

manual submission     HIGH
API provisioning      MEDIUM
OAuth consent         LOW/one-time
KYC                   SHOULD REMAIN HUMAN
physical action       requires human provider
```

Now the Lab works on:

```text
manual submission
```

not KYC.

That's a good economic research allocator.

---

# Credentials: definitely do not build this ourselves

There are already excellent primitives.

I would create exactly one tiny Moltwork interface:

```text
CredentialRef
```

Never:

```text
Credential
```

Something like:

```yaml
credential:
  provider: arcade
  ref: roblox-main
  scopes:
    - asset.write
```

The secret itself **never** belongs in:

```text
Git
Hydra
Letta MemFS
prompt
ATIF
Harbor artifact
WorkerKit receipt
```

Only the reference does.

---

## OAuth: Arcade is unusually well aligned

Arcade's tool-auth architecture handles OAuth on behalf of agents. Critically, after the human completes the initial OAuth challenge, Arcade injects the access token into the trusted tool context and **the LLM/client never sees the token**. It also remembers the authorization until revoked. ([Arcade Docs][19])

That gives:

```text
Letta
   │
   │ call tool
   ▼
Arcade tool boundary
   │
   │ obtains hidden credential
   ▼
external API
```

Much better than:

```text
Letta sees ROBLOX_API_KEY
```

First use:

```text
agent needs Etsy
      ↓
Arcade detects auth absent
      ↓
HumanQueue:
"Authorize Etsy"
      ↓
user does OAuth once
      ↓
future runs autonomous
```

That maps perfectly to H1.

Arcade also has a generic OAuth 2.0 provider for APIs that don't have a prebuilt provider. ([Arcade Docs][20])

---

# Composio is the obvious alternative

Composio does essentially the same class of job but emphasizes breadth.

It stores and refreshes connected-account credentials by stable user identity and supports OAuth2, bearer tokens, API keys and Basic Auth. ([Composio][21])

Its managed-auth layer means common integrations don't require you to register/maintain your own OAuth application. ([Composio][22])

I wouldn't integrate both immediately.

For the private Lab:

```text
Arcade
OR
Composio
```

Pick whichever covers the first three Venue integrations better.

My slight preference for the Moltwork architecture is **Arcade**, because its “credential only exists inside trusted tool context, not LLM context” model maps very cleanly onto WorkerKit provenance.

---

# Static API keys: Infisical or Vault

For things like:

```text
API key
developer secret
service token
```

don't use Letta environment memory.

Use a real secrets manager.

Infisical has a daemon explicitly designed to retrieve/renew secrets for applications and can revoke managed dynamic leases/identity tokens at shutdown. ([Infisical Blog][23])

Vault is the more mature heavy-duty version and supports static secrets plus dynamic, short-lived credentials with leases and revocation. ([HashiCorp Developer][24])

For your private Lab I would probably start:

```text
Infisical
```

because it's less operationally heavy.

Then:

```text
Arcade        → OAuth/user accounts
Infisical     → raw/static secrets
```

No Moltwork secret vault.

---

# This gives us a clean credential architecture

```text
                  HUMAN
                    │
              initial auth/KYC
                    │
                    ▼
           AUTH / SECRET LAYER
          ┌─────────┴──────────┐
          ▼                    ▼
       Arcade              Infisical
       OAuth               API keys
          │                    │
          └─────────┬──────────┘
                    ▼
              trusted tools
                    │
                    ▼
                  Letta
         never sees raw credentials
```

And Harbor environments get:

```text
credential capability
```

rather than giant `.env` files whenever possible.

---

# I would introduce only two small new implementation concepts

Not five more systems.

### `ExecutionStep`

Extends the existing Opportunity model.

```yaml
stage: submit
action: publish_asset
actor: agent
interface: roblox_open_cloud
credential_ref: roblox-main
human_dependency: null
```

### `HumanDependency`

Structured replacement for the existing strings.

```yaml
id: human.identity_verify
stage: enter
recurrence: once
mandatory: true
delegatable: false
estimated_minutes: 4
```

That's basically it.

Everything else already exists.

---

# Then derive H0–H4 from those steps

For example:

```text
H0
no mandatory human execution after provisioning

H1
one-time onboarding/auth
or occasional bounded approval/escalation

H2
substantive human judgment on normal runs

H3
human remains primary task performer

H4
fundamentally human/physical execution
```

And H4 doesn't mean “discard.”

Because:

```text
H4 step
   ↓
RentAHuman
   ↓
agent-controlled workflow
```

might still make the **whole economic process viable**.

That's a subtle but important distinction.

---

# This also means human work becomes measurable Lab infrastructure

Hydra can eventually query:

```text
Which human dependency costs us most money?

Which human steps produce the longest delays?

Which formerly-human steps have been automated?

Which MCP integration lowered cost most?

Which markets became profitable after an unlock?

Where does human judgment genuinely improve outcomes?

Which human provider is best for which task?
```

Humans aren't outside the Lab.

They are an executor type inside it.

---

# The Oracle moat becomes clearer

Not:

> We found Upwork jobs.

Anyone can scrape jobs.

Instead:

```text
Oracle understands:

1. what economic work exists

2. what exact steps are required

3. which steps are machine-executable

4. which require humans and why

5. which existing API/MCP/WebMCP/tool
   can remove that dependency

6. what credential/onboarding is needed

7. what it costs in human time + agent compute

8. which workers have succeeded there

9. which Schools/Evaluators/Skills improve performance
```

That's substantially harder to reproduce.

---

# The frontier scanner should basically run against Packs

For each Pack:

```text
RobloxPack
EtsyPack
UpworkPack
ShopifyPack
HackathonPack
...
```

periodically ask:

```text
Have official APIs changed?

New OpenAPI endpoints?

New MCP server?

New WebMCP tools?

New Zapier actions?

New community MCP?

New browser automation support?

Policy changed?

Human dependency removed?

Human dependency added?
```

Then update:

```text
ExecutionPlan
      ↓
H-level
      ↓
eligible Worker population
      ↓
expected economic value
```

This is exactly the kind of Oracle research worth automating.

---

## So the immediate Oracle dev change is smaller than I initially suggested

I would give the coding agent these instructions:

1. **Do not add another agentability taxonomy.** H0–H4 remains canonical.
2. **Fix canonical `Opportunity` serialization** so `human_dependencies`, `eligibility`, `venue_policy`, `source_evidence`, and `market_signals` survive round-trips.
3. **Delete the duplicate Venue `Opportunity` schema** and import the canonical one.
4. Change `human_dependencies: list[str]` to structured backwards-compatible dependencies.
5. Add `execution_steps` at Opportunity/Route level using our already-defined workflow stages: discover → qualify → enter → work → submit → evaluate → settle → outcome.
6. Derive or validate H0–H4 from those steps.
7. Build a `HumanQueueAdapter`; first providers can simply be `manual://owner` and RentAHuman MCP. RentAHuman already provides exactly the agent→human bridge. ([RentAHuman][25])
8. Add only a `CredentialRef`/`AuthBroker` boundary. Use Arcade/Composio + Infisical/Vault rather than implementing credential storage.
9. Extend Pack research with an **automation resolver** that checks official API → MCP → WebMCP → Zapier → approved community MCP → browser → human.
10. Record every resolved human dependency in Hydra so we can measure when a market genuinely becomes more autonomous.

And there are already some extremely promising immediate Pack targets: **Roblox now has an official Studio MCP plus Open Cloud/Creator Store APIs; Upwork officially exposes proposal/search/contract APIs subject to approved automation; Etsy has a broad Open API plus active MCP ecosystem; Shopify is exposing marketplace/commerce functionality through APIs and MCP; Zapier MCP gives a generic bridge into thousands of applications.** ([GitHub][6])

That's the real “market unlock” mechanism: **don't classify new markets differently—continually drive their existing H-level downward by eliminating specific human dependencies with frontier infrastructure.**

[1]: https://rentahuman.ai/docs/use-cases/api-integration?utm_source=chatgpt.com "REST API Integration for AI Pipelines — Human-in-the-Loop Automation | RentAHuman — AI Agent Marketplace"
[2]: https://www.upwork.com/developer?utm_source=chatgpt.com "Upwork Developer Space"
[3]: https://www.upwork.com/legal?utm_source=chatgpt.com "Upwork Legal Center"
[4]: https://support.upwork.com/hc/en-us/articles/43342677368467-Use-bots-and-other-automation-properly?utm_source=chatgpt.com "Use bots and other automation properly – Upwork Customer Service & Support | Upwork Help"
[5]: https://github.com/AbbottDevelopments/upwork-mcp-server?utm_source=chatgpt.com "GitHub - AbbottDevelopments/upwork-mcp-server: Open-source MCP server for Upwork's GraphQL API — search jobs, manage contracts, send messages, and more through AI agents like Claude · GitHub"
[6]: https://github.com/Roblox/creator-docs/blob/main/content/en-us/studio/mcp.md?utm_source=chatgpt.com "creator-docs/content/en-us/studio/mcp.md at main · Roblox/creator-docs · GitHub"
[7]: https://create.roblox.com/docs/cloud?utm_source=chatgpt.com "Cloud API reference | Documentation - Roblox Creator Hub"
[8]: https://create.roblox.com/docs/cloud/guides/usage-assets?utm_source=chatgpt.com "Usage guide for assets | Documentation - Roblox Creator Hub"
[9]: https://create.roblox.com/docs/cloud/reference/features/creator-store?utm_source=chatgpt.com "Creator Store | Documentation - Roblox Creator Hub"
[10]: https://developers.etsy.com/?utm_source=chatgpt.com "Etsy Open API v3 | Etsy Open API v3"
[11]: https://developers.etsy.com/documentation/mcp_server/devmcpserver/?utm_source=chatgpt.com "Dev MCP Server | Etsy Open API v3"
[12]: https://github.com/DColl/etsy-mcp-server?utm_source=chatgpt.com "GitHub - DColl/etsy-mcp-server: Full-featured MCP server for Etsy Open API v3 — manage listings, inventory, images and orders via Claude or any MCP client · GitHub"
[13]: https://shopify.dev/docs/api/partner/unstable?utm_source=chatgpt.com "Partner API reference"
[14]: https://shopify.dev/docs/agents/orders/order-mcp?utm_source=chatgpt.com "Order MCP server"
[15]: https://help.zapier.com/hc/en-us/articles/48308034391821-What-is-Zapier-MCP?utm_source=chatgpt.com "What is Zapier MCP? – Zapier"
[16]: https://help.zapier.com/hc/en-us/articles/38777069364109-Connect-remote-MCP-servers-to-Zapier-using-MCP-Client?utm_source=chatgpt.com "Connect remote MCP servers to Zapier using MCP Client – Zapier"
[17]: https://developer.chrome.com/docs/ai/agents?hl=en&utm_source=chatgpt.com "WebMCP and AI agents  |  AI on Chrome  |  Chrome for Developers"
[18]: https://github.com/GoogleChromeLabs/webmcp-tools?utm_source=chatgpt.com "GitHub - GoogleChromeLabs/webmcp-tools: This repository contains a suite of developer utilities and demos designed to support the adoption of the WebMCP API. · GitHub"
[19]: https://docs.arcade.dev/en/build/create-tools/tool-basics/create-tool-auth?utm_source=chatgpt.com "Add user authorization to your MCP tools | Arcade Docs"
[20]: https://docs.arcade.dev/en/references/auth-providers/oauth2?utm_source=chatgpt.com "OAuth 2.0 | Arcade Docs"
[21]: https://docs.composio.dev/docs/authentication?utm_source=chatgpt.com "Authentication | Composio"
[22]: https://docs.composio.dev/toolkits/managed-auth?utm_source=chatgpt.com "Managed Auth | Composio"
[23]: https://infisical.com/docs/integrations/platforms/infisical-agent?utm_source=chatgpt.com "Infisical Agent - Infisical"
[24]: https://developer.hashicorp.com/vault/tutorials/get-started/understand-static-dynamic-secrets?utm_source=chatgpt.com "Understand static and dynamic secrets | Vault | HashiCorp Developer"
[25]: https://rentahuman.ai/mcp?utm_source=chatgpt.com "Documentation | RentAHuman — MCP Server for AI Agents"
