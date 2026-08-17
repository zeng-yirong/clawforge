import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    results = []
    total_score = 0

    # --- 1. ops directory exists (5 points) ---
    ops_exists = os.path.isdir("ops")
    results.append({
        "item": "ops directory exists",
        "score": 5 if ops_exists else 0,
        "max_score": 5,
        "passed": ops_exists,
        "reason": "ops folder found" if ops_exists else "ops folder missing"
    })
    total_score += 5 if ops_exists else 0

    if not ops_exists:
        # Can't proceed; write and exit
        final = {"total_score": total_score, "details": results}
        with open("workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # --- 2. adjustments.json exists and valid JSON (10) ---
    adj_path = "ops/adjustments.json"
    adj_valid = False
    adj_data = None
    if os.path.isfile(adj_path):
        try:
            with open(adj_path) as f:
                adj_data = json.load(f)
            adj_valid = True
        except (json.JSONDecodeError, Exception):
            adj_valid = False
    results.append({
        "item": "adjustments.json valid JSON",
        "score": 10 if adj_valid else 0,
        "max_score": 10,
        "passed": adj_valid,
        "reason": "File exists and parses" if adj_valid else "Missing or invalid JSON"
    })
    total_score += 10 if adj_valid else 0

    # --- 3. adjustments has required keys (10) ---
    has_keys = False
    if adj_valid and isinstance(adj_data, dict):
        has_keys = "adjusted_hotel_bookings" in adj_data and "adjusted_transport_bookings" in adj_data
    results.append({
        "item": "adjustments.json contains required keys",
        "score": 10 if has_keys else 0,
        "max_score": 10,
        "passed": has_keys,
        "reason": "Keys found" if has_keys else "Missing one or both keys"
    })
    total_score += 10 if has_keys else 0

    # --- 4. Hotel booking adjustment correctness (20) ---
    hotel_ok = False
    hotel_reason = ""
    if adj_valid and has_keys:
        hotel_list = adj_data.get("adjusted_hotel_bookings", [])
        if hotel_list:
            entry = hotel_list[0]
            if (entry.get("booking_id") == "hb_001" and
                entry.get("new_check_in") == "2025-06-16" and
                entry.get("new_check_out") == "2025-06-17"):
                hotel_ok = True
                hotel_reason = "Correct hotel adjustment"
            else:
                hotel_reason = f"Unexpected values: {entry}"
        else:
            hotel_reason = "Hotel adjustments list empty"
    else:
        hotel_reason = "Previous checks failed"
    results.append({
        "item": "Hotel booking adjustment",
        "score": 20 if hotel_ok else 0,
        "max_score": 20,
        "passed": hotel_ok,
        "reason": hotel_reason
    })
    total_score += 20 if hotel_ok else 0

    # --- 5. Transport booking adjustment correctness (20) ---
    transport_ok = False
    transport_reason = ""
    if adj_valid and has_keys:
        trans_list = adj_data.get("adjusted_transport_bookings", [])
        if trans_list:
            entry = trans_list[0]
            if (entry.get("booking_id") == "tb_001" and
                entry.get("new_pickup_time") == "2025-06-15T12:00"):
                transport_ok = True
                transport_reason = "Correct transport adjustment"
            else:
                transport_reason = f"Unexpected values: {entry}"
        else:
            transport_reason = "Transport adjustments list empty"
    else:
        transport_reason = "Previous checks failed"
    results.append({
        "item": "Transport booking adjustment",
        "score": 20 if transport_ok else 0,
        "max_score": 20,
        "passed": transport_ok,
        "reason": transport_reason
    })
    total_score += 20 if transport_ok else 0

    # --- 6. notifications.json exists and valid JSON (10) ---
    notif_path = "ops/notifications.json"
    notif_valid = False
    notif_data = None
    if os.path.isfile(notif_path):
        try:
            with open(notif_path) as f:
                notif_data = json.load(f)
            notif_valid = True
        except (json.JSONDecodeError, Exception):
            notif_valid = False
    results.append({
        "item": "notifications.json valid JSON",
        "score": 10 if notif_valid else 0,
        "max_score": 10,
        "passed": notif_valid,
        "reason": "File exists and parses" if notif_valid else "Missing or invalid JSON"
    })
    total_score += 10 if notif_valid else 0

    # --- 7. notifications has notifications key and non-empty list (5) ---
    notif_has = False
    if notif_valid and isinstance(notif_data, dict):
        notif_list = notif_data.get("notifications", [])
        if isinstance(notif_list, list) and len(notif_list) > 0:
            notif_has = True
    results.append({
        "item": "notifications list present and non-empty",
        "score": 5 if notif_has else 0,
        "max_score": 5,
        "passed": notif_has,
        "reason": "Found" if notif_has else "Missing or empty notifications list"
    })
    total_score += 5 if notif_has else 0

    # --- 8. First notification 'to' field correct (10) ---
    to_ok = False
    to_reason = ""
    if notif_has:
        first = notif_data["notifications"][0]
        if first.get("to") == "jane.doe@example.com":
            to_ok = True
            to_reason = "Correct recipient"
        else:
            to_reason = f"Expected jane.doe@example.com, got {first.get('to')}"
    else:
        to_reason = "No notification to check"
    results.append({
        "item": "Notification recipient email",
        "score": 10 if to_ok else 0,
        "max_score": 10,
        "passed": to_ok,
        "reason": to_reason
    })
    total_score += 10 if to_ok else 0

    # --- 9. Subject contains 'UA123' (5) ---
    sub_ok = False
    sub_reason = ""
    if notif_has:
        first = notif_data["notifications"][0]
        sub = first.get("subject", "")
        if "UA123" in sub:
            sub_ok = True
            sub_reason = "Subject contains UA123"
        else:
            sub_reason = f"Subject missing UA123: '{sub}'"
    else:
        sub_reason = "No notification to check"
    results.append({
        "item": "Subject includes flight number",
        "score": 5 if sub_ok else 0,
        "max_score": 5,
        "passed": sub_ok,
        "reason": sub_reason
    })
    total_score += 5 if sub_ok else 0

    # --- 10. Body contains key data points (5) ---
    body_ok = False
    body_reason = ""
    if notif_has:
        first = notif_data["notifications"][0]
        body = first.get("body", "")
        required = ["120", "minutes", "2025-06-16", "12:00", "Westin"]
        missing = [k for k in required if k not in body]
        if not missing:
            body_ok = True
            body_reason = "All required fragments present"
        else:
            body_reason = f"Missing fragments: {missing}"
    else:
        body_reason = "No notification to check"
    results.append({
        "item": "Body includes delay details and adjusted values",
        "score": 5 if body_ok else 0,
        "max_score": 5,
        "passed": body_ok,
        "reason": body_reason
    })
    total_score += 5 if body_ok else 0

    # --- Write score file ---
    final = {"total_score": total_score, "details": results}
    with open("workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
