# Metaculus Scoring System

## Overview

Metaculus uses proper scoring rules to evaluate forecast accuracy. Scores measure how well predictions align with actual outcomes.

## Score Types

### 1. Peer Score (Main)

**Measures:** Performance relative to community aggregate

**Formula:**
```
peer_score = community_score - your_score
```

Where community_score is the log score of the community prediction.

**Interpretation:**
- Positive = you beat the crowd
- Negative = crowd beat you
- Zero = you matched the crowd

### 2. Baseline Score

**Measures:** Performance relative to a simple prior

**Baseline types:**
- Binary: 50% prior
- Numeric: uniform distribution
- Multiple choice: equal probability per option

**Formula:**
```
baseline_score = baseline_score - your_score
```

### 3. Spot Peer Score

**Measures:** Peer score at Community Prediction (CP) reveal time

**Purpose:** Prevents gaming through frequent updates

**Used in:** Tournament scoring

### 4. Spot Baseline Score

**Measures:** Baseline score at CP reveal time

**Purpose:** Same anti-gaming as spot peer

### 5. Legacy Relative Score

**Status:** Deprecated

**Note:** Historical scoring from old Metaculus. Do not use for new forecasts.

## Scoring Mechanics

### Step 1: Log Score

For binary questions with outcome O and prediction p:

```
If O = Yes: score = log₂(p)
If O = No:  score = log₂(1-p)
```

**Properties:**
- Rewards well-calibrated probabilities
- Penalizes overconfidence
- Maximum score: 0 (perfect prediction)
- Minimum score: -∞ (predicted 0% for event that happened)

### Step 2: Continuous Questions

For numeric questions:

1. Convert CDF to PMF (probability mass function)
2. Calculate log score based on probability mass assigned to actual outcome
3. Score depends on how narrow your prediction was around the truth

### Step 3: Coverage

**Coverage** = fraction of scored questions you forecasted

```
coverage = scored_questions_you_forecasted / total_scored_questions
```

**Impact:** Higher coverage makes your score more reliable and statistically meaningful.

### Step 4: Aggregation

Scores across questions are averaged with question weights:

```
final_score = Σ(weight_i × score_i) / Σ(weight_i)
```

**Weights depend on:**
- Question difficulty
- Question importance
- Tournament rules

## Tournament Scoring

### PEER_TOURNAMENT

```
tournament_score = Σ(peer_scores across all tournament questions)
```

**Key points:**
- Sum, not average
- Coverage matters: forecasting more questions = higher potential score
- Spot scores prevent gaming via frequent updates

### Anti-Gaming Mechanisms

1. **Spot Scores:** Evaluated at CP reveal time, not continuously
2. **Recency Weighting:** More recent forecasts may have higher weight
3. **Coverage Requirements:** Must forecast on many questions to compete

## Score Calculation Examples

### Binary Question Example

```
Question: "Will it rain tomorrow?"
Community prediction: 30%
Your prediction: 70%
Actual outcome: Yes (it rained)

Your log score: log₂(0.70) = -0.515
Community log score: log₂(0.30) = -1.737

Your peer score: -1.737 - (-0.515) = -1.222
(You did worse than the crowd)
```

### Numeric Question Example

```
Question: "What will GDP growth be in 2026?"
Your CDF: centered around 2.5% with ±1% spread
Actual outcome: 2.3%

Your score depends on:
- How much probability mass you assigned near 2.3%
- How narrow your prediction was
- Community's prediction for comparison
```

## Leaderboard Rankings

### Global Leaderboard

```bash
GET /api/leaderboards/global/?score_type=peer
```

### Tournament Leaderboard

```bash
GET /api/leaderboards/project/{tournament_id}/?score_type=peer_tournament
```

### User Position

```bash
GET /api/leaderboards/global/?show_position={user_id}
```

## Score Data Download

### Available Formats

```bash
GET /api/data/  # List available datasets
```

### Score CSV Schema

| Column | Description |
|--------|-------------|
| `question_id` | Question this score is for |
| `user_id` | User who earned this score |
| `username` | Username of the scorer |
| `score_type` | `peer`, `baseline`, `spot_peer`, `spot_baseline` |
| `score` | Score value (higher is better) |
| `coverage` | 0-1 fraction of questions forecasted |

## Best Practices for High Scores

### 1. Coverage First
- Forecast on ALL questions early
- Even rough estimates count
- Coverage multiplier rewards breadth

### 2. Focus on Edge
- Questions where you have domain expertise
- Where your knowledge exceeds the crowd
- Avoid questions you know nothing about

### 3. Calibrate Well
- Use proper probability calibration
- Don't overconfidence
- Update when new information arrives

### 4. Read Comments
- Top forecasters share reasoning
- Community discussion reveals blind spots
- Learn from others' analysis

### 5. Track Resolution
- Know when questions will resolve
- Focus on near-term questions first
- Build reputation on resolvable questions

## Tournament Strategy

### For $50K Tournament (328 questions)

```
Expected value calculation:

1. Coverage: forecast all 328 questions
2. Edge: assume 5% improvement over community
3. Average question prize: $50,000 / 328 = ~$152
4. Your share if 5% better: ~$7.60 per question
5. Expected earnings: 328 × $7.60 = ~$2,493

Note: This is rough estimate. Actual depends on:
- Number of competitors
- Your actual edge per question
- Tournament scoring formula
- Prize distribution rules
```

### Bot Participation

**Tournament settings for bots:**
- `exclude_and_hide`: Bots not visible (default)
- `exclude_and_show`: Bots visible but no prizes
- `include`: Bots compete for prizes
- `bots_only`: Only bots compete

**Check tournament rules before participating!**

## References

- [Metaculus Scores FAQ](https://www.metaculus.com/help/scores-faq/)
- [API Documentation](https://metaculus-metaculus.mintlify.app/api/overview)
- [Tournament Guide](https://metaculus-metaculus.mintlify.app/features/tournaments)
