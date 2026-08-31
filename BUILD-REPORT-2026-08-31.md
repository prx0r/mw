# Build Report — 2026-08-31 06:00 UTC

## What's Running
- runtime-letta: UP on :3000 (PID 3190968)
- Model: opencode-go/mimo-v2.5
- Stateful sessions (memory persists across turns)

## What's Wired (tested, working)
1. **FakeWorkerRuntime** — ms-speed orchestration tests
2. **MockHarbor** — Docker-free trials + regrade
3. **RunBinding** — content-addressed statements
4. **GraphStore** — 39 nodes, 12 edges in hydradb.db
5. **Regrade** — v0/v1/v2 with calibration
6. **LabBrief** — compounds evidence across campaigns
7. **AutomationResolver** — API→MCP→WebMCP→human ladder
8. **MarketPacks** — Roblox/Upwork/Etsy/Hackathon
9. **Opportunity schema** — execution_steps, human_deps
10. **Campaign lifecycle** — create/run/grade/regrade/outcome

## What's NOT Wired
1. **Harbor CLI** — `harbor run` not called (MockHarbor only)
2. **Trace2Skill** — vendor/ cloned, never called
3. **GEPA** — vendor/ cloned, never called
4. **Letta single-turn** — trying stateless:true now
5. **HydraDB over Bolt** — SQLite only, HTTP client ready
6. **Real submissions** — all synthetic, Letta produces files but slow

## Letta Performance
- 24+ model calls per run (16 reasoning + 7 assistant + 1 tool)
- ~60-120s per run
- File creation WORKS (verified: MOLTWOK_SMOKE_OK, x402 ideas)
- Stream never terminates (upstream issue, file exists as success)

## HydraDB Status
- SQLite: data/hydradb.db (39 nodes, 12 edges)
- lab_runs: 1 row (from earlier test)
- HTTP client ready for when HydraDB Bolt is available

## Test Results
- 91/91 workerkit invariants PASS
- 17/17 Letta adapter tests PASS
- 63/63 qdw unit tests PASS
- E2E: opportunity → campaign → run → grade → regrade → graph PASS

## What Was Built This Session
- mw_labkit/ — FakeWorkerRuntime, MockHarbor, RunBinding
- regrade.py — v0/v1/v2 assessor versions
- lab_brief.py — evidence compounding
- hydra/graph.py — fixed schema to match existing DB
- hydra/client.py — Bolt/HTTP or SQLite fallback
- ontology.py — shared types (ExecutionStep, HumanDependency)
- campaign.py — auto-projects to graph
- market_packs.py — 4 researched packs
- automation.py — resolver ladder
- runtime-letta fixes — singleton, Write tools, session.close

## Immediate Next Steps
1. Run 10 real Letta campaigns (slow but works)
2. Wire Harbor CLI for real trials
3. Test Trace2Skill on Letta trajectories
4. Wire HydraDB over Bolt when available
