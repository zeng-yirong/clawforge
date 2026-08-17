import os
import sys
import json

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # --- 1. Directory structure (10 points) ---
    item = {"item": "ops directory exists", "max_score": 5, "score": 0, "passed": False, "reason": ""}
    if os.path.isdir(os.path.join(workspace, "ops")):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "ops/ directory found"
    else:
        item["reason"] = "ops/ directory missing"
    details.append(item)
    total_score += item["score"]

    item = {"item": "output file exists", "max_score": 5, "score": 0, "passed": False, "reason": ""}
    output_path = os.path.join(workspace, "ops", "high_value_competitors.json")
    if os.path.isfile(output_path):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "ops/high_value_competitors.json found"
    else:
        item["reason"] = "ops/high_value_competitors.json missing"
    details.append(item)
    total_score += item["score"]

    # --- 2. JSON validity and structure (15 points) ---
    item = {"item": "output file is valid JSON", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    try:
        with open(output_path, 'r') as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Valid JSON parsed"
    except Exception as e:
        item["reason"] = f"Invalid JSON: {e}"
        # If file doesn't exist, skip further checks
        details.append(item)
        total_score += 0
        # Return early with remaining scores zero
        for missing_item in ["correct structure", "competitor_id present", "total_ltv correct"]:
            details.append({"item": missing_item, "max_score": 25, "score": 0, "passed": False, "reason": "Output file missing/invalid"})
        return {"total_score": total_score, "details": details}
    details.append(item)
    total_score += item["score"]

    # Check structure: must be a list of objects with 'competitor_id' and 'total_ltv'
    item = {"item": "output is a list with required fields", "max_score": 5, "score": 0, "passed": False, "reason": ""}
    if isinstance(data, list) and all(isinstance(entry, dict) and "competitor_id" in entry and "total_ltv" in entry for entry in data):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = f"List of {len(data)} entries with competitor_id and total_ltv"
    else:
        item["reason"] = "Expected list of dicts with competitor_id and total_ltv"
    details.append(item)
    total_score += item["score"]

    # --- 3. Content correctness (70 points) ---
    # Expected answer: only CloudMajor with total_ltv = 8000+6000 = 14000
    expected = [{"competitor_id": "CloudMajor", "total_ltv": 14000}]
    # Normalize (sort by competitor_id)
    # Sort both expected and data
    data_sorted = sorted(data, key=lambda x: x.get("competitor_id", ""))
    expected_sorted = sorted(expected, key=lambda x: x["competitor_id"])

    # Check length match
    item = {"item": "correct number of entries", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if len(data_sorted) == len(expected_sorted):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"Found {len(data_sorted)} entries, expected {len(expected_sorted)}"
    else:
        item["reason"] = f"Expected {len(expected_sorted)} entries, got {len(data_sorted)}"
    details.append(item)
    total_score += item["score"]

    # Check each expected entry exists with exact total_ltv (within integer equality)
    item = {"item": "competitor_id and total_ltv match expected", "max_score": 60, "score": 0, "passed": False, "reason": ""}
    all_match = True
    for exp in expected_sorted:
        found = False
        for d in data_sorted:
            if d.get("competitor_id") == exp["competitor_id"] and d.get("total_ltv") == exp["total_ltv"]:
                found = True
                break
        if not found:
            all_match = False
            break
    if all_match and len(data_sorted) == len(expected_sorted):
        item["score"] = 60
        item["passed"] = True
        item["reason"] = "All entries match exact expected values"
    else:
        item["reason"] = f"Expected {expected_sorted}, got {data_sorted}"
    details.append(item)
    total_score += item["score"]

    # --- 4. No extra or missing fields per entry (5 points) ---
    item = {"item": "no extra fields in entries", "max_score": 5, "score": 0, "passed": False, "reason": ""}
    extra_found = False
    for entry in data_sorted:
        keys = set(entry.keys())
        if keys != {"competitor_id", "total_ltv"}:
            extra_found = True
            break
    if not extra_found:
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "All entries contain exactly two required fields"
    else:
        item["reason"] = "Some entries have extra keys"
    details.append(item)
    total_score += item["score"]

    # Final total capped
    total_score = min(total_score, max_total)
    return {"total_score": total_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # Write score file
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
