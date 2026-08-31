from mw_labkit.rewardkit_scaffold import AssessorSpec, build_artifact_evaluation_task

spec = AssessorSpec(
    assessor_id="technical-submission",
    version="v0",
    include_subjective_judge=False,
)
build_artifact_evaluation_task("./workspace", "./generated-harbor-task", spec)
print("generated ./generated-harbor-task")
print("then: harbor run -p ./generated-harbor-task -a nop --env docker")
