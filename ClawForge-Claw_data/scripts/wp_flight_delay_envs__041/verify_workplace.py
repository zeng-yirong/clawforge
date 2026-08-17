import sys
import os
import json
from datetime import datetime, timedelta

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. Check ops directory exists (5 pts)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        total_score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ not found"})

    # 2. Check delay_notifications.json exists (10 pts)
    notif_path = os.path.join(ops_dir, "delay_notifications.json")
    if os.path.isfile(notif_path):
        details.append({"item": "delay_notifications.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file present"})
        total_score += 10
    else:
        details.append({"item": "delay_notifications.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        print(json.dumps({"total_score": total_score, "details": details}))
        # Early exit? No, continue to report all checks
        # But we'll skip further checks that depend on file
        # For simplicity, write score and return
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. Validate JSON format (10 pts)
    try:
        data = load_json(notif_path)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parse succeeded"})
        total_score += 10
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. Check that data is a list (5 pts)
    if isinstance(data, list):
        details.append({"item": "notification list", "score": 5, "max_score": 5, "passed": True, "reason": "top-level list"})
        total_score += 5
    else:
        details.append({"item": "notification list", "score": 0, "max_score": 5, "passed": False, "reason": f"expected list, got {type(data).__name__}"})
        # but still continue

    if not isinstance(data, list):
        # can't proceed
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 5. Each entry must have recipient_email, subject, message (15 pts)
    required_fields = {"recipient_email", "subject", "message"}
    field_ok = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_ok = False
            break
        missing = required_fields - set(entry.keys())
        if missing:
            field_ok = False
            break
    if field_ok:
        details.append({"item": "notification fields", "score": 15, "max_score": 15, "passed": True, "reason": "all entries have required fields"})
        total_score += 15
    else:
        details.append({"item": "notification fields", "score": 0, "max_score": 15, "passed": False, "reason": "missing or invalid fields"})

    # 6. Correct recipient email (10 pts)
    emails = [e.get("recipient_email") for e in data]
    if "john.smith@example.com" in emails:
        details.append({"item": "recipient email", "score": 10, "max_score": 10, "passed": True, "reason": "John Smith email present"})
        total_score += 10
    else:
        details.append({"item": "recipient email", "score": 0, "max_score": 10, "passed": False, "reason": "john.smith@example.com not found"})

    # 7. Correct subject (10 pts) - must contain "Flight Delay" or "Delay Notification"
    subject_ok = False
    for e in data:
        subj = e.get("subject", "")
        if "delay" in subj.lower():
            subject_ok = True
            break
    if subject_ok:
        details.append({"item": "subject contains 'delay'", "score": 10, "max_score": 10, "passed": True, "reason": "found delay-related subject"})
        total_score += 10
    else:
        details.append({"item": "subject contains 'delay'", "score": 0, "max_score": 10, "passed": False, "reason": "no delay keyword in subject"})

    # 8. Core timing correctness (35 pts)
    # Load original transport booking to get base pickup time
    # Expected new pickup = base pickup + delay_minutes
    tb_path = os.path.join(workspace, "transport_bookings.json")
    fl_path = os.path.join(workspace, "flights", "flights.json")
    timing_ok = False
    timing_reason = ""
    try:
        tb_data = load_json(tb_path)
        fl_data = load_json(fl_path)
        # Find the booking for UA123 flight
        target_booking = None
        for b in tb_data.get("transport_bookings", []):
            if b.get("flight_id") == "F001" and b.get("status") == "confirmed":
                target_booking = b
                break
        if not target_booking:
            timing_reason = "no confirmed transport booking for flight F001 found"
        else:
            original_pickup_str = target_booking["pickup_time"]
            original_pickup = datetime.strptime(original_pickup_str, "%Y-%m-%d %H:%M")
            # Get delay from flight
            delay_minutes = None
            for f in fl_data.get("flights", []):
                if f["flight_id"] == "F001":
                    delay_minutes = f["delay_minutes"]
                    break
            if delay_minutes is None:
                timing_reason = "delay minutes not found for flight F001"
            else:
                expected_pickup = original_pickup + timedelta(minutes=delay_minutes)
                expected_time_str = expected_pickup.strftime("%H:%M")
                # Check if any message mentions the expected time
                for e in data:
                    msg = e.get("message", "")
                    if expected_time_str in msg:
                        timing_ok = True
                        break
                if not timing_ok:
                    timing_reason = f"expected time {expected_time_str} not found in any message"
    except Exception as ex:
        timing_reason = f"error reading base data: {ex}"

    if timing_ok:
        details.append({"item": "correct new pickup time in message", "score": 35, "max_score": 35, "passed": True, "reason": "correct time derived"})
        total_score += 35
    else:
        details.append({"item": "correct new pickup time in message", "score": 0, "max_score": 35, "passed": False, "reason": timing_reason})

    # 9. No stale/cancelled bookings referenced (optional strict check: no extra unrelated recipients) (5 pts)
    # We'll check that only john.smith@example.com appears (or at least no other contacts from distractor)
    extra_ok = True
    for e in data:
        if e.get("recipient_email") not in ["john.smith@example.com"]:
            extra_ok = False
            break
    if extra_ok:
        details.append({"item": "no extra recipients", "score": 5, "max_score": 5, "passed": True, "reason": "only John Smith"})
        total_score += 5
    else:
        details.append({"item": "no extra recipients", "score": 0, "max_score": 5, "passed": False, "reason": "unexpected recipient found"})

    # Write final score
    total_score = min(total_score, 100)  # cap
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
