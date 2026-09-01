#!/usr/bin/env python3
"""Metaculus Bot — xev0

Usage:
    python3 bot.py                    # Forecast all open questions
    python3 bot.py --tournament 33022 # Forecast specific tournament
    python3 bot.py --dry-run          # Don't submit, just print
"""
import os
import sys
import json
import time
import asyncio
import argparse
import requests
from typing import Optional

# Config
API_BASE = "https://www.metaculus.com/api2"
TOKEN = os.environ.get("METACULUS_TOKEN", "04a3c97a97707c9edcbc9eb5a67c3a1d7212ac7f")
HEADERS = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}

# Summer 2026 FutureEval Bot Tournament
DEFAULT_TOURNAMENT = 33022


def api_get(path: str, params: dict = None) -> dict:
    """GET request to Metaculus API with retry."""
    for attempt in range(3):
        r = requests.get(f"{API_BASE}{path}", headers=HEADERS, params=params or {})
        if r.status_code == 429:
            wait = 2 ** attempt * 2
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()
    return {}


def api_post(path: str, data: dict) -> dict:
    """POST request to Metaculus API."""
    r = requests.post(f"{API_BASE}{path}", headers=HEADERS, json=data)
    if not r.ok:
        print(f"  ERROR {r.status_code}: {r.text[:200]}")
    return r.json() if r.ok else {"error": r.text}


def get_tournament_questions(tournament_id: int) -> list:
    """Get all open questions from a tournament."""
    questions = []
    offset = 0
    while True:
        data = api_get(f"/questions/", {
            "status": "open",
            "project": tournament_id,
            "limit": 50,
            "offset": offset
        })
        batch = data.get("results", [])
        if not batch:
            break
        questions.extend(batch)
        offset += len(batch)
        if offset >= data.get("count", 0):
            break
    return questions


def get_all_open_questions() -> list:
    """Get all open questions."""
    questions = []
    offset = 0
    while True:
        data = api_get("/questions/", {"status": "open", "limit": 50, "offset": offset})
        batch = data.get("results", [])
        if not batch:
            break
        questions.extend(batch)
        offset += len(batch)
        if offset >= data.get("count", 0):
            break
    return questions


def forecast_binary(question_id: int, probability: float) -> bool:
    """Submit a binary forecast."""
    result = api_post("/questions/forecast/", [{
        "question": question_id,
        "probability_yes": probability,
        "confidence": None
    }])
    return "error" not in result


def forecast_numeric(question_id: int, cdf: list) -> bool:
    """Submit a numeric forecast (201-point CDF)."""
    result = api_post("/questions/forecast/", [{
        "question": question_id,
        "continuous_cdf": cdf
    }])
    return "error" not in result


def forecast_multiple_choice(question_id: int, probabilities: dict) -> bool:
    """Submit a multiple choice forecast."""
    result = api_post("/questions/forecast/", [{
        "question": question_id,
        "probability_yes_per_category": probabilities
    }])
    return "error" not in result


def post_comment(post_id: int, text: str) -> bool:
    """Post a comment explaining reasoning."""
    result = api_post("/comments/create/", {
        "text": text,
        "parent": None,
        "included_forecast": True,
        "is_private": True,
        "on_post": post_id
    })
    return "error" not in result


def generate_initial_forecast(question: dict) -> Optional[dict]:
    """Generate initial forecast based on question type.
    
    This is a simple base-rate forecast.
    For production, replace with LLM-based forecasting.
    """
    qtype = question.get("question", {}).get("type", "binary")
    title = question.get("title", "")
    
    if qtype == "binary":
        # Simple heuristic: use community prediction if available, else 50%
        community = question.get("community_prediction")
        if community and community > 0:
            return {"probability_yes": community}
        return {"probability_yes": 0.5}
    
    elif qtype == "multiple_choice":
        options = question.get("question", {}).get("options", [])
        if options:
            n = len(options)
            prob = 1.0 / n
            return {"probability_yes_per_category": {opt: prob for opt in options}}
    
    elif qtype in ("numeric", "date", "discrete"):
        # Generate simple uniform CDF
        scaling = question.get("question", {}).get("scaling", {})
        lower = scaling.get("range_min", 0)
        upper = scaling.get("range_max", 100)
        cdf = [i / 200 for i in range(201)]
        return {"continuous_cdf": cdf}
    
    return None


def forecast_question(question: dict, dry_run: bool = False) -> dict:
    """Forecast a single question."""
    qid = question["id"]
    post_id = question.get("id", qid)
    title = question.get("title", "")[:60]
    qtype = question.get("question", {}).get("type", "binary")
    
    result = {"id": qid, "title": title, "type": qtype, "status": "skipped"}
    
    # Generate forecast
    forecast = generate_initial_forecast(question)
    if not forecast:
        result["status"] = "no_forecast_generated"
        return result
    
    if dry_run:
        result["status"] = "dry_run"
        result["forecast"] = forecast
        return result
    
    # Submit forecast
    success = False
    if qtype == "binary":
        success = forecast_binary(qid, forecast["probability_yes"])
    elif qtype == "multiple_choice":
        success = forecast_multiple_choice(qid, forecast["probability_yes_per_category"])
    elif qtype in ("numeric", "date", "discrete"):
        success = forecast_numeric(qid, forecast["continuous_cdf"])
    
    if success:
        result["status"] = "submitted"
        # Post comment explaining reasoning
        comment = f"## xev0 Bot Forecast\n\nInitial forecast based on base rates and available information.\n\nForecast: {json.dumps(forecast)[:200]}"
        post_comment(post_id, comment)
    else:
        result["status"] = "failed"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Metaculus Bot — xev0")
    parser.add_argument("--tournament", type=int, default=None,
                       help="Tournament ID (default: all open questions)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Don't submit forecasts, just print")
    parser.add_argument("--limit", type=int, default=0,
                       help="Max questions to forecast (0=all)")
    args = parser.parse_args()
    
    print(f"🤖 xev0 Metaculus Bot")
    print(f"   Token: {TOKEN[:12]}...")
    print(f"   Tournament: {args.tournament or 'ALL'}")
    print(f"   Dry run: {args.dry_run}")
    print()
    
    # Get questions
    if args.tournament:
        print(f"Fetching tournament {args.tournament} questions...")
        questions = get_tournament_questions(args.tournament)
    else:
        print("Fetching all open questions...")
        questions = get_all_open_questions()
    
    print(f"Found {len(questions)} open questions")
    
    if args.limit > 0:
        questions = questions[:args.limit]
    
    # Forecast each question
    results = {"submitted": 0, "failed": 0, "skipped": 0}
    for i, q in enumerate(questions):
        title = q.get("title", "")[:50]
        print(f"\n[{i+1}/{len(questions)}] {title}")
        
        result = forecast_question(q, dry_run=args.dry_run)
        print(f"  Status: {result['status']}")
        
        if result["status"] in results:
            results[result["status"]] += 1
        
        # Rate limit
        if not args.dry_run:
            time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Results: {results}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
