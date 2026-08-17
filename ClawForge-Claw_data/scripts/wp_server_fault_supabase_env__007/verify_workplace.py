import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score = 0
details = []

def check_path(path, exist=True):
    full = os.path.join(workspace, path)
    exists = os.path.exists(full)
    return exists, full

# 1. Directory structure (10 points)
dirs_ok = True
for d in ["db_dumps", "data", "ops"]:
    ok, _ = check_path(d)
    if not ok:
        dirs_ok = False
        break
if dirs_ok:
    score += 10
    details.append({"item": "Directory structure (db_dumps, data, ops)", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories exist."})
else:
    details.append({"item": "Directory structure (db_dumps, data, ops)", "score": 0, "max_score": 10, "passed": False, "reason": "Missing one or more directories."})

# 2. Source files existence and validity (10 points)
src_ok = True
src_reason = []
# lock_analysis.txt
ok, path_lock = check_path("db_dumps/lock_analysis.txt")
if not ok:
    src_ok = False
    src_reason.append("lock_analysis.txt missing")
else:
    try:
        with open(path_lock, "r") as f:
            content = f.read()
        if "TX-20250321-001" not in content:
            src_ok = False
            src_reason.append("lock_analysis.txt does not contain expected TX ID")
    except Exception as e:
        src_ok = False
        src_reason.append(f"lock_analysis.txt read error: {e}")

# incidents_pool.json
ok, path_inc = check_path("data/incidents_pool.json")
if not ok:
    src_ok = False
    src_reason.append("incidents_pool.json missing")
else:
    try:
        with open(path_inc, "r") as f:
            data = json.load(f)
        if "incidents" not in data or not isinstance(data["incidents"], list):
            src_ok = False
            src_reason.append("incidents_pool.json invalid structure")
    except Exception as e:
        src_ok = False
        src_reason.append(f"incidents_pool.json parse error: {e}")

if src_ok:
    score += 10
    details.append({"item": "Source files valid and contain expected data", "score": 10, "max_score": 10, "passed": True, "reason": "Both source files exist and are valid."})
else:
    details.append({"item": "Source files valid and contain expected data", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(src_reason)})

# 3. Output file exists and is valid JSON (10 points)
out_ok = True
out_reason = []
ok, path_out = check_path("ops/resolve_target.json")
if not ok:
    out_ok = False
    out_reason.append("ops/resolve_target.json missing")
else:
    try:
        with open(path_out, "r") as f:
            result = json.load(f)
        if not isinstance(result, dict):
            out_ok = False
            out_reason.append("Result is not a JSON object")
        elif "incident_id" not in result:
            out_ok = False
            out_reason.append("Missing 'incident_id' field")
    except Exception as e:
        out_ok = False
        out_reason.append(f"JSON parse error: {e}")

if out_ok:
    score += 10
    details.append({"item": "Output file ops/resolve_target.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Output file valid."})
else:
    details.append({"item": "Output file ops/resolve_target.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(out_reason)})

# 4. Correct incident_id extraction (70 points)
if out_ok:
    target_id = result["incident_id"]
    if target_id == "inc-003":
        score += 70
        details.append({"item": "Correct incident_id (inc-003) extracted", "score": 70, "max_score": 70, "passed": True, "reason": "Agent correctly identified the matching incident."})
    else:
        details.append({"item": "Correct incident_id (inc-003) extracted", "score": 0, "max_score": 70, "passed": False, "reason": f"Got '{target_id}', expected 'inc-003'."})
else:
    details.append({"item": "Correct incident_id extraction", "score": 0, "max_score": 70, "passed": False, "reason": "Output file invalid, cannot check value."})

total_score = min(score, 100)  # ensure 100 cap
result = {
    "total_score": total_score,
    "details": details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
