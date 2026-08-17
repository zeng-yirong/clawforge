import json
import os
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    max_total = 100

    # 1. Directory existence (10)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score += 10
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops directory found"})
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops directory missing"})

    # 2. File existence (10)
    summary_path = os.path.join(ops_dir, "brief_summary.json")
    if os.path.isfile(summary_path):
        score += 10
        details.append({"item": "brief_summary.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
    else:
        details.append({"item": "brief_summary.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # If file missing, no further checks possible
        total_score = score
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Score: {total_score}/100")
        return result

    # 3. Valid JSON (10)
    try:
        with open(summary_path, "r") as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
    except (json.JSONDecodeError, ValueError) as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {e}"})
        total_score = score
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Score: {total_score}/100")
        return result

    # 4. Field checks (20 each)
    expected_fields = {
        "product_name": "AuraSync",
        "launch_date": "2025-09-15",
        "version": "3.2.1"
    }

    field_score = 0
    for field, expected_value in expected_fields.items():
        if field in data:
            if data[field] == expected_value:
                field_score += 20
                details.append({"item": f"field '{field}' correct", "score": 20, "max_score": 20, "passed": True, "reason": f"value '{data[field]}' matches expected"})
            else:
                details.append({"item": f"field '{field}' correct", "score": 0, "max_score": 20, "passed": False, "reason": f"expected '{expected_value}', got '{data[field]}'"})
        else:
            details.append({"item": f"field '{field}' correct", "score": 0, "max_score": 20, "passed": False, "reason": f"field missing from JSON"})
    score += field_score

    # 5. Extra fields penalty (up to -10)
    extra_fields = [k for k in data if k not in expected_fields]
    if extra_fields:
        penalty = min(len(extra_fields) * 5, 10)
        score -= penalty
        details.append({"item": "no extra fields", "score": -penalty, "max_score": 0, "passed": False, "reason": f"extra fields found: {extra_fields}, penalty -{penalty}"})
    else:
        details.append({"item": "no extra fields", "score": 0, "max_score": 0, "passed": True, "reason": "no extra fields"})

    # Ensure score between 0 and 100
    total_score = max(0, min(score, 100))
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")
    return result

if __name__ == "__main__":
    verify()
