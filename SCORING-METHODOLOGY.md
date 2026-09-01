# Marketplace Scoring Methodology

## Score Formula

```
Score = (agentability × 4) + (revenue_potential × 3) + (api_quality × 2) + (submission_ease × 1)
```

### Component Definitions

**Agentability (0-10)** — Can an agent do this autonomously?
- 10: Fully autonomous (API-only, no human review, no account creation)
- 8: Autonomous after one-time setup (OAuth, API key)
- 6: Needs human for initial account/approval, then autonomous
- 4: Needs human per submission (review/approval)
- 2: Needs human for deliverable (design, video, content)
- 0: Fundamentally human-only

**Revenue Potential (0-10)** — How much can an agent earn?
- 10: $10k+/month potential (SaaS marketplace, high-volume)
- 8: $1k-10k/month (app marketplace with recurring revenue)
- 6: $100-1k/month (per-sale or per-submission)
- 4: $10-100/month (small but consistent)
- 2: $1-10/month (micro-revenue)
- 0: No direct revenue (practice only)

**API Quality (0-10)** — How good is the API?
- 10: Full CRUD API, OAuth, webhooks, docs
- 8: REST API with auth, good docs
- 6: Basic API, some manual steps
- 4: Limited API, needs browser automation
- 2: No API, only portal
- 0: No submission mechanism

**Submission Ease (0-10)** — How easy to submit?
- 10: One API call to submit
- 8: CLI tool or SDK
- 6: Form submission (automatable)
- 4: Multi-step process
- 2: Needs portfolio/review
- 0: Application process, human gatekeeping

## Scoring Data Sources

1. **Oracle registry** —351 marketplaces with revenue models, API info
2. **Unlocks reports** — 3 reports with detailed analysis (Aug 31 - Sep 1, 2026)
3. **Lab history** — What actually worked (Metaculus, BountyBook)
4. **Live research** — Web search for current demand, submission friction

## Score History

### 2026-09-01 Initial Scores
- Based on registry analysis + unlocks reports
- No lab history yet (just starting)

### Future Adjustments
- After 100+ submissions: adjust scores based on actual success rate
- After revenue data: adjust revenue_potential based on real earnings
- After API testing: adjust api_quality based on actual friction
- Lab specialization: boost scores for markets where agent excels
