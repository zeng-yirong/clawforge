"""
Verifier for flight delay cascade task (wp_flight_delay_envs__039).
Checks the agent's output file ops/affected_travelers.json against predefined truth.
No network calls, no LLM.
"""
import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    score = 0
    max_score = 100
    details = []

    # paths
    result_path = Path(workspace) / "ops" / "affected_travelers.json"
    data_dir = Path(workspace) / "data"

    # 1. File exists (10 points)
    if not result_path.exists():
        details.append({"item": "File exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/affected_travelers.json not found"})
        # cannot proceed further, early exit
        return {"total_score": 0, "details": details}
    else:
        details.append({"item": "File exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        score += 10

    # 2. Valid JSON (10 points)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed"})
        score += 10
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON error: {str(e)}"})
        return {"total_score": score, "details": details}

    # 3. Structure check (20 points)
    if not isinstance(data, dict) or "affected_travelers" not in data:
        details.append({"item": "Structure (top-level key)", "score": 0, "max_score": 20, "passed": False, "reason": "Missing 'affected_travelers' key or root not object"})
        return {"total_score": score, "details": details}

    travelers = data["affected_travelers"]
    if not isinstance(travelers, list):
        details.append({"item": "Structure (list)", "score": 0, "max_score": 20, "passed": False, "reason": "'affected_travelers' is not a list"})
        return {"total_score": score, "details": details}

    # check each traveler has required fields
    mandatory_fields = ["contact_id", "name", "email", "affected_bookings"]
    structure_ok = True
    for t in travelers:
        for f in mandatory_fields:
            if f not in t:
                structure_ok = False
                break
        if not structure_ok:
            break
        bookings = t.get("affected_bookings", [])
        if not isinstance(bookings, list):
            structure_ok = False
            break
        for b in bookings:
            for bf in ["type", "booking_id", "flight_id"]:
                if bf not in b:
                    structure_ok = False
                    break
            if not structure_ok:
                break
        if not structure_ok:
            break

    if structure_ok:
        details.append({"item": "Structure (fields in travelers and bookings)", "score": 20, "max_score": 20, "passed": True, "reason": "All required fields present"})
        score += 20
    else:
        details.append({"item": "Structure (fields in travelers and bookings)", "score": 0, "max_score": 20, "passed": False, "reason": "Missing required field in traveler or booking"})
        return {"total_score": score, "details": details}

    # 4. Correct traveler count and identities (15 points) - must be exactly Jane Doe and Mike Johnson
    expected_traveler_ids = {"C001", "C003"}  # Jane and Mike
    actual_ids = set()
    contact_map = {}
    for t in travelers:
        actual_ids.add(t["contact_id"])
        contact_map[t["contact_id"]] = t

    if actual_ids != expected_traveler_ids:
        details.append({"item": "Traveler identification", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected travelers C001,C003 but got {actual_ids}"})
        return {"total_score": score, "details": details}
    else:
        # also verify names and emails
        name_email_ok = True
        if contact_map["C001"]["name"] != "Jane Doe" or contact_map["C001"]["email"] != "jane.doe@example.com":
            name_email_ok = False
        if contact_map["C003"]["name"] != "Mike Johnson" or contact_map["C003"]["email"] != "mike.johnson@example.com":
            name_email_ok = False
        if name_email_ok:
            details.append({"item": "Traveler identification", "score": 15, "max_score": 15, "passed": True, "reason": "Correct travelers with correct names/emails"})
            score += 15
        else:
            details.append({"item": "Traveler identification", "score": 0, "max_score": 15, "passed": False, "reason": "Traveler ID correct but name/email mismatch"})
            return {"total_score": score, "details": details}

    # 5. Check Jane's bookings (2 bookings: hotel H001 and transport T001) (20 points)
    jane = contact_map["C001"]
    jane_bookings = jane["affected_bookings"]
    expected_jane = [
        {"type": "hotel", "booking_id": "H001", "flight_id": "FL001"},
        {"type": "transport", "booking_id": "T001", "flight_id": "FL001"}
    ]
    # create lookup by booking_id for easier check
    jane_map = {b["booking_id"]: b for b in jane_bookings}
    jane_ok = True
    req_ids = {"H001", "T001"}
    if set(jane_map.keys()) != req_ids:
        jane_ok = False
    else:
        for b in expected_jane:
            actual = jane_map[b["booking_id"]]
            if actual.get("type") != b["type"] or actual.get("flight_id") != b["flight_id"]:
                jane_ok = False
                break
    if jane_ok:
        details.append({"item": "Jane Doe bookings", "score": 20, "max_score": 20, "passed": True, "reason": "H001 and T001 correctly included"})
        score += 20
    else:
        details.append({"item": "Jane Doe bookings", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected H001,T001; got {list(jane_map.keys())}"})
        return {"total_score": score, "details": details}

    # 6. Check Mike's bookings (2 bookings: hotel H003 and transport T003) (20 points)
    mike = contact_map["C003"]
    mike_bookings = mike["affected_bookings"]
    expected_mike = [
        {"type": "hotel", "booking_id": "H003", "flight_id": "FL003"},
        {"type": "transport", "booking_id": "T003", "flight_id": "FL003"}
    ]
    mike_map = {b["booking_id"]: b for b in mike_bookings}
    mike_ok = True
    req_ids = {"H003", "T003"}
    if set(mike_map.keys()) != req_ids:
        mike_ok = False
    else:
        for b in expected_mike:
            actual = mike_map[b["booking_id"]]
            if actual.get("type") != b["type"] or actual.get("flight_id") != b["flight_id"]:
                mike_ok = False
                break
    if mike_ok:
        details.append({"item": "Mike Johnson bookings", "score": 20, "max_score": 20, "passed": True, "reason": "H003 and T003 correctly included"})
        score += 20
    else:
        details.append({"item": "Mike Johnson bookings", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected H003,T003; got {list(mike_map.keys())}"})
        return {"total_score": score, "details": details}

    # 7. Bonus check: no canceled bookings and no unaffected traveler (5 points extra but within 100 max)
    # Ensure H004 (canceled) is not in Jane's bookings
    if "H004" in jane_map or "H004" in mike_map:
        details.append({"item": "No canceled bookings", "score": -5, "max_score": 0, "passed": False, "reason": "Canceled booking H004 should be excluded"})
        # subtract 5, but not below 0
        details[-1]["score"] = -5
        score = max(0, score-5)
    else:
        details.append({"item": "No canceled bookings", "score": 0, "max_score": 0, "passed": True, "reason": "Canceled booking correctly excluded"})

    # Ensure John Smith (C002) is NOT in the list
    if "C002" in actual_ids:
        details.append({"item": "No unaffected traveler", "score": -5, "max_score": 0, "passed": False, "reason": "John Smith (C002) should not be present"})
        score = max(0, score-5)
    else:
        details.append({"item": "No unaffected traveler", "score": 0, "max_score": 0, "passed": True, "reason": "John Smith correctly excluded"})

    # finalize, score capped at 100
    final_score = min(score, 100)
    details[-1]["score"] = final_score - sum(d["score"] for d in details[:-1])  # adjust last item to match
    if final_score < 0:
        final_score = 0

    return {"total_score": final_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
