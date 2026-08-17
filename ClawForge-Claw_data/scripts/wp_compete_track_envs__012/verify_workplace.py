import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    details = []

    # ---------- 1. Directory structure (10 points) ----------
    expected_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(expected_dir)
    if dir_exists:
        total_score += 10
        details.append({
            "item": "Directory 'ops/' exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found."
        })
    else:
        details.append({
            "item": "Directory 'ops/' exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found."
        })

    # ---------- 2. File exists and valid JSON (10 points) ----------
    alert_path = os.path.join(workspace, "ops", "alert_impact.json")
    file_found = os.path.isfile(alert_path)
    json_valid = False
    parsed = None
    if file_found:
        try:
            with open(alert_path, "r") as f:
                parsed = json.load(f)
            json_valid = True
            total_score += 10
            details.append({
                "item": "alert_impact.json exists and is valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "File present and parseable."
            })
        except (json.JSONDecodeError, Exception) as e:
            total_score += 0
            details.append({
                "item": "alert_impact.json exists and is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"File is not valid JSON: {str(e)}"
            })
    else:
        details.append({
            "item": "alert_impact.json exists and is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })

    # ---------- 3. Required fields present (10 points) ----------
    required_fields = ["competitor_name", "policy_title", "affected_user_count", "affected_revenue", "risk_level"]
    fields_ok = True
    missing_fields = []
    if parsed and isinstance(parsed, dict):
        for f in required_fields:
            if f not in parsed:
                fields_ok = False
                missing_fields.append(f)
        if fields_ok:
            total_score += 10
            details.append({
                "item": "Required fields present",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"All required fields found: {required_fields}"
            })
        else:
            details.append({
                "item": "Required fields present",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Missing fields: {missing_fields}"
            })
    else:
        details.append({
            "item": "Required fields present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Parsed object is not a dict or missing."
        })

    # ---------- 4. Field values correctness (70 points) ----------
    # Only proceed if fields are present.
    value_score = 0
    max_value_score = 70
    if parsed and isinstance(parsed, dict) and fields_ok:
        sub_score = 0
        # 4a competitor_name (5 points)
        if parsed.get("competitor_name") == "DataFlow AI":
            sub_score += 5
        else:
            details.append({
                "item": "competitor_name correct",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Expected 'DataFlow AI', got '{parsed.get('competitor_name')}'"
            })
        # 4b policy_title (5 points)
        if parsed.get("policy_title") == "EU Digital Markets Act Compliance":
            sub_score += 5
        else:
            details.append({
                "item": "policy_title correct",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Expected 'EU Digital Markets Act Compliance', got '{parsed.get('policy_title')}'"
            })
        # 4c affected_user_count (20 points) -> expected 3
        expected_user_count = 3
        if parsed.get("affected_user_count") == expected_user_count:
            sub_score += 20
        else:
            details.append({
                "item": "affected_user_count correct",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"Expected {expected_user_count}, got {parsed.get('affected_user_count')}"
            })
        # 4d affected_revenue (20 points) -> expected 15000+20000+25000 = 60000
        expected_revenue = 15000 + 20000 + 25000  # 60000
        if parsed.get("affected_revenue") == expected_revenue:
            sub_score += 20
        else:
            details.append({
                "item": "affected_revenue correct",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"Expected {expected_revenue}, got {parsed.get('affected_revenue')}"
            })
        # 4e risk_level (20 points) -> from policy impact_level "high"
        if parsed.get("risk_level") == "high":
            sub_score += 20
        else:
            details.append({
                "item": "risk_level correct",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"Expected 'high', got '{parsed.get('risk_level')}'"
            })
        # Add collected sub_score to total
        total_score += sub_score
        # Record details for value items (only if failed)
        if sub_score < 70:
            # Already added per-item failures above; need to ensure we don't double count.
            # Actually we appended only on failure. If all passed, we add a single summary.
            if sub_score == 70:
                details.append({
                    "item": "All field values correct",
                    "score": 70,
                    "max_score": 70,
                    "passed": True,
                    "reason": "All values match expected."
                })
    else:
        # If fields missing or not parsed, give 0 for this section
        total_score += 0
        details.append({
            "item": "Field values correctness",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "Cannot verify values due to earlier failures."
        })

    # ---------- Final output ----------
    total_score = min(total_score, 100)  # cap
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {score_path}: {total_score}/100")

if __name__ == "__main__":
    main()
