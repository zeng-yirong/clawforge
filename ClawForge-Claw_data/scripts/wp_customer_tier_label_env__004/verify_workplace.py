import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. Check that ops directory exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops directory found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops directory not found"})

    # 2. Check that segment_result.json exists (10 points)
    result_path = os.path.join(ops_dir, "segment_result.json") if ops_dir != workspace else os.path.join(workspace, "ops", "segment_result.json")
    if os.path.isfile(result_path):
        details.append({"item": "segment_result.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "segment_result.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # If file missing, still try to read? No, can't proceed.
        write_score(workspace, total_score, details)
        return

    # 3. Parse JSON and check format (10 points)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        details.append({"item": "Valid JSON format", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        write_score(workspace, total_score, details)
        return

    if not isinstance(data, dict) or "segments" not in data or not isinstance(data["segments"], list):
        details.append({"item": "Valid JSON format", "score": 0, "max_score": 10, "passed": False, "reason": "Expected top-level key 'segments' with list value"})
        write_score(workspace, total_score, details)
        return
    details.append({"item": "Valid JSON format", "score": 10, "max_score": 10, "passed": True, "reason": "JSON structure correct"})
    total_score += 10

    # 4. Check each segment entry has only customer_id and new_tier (field integrity, 10 points)
    segments = data["segments"]
    all_fields_ok = True
    for i, entry in enumerate(segments):
        if not isinstance(entry, dict):
            all_fields_ok = False
            break
        keys = set(entry.keys())
        if keys != {"customer_id", "new_tier"}:
            all_fields_ok = False
            break
        if not isinstance(entry.get("customer_id"), str) or not isinstance(entry.get("new_tier"), str):
            all_fields_ok = False
            break
    if all_fields_ok:
        details.append({"item": "Each record has only customer_id and new_tier (strings)", "score": 10, "max_score": 10, "passed": True, "reason": "All records meet field requirements"})
        total_score += 10
    else:
        details.append({"item": "Each record has only customer_id and new_tier (strings)", "score": 0, "max_score": 10, "passed": False, "reason": "Some records have missing/extra fields or wrong types"})
        # Continue to check content but note penalty

    # 5. Check correct tier for each expected customer (50 points, 10 per customer)
    expected = {
        "C001": "platinum",
        "C002": "silver",
        "C003": "silver",
        "C004": "bronze",
        "C005": "gold"
    }
    # Build a lookup from agent output
    result_map = {}
    for entry in segments:
        cid = entry.get("customer_id")
        if cid:
            result_map[cid] = entry.get("new_tier")

    # Score per customer
    customer_score = 0
    customer_max = 50  # 5 customers * 10
    per_customer_max = 10
    for cid, correct_tier in expected.items():
        if cid not in result_map:
            details.append({"item": f"Customer {cid} present", "score": 0, "max_score": per_customer_max, "passed": False, "reason": "Customer ID missing in output"})
        else:
            if result_map[cid] == correct_tier:
                details.append({"item": f"Customer {cid} tier correct", "score": per_customer_max, "max_score": per_customer_max, "passed": True, "reason": f"Tier is {correct_tier}"})
                customer_score += per_customer_max
            else:
                details.append({"item": f"Customer {cid} tier correct", "score": 0, "max_score": per_customer_max, "passed": False, "reason": f"Expected {correct_tier}, got {result_map[cid]}"})
    total_score += customer_score

    # 6. Penalty for extra customers not expected (max -20)
    extra_customers = set(result_map.keys()) - set(expected.keys())
    penalty = 0
    for cid in extra_customers:
        penalty += 5
        details.append({"item": f"No extra customer {cid}", "score": 0, "max_score": 0, "passed": False, "reason": f"Unexpected customer {cid} found in output"})
    penalty = min(penalty, 20)
    if penalty > 0:
        total_score = total_score - penalty
        details.append({"item": "Penalty for extra customers", "score": -penalty, "max_score": 0, "passed": False, "reason": f"Subtracted {penalty} points for {len(extra_customers)} extra customers"})

    # Clamp total between 0 and 100
    total_score = max(0, min(100, total_score))
    write_score(workspace, total_score, details)

def write_score(workspace, total_score, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    output = {
        "total_score": total_score,
        "details": details
    }
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written to {score_path}")

if __name__ == "__main__":
    main()
