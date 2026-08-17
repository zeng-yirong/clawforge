#!/usr/bin/env python3
"""
Verifier for wp_finance_envs__006.
Checks that the agent produced result.json with the correct ticker and revenue_beat_pct.
"""

import json
import os
import sys

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # 1) File existence (10 pts)
    filepath = os.path.join(workspace, "result.json")
    if os.path.isfile(filepath):
        details.append({
            "item": "result.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found at workspace root."
        })
        total_score += 10
    else:
        details.append({
            "item": "result.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"File not found at {filepath}."
        })
        # No need to continue if file missing
        return {"total_score": total_score, "details": details}

    # 2) JSON validity (10 pts)
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        details.append({
            "item": "result.json is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File parsed successfully."
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "result.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        return {"total_score": total_score, "details": details}

    # 3) Contains ticker field (10 pts)
    if "ticker" in data and isinstance(data["ticker"], str):
        details.append({
            "item": "Contains 'ticker' field (string)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"ticker field present: {data['ticker']}"
        })
        total_score += 10
    else:
        details.append({
            "item": "Contains 'ticker' field (string)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ticker field missing or not a string."
        })

    # 4) Contains revenue_beat_pct field (10 pts)
    if "revenue_beat_pct" in data and isinstance(data["revenue_beat_pct"], (int, float)):
        details.append({
            "item": "Contains 'revenue_beat_pct' field (numeric)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"revenue_beat_pct field present: {data['revenue_beat_pct']}"
        })
        total_score += 10
    else:
        details.append({
            "item": "Contains 'revenue_beat_pct' field (numeric)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "revenue_beat_pct field missing or not numeric."
        })

    # 5) No extra unexpected fields (10 pts)
    expected_keys = {"ticker", "revenue_beat_pct"}
    actual_keys = set(data.keys())
    extra = actual_keys - expected_keys
    if not extra:
        details.append({
            "item": "No extra unexpected fields",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only ticker and revenue_beat_pct present."
        })
        total_score += 10
    else:
        details.append({
            "item": "No extra unexpected fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Unexpected fields found: {extra}"
        })

    # 6) Ticker value correct (20 pts)
    expected_ticker = "TECH"
    if data.get("ticker") == expected_ticker:
        details.append({
            "item": "Correct ticker",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"ticker is '{expected_ticker}'."
        })
        total_score += 20
    else:
        details.append({
            "item": "Correct ticker",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected '{expected_ticker}', got '{data.get('ticker')}'."
        })

    # 7) Revenue_beat_pct value correct (30 pts)
    # The ground truth: TECH Q2 2026 has revenue_beat_pct = 19.05 (from earnings.json)
    expected_beat = 19.05
    beat_val = data.get("revenue_beat_pct")
    # Use tolerance for floating point (though JSON exact representation)
    if isinstance(beat_val, (int, float)) and abs(beat_val - expected_beat) < 1e-9:
        details.append({
            "item": "Correct revenue_beat_pct",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"revenue_beat_pct is {beat_val} (expected {expected_beat})."
        })
        total_score += 30
    else:
        details.append({
            "item": "Correct revenue_beat_pct",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Expected {expected_beat}, got {beat_val}."
        })

    return {"total_score": total_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # Write score file
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {score_path}: {result['total_score']}/100")

if __name__ == "__main__":
    main()
