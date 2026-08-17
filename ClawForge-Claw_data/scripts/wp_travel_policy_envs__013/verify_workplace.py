import sys
import json
import os
import re
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace).resolve()

    score_details = []
    total_score = 0
    max_total = 100

    # 1) Check that ops/booking_candidate.json exists
    result_path = workspace_path / "ops" / "booking_candidate.json"
    item1 = {"item": "File ops/booking_candidate.json exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if result_path.exists():
        item1["score"] = 10
        item1["passed"] = True
        item1["reason"] = "File found."
    else:
        item1["reason"] = "File not found. Cannot proceed."
        score_details.append(item1)
        # If file missing, no further checks possible; give 0 total
        result = {"total_score": 0, "details": score_details}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Missing required output file. Total score: 0")
        return

    # Parse JSON
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        item1["reason"] = f"Invalid JSON: {e}"
        score_details.append(item1)
        result = {"total_score": 0, "details": score_details}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Invalid JSON. Total score: 0")
        return

    item1["score"] = 10
    item1["passed"] = True
    item1["reason"] = "File exists and is valid JSON."
    score_details.append(item1)
    total_score += 10

    # 2) Validate JSON is a dict and contains all required fields
    required_fields = ["flight_id", "platform_id", "total_cost", "policy_id", "policy_version", "meets_policy", "requires_approval"]
    item2 = {"item": "JSON contains all required fields", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if not isinstance(data, dict):
        item2["reason"] = "Root element is not a JSON object."
        score_details.append(item2)
        result = {"total_score": total_score, "details": score_details}
        # still continue to compute partial
    else:
        missing = [f for f in required_fields if f not in data]
        if missing:
            item2["reason"] = f"Missing fields: {', '.join(missing)}"
            item2["score"] = 0
        else:
            item2["score"] = 20
            item2["passed"] = True
            item2["reason"] = "All required fields present."
        score_details.append(item2)
        total_score += item2["score"]

    # 3) Check each field value
    # flight_id = "flight-001"
    item3 = {"item": "flight_id = 'flight-001'", "score": 0, "max_score": 15, "passed": False, "reason": ""}
    if isinstance(data, dict) and data.get("flight_id") == "flight-001":
        item3["score"] = 15
        item3["passed"] = True
        item3["reason"] = "Correct flight_id."
    else:
        item3["reason"] = f"Expected 'flight-001', got {data.get('flight_id')!r}"
    score_details.append(item3)
    total_score += item3["score"]

    # platform_id = "skybook"
    item4 = {"item": "platform_id = 'skybook'", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if isinstance(data, dict) and data.get("platform_id") == "skybook":
        item4["score"] = 10
        item4["passed"] = True
        item4["reason"] = "Correct platform_id."
    else:
        item4["reason"] = f"Expected 'skybook', got {data.get('platform_id')!r}"
    score_details.append(item4)
    total_score += item4["score"]

    # total_cost = 2150.0 (float or int, check numeric)
    item5 = {"item": "total_cost = 2150.0", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if isinstance(data, dict):
        try:
            val = float(data.get("total_cost"))
            if abs(val - 2150.0) < 0.001:
                item5["score"] = 20
                item5["passed"] = True
                item5["reason"] = f"Correct total_cost: {val}"
            else:
                item5["reason"] = f"Expected 2150.0, got {val}"
        except (TypeError, ValueError):
            item5["reason"] = f"total_cost not a number: {data.get('total_cost')!r}"
    else:
        item5["reason"] = "Not a dict."
    score_details.append(item5)
    total_score += item5["score"]

    # policy_id = "policy_002"
    item6 = {"item": "policy_id = 'policy_002'", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if isinstance(data, dict) and data.get("policy_id") == "policy_002":
        item6["score"] = 5
        item6["passed"] = True
        item6["reason"] = "Correct policy_id."
    else:
        item6["reason"] = f"Expected 'policy_002', got {data.get('policy_id')!r}"
    score_details.append(item6)
    total_score += item6["score"]

    # policy_version = "2.0"
    item7 = {"item": "policy_version = '2.0'", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if isinstance(data, dict) and data.get("policy_version") == "2.0":
        item7["score"] = 5
        item7["passed"] = True
        item7["reason"] = "Correct policy_version."
    else:
        item7["reason"] = f"Expected '2.0', got {data.get('policy_version')!r}"
    score_details.append(item7)
    total_score += item7["score"]

    # meets_policy = True
    item8 = {"item": "meets_policy = true", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if isinstance(data, dict):
        v = data.get("meets_policy")
        if v is True:
            item8["score"] = 5
            item8["passed"] = True
            item8["reason"] = "meets_policy is true."
        else:
            item8["reason"] = f"Expected true, got {v!r}"
    else:
        item8["reason"] = "Not a dict."
    score_details.append(item8)
    total_score += item8["score"]

    # requires_approval = True
    item9 = {"item": "requires_approval = true", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if isinstance(data, dict):
        v = data.get("requires_approval")
        if v is True:
            item9["score"] = 5
            item9["passed"] = True
            item9["reason"] = "requires_approval is true."
        else:
            item9["reason"] = f"Expected true, got {v!r}"
    else:
        item9["reason"] = "Not a dict."
    score_details.append(item9)
    total_score += item9["score"]

    # Optional: penalize extra fields (max -5)
    extra_fields = set(data.keys()) - set(required_fields) if isinstance(data, dict) else set()
    if extra_fields:
        penalty = min(5, len(extra_fields) * 2)  # each extra field costs 2 points up to 5
        total_score -= penalty
        # Add a note but not as an item
        # We can add a detail item for transparency
        extra_item = {"item": "No extra fields", "score": -penalty, "max_score": 0, "passed": False, "reason": f"Extra fields: {', '.join(extra_fields)}"}
        score_details.append(extra_item)

    # Ensure total_score does not exceed max
    total_score = max(0, min(total_score, max_total))

    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(workspace_path / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Total score: {total_score}/{max_total}")

if __name__ == "__main__":
    main()
