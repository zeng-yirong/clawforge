import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(workspace, rel_path)
    with open(full) as f:
        return json.load(f)

# ------------------------------------------------------------
# Compute expected conflicts from the environment data
# ------------------------------------------------------------
devices_data = load_json("data/devices/devices.json")
devices = devices_data["devices"]
health_data = load_json("data/health/health.json")
users = health_data["users"]

user_by_id = {u["user_id"]: u for u in users}
device_by_location = {}
for d in devices:
    loc = d.get("location")
    device_by_location.setdefault(loc, []).append(d)

expected_conflicts = []
for uid, user in user_by_id.items():
    room = user.get("room")
    if not room:
        continue
    room_devices = device_by_location.get(room, [])
    for d in room_devices:
        dtype = d["type"]
        settings = d.get("default_settings", {})
        if dtype == "air_conditioner":
            target = settings.get("target_temperature")
            if target is not None:
                pref = user["temperature_preference"]
                if not (pref["min_temp"] <= target <= pref["max_temp"]):
                    expected_conflicts.append({
                        "device_id": d["device_id"],
                        "user_id": uid,
                        "issue": f"Temperature target {target}°C outside preferred range ({pref['min_temp']}-{pref['max_temp']})"
                    })
        elif dtype == "humidifier":
            target = settings.get("target_humidity")
            if target is not None:
                pref = user["humidity_preference"]
                if not (pref["min_humidity"] <= target <= pref["max_humidity"]):
                    expected_conflicts.append({
                        "device_id": d["device_id"],
                        "user_id": uid,
                        "issue": f"Humidity target {target}% outside preferred range ({pref['min_humidity']}-{pref['max_humidity']})"
                    })

# ------------------------------------------------------------
# Score the agent output
# ------------------------------------------------------------
output_path = os.path.join(workspace, "ops", "health_conflicts.json")
details = []
total_score = 0

# 1) ops directory exists (10 pts)
if os.path.isdir(os.path.join(workspace, "ops")):
    details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops directory found"})
    total_score += 10
else:
    details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops directory not found"})

# 2) output file exists (10 pts)
if os.path.isfile(output_path):
    details.append({"item": "output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "health_conflicts.json exists"})
    total_score += 10
else:
    details.append({"item": "output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
    # Cannot continue scoring
    final = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    sys.exit(0)

# 3) JSON parseable and is a list (10 pts)
try:
    with open(output_path) as f:
        agent_data = json.load(f)
    if not isinstance(agent_data, list):
        details.append({"item": "output JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": "JSON root is not a list"})
    else:
        details.append({"item": "output JSON is a list", "score": 10, "max_score": 10, "passed": True, "reason": "valid list"})
        total_score += 10
except Exception as e:
    details.append({"item": "output JSON parseable", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
    final = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    sys.exit(0)

# 4) Conflict count (20 pts)
expected_len = len(expected_conflicts)
actual_len = len(agent_data)
if actual_len == expected_len:
    details.append({"item": "conflict count", "score": 20, "max_score": 20, "passed": True, "reason": f"expected {expected_len}, found {actual_len}"})
    total_score += 20
else:
    details.append({"item": "conflict count", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_len}, found {actual_len}"})

# 5) Each record has required fields (10 pts)
field_ok = True
for i, rec in enumerate(agent_data):
    if not isinstance(rec, dict):
        field_ok = False
        break
    if "device_id" not in rec or "user_id" not in rec or "issue" not in rec:
        field_ok = False
        break
if field_ok:
    details.append({"item": "record fields valid", "score": 10, "max_score": 10, "passed": True, "reason": "all records have device_id, user_id, issue"})
    total_score += 10
else:
    details.append({"item": "record fields valid", "score": 0, "max_score": 10, "passed": False, "reason": "some records missing required fields"})

# 6) Conflict content correctness (40 pts)
expected_pairs = {(e["device_id"], e["user_id"]) for e in expected_conflicts}
actual_pairs = {(r.get("device_id"), r.get("user_id")) for r in agent_data if isinstance(r, dict)}
matched = len(expected_pairs & actual_pairs)
extra = actual_pairs - expected_pairs
if matched == expected_len and len(extra) == 0:
    details.append({"item": "conflict content correctness", "score": 40, "max_score": 40, "passed": True, "reason": "all expected conflicts found, no extra"})
    total_score += 40
else:
    # proportional score, subtract 10 if extra exist
    proportion = 40 * matched / expected_len if expected_len > 0 else 0
    score = int(proportion)
    if len(extra) > 0:
        score = max(0, score - 10)
    details.append({"item": "conflict content correctness", "score": score, "max_score": 40, "passed": (score == 40), "reason": f"matched {matched}/{expected_len}, extra {len(extra)}"})
    total_score += score

# ------------------------------------------------------------
# Write final score
# ------------------------------------------------------------
final = {"total_score": total_score, "details": details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(final, f, indent=2)
