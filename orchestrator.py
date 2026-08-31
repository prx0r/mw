"""Orchestrator — wire the full Moltwork pipeline.

    Opportunity → Campaign → WorkOrder → Run → Receipt → Lab → Harvest

One entry point. Every run produces:
  - A verifiable receipt (WorkerKit)
  - A lab projection record (LabProjector)
  - Asset candidates (Harvester)
  - Capability evidence (CapabilityTracker)
  - Learning observations (ReflectionPipeline)
"""
from __future__ import annotations

import asyncio
import inspect
import time
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

try:
    from workerkit.sdk import WorkerKit, WorkOrder, Run
    from workerkit.core.events import EventLedger
    from workerkit.core.receipts import WorkReceipt
    from workerkit.verify.contracts import AcceptanceContract
    from workerkit.hydra.store import LabProjection
    from workerkit.lab.projection import LabProjector
    from workerkit.lab.reflection import ReflectionPipeline
    from workerkit.harvest.candidates import Harvester
    from workerkit.capabilities import CapabilityTracker
    from workerkit.economics.decisions import DecisionEngine
    from workerkit.campaigns.schema import Campaign, WorkPlan, WorkUnit
    from workerkit.opportunities.schema import Opportunity
except ImportError:
    from sdk import WorkerKit, WorkOrder, Run
    from core.events import EventLedger
    from core.receipts import WorkReceipt
    from verify.contracts import AcceptanceContract
    from hydra.store import LabProjection
    from lab.projection import LabProjector
    from lab.reflection import ReflectionPipeline
    from harvest.candidates import Harvester
    from capabilities import CapabilityTracker
    from economics.decisions import DecisionEngine
    from campaigns.schema import Campaign, WorkPlan, WorkUnit
    from opportunities.schema import Opportunity


@dataclass
class UnitResult:
    """Result of executing a single WorkUnit."""
    work_unit_id: str = ""
    run_id: str = ""
    receipt_hash: str = ""
    gate_decision: str = ""
    cost_usd: float = 0.0
    artifact_count: int = 0
    harvest_candidates: int = 0
    capability_recorded: bool = False
    lab_projected: bool = False
    error: str = ""


@dataclass
class CampaignResult:
    """Result of running a full Campaign."""
    campaign_id: str = ""
    opportunity_id: str = ""
    status: str = ""
    total_units: int = 0
    completed_units: int = 0
    failed_units: int = 0
    total_cost: float = 0.0
    total_reward: float = 0.0
    unit_results: list[UnitResult] = field(default_factory=list)
    learning_proposals: int = 0
    harvest_candidates: int = 0
    capability_count: int = 0
    aborted_early: bool = False
    abort_reason: str = ""
    duration_s: float = 0.0


class Orchestrator:
    """Wire Opportunity → Campaign → Run → Receipt → Lab → Harvest.

    Usage:
        orch = Orchestrator(data_dir="data")
        result = orch.run_campaign(opportunity, campaign)
    """

    def __init__(self, data_dir: str = "data", ledger_db: str = "",
                 projection_db: str = "", worker_id: str = ""):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.worker_id = worker_id

        # Core infrastructure
        ledger_path = ledger_db or str(self.data_dir / "wk-events.db")
        proj_path = projection_db or str(self.data_dir / "hydra.db")

        self.ledger = EventLedger(ledger_path)
        self.projection = LabProjection(proj_path, append_only=False)
        self.projector = LabProjector(self.ledger, self.projection)
        self.wk = WorkerKit(db_path=ledger_path)

        # Subsystems
        self.harvester = Harvester()
        self.capabilities = CapabilityTracker()
        self.reflection = ReflectionPipeline(hydra=self.projection)
        self.decision_engine = DecisionEngine()

        # Personal Lab — wired to the same ledger
        from lab.persistence import MoltworkLab
        self.lab = MoltworkLab(
            data_dir=str(self.data_dir / "lab"),
            worker_id=worker_id or "default",
        )
        self.lab._ledger = self.ledger  # direct reference for rebuild

        # Venues (where work happens)
        self._venues: dict[str, Any] = {}

        # Load existing capabilities
        cap_path = self.data_dir / "capabilities"
        if (cap_path / "capabilities.json").exists():
            try:
                self.capabilities.load(cap_path)
            except Exception:
                pass

    def register_venue(self, name: str, venue):
        """Register a WorkVenue adapter."""
        self._venues[name] = venue

    def discover_opportunities(self, agent_caps: list[str] | None = None,
                               limit: int = 50) -> list[dict]:
        """Discover opportunities across all registered venues.

        Returns unified Opportunity dicts regardless of source venue.
        """
        all_opps = []
        for name, venue in self._venues.items():
            try:
                opps = venue.discover()
                for opp in opps:
                    opp_dict = opp.to_dict() if hasattr(opp, "to_dict") else opp
                    opp_dict["venue"] = name
                    all_opps.append(opp_dict)
            except Exception:
                continue

        # Sort by reward descending
        all_opps.sort(key=lambda o: o.get("reward_usd", 0), reverse=True)

        # Filter by agent capabilities if provided
        if agent_caps:
            filtered = []
            for opp in all_opps:
                opp_caps = set(opp.get("capabilities", []))
                if not opp_caps or opp_caps & set(agent_caps):
                    filtered.append(opp)
            all_opps = filtered

        return all_opps[:limit]

    async def run_campaign(self, opportunity: Opportunity, campaign: Campaign,
                     execute_fn=None, contract: AcceptanceContract | None = None,
                     budget_remaining: float | None = None) -> CampaignResult:
        """Run a full Campaign against an Opportunity.

        execute_fn: optional callable(run_id, work_unit, workspace) -> dict
            If None, simulates execution with a stub artifact.
        contract: AcceptanceContract for verification. Default: empty criteria.
        """
        t0 = time.time()
        result = CampaignResult(
            campaign_id=campaign.campaign_id,
            opportunity_id=opportunity.id,
        )

        if not campaign.work_plan or not campaign.work_plan.work_units:
            result.status = "NO_WORK_PLAN"
            return result

        campaign.status = "ACTIVE"
        best_route = opportunity.best_route()
        cap = contract or AcceptanceContract(criteria=[])

        for wu in campaign.work_plan.work_units:
            # Check budget
            if not campaign.can_continue():
                result.aborted_early = True
                result.abort_reason = "budget exhausted"
                break

            # Decision engine check
            if campaign.spent_usd > 0:
                decision = self.decision_engine.decide(
                    spent=campaign.spent_usd,
                    remaining_budget=campaign.remaining_budget(),
                    p_success=0.5,
                    reward=best_route.reward_usd if best_route else 0,
                    estimated_remaining=wu.estimated_cost_usd,
                )
                if decision.action == "ABORT":
                    result.aborted_early = True
                    result.abort_reason = decision.reason
                    break

            unit_result = await self._execute_unit(
                wu, opportunity, campaign, execute_fn, cap,
                budget_remaining or campaign.remaining_budget(),
            )
            result.unit_results.append(unit_result)

            if unit_result.error:
                result.failed_units += 1
                wu.status = "FAILED"
            else:
                result.completed_units += 1
                wu.status = "COMPLETED"
                campaign.record_cost(unit_result.cost_usd)

            result.total_cost += unit_result.cost_usd

        # Post-campaign: learning
        self._post_campaign_learning(campaign)

        # Persist capabilities
        try:
            self.capabilities.save(self.data_dir / "capabilities")
        except Exception:
            pass

        # Sync lab projection
        try:
            self.projector.sync()
        except Exception:
            pass

        result.status = "COMPLETED" if not result.aborted_early else "ABORTED"
        result.completed_units = sum(1 for u in result.unit_results if not u.error)
        result.failed_units = sum(1 for u in result.unit_results if u.error)
        result.harvest_candidates = len(self.harvester.list_candidates())
        result.capability_count = len(self.capabilities.capabilities)
        result.learning_proposals = len(self.reflection.scan_candidates(min_evidence=1))
        result.duration_s = time.time() - t0
        campaign.status = result.status
        campaign.completed_at = time.time()

        return result

    async def _execute_unit(self, wu: WorkUnit, opportunity: Opportunity,
                      campaign: Campaign, execute_fn, contract,
                      budget_remaining: float) -> UnitResult:
        """Execute a single WorkUnit through the full pipeline."""
        ur = UnitResult(work_unit_id=wu.work_unit_id)

        try:
            # 1. Create WorkOrder
            best_route = opportunity.best_route()
            order = WorkOrder(
                objective=wu.description or wu.title,
                reward_value=str(best_route.reward_usd) if best_route else "0",
                raw={"max_cost": wu.estimated_cost_usd},
            )

            # 2. Start run
            run = self.wk.start(order)
            # Record dependencies (capabilities + task_family for Lab rebuild)
            run.set_dependencies(
                worker_version_id=opportunity.domain,
                skill_version_ids=wu.required_capabilities or [opportunity.domain],
            )
            # Also emit task_family into the event chain
            run.event("task.assigned", {
                "task_family": opportunity.domain,
                "capabilities": wu.required_capabilities or [opportunity.domain],
            })

            # 3. Execute (adapter, callable, or stub)
            if execute_fn is not None:
                exec_result = await self._invoke_execute(
                    execute_fn, run.run.id, wu, order, budget_remaining
                )
                if isinstance(exec_result, Exception):
                    ur.error = f"execute error: {exec_result}"
                    return ur
                if isinstance(exec_result, dict):
                    for art in exec_result.get("artifacts", []):
                        if isinstance(art, dict):
                            run.artifact(
                                name=art.get("name", "output"),
                                content=art.get("content", b""),
                                media_type=art.get("media_type", ""),
                            )
                    for cost_entry in exec_result.get("costs", []):
                        if isinstance(cost_entry, dict):
                            run.cost(
                                cost_entry.get("category", "llm"),
                                cost_entry.get("amount", 0),
                            )
                # WorkerAdapter returns ExecutionResult — map to run artifacts
                from workerkit.adapters.base import ExecutionResult
                if isinstance(exec_result, ExecutionResult):
                    if exec_result.ok and exec_result.output_content:
                        run.artifact(
                            name=f"{wu.work_unit_id}-output.md",
                            content=exec_result.output_content,
                            media_type="text/markdown",
                        )
                    if exec_result.cost_usd > 0:
                        run.cost("llm", exec_result.cost_usd)
                    if exec_result.error:
                        ur.error = exec_result.error
                        return ur
            else:
                # Stub execution
                artifact_content = f"# {wu.title}\n\nExecuted by workerkit orchestrator."
                run.artifact(
                    name=f"{wu.work_unit_id}-output.md",
                    content=artifact_content,
                    media_type="text/markdown",
                )
                run.cost("llm", wu.estimated_cost_usd * 0.1)

            # 4. Verify + Gate
            artifacts = run._artifacts
            artifact = artifacts[0] if artifacts else None
            vr = await self.wk.verify(run, contract, artifact)
            cd = self.wk.gate(run, "SUBMIT", vr, budget_remaining=budget_remaining)

            # 5. Close → Receipt
            receipt = self.wk.close(run, projection=self.projection)
            ur.receipt_hash = receipt.root_hash
            ur.run_id = run.run.id
            ur.gate_decision = cd.decision
            ur.cost_usd = float(run.meter.total_cost)
            ur.artifact_count = len(artifacts)

            # 6. Lab projection
            try:
                self.projector.project_run(run.run.id)
                ur.lab_projected = True
            except Exception:
                pass

            # 7. Harvest
            artifact_paths = [a.name for a in artifacts]
            candidates = self.harvester.harvest(
                run_id=run.run.id,
                artifact_paths=artifact_paths,
                receipt_id=receipt.root_hash,
            )
            ur.harvest_candidates = len(candidates)

            # 8. Capability tracking
            cap_name = wu.required_capabilities[0] if wu.required_capabilities else opportunity.domain
            self.capabilities.record_run(
                run_id=run.run.id,
                capability_name=cap_name,
                accepted=(cd.decision == "ALLOW"),
                cost=ur.cost_usd,
                payout=float(best_route.reward_usd) if best_route and cd.decision == "ALLOW" else 0,
                evaluator_score=0.0,
                task_family=opportunity.domain,
            )
            ur.capability_recorded = True

            # 9. Update Personal Lab
            try:
                self.lab.record_run(
                    run=run,
                    receipt=receipt,
                    gate_decision=cd.decision,
                    reward=float(best_route.reward_usd) if best_route and cd.decision == "ALLOW" else 0,
                    task_family=opportunity.domain,
                    capabilities_used=wu.required_capabilities or [opportunity.domain],
                )
            except Exception:
                pass

            # 10. Record outcome in campaign
            wu.receipt_ids.append(receipt.root_hash)
            wu.artifact_paths.extend(artifact_paths)
            wu.cost_usd = ur.cost_usd

        except Exception as e:
            ur.error = str(e)

        return ur

    async def _invoke_execute(self, execute_fn, run_id: str, wu: WorkUnit,
                              order: WorkOrder, budget_remaining: float):
        """Invoke execute_fn whether it's a WorkerAdapter, async callable, or sync callable."""
        from workerkit.adapters.base import WorkerAdapter, RunContext

        # Case 1: WorkerAdapter — use its async execute protocol
        if hasattr(execute_fn, "execute") and hasattr(execute_fn, "runtime"):
            context = RunContext(
                workspace=f"/tmp/moltwork-run/{run_id}",
                budget_remaining=budget_remaining,
                timeout_seconds=300,
            )
            return await execute_fn.execute(order, context)

        # Case 2: async callable
        if callable(execute_fn):
            if asyncio.iscoroutinefunction(execute_fn):
                return await execute_fn(run_id, wu, order)
            # sync callable — run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, execute_fn, run_id, wu, order)

        return ValueError(f"execute_fn must be a WorkerAdapter or callable, got {type(execute_fn)}")

    def _post_campaign_learning(self, campaign: Campaign) -> None:
        """After campaign: feed outcomes into reflection, scan for proposals."""
        # Record observations from campaign results
        for wu in (campaign.work_plan.work_units if campaign.work_plan else []):
            if wu.status == "COMPLETED":
                self.reflection.observe(
                    run_id=wu.work_unit_id,
                    evaluation=0.8,
                    outcome="won",
                )
            elif wu.status == "FAILED":
                self.reflection.observe(
                    run_id=wu.work_unit_id,
                    evaluation=0.2,
                    outcome="lost",
                    failure_reason="work_unit_failed",
                )

        # Scan for learning candidates
        candidates = self.reflection.scan_candidates(min_evidence=3)

        # Save Lab state
        try:
            self.lab.save()
        except Exception:
            pass

    def get_lab_profile(self) -> str:
        """Get the worker's Lab profile — the single-player killer feature."""
        return self.lab.profile()

    def get_lab_summary(self) -> dict:
        """Get machine-readable worker profile."""
        return self.lab.summary()

    def rebuild_lab(self) -> dict:
        """Rebuild Lab from EventLedger. Real rebuild, not simulated."""
        stats = self.lab.rebuild_from_ledger(self.ledger)
        self.lab.save()
        return stats
