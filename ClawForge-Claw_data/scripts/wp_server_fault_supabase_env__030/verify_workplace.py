import json
import os
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_total = 100
    details = []

    # 1. Directory structure (10 points)
    dirs_ok = True
    required_dirs = [
        os.path.join(workspace, "ops"),
        os.path.join(workspace, "data")
    ]
    for d in required_dirs:
        if not os.path.isdir(d):
            dirs_ok = False
            break
    if dirs_ok:
        details.append({
            "item": "Required directories exist",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ and data/ directories found"
        })
        score += 10
    else:
        details.append({
            "item": "Required directories exist",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing one or more directories"
        })

    # 2. Target file exists (10 points)
    target_path = os.path.join(workspace, "ops", "kill_targets.json")
    if os.path.isfile(target_path):
        details.append({
            "item": "ops/kill_targets.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found"
        })
        score += 10
    else:
        details.append({
            "item": "ops/kill_targets.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # If file missing, we can't check further content, but we still continue
        # other checks will fail gracefully.

    # 3. JSON valid (10 points)
    file_valid = False
    data = None
    if os.path.isfile(target_path):
        try:
            with open(target_path, "r") as f:
                data = json.load(f)
            file_valid = True
        except (json.JSONDecodeError, IOError):
            pass
    if file_valid:
        details.append({
            "item": "Target file contains valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully"
        })
        score += 10
    else:
        details.append({
            "item": "Target file contains valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Invalid JSON or unreadable"
        })

    # 4. Correct structure: object with "targets" list (20 points)
    structure_ok = False
    if isinstance(data, dict) and "targets" in data and isinstance(data["targets"], list):
        structure_ok = True
        details.append({
            "item": "Correct structure: JSON object with 'targets' array",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Structure correct"
        })
        score += 20
    else:
        details.append({
            "item": "Correct structure: JSON object with 'targets' array",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got type {type(data).__name__}, missing 'targets' or not list"
        })

    # 5. Correct transaction ID (40 points)
    id_correct = False
    if structure_ok:
        if len(data["targets"]) == 1 and data["targets"][0] == "tx_ab12cd34":
            id_correct = True
            details.append({
                "item": "Target contains exactly one transaction ID 'tx_ab12cd34'",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": "ID matches expected"
            })
            score += 40
        else:
            details.append({
                "item": "Target contains exactly one transaction ID 'tx_ab12cd34'",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": f"Got {data['targets']}"
            })
    else:
        details.append({
            "item": "Target contains exactly one transaction ID 'tx_ab12cd34'",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "Structure was invalid"
        })

    # 6. No extra fields in JSON (10 points)
    extra_ok = False
    if isinstance(data, dict):
        allowed_keys = {"targets"}
        extra_keys = set(data.keys()) - allowed_keys
        if not extra_keys:
            extra_ok = True
            details.append({
                "item": "No extra top-level fields",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Only 'targets' present"
            })
            score += 10
        else:
            details.append({
                "item": "No extra top-level fields",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Extra keys: {extra_keys}"
            })
    else:
        details.append({
            "item": "No extra top-level fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Data not a dict"
        })

    total_score = min(score, max_total)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Total score: {total_score}/{max_total}")
    return total_score

if __name__ == "__main__":
    verify()
