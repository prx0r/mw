"""Shared Ontology — maps raw source categories to canonical Moltwork taxonomy.

Oracle ingests raw data from 7+ sources with inconsistent categories.
This module maps them to the canonical task families defined in
workerkit/core/taxonomy.py so every opportunity is classifiable and filterable.
"""
from __future__ import annotations


# ─── Source category → canonical task family mapping ──────────────────
#
# Format: "source:raw_category" → "canonical.task.family.path"
# Unmapped categories fall through to DEFAULT_TASK_FAMILY.

SOURCE_CATEGORY_MAP = {
    # BountyBook
    "bountybook:development": "software.backend",
    "bountybook:dev": "software.backend",
    "bountybook:frontend": "software.frontend.web",
    "bountybook:backend": "software.backend",
    "bountybook:mobile": "software.frontend.mobile",
    "bountybook:design": "design.ui",
    "bountybook:writing": "content.writing.blog",
    "bountybook:research": "research.analysis.data",
    "bountybook:data": "data.analysis",
    "bountybook:marketing": "content.writing.copywriting",
    "bountybook:security": "software.hacking.bounty",
    "bountybook:general": "research.ideation.technical",

    # GitHub
    "github:development": "software.backend",
    "github:bug-bounty": "software.hacking.bounty",
    "github:enhancement": "software.backend",
    "github:documentation": "software.documentation",
    "github:bug": "software.api.debugging",
    "github:feature": "software.backend",
    "github:design": "design.ui",
    "github:research": "research.analysis.data",

    # SuperTeam
    "superteam:bounty": "software.backend",
    "superteam:grant": "research.ideation.technical",
    "superteam:project": "software.backend",
    "superteam:content": "content.writing.blog",
    "superteam:design": "design.ui",

    # AgentHansa
    "agenthansa:general": "services.support.it",
    "agenthansa:development": "software.backend",
    "agenthansa:design": "design.ui",
    "agenthansa:research": "research.analysis.data",

    # RentaHuman
    "rentahuman:general": "services.support.customer",
    "rentahuman:development": "software.backend",
    "rentahuman:writing": "content.writing.blog",
    "rentahuman:design": "design.ui",

    # Daydreams
    "daydreams:general": "research.ideation.technical",
    "daydreams:development": "software.backend",
    "daydreams:code": "software.backend",

    # OpenServ
    "openserv:general": "research.ideation.technical",
    "openserv:code": "software.backend",
    "openserv:design": "design.ui",

    # NEAR AI
    "nearai:general": "research.ideation.technical",
    "nearai:development": "software.backend",
    "nearai:code": "software.backend",

    # AgentLux
    "agentlux:general": "services.support.it",
    "agentlux:development": "software.backend",

    # Augmi
    "augmi:general": "research.ideation.technical",
    "augmi:development": "software.backend",

    # AgentWorld
    "agentworld:general": "research.ideation.technical",
    "agentworld:development": "software.backend",

    # Atelier
    "atelier:general": "research.ideation.technical",
    "atelier:development": "software.backend",

    # Clustly
    "clustly:general": "research.ideation.technical",
    "clustly:development": "software.backend",

    # TaskForce
    "taskforce:general": "services.support.customer",
    "taskforce:development": "software.backend",
    "taskforce:writing": "content.writing.blog",

    # MoltJobs
    "moltjobs:general": "research.ideation.technical",
    "moltjobs:development": "software.backend",
    "moltjobs:code": "software.backend",
}

DEFAULT_TASK_FAMILY = "research.ideation.technical"

# ─── Source skill → canonical capability mapping ──────────────────────
#
# Maps raw source skill tags to canonical capabilities.
# Unmapped skills are stored as-is in oracle_skills but NOT in canonical_capabilities.

SKILL_CAPABILITY_MAP = {
    # Languages / frameworks → capabilities
    "python": "coding",
    "javascript": "coding",
    "typescript": "coding",
    "rust": "coding",
    "go": "coding",
    "java": "coding",
    "solidity": "coding",
    "react": "frontend-dev",
    "vue": "frontend-dev",
    "nextjs": "frontend-dev",
    "nodejs": "backend-dev",
    "fastapi": "api-implementation",
    "django": "backend-dev",
    "postgresql": "database",
    "mysql": "database",
    "redis": "backend-dev",
    "docker": "devops",
    "kubernetes": "devops",
    "aws": "devops",
    "gcp": "devops",
    "terraform": "devops",

    # Task types → capabilities
    "api": "api-implementation",
    "backend": "backend-dev",
    "frontend": "frontend-dev",
    "mobile": "frontend-dev",
    "design": "ui-design",
    "ui": "ui-design",
    "ux": "ux-research",
    "testing": "testing",
    "security": "security-audit",
    "data": "data-analysis",
    "research": "technical-research",
    "writing": "writing",
    "documentation": "technical-writing",
    "devops": "devops",
    "database": "database",
    "debugging": "debugging",
    "automation": "coding",
    "integration": "api-implementation",

    # Specific tools
    "figma": "ui-design",
    "photoshop": "ui-design",
    "illustrator": "ui-design",
    "git": "coding",
    "linux": "devops",
    "nginx": "devops",
    "graphql": "api-implementation",
    "rest": "api-implementation",
    "web3": "coding",
    "blockchain": "coding",
    "ai": "technical-research",
    "ml": "data-analysis",
    "llm": "technical-research",
}

DEFAULT_CAPABILITY = "coding"


def map_task_family(source: str, raw_category: str) -> str:
    """Map a source's raw category to a canonical task family path.

    Args:
        source: source slug (e.g. "bountybook")
        raw_category: source's raw category string (e.g. "development")

    Returns:
        Canonical task family path (e.g. "software.backend")
    """
    key = f"{source}:{raw_category.lower().strip()}"
    return SOURCE_CATEGORY_MAP.get(key, DEFAULT_TASK_FAMILY)


def map_capabilities(source_skills: list[str]) -> list[str]:
    """Map raw source skill tags to canonical capabilities.

    Args:
        source_skills: list of raw skill tags from source

    Returns:
        Deduplicated list of canonical capability slugs
    """
    caps = set()
    for skill in source_skills:
        slug = skill.lower().strip().replace(" ", "-")
        mapped = SKILL_CAPABILITY_MAP.get(slug)
        if mapped:
            caps.add(mapped)
        else:
            # Try partial match
            for key, cap in SKILL_CAPABILITY_MAP.items():
                if key in slug or slug in key:
                    caps.add(cap)
                    break
    if not caps:
        caps.add(DEFAULT_CAPABILITY)
    return sorted(caps)


def classify_opportunity(source: str, raw_category: str, raw_skills: list[str]) -> dict:
    """Classify an opportunity into canonical taxonomy.

    Returns:
        {
            "task_family": "software.backend",
            "capabilities": ["coding", "api-implementation"],
            "autonomy_level": "H1",
            "economic_surface": "BOUNTY",
        }
    """
    task_family = map_task_family(source, raw_category)
    capabilities = map_capabilities(raw_skills)

    # Derive autonomy from task family
    autonomy = "H1"
    if task_family.startswith("software.hacking"):
        autonomy = "H0"
    elif task_family.startswith("design.") or task_family.startswith("content.video"):
        autonomy = "H2"
    elif task_family.startswith("services."):
        autonomy = "H2"

    return {
        "task_family": task_family,
        "capabilities": capabilities,
        "autonomy_level": autonomy,
        "economic_surface": "BOUNTY",
    }
