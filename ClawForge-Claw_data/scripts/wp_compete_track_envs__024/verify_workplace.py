import sys
import os
import json
import csv

VALID_SOURCES = {"organic", "paid_ads", "referral", "social"}

def load_users(workspace):
    users_dir = os.path.join(workspace, "data", "users")
    if not os.path.isdir(users_dir):
        return None, "data/users/ directory not found"

    users = []
    for fname in os.listdir(users_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(users_dir, fname)
        try:
            with open(fpath, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue  # skip unparseable files
        if not isinstance(data, dict):
            continue
        # basic field checks
        if "acquisition_source" not in data or "acquisition_cost" not in data or "lifetime_value" not in data:
            continue
        source = data["acquisition_source"]
        cost = data.get("acquisition_cost", 0)
        ltv = data.get("lifetime_value", 0)
        # accept only valid sources and positive cost/ltv
        if source not in VALID_SOURCES:
            continue
        if not isinstance(cost, (int, float)) or cost <= 0:
            continue
        if not isinstance(ltv, (int, float)) or ltv < 0:
            continue
        users.append((source, cost, ltv))
    return users, None

def compute_worst_channel(users):
    from collections import defaultdict
    totals = defaultdict(lambda: {"cost": 0.0, "ltv": 0.0})
    for source, cost, ltv in users:
        totals[source]["cost"] += cost
        totals[source]["ltv"] += ltv
    roi = {}
    for source, vals in totals.items():
        if vals["cost"] > 0:
            roi[source] = vals["ltv"] / vals["cost"]
    if not roi:
        return None, None
    worst = min(roi, key=roi.get)
    return worst, roi[worst]

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []

    # 1. Check ops/ directory exists (10 pts)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({"item": "ops/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found"})
    else:
        score_details.append({"item": "ops/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing"})
        # if no ops dir, no point checking further
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f, indent=2)
        return

    # 2. Check channel_alert.json exists (10 pts)
    alert_path = os.path.join(ops_dir, "channel_alert.json")
    if os.path.isfile(alert_path):
        score_details.append({"item": "channel_alert.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found"})
    else:
        score_details.append({"item": "channel_alert.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f, indent=2)
        return

    # 3. JSON valid (10 pts)
    try:
        with open(alert_path, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Parse successful"})
    except (json.JSONDecodeError, OSError) as e:
        score_details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f, indent=2)
        return

    # 4. Contains "channel" field (10 pts)
    if "channel" in data and isinstance(data["channel"], str):
        score_details.append({"item": "channel field present and string", "score": 10, "max_score": 10, "passed": True, "reason": f"channel = {data['channel']}"})
    else:
        score_details.append({"item": "channel field present and string", "score": 0, "max_score": 10, "passed": False, "reason": "Missing or not string"})

    # 5. Contains "roi" field (10 pts)
    if "roi" in data and isinstance(data["roi"], (int, float)):
        score_details.append({"item": "roi field present and numeric", "score": 10, "max_score": 10, "passed": True, "reason": f"roi = {data['roi']}"})
    else:
        score_details.append({"item": "roi field present and numeric", "score": 0, "max_score": 10, "passed": False, "reason": "Missing or not numeric"})

    # 6. Compute expected answer from clean users (20 pts for channel, 30 pts for roi)
    users, err = load_users(workspace)
    if err:
        score_details.append({"item": "Compute worst channel (channel)", "score": 0, "max_score": 20, "passed": False, "reason": err})
        score_details.append({"item": "Compute worst channel (roi)", "score": 0, "max_score": 30, "passed": False, "reason": err})
    else:
        expected_channel, expected_roi = compute_worst_channel(users)
        if expected_channel is None:
            score_details.append({"item": "Compute worst channel (channel)", "score": 0, "max_score": 20, "passed": False, "reason": "No valid users found"})
            score_details.append({"item": "Compute worst channel (roi)", "score": 0, "max_score": 30, "passed": False, "reason": "No valid users found"})
        else:
            # Check channel name
            if data.get("channel") == expected_channel:
                score_details.append({"item": "Compute worst channel (channel)", "score": 20, "max_score": 20, "passed": True, "reason": f"Correct channel: {expected_channel}"})
            else:
                score_details.append({"item": "Compute worst channel (channel)", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_channel}, got {data.get('channel')}"})
            # Check ROI value (allow 1e-6 tolerance)
            actual_roi = data.get("roi")
            if isinstance(actual_roi, (int, float)) and abs(actual_roi - expected_roi) < 1e-6:
                score_details.append({"item": "Compute worst channel (roi)", "score": 30, "max_score": 30, "passed": True, "reason": f"ROI correct: {expected_roi}"})
            else:
                score_details.append({"item": "Compute worst channel (roi)", "score": 0, "max_score": 30, "passed": False, "reason": f"Expected {expected_roi}, got {actual_roi}"})

    total_score = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
