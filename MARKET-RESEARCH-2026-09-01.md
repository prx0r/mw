# Market Research — What's Hot and Agent-Submittable

## 1. Chrome Web Store (Score: 9.0)

### What's Hot
- **AI sidebars** — AskGo ChatGPT sidebar grew +562% (19K→127K installs)
- **Shopping extensions** — demand +37.4% outpacing supply +26.3%
- **Developer tools** — install growth +82.7% on Edge, high willingness to pay
- **Education/assessment** — Vretta grew +2,900% (10K→300K installs)
- **Media utilities** — volume boosters, downloaders showing triple-digit growth

### Agent Submission Path
- Chrome Web Store API v2 — fully programmatic
- Submit via `chrome.management` API or `gcloud` CLI
- No human review for updates (only initial listing)
- Revenue: self-hosted billing (Stripe), 5-15% of top extensions make $3K+/mo

### Best Niches for Agent
1. **AI writing/summarization sidebar** — high demand, code-heavy, agent builds
2. **Shopping price tracker** — affiliate commissions, agent can build comparison logic
3. **Developer productivity** — code snippet managers, PR reviewers
4. **Expired extension replacements** — 2,400 extensions expired with 1K+ users

## 2. Atlassian Marketplace (Score: 9.3)

### What's Hot
- ScriptRunner: 35.7K installs, market leader
- draw.io: 68K installs, #1 most reviewed
- Tempo Timesheets: 88K installs, $10M+ revenue

### Agent Submission Path
- Forge CLI — `forge create`, `forge deploy`, `forge install`
- 0% revenue share on first $1M lifetime Forge revenue
- App review process exists but is automated for standard patterns
- Revenue: subscription per-seat, 83-100% to developer

### Best Niches for Agent
1. **Jira automation workflows** — code-heavy, agent builds, API-driven
2. **Confluence integrations** — document templates, data connectors
3. **GitHub/GitLab sync tools** — agent understands code integration
4. **Custom dashboards** — reporting, analytics, agent builds

## 3. Reddit Devvit (Score: 8.9)

### What's Hot
- Games (Hot & Cold, Sword & Supper, Honk)
- Mod tools (Comment Mop, ContextMod)
- Community apps (SubVitals CX analytics)

### Agent Submission Path
- `devvit` CLI — TypeScript, `npm run dev`, `devvit publish`
- Free hosting by Reddit
- $167K max developer funds (Tier 8: 1M daily engagers)
- App review process, but template-based apps get through

### Best Niches for Agent
1. **Community games** — agent builds TypeScript games, simple submission
2. **Mod automation tools** — comment moderation, spam detection
3. **Poll/survey apps** — community engagement, agent builds
4. **Analytics dashboards** — SubVitals-style, agent builds React

## 4. Metaculus (Score: 10.0 — Already Working)

### What's Hot
- FutureEval $50K tournament (Sep 6 deadline)
- 1,220 open binary questions
- Free inference subsidized by OpenAI/Anthropic/Google

### Agent Submission Path
- REST API — `POST /api2/questions/{id}/forecast/`
- Bot account already set up (xev0)
- Score = log score against resolution
- No human gatekeeping

## 5. Gumroad (Score: 8.0)

### What's Hot
- Digital products: templates, prompts, code, courses
- 95%+ revenue to creator
- API allows product creation and management

### Agent Submission Path
- REST API — create product, upload files, set price
- Agent can create templates, code snippets, prompt packs
- Self-hosted billing
- Revenue: direct sales, no gatekeeping

## Priority Ranking for Agent

| Priority | Market | Why |
|----------|--------|-----|
| 1 | Metaculus | Already working, fully autonomous, tournament prizes |
| 2 | Chrome Web Store | High demand, API submission, AI tools hot |
| 3 | Atlassian Marketplace | 0% rev share first $1M, Forge CLI, agent builds apps |
| 4 | Reddit Devvit | Free hosting, $167K funds, TypeScript, simple |
| 5 | Gumroad | Digital products, 95% rev, API submission |
