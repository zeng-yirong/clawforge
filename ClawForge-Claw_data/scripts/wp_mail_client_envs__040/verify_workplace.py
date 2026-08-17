"""
Verify that the agent correctly extracted meeting details from Bob's email.
Scores:
- ops/meeting_details.json exists: 10
- JSON is valid: 10
- meeting_time equals expected: 25
- location equals expected: 25
- preparation_items list matches expected (unordered): 30
- No extra top-level keys: 10
Total: 100
"""

import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details_path = os.path.join(workspace, "ops", "meeting_details.json")
    score = 0
    details = []
    
    # --- item 1: file exists ---
    if os.path.isfile(details_path):
        details.append({"item": "File exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/meeting_details.json found"})
        score += 10
    else:
        details.append({"item": "File exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # Cannot proceed further
        write_score(score, details, workspace)
        return
    
    # --- item 2: valid JSON ---
    try:
        with open(details_path, "r") as f:
            data = json.load(f)
        details.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        score += 10
    except Exception as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
        write_score(score, details, workspace)
        return
    
    # Expected values
    expected_time = "2025-04-15 15:00:00"
    expected_location = "Conference Room B"
    expected_items = {"project roadmap", "budget report"}
    
    # --- item 3: meeting_time ---
    actual_time = data.get("meeting_time", "")
    if actual_time == expected_time:
        details.append({"item": "Meeting time", "score": 25, "max_score": 25, "passed": True, "reason": f"Correct: {actual_time}"})
        score += 25
    else:
        details.append({"item": "Meeting time", "score": 0, "max_score": 25, "passed": False, "reason": f"Expected '{expected_time}', got '{actual_time}'"})
    
    # --- item 4: location ---
    actual_location = data.get("location", "")
    if actual_location == expected_location:
        details.append({"item": "Location", "score": 25, "max_score": 25, "passed": True, "reason": f"Correct: {actual_location}"})
        score += 25
    else:
        details.append({"item": "Location", "score": 0, "max_score": 25, "passed": False, "reason": f"Expected '{expected_location}', got '{actual_location}'"})
    
    # --- item 5: preparation_items list ---
    actual_items = data.get("preparation_items", [])
    if isinstance(actual_items, list) and len(actual_items) == 2:
        actual_set = {item.strip().lower() for item in actual_items if isinstance(item, str)}
        expected_set = {item.lower() for item in expected_items}
        if actual_set == expected_set:
            details.append({"item": "Preparation items", "score": 30, "max_score": 30, "passed": True, "reason": "Both items present (ignoring order/case)"})
            score += 30
        else:
            details.append({"item": "Preparation items", "score": 0, "max_score": 30, "passed": False, "reason": f"Expected {expected_set}, got {actual_set}"})
    else:
        details.append({"item": "Preparation items", "score": 0, "max_score": 30, "passed": False, "reason": f"No valid list found or wrong length: {actual_items}"})
    
    # --- item 6: no extra keys ---
    required_keys = {"meeting_time", "location", "preparation_items"}
    extra = set(data.keys()) - required_keys
    if not extra:
        details.append({"item": "No extra keys", "score": 10, "max_score": 10, "passed": True, "reason": "Only the three required keys present"})
        score += 10
    else:
        details.append({"item": "No extra keys", "score": 0, "max_score": 10, "passed": False, "reason": f"Extra keys found: {extra}"})
    
    write_score(score, details, workspace)

def write_score(total, details, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
