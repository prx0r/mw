# mwmarket

**The marketplace that emerges from the data.**

Not a new marketplace to launch. The layer where accumulated WorkerKit work becomes economically reusable.

## What it sells

```
PART       reusable intermediate artifact
PRODUCT    finished reusable thing
SERVICE    capability you invoke
WORKER     complete agent configuration
RECIPE     production process
DATA       datasets, evidence, intelligence
VERIFIER  quality/outcome verification
```

## What it does NOT build

- No execution runtime (workerkit)
- No market intelligence (oracle)
- No wallet/escrow (x402, Stripe)
- No agent framework

## Quick start

```python
from mwmarket.api import MarketAPI
from mwmarket.schema import Listing, WorkerProfile

market = MarketAPI()
listing = Listing(type="product", title="Research Report", price=5.0)
market.publish_listing(listing)
```

## Related repos

- `workerkit/` — economic evidence kernel
- `mwgo/` — consumer product
- `repute/` — oracle (market intelligence)
