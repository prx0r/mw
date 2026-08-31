from pathlib import Path
from mw_labkit.campaign import FastCampaignHarness
from mw_labkit.runtime import FakeWorkerRuntime
from mw_labkit.records import WorkerVersionRef
from mw_labkit.hydra import MemoryGraphSink

root = Path(".lab-demo")
h = FastCampaignHarness(root, FakeWorkerRuntime())
worker = WorkerVersionRef(worker_id="researcher-v1", version_id="v0", model="fake/model")
binding, e0, job = h.execute_and_grade("demo-opportunity", "Build a technical submission", worker)
e1 = h.regrade(binding, job)

graph = MemoryGraphSink()
graph.project_run_binding(binding)
graph.project_evaluation(e0)
graph.project_evaluation(e1)

print("run", binding.run_id)
print("assessor v0", e0.reward, e0.dimensions)
print("assessor v1", e1.reward, e1.dimensions)
print("graph writes", len(graph.queries))
print("binding digest", binding.content_hash())
