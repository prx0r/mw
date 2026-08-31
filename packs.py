"""Pack research — domain intelligence that produces execution steps and human deps.

Each Pack turns raw market info into normalized opportunities with execution plans.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PackResearch:
    """Result of researching a market/opportunity class."""
    pack_id: str = ""
    market_id: str = ""
    market_name: str = ""
    research_date: str = ""

    # What we found
    official_api: dict = field(default_factory=dict)       # {available, url, auth_type, endpoints}
    official_mcp: dict = field(default_factory=dict)       # {available, url, auth_type}
    official_webmcp: list = field(default_factory=list)    # [{url, tools: [...]}]
    zapier_integration: dict = field(default_factory=dict) # {available, actions: [...]}
    community_mcps: list = field(default_factory=list)     # [{url, trust, auth_type}]
    browser_automation: dict = field(default_factory=dict) # {feasible, risk}

    # Execution plan
    execution_steps: list[dict] = field(default_factory=list)
    human_dependencies: list[dict] = field(default_factory=list)

    # Derived
    human_level: str = ""
    automation_score: float = 0.0  # 0=fully human, 1=fully autonomous

    # Venues
    venues: list[dict] = field(default_factory=list)

    raw_findings: dict = field(default_factory=dict)

    def to_dict(self): 
        from dataclasses import asdict
        return asdict(self)


# ─── Known Pack Research Results ───────────────────────────────────────

KNOWN_PACKS = {
    "roblox": PackResearch(
        pack_id="roblox",
        market_id="roblox",
        market_name="Roblox",
        official_api={"available": True, "url": "create.roblox.com/docs/cloud", "auth_type": "oauth"},
        official_mcp={"available": True, "url": "github.com/Roblox/creator-docs/studio/mcp", "auth_type": "studio_session"},
        official_webmcp=[],
        zapier_integration={"available": False},
        execution_steps=[
            {"stage": "discover", "action": "find_bounties", "actor": "agent", "interface": "api"},
            {"stage": "work", "action": "build_in_studio", "actor": "agent", "interface": "official_mcp"},
            {"stage": "work", "action": "test_playtest", "actor": "agent", "interface": "official_mcp"},
            {"stage": "submit", "action": "upload_asset", "actor": "agent", "interface": "open_cloud_api"},
            {"stage": "submit", "action": "publish", "actor": "agent", "interface": "open_cloud_api"},
        ],
        human_dependencies=[
            {"id": "human.account_create", "stage": "enter", "recurrence": "once", "mandatory": True},
            {"id": "human.oauth_consent", "stage": "enter", "recurrence": "once", "mandatory": True},
        ],
        human_level="H1",
        automation_score=0.9,
    ),
    "upwork": PackResearch(
        pack_id="upwork",
        market_id="upwork",
        market_name="Upwork",
        official_api={"available": True, "url": "upwork.com/developer", "auth_type": "oauth", "endpoints": ["jobs", "proposals", "contracts"]},
        official_mcp={"available": False},
        official_webmcp=[],
        zapier_integration={"available": True, "actions": ["search_jobs", "manage_contracts"]},
        community_mcps=[{"url": "github.com/AbbottDevelopments/upwork-mcp-server", "trust": 0.7}],
        execution_steps=[
            {"stage": "discover", "action": "search_jobs", "actor": "agent", "interface": "api"},
            {"stage": "qualify", "action": "score_fit", "actor": "agent", "interface": "internal"},
            {"stage": "work", "action": "produce_deliverable", "actor": "agent", "interface": "workspace"},
            {"stage": "submit", "action": "submit_proposal", "actor": "agent", "interface": "api"},
            {"stage": "submit", "action": "send_message", "actor": "agent", "interface": "api"},
            {"stage": "settle", "action": "manage_contract", "actor": "agent", "interface": "api"},
        ],
        human_dependencies=[
            {"id": "human.account_create", "stage": "enter", "recurrence": "once", "mandatory": True},
            {"id": "human.identity_verify", "stage": "enter", "recurrence": "once", "mandatory": True},
            {"id": "human.api_approval", "stage": "enter", "recurrence": "once", "mandatory": True},
        ],
        human_level="H1",
        automation_score=0.85,
    ),
    "etsy": PackResearch(
        pack_id="etsy",
        market_id="etsy",
        market_name="Etsy",
        official_api={"available": True, "url": "developers.etsy.com", "auth_type": "oauth", "endpoints": ["listings", "inventory", "orders"]},
        official_mcp={"available": True, "url": "developers.etsy.com/documentation/mcp_server", "auth_type": "documentation_only"},
        official_webmcp=[],
        community_mcps=[{"url": "github.com/DColl/etsy-mcp-server", "trust": 0.7, "auth_type": "oauth"}],
        execution_steps=[
            {"stage": "discover", "action": "find_demand", "actor": "agent", "interface": "api"},
            {"stage": "work", "action": "create_listing", "actor": "agent", "interface": "api"},
            {"stage": "work", "action": "upload_images", "actor": "agent", "interface": "api"},
            {"stage": "submit", "action": "publish_listing", "actor": "agent", "interface": "api"},
            {"stage": "settle", "action": "manage_orders", "actor": "agent", "interface": "api"},
        ],
        human_dependencies=[
            {"id": "human.account_create", "stage": "enter", "recurrence": "once", "mandatory": True},
            {"id": "human.oauth_consent", "stage": "enter", "recurrence": "once", "mandatory": True},
        ],
        human_level="H1",
        automation_score=0.88,
    ),
    "hackathon": PackResearch(
        pack_id="hackathon",
        market_id="hackathon",
        market_name="Hackathons (general)",
        official_api={"available": False},
        official_mcp={"available": False},
        execution_steps=[
            {"stage": "discover", "action": "find_competitions", "actor": "agent", "interface": "api"},
            {"stage": "qualify", "action": "analyze_rules", "actor": "agent", "interface": "internal"},
            {"stage": "work", "action": "research_sponsor", "actor": "agent", "interface": "api"},
            {"stage": "work", "action": "generate_ideas", "actor": "agent", "interface": "internal"},
            {"stage": "work", "action": "build_prototype", "actor": "agent", "interface": "workspace"},
            {"stage": "work", "action": "write_docs", "actor": "agent", "interface": "internal"},
            {"stage": "submit", "action": "submit_entry", "actor": "agent", "interface": "browser"},
        ],
        human_dependencies=[
            {"id": "human.account_create", "stage": "enter", "recurrence": "once", "mandatory": True},
            {"id": "human.manual_submission", "stage": "submit", "recurrence": "per_run", "mandatory": True},
        ],
        human_level="H1",
        automation_score=0.75,
    ),
}


def get_pack(pack_id: str) -> PackResearch | None:
    return KNOWN_PACKS.get(pack_id)


def list_packs() -> list[str]:
    return list(KNOWN_PACKS.keys())


def research_automation_score(pack: PackResearch) -> float:
    """Calculate what % of steps are agent-executable."""
    total = len(pack.execution_steps)
    if total == 0:
        return 0.0
    agent_steps = sum(1 for s in pack.execution_steps if s.get("actor") == "agent")
    return agent_steps / total
