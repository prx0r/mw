# oracle

**The map of machine-work markets.**

20 API routes. 12 models. 27 adapters. 441 opportunities. 576 services. 882 observations.

## What it does

- Observes demand, supply, and markets across the ecosystem
- Normalizes opportunities into a canonical graph
- Provides intelligence to WorkerKit and mwmarket
- Tracks historical market state

## Quick start

```python
from oracle.sdk import Oracle

o = Oracle()
print(o.pulse())           # market snapshot
print(o.work(skill="python"))  # find work
print(o.brief(skills="solidity"))  # agent briefing
```

## API routes

```
GET /pulse          — market snapshot
GET /work           — work opportunities
GET /svc            — services
GET /sub            — subnets
GET /demand         — cross-layer demand
GET /compare        — platform comparison
GET /brief          — agent briefing
GET /supply         — supply data
GET /trends         — market trends
GET /boards         — seller boards
GET /econ           — economic data
GET /metrics        — market metrics
GET /history        — historical data
GET /signals        — market signals
GET /opportunities  — all opportunities
GET /markets        — market list
GET /settlements    — settlement data
GET /h-levels       — human intervention levels
GET /work-receipts  — WorkerKit receipts
```

## Models

```
Source, Market, Actor, Capability, Opportunity,
Service, IncentiveMarket, Observation, Submission,
Outcome, Payment, Prediction, WorkReceiptRef
```

## Feeds

```
work.py   — work opportunity feed
svc.py    — service feed
sig.py    — signal feed
```

## Related repos

- `workerkit/` — economic evidence kernel (produces WorkReceipts)
- `mwmarket/` — marketplace (listings, transactions)
- `mwgo/` — consumer product
- `get-me-money/` — original earning loop
