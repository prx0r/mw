"""Moltwork logging — every run, error, and report is recorded."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

LOG_DIR = Path(os.environ.get("MOLTWORK_LOG_DIR", "/root/workerkit/data/logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log_run(run_id: str, worker_id: str, task: str, status: str,
            result: dict | None = None, error: str | None = None,
            cost_usd: float = 0, duration_s: float = 0):
    """Log a run attempt."""
    entry = {
        "ts": _ts(), "type": "run", "run_id": run_id, "worker_id": worker_id,
        "task": task[:200], "status": status, "cost_usd": cost_usd,
        "duration_s": duration_s,
    }
    if result:
        entry["result_summary"] = str(result)[:500]
    if error:
        entry["error"] = error[:500]
    _append("runs.jsonl", entry)


def log_error(source: str, error: str, context: dict | None = None):
    """Log an error with context."""
    entry = {"ts": _ts(), "type": "error", "source": source, "error": error[:1000]}
    if context:
        entry["context"] = context
    _append("errors.jsonl", entry)
    print(f"  [ERROR] {source}: {error[:200]}")


def log_report(report_type: str, data: dict):
    """Log a report (summary, comparison, etc)."""
    entry = {"ts": _ts(), "type": "report", "report_type": report_type, "data": data}
    _append("reports.jsonl", entry)


def log_event(event_type: str, data: dict):
    """Log a generic event."""
    entry = {"ts": _ts(), "type": event_type, "data": data}
    _append("events.jsonl", entry)


def _append(filename: str, entry: dict):
    """Append one JSON line to a log file."""
    try:
        path = LOG_DIR / filename
        with open(path, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        print(f"  [LOG-ERROR] Failed to write log: {e}")


def read_logs(filename: str, limit: int = 50) -> list[dict]:
    """Read last N entries from a log file."""
    path = LOG_DIR / filename
    if not path.exists():
        return []
    lines = path.read_text().strip().split("\n")
    entries = []
    for line in lines[-limit:]:
        try:
            entries.append(json.loads(line))
        except Exception:
            pass
    return entries


def tail_log(filename: str, n: int = 20) -> str:
    """Tail last N lines of a log file."""
    path = LOG_DIR / filename
    if not path.exists():
        return f"(no {filename} log)"
    lines = path.read_text().strip().split("\n")
    return "\n".join(lines[-n:])
