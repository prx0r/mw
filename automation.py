"""Automation resolver — for each human dependency, search the resolution ladder.

This is the core Oracle research loop:
> What human dependency, if eliminated, unlocks the most valuable opportunity?
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

# Resolution ladder (highest → lowest preference)
LADDER = [
    {"id": "official_api", "name": "Official API", "trust": 1.0},
    {"id": "official_openapi", "name": "Official OpenAPI Spec", "trust": 1.0},
    {"id": "official_mcp", "name": "Official MCP Server", "trust": 0.95},
    {"id": "official_webmcp", "name": "Official WebMCP", "trust": 0.9},
    {"id": "approved_integration", "name": "Approved Integration", "trust": 0.85},
    {"id": "zapier_mcp", "name": "Zapier MCP", "trust": 0.8},
    {"id": "community_mcp", "name": "Community MCP", "trust": 0.6},
    {"id": "browser_automation", "name": "Browser Automation", "trust": 0.5},
    {"id": "human_queue", "name": "Human Queue (RentAHuman)", "trust": 0.3},
]


@dataclass
class ResolutionResult:
    dependency_id: str = ""
    resolved_by: str = ""       # ladder entry id
    trust: float = 0.0
    credential_type: str = ""   # oauth, api_key, none
    human_initial_auth: bool = False
    notes: str = ""


@dataclass
class AutomationAnalysis:
    opportunity_id: str = ""
    market_id: str = ""
    total_steps: int = 0
    agent_steps: int = 0
    human_steps: int = 0
    resolved_steps: int = 0
    unresolved_steps: int = 0
    resolved_by_ladder: dict = field(default_factory=dict)  # ladder_id → count
    human_level_derived: str = ""
    blocked_value_usd: float = 0
    resolutions: list[dict] = field(default_factory=list)


def resolve_dependency(
    dep_id: str,
    market_id: str = "",
    available_apis: list[dict] = None,
    available_mcps: list[dict] = None,
    webmcp_tools: list[dict] = None,
    zapier_actions: list[dict] = None,
) -> ResolutionResult:
    """Search the resolution ladder for a human dependency."""
    available_apis = available_apis or []
    available_mcps = available_mcps or []
    webmcp_tools = webmcp_tools or []
    zapier_actions = zapier_actions or []

    # Map dependency to what we're looking for
    dep_keywords = dep_id.lower().replace("human.", "").split("_")

    # Check official API
    for api in available_apis:
        if any(kw in api.get("description", "").lower() for kw in dep_keywords):
            return ResolutionResult(
                dependency_id=dep_id,
                resolved_by="official_api",
                trust=1.0,
                credential_type=api.get("auth_type", "api_key"),
                notes=f"Official API: {api.get('name', '')}",
            )

    # Check official MCP
    for mcp in available_mcps:
        if any(kw in mcp.get("description", "").lower() for kw in dep_keywords):
            return ResolutionResult(
                dependency_id=dep_id,
                resolved_by="official_mcp",
                trust=0.95,
                credential_type=mcp.get("auth_type", "oauth"),
                notes=f"Official MCP: {mcp.get('name', '')}",
            )

    # Check WebMCP
    for tool in webmcp_tools:
        if any(kw in tool.get("name", "").lower() for kw in dep_keywords):
            return ResolutionResult(
                dependency_id=dep_id,
                resolved_by="official_webmcp",
                trust=0.9,
                human_initial_auth=True,
                notes=f"WebMCP tool: {tool.get('name', '')}",
            )

    # Check Zapier
    for action in zapier_actions:
        if any(kw in action.get("description", "").lower() for kw in dep_keywords):
            return ResolutionResult(
                dependency_id=dep_id,
                resolved_by="zapier_mcp",
                trust=0.8,
                credential_type="oauth",
                notes=f"Zapier: {action.get('name', '')}",
            )

    # Unresolved — falls to human queue
    return ResolutionResult(
        dependency_id=dep_id,
        resolved_by="human_queue",
        trust=0.3,
        human_initial_auth=True,
        notes="No automation found — requires human",
    )


def analyze_opportunity(
    opp_id: str,
    execution_steps: list[dict],
    human_dependencies: list[dict],
    market_id: str = "",
    reward_usd: float = 0,
    **resolver_kwargs,
) -> AutomationAnalysis:
    """Full automation analysis for an opportunity."""
    analysis = AutomationAnalysis(opportunity_id=opp_id, market_id=market_id)
    analysis.total_steps = len(execution_steps)

    for step in execution_steps:
        if step.get("actor") == "agent":
            analysis.agent_steps += 1
        else:
            analysis.human_steps += 1

    for dep in human_dependencies:
        result = resolve_dependency(dep["id"], market_id, **resolver_kwargs)
        analysis.resolutions.append(result.__dict__)

        if result.resolved_by != "human_queue":
            analysis.resolved_steps += 1
            analysis.resolved_by_ladder[result.resolved_by] = (
                analysis.resolved_by_ladder.get(result.resolved_by, 0) + 1
            )
        else:
            analysis.unresolved_steps += 1

    # Derive H-level from unresolved human dependencies
    unresolved = analysis.unresolved_steps
    total_deps = len(human_dependencies)
    if total_deps == 0:
        analysis.human_level_derived = "H0"
    elif unresolved == 0:
        analysis.human_level_derived = "H1"  # all deps resolved by automation
    elif unresolved == 1:
        analysis.human_level_derived = "H2"
    else:
        analysis.human_level_derived = "H3"

    # Blocked value = reward × proportion of unresolved deps
    if total_deps > 0:
        analysis.blocked_value_usd = reward_usd * (unresolved / total_deps)
    return analysis
