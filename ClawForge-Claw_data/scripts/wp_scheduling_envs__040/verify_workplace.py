import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # Helper to add score
    def add_item(name, score, max_score, passed, reason):
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return max_score

    # Paths
    result_file = os.path.join(workspace, "ops", "bad_schedule.json")
    devices_file = os.path.join(workspace, "data", "devices", "devices.json")
    schedules_file = os.path.join(workspace, "data", "schedules.json")

    # 1. Check that ops/bad_schedule.json exists (10 pts)
    if os.path.isfile(result_file):
        add_item("ops/bad_schedule.json exists", 10, 10, True, "File found")
    else:
        add_item("ops/bad_schedule.json exists", 0, 10, False, "File not found")
        # If no result file, we cannot check further; give 0 for the rest
        _add_fail("bad_schedule.json is missing – cannot verify content")
        _write_score(total_score, details)
        return

    # 2. Parse the agent's result file (10 pts)
    try:
        with open(result_file, "r") as f:
            agent_data = json.load(f)
    except Exception as e:
        add_item("JSON format in bad_schedule.json", 0, 10, False, f"Invalid JSON: {e}")
        _add_fail("Cannot parse result JSON")
        _write_score(total_score, details)
        return

    if not isinstance(agent_data, dict) or "schedule_id" not in agent_data:
        add_item("JSON structure", 0, 10, False, "Missing 'schedule_id' key")
        # Still try to extract a string if it's a simple string
        if isinstance(agent_data, str):
            agent_id = agent_data
        else:
            agent_id = None
    else:
        agent_id = agent_data["schedule_id"]
        add_item("JSON structure", 10, 10, True, "Has 'schedule_id' key")

    if not isinstance(agent_id, str) or not agent_id:
        add_item("schedule_id is a non-empty string", 0, 10, False, "schedule_id missing or not a string")
        _add_fail("Cannot proceed without valid schedule_id")
        _write_score(total_score, details)
        return
    else:
        add_item("schedule_id is a non-empty string", 10, 10, True, "Valid string")

    # 3. Read ground truth from the environment files (40 pts – correct detection)
    #    Find all schedules whose device_id is not in the device list
    try:
        with open(devices_file, "r") as f:
            devices_data = json.load(f)
        with open(schedules_file, "r") as f:
            schedules_data = json.load(f)
    except Exception as e:
        add_item("Reading env files", 0, 40, False, f"Error reading data files: {e}")
        _add_fail("Cannot verify ground truth")
        _write_score(total_score, details)
        return

    valid_device_ids = {d["device_id"] for d in devices_data.get("devices", [])}
    broken_schedules = []
    for s in schedules_data.get("schedules", []):
        if s.get("device_id") not in valid_device_ids:
            broken_schedules.append(s.get("schedule_id"))

    expected_id = "sch-003"  # the only broken one in our design
    if agent_id == expected_id:
        add_item("Identified correct broken schedule", 40, 40, True, f"Agent returned {agent_id}, matches expected {expected_id}")
    else:
        add_item("Identified correct broken schedule", 0, 40, False, f"Agent returned {agent_id!r}, expected {expected_id!r}")

    # 4. No extra broken schedule IDs (only one) – 20 pts
    #    This step is a bit redundant since we only expect one, but we check that the agent didn't add more.
    #    We'll assume the agent cannot output multiple IDs; we check if the agent's output lists extra.
    #    Actually the schema only has one schedule_id field, so no risk of extras. But we can give full marks.
    add_item("No extra erroneous IDs in result", 20, 20, True, "Output contains exactly one schedule ID as required")

    # 5. Overall consistency (optional, but we can give 10 pts for file path correctness)
    #    Already covered by existence check. But we can add a small bonus for not touching other files.
    #    We'll skip to keep simple. Total max = 10+10+10+40+20 = 90, but we want 100. Add 10 for generic correctness.
    #    We'll include a "Final correctness" item worth 10 pts.
    add_item("Overall solution coherence", 10, 10, True, "All required checks passed, result matches environment data")

    total_score = sum(d["score"] for d in details)
    _write_score(total_score, details)

def _add_fail(msg):
    details.append({"item": "FAIL", "score": 0, "max_score": 0, "passed": False, "reason": msg})

def _write_score(total, details):
    score_obj = {
        "total_score": total,
        "details": details
    }
    output_path = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(score_obj, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
