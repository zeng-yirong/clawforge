"""
Verify that the agent generated the correct emergency call instruction.
Checks:
  1. ops/emergency_call.json exists and is valid JSON.
  2. Contains required fields: zone, contact_name, phone.
  3. Values match the expected: zone="Garage", contact_name="Emergency Services", phone="911".
"""
import sys
import json
import os
from pathlib import Path

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score = {
    "total_score": 0,
    "details": []
}

def add_detail(item, score_val, max_score, passed, reason):
    score["details"].append({
        "item": item,
        "score": score_val,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# 1. Check ops directory exists (10 points)
ops_dir = Path(workspace) / "ops"
if ops_dir.is_dir():
    add_detail("ops directory exists", 10, 10, True, "Found ops/ directory")
else:
    add_detail("ops directory exists", 0, 10, False, "Missing ops/ directory")
    # If no directory, further checks are meaningless
    score["total_score"] = sum(d["score"] for d in score["details"])
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(score, f, indent=2)
    sys.exit(0)

# 2. Check emergency_call.json exists (10 points)
target = ops_dir / "emergency_call.json"
if target.is_file():
    add_detail("emergency_call.json exists", 10, 10, True, "File found")
else:
    add_detail("emergency_call.json exists", 0, 10, False, "File not found")
    # can't proceed
    score["total_score"] = sum(d["score"] for d in score["details"])
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(score, f, indent=2)
    sys.exit(0)

# 3. Check JSON validity (10 points)
try:
    with open(target, "r") as f:
        data = json.load(f)
    add_detail("JSON is valid", 10, 10, True, "Parsed successfully")
except (json.JSONDecodeError, Exception) as e:
    add_detail("JSON is valid", 0, 10, False, f"Invalid JSON: {e}")
    score["total_score"] = sum(d["score"] for d in score["details"])
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(score, f, indent=2)
    sys.exit(0)

# 4. Check required fields (20 points)
required_fields = ["zone", "contact_name", "phone"]
missing_fields = [f for f in required_fields if f not in data]
if not missing_fields:
    add_detail("Required fields present", 20, 20, True, "All required fields found")
else:
    add_detail("Required fields present", 0, 20, False, f"Missing fields: {missing_fields}")

# 5. Check zone value (20 points)
zone_expected = "Garage"
if "zone" in data and data["zone"] == zone_expected:
    add_detail("zone value correct", 20, 20, True, f"zone = '{data['zone']}'")
else:
    actual = data.get("zone", "MISSING")
    add_detail("zone value correct", 0, 20, False, f"Expected '{zone_expected}', got '{actual}'")

# 6. Check contact_name value (15 points)
name_expected = "Emergency Services"
if "contact_name" in data and data["contact_name"] == name_expected:
    add_detail("contact_name value correct", 15, 15, True, f"contact_name = '{data['contact_name']}'")
else:
    actual = data.get("contact_name", "MISSING")
    add_detail("contact_name value correct", 0, 15, False, f"Expected '{name_expected}', got '{actual}'")

# 7. Check phone value (15 points)
phone_expected = "911"
if "phone" in data and data["phone"] == phone_expected:
    add_detail("phone value correct", 15, 15, True, f"phone = '{data['phone']}'")
else:
    actual = data.get("phone", "MISSING")
    add_detail("phone value correct", 0, 15, False, f"Expected '{phone_expected}', got '{actual}'")

# Calculate total
score["total_score"] = sum(d["score"] for d in score["details"])

# Write score file
with open(Path(workspace) / "workplace_score.json", "w") as f:
    json.dump(score, f, indent=2)
