import json
import os
import sys

def verify(workspace: str):
    """Verify agent outputs for flight delay cascade task.
    Scores are based on presence, validity, and correctness of three output files.
    Total = 100.
    """
    results = []
    total = 0

    ops_dir = os.path.join(workspace, "ops")
    # 1. ops directory existence (10 points)
    if os.path.isdir(ops_dir):
        total += 10
        results.append({"item": "ops/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
    else:
        results.append({"item": "ops/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})
        # early exit? We'll continue but files will fail
        # Still need to write score file, so skip remaining checks
        final_score = total
        _write_score(final_score, results)
        return final_score

    # ---- ota_adjustment.json (max 30) ----
    ota_path = os.path.join(ops_dir, "ota_adjustment.json")
    ota_valid = False
    if os.path.isfile(ota_path):
        try:
            with open(ota_path, "r") as f:
                ota_data = json.load(f)
            ota_valid = True
        except (json.JSONDecodeError, Exception):
            pass

    if ota_valid:
        results.append({"item": "ota_adjustment.json is valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "parse OK"})
        total += 5
        # check hotel_id "H001" (5)
        if isinstance(ota_data, list) and any(isinstance(o, dict) and o.get("hotel_id") == "H001" for o in ota_data):
            results.append({"item": "ota_adjustment.json contains H001", "score": 5, "max_score": 5, "passed": True, "reason": "hotel_id H001 found"})
            total += 5
            # check check_in_date "2025-03-16" (15)
            target_hotel = next(o for o in ota_data if o.get("hotel_id") == "H001")
            if target_hotel.get("check_in_date") == "2025-03-16":
                results.append({"item": "check_in_date correctly adjusted to 2025-03-16", "score": 15, "max_score": 15, "passed": True, "reason": "date updated"})
                total += 15
            else:
                results.append({"item": "check_in_date correctly adjusted to 2025-03-16", "score": 0, "max_score": 15, "passed": False, "reason": f"got {target_hotel.get('check_in_date')}"})
            # check hotel_name remains "Hilton Manhattan" (5) as proof of completeness
            if target_hotel.get("hotel_name") == "Hilton Manhattan":
                results.append({"item": "hotel_name unchanged (Hilton Manhattan)", "score": 5, "max_score": 5, "passed": True, "reason": "name correct"})
                total += 5
            else:
                results.append({"item": "hotel_name unchanged (Hilton Manhattan)", "score": 0, "max_score": 5, "passed": False, "reason": f"got {target_hotel.get('hotel_name')}"})
        else:
            results.append({"item": "ota_adjustment.json contains H001", "score": 0, "max_score": 5, "passed": False, "reason": "hotel_id H001 not found"})
            results.append({"item": "check_in_date correctly adjusted to 2025-03-16", "score": 0, "max_score": 15, "passed": False, "reason": "skipped"})
            results.append({"item": "hotel_name unchanged (Hilton Manhattan)", "score": 0, "max_score": 5, "passed": False, "reason": "skipped"})
    else:
        results.append({"item": "ota_adjustment.json is valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": "file missing or invalid"})
        results.append({"item": "ota_adjustment.json contains H001", "score": 0, "max_score": 5, "passed": False, "reason": "skipped"})
        results.append({"item": "check_in_date correctly adjusted to 2025-03-16", "score": 0, "max_score": 15, "passed": False, "reason": "skipped"})
        results.append({"item": "hotel_name unchanged (Hilton Manhattan)", "score": 0, "max_score": 5, "passed": False, "reason": "skipped"})

    # ---- trans_reschedule.json (max 30) ----
    trans_path = os.path.join(ops_dir, "trans_reschedule.json")
    trans_valid = False
    if os.path.isfile(trans_path):
        try:
            with open(trans_path, "r") as f:
                trans_data = json.load(f)
            trans_valid = True
        except (json.JSONDecodeError, Exception):
            pass

    if trans_valid:
        results.append({"item": "trans_reschedule.json is valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "parse OK"})
        total += 5
        if isinstance(trans_data, list) and any(isinstance(o, dict) and o.get("transport_id") == "T001" for o in trans_data):
            results.append({"item": "trans_reschedule.json contains T001", "score": 5, "max_score": 5, "passed": True, "reason": "transport_id T001 found"})
            total += 5
            target_transport = next(o for o in trans_data if o.get("transport_id") == "T001")
            expected_pickup = "2025-03-15T22:30"
            if target_transport.get("pickup_time") == expected_pickup:
                results.append({"item": "pickup_time correctly adjusted to 2025-03-15T22:30", "score": 15, "max_score": 15, "passed": True, "reason": "time updated"})
                total += 15
            else:
                results.append({"item": "pickup_time correctly adjusted to 2025-03-15T22:30", "score": 0, "max_score": 15, "passed": False, "reason": f"got {target_transport.get('pickup_time')}"})
            # check service_provider remains "SuperShuttle" (5)
            if target_transport.get("service_provider") == "SuperShuttle":
                results.append({"item": "service_provider unchanged (SuperShuttle)", "score": 5, "max_score": 5, "passed": True, "reason": "provider correct"})
                total += 5
            else:
                results.append({"item": "service_provider unchanged (SuperShuttle)", "score": 0, "max_score": 5, "passed": False, "reason": f"got {target_transport.get('service_provider')}"})
        else:
            results.append({"item": "trans_reschedule.json contains T001", "score": 0, "max_score": 5, "passed": False, "reason": "transport_id T001 not found"})
            results.append({"item": "pickup_time correctly adjusted to 2025-03-15T22:30", "score": 0, "max_score": 15, "passed": False, "reason": "skipped"})
            results.append({"item": "service_provider unchanged (SuperShuttle)", "score": 0, "max_score": 5, "passed": False, "reason": "skipped"})
    else:
        results.append({"item": "trans_reschedule.json is valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": "file missing or invalid"})
        results.append({"item": "trans_reschedule.json contains T001", "score": 0, "max_score": 5, "passed": False, "reason": "skipped"})
        results.append({"item": "pickup_time correctly adjusted to 2025-03-15T22:30", "score": 0, "max_score": 15, "passed": False, "reason": "skipped"})
        results.append({"item": "service_provider unchanged (SuperShuttle)", "score": 0, "max_score": 5, "passed": False, "reason": "skipped"})

    # ---- notifications.json (max 30) ----
    notif_path = os.path.join(ops_dir, "notifications.json")
    notif_valid = False
    if os.path.isfile(notif_path):
        try:
            with open(notif_path, "r") as f:
                notif_data = json.load(f)
            notif_valid = True
        except (json.JSONDecodeError, Exception):
            pass

    if notif_valid:
        results.append({"item": "notifications.json is valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "parse OK"})
        total += 5
        if isinstance(notif_data, list) and "john.smith@example.com" in notif_data:
            results.append({"item": "notifications.json contains john.smith@example.com", "score": 20, "max_score": 20, "passed": True, "reason": "email present"})
            total += 20
            # extra: ensure not too many extra emails? 5 points
            expected_emails = {"john.smith@example.com"}
            actual_emails = set(notif_data) if isinstance(notif_data, list) else set()
            if actual_emails == expected_emails:
                results.append({"item": "notifications.json contains exactly the correct set of emails", "score": 5, "max_score": 5, "passed": True, "reason": "no extra emails"})
                total += 5
            else:
                results.append({"item": "notifications.json contains exactly the correct set of emails", "score": 0, "max_score": 5, "passed": False, "reason": f"got {actual_emails}, expected {expected_emails}"})
        else:
            results.append({"item": "notifications.json contains john.smith@example.com", "score": 0, "max_score": 20, "passed": False, "reason": "email not found"})
            results.append({"item": "notifications.json contains exactly the correct set of emails", "score": 0, "max_score": 5, "passed": False, "reason": "skipped"})
    else:
        results.append({"item": "notifications.json is valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": "file missing or invalid"})
        results.append({"item": "notifications.json contains john.smith@example.com", "score": 0, "max_score": 20, "passed": False, "reason": "skipped"})
        results.append({"item": "notifications.json contains exactly the correct set of emails", "score": 0, "max_score": 5, "passed": False, "reason": "skipped"})

    # Ensure total is clamped to 100
    total = min(total, 100)
    _write_score(total, results)
    return total

def _write_score(score: int, details: list):
    output = {"total_score": score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
