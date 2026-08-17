import os
import sys
import json

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # Item 1: ops directory exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    item = {
        "item": "ops/ directory exists",
        "max_score": 10,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    if os.path.isdir(ops_dir):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Found ops/ directory."
    else:
        item["reason"] = "ops/ directory not found."
    details.append(item)
    total_score += item["score"]

    # Item 2: launch_key.txt exists (20 points)
    key_path = os.path.join(ops_dir, "launch_key.txt")
    item = {
        "item": "ops/launch_key.txt exists",
        "max_score": 20,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    if os.path.isfile(key_path):
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "File ops/launch_key.txt exists."
    else:
        item["reason"] = "File ops/launch_key.txt not found."
    details.append(item)
    total_score += item["score"]

    # Item 3: Content matches the correct token (70 points)
    item = {
        "item": "launch_key.txt content matches correct token",
        "max_score": 70,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    if os.path.isfile(key_path):
        try:
            with open(key_path, "r") as f:
                content = f.read().strip()
            # The correct token (must match exactly what env_builder placed)
            correct_token = "ORBITAL_LAUNCH_KEY_A1B2C3"
            if content == correct_token:
                item["score"] = 70
                item["passed"] = True
                item["reason"] = f"Exact match: '{correct_token}'."
            else:
                item["reason"] = f"Content mismatch. Got '{content}', expected '{correct_token}'."
        except Exception as e:
            item["reason"] = f"Could not read file: {e}"
    else:
        item["reason"] = "File missing, cannot check content."
    details.append(item)
    total_score += item["score"]

    # Ensure total_score is integer
    result = {
        "total_score": total_score,
        "details": details
    }
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
