# AGENTS.md — How to find API keys and resources

## API Keys (stored in /root/workerkit/.env)

```bash
# View keys (never commit these)
cat /root/workerkit/.env

# Available providers:
OPENCODE_API_KEY=sk-fv9...    # opencode-go/mimo-v2.5 (free)
GROQ_API_KEY=gsk_1J...        # groq models (paid, cheap)
CF_API_TOKEN=cfat_A...        # cloudflare R2 storage
HARBOR_API_KEY=sk-harbor...   # harbor framework
```

## Provider Registry (code access)

```python
from providers.registry import ProviderRegistry

reg = ProviderRegistry()
key = reg.get_key("opencode-go")  # returns API key
pricing = reg.get_pricing("groq/llama-3.3-70b-versatile")
cost = reg.estimate_cost(model, prompt_tokens, completion_tokens)
```

## LiveLLM (real-time pricing)

```bash
# Start LiveLLM
cd /root/livellm && npm run serve

# Query pricing
curl http://localhost:3847/v1/market
curl http://localhost:3847/v1/economics/GPT-4o
```

## BATS (budget-aware routing)

```python
from providers.bats import BATS, BudgetState

bats = BATS(reg)
budget = BudgetState(total_usd=0.10, remaining_usd=0.10)
decision = bats.select_model("coding", budget, uncertainty=0.7)
# → {"model": "groq/llama-3.3-70b-versatile", "reason": "high_uncertainty"}
```

## Repos

```bash
/root/workerkit    # main codebase
/root/oracle       # market intelligence
/root/mwgym        # experiment lab
/root/livellm      # pricing data
/root/qdw          # strategy docs
/root/qdw-sandbox  # sandbox experiments
```

## Model selection priority

1. Free models (opencode-go/mimo-v2.5) for routine tasks
2. Cheap models (groq) for medium uncertainty
3. Strong models (claude, gpt-4o) only for high-stakes decisions
4. Always check BATS before using paid models
