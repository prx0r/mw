# Letta Performance Note

## The Issue
Each worker run makes 24+ separate API calls through Letta:
- 16 reasoning events (agent thinking)
- 7 assistant events (agent output)
- 1 tool call (actual work)
- 13 loop_status events (Letta checking)

At ~4s per call through opencode-go, that's 96s+ per run.

## Why
Letta is designed for multi-turn conversations with persistent memory.
Each "turn" in the agentic loop is a separate model call.
The agent thinks → acts → thinks → acts → ... until it decides to stop.

## The Cost
- Latency: 60-120s per worker run
- Tokens: 24x what a single call would use
- No compounding intelligence within a run (separate calls don't share context)

## The Fix Options
1. **Accept it** — Letta provides persistence, this is the tradeoff
2. **Bypass Letta for single-shot** — call model directly, load memory manually
3. **Configure Letta for single-turn** — if possible upstream

## Current State
- Agent works: creates files, uses tools
- File creation: verified (MOLTWOK_SMOKE_OK, x402 ideas)
- Persistence: MemFS with git-backed memory
- Latency: 60-120s per run (known limitation)
