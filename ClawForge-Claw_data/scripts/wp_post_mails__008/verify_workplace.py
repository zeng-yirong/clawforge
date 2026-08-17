#!/usr/bin/env python3
"""Verify the agent's output for wp_post_mails__008."""
import sys
import json
import os
import re

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def main():
    details = []
    total_score = 0

    # 1. Check that ops directory exists (10 pts)
    ops_dir = os.path.join(WORKSPACE, "ops")
    d1 = {"item": "ops/ directory exists", "max_score": 10}
    if os.path.isdir(ops_dir):
        d1["score"] = 10
        d1["passed"] = True
        d1["reason"] = "Found ops/ directory"
    else:
        d1["score"] = 0
        d1["passed"] = False
        d1["reason"] = "Directory ops/ not found"
    total_score += d1["score"]
    details.append(d1)

    # 2. Check that ops/draft.json exists (20 pts)
    draft_path = os.path.join(WORKSPACE, "ops", "draft.json")
    d2 = {"item": "ops/draft.json exists", "max_score": 20}
    if os.path.isfile(draft_path):
        d2["score"] = 20
        d2["passed"] = True
        d2["reason"] = "File found"
    else:
        d2["score"] = 0
        d2["passed"] = False
        d2["reason"] = "File ops/draft.json missing"
    total_score += d2["score"]
    details.append(d2)

    if d2["passed"]:
        # 3. Check JSON is valid (10 pts)
        d3 = {"item": "draft.json is valid JSON", "max_score": 10}
        try:
            with open(draft_path, "r") as f:
                data = json.load(f)
            d3["score"] = 10
            d3["passed"] = True
            d3["reason"] = "JSON parse succeeded"
        except (json.JSONDecodeError, Exception) as e:
            d3["score"] = 0
            d3["passed"] = False
            d3["reason"] = f"JSON parse error: {e}"
            # Stop further checks that require data
            total_score += d3["score"]
            details.append(d3)
            # Fill remaining items with 0
            for item_name in ["Contains mission_name field", "Contains launch_code field",
                              "mission_name == 'Nova-7'", "launch_code == '0428'"]:
                details.append({"item": item_name, "score": 0, "max_score": 15 if "field" in item_name else 20,
                                "passed": False, "reason": "Skipped due to invalid JSON"})
            write_score(total_score, details)
            return

        total_score += d3["score"]
        details.append(d3)

        # 4. Check required fields (15 pts each)
        # 4a. mission_name
        d4a = {"item": "Contains mission_name field", "max_score": 15}
        if "mission_name" in data:
            d4a["score"] = 15
            d4a["passed"] = True
            d4a["reason"] = "Field present"
        else:
            d4a["score"] = 0
            d4a["passed"] = False
            d4a["reason"] = "Field mission_name missing"
        total_score += d4a["score"]
        details.append(d4a)

        # 4b. launch_code
        d4b = {"item": "Contains launch_code field", "max_score": 15}
        if "launch_code" in data:
            d4b["score"] = 15
            d4b["passed"] = True
            d4b["reason"] = "Field present"
        else:
            d4b["score"] = 0
            d4b["passed"] = False
            d4b["reason"] = "Field launch_code missing"
        total_score += d4b["score"]
        details.append(d4b)

        # 5. Check values (20 pts each)
        expected_mission = "Nova-7"
        expected_code = "0428"

        # 5a. mission_name value
        d5a = {"item": "mission_name == 'Nova-7'", "max_score": 20}
        if data.get("mission_name") == expected_mission:
            d5a["score"] = 20
            d5a["passed"] = True
            d5a["reason"] = f"Value matches '{expected_mission}'"
        else:
            d5a["score"] = 0
            d5a["passed"] = False
            d5a["reason"] = f"Expected '{expected_mission}', got '{data.get('mission_name')}'"
        total_score += d5a["score"]
        details.append(d5a)

        # 5b. launch_code value
        d5b = {"item": "launch_code == '0428'", "max_score": 20}
        if data.get("launch_code") == expected_code:
            d5b["score"] = 20
            d5b["passed"] = True
            d5b["reason"] = f"Value matches '{expected_code}'"
        else:
            d5b["score"] = 0
            d5b["passed"] = False
            d5b["reason"] = f"Expected '{expected_code}', got '{data.get('launch_code')}'"
        total_score += d5b["score"]
        details.append(d5b)
    else:
        # draft.json missing -> all subsequent items get 0
        for item_name in ["Valid JSON", "Contains mission_name field", "Contains launch_code field",
                          "mission_name == 'Nova-7'", "launch_code == '0428'"]:
            details.append({"item": item_name, "score": 0, "max_score": 10 if "JSON" in item_name else 15 if "field" in item_name else 20,
                            "passed": False, "reason": "draft.json missing"})

    total_score = min(total_score, 100)  # cap
    write_score(total_score, details)

def write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    out_path = os.path.join(WORKSPACE, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {score}/100")

if __name__ == "__main__":
    main()
