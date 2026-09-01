# Metaculus — Forecasting Tournament Marketplace

**Category:** Forecasting / Prediction Markets
**URL:** https://www.metaculus.com
**Revenue Model:** Prize pools ($50K+ tournaments)
**Autonomy Level:** H0 (fully autonomous after bot setup)

---

## Quick Start

```bash
# API base
API="https://www.metaculus.com/api2"

# Auth
TOKEN=$(agent-vault vault credential get METACULUS_API_KEY --vault oracle)
HEADERS="Authorization: Token $TOKEN"

# Get questions
curl -H "$HEADERS" "$API/questions/?limit=10&status=open"

# Submit forecast (binary)
curl -X POST -H "$HEADERS" -H "Content-Type: application/json" \
  "$API/questions/12345/forecast/" \
  -d '{"probability": 0.65}'

# Get tournament leaderboard
curl -H "$HEADERS" "$API/leaderboards/project/3876/"
```

## Bot Configuration

| Key | Value | Source |
|-----|-------|--------|
| `METACULUS_API_KEY` | `04a3c97a...` | Agent Vault |
| `METACULUS_BOT_NAME` | `xev0` | Agent Vault |
| `METACULUS_USERNAME` | `xev` | Agent Vault |

## Tournaments

### Active Tournaments

| Tournament | ID | Prize Pool | Status |
|------------|-----|-----------|--------|
| FutureEval | 3876 | $50,000 | Active (Sep 6 deadline!) |
| AI Forecasting | TBD | TBD | Check API |

### Tournament Lifecycle

```
Announcement → Forecasting → Close → Resolution → Prizes
     ↓              ↓          ↓         ↓          ↓
  start_date   forecasting  close_date  resolve   distribute
               _end_date                          prizes
```

## Scoring System

### Score Types

| Type | Description | Use Case |
|------|-------------|----------|
| `peer` | vs community aggregate | Main leaderboard |
| `baseline` | vs simple prior | Quality measure |
| `spot_peer` | peer score at CP reveal time | Tournament anti-gaming |
| `spot_baseline` | baseline at CP reveal time | Tournament anti-gaming |

### Scoring Formula

```
Binary: score = log₂(p) if O=Yes, log₂(1-p) if O=No
Continuous: CDF → PMF → log score
Coverage: fraction of scored questions forecasted
Final: weighted average across questions
```

### Tournament Scoring

```
PEER_TOURNAMENT = sum(peer_scores across all tournament questions)
```

## API Endpoints

### Questions

```
GET  /api2/questions/                    — list questions
GET  /api2/questions/{id}/               — single question
POST /api2/questions/{id}/forecast/      — submit forecast
GET  /api2/questions/{id}/forecasts/     — get forecasts
```

### Tournaments

```
GET  /api/projects/{id}/                 — tournament details
GET  /api/leaderboards/project/{id}/     — tournament leaderboard
GET  /api/leaderboards/global/           — global leaderboard
```

### User

```
GET  /api/user/                          — current user
GET  /api/users/{id}/                    — user profile
GET  /api/users/{username}/              — user by username
```

### Data Downloads

```
GET  /api/data/                          — available datasets
GET  /api/scores/                        — score data
```

## Bot Participation Rules

| Setting | Value | Meaning |
|---------|-------|---------|
| `bot_leaderboard_status` | `include` | Bots compete for prizes |
| Default | `exclude_and_show` | Bots shown but no prizes |

**Note:** Check tournament rules — some tournaments may set `exclude_and_hide` for bots.

## Question Types

| Type | Input Format | Example |
|------|-------------|---------|
| `binary` | probability 0-1 | "Will X happen?" → 0.65 |
| `numeric` | 201-point CDF | "How many Y?" → [0, 0.01, ...] |
| `multiple_choice` | probs sum to 1.0 | "Which option?" → [0.3, 0.5, 0.2] |
| `date` | date prediction | "When will Z?" → "2026-12-31" |

## Forecast Submission

### Binary Question

```python
import requests

headers = {"Authorization": "Token YOUR_TOKEN"}
response = requests.post(
    "https://www.metaculus.com/api2/questions/12345/forecast/",
    headers=headers,
    json={"probability": 0.65}
)
```

### Numeric Question (CDF)

```python
import numpy as np

# Generate 201-point CDF
x = np.linspace(lower_bound, upper_bound, 201)
cdf = 1 / (1 + np.exp(-(x - mean) / std))  # logistic CDF

response = requests.post(
    f"https://www.metaculus.com/api2/questions/{question_id}/forecast/",
    headers=headers,
    json={"continuous_cdf": cdf.tolist()}
)
```

## Strategy

### Tournament Play

1. **Coverage first** — forecast on ALL questions early
2. **Focus on edge** — questions where you have domain knowledge
3. **Track comments** — top forecasters' reasoning is public
4. **Don't game** — spot scores prevent update manipulation

### Expected Value

```
EV = Σ(probability_of_winning × prize_pool_share) - compute_cost

For $50K tournament with 328 questions:
- Average question: ~$152 prize value
- If you can beat community by 5%: ~$7.60/question
- 328 questions × $7.60 = ~$2,493 expected earnings
```

## Files

| File | Purpose |
|------|---------|
| `README.md` | This file |
| `API.md` | Detailed API reference |
| `SCORING.md` | Scoring system deep dive |
| `STRATEGY.md` | Bot forecasting strategy |
| `adapter.py` | Oracle adapter for ingestion |

## Related

- `data/sick-oracle-moltwork` — Metaculus ranked as top opportunity
- `ORACLE-SPEC.md` — H0 classification for forecasting
