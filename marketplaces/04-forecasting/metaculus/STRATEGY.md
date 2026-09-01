# Metaculus Bot Strategy — xev0

## Overview

**Bot Name:** xev0
**Human Username:** xev
**Platform:** Metaculus
**Goal:** Maximize tournament earnings through automated forecasting

## Current Status

| Item | Status | Notes |
|------|--------|-------|
| API Key | ✅ Stored | Agent Vault |
| Bot Name | ✅ Stored | xev0 |
| Human Username | ✅ Stored | xev |
| Tournament | ⚠️ Needs claim | $50K FutureEval, Sep 6 deadline |
| Adapter | ❌ Not built | Need to create oracle adapter |

## Tournament Priority

### FutureEval ($50K) — CRITICAL

- **Deadline:** Sep 6, 2026 (5 days!)
- **Questions:** 328
- **Prize Pool:** $50,000
- **Bot Status:** Check `bot_leaderboard_status` setting

**Action Items:**
1. Create Metaculus account for xev0
2. Get bot token
3. Store in Agent Vault
4. Build adapter
5. Submit forecasts on all questions

## Forecasting Strategy

### Phase 1: Coverage (Days 1-2)

**Goal:** Forecast on ALL 328 questions

**Approach:**
- Initial rough estimates for every question
- Use base rates and reference classes
- Don't worry about accuracy yet, just coverage

**Python:**
```python
import requests

# Get all open questions
questions = client.list_questions(status="open", project=3876, limit=328)

# Submit initial forecasts
for q in questions["results"]:
    if q["type"] == "binary":
        # Start with community prediction if available
        prob = q.get("community_prediction", 0.5)
        client.forecast_binary(q["id"], prob)
    elif q["type"] == "numeric":
        # Generate simple CDF
        cdf = generate_simple_cdf(q)
        client.forecast_numeric(q["id"], cdf)
```

### Phase 2: Refinement (Days 3-4)

**Goal:** Improve forecasts on high-value questions

**Approach:**
- Identify questions with largest prize values
- Research domain-specific information
- Update forecasts based on new information

**Priority Queue:**
```python
def prioritize_questions(questions, prize_values):
    """Rank questions by expected value improvement."""
    scored = []
    for q in questions:
        # Estimate edge (how much you can improve over community)
        edge = estimate_edge(q)
        prize = prize_values.get(q["id"], 0)
        ev = edge * prize
        scored.append((q, ev))
    return sorted(scored, key=lambda x: -x[1])
```

### Phase 3: Monitoring (Day 5)

**Goal:** Track resolution and adjust

**Approach:**
- Monitor question resolutions
- Update forecasts on new information
- Prepare for next tournament

## Question Type Strategies

### Binary Questions

**Base Rate Approach:**
```python
def binary_forecast(question):
    """Simple base rate forecast."""
    # Get category/base rate
    category = question.get("category", "unknown")
    base_rate = get_base_rate(category)
    
    # Adjust for specific question details
    adjustment = analyze_question_details(question)
    
    return base_rate + adjustment
```

### Numeric Questions

**CDF Generation:**
```python
import numpy as np

def numeric_forecast(question):
    """Generate CDF for numeric question."""
    # Get question bounds
    lower = question.get("resolution", {}).get("lower_bound", 0)
    upper = question.get("resolution", {}).get("upper_bound", 100)
    
    # Generate logistic CDF
    x = np.linspace(lower, upper, 201)
    mean = estimate_mean(question)
    std = estimate_std(question)
    
    cdf = 1 / (1 + np.exp(-(x - mean) / std))
    return cdf.tolist()
```

### Multiple Choice

**Probability Allocation:**
```python
def multiple_choice_forecast(question):
    """Allocate probabilities across options."""
    options = question.get("options", [])
    
    # Get base rates for each option
    base_rates = [get_option_base_rate(opt) for opt in options]
    
    # Normalize to sum to 1.0
    total = sum(base_rates)
    return [br / total for br in base_rates]
```

## Edge Estimation

### How to Beat the Crowd

1. **Domain Expertise:** Focus on questions in your knowledge area
2. **Information Advantage:** Find information the crowd hasn't seen
3. **Calibration:** Better calibrated probabilities
4. **Speed:** Update faster when new information arrives

### Edge Calculation

```python
def estimate_edge(question):
    """Estimate how much you can improve over community."""
    # Factors that indicate potential edge:
    # 1. Community is uncertain (wide spread)
    # 2. You have domain knowledge
    # 3. Information is available but not priced in
    
    community_prob = question.get("community_prediction", 0.5)
    uncertainty = abs(community_prob - 0.5) * 2  # 0-1 scale
    
    # Lower uncertainty = harder to beat
    # Higher uncertainty = more opportunity
    return uncertainty * 0.1  # Conservative 10% edge estimate
```

## Risk Management

### Bankroll Management

- Never risk more than 20% of expected earnings on single question
- Diversify across many questions
- Focus on coverage over accuracy

### Anti-Gaming Compliance

- Don't submit rapid updates to manipulate spot scores
- Use natural forecast timing
- Respect tournament rules

## Monitoring Dashboard

### Key Metrics

```python
metrics = {
    "coverage": 0.0,  # % of questions forecasted
    "edge": 0.0,      # Average edge over community
    "ev": 0.0,        # Expected value of forecasts
    "rank": 0,        # Tournament rank
    "score": 0.0,     # Current score
}
```

### Daily Check

```bash
# Check tournament status
curl -H "Authorization: Token $TOKEN" \
  "https://www.metaculus.com/api/leaderboards/project/3876/"

# Check your position
curl -H "Authorization: Token $TOKEN" \
  "https://www.metaculus.com/api/leaderboards/project/3876/?show_position=YOUR_USER_ID"
```

## Files

| File | Purpose |
|------|---------|
| `README.md` | Overview and quick start |
| `API.md` | API reference |
| `SCORING.md` | Scoring system |
| `STRATEGY.md` | This file |
| `adapter.py` | Oracle adapter |
| `bot.py` | Main bot logic |

## Next Steps

1. [ ] Create Metaculus account for xev0
2. [ ] Get bot API token
3. [ ] Store in Agent Vault
4. [ ] Build oracle adapter
5. [ ] Test on sample questions
6. [ ] Submit to FutureEval tournament
7. [ ] Monitor and refine
