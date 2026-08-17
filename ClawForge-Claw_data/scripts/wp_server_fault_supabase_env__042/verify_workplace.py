import sys
import json
import os

# Expected result after applying filter:
# conditions: (category in ['ups_outage','service_down']) AND (status == 'open') AND (ticket_type == 'risk_work_order') AND opened_at >= "2025-04-10T00:00:00Z"
# sort by severity order: critical > high > medium, then by opened_at descending (newer first)
# From env_builder data:
# INC-005: service_down, critical, opened_at 2025-04-12T06:30:00Z -> passes
# INC-007: ups_outage, high, opened_at 2025-04-11T15:00:00Z -> passes
# INC-010: ups_outage, medium, opened_at 2025-04-14T08:00:00Z -> passes
# INC-006: service_down, high, opened_at 2025-04-10T01:00:00Z -> passes (>= threshold)
# Also INC-001? category ups_outage but opened_at 2025-04-08 (< threshold) -> excluded
# INC-004 ups_outage but ticket_type watchlist -> excluded
# INC-002 service_down but status closed -> excluded
# INC-008 network_degradation -> excluded
# INC-003 network_degradation -> excluded
# INC-009 service_down but opened_at 2025-04-09 (< threshold) -> excluded
# So passing: INC-005 (critical), INC-007 (high), INC-010 (medium), INC-006 (high)
# Order: critical first: INC-005 (2025-04-12)
# Then high: two -> newer first: INC-007 (2025-04-11) vs INC-006 (2025-04-10) => INC-007 before INC-006 (because 2025-04-11 > 2025-04-10)
# Then medium: INC-010 (2025-04-14)
# Expected list: ["INC-005", "INC-007", "INC-006", "INC-010"]

EXPECTED = ["INC-005", "INC-007", "INC-006", "INC-010"]

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "ops", "remediation_targets.json")
    details = []
    total_score = 0

    # 1) Check directory ops exists
    ops_dir = os.path.join(workspace, "ops")
    dir_passed = os.path.isdir(ops_dir)
    details.append({
        "item": "Directory 'ops' exists",
        "score": 10 if dir_passed else 0,
        "max_score": 10,
        "passed": dir_passed,
        "reason": "Directory found" if dir_passed else "Missing ops/ directory"
    })
    if dir_passed:
        total_score += 10

    # 2) Check target file exists
    file_passed = os.path.isfile(target_file)
    details.append({
        "item": "File 'ops/remediation_targets.json' exists",
        "score": 20 if file_passed else 0,
        "max_score": 20,
        "passed": file_passed,
        "reason": "File exists" if file_passed else "File not found at expected path"
    })
    if file_passed:
        total_score += 20

    # 3) Validate JSON parse
    json_valid = False
    payload = None
    if file_passed:
        try:
            with open(target_file, "r") as f:
                payload = json.load(f)
            json_valid = True
        except (json.JSONDecodeError, Exception):
            json_valid = False
    details.append({
        "item": "File contains valid JSON",
        "score": 20 if json_valid else 0,
        "max_score": 20,
        "passed": json_valid,
        "reason": "Valid JSON" if json_valid else "File could not be parsed as JSON"
    })
    if json_valid:
        total_score += 20

    # 4) Check that payload is a list of strings
    list_valid = False
    if json_valid and isinstance(payload, list):
        if all(isinstance(x, str) for x in payload):
            list_valid = True
    details.append({
        "item": "Payload is a JSON array of strings",
        "score": 10 if list_valid else 0,
        "max_score": 10,
        "passed": list_valid,
        "reason": "Array of strings" if list_valid else "Not a list of strings (possibly extra fields or wrong type)"
    })
    if list_valid:
        total_score += 10

    # 5) Exact content match with expected order
    content_match = False
    if list_valid:
        content_match = (payload == EXPECTED)
    details.append({
        "item": "Incident IDs match expected list in correct order",
        "score": 40 if content_match else 0,
        "max_score": 40,
        "passed": content_match,
        "reason": "Exact match" if content_match else f"Expected {EXPECTED}, got {payload}"
    })
    if content_match:
        total_score += 40

    # Write score file
    score_obj = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_obj, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/100")
    sys.exit(0 if total_score == 100 else 1)

if __name__ == "__main__":
    main()
