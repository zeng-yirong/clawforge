import os
import sys
import json
import re

def verify_workspace(workspace):
    results = []
    total_score = 0

    # 1. Check that ops/onboarding_summary.json exists
    summary_path = os.path.join(workspace, "ops", "onboarding_summary.json")
    if os.path.isfile(summary_path):
        results.append({"item": "output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/onboarding_summary.json found"})
        total_score += 10
    else:
        results.append({"item": "output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/onboarding_summary.json not found"})
        # can't continue without file
        write_results(results, total_score, workspace)
        return

    # 2. Parse JSON, check structure and correctness
    try:
        with open(summary_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        results.append({"item": "JSON validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        write_results(results, 10, workspace)
        return

    if not isinstance(data, list):
        results.append({"item": "JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "Expected a JSON array"})
        write_results(results, 10, workspace)
        return
    results.append({"item": "JSON validity", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON array"})
    total_score += 10

    # 3. Check length (should be 4 signed contracts: E001,E002,E003,E006)
    expected_count = 4
    actual_count = len(data)
    if actual_count == expected_count:
        results.append({"item": "record count", "score": 15, "max_score": 15, "passed": True, "reason": f"Contains {expected_count} records"})
        total_score += 15
    else:
        results.append({"item": "record count", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_count}, got {actual_count}"})
        # partial credit? can still check content of present records
        # but for fairness we just give 0 and stop scoring content? We'll still try to give partial on fields.
        # We'll adjust: give correct count full points, otherwise 0.
        # but we can still check fields for partial.

    # 4. Build expected result (sorted by email for consistency)
    #   Contracts signed: E001 Alice, E002 Bob, E003 Charlie, E006 Frank
    #   Standard systems sorted: ["crm", "email", "intranet"]  (alphabetic)
    #   Available equipment (by asset_tag): EQ001, EQ003, EQ005 (EQ006 also available but only first 3)
    #   Assign: E001->EQ001, E002->EQ003, E003->EQ005, E006->null (since only 3 available)
    std_systems = sorted(["crm", "intranet", "email"])
    expected = [
        {"email": "alice@company.com", "systems": std_systems, "asset_tag": "EQ001"},
        {"email": "bob@company.com",   "systems": std_systems, "asset_tag": "EQ003"},
        {"email": "charlie@company.com", "systems": std_systems, "asset_tag": "EQ005"},
        {"email": "frank@company.com", "systems": std_systems, "asset_tag": None}
    ]
    # Sort both by email
    expected_sorted = sorted(expected, key=lambda x: x["email"])
    # We expect agent's output sorted as well (by email or by employee_id? We'll mandate we sort by email in check)
    # Actually prompt doesn't specify order, but verify will sort both and compare.
    data_sorted = sorted(data, key=lambda x: x.get("email", ""))

    # 5. Check required fields for each record
    fields_ok = True
    for i, rec in enumerate(data_sorted):
        if not all(k in rec for k in ("email", "systems", "asset_tag")):
            fields_ok = False
            break
    if fields_ok:
        results.append({"item": "field completeness", "score": 10, "max_score": 10, "passed": True, "reason": "All records have email, systems, asset_tag"})
        total_score += 10
    else:
        results.append({"item": "field completeness", "score": 0, "max_score": 10, "passed": False, "reason": "Missing required fields in some records"})
        # cannot compare further
        write_results(results, total_score, workspace)
        return

    # 6. Compare exact values
    exact_match = True
    if len(data_sorted) != len(expected_sorted):
        exact_match = False
        results.append({"item": "value correctness", "score": 0, "max_score": 45, "passed": False, "reason": f"Record count mismatch, expected {len(expected_sorted)}, got {len(data_sorted)}"})
    else:
        mismatch_detail = []
        for i, (exp, act) in enumerate(zip(expected_sorted, data_sorted)):
            issues = []
            if exp["email"] != act.get("email"):
                issues.append(f"email expected {exp['email']}, got {act.get('email')}")
            if exp["systems"] != act.get("systems"):
                issues.append(f"systems expected {exp['systems']}, got {act.get('systems')}")
            if exp["asset_tag"] != act.get("asset_tag"):
                issues.append(f"asset_tag expected {exp['asset_tag']}, got {act.get('asset_tag')}")
            if issues:
                mismatch_detail.append(f"Record {i}: {'; '.join(issues)}")
        if mismatch_detail:
            exact_match = False
            reason = " | ".join(mismatch_detail)
            # Graded scoring: each record has weight 45/4 = 11.25, but we'll give partial according to correct records
            correct_records = sum(1 for i in range(len(expected_sorted)) if all(
                expected_sorted[i][k] == data_sorted[i].get(k) for k in ("email", "systems", "asset_tag")
            ))
            score = int(round(45 * correct_records / len(expected_sorted)))
            results.append({"item": "value correctness", "score": score, "max_score": 45, "passed": False, "reason": reason})
            total_score += score
        else:
            results.append({"item": "value correctness", "score": 45, "max_score": 45, "passed": True, "reason": "All field values exactly match expected"})
            total_score += 45

    # 7. Ensure no extra fields
    extra_fields = False
    for rec in data_sorted:
        if set(rec.keys()) != {"email", "systems", "asset_tag"}:
            extra_fields = True
            break
    if not extra_fields:
        results.append({"item": "no extra fields", "score": 10, "max_score": 10, "passed": True, "reason": "No extra fields in records"})
        total_score += 10
    else:
        results.append({"item": "no extra fields", "score": 0, "max_score": 10, "passed": False, "reason": "Records contain extra fields not requested"})

    write_results(results, total_score, workspace)

def write_results(results, total_score, workspace):
    output = {"total_score": total_score, "details": results}
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score: {total_score}/100")
    sys.exit(0 if total_score >= 80 else 1)  # optional exit code

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workspace(workspace)
