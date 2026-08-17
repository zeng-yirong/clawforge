import json
import csv
import os
import sys
import math
from collections import defaultdict

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def read_json_relative(path):
    full = os.path.join(workspace, path)
    if not os.path.exists(full):
        return None
    with open(full, "r") as f:
        return json.load(f)

def path_exists(path):
    return os.path.exists(os.path.join(workspace, path))

def check_score(details, item, score, max_score, passed, reason):
    details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

def main():
    details = []
    total = 0

    # 1. Directory existence
    if path_exists("report"):
        check_score(details, "report directory exists", 5, 5, True, "")
        total += 5
    else:
        check_score(details, "report directory exists", 0, 5, False, "Missing report/ directory")

    # 2. Result file existence
    result_path = "report/avg_by_product_region.json"
    if path_exists(result_path):
        check_score(details, "result JSON file exists", 10, 10, True, "")
        total += 10
    else:
        check_score(details, "result JSON file exists", 0, 10, False, "File not found")
        # cannot continue further checks
        write_final(details, total)
        return

    # 3. JSON valid and is a list
    data = read_json_relative(result_path)
    if data is None:
        check_score(details, "JSON is valid", 0, 10, False, "Failed to parse JSON")
        total += 0
        write_final(details, total)
        return

    if not isinstance(data, list):
        check_score(details, "JSON is a list", 0, 10, False, "Root is not a list")
        total += 0
        write_final(details, total)
        return
    else:
        check_score(details, "JSON is a list", 10, 10, True, "")

    total += 10

    # 4. Field completeness in each entry
    required_fields = {"product_id", "product_name", "region", "avg_order_amount"}
    field_ok = True
    for entry in data:
        if not isinstance(entry, dict):
            field_ok = False
            break
        if not required_fields.issubset(entry.keys()):
            field_ok = False
            break
    if field_ok:
        check_score(details, "all entries have required fields", 10, 10, True, "")
        total += 10
    else:
        check_score(details, "all entries have required fields", 0, 10, False, "Missing or extra fields in entries")

    # 5. Check deduplication: there should be 6 distinct transaction groups (after dedup)
    # We'll compute expected data from the known raw content (simulate dedup and region fill)
    # Hardcode expected groups (product_id, region) and avg amounts
    # Expected based on raw data:
    # P001+Widget A+East: T001 (100.0) -> avg 100.0
    # P001+Widget A+Midwest: T003 (150.0) -> avg 150.0
    # P002+Widget B+West: T002 (200.0) + T006 (250.0) -> avg 225.0
    # P003+Gadget X+South: T004 (300.0) -> avg 300.0
    # P004+Gadget Y+West: T007 (400.0) -> avg 400.0
    # P005+Widget C+East: T008 (50.0) -> avg 50.0
    expected = [
        {"product_id": "P001", "product_name": "Widget A", "region": "East", "avg_order_amount": 100.0},
        {"product_id": "P001", "product_name": "Widget A", "region": "Midwest", "avg_order_amount": 150.0},
        {"product_id": "P002", "product_name": "Widget B", "region": "West", "avg_order_amount": 225.0},
        {"product_id": "P003", "product_name": "Gadget X", "region": "South", "avg_order_amount": 300.0},
        {"product_id": "P004", "product_name": "Gadget Y", "region": "West", "avg_order_amount": 400.0},
        {"product_id": "P005", "product_name": "Widget C", "region": "East", "avg_order_amount": 50.0}
    ]

    # Normalize both lists by sorting
    def sort_key(e):
        return (e["product_id"], e["region"])
    agent_sorted = sorted(data, key=sort_key)
    expected_sorted = sorted(expected, key=sort_key)

    # Compare element by element with tolerance
    match = True
    if len(agent_sorted) != len(expected_sorted):
        match = False
    else:
        for a, e in zip(agent_sorted, expected_sorted):
            if a["product_id"] != e["product_id"] or a["product_name"] != e["product_name"] or a["region"] != e["region"]:
                match = False
                break
            if abs(a["avg_order_amount"] - e["avg_order_amount"]) > 0.01:
                match = False
                break

    if match:
        check_score(details, "correct product-region groups and average amounts", 65, 65, True, "")
        total += 65
    else:
        check_score(details, "correct product-region groups and average amounts", 0, 65, False,
                    f"Expected {len(expected_sorted)} entries, got {len(agent_sorted)}. "
                    f"First mismatch example: Agent {agent_sorted[:2] if agent_sorted else 'empty'} vs Expected {expected_sorted[:2]}")
        total += 0

    # Write final score
    write_final(details, total)

def write_final(details, total_score):
    score_obj = {
        "total_score": total_score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(score_obj, f, indent=2)
    print(f"Total score: {total_score}/100")

if __name__ == "__main__":
    main()
