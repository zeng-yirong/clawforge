"""
Verify that the agent produced the correct trip plan based on the business requirement.
Scoring criteria:
- Directory structure (ops exists)        : 10 pts
- File ops/trip_plan.json exists          : 10 pts
- Valid JSON                              : 10 pts
- Required fields present (origin, destination, transport, cost, duration_hours, route_id) : 20 pts (each 3.33, rounded to 20)
- Correct origin ("BJS")                  : 10 pts
- Correct destination ("SHA")             : 10 pts
- Correct transport ("high_speed_train")  : 10 pts
- Correct cost (500)                      : 10 pts
- Correct duration_hours (4.5)            : 10 pts
- Correct route_id ("BJS-SHA-001")        : 10 pts
Total = 100
"""

import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base = Path(workspace)

    scores = []
    total = 0

    # 1. ops directory exists
    ops_dir = base / "ops"
    if ops_dir.is_dir():
        scores.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops/ directory."})
        total += 10
    else:
        scores.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ directory not found."})

    # 2. trip_plan.json exists
    plan_path = ops_dir / "trip_plan.json"
    if plan_path.is_file():
        scores.append({"item": "trip_plan.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists."})
        total += 10
    else:
        scores.append({"item": "trip_plan.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found at ops/trip_plan.json."})
        # Cannot proceed further
        return write_score(total, scores)

    # 3. Valid JSON
    try:
        with open(plan_path, "r") as f:
            data = json.load(f)
        scores.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully."})
        total += 10
    except (json.JSONDecodeError, Exception) as e:
        scores.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        return write_score(total, scores)

    # 4. Required fields
    required_fields = ["origin", "destination", "transport", "cost", "duration_hours", "route_id"]
    field_score_per = 20 // len(required_fields)  # 3.33 each, total 20
    field_scores = 0
    for field in required_fields:
        if field in data:
            field_scores += field_score_per
        else:
            scores.append({"item": f"Field '{field}' present", "score": 0, "max_score": field_score_per, "passed": False, "reason": f"Missing field: {field}"})
    # If all present, record as one item for simplicity
    if field_scores == 20:
        scores.append({"item": "All required fields present", "score": 20, "max_score": 20, "passed": True, "reason": "origin, destination, transport, cost, duration_hours, route_id all found."})
        total += 20
    else:
        scores.append({"item": "All required fields present", "score": field_scores, "max_score": 20, "passed": False, "reason": f"Only {field_scores}/{20} points from fields"})
        total += field_scores

    # 5. Correct origin
    if data.get("origin") == "BJS":
        scores.append({"item": "origin == 'BJS'", "score": 10, "max_score": 10, "passed": True, "reason": "Correct origin."})
        total += 10
    else:
        scores.append({"item": "origin == 'BJS'", "score": 0, "max_score": 10, "passed": False, "reason": f"Got '{data.get('origin')}', expected 'BJS'."})

    # 6. Correct destination
    if data.get("destination") == "SHA":
        scores.append({"item": "destination == 'SHA'", "score": 10, "max_score": 10, "passed": True, "reason": "Correct destination."})
        total += 10
    else:
        scores.append({"item": "destination == 'SHA'", "score": 0, "max_score": 10, "passed": False, "reason": f"Got '{data.get('destination')}', expected 'SHA'."})

    # 7. Correct transport
    if data.get("transport") == "high_speed_train":
        scores.append({"item": "transport == 'high_speed_train'", "score": 10, "max_score": 10, "passed": True, "reason": "Correct transport mode."})
        total += 10
    else:
        scores.append({"item": "transport == 'high_speed_train'", "score": 0, "max_score": 10, "passed": False, "reason": f"Got '{data.get('transport')}', expected 'high_speed_train'."})

    # 8. Correct cost (must be numeric 500)
    cost = data.get("cost")
    try:
        cost_val = float(cost)
        if cost_val == 500.0:
            scores.append({"item": "cost == 500", "score": 10, "max_score": 10, "passed": True, "reason": "Correct cost."})
            total += 10
        else:
            scores.append({"item": "cost == 500", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {cost_val}, expected 500."})
    except (TypeError, ValueError):
        scores.append({"item": "cost == 500", "score": 0, "max_score": 10, "passed": False, "reason": f"cost is not numeric: {cost}"})

    # 9. Correct duration_hours (must be numeric 4.5)
    dur = data.get("duration_hours")
    try:
        dur_val = float(dur)
        if dur_val == 4.5:
            scores.append({"item": "duration_hours == 4.5", "score": 10, "max_score": 10, "passed": True, "reason": "Correct duration."})
            total += 10
        else:
            scores.append({"item": "duration_hours == 4.5", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {dur_val}, expected 4.5."})
    except (TypeError, ValueError):
        scores.append({"item": "duration_hours == 4.5", "score": 0, "max_score": 10, "passed": False, "reason": f"duration_hours is not numeric: {dur}"})

    # 10. Correct route_id
    if data.get("route_id") == "BJS-SHA-001":
        scores.append({"item": "route_id == 'BJS-SHA-001'", "score": 10, "max_score": 10, "passed": True, "reason": "Correct route_id."})
        total += 10
    else:
        scores.append({"item": "route_id == 'BJS-SHA-001'", "score": 0, "max_score": 10, "passed": False, "reason": f"Got '{data.get('route_id')}', expected 'BJS-SHA-001'."})

    write_score(total, scores)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
