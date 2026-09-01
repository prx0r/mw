# Problem Spaces — Oracle Taxonomy

## Why Problem Spaces Matter

You can't compare a hackathon to a Chrome extension. They're different problems with different success criteria, different time horizons, different competition dynamics, and different revenue models.

The Oracle must categorize by problem space FIRST, then by H-level, then by reward. This makes good opportunities obvious without arbitrary reasoning.

## The 6 Problem Spaces

### 1. PREDICTION
**What:** Forecast outcomes, predict the future
**Examples:** Metaculus, Bittensor subnet 118 (Ditto), Polymarket
**Success =** accuracy vs ground truth
**Metric =** Brier score, log score, calibration
**Time =** question resolves in days to years
**Competition =** vs community aggregate, other bots
**Revenue =** tournament prizes, subnet emissions, market profits
**Skills =** research, reasoning, evidence synthesis, calibration
**Agent fit =** PERFECT — fully autonomous, machine-scored, fast feedback

### 2. BOUNTY
**What:** Complete a specific task for a reward
**Examples:** GitHub bounties, bug bounties, code challenges, RentAHuman
**Success =** deliverable that passes verification
**Metric =** tests pass, bug found, task completed, submission accepted
**Time =** hours to days
**Competition =** first to submit, or best submission wins
**Revenue =** per-bounty reward (one-time)
**Skills =** coding, debugging, security, research
**Agent fit =** GOOD — clear verification, fast feedback, per-task

### 3. MARKETPLACE
**What:** Build products that sell repeatedly
**Examples:** Chrome extensions, Atlassian apps, Gumroad products, Unity assets
**Success =** product that gets users and revenue
**Metric =** installs, revenue, retention, reviews
**Time =** weeks to build, months to earn, ongoing maintenance
**Competition =** market dynamics, quality, positioning
**Revenue =** recurring, percentage of sales, subscription
**Skills =** product development, UI/UX, marketing, maintenance
**Agent fit =** GOOD — code-heavy, API submission, recurring revenue

### 4. HACKATHON
**What:** Build demo in time limit, win prizes
**Examples:** ETHGlobal, Devpost, MLH, protocol-specific hackathons
**Success =** winning submission
**Metric =** judges score, demo quality, innovation
**Time =** 24-72 hours, fixed deadline
**Competition =** ranked against other teams
**Revenue =** prize pool (non-recurring)
**Skills =** rapid prototyping, presentation, innovation, breadth
**Agent fit =** MODERATE — needs creativity, presentation, time pressure

### 5. INFRASTRUCTURE
**What:** Build tools others use
**Examples:** API services, x402 endpoints, templates, libraries
**Success =** others adopt and pay for your tool
**Metric =** API calls, installs, revenue, usage growth
**Time =** build once, sell repeatedly
**Competition =** network effects, first-mover, quality
**Revenue =** usage-based, subscription, per-call
**Skills =** API design, reliability, documentation, distribution
**Agent fit =** GOOD — code-heavy, API-native, scalable

### 6. RESEARCH
**What:** Advance state of the art
**Examples:** Vesuvius Challenge, open scientific problems, benchmarks
**Success =** breakthrough or contribution
**Metric =** papers, benchmarks, citations, open-source adoption
**Time =** months to years
**Competition =** academic/peer recognition
**Revenue =** grants, prizes, IP licensing
**Skills =** deep domain expertise, experimentation, writing
**Agent fit =** MODERATE — needs domain depth, long feedback loops

## Problem Space × H-Level Matrix

| Problem Space | H0 | H1 | H2 | H4 |
|---------------|-----|-----|-----|-----|
| PREDICTION | Metaculus forecasting | Bittensor subnet training | — | — |
| BOUNTY | Simple code tasks | Complex bounties with setup | Security bounties | — |
| MARKETPLACE | — | Chrome extensions, Atlassian apps | Gumroad products | — |
| HACKATHON | — | Code-heavy hackathons | Presentation-heavy | Team hackathons |
| INFRASTRUCTURE | — | API tools, templates | SaaS platforms | — |
| RESEARCH | Literature review | Vesuvius experiments | Lab experiments | — |

## Revenue Characteristics by Problem Space

| Problem Space | Revenue Model | Time to First $ | Revenue Ceiling | Predictability |
|---------------|---------------|-----------------|-----------------|----------------|
| PREDICTION | Tournament prizes | Weeks | $50K+ per tournament | Low (competition) |
| BOUNTY | Per-task reward | Hours | $100-5K per bounty | Medium (volume) |
| MARKETPLACE | Recurring/subscription | Months | $10K+/month | High (if product-market fit) |
| HACKATHON | Prize pool | Days | $1K-100K per event | Low (judges) |
| INFRASTRUCTURE | Usage-based | Months | $5K+/month | High (if adopted) |
| RESEARCH | Grants/prizes | Years | $100K+ per grant | Low (uncertain) |

## Skills Required by Problem Space

| Problem Space | Core Skills | Secondary Skills | Agent Can Learn? |
|---------------|-------------|------------------|------------------|
| PREDICTION | Research, reasoning | Data analysis, writing | YES — fast feedback |
| BOUNTY | Coding, debugging | Security, API knowledge | YES — per-task learning |
| MARKETPLACE | Product dev, UI/UX | Marketing, maintenance | SLOWLY — needs iteration |
| HACKATHON | Prototyping, breadth | Presentation, innovation | MODERATE — needs creativity |
| INFRASTRUCTURE | API design, reliability | Documentation, distribution | YES — code-heavy |
| RESEARCH | Domain expertise | Experimentation, writing | SLOWLY — needs depth |

## How the Oracle Should Use This

1. **Classify every opportunity by problem space** (not just source/category)
2. **Filter by problem space** — show only prediction opportunities, or only bounties
3. **Compare within problem space** — Metaculus vs Bittensor, not Metaculus vs Chrome extension
4. **Track performance per problem space** — what is the agent good at?
5. **Recommend problem spaces** — based on agent capabilities and revenue goals

## Agent Strategy by Problem Space

**Start with:** PREDICTION (Metaculus) — fully autonomous, fast feedback, proven
**Then add:** BOUNTY (code tasks) — clear verification, per-task learning
**Then add:** MARKETPLACE (Chrome extensions) — recurring revenue, product thinking
**Later:** HACKATHON, INFRASTRUCTURE, RESEARCH — need more capability
