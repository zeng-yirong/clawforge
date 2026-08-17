import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # Check ops directory
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops/"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # Check reject.json file
    reject_path = os.path.join(workspace, "ops", "reject.json")
    if os.path.isfile(reject_path):
        details.append({"item": "reject.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops/reject.json"})
        score += 10
    else:
        details.append({"item": "reject.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        write_score(workspace, score, details)
        return

    # Parse JSON
    try:
        with open(reject_path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            details.append({"item": "reject.json is valid JSON object", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON dict"})
            score += 10
        else:
            details.append({"item": "reject.json is valid JSON object", "score": 0, "max_score": 10, "passed": False, "reason": "Not a dict"})
            write_score(workspace, score, details)
            return
    except Exception as e:
        details.append({"item": "reject.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {str(e)}"})
        write_score(workspace, score, details)
        return

    # Check request_id
    rid = data.get("request_id")
    if rid == "req_007":
        details.append({"item": "request_id field is 'req_007'", "score": 30, "max_score": 30, "passed": True, "reason": "Correct request ID"})
        score += 30
    else:
        details.append({"item": "request_id field is 'req_007'", "score": 0, "max_score": 30, "passed": False, "reason": f"Found '{rid}' instead of 'req_007'"})

    # Check signed_by
    signer = data.get("signed_by")
    if signer == "Alice":
        details.append({"item": "signed_by field is 'Alice'", "score": 30, "max_score": 30, "passed": True, "reason": "Correct signer"})
        score += 30
    else:
        details.append({"item": "signed_by field is 'Alice'", "score": 0, "max_score": 30, "passed": False, "reason": f"Found '{signer}' instead of 'Alice'"})

    final_score = min(score, 100)
    write_score(workspace, final_score, details)

def write_score(workspace, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
