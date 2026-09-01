# Metaculus Lab Setup — Lessons from Telegraph

**Date:** 2026-09-01
**Status:** Pipeline live, 101 questions ingested

---

## What Telegraph Did Wrong (And What We Learn)

### 1. Over-engineered early
**Telegraph mistake:** Built BM25, sigmoid, three-band scoring before testing simple word overlap.
**Metaculus lesson:** Start with community_prediction as baseline. Don't build complex forecasting until we beat it.

### 2. Didn't submit early enough
**Telegraph mistake:** Burned hours on algorithm iterations while network evaluated slowly.
**Metaculus lesson:** Submit TODAY. Coverage > accuracy. The scoring formula rewards early, broad participation.

### 3. Missed domain knowledge
**Telegraph mistake:** Champion used curated keyword lists per intent. We used generic algorithms.
**Metaculus lesson:** Each question type needs domain-specific approach. Binary ≠ numeric ≠ multiple_choice.

### 4. Got close but not close enough
**Telegraph mistake:** 11-14/15 on ordering. Champion gets 15/15.
**Metaculus lesson:** Don't aim for perfect. Aim for better than community average on enough questions.

### 5. No tracking system
**Telegraph mistake:** Had to reverse-engineer champion from WASM binaries.
**Metaculus lesson:** Log everything. Every forecast, every score, every update.

---

## The Lab Setup

### Directory Structure

```
oracle/marketplaces/04-forecasting/metaculus/
├── MASTER-GUIDE.md          # API, scoring, strategy
├── API.md                   # Detailed API reference
├── SCORING.md               # Scoring system deep dive
├── STRATEGY.md              # Bot strategy
├── bot.py                   # Main bot (dry-run + submit)
├── adapter.py               # Oracle adapter
├── lab/
│   ├── LAB-SETUP.md         # This file
│   ├── forecasts/           # Every forecast logged
│   ├── scores/              # Score tracking
│   ├── experiments/         # Algorithm experiments
│   └── lessons/             # What worked, what didn't
```

### The Rules (from Telegraph)

1. **Submit first, optimize later** — Coverage is 50% of scoring
2. **Never skip a question** — Even 50% guess beats 0%
3. **Log everything** — If it's not in the log, it didn't happen
4. **One change at a time** — Don't iterate 3 things simultaneously
5. **Check leaderboard daily** — Know where you stand

---

## Phase 1: Coverage (TODAY)

### Goal: Forecast on ALL 101 questions

```bash
# Dry run first
cd /root/mwgym
PYTHONPATH=/root python3 -c "
from mwgym.metaculus import MetaculusClient
import os

client = MetaculusClient(os.environ['METACULUS_API_KEY'])
questions = client.list_questions(status='open', limit=200)

print(f'Found {len(questions)} questions')
for q in questions:
    print(f'  [{q.question_id}] {q.title[:50]} type={q.question_type}')
"

# Then submit
python3 /root/oracle/marketplaces/04-forecasting/metaculus/bot.py
```

### Initial Forecast Strategy

| Question Type | Strategy | Time |
|---------------|----------|------|
| Binary | Use community_prediction if available, else 50% | 1 sec |
| Numeric | Uniform CDF (lazy but gets coverage) | 2 sec |
| Multiple Choice | Equal probability per option | 1 sec |

**This is not about accuracy. This is about COVERAGE.**

---

## Phase 2: Refinement (This Week)

### Goal: Improve forecasts on high-value questions

1. **Sort by prize pool** — Tournament questions first
2. **Read resolution criteria** — Understand what "yes" means
3. **Check comments** — Top forecasters share reasoning
4. **Update forecasts** — New info = new forecast

### What to Track

```json
{
  "question_id": 45387,
  "title": "Will X happen?",
  "type": "binary",
  "first_forecast": "2026-09-01",
  "first_forecast_value": 0.5,
  "updates": [
    {"date": "2026-09-02", "value": 0.6, "reason": "new article"},
    {"date": "2026-09-03", "value": 0.65, "reason": "more data"}
  ],
  "resolved": null,
  "score": null,
  "lessons": ""
}
```

---

## Phase 3: Algorithm Development (Next Week)

### Goal: Beat community prediction consistently

Only AFTER Phase 1 and 2 are complete.

### The Telegraph Lesson Applied

Don't build:
- Complex scoring algorithms
- ML models
- Multi-signal fusion

Build:
- Domain knowledge per question category
- Better base rates
- Faster information processing

### Question Categories to Master

| Category | Base Rate | Approach |
|----------|-----------|----------|
| Politics | 50% (polls) | Read polls, adjust for house effects |
| Science | 30% (conservative) | Check replication status |
| Technology | 40% (trend-based) | Check development timelines |
| Economics | 50% (market odds) | Check prediction markets |
| Geopolitics | 20% (rare events) | Check expert consensus |

---

## The Dashboard

### Key Metrics to Track

```bash
# Check your position
curl -s "https://www.metaculus.com/api/leaderboards/project/33022/" \
  -H "Authorization: Token $TOKEN" | python3 -c "
import json,sys
d = json.load(sys.stdin)
for e in d.get('entries',[])[:10]:
    print(f'{e[\"rank\"]:3d}. {e[\"user\"][\"username\"]:20s} score={e[\"score\"]:7.2f} coverage={e[\"coverage\"]:.0%}')
"
```

### Daily Check Routine

1. **Morning:** Check new questions, submit rough forecasts
2. **Midday:** Check leaderboard position
3. **Evening:** Update forecasts on resolved or closing questions
4. **Weekly:** Review scores, identify patterns

---

## What Success Looks Like

### Week 1
- 101 questions forecasted (100% coverage)
- Rank: Top 50%
- Score: Positive (beat community on some questions)

### Month 1
- 300+ questions forecasted
- Rank: Top 20%
- Score: Consistently positive
- Prize: Some tournament payout

### Month 3
- 500+ questions forecasted
- Rank: Top 10%
- Score: Top performer
- Prize: Regular tournament payouts

---

## The Telegraph Takeaway

> **"The champion's moat wasn't the algorithm — it was the domain-specific token knowledge."**

For Metaculus, the moat is:
1. **Coverage** — forecast everything, early
2. **Domain knowledge** — understand each question deeply
3. **Speed** — process new information faster
4. **Calibration** — know what you know and don't know

Don't over-engineer. Just be consistently good at the basics.

---

*Lab setup 2026-09-01. Learn from telegraph: submit early, track everything, don't over-engineer.*
