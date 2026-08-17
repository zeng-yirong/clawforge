#!/usr/bin/env python3
import json
import sys
import os

def verify(workspace):
    score = 0
    details = []
    total_max = 100

    # 1. Required directories (10 pts)
    dirs_ok = True
    for d in ["ops", "data"]:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_ok = False
            break
    if dirs_ok:
        score += 10
        details.append({"item": "Required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "ops and data present"})
    else:
        details.append({"item": "Required directories exist", "score": 0, "max_score": 10, "passed": False, "reason": "ops or data missing"})

    # 2. fix_schedule.json exists (10 pts)
    fix_path = os.path.join(workspace, "ops", "fix_schedule.json")
    if os.path.isfile(fix_path):
        score += 10
        details.append({"item": "fix_schedule.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
    else:
        details.append({"item": "fix_schedule.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # Cannot continue scoring JSON-dependent items
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 3. Valid JSON (10 pts)
    try:
        with open(fix_path, "r") as f:
            data = json.load(f)
        score += 10
        details.append({"item": "fix_schedule.json valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parse success"})
    except Exception as e:
        details.append({"item": "fix_schedule.json valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON error: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 4. Contains key "schedule_id" (20 pts)
    if "schedule_id" in data:
        score += 20
        details.append({"item": "Has key schedule_id", "score": 20, "max_score": 20, "passed": True, "reason": "key present"})
    else:
        details.append({"item": "Has key schedule_id", "score": 0, "max_score": 20, "passed": False, "reason": "key missing"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 5. Value equals "sched_002" (50 pts)
    if data["schedule_id"] == "sched_002":
        score += 50
        details.append({"item": "Correct schedule_id value", "score": 50, "max_score": 50, "passed": True, "reason": "value is sched_002"})
    else:
        details.append({"item": "Correct schedule_id value", "score": 0, "max_score": 50, "passed": False, "reason": f"got {data['schedule_id']}"})

    # Write final score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
