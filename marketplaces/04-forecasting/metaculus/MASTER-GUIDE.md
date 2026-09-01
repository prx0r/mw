# Metaculus Master Guide — xev0 Bot

## Account Setup

1. Create human account: https://www.metaculus.com/accounts/signup/
2. Username: `xev`
3. Go to Settings → My Forecasting Bots → Create Bot
4. Bot username: `xev0`
5. Copy API token

## API Keys (in Agent Vault)

| Key | Value | Status |
|-----|-------|--------|
| `METACULUS_API_KEY` | `04a3c97a97707c9edcbc9eb5a67c3a1d7212ac7f` | ✅ Working |
| `METACULUS_BOT_NAME` | `xev0` | ✅ Stored |
| `METACULUS_USERNAME` | `xev` | ✅ Stored |

## API Endpoints

### Base URL
```
https://www.metaculus.com/api2/
```

### Authentication
```bash
Authorization: Token 04a3c97a97707c9edcbc9eb5a67c3a1d7212ac7f
```

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api2/questions/?status=open` | GET | List open questions |
| `/api2/questions/{id}/` | GET | Get question details |
| `/api2/questions/forecast/` | POST | Submit forecasts |
| `/api2/questions/withdraw/` | POST | Withdraw forecasts |
| `/api/leaderboards/project/{id}/` | GET | Tournament leaderboard |
| `/api/leaderboards/global/` | GET | Global leaderboard |

### Submit Forecast (Binary)
```bash
POST /api2/questions/forecast/
Content-Type: application/json

[{
  "question": 12345,
  "probability_yes": 0.65
}]
```

### Submit Forecast (Numeric/CDF)
```bash
POST /api2/questions/forecast/
Content-Type: application/json

[{
  "question": 12345,
  "continuous_cdf": [0.0, 0.01, ..., 1.0]  // 201 points
}]
```

### Submit Forecast (Multiple Choice)
```bash
POST /api2/questions/forecast/
Content-Type: application/json

[{
  "question": 12345,
  "probability_yes_per_category": {"option1": 0.3, "option2": 0.5, "option3": 0.2}
}]
```

## Bot Rules

1. **Bot must post comment explaining reasoning alongside each forecast**
2. **One prize-eligible bot per user**
3. **Must be willing to share code/description of how bot works**
4. **Metaculus can inspect code**

## Tournament Scoring

### How It Works
- **Peer Score**: Your score vs community aggregate
- **Coverage**: % of questions you forecasted (higher = better)
- **Prize**: Proportional to (sum of peer scores)²
- **Hidden Period**: Community prediction hidden at start → rewards early forecasting

### Key Rules
1. **Forecast EVERY question early** — coverage matters enormously
2. **Don't extremize** — 99% forecasts get punished hard when wrong
3. **Sweep standing forecasts weekly** — time-averaged scoring
4. **Prizes below $50 not paid** (redistributed upward)

### Prize Formula
```
prize_share = (your_peer_score_sum)² / (sum of all (peer_score_sum)²)
```

## Active Tournaments (Check Live)

| Tournament | Prize | Status |
|------------|-------|--------|
| Summer 2026 FutureEval Bot | $50,000 | Ends in 5 days! |
| Metaculus Cup Summer 2026 | $5,000 | Ends 1 day |
| US Midterms 2026 | $10,000 | 2 months |
| Labor Automation | $35,000 | 9 years |
| ACX 2026 | $10,000 | 4 months |
| Market Pulse Challenge | $7,500 | 2 weeks |

## Strategy

### Phase 1: Coverage (NOW)
- Get API working
- Submit rough forecasts on ALL open questions
- Don't worry about accuracy, just coverage

### Phase 2: Refinement
- Research high-value questions
- Update forecasts based on new info
- Focus on questions with hidden period ending soon

### Phase 3: Monitoring
- Track leaderboard position
- Update forecasts as info changes
- Withdraw from questions you can't forecast well

## Files

| File | Purpose |
|------|---------|
| `README.md` | This file |
| `API.md` | Detailed API reference |
| `SCORING.md` | Scoring system deep dive |
| `STRATEGY.md` | Bot forecasting strategy |
| `bot.py` | Main bot code |
| `adapter.py` | Oracle adapter |
