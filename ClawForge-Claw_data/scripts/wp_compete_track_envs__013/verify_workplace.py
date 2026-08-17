import sys
import json
import os
import re

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def score():
    details = []
    total = 0

    # 1. Check that ops directory exists (10 pts)
    ops_path = os.path.join(WORKSPACE, "ops")
    if os.path.isdir(ops_path):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        total += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ missing"})

    # 2. Check that ops/eu_risk_report.json exists (10 pts)
    report_path = os.path.join(ops_path, "eu_risk_report.json") if os.path.isdir(ops_path) else None
    if report_path and os.path.isfile(report_path):
        details.append({"item": "eu_risk_report.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file present"})
        total += 10
    else:
        details.append({"item": "eu_risk_report.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # Cannot proceed further
        return finalize(total, details)

    # 3. Parse as JSON (10 pts)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parsed successfully"})
        total += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
        return finalize(total, details)

    # 4. Must be a list (5 pts)
    if isinstance(data, list):
        details.append({"item": "output is a list", "score": 5, "max_score": 5, "passed": True, "reason": "type list"})
        total += 5
    else:
        details.append({"item": "output is a list", "score": 0, "max_score": 5, "passed": False, "reason": f"expected list, got {type(data).__name__}"})
        # can still check list-like; but abort further list checks
        # we'll continue but later checks will be skipped

    # 5. Each item must have exactly required fields: policy_id, title, impact_level (15 pts)
    field_issues = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            field_issues.append(f"item {i} not dict")
            continue
        required = {"policy_id", "title", "impact_level"}
        actual = set(item.keys())
        missing = required - actual
        extra = actual - required
        if missing:
            field_issues.append(f"item {i} missing {missing}")
        if extra:
            field_issues.append(f"item {i} has extra fields {extra}")
    if field_issues:
        details.append({"item": "field correctness (required fields only)", "score": 0, "max_score": 15, "passed": False, "reason": "; ".join(field_issues)})
    else:
        details.append({"item": "field correctness (required fields only)", "score": 15, "max_score": 15, "passed": True, "reason": "all items have exactly policy_id, title, impact_level"})
        total += 15

    # 6. Length must be exactly 2 (20 pts)
    expected_len = 2
    actual_len = len(data)
    if actual_len == expected_len:
        details.append({"item": "correct number of policies", "score": 20, "max_score": 20, "passed": True, "reason": f"found {actual_len} entries"})
        total += 20
    else:
        details.append({"item": "correct number of policies", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_len}, got {actual_len}"})

    # 7. Verify the exact policy_id values (30 pts)
    if isinstance(data, list):
        actual_ids = set()
        for item in data:
            if isinstance(item, dict) and "policy_id" in item:
                actual_ids.add(item["policy_id"])
        expected_ids = {"EU-DMA-2025", "EU-GDPR-2026"}
        if actual_ids == expected_ids:
            details.append({"item": "correct policy IDs (EU-DMA-2025, EU-GDPR-2026)", "score": 30, "max_score": 30, "passed": True, "reason": f"matched exactly: {actual_ids}"})
            total += 30
        else:
            missing_ids = expected_ids - actual_ids
            extra_ids = actual_ids - expected_ids
            reason_parts = []
            if missing_ids:
                reason_parts.append(f"missing: {missing_ids}")
            if extra_ids:
                reason_parts.append(f"extra: {extra_ids}")
            details.append({"item": "correct policy IDs", "score": 0, "max_score": 30, "passed": False, "reason": "; ".join(reason_parts)})
    else:
        details.append({"item": "correct policy IDs", "score": 0, "max_score": 30, "passed": False, "reason": "data not a list, cannot check IDs"})

    # Finalize
    finalize(total, details)

def finalize(total, details):
    result = {"total_score": total, "details": details}
    result_path = os.path.join(WORKSPACE, "workplace_score.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/100 written to {result_path}")
    sys.exit(0)

if __name__ == "__main__":
    score()
