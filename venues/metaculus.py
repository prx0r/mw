"""MetaculusVenue — adapter for Metaculus forecasting platform.

Implements WorkVenue protocol: discover, inspect, submit, status, settle.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from dataclasses import dataclass, field

from .base import Opportunity, Outcome, Settlement, SubmissionRef, WorkVenue


METACULUS_API = "https://www.metaculus.com/api2"
METACULUS_API_V1 = "https://www.metaculus.com/api"


class MetaculusVenue:
    """Metaculus forecasting platform adapter."""

    def __init__(self, token: str = "", tournament_id: int = 0):
        self.token = token or os.environ.get("METACULUS_API_KEY", "")
        self.tournament_id = tournament_id or int(os.environ.get("METACULUS_TOURNAMENT", "0"))
        self._headers = {
            "Authorization": f"Token {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

    def _get(self, path: str, params: dict = None) -> dict | None:
        url = f"{METACULUS_API}{path}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query:
                url += f"?{query}"
        try:
            req = urllib.request.Request(url, headers=self._headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e)}

    def _post(self, path: str, data, use_v1: bool = False) -> dict | None:
        base = METACULUS_API_V1 if use_v1 else METACULUS_API
        url = f"{base}{path}"
        body = json.dumps(data).encode()
        try:
            req = urllib.request.Request(url, data=body, headers=self._headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e)}

    def discover(self) -> list[Opportunity]:
        """Find open forecasting questions in the tournament."""
        opps = []
        offset = 0
        while True:
            data = self._get("/questions/", {
                "status": "open",
                "project": self.tournament_id,
                "limit": 50,
                "offset": offset,
            })
            if not data or "results" not in data:
                break
            for q in data["results"]:
                qid = q.get("id", 0)
                qdata = q.get("question", {})
                qtype = qdata.get("type", "binary")
                cp = None
                aggs = q.get("aggregations", {})
                if aggs:
                    unweighted = aggs.get("unweighted", {})
                    latest = unweighted.get("latest", {})
                    if latest:
                        cp = latest.get("probability")

                opps.append(Opportunity(
                    id=str(qid),
                    venue="metaculus",
                    title=q.get("title", ""),
                    description=(q.get("description", "") or "")[:500],
                    task_family=f"forecasting.{qtype}",
                    capabilities=["evidence.gather", "calibration.apply", "uncertainty.quantify"],
                    reward_usd=0.0,
                    deadline=q.get("scheduled_close_time") or q.get("actual_close_time") or "",
                    status="open",
                    source_url=f"https://www.metaculus.com/questions/{qid}/",
                    metadata={
                        "question_type": qtype,
                        "community_prediction": cp,
                        "nr_forecasters": q.get("nr_forecasters", 0),
                        "tournament_id": self.tournament_id,
                    },
                ))
            if not data.get("next"):
                break
            offset += 50
        return opps

    def inspect(self, opportunity_id: str) -> Opportunity | None:
        """Get full question details."""
        qid = int(opportunity_id)
        data = self._get(f"/questions/{qid}/")
        if not data or "error" in data:
            return None

        qdata = data.get("question", {})
        qtype = qdata.get("type", "binary")
        cp = None
        aggs = data.get("aggregations", {})
        if aggs:
            unweighted = aggs.get("unweighted", {})
            latest = unweighted.get("latest", {})
            if latest:
                cp = latest.get("probability")

        return Opportunity(
            id=str(qid),
            venue="metaculus",
            title=data.get("title", ""),
            description=(data.get("description", "") or "")[:1000],
            task_family=f"forecasting.{qtype}",
            capabilities=["evidence.gather", "calibration.apply", "uncertainty.quantify"],
            deadline=data.get("scheduled_close_time") or "",
            status=data.get("status", "open"),
            source_url=f"https://www.metaculus.com/questions/{qid}/",
            metadata={
                "question_type": qtype,
                "community_prediction": cp,
                "nr_forecasters": data.get("nr_forecasters", 0),
                "resolution_criteria": qdata.get("resolution_criteria", ""),
                "fine_print": qdata.get("fine_print", ""),
            },
        )

    def submit(self, opportunity_id: str, forecast: dict = None) -> SubmissionRef | None:
        """Submit a forecast to Metaculus.

        forecast = {"probability": 0.65} for binary
        forecast = {"cdf_201": [...]} for numeric
        forecast = {"probabilities": {"opt1": 0.3, ...}} for multiple_choice
        """
        if not forecast:
            return None
        qid = int(opportunity_id)
        qtype = forecast.get("question_type", "binary")

        if qtype == "binary":
            p = max(0.01, min(0.99, forecast.get("probability", 0.5)))
            payload = [{"question": qid, "probability_yes": p}]
        elif qtype == "numeric":
            payload = [{"question": qid, "continuous_cdf": forecast.get("cdf_201", [])}]
        elif qtype == "multiple_choice":
            payload = [{"question": qid, "probability_yes_per_category": forecast.get("probabilities", {})}]
        else:
            return None

        result = self._post("/questions/forecast/", payload, use_v1=True)
        if not result or "error" in result:
            return None

        # Post reasoning comment if provided
        reasoning = forecast.get("reasoning", "")
        if reasoning:
            self._post("/comments/create/", {
                "text": f"## Moltwork Forecaster\n\n{reasoning}",
                "parent": None,
                "included_forecast": True,
                "is_private": True,
                "on_post": qid,
            })

        return SubmissionRef(
            submission_id=f"meta-{qid}-{int(time.time())}",
            venue="metaculus",
            opportunity_id=opportunity_id,
            artifact_hash=str(hash(json.dumps(forecast, sort_keys=True))),
            status="submitted",
        )

    def status(self, submission_id: str) -> Outcome | None:
        """Check if a question has resolved."""
        # submission_id format: "meta-{qid}-{timestamp}"
        parts = submission_id.split("-")
        if len(parts) < 3:
            return None
        qid = int(parts[1])
        data = self._get(f"/questions/{qid}/")
        if not data or "error" in data:
            return None

        resolved = data.get("status") == "resolved"
        if not resolved:
            return Outcome(submission_id=submission_id, status="pending", score=0.0)

        # Get resolution
        resolution = data.get("resolution")
        my_forecast = self._get(f"/questions/{qid}/forecasts/")
        score = 0.0
        if my_forecast and "results" in my_forecast:
            for f in my_forecast["results"]:
                if f.get("forecast", {}).get("probability_yes") is not None:
                    p = f["forecast"]["probability_yes"]
                    if resolution is True:
                        score = max(-10.0, __import__("math").log2(max(0.01, p)))
                    elif resolution is False:
                        score = max(-10.0, __import__("math").log2(max(0.01, 1.0 - p)))
                    break

        return Outcome(
            submission_id=submission_id,
            status="won" if score > -1.0 else "lost",
            score=score,
            feedback=f"resolution={resolution}",
        )

    def settle(self, submission_id: str) -> Settlement | None:
        """Tournament prizes are automatic on Metaculus."""
        return None
