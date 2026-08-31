from __future__ import annotations
import json
import urllib.error
import urllib.request
from dataclasses import asdict
from typing import Any
from .records import RunBinding, EvaluationRecord


def _cypher_string(value: str) -> str:
    # Hydra supports scalar parameters, but the public HTTP README only guarantees
    # {cell_id, query}. Keep this dependency-free adapter conservative.
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


class HydraHTTPClient:
    """Minimal client for HydraDB's documented HTTPS/OpenCypher boundary."""
    def __init__(self, base_url: str = "http://127.0.0.1:8443", token: str = "local-development-token-32-bytes", namespace: str = "default", graph: str = "default", cell_id: str = "cell-0"):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.namespace = namespace
        self.graph = graph
        self.cell_id = cell_id

    def query(self, cypher: str) -> dict:
        url = f"{self.base_url}/v1/graphs/{self.graph}/query"
        body = json.dumps({"cell_id": self.cell_id, "query": cypher}).encode()
        req = urllib.request.Request(url, data=body, method="POST", headers={
            "Authorization": f"Bearer {self.token}",
            "X-Graph-Namespace": self.namespace,
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HydraDB HTTP {e.code}: {e.read().decode(errors='replace')}") from e

    def project_run_binding(self, binding: RunBinding) -> None:
        r = binding.run_id
        c = binding.campaign.campaign_id
        o = binding.campaign.opportunity_id
        wv = f"{binding.worker.worker_id}:{binding.worker.version_id}"
        digest = binding.content_hash()
        queries = [
            f"MERGE (c:Campaign {{id: {_cypher_string(c)}}})",
            f"MERGE (o:Opportunity {{id: {_cypher_string(o)}}})",
            f"MERGE (w:WorkerVersion {{id: {_cypher_string(wv)}}})",
            f"MERGE (r:Run {{id: {_cypher_string(r)}, binding_digest: {_cypher_string(digest)}}})",
            f"MATCH (c:Campaign {{id: {_cypher_string(c)}}}), (o:Opportunity {{id: {_cypher_string(o)}}}) MERGE (c)-[:TARGETS]->(o)",
            f"MATCH (r:Run {{id: {_cypher_string(r)}}}), (c:Campaign {{id: {_cypher_string(c)}}}) MERGE (r)-[:PART_OF]->(c)",
            f"MATCH (r:Run {{id: {_cypher_string(r)}}}), (w:WorkerVersion {{id: {_cypher_string(wv)}}}) MERGE (r)-[:EXECUTED_BY]->(w)",
        ]
        if binding.harbor_trial:
            ht = binding.harbor_trial.trial_id
            queries += [
                f"MERGE (h:HarborTrial {{id: {_cypher_string(ht)}, lock_digest: {_cypher_string(binding.harbor_trial.lock_digest)}}})",
                f"MATCH (r:Run {{id: {_cypher_string(r)}}}), (h:HarborTrial {{id: {_cypher_string(ht)}}}) MERGE (r)-[:EVALUATED_AS]->(h)",
            ]
        for q in queries:
            self.query(q)

    def project_evaluation(self, record: EvaluationRecord) -> None:
        e, r, a = record.evaluation_id, record.run_id, record.assessor_version
        reward = "0" if record.reward is None else repr(float(record.reward))
        for q in [
            f"MERGE (a:AssessorVersion {{id: {_cypher_string(a)}}})",
            f"MERGE (e:Evaluation {{id: {_cypher_string(e)}, reward: {reward}}})",
            f"MATCH (e:Evaluation {{id: {_cypher_string(e)}}}), (a:AssessorVersion {{id: {_cypher_string(a)}}}) MERGE (e)-[:USED_ASSESSOR]->(a)",
            f"MATCH (e:Evaluation {{id: {_cypher_string(e)}}}), (r:Run {{id: {_cypher_string(r)}}}) MERGE (e)-[:ASSESSED]->(r)",
        ]:
            self.query(q)


class MemoryGraphSink:
    """Captures graph writes for fast tests without HydraDB."""
    def __init__(self):
        self.queries: list[str] = []

    def query(self, cypher: str) -> dict:
        self.queries.append(cypher)
        return {"columns": [], "rows": []}

    project_run_binding = HydraHTTPClient.project_run_binding
    project_evaluation = HydraHTTPClient.project_evaluation
