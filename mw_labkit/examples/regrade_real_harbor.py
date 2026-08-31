from mw_labkit.harbor import HarborCLI
import sys

source_job, new_task = sys.argv[1], sys.argv[2]
h = HarborCLI()
print(" ".join(h.regrade_command(source_job, new_task)))
if not h.available():
    raise SystemExit("Harbor is not installed in this environment")
result = h.regrade(source_job, new_task, cwd=".")
print(result.stdout)
print(result.stderr)
raise SystemExit(result.returncode)
