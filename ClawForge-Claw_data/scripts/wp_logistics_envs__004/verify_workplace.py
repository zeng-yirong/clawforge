import sys
import os
import json

def verify(workspace: str):
    details = []
    total = 0
    max_total = 100

    # check ops directory exists
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops/ directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found ops/ directory"
        })
        total += 10
    else:
        details.append({
            "item": "ops/ directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })
        # If ops dir missing, rest is impossible
        print(json.dumps({"total_score": total, "details": details}))
        return

    # check kill_target.json exists
    target_path = os.path.join(ops_dir, "kill_target.json")
    if os.path.isfile(target_path):
        details.append({
            "item": "ops/kill_target.json file exists",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Target file found"
        })
        total += 20
    else:
        details.append({
            "item": "ops/kill_target.json file exists",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "File not found"
        })
        print(json.dumps({"total_score": total, "details": details}))
        return

    # parse JSON
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON is valid",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Successfully parsed JSON"
        })
        total += 20
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        print(json.dumps({"total_score": total, "details": details}))
        return

    # check required field transaction_id
    if "transaction_id" in data:
        details.append({
            "item": "Field 'transaction_id' exists",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Required field present"
        })
        total += 20
    else:
        details.append({
            "item": "Field 'transaction_id' exists",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Missing 'transaction_id' key"
        })
        print(json.dumps({"total_score": total, "details": details}))
        return

    # check correct value
    correct_id = "txn_045"
    if data["transaction_id"] == correct_id:
        details.append({
            "item": "transaction_id value is correct",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"Value matches expected '{correct_id}'"
        })
        total += 30
    else:
        details.append({
            "item": "transaction_id value is correct",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Got '{data['transaction_id']}', expected '{correct_id}'"
        })

    # Total already in [0,100], ensure integer
    total = int(total)
    result = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
