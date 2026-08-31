"""Moltwork Lab Bridge — HTTP service connecting Letta mod tools to WorkerKit pipeline.

The Letta mod registers tools that call this service.
This service bridges to: Oracle, WorkerKit Orchestrator, Hydra, Assessor.

Run with: python -m lab.bridge --port 8789
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    print("http.server not available")
    sys.exit(1)


# ─── Load state from the mod's state file ─────────────────────────────

MOD_STATE_PATH = Path.home() / ".letta" / "mods" / "moltwork-lab.state.json"

def read_mod_state() -> dict:
    try:
        if MOD_STATE_PATH.exists():
            return json.loads(MOD_STATE_PATH.read_text())
    except Exception:
        pass
    return {"worker_id": "default", "worker_version": "v1", "runs": [], "capabilities": []}


# ─── HTTP handler ──────────────────────────────────────────────────────

class LabHandler(BaseHTTPRequestHandler):
    """Handle requests from the Letta mod tools."""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        path = self.path.rstrip("/")

        handlers = {
            "/oracle/search": self._oracle_search,
            "/oracle/opportunity": self._oracle_get_opportunity,
            "/lab/brief": self._lab_brief,
            "/lab/capability": self._lab_capability,
            "/budget/check": self._budget_check,
            "/budget/record": self._budget_record,
            "/assessor/preflight": self._assessor_preflight,
            "/assessor/review": self._assessor_review,
            "/outcome/record": self._outcome_record,
        }

        handler = handlers.get(path)
        if handler:
            try:
                result = handler(body)
                self._respond(200, result)
            except Exception as e:
                self._respond(500, {"error": str(e)})
        else:
            self._respond(404, {"error": f"unknown endpoint: {path}"})

    def do_GET(self):
        path = self.path.rstrip("/")
        if path == "/health":
            self._respond(200, {"ok": True, "service": "moltwork-lab-bridge"})
        elif path == "/state":
            self._respond(200, read_mod_state())
        else:
            self._respond(404, {"error": f"unknown endpoint: {path}"})

    def _respond(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    # ─── Oracle ────────────────────────────────────────────────────────

    def _oracle_search(self, body: dict) -> dict:
        """Search Oracle for opportunities."""
        oracle_url = body.get("oracle_url", "http://localhost:8788")
        import urllib.request
        try:
            params = f"q={body.get('query', '')}&limit={body.get('limit', 10)}"
            req = urllib.request.Request(f"{oracle_url}/v1/opportunities?{params}")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                return {"count": len(data.get("opportunities", [])), "opportunities": data.get("opportunities", [])}
        except Exception as e:
            return {"count": 0, "opportunities": [], "error": str(e)}

    def _oracle_get_opportunity(self, body: dict) -> dict:
        """Get specific opportunity details."""
        return {"opportunity_id": body.get("opportunity_id"), "status": "not_implemented"}

    # ─── Lab ───────────────────────────────────────────────────────────

    def _lab_brief(self, body: dict) -> dict:
        """Generate a Lab brief for a task family."""
        state = read_mod_state()
        task_family = body.get("task_family", "unknown")
        runs = [r for r in state.get("runs", []) if r.get("task_family") == task_family]
        wins = [r for r in runs if r.get("outcome") == "won"]

        return {
            "task_family": task_family,
            "total_runs": len(runs),
            "win_rate": len(wins) / len(runs) if runs else 0,
            "avg_cost": sum(r.get("cost_usd", 0) for r in runs) / len(runs) if runs else 0,
            "avg_reward": sum(r.get("reward_usd", 0) for r in wins) / len(wins) if wins else 0,
            "capabilities": [c for c in state.get("capabilities", []) if c.get("task_class") == task_family],
            "recent_runs": runs[-5:],
            "worker_version": state.get("worker_version", "v1"),
        }

    def _lab_capability(self, body: dict) -> dict:
        """Get capability evidence for a task class."""
        state = read_mod_state()
        task_class = body.get("task_class", "unknown")
        caps = [c for c in state.get("capabilities", []) if c.get("task_class") == task_class]
        return caps[0] if caps else {"task_class": task_class, "sample_size": 0, "acceptance_rate": 0}

    # ─── Budget ────────────────────────────────────────────────────────

    def _budget_check(self, body: dict) -> dict:
        state = read_mod_state()
        spent = sum(r.get("cost_usd", 0) for r in state.get("runs", []))
        cap = state.get("budget_cap_usd", 10.0)
        return {"cap": cap, "spent": spent, "remaining": cap - spent}

    def _budget_record(self, body: dict) -> dict:
        return {"recorded": True, "cost_usd": body.get("cost_usd", 0)}

    # ─── Assessor ──────────────────────────────────────────────────────

    def _assessor_preflight(self, body: dict) -> dict:
        """G0 deterministic checks."""
        content = body.get("content", "")
        checks = [
            {"name": "has_content", "passed": bool(content and len(content) > 50)},
            {"name": "has_structure", "passed": any(m in content for m in ["#", "1.", "- "])},
            {"name": "not_error", "passed": "error" not in content.lower()[:200]},
        ]
        return {"gate": "G0", "passed": all(c["passed"] for c in checks), "checks": checks}

    def _assessor_review(self, body: dict) -> dict:
        """Full assessment request."""
        return {
            "assessment_id": f"assess-{int(time.time())}",
            "status": "submitted",
            "gates": ["G0", "G1", "G2"],
            "note": "Full evaluation via letta-evals pending",
        }

    # ─── Outcomes ──────────────────────────────────────────────────────

    def _outcome_record(self, body: dict) -> dict:
        """Record outcome and update capability evidence."""
        state = read_mod_state()
        run = {
            "run_id": f"run-{int(time.time())}",
            "opportunity_id": body.get("opportunity_id", ""),
            "task_family": body.get("task_family", "unknown"),
            "artifact_hash": body.get("artifact_hash", ""),
            "outcome": body.get("outcome", "unknown"),
            "cost_usd": body.get("cost_usd", 0),
            "reward_usd": body.get("reward_usd", 0),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        state.setdefault("runs", []).append(run)

        # Update capabilities
        tf = run["task_family"]
        caps = state.setdefault("capabilities", [])
        cap = next((c for c in caps if c.get("task_class") == tf), None)
        if not cap:
            cap = {"task_class": tf, "sample_size": 0, "acceptance_rate": 0, "median_cost": 0, "total_revenue": 0}
            caps.append(cap)
        cap["sample_size"] += 1
        tf_runs = [r for r in state["runs"] if r.get("task_family") == tf]
        tf_wins = [r for r in tf_runs if r.get("outcome") == "won"]
        cap["acceptance_rate"] = len(tf_wins) / len(tf_runs) if tf_runs else 0
        cap["total_revenue"] = sum(r.get("reward_usd", 0) for r in tf_wins)

        # Write back
        MOD_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        MOD_STATE_PATH.write_text(json.dumps(state, indent=2))

        return {"recorded": True, "run_id": run["run_id"], "capability": cap}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Moltwork Lab Bridge")
    parser.add_argument("--port", type=int, default=8789)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), LabHandler)
    print(f"Moltwork Lab Bridge running on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
