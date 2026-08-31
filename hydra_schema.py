"""Hydra schema — all node types and edge types for the empirical graph.

Nodes: Worker, WorkerVersion, World, WorldVersion, Run, Artifact, Evaluation, etc.
Edges: MUTATION_OF, EXECUTED_BY, IN_WORLD, PRODUCED, ASSESSED_BY, etc.
"""
from __future__ import annotations

# ─── Node types ───────────────────────────────────────────────────────

NODE_TYPES = {
    # Git objects
    "Repo": {"properties": ["url", "name", "type"]},
    "Commit": {"properties": ["hash", "message", "author", "timestamp"]},
    "Branch": {"properties": ["name", "head_commit"]},
    "Tag": {"properties": ["name", "commit", "annotation"]},
    
    # Worker entities
    "Worker": {"properties": ["worker_id", "created_at"]},
    "WorkerVersion": {"properties": ["version_id", "worker_id", "model", "promoted", "created_at"]},
    "MemoryCommit": {"properties": ["git_hash", "worker_version_id", "summary"]},
    "SkillVersion": {"properties": ["skill_id", "version_id", "name", "content_hash"]},
    "ModVersion": {"properties": ["mod_id", "version_id", "name"]},
    
    # World entities
    "World": {"properties": ["world_id", "task_family", "submission_type"]},
    "WorldVersion": {"properties": ["version_id", "world_id", "commit_hash", "validity_claim"]},
    "Scenario": {"properties": ["scenario_id", "world_version_id", "difficulty"]},
    "School": {"properties": ["school_id", "task_family"]},
    "SchoolVersion": {"properties": ["version_id", "school_id", "baseline_score"]},
    
    # Experiment entities
    "Experiment": {"properties": ["experiment_id", "hypothesis", "design", "controlled"]},
    "Treatment": {"properties": ["treatment_id", "experiment_id", "type", "description"]},
    "Run": {"properties": ["run_id", "worker_version_id", "world_version_id", "outcome", "cost_usd"]},
    "Decision": {"properties": ["decision_id", "run_id", "action", "reasoning"]},
    "Trajectory": {"properties": ["trajectory_id", "run_id", "format", "content_hash"]},
    
    # Artifact entities
    "Artifact": {"properties": ["artifact_id", "hash", "type", "content_length"]},
    "Asset": {"properties": ["asset_id", "type", "content_hash"]},
    
    # Assessment entities
    "Assessor": {"properties": ["assessor_id", "created_at"]},
    "AssessorVersion": {"properties": ["version_id", "assessor_id", "judge_model", "calibration_error"]},
    "Evaluation": {"properties": ["evaluation_id", "run_id", "assessor_version_id", "overall_score"]},
    "Criterion": {"properties": ["criterion_id", "name", "weight", "score"]},
    
    # Outcome entities
    "Opportunity": {"properties": ["opportunity_id", "source", "task_family", "reward_usd"]},
    "Outcome": {"properties": ["outcome_id", "run_id", "result", "reward_usd", "external"]},
    
    # Learning entities
    "LearningProposal": {"properties": ["proposal_id", "type", "hypothesis", "status"]},
    "CapabilityClaim": {"properties": ["claim_id", "subject", "metric", "value", "n"]},
    "WorldValidityClaim": {"properties": ["claim_id", "world_id", "metric", "value"]},
}

# ─── Edge types ───────────────────────────────────────────────────────

EDGE_TYPES = {
    # Git lineage
    "PARENT_OF": {"from": "Commit", "to": "Commit"},
    
    # Worker version lineage
    "MUTATION_OF": {"from": "WorkerVersion", "to": "WorkerVersion"},
    "USES_MEMORY": {"from": "WorkerVersion", "to": "MemoryCommit"},
    "USES_SKILL": {"from": "WorkerVersion", "to": "SkillVersion"},
    "USES_MOD": {"from": "WorkerVersion", "to": "ModVersion"},
    
    # World version lineage
    "WORLD_VERSION_OF": {"from": "WorldVersion", "to": "World"},
    "WORLD_PARENT": {"from": "WorldVersion", "to": "WorldVersion"},
    "CONTAINS_SCENARIO": {"from": "WorldVersion", "to": "Scenario"},
    
    # School version lineage
    "SCHOOL_VERSION_OF": {"from": "SchoolVersion", "to": "School"},
    "SCHOOL_PARENT": {"from": "SchoolVersion", "to": "SchoolVersion"},
    "USES_WORLD": {"from": "SchoolVersion", "to": "WorldVersion"},
    "USES_ASSESSOR": {"from": "SchoolVersion", "to": "AssessorVersion"},
    
    # Run relationships
    "EXECUTED_BY": {"from": "Run", "to": "WorkerVersion"},
    "IN_WORLD": {"from": "Run", "to": "WorldVersion"},
    "TREATMENT_OF": {"from": "Run", "to": "Experiment"},
    "GENERATED": {"from": "Run", "to": "Trajectory"},
    "PRODUCED": {"from": "Run", "to": "Artifact"},
    "CONTAINS": {"from": "Run", "to": "Decision"},
    
    # Assessment relationships
    "ASSESSED": {"from": "Evaluation", "to": "Artifact"},
    "USED_ASSESSOR": {"from": "Evaluation", "to": "AssessorVersion"},
    "SCORED": {"from": "Evaluation", "to": "Criterion"},
    
    # Outcome relationships
    "RESULT_OF": {"from": "Outcome", "to": "Run"},
    "TARGETED": {"from": "Run", "to": "Opportunity"},
    
    # Learning relationships
    "SUPPORTED_BY": {"from": "LearningProposal", "to": "Run"},
    "SUPPORTED_BY": {"from": "CapabilityClaim", "to": "Experiment"},
    "SUPPORTED_BY": {"from": "WorldValidityClaim", "to": "Outcome"},
    
    # Experiment relationships
    "HAS_TREATMENT": {"from": "Experiment", "to": "Treatment"},
    "CONTROLLED_BY": {"from": "Treatment", "to": "WorkerVersion"},
}

# ─── Schema as Cypher DDL ─────────────────────────────────────────────

def generate_cypher_schema() -> str:
    """Generate Cypher DDL for the Hydra schema."""
    lines = []
    lines.append("// Moltwork Lab — Hydra Schema")
    lines.append("// Git stores versions. Hydra stores evidence about interactions between versions.")
    lines.append("")
    
    # Node labels
    for node_type, config in NODE_TYPES.items():
        props = ", ".join(f"{p}: STRING" for p in config["properties"])
        lines.append(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node_type}) REQUIRE n.id IS UNIQUE")
    
    lines.append("")
    
    # Relationship types
    for edge_type, config in EDGE_TYPES.items():
        lines.append(f"// {edge_type}: {config['from']} -> {config['to']}")
    
    return "\n".join(lines)


# ─── Query patterns ───────────────────────────────────────────────────

QUERIES = {
    "worker_lineage": """
        MATCH (wv:WorkerVersion {worker_id: $worker_id})
        MATCH path = (wv)-[:MUTATION_OF*0..]->(ancestor:WorkerVersion)
        RETURN ancestor.version_id, ancestor.model, ancestor.promoted
        ORDER BY ancestor.created_at
    """,
    
    "runs_by_worker": """
        MATCH (r:Run)-[:EXECUTED_BY]->(wv:WorkerVersion {worker_id: $worker_id})
        MATCH (r)-[:IN_WORLD]->(world:WorldVersion)
        RETURN r.run_id, r.outcome, r.cost_usd, world.world_id
        ORDER BY r.created_at DESC
    """,
    
    "capability_transfer": """
        MATCH (s:SkillVersion)<-[:USES_SKILL]-(wv:WorkerVersion)
        MATCH (r:Run)-[:EXECUTED_BY]->(wv)
        MATCH (r)-[:IN_WORLD]->(wv2:WorldVersion)
        MATCH (wv2)-[:WORLD_VERSION_OF]->(w:World)
        RETURN s.name, w.task_family, COUNT(r) as runs, 
               AVG(CASE WHEN r.outcome = 'won' THEN 1.0 ELSE 0.0 END) as win_rate
    """,
    
    "assessor_calibration": """
        MATCH (e:Evaluation)-[:USED_ASSESSOR]->(av:AssessorVersion)
        MATCH (e)-[:ASSESSED]->(a:Artifact)
        MATCH (o:Outcome)-[:RESULT_OF]->(r:Run)-[:PRODUCED]->(a)
        RETURN av.version_id, 
               e.overall_score as predicted,
               CASE WHEN o.result = 'won' THEN 1.0 ELSE 0.0 END as actual,
               ABS(e.overall_score - CASE WHEN o.result = 'won' THEN 1.0 ELSE 0.0 END) as error
    """,
    
    "skill_effectiveness": """
        MATCH (s:SkillVersion)<-[:USES_SKILL]-(wv:WorkerVersion)
        MATCH (r:Run)-[:EXECUTED_BY]->(wv)
        WHERE r.outcome = 'won'
        MATCH (r2:Run)-[:EXECUTED_BY]->(wv2:WorkerVersion)
        WHERE wv2.worker_id = wv.worker_id AND r2.outcome = 'lost'
        AND NOT (wv2)-[:USES_SKILL]->(s)
        RETURN s.name, 
               COUNT(DISTINCT r.run_id) as wins_with,
               COUNT(DISTINCT r2.run_id) as losses_without
    """,
}
