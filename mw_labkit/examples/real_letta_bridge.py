"""One expensive Letta turn, then cheap/regradable Harbor evaluation."""
from pathlib import Path
from mw_labkit.runtime import LettaRuntimeClient
from mw_labkit.rewardkit_scaffold import AssessorSpec, build_artifact_evaluation_task
from mw_labkit.hashing import tree_digest

worker_id = "researcher-v1"
workspace = Path("./live-campaign-workspace").resolve()
workspace.mkdir(exist_ok=True)

letta = LettaRuntimeClient("http://127.0.0.1:3000")
letta.ensure_worker(worker_id, model="mimo-v2.5")
run = letta.execute(
    worker_id,
    "Produce a concrete technical submission. Save the primary deliverable as submission.md.",
    str(workspace),
    timeout=600,
)
if not run.ok:
    raise SystemExit("Letta execution failed")
if not (workspace / "submission.md").exists():
    # The runtime service currently returns output as text; bridge it into the
    # artifact contract if the worker did not write the requested file.
    (workspace / "submission.md").write_text(run.output_content)

print("conversation", run.conversation_id)
print("workspace digest", tree_digest(workspace))

task = build_artifact_evaluation_task(
    workspace,
    "./live-harbor-assessor-v0",
    AssessorSpec(version="v0", include_subjective_judge=False),
)
print("Harbor task", task)
print(f"Run: harbor run -p {task} -a nop --env docker")
print("After editing only tests/ for v1:")
print("Run: harbor job regrade jobs/<source-job> -p ./live-harbor-assessor-v1 -e docker")
