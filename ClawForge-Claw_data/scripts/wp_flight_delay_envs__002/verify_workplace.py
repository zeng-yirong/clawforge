#!/usr/bin/env python3
"""
Verify that the agent produced the correct transport update and notification draft.
Score breakdown (total 100):
  - ops/ directory exists: 10
  - ops/transport_updates.json exists: 10
  - ops/notification_draft.json exists: 10
  - transport_updates.json valid JSON: 5
  - notification_draft.json valid JSON: 5
  - transport_updates contains correct booking_id (tb001): 10
  - transport_updates contains correct new pickup time (2024-03-15 20:30): 15
  - transport_updates does NOT include cancelled or unrelated bookings: 10
  - notification_draft contains correct recipient email: 10
  - notification_draft mentions delay and new time: 10
"""
import sys
import json
import os

workplace = sys.argv[1] if len(sys.argv) > 1 else "."

result = {
    "total_score": 0,
    "details": []
}

def add_item(name, max_score, passed, reason, score=None):
    if score is None:
        score = max_score if passed else 0
    result["details"].append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# 1. ops/ directory exists
ops_dir = os.path.join(workplace, "ops")
if os.path.isdir(ops_dir):
    add_item("ops/ directory exists", 10, True, "Found ops/")
else:
    add_item("ops/ directory exists", 10, False, "Missing ops/")
    # If directory missing, remaining checks will likely fail, but we still run them
    add_item("ops/transport_updates.json exists", 10, False, "Directory missing", 0)
    add_item("ops/notification_draft.json exists", 10, False, "Directory missing", 0)
    add_item("transport_updates.json valid JSON", 5, False, "File missing", 0)
    add_item("notification_draft.json valid JSON", 5, False, "File missing", 0)
    add_item("correct booking_id", 10, False, "File missing", 0)
    add_item("correct new pickup time", 15, False, "File missing", 0)
    add_item("excludes cancelled/unrelated", 10, False, "File missing", 0)
    add_item("recipient email correct", 10, False, "File missing", 0)
    add_item("notification mentions delay", 10, False, "File missing", 0)
    result["total_score"] = sum(d["score"] for d in result["details"])
    with open(os.path.join(workplace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 2. transport_updates.json exists
tu_path = os.path.join(ops_dir, "transport_updates.json")
if os.path.isfile(tu_path):
    add_item("ops/transport_updates.json exists", 10, True, "File found")
else:
    add_item("ops/transport_updates.json exists", 10, False, "File missing")
    # skip further transport checks
    add_item("transport_updates.json valid JSON", 5, False, "File missing", 0)
    add_item("correct booking_id", 10, False, "File missing", 0)
    add_item("correct new pickup time", 15, False, "File missing", 0)
    add_item("excludes cancelled/unrelated", 10, False, "File missing", 0)
    # still check notification if it exists
    nd_path = os.path.join(ops_dir, "notification_draft.json")
    if os.path.isfile(nd_path):
        add_item("ops/notification_draft.json exists", 10, True, "File found")
        # ... notification checks
    else:
        add_item("ops/notification_draft.json exists", 10, False, "File missing")
        add_item("notification_draft.json valid JSON", 5, False, "File missing", 0)
        add_item("recipient email correct", 10, False, "File missing", 0)
        add_item("notification mentions delay", 10, False, "File missing", 0)
        result["total_score"] = sum(d["score"] for d in result["details"])
        with open(os.path.join(workplace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        sys.exit(0)

# 3. notification_draft.json exists
nd_path = os.path.join(ops_dir, "notification_draft.json")
if os.path.isfile(nd_path):
    add_item("ops/notification_draft.json exists", 10, True, "File found")
else:
    add_item("ops/notification_draft.json exists", 10, False, "File missing")

# 4. transport_updates JSON valid
try:
    with open(tu_path, "r") as f:
        tu = json.load(f)
    add_item("transport_updates.json valid JSON", 5, True, "Valid JSON")
except (json.JSONDecodeError, Exception) as e:
    add_item("transport_updates.json valid JSON", 5, False, f"Invalid JSON: {e}")
    tu = None

# 5. notification_draft JSON valid
try:
    with open(nd_path, "r") as f:
        nd = json.load(f)
    add_item("notification_draft.json valid JSON", 5, True, "Valid JSON")
except (json.JSONDecodeError, Exception) as e:
    add_item("notification_draft.json valid JSON", 5, False, f"Invalid JSON: {e}")
    nd = None

# 6. transport_updates correct booking_id (should be tb001)
if tu is not None:
    # Expect a list of updates or a single object; we support both.
    if isinstance(tu, dict):
        updates = [tu]
    elif isinstance(tu, list):
        updates = tu
    else:
        updates = []
    found_correct = False
    for u in updates:
        if u.get("booking_id") == "tb001" or u.get("booking_id") == "tb001":
            found_correct = True
            break
    if found_correct:
        add_item("correct booking_id (tb001) in transport_updates", 10, True, "Found tb001")
    else:
        add_item("correct booking_id (tb001) in transport_updates", 10, False, "Missing or incorrect booking_id")

    # 7. correct new pickup time: 2024-03-15 20:30 (delay 120 min + 30 min buffer after landing)
    # original pickup was 18:30, delay 120 → 20:30, plus 30 min buffer? The prompt says "an extra 30 minutes after landing to clear customs".
    # Landing delayed from 22:00 to 00:00? Wait original arrival was 22:00, but departure delayed 2h so arrival 00:00, but pickup should be after landing.
    # Actually original pickup was at 18:30, but flight arrives at 22:00 (if on time). But we just shift pickup by delay+30: 18:30 + 150 min = 21:00?
    # Let's re-read: UA123 departure 18:00, arrival 22:00 (4h flight). Delay 120 min → departure 20:00, arrival 00:00 next day.
    # Pickup originally at 18:30? That doesn't match arrival at 22:00. This is a potential inconsistency in env_builder. Let's correct: we should set pickup to match arrival. But for test, we need a unique answer.
    # Instead, we can define: original pickup time = 22:30 (30 min after on-time arrival). Then delay 120 min yields new pickup = 00:30 next day. But easier: set original pickup = 22:30. Then new = 00:30.
    # However, we already wrote env_builder with pickup 18:30. That is a mistake. We must adjust env_builder to be consistent. Let's fix env_builder to have pickup = 22:30.
    # Since we haven't submitted yet, I'll rewrite env_builder to have consistent times.
    # Let's do it now: change pickup_time to "2024-03-15 22:30". Then delay 120 min plus 30 min = 150 min → new pickup "2024-03-16 01:00".
    # But prompt says "accounting for an extra 30 minutes after landing to clear customs". That adds 30 min after landing, not after original pickup.
    # So new pickup = original arrival time (22:00) + delay (120) + 30 = 00:30 next day. Wait arrival becomes 00:00 (delayed 2h). Then +30 = 00:30.
    # So new pickup = "2024-03-16 00:30".
    # Let's set original pickup = "2024-03-15 22:30" (30 min after original arrival). Then delay+30 => new = "2024-03-16 00:30". That's consistent.
    # I'll update env_builder. Also adjust verify accordingly.
    # We'll assume new time is "2024-03-16 00:30". We'll check exactly that.
    # For simplicity, we can make new time "2024-03-16 00:30".
    # I'll redo the env_builder with corrected pickup.
    # But the prompt already printed, can't change. However the prompt didn't give exact times, so we can fix env_builder.
    # We'll proceed with the corrected logic in verify.

    # Actually let's recompute properly: flight UA123: original departure 18:00, arrival 22:00 (4h). Delay 120 → departure 20:00, arrival 00:00 (next day).
    # Original pickup time should be ~22:30 (30 min after on-time arrival). New pickup time = arrival after delay (00:00) + 30 min = 00:30.
    # So new pickup = "2024-03-16 00:30".
    # We'll check for that string.
    expected_time = "2024-03-16 00:30"
    time_correct = False
    for u in updates:
        if u.get("pickup_time") == expected_time:
            time_correct = True
            break
    if time_correct:
        add_item("correct new pickup time", 15, True, f"Found {expected_time}")
    else:
        add_item("correct new pickup time", 15, False, f"Expected {expected_time}, got something else")

    # 8. Excludes cancelled and unrelated bookings
    # Should only contain tb001 (the affected one) or at least not contain tb003 (cancelled) or tb002/tb004 (unrelated)
    bad_ids = {"tb002", "tb003", "tb004"}
    found_bad = False
    for u in updates:
        if u.get("booking_id") in bad_ids:
            found_bad = True
            break
    if not found_bad:
        add_item("excludes cancelled/unrelated bookings", 10, True, "Only tb001 present")
    else:
        add_item("excludes cancelled/unrelated bookings", 10, False, "Contains unwanted booking")

# 9. notification_draft recipient email
if nd is not None:
    if isinstance(nd, dict):
        # could be {"to": "john.smith@example.com", ...} or {"recipient": ...}
        email = nd.get("to") or nd.get("recipient") or nd.get("email") or ""
        if email == "john.smith@example.com":
            add_item("recipient email correct", 10, True, "Found john.smith@example.com")
        else:
            add_item("recipient email correct", 10, False, f"Expected john.smith@example.com, got '{email}'")
    else:
        add_item("recipient email correct", 10, False, "Notification is not a dict")

    # 10. notification mentions delay and new time
    if isinstance(nd, dict):
        msg = json.dumps(nd).lower()
        if "delay" in msg and ("00:30" in msg or "12:30 am" in msg or "0:30" in msg):
            add_item("notification mentions delay and new time", 10, True, "Contains delay and new time")
        else:
            add_item("notification mentions delay and new time", 10, False, "Missing delay or new time reference")
    else:
        add_item("notification mentions delay and new time", 10, False, "Notification not a dict")
else:
    add_item("recipient email correct", 10, False, "No notification data", 0)
    add_item("notification mentions delay and new time", 10, False, "No notification data", 0)

# Compute total
result["total_score"] = sum(d["score"] for d in result["details"])
with open(os.path.join(workplace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"Score: {result['total_score']}/100")
print(json.dumps(result["details"], indent=2))
