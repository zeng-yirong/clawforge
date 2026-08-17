import json
import os
import sys
from pathlib import Path

def verify(workspace: str):
    details = []
    total_score = 0
    
    ws = Path(workspace)
    
    # 1. Check that ops directory exists (5 points)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Found ops/ directory"
        })
        total_score += 5
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ directory not found"
        })
        # If directory missing, we cannot check file, skip remaining checks
        report = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(report, f, indent=2)
        return
    
    # 2. Check that disruption_report.json exists (10 points)
    report_file = ops_dir / "disruption_report.json"
    if report_file.is_file():
        details.append({
            "item": "disruption_report.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists at ops/disruption_report.json"
        })
        total_score += 10
    else:
        details.append({
            "item": "disruption_report.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found: ops/disruption_report.json"
        })
        report = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(report, f, indent=2)
        return
    
    # 3. Parse JSON (5 points)
    try:
        data = json.loads(report_file.read_text())
        details.append({
            "item": "Valid JSON",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Parsed successfully"
        })
        total_score += 5
    except json.JSONDecodeError as e:
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"JSON decode error: {e}"
        })
        report = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(report, f, indent=2)
        return
    
    # 4. Flight info (10 points)
    flight = data.get("flight", {})
    if flight.get("flight_id") == "AA456" and flight.get("delay_minutes") == 145:
        details.append({
            "item": "Flight info correct",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct flight_id and delay_minutes"
        })
        total_score += 10
    else:
        details.append({
            "item": "Flight info correct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected flight_id AA456 delay_minutes 145, got {flight}"
        })
    
    # 5. Adjusted hotel bookings list length = 1 (10 points)
    hotel_adjustments = data.get("adjusted_hotel_bookings", [])
    if len(hotel_adjustments) == 1:
        details.append({
            "item": "Adjusted hotel bookings count",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Exactly 1 hotel adjustment"
        })
        total_score += 10
    else:
        details.append({
            "item": "Adjusted hotel bookings count",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected 1, got {len(hotel_adjustments)}"
        })
    
    # 6. Hotel booking_id = booking_h1 (5 points)
    if hotel_adjustments and hotel_adjustments[0].get("booking_id") == "booking_h1":
        details.append({
            "item": "Hotel booking ID correct",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "booking_h1"
        })
        total_score += 5
    else:
        details.append({
            "item": "Hotel booking ID correct",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Expected booking_h1, got {hotel_adjustments[0].get('booking_id') if hotel_adjustments else None}"
        })
    
    # 7. new_check_in = 2025-07-21 (10 points)
    if hotel_adjustments and hotel_adjustments[0].get("new_check_in") == "2025-07-21":
        details.append({
            "item": "Hotel new check-in",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct new check-in date"
        })
        total_score += 10
    else:
        details.append({
            "item": "Hotel new check-in",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected 2025-07-21, got {hotel_adjustments[0].get('new_check_in') if hotel_adjustments else None}"
        })
    
    # 8. new_check_out = 2025-07-23 (10 points)
    if hotel_adjustments and hotel_adjustments[0].get("new_check_out") == "2025-07-23":
        details.append({
            "item": "Hotel new check-out",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct new check-out date"
        })
        total_score += 10
    else:
        details.append({
            "item": "Hotel new check-out",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected 2025-07-23, got {hotel_adjustments[0].get('new_check_out') if hotel_adjustments else None}"
        })
    
    # 9. Transport adjustments list length = 1 (10 points)
    transport_adjustments = data.get("adjusted_transport_bookings", [])
    if len(transport_adjustments) == 1:
        details.append({
            "item": "Adjusted transport bookings count",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Exactly 1 transport adjustment"
        })
        total_score += 10
    else:
        details.append({
            "item": "Adjusted transport bookings count",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected 1, got {len(transport_adjustments)}"
        })
    
    # 10. Transport booking_id = booking_t1 (5 points)
    if transport_adjustments and transport_adjustments[0].get("booking_id") == "booking_t1":
        details.append({
            "item": "Transport booking ID correct",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "booking_t1"
        })
        total_score += 5
    else:
        details.append({
            "item": "Transport booking ID correct",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Expected booking_t1, got {transport_adjustments[0].get('booking_id') if transport_adjustments else None}"
        })
    
    # 11. new_pickup_time = "2025-07-20 20:55" (10 points)
    expected_pickup = "2025-07-20 20:55"
    if transport_adjustments and transport_adjustments[0].get("new_pickup_time") == expected_pickup:
        details.append({
            "item": "Transport new pickup time",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Correct new pickup time ({expected_pickup})"
        })
        total_score += 10
    else:
        details.append({
            "item": "Transport new pickup time",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected {expected_pickup}, got {transport_adjustments[0].get('new_pickup_time') if transport_adjustments else None}"
        })
    
    # 12. Notifications list length = 2 (5 points)
    notifications = data.get("notifications", [])
    if len(notifications) == 2:
        details.append({
            "item": "Notifications count",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Exactly 2 notifications"
        })
        total_score += 5
    else:
        details.append({
            "item": "Notifications count",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Expected 2, got {len(notifications)}"
        })
    
    # 13. First notification: Jane Doe (2.5 points)
    if len(notifications) >= 1:
        n0 = notifications[0]
        if n0.get("name") == "Jane Doe" and n0.get("email") == "jane.doe@example.com":
            details.append({
                "item": "Notification 1 (Jane Doe)",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Name and email correct"
            })
            total_score += 5
        else:
            details.append({
                "item": "Notification 1 (Jane Doe)",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Expected name Jane Doe, email jane.doe@example.com, got {n0}"
            })
    else:
        details.append({
            "item": "Notification 1 (Jane Doe)",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Notifications list has fewer than 1 entries"
        })
    
    # 14. Second notification: John Smith (2.5 points)
    if len(notifications) >= 2:
        n1 = notifications[1]
        if n1.get("name") == "John Smith" and n1.get("email") == "john.smith@example.com":
            details.append({
                "item": "Notification 2 (John Smith)",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Name and email correct"
            })
            total_score += 5
        else:
            details.append({
                "item": "Notification 2 (John Smith)",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Expected name John Smith, email john.smith@example.com, got {n1}"
            })
    else:
        details.append({
            "item": "Notification 2 (John Smith)",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Notifications list has fewer than 2 entries"
        })
    
    # Build final report
    report = {
        "total_score": total_score,
        "details": details
    }
    
    # Write to workplace_score.json
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary (optional, but helpful for agent)
    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
