import json
import os
import sys
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    score_details = []
    total_score = 0

    # Helper to add score item
    def add_item(name, score, max_score, passed, reason=""):
        score_details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. Output directory exists (5 points)
    output_dir = ws / "output"
    if output_dir.is_dir():
        total_score += add_item("output/ directory exists", 5, 5, True)
    else:
        total_score += add_item("output/ directory exists", 0, 5, False, "Missing output/ directory")

    # 2. booking_summary.json exists and is valid JSON (10 points)
    summary_path = output_dir / "booking_summary.json"
    if summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text())
            total_score += add_item("booking_summary.json valid JSON", 10, 10, True)
        except (json.JSONDecodeError, Exception) as e:
            total_score += add_item("booking_summary.json valid JSON", 0, 10, False, f"Invalid JSON: {e}")
            summary = None
    else:
        total_score += add_item("booking_summary.json exists", 0, 10, False, "File not found")
        summary = None

    # 3. approval_request.json exists and is valid JSON (10 points)
    approval_path = output_dir / "approval_request.json"
    if approval_path.is_file():
        try:
            approval = json.loads(approval_path.read_text())
            total_score += add_item("approval_request.json valid JSON", 10, 10, True)
        except (json.JSONDecodeError, Exception) as e:
            total_score += add_item("approval_request.json valid JSON", 0, 10, False, f"Invalid JSON: {e}")
            approval = None
    else:
        total_score += add_item("approval_request.json exists", 0, 10, False, "File not found")
        approval = None

    # 4. booking_summary field completeness (15 points)
    summary_fields = ["booking_id", "selected_platform", "price", "currency", "cabin_class",
                      "departure_date", "origin", "destination", "policy_id", "policy_compliant",
                      "approval_required"]
    if summary is not None:
        missing = [f for f in summary_fields if f not in summary]
        if not missing:
            total_score += add_item("booking_summary contains all required fields", 15, 15, True)
        else:
            total_score += add_item("booking_summary contains all required fields", 0, 15, False,
                                    f"Missing fields: {missing}")

    # 5. approval_request field completeness (15 points)
    approval_fields = ["booking_id", "requester", "price", "policy_id", "approvers", "status"]
    if approval is not None:
        missing = [f for f in approval_fields if f not in approval]
        if not missing:
            total_score += add_item("approval_request contains all required fields", 15, 15, True)
        else:
            total_score += add_item("approval_request contains all required fields", 0, 15, False,
                                    f"Missing fields: {missing}")

    # 6. Core numeric and string correctness (45 points total, split into sub-items)
    if summary is not None:
        # 6a. selected_platform = "SkyBook" (10)
        if summary.get("selected_platform") == "SkyBook":
            total_score += add_item("selected_platform is SkyBook", 10, 10, True)
        else:
            total_score += add_item("selected_platform is SkyBook", 0, 10, False,
                                    f"Got {summary.get('selected_platform')}")

        # 6b. price = 3200 (10)
        if summary.get("price") == 3200:
            total_score += add_item("price is 3200", 10, 10, True)
        else:
            total_score += add_item("price is 3200", 0, 10, False,
                                    f"Got {summary.get('price')}")

        # 6c. policy_compliant = True (5)
        if summary.get("policy_compliant") is True:
            total_score += add_item("policy_compliant is True", 5, 5, True)
        else:
            total_score += add_item("policy_compliant is True", 0, 5, False,
                                    f"Got {summary.get('policy_compliant')}")

        # 6d. approval_required = True (5)
        if summary.get("approval_required") is True:
            total_score += add_item("approval_required is True", 5, 5, True)
        else:
            total_score += add_item("approval_required is True", 0, 5, False,
                                    f"Got {summary.get('approval_required')}")

        # 6e. other fields correctness (15)
        other_checks = [
            ("cabin_class", "business"),
            ("origin", "JFK"),
            ("destination", "LHR"),
            ("departure_date", "2026-06-15"),
            ("currency", "USD"),
            ("policy_id", "standard_travel_policy")
        ]
        passed_other = 0
        total_other = len(other_checks)
        for field, expected in other_checks:
            if summary.get(field) == expected:
                passed_other += 1
        if passed_other == total_other:
            total_score += add_item("Other fixed fields correct", 15, 15, True)
        else:
            total_score += add_item("Other fixed fields correct",
                                    int(15 * passed_other / total_other), 15, False,
                                    f"Passed {passed_other}/{total_other}: {[(f, summary.get(f)) for f,_ in other_checks]}")

    # 7. approval_request correctness (remainder of points? Already covered fields. We'll add a check for status = "pending" (5 points) and booking_id consistency (5 points)
    if approval is not None:
        # status = "pending"
        if approval.get("status") == "pending":
            total_score += add_item("approval status is pending", 5, 5, True)
        else:
            total_score += add_item("approval status is pending", 0, 5, False,
                                    f"Got {approval.get('status')}")

        # booking_id consistency between the two files
        if summary is not None and approval.get("booking_id") == summary.get("booking_id"):
            total_score += add_item("booking_id consistent across files", 5, 5, True)
        else:
            total_score += add_item("booking_id consistent across files", 0, 5, False,
                                    "booking_id mismatch or missing")
    else:
        total_score += add_item("approval status check skipped", 0, 5, False, "approval_request missing")
        total_score += add_item("booking_id consistency check skipped", 0, 5, False, "approval_request missing")

    # Clamp to 100
    final_score = min(total_score, 100)

    result = {
        "total_score": final_score,
        "details": score_details
    }
    output_path = ws / "workplace_score.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
