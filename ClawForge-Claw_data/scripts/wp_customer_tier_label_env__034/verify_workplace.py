import json
import os
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. Check directory structure (ops/ exists)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ not found"})

    # 2. Check label_updates.json exists
    updates_path = os.path.join(workspace, "ops", "label_updates.json")
    if os.path.isfile(updates_path):
        details.append({"item": "label_updates.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "File found"})
        score += 5
    else:
        details.append({"item": "label_updates.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "File missing"})
        # continue to allow partial scoring

    # 3. Parse JSON and validate structure
    if os.path.isfile(updates_path):
        try:
            with open(updates_path, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                details.append({"item": "JSON is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON array"})
                score += 10
            else:
                details.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": "Root is not a list"})
                data = []  # treat as empty
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
            data = []
    else:
        details.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})
        data = []

    # 4. Each item must have customer_id, tier, labels
    required_fields = {"customer_id", "tier", "labels"}
    field_ok = True
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            field_ok = False
            break
        if not required_fields.issubset(item.keys()):
            field_ok = False
            break
        if not isinstance(item.get("labels"), list):
            field_ok = False
            break
    if field_ok:
        details.append({"item": "All items have required fields", "score": 10, "max_score": 10, "passed": True, "reason": "Fields correct"})
        score += 10
    else:
        details.append({"item": "All items have required fields", "score": 0, "max_score": 10, "passed": False, "reason": "Missing or invalid fields"})

    # 5. Expected updates: C001 and C002 only
    expected = {
        "C001": {"tier": "enterprise", "labels": ["premium", "high_value"]},
        "C002": {"tier": "mid_market", "labels": ["growth"]}
    }
    expected_ids = set(expected.keys())
    actual_ids = {item.get("customer_id") for item in data if isinstance(item, dict)}

    # 5a. Count correctness (exactly 2 items)
    if len(data) == 2:
        details.append({"item": "Exactly 2 updates", "score": 15, "max_score": 15, "passed": True, "reason": "List has 2 items"})
        score += 15
    else:
        details.append({"item": "Exactly 2 updates", "score": 0, "max_score": 15, "passed": False, "reason": f"Found {len(data)} items, expected 2"})

    # 5b. C001 correct
    c001_item = next((x for x in data if isinstance(x, dict) and x.get("customer_id") == "C001"), None)
    if c001_item and c001_item["tier"] == expected["C001"]["tier"] and sorted(c001_item["labels"]) == sorted(expected["C001"]["labels"]):
        details.append({"item": "C001 tier and labels correct", "score": 20, "max_score": 20, "passed": True, "reason": "C001 enterprise + premium,high_value"})
        score += 20
    else:
        details.append({"item": "C001 tier and labels correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Got {c001_item}" if c001_item else "Missing C001"})

    # 5c. C002 correct
    c002_item = next((x for x in data if isinstance(x, dict) and x.get("customer_id") == "C002"), None)
    if c002_item and c002_item["tier"] == expected["C002"]["tier"] and sorted(c002_item["labels"]) == sorted(expected["C002"]["labels"]):
        details.append({"item": "C002 tier and labels correct", "score": 20, "max_score": 20, "passed": True, "reason": "C002 mid_market + growth"})
        score += 20
    else:
        details.append({"item": "C002 tier and labels correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Got {c002_item}" if c002_item else "Missing C002"})

    # 5d. No extra customers (like C003, C004, C005, C006, C007) are present
    forbidden = actual_ids - expected_ids
    if not forbidden:
        details.append({"item": "No unexpected customers in updates", "score": 10, "max_score": 10, "passed": True, "reason": "Only C001 and C002"})
        score += 10
    else:
        details.append({"item": "No unexpected customers in updates", "score": 0, "max_score": 10, "passed": False, "reason": f"Found extra customers: {forbidden}"})

    # total score
    total = min(score, 100)
    result = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
