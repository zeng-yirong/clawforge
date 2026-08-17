import sys
import os
import json

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_ground_truth(workspace):
    """Given the workspace, compute the expected answer from the environment files."""
    # find the email that has both "approved" and "final" labels
    emails_dir = os.path.join(workspace, "data", "emails")
    target_email = None
    for fname in os.listdir(emails_dir):
        if not fname.endswith(".json"):
            continue
        em = load_json(os.path.join(emails_dir, fname))
        labels = em.get("labels", [])
        if "approved" in labels and "final" in labels:
            # take the latest (max timestamp) – in case multiple, pick the greatest
            if target_email is None or em["timestamp"] > target_email["timestamp"]:
                target_email = em
    if target_email is None:
        return None

    # get attachment id
    atts = target_email.get("attachments", [])
    if not atts:
        return None
    att_id = atts[0]["attachment_id"]  # assume first attachment
    att_path = os.path.join(workspace, "data", "attachments", f"{att_id}.txt")
    if not os.path.exists(att_path):
        return None

    # parse attachment content
    with open(att_path, "r") as f:
        lines = f.readlines()
    mission = None
    launch_date = None
    for line in lines:
        line = line.strip()
        if line.startswith("Mission Name:"):
            mission = line.split(":", 1)[1].strip()
        elif line.startswith("Launch Date:"):
            launch_date = line.split(":", 1)[1].strip()
    return {"mission_name": mission, "launch_date": launch_date}

def check_file_exists(path):
    return os.path.isfile(path)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # ------------------------------------------------------------------
    # 1. Check ops directory exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ missing"})
        # if ops missing, no point checking file – skip rest
        write_score(details, score)
        return

    # ------------------------------------------------------------------
    # 2. Check launch_schedule.json exists and is valid JSON (15 points)
    target_file = os.path.join(workspace, "ops", "launch_schedule.json")
    if not check_file_exists(target_file):
        details.append({"item": "ops/launch_schedule.json exists", "score": 0, "max_score": 15, "passed": False, "reason": "file not found"})
        write_score(details, score)
        return
    try:
        agent_data = load_json(target_file)
        details.append({"item": "ops/launch_schedule.json exists", "score": 15, "max_score": 15, "passed": True, "reason": "valid JSON file present"})
        score += 15
    except Exception as e:
        details.append({"item": "ops/launch_schedule.json exists", "score": 0, "max_score": 15, "passed": False, "reason": f"invalid JSON: {str(e)}"})
        write_score(details, score)
        return

    # ------------------------------------------------------------------
    # 3. Compute ground truth (if we cannot, error but still give partial)
    truth = extract_ground_truth(workspace)
    if truth is None:
        details.append({"item": "ground truth computable", "score": 0, "max_score": 0, "passed": False, "reason": "Could not compute expected answer from workspace – possible env corruption"})
        # we can still check structure but not values
        # proceed with partial checks
        pass

    # ------------------------------------------------------------------
    # 4. Check mission_name field (30 points)
    mission = agent_data.get("mission_name")
    expected_mission = truth["mission_name"] if truth else "Aurora-7"
    if mission == expected_mission:
        details.append({"item": "mission_name correct", "score": 30, "max_score": 30, "passed": True, "reason": f"mission_name is '{mission}'"})
        score += 30
    else:
        details.append({"item": "mission_name correct", "score": 0, "max_score": 30, "passed": False, "reason": f"expected '{expected_mission}', got '{mission}'"})

    # ------------------------------------------------------------------
    # 5. Check launch_date field (30 points)
    launch_date = agent_data.get("launch_date")
    expected_date = truth["launch_date"] if truth else "2025-08-15"
    if launch_date == expected_date:
        details.append({"item": "launch_date correct", "score": 30, "max_score": 30, "passed": True, "reason": f"launch_date is '{launch_date}'"})
        score += 30
    else:
        details.append({"item": "launch_date correct", "score": 0, "max_score": 30, "passed": False, "reason": f"expected '{expected_date}', got '{launch_date}'"})

    # ------------------------------------------------------------------
    # 6. No extra unexpected fields (15 points)
    expected_keys = {"mission_name", "launch_date"}
    actual_keys = set(agent_data.keys())
    extra = actual_keys - expected_keys
    if not extra:
        details.append({"item": "no extra fields", "score": 15, "max_score": 15, "passed": True, "reason": "only required fields present"})
        score += 15
    else:
        details.append({"item": "no extra fields", "score": 0, "max_score": 15, "passed": False, "reason": f"unexpected fields: {extra}"})

    write_score(details, score)

def write_score(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
