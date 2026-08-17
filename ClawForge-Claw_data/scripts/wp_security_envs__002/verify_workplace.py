import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score = 0
details = []

def check(passed, reason, max_score, item):
    details.append({
        "item": item,
        "score": max_score if passed else 0,
        "max_score": max_score,
        "passed": passed,
        "reason": reason if not passed else "OK"
    })
    return max_score if passed else 0

# 1. ops directory exists (10)
ops_dir = os.path.join(workspace, "ops")
exists_ops = os.path.isdir(ops_dir)
score += check(exists_ops, f"ops/ directory not found at {ops_dir}", 10, "ops/ directory exists")

# 2. acknowledge.json exists (10)
file_path = os.path.join(ops_dir, "acknowledge.json")
exists_file = os.path.isfile(file_path)
score += check(exists_file, f"ops/acknowledge.json not found", 10, "acknowledge.json exists")

# 3. Valid JSON (10)
if exists_file:
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        score += check(True, "Valid JSON", 10, "File is valid JSON")
    except (json.JSONDecodeError, ValueError) as e:
        score += check(False, f"Invalid JSON: {e}", 10, "File is valid JSON")
        data = None
else:
    data = None
    details.append({"item": "File is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})

# 4. Contains required fields (40 total)
if data is not None:
    # alert_id field (30)
    alert_id = data.get("alert_id")
    alert_id_correct = (alert_id == "alert-007")
    score += check(alert_id_correct, 
                   f"alert_id expected 'alert-007', got {alert_id!r}", 
                   30, "alert_id is 'alert-007'")

    # acknowledged field (10) must be boolean True
    acknowledged = data.get("acknowledged")
    ack_correct = (acknowledged is True)
    score += check(ack_correct,
                   f"acknowledged expected True, got {acknowledged!r}",
                   10, "acknowledged is true")

    # 5. No extra keys (10)
    allowed = {"alert_id", "acknowledged"}
    extra = set(data.keys()) - allowed
    no_extra = len(extra) == 0
    score += check(no_extra,
                   f"Extra fields found: {extra}",
                   10, "No extra fields in JSON")
else:
    score += check(False, "No data to check", 30, "alert_id is 'alert-007'")
    score += check(False, "No data to check", 10, "acknowledged is true")
    score += check(False, "No data to check", 10, "No extra fields in JSON")

# 6. (Bonus) Only acknowledge.json in ops directory – if extra files penalize (10)
extra_files = [f for f in os.listdir(ops_dir) if f != "acknowledge.json"] if os.path.isdir(ops_dir) else []
if extra_files:
    score += check(False, f"Extra files in ops/: {extra_files}", 10, "ops/ contains only acknowledge.json")
else:
    score += check(True, "ops/ contains only acknowledge.json", 10, "ops/ contains only acknowledge.json")

total_score = min(100, int(score))

result = {
    "total_score": total_score,
    "details": details
}

with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"Score: {total_score}/100")
