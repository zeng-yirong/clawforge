import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0

    # 1. File existence (10 points)
    exists = os.path.isfile("reproduction_ledger.json")
    details.append({
        "item": "reproduction_ledger.json exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "File found" if exists else "File not found"
    })
    if not exists:
        total_score = sum(d["score"] for d in details)
        _write_score(total_score, details)
        return

    # 2. Valid JSON (10 points)
    try:
        with open("reproduction_ledger.json", "r") as f:
            data = json.load(f)
        valid_json = True
        details.append({
            "item": "Valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parses successfully"
        })
    except Exception as e:
        valid_json = False
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Parse error: {e}"
        })
        total_score = sum(d["score"] for d in details)
        _write_score(total_score, details)
        return

    # 3. Contains required top-level fields (5 points each, total 15)
    required_fields = ["project_id", "total_docs", "success_count", "failure_count", "details"]
    for field in required_fields:
        present = field in data
        details.append({
            "item": f"Field '{field}' present",
            "score": 5 if present else 0,
            "max_score": 5,
            "passed": present,
            "reason": "Found" if present else f"Missing field '{field}'"
        })

    # 4. Correct project_id (5 points)
    pid_correct = data.get("project_id") == "proj-repro-001"
    details.append({
        "item": "project_id is 'proj-repro-001'",
        "score": 5 if pid_correct else 0,
        "max_score": 5,
        "passed": pid_correct,
        "reason": f"Got '{data.get('project_id')}'" if pid_correct else f"Expected 'proj-repro-001', got '{data.get('project_id')}'"
    })

    # 5. correct total_docs (should be 4) - 15 points
    expected_total = 4
    total_correct = data.get("total_docs") == expected_total
    details.append({
        "item": f"total_docs equals {expected_total}",
        "score": 15 if total_correct else 0,
        "max_score": 15,
        "passed": total_correct,
        "reason": f"Got {data.get('total_docs')}" if total_correct else f"Expected {expected_total}, got {data.get('total_docs')}"
    })

    # 6. correct success_count (should be 3) - 20 points
    expected_success = 3
    success_correct = data.get("success_count") == expected_success
    details.append({
        "item": f"success_count equals {expected_success}",
        "score": 20 if success_correct else 0,
        "max_score": 20,
        "passed": success_correct,
        "reason": f"Got {data.get('success_count')}" if success_correct else f"Expected {expected_success}, got {data.get('success_count')}"
    })

    # 7. correct failure_count (should be 1) - 20 points
    expected_failure = 1
    failure_correct = data.get("failure_count") == expected_failure
    details.append({
        "item": f"failure_count equals {expected_failure}",
        "score": 20 if failure_correct else 0,
        "max_score": 20,
        "passed": failure_correct,
        "reason": f"Got {data.get('failure_count')}" if failure_correct else f"Expected {expected_failure}, got {data.get('failure_count')}"
    })

    # 8. details list length (should be 4) - 10 points
    details_list = data.get("details", [])
    len_correct = len(details_list) == 4
    details.append({
        "item": "details list length is 4",
        "score": 10 if len_correct else 0,
        "max_score": 10,
        "passed": len_correct,
        "reason": f"Length {len(details_list)}" if len_correct else f"Expected 4, got {len(details_list)}"
    })

    # 9. Each detail has doc_id and status (5 points)
    all_have_fields = True
    for entry in details_list:
        if not isinstance(entry, dict) or "doc_id" not in entry or "status" not in entry:
            all_have_fields = False
            break
    details.append({
        "item": "Each detail has 'doc_id' and 'status'",
        "score": 5 if all_have_fields else 0,
        "max_score": 5,
        "passed": all_have_fields,
        "reason": "All entries have required fields" if all_have_fields else "Missing fields in some entries"
    })

    # Sum up
    total_score = sum(d["score"] for d in details)
    _write_score(total_score, details)

def _write_score(total, details):
    score_data = {"total_score": min(total, 100), "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)
    # Also print to stdout for logging
    print(f"Total Score: {score_data['total_score']}/100")
    for d in details:
        print(f"  {d['item']}: {d['passed']} ({d['score']}/{d['max_score']})")

if __name__ == "__main__":
    main()
