#!/usr/bin/env python3
import json
import os
import sys
import re

def read_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. Check that onboarding_completion.json exists and is valid JSON (10 pts)
    result_path = os.path.join(workspace, "onboarding_completion.json")
    result = read_json(result_path)
    if result is None:
        details.append({
            "item": "onboarding_completion.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File missing or invalid JSON"
        })
        # early exit if no file
        score_output = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_output, f, indent=2)
        return
    else:
        details.append({
            "item": "onboarding_completion.json exists and valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File present and parseable"
        })
        total_score += 10

    # 2. Check top-level structure: must have key "completed_onboardings" (10 pts)
    if not isinstance(result, dict) or "completed_onboardings" not in result:
        details.append({
            "item": "Top-level key 'completed_onboardings' present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing key or not a dict"
        })
    else:
        onboardings = result["completed_onboardings"]
        if not isinstance(onboardings, list):
            details.append({
                "item": "Top-level key 'completed_onboardings' present",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Value is not a list"
            })
        else:
            details.append({
                "item": "Top-level key 'completed_onboardings' present",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Structure correct"
            })
            total_score += 10

            # 3. Exactly 1 entry in the list (only EMP003 qualifies) (15 pts)
            if len(onboardings) != 1:
                details.append({
                    "item": "Exactly one completed onboarding entry",
                    "score": 0,
                    "max_score": 15,
                    "passed": False,
                    "reason": f"Expected 1 entry, found {len(onboardings)}"
                })
            else:
                details.append({
                    "item": "Exactly one completed onboarding entry",
                    "score": 15,
                    "max_score": 15,
                    "passed": True,
                    "reason": "Count matches expectation"
                })
                total_score += 15

                entry = onboardings[0]

                # 4. employee_id = "EMP003" (5 pts)
                if entry.get("employee_id") == "EMP003":
                    details.append({
                        "item": "employee_id is EMP003",
                        "score": 5,
                        "max_score": 5,
                        "passed": True,
                        "reason": "Correct ID"
                    })
                    total_score += 5
                else:
                    details.append({
                        "item": "employee_id is EMP003",
                        "score": 0,
                        "max_score": 5,
                        "passed": False,
                        "reason": f"Got {entry.get('employee_id')}"
                    })

                # 5. email_profile = "john.smith@company.com" (15 pts)
                expected_email = "john.smith@company.com"
                if entry.get("email_profile") == expected_email:
                    details.append({
                        "item": "email_profile correct",
                        "score": 15,
                        "max_score": 15,
                        "passed": True,
                        "reason": "Matches expected"
                    })
                    total_score += 15
                else:
                    details.append({
                        "item": "email_profile correct",
                        "score": 0,
                        "max_score": 15,
                        "passed": False,
                        "reason": f"Got '{entry.get('email_profile')}', expected '{expected_email}'"
                    })

                # 6. system_access list (15 pts)
                expected_systems = ["GitLab", "Jira", "Confluence"]
                systems = entry.get("system_access", [])
                if isinstance(systems, list) and sorted(systems) == sorted(expected_systems):
                    details.append({
                        "item": "system_access correct (Engineering pack)",
                        "score": 15,
                        "max_score": 15,
                        "passed": True,
                        "reason": "Systems match expected"
                    })
                    total_score += 15
                else:
                    details.append({
                        "item": "system_access correct (Engineering pack)",
                        "score": 0,
                        "max_score": 15,
                        "passed": False,
                        "reason": f"Got {systems}, expected {expected_systems}"
                    })

                # 7. equipment_assigned = "LT-2025-001" (15 pts)
                if entry.get("equipment_assigned") == "LT-2025-001":
                    details.append({
                        "item": "equipment_assigned correct (available laptop)",
                        "score": 15,
                        "max_score": 15,
                        "passed": True,
                        "reason": "Asset tag matches"
                    })
                    total_score += 15
                else:
                    details.append({
                        "item": "equipment_assigned correct (available laptop)",
                        "score": 0,
                        "max_score": 15,
                        "passed": False,
                        "reason": f"Got '{entry.get('equipment_assigned')}', expected 'LT-2025-001'"
                    })

                # 8. welcome_message contains "John" and onboarding wording (5 pts)
                msg = entry.get("welcome_message", "")
                if isinstance(msg, str) and "John" in msg and "onboarding" in msg.lower():
                    details.append({
                        "item": "welcome_message has correct content",
                        "score": 5,
                        "max_score": 5,
                        "passed": True,
                        "reason": "Message includes name and onboarding reference"
                    })
                    total_score += 5
                else:
                    details.append({
                        "item": "welcome_message has correct content",
                        "score": 0,
                        "max_score": 5,
                        "passed": False,
                        "reason": f"Got '{msg}'"
                    })

    # Final score
    score_output = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_output, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
