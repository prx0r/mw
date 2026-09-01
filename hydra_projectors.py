"""Hydra Projectors — feed Git, Runs, Evaluations, Outcomes into the graph.

GitProjector: commit/fork/tag → Hydra nodes
RunProjector: WorkerKit + Trajectory → Hydra nodes
EvalProjector: Letta Evals → Hydra nodes
OutcomeProjector: external results → Hydra nodes
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


def _sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


class HydraProjector:
    """Base projector — writes to SQLite-backed Hydra store."""
    
    def __init__(self, db_path: str = "data/graph_store.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hydra_nodes (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                properties TEXT NOT NULL,
                created_at REAL DEFAULT (strftime('%s','now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hydra_edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                type TEXT NOT NULL,
                properties TEXT DEFAULT '{}',
                created_at REAL DEFAULT (strftime('%s','now'))
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_label ON hydra_nodes(label)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON hydra_edges(source_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON hydra_edges(target_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_type ON hydra_edges(type)")
        conn.commit()
        conn.close()
    
    def upsert_node(self, node_id: str, label: str, properties: dict):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO hydra_nodes (id, label, properties) VALUES (?, ?, ?)",
            (node_id, label, json.dumps(properties))
        )
        conn.commit()
        conn.close()
    
    def upsert_edge(self, source_id: str, target_id: str, edge_type: str, properties: dict = None):
        edge_id = f"{source_id}:{edge_type}:{target_id}"
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO hydra_edges (id, source_id, target_id, type, properties) VALUES (?, ?, ?, ?, ?)",
            (edge_id, source_id, target_id, edge_type, json.dumps(properties or {}))
        )
        conn.commit()
        conn.close()
    
    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class GitProjector(HydraProjector):
    """Turn Git objects into Hydra nodes."""
    
    def project_repo(self, repo_url: str, repo_name: str):
        self.upsert_node(f"repo:{repo_name}", "Repo", {
            "url": repo_url, "name": repo_name, "type": "worker"
        })
    
    def project_commit(self, repo_name: str, commit_hash: str, message: str = "",
                       author: str = "", timestamp: float = 0):
        node_id = f"commit:{commit_hash[:12]}"
        self.upsert_node(node_id, "Commit", {
            "hash": commit_hash, "message": message,
            "author": author, "timestamp": timestamp,
        })
        self.upsert_edge(f"repo:{repo_name}", node_id, "CONTAINS_COMMIT")
    
    def project_branch(self, repo_name: str, branch_name: str, head_commit: str):
        node_id = f"branch:{repo_name}:{branch_name}"
        self.upsert_node(node_id, "Branch", {
            "name": branch_name, "head_commit": head_commit,
        })
        self.upsert_edge(f"repo:{repo_name}", node_id, "HAS_BRANCH")
    
    def project_tag(self, repo_name: str, tag_name: str, commit_hash: str, annotation: str = ""):
        node_id = f"tag:{repo_name}:{tag_name}"
        self.upsert_node(node_id, "Tag", {
            "name": tag_name, "commit": commit_hash, "annotation": annotation,
        })
        self.upsert_edge(f"repo:{repo_name}", node_id, "HAS_TAG")


class RunProjector(HydraProjector):
    """Turn WorkerKit runs + Trajectories into Hydra nodes."""
    
    def project_worker(self, worker_id: str):
        self.upsert_node(f"worker:{worker_id}", "Worker", {
            "worker_id": worker_id, "created_at": time.time(),
        })
    
    def project_worker_version(self, version: dict):
        node_id = f"wv:{version['worker_id']}:{version['version_id']}"
        self.upsert_node(node_id, "WorkerVersion", version)
        self.upsert_edge(f"worker:{version['worker_id']}", node_id, "HAS_VERSION")
        
        if version.get("parent_version"):
            parent_id = f"wv:{version['worker_id']}:{version['parent_version']}"
            self.upsert_edge(node_id, parent_id, "MUTATION_OF")
    
    def project_run(self, run: dict):
        run_id = run.get("run_id", f"run-{int(time.time())}")
        node_id = f"run:{run_id}"
        self.upsert_node(node_id, "Run", run)
        
        if run.get("worker_version_id"):
            self.upsert_edge(node_id, f"wv:{run['worker_version_id']}", "EXECUTED_BY")
        if run.get("world_version_id"):
            self.upsert_edge(node_id, f"wv:{run['world_version_id']}", "IN_WORLD")
        if run.get("opportunity_id"):
            self.upsert_edge(node_id, f"opp:{run['opportunity_id']}", "TARGETED")
        
        return node_id
    
    def project_trajectory(self, run_id: str, trajectory: dict):
        traj_id = f"traj:{run_id}"
        self.upsert_node(traj_id, "Trajectory", {
            "run_id": run_id, "format": "letta-trajectory",
            "content_hash": _sha256(trajectory)[:16],
        })
        self.upsert_edge(f"run:{run_id}", traj_id, "GENERATED")
    
    def project_artifact(self, run_id: str, artifact: dict):
        art_id = f"art:{artifact.get('hash', _sha256(artifact))[:12]}"
        self.upsert_node(art_id, "Artifact", artifact)
        self.upsert_edge(f"run:{run_id}", art_id, "PRODUCED")


class EvalProjector(HydraProjector):
    """Turn Letta Evals results into Hydra nodes."""
    
    def project_assessor(self, assessor_id: str):
        self.upsert_node(f"assessor:{assessor_id}", "Assessor", {
            "assessor_id": assessor_id, "created_at": time.time(),
        })
    
    def project_assessor_version(self, version: dict):
        node_id = f"av:{version['assessor_id']}:{version['version_id']}"
        self.upsert_node(node_id, "AssessorVersion", version)
        self.upsert_edge(f"assessor:{version['assessor_id']}", node_id, "HAS_VERSION")
    
    def project_evaluation(self, run_id: str, eval_result: dict, assessor_version: str = ""):
        eval_id = f"eval:{run_id}:{int(time.time())}"
        self.upsert_node(eval_id, "Evaluation", {
            "run_id": run_id,
            "overall_score": eval_result.get("overall_score", 0),
            "gates_passed": eval_result.get("gates_passed", 0),
        })
        self.upsert_edge(f"run:{run_id}", eval_id, "EVALUATED_BY")
        
        if assessor_version:
            self.upsert_edge(eval_id, f"av:{assessor_version}", "USED_ASSESSOR")
        
        # Project individual gate scores
        for gate_name, gate_data in eval_result.get("gate_details", {}).items():
            criterion_id = f"crit:{run_id}:{gate_name}"
            self.upsert_node(criterion_id, "Criterion", {
                "name": gate_name, "weight": gate_data.get("weight", 0),
                "score": gate_data.get("score", 0),
            })
            self.upsert_edge(eval_id, criterion_id, "SCORED")


class OutcomeProjector(HydraProjector):
    """Turn external outcomes into Hydra nodes."""
    
    def project_outcome(self, run_id: str, outcome: dict):
        outcome_id = f"out:{run_id}"
        self.upsert_node(outcome_id, "Outcome", {
            "run_id": run_id,
            "result": outcome.get("result", "unknown"),
            "reward_usd": outcome.get("reward_usd", 0),
            "external": outcome.get("external", False),
        })
        self.upsert_edge(outcome_id, f"run:{run_id}", "RESULT_OF")
    
    def project_learning_proposal(self, proposal: dict):
        prop_id = f"lp:{proposal.get('id', int(time.time()))}"
        self.upsert_node(prop_id, "LearningProposal", proposal)
        for run_id in proposal.get("supported_by_runs", []):
            self.upsert_edge(prop_id, f"run:{run_id}", "SUPPORTED_BY")
    
    def project_capability_claim(self, claim: dict):
        claim_id = f"cc:{claim.get('id', int(time.time()))}"
        self.upsert_node(claim_id, "CapabilityClaim", claim)
        for exp_id in claim.get("evidence_experiments", []):
            self.upsert_edge(claim_id, f"exp:{exp_id}", "SUPPORTED_BY")
