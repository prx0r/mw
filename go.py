"""Moltwork Go — one command from an existing agent to the earning loop.

This module deliberately does not choose a new agent framework. It activates the
agent with Moltwork, mirrors the wallet-safety task to the existing Human Task
queue, syncs executable work from the Oracle, and calls the existing earn cycle.

Run:
    python -m get_me_money.go

Moltbook agents can set a temporary (one-hour) identity token in
MOLTBOOK_IDENTITY_TOKEN. Never provide a permanent Moltbook API key here.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import click
import httpx

from get_me_money.config import Config
from get_me_money.human_tasks import APPROVAL, create_task
from get_me_money.ledger import save_opportunity
from get_me_money.models import (
    ExecutionMode,
    Opportunity,
    OpportunityType,
    Platform,
    TaskCategory,
)
from get_me_money.oracle_feeds import OracleFeeds, WorkOpportunity

GO_STATE_FILE = "go-state.json"
GO_CLIENT_ID_FILE = "go-client-id"


_SOURCE_PLATFORM = {
    "taskmarket": Platform.TASKMARKET,
    "moltjobs": Platform.MOLTJOBS,
    "superteam": Platform.SUPERTEAM,
    "algora": Platform.ALGORA,
    "opire": Platform.OPIRE,
    "bounty": Platform.BOUNTY,
    "bountybook": Platform.CUSTOM,
    "gigs": Platform.GIGS,
    "gigs.sh": Platform.GIGS,
}

_CATEGORY = {
    "research": TaskCategory.RESEARCH,
    "code": TaskCategory.CODE_FEATURE,
    "coding": TaskCategory.CODE_FEATURE,
    "data": TaskCategory.DATA_EXTRACTION,
    "content": TaskCategory.CONTENT,
    "documentation": TaskCategory.DOCUMENTATION,
    "testing": TaskCategory.TESTING,
    "design": TaskCategory.DESIGN,
}


def _get_or_create_client_id(config: Config) -> str:
    """Persistent local idempotency key for generic agents. Not a secret."""
    path = config.data_dir / GO_CLIENT_ID_FILE
    if path.exists():
        value = path.read_text().strip()
        if value:
            return value
    import uuid
    value = f"client-{uuid.uuid4().hex}"
    path.write_text(value)
    return value


def _activate(base_url: str, name: str, runtime: str, moltos_agent_id: str, client_id: str) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    # This MUST be a temporary Moltbook identity token, never the bot's API key.
    moltbook_token = os.getenv("MOLTBOOK_IDENTITY_TOKEN", "").strip()
    if moltbook_token:
        headers["X-Moltbook-Identity"] = moltbook_token

    body = {"name": name, "runtime": runtime, "moltos_agent_id": moltos_agent_id, "client_id": client_id}
    with httpx.Client(timeout=20) as client:
        response = client.post(f"{base_url.rstrip('/')}/api/go/activate", json=body, headers=headers)
        response.raise_for_status()
        return response.json()


def _save_public_state(config: Config, activation: dict[str, Any]) -> Path:
    """Persist public activation state only; never identity tokens or wallet secrets."""
    state = {
        "worker": activation.get("worker", {}),
        "identity": activation.get("identity", {}),
        "wallet": activation.get("wallet", {}),
        "session": activation.get("session", {}),
    }
    path = config.data_dir / GO_STATE_FILE
    path.write_text(json.dumps(state, indent=2, default=str))
    return path


def _mirror_human_task(activation: dict[str, Any]) -> None:
    task = activation.get("human_task") or {}
    if not task:
        return
    create_task(
        title=task.get("title", "Review your agent's work wallet"),
        description=task.get("description", "Review wallet safety settings."),
        task_type=APPROVAL,
        priority="normal",
        agent_id=(activation.get("worker") or {}).get("id", ""),
        effort_seconds=30,
        requested_action="review_wallet_safety",
        resume_event="wallet_safety_reviewed",
        metadata=task.get("metadata", {}),
    )


def _from_oracle(item: WorkOpportunity) -> Opportunity:
    source = (item.source or "").lower()
    category = (item.category or "").lower()
    platform = _SOURCE_PLATFORM.get(source, Platform.CUSTOM)
    task_category = _CATEGORY.get(category, TaskCategory.UNKNOWN)
    opp_type = {
        TaskCategory.RESEARCH: OpportunityType.RESEARCH,
        TaskCategory.CODE_FIX: OpportunityType.CODE,
        TaskCategory.CODE_FEATURE: OpportunityType.CODE,
        TaskCategory.DATA_EXTRACTION: OpportunityType.DATA,
        TaskCategory.CONTENT: OpportunityType.CONTENT,
        TaskCategory.DOCUMENTATION: OpportunityType.CONTENT,
        TaskCategory.DESIGN: OpportunityType.ASSET,
    }.get(task_category, OpportunityType.DATA)
    return Opportunity(
        id=item.id or "",
        opportunity_type=opp_type,
        category=task_category,
        execution_mode=ExecutionMode.H0 if item.execution_mode == "agent_only" else ExecutionMode.H2,
        reward=item.reward_usd,
        currency=item.currency or "USD",
        platform=platform,
        external_id=item.id,
        title=item.title,
        description=item.description,
        url=item.url,
        tags=list(item.skills),
        deadline=item.deadline,
        competition_estimate=item.competition,
        raw=item.raw,
    )


def sync_oracle(config: Config, limit: int = 100) -> dict[str, Any]:
    """Pull normalized work into the existing ledger.

    Oracle discovery is intentionally broader than execution support. We persist
    everything we can normalize; the existing adapter boundary determines what
    can actually be submitted automatically.
    """
    feed = OracleFeeds()
    work = feed.work(min_reward=0, limit=limit)
    stored = 0
    executable = 0

    # The ledger is also used directly by earn_cycle(). Persist only platforms
    # with an execution/submission adapter so the existing loop can never select
    # an opportunity it cannot submit. The Oracle may still observe many more.
    from get_me_money.main import get_adapters
    auto_submit_platforms = set(get_adapters(config))
    observed_only = 0
    for item in work:
        opp = _from_oracle(item)
        if not opp.title:
            continue
        if opp.platform not in auto_submit_platforms:
            observed_only += 1
            continue
        save_opportunity(opp)
        stored += 1
        executable += 1
    return {
        "seen": len(work),
        "stored": stored,
        "auto_submittable": executable,
        "observed_only": observed_only,
    }


async def _run(config: Config, execute: bool) -> dict[str, Any]:
    from get_me_money.main import earn_cycle
    oracle = sync_oracle(config)
    result = await earn_cycle(config, execute=execute)
    return {"oracle": oracle, "cycle": result}


@click.command()
@click.option("--name", default="", help="Optional Moltwork worker name")
@click.option("--runtime", default="existing-agent", help="Runtime label only; Moltwork does not replace your agent framework")
@click.option("--moltos-agent-id", default=lambda: os.getenv("MOLTOS_AGENT_ID", ""), help="Public MoltOS agent ID")
@click.option("--moltwork-url", default=lambda: os.getenv("MOLTWORK_URL", "http://localhost:8788"), show_default=True)
@click.option("--dry-run", is_flag=True, help="Activate and rank work without submitting")
def main(name: str, runtime: str, moltos_agent_id: str, moltwork_url: str, dry_run: bool) -> None:
    """Activate this agent and immediately enter the default work loop."""
    config = Config()
    config.load()

    try:
        client_id = _get_or_create_client_id(config)
        activation = _activate(moltwork_url, name, runtime, moltos_agent_id, client_id)
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:800]
        raise click.ClickException(f"Moltwork activation failed ({exc.response.status_code}): {detail}") from exc
    except Exception as exc:
        raise click.ClickException(f"Could not activate with Moltwork: {exc}") from exc

    _save_public_state(config, activation)
    _mirror_human_task(activation)

    worker = activation.get("worker", {})
    wallet = activation.get("wallet", {})
    identity = activation.get("identity", {})

    click.echo(f"Worker: {worker.get('name', '')} ({worker.get('id', '')})")
    click.echo(f"Identity: {identity.get('provider', 'moltwork')} | verified={bool(identity.get('verified'))}")
    if wallet.get("address"):
        click.echo(f"Wallet: {wallet['address']} ({wallet.get('network', '')})")
    else:
        click.echo(f"Wallet: {wallet.get('status', 'not provisioned')}")
    policy = wallet.get("policy", {})
    click.echo(f"Wallet spending: {'enabled' if policy.get('spend_enabled') else 'OFF'}")
    click.echo("Starting work loop..." if not dry_run else "Scanning work (dry run)...")

    result = asyncio.run(_run(config, execute=not dry_run))
    click.echo(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
