"""wk_run — Run a real task through a persistent Letta worker.

Usage:
    python wk_run.py --worker researcher-v1 --task "Your task description"
    python wk_run.py --worker researcher-v1 --task-file task.md
    python wk_run.py --worker researcher-v1 --task "Hackathon idea gen" --budget 2.0

Wires: LettaServiceAdapter → Orchestrator → real Letta worker → receipt → Lab
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


async def run_task(worker_id: str, task: str, budget: float = 2.0,
                   data_dir: str = "data", service_url: str = "http://localhost:3000"):
    """Run a single task through the full Moltwork pipeline with a real worker."""
    from orchestrator import Orchestrator
    from adapters.direct import DirectAdapter
    from opportunities.schema import Opportunity, OpportunityRoute
    from campaigns.schema import Campaign, WorkPlan, WorkUnit
    from verify.contracts import AcceptanceContract, Criterion

    print(f"\n{'='*60}")
    print(f"MOLTWORK RUN — {worker_id}")
    print(f"{'='*60}")
    print(f"Task: {task[:80]}{'...' if len(task) > 80 else ''}")
    print(f"Budget: ${budget:.2f}")

    # 1. Create adapter — direct opencode-go (reliable, no App Server dependency)
    adapter = DirectAdapter(worker_id=worker_id)
    health = await adapter.health()
    print(f"Worker: {worker_id} (runtime: {health.runtime}, model: {adapter.model})")

    # 2. Create a synthetic Opportunity (will be replaced by Oracle feed later)
    opportunity = Opportunity(
        id=f"run-{int(time.time())}",
        source="direct",
        kind="GIG",
        domain="research",
        title=task[:100],
        description=task,
        reward_model="FIXED",
        reward_usd=budget * 3,  # assume 3x budget as target reward
        routes=[
            OpportunityRoute(
                route_id="standard",
                name="Standard",
                reward_usd=budget * 3,
                required_capabilities=["research"],
            ),
        ],
        required_capabilities=["research"],
    )

    # 3. Create Campaign with single WorkUnit
    campaign = Campaign(
        campaign_id=f"camp-{int(time.time())}",
        opportunity_id=opportunity.id,
        route_id="standard",
        budget_usd=budget,
        cost_cap_usd=budget,
        work_plan=WorkPlan(
            plan_id=f"plan-{int(time.time())}",
            strategy="single-task",
            work_units=[
                WorkUnit(
                    work_unit_id="wu-1",
                    title=task[:100],
                    description=task,
                    required_capabilities=["research"],
                    estimated_cost_usd=budget * 0.8,
                ),
            ],
        ),
    )

    # 4. Create Orchestrator with worker_id
    orch = Orchestrator(data_dir=data_dir, worker_id=worker_id)

    # 5. Simple acceptance contract
    contract = AcceptanceContract(criteria=[
        Criterion(name="has_output", description="output not empty", check_type="content_min", required=True),
    ])

    # 6. Execute
    print(f"\nExecuting...")
    t0 = time.time()
    result = await orch.run_campaign(
        opportunity, campaign,
        execute_fn=adapter,
        contract=contract,
        budget_remaining=budget,
    )
    elapsed = time.time() - t0

    # 7. Report
    print(f"\n{'='*60}")
    print(f"RESULT")
    print(f"{'='*60}")
    print(f"Status:      {result.status}")
    print(f"Units:       {result.completed_units} completed, {result.failed_units} failed")
    print(f"Cost:        ${result.total_cost:.4f}")
    print(f"Duration:    {elapsed:.1f}s")

    if result.unit_results:
        ur = result.unit_results[0]
        print(f"Run ID:      {ur.run_id}")
        print(f"Receipt:     {ur.receipt_hash[:16]}...")
        print(f"Gate:        {ur.gate_decision}")
        print(f"Lab:         {'projected' if ur.lab_projected else 'not projected'}")
        if ur.error:
            print(f"Error:       {ur.error}")

    # 8. Show lab profile
    try:
        profile = orch.get_lab_profile()
        if profile:
            print(f"\n--- Lab Profile ---")
            print(profile[:500])
    except Exception:
        pass

    # 9. Show learning observations
    print(f"\nLearning:    {orch.reflection._total_runs} observations")
    candidates = orch.reflection.scan_candidates(min_evidence=2)
    if candidates:
        print(f"Candidates:  {len(candidates)}")
        for c in candidates[:3]:
            print(f"  - {c.content} (evidence: {c.evidence_runs})")

    print(f"{'='*60}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Run a task through a Moltwork Letta worker")
    parser.add_argument("--worker", "-w", default="researcher-v1", help="Worker ID")
    parser.add_argument("--task", "-t", help="Task description")
    parser.add_argument("--task-file", help="Read task from file")
    parser.add_argument("--budget", "-b", type=float, default=2.0, help="Budget in USD")
    parser.add_argument("--data-dir", default="data", help="Data directory")
    parser.add_argument("--service-url", default="http://localhost:3000", help="Runtime-letta URL")

    args = parser.parse_args()

    task = args.task
    if args.task_file:
        task = Path(args.task_file).read_text()
    if not task:
        print("Error: provide --task or --task-file")
        sys.exit(1)

    result = asyncio.run(run_task(
        worker_id=args.worker,
        task=task,
        budget=args.budget,
        data_dir=args.data_dir,
        service_url=args.service_url,
    ))
    sys.exit(0 if result and result.status == "COMPLETED" else 1)


if __name__ == "__main__":
    main()
