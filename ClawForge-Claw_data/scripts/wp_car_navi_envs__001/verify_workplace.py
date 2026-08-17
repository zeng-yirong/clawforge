import sys
import json
import os
from pathlib import Path

def verify(workspace: str) -> dict:
    ws = Path(workspace)
    details = []
    total_score = 0
    max_total = 100

    # --- 1. Check that trip_plan.json exists (10 points) ---
    plan_path = ws / "trip_plan.json"
    if plan_path.is_file():
        details.append({
            "item": "trip_plan.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
        total_score += 10
    else:
        details.append({
            "item": "trip_plan.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File does not exist."
        })
        # If file missing, skip further checks and return
        return {"total_score": 0, "details": details}

    # --- 2. Check JSON validity and structure (10 points) ---
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({
            "item": "Valid JSON with 'waypoints' key",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        return {"total_score": total_score, "details": details}

    if not isinstance(data, dict) or "waypoints" not in data:
        details.append({
            "item": "Valid JSON with 'waypoints' key",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing 'waypoints' key or not a dict."
        })
        return {"total_score": total_score, "details": details}

    waypoints = data["waypoints"]
    if not isinstance(waypoints, list):
        details.append({
            "item": "Valid JSON with 'waypoints' key",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "'waypoints' is not a list."
        })
        return {"total_score": total_score, "details": details}

    details.append({
        "item": "Valid JSON with 'waypoints' key",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON with list under 'waypoints'."
    })
    total_score += 10

    # --- 3. Check waypoints list length == 3 (20 points) ---
    if len(waypoints) != 3:
        details.append({
            "item": "Waypoints list contains exactly 3 POIs",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected 3 waypoints, got {len(waypoints)}."
        })
        # Still continue to check IDs for partial credit?
    else:
        details.append({
            "item": "Waypoints list contains exactly 3 POIs",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Length is 3."
        })
        total_score += 20

    # --- 4. Verify each POI ID matches the expected order (50 points total, split per position) ---
    expected_ids = ["food-001", "chrg-001", "hotel-001"]
    passed_all_ids = True
    for i, (actual, expected) in enumerate(zip(waypoints, expected_ids)):
        if not isinstance(actual, str):
            details.append({
                "item": f"Waypoint {i+1} is a valid string POI ID",
                "score": 0,
                "max_score": 16,
                "passed": False,
                "reason": f"Waypoint {i+1} is not a string: {actual}"
            })
            passed_all_ids = False
            continue
        if actual == expected:
            details.append({
                "item": f"Waypoint {i+1} is '{expected}'",
                "score": 16,
                "max_score": 16,
                "passed": True,
                "reason": f"Got '{actual}'."
            })
            total_score += 16
        else:
            details.append({
                "item": f"Waypoint {i+1} is '{expected}'",
                "score": 0,
                "max_score": 16,
                "passed": False,
                "reason": f"Expected '{expected}', got '{actual}'."
            })
            passed_all_ids = False

    # If list had fewer than 3 items, fill remaining details with 0
    while len(details) < 4:  # after the first three checks, we want position checks
        pass  # already covered by loop

    # If any ID missing, we already gave 0 for those indices; adjust total slightly
    # (already done in loop)

    # --- 5. Bonus: ensure no extra keys or unexpected format (10 points) ---
    # Only check if top-level keys exceed 'waypoints'
    extra_keys = set(data.keys()) - {"waypoints"}
    if extra_keys:
        details.append({
            "item": "No unnecessary top-level keys",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Unexpected keys: {extra_keys}"
        })
    else:
        details.append({
            "item": "No unnecessary top-level keys",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only 'waypoints' present."
        })
        total_score += 10

    # Clamp total to 0-100
    total_score = max(0, min(100, total_score))
    return {"total_score": total_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # Write score file
    score_path = Path(workspace) / "workplace_score.json"
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Verification complete. Total score: {result['total_score']}/100")

if __name__ == "__main__":
    main()
