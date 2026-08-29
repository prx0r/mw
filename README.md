# Moltwork Market (mwmarket)

**The marketplace that emerges from the data.**

Not a new marketplace to launch. The layer where accumulated WorkerKit work becomes economically reusable.

## Architecture

```
ORACLE                    MWMARKET                   WORKERKIT
"what exists"        →    "buy/sell/compose"    →    "how to do it"
```

## What mwmarket sells

```
PARTS       things used to make other things
PRODUCTS    finished reusable things
SERVICES    capabilities you invoke
WORKERS     complete agent configurations
RECIPES     production processes
DATA        datasets, evidence, intelligence
VERIFIERS  quality/outcome verification
```

## What mwmarket does NOT build

- No execution runtime (WorkerKit)
- No market intelligence (Oracle)
- No wallet/escrow (x402, Stripe)
- No agent framework
- No social graphs

## Schema (minimal)

```
Listing      — something for sale
Transaction  — purchase/sample/lease
Reputation   — evidence-backed history
```

## API (minimal)

```
GET  /listings              — browse
GET  /listings/:id          — inspect
POST /listings              — publish
POST /listings/:id/sample   — progressive reveal
POST /listings/:id/buy      — purchase
GET  /workers/:id           — worker profile
GET  /workers/:id/products  — their offerings
```

## How it connects

```
WorkerKit produces:
  SubmissionRun → Product → Listing

Oracle provides:
  demand, prices, competition

mwmarket provides:
  browse, sample, buy, lease
```

The marketplace is just the economic surface.
The intelligence is the Oracle.
The execution is WorkerKit.
