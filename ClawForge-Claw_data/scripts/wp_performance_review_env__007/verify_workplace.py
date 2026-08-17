import json
import os
import sys

def check(expected: dict):
    """Run all checks and return score details."""
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0
    max_total = 100

    # 1. Directory structure check (10 pts)
    required_dirs = ["data/employees", "data/ledgers", "data/rules"]
    dir_ok = all(os.path.isdir(os.path.join(workspace, d)) for d in required_dirs)
    details.append({
        "item": "Required directories exist",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "Found all required directories" if dir_ok else "Missing one or more of data/employees, data/ledgers, data/rules"
    })
    total += 10 if dir_ok else 0

    # 2. Output file exists (10 pts)
    output_path = os.path.join(workspace, "ops/performance_profiles.json")
    file_exists = os.path.isfile(output_path)
    details.append({
        "item": "ops/performance_profiles.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "Found file" if file_exists else "File not found at ops/performance_profiles.json"
    })
    if not file_exists:
        # Early exit
        details.append({
            "item": "JSON validity",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Skipped due to missing file"
        })
        details.append({
            "item": "Data completeness (3 employees)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Skipped due to missing file"
        })
        details.append({
            "item": "Score correctness for E001",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Skipped due to missing file"
        })
        details.append({
            "item": "Score correctness for E002",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Skipped due to missing file"
        })
        details.append({
            "item": "Score correctness for E003",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Skipped due to missing file"
        })
        total = 10 if dir_ok else 0
        write_score(details, total)
        return

    # 3. JSON validity (10 pts)
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        json_ok = isinstance(data, list) and len(data) == 3
        details.append({
            "item": "Output JSON is valid and contains array of 3 objects",
            "score": 10 if json_ok else 0,
            "max_score": 10,
            "passed": json_ok,
            "reason": "Valid JSON with 3 entries" if json_ok else "Invalid format or wrong count"
        })
        total += 10 if json_ok else 0
        if not json_ok:
            # Cannot proceed
            details.append({
                "item": "Data completeness",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Skipped - invalid data structure"
            })
            details.append({
                "item": "Score correctness for E001",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Skipped"
            })
            details.append({
                "item": "Score correctness for E002",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Skipped"
            })
            details.append({
                "item": "Score correctness for E003",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Skipped"
            })
            write_score(details, total)
            return
    except Exception as e:
        details.append({
            "item": "Output JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        write_score(details, 0)
        return

    # 4. Data completeness & field presence (20 pts)
    expected_ids = ["E001", "E002", "E003"]
    expected_fields = ["employee_id", "employee_name", "department", "role_code",
                       "feature_delivery", "quality_score", "collaboration_score", "total_score"]
    ids_in_output = [entry.get("employee_id") for entry in data]
    completeness = True
    missing_ids = []
    extra_fields_missing = []
    for entry in data:
        for field in expected_fields:
            if field not in entry:
                extra_fields_missing.append(f"Missing field '{field}' in entry {entry.get('employee_id', '?')}")
    for eid in expected_ids:
        if eid not in ids_in_output:
            missing_ids.append(eid)
            completeness = False
    if extra_fields_missing:
        completeness = False
    details.append({
        "item": "All 3 employees present with all required fields",
        "score": 20 if completeness else 0,
        "max_score": 20,
        "passed": completeness,
        "reason": "Complete and correct" if completeness else f"Problems: {', '.join(missing_ids + extra_fields_missing)}"
    })
    total += 20 if completeness else 0

    # 5. Score correctness (20+20+10 = 50 pts)
    # Expected totals (precomputed)
    expected_totals = {
        "E001": 80*0.5 + 70*0.3 + 90*0.2,  # 79.0
        "E002": 60*0.2 + 85*0.6 + 95*0.2,  # 82.0
        "E003": 90*0.4 + 80*0.4 + 85*0.2   # 85.0
    }
    # Build dict from output
    output_map = {e["employee_id"]: e for e in data}
    # Check E001 (20 pts)
    e1 = output_map.get("E001")
    if e1 and abs(e1.get("total_score", -1) - expected_totals["E001"]) < 0.15:
        details.append({
            "item": "E001 total_score correct (79.0)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Got {e1['total_score']}, expected 79.0"
        })
        total += 20
    else:
        details.append({
            "item": "E001 total_score correct (79.0)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {e1['total_score'] if e1 else 'missing'}, expected 79.0"
        })
    # E002 (20 pts)
    e2 = output_map.get("E002")
    if e2 and abs(e2.get("total_score", -1) - expected_totals["E002"]) < 0.15:
        details.append({
            "item": "E002 total_score correct (82.0)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Got {e2['total_score']}, expected 82.0"
        })
        total += 20
    else:
        details.append({
            "item": "E002 total_score correct (82.0)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {e2['total_score'] if e2 else 'missing'}, expected 82.0"
        })
    # E003 (10 pts)
    e3 = output_map.get("E003")
    if e3 and abs(e3.get("total_score", -1) - expected_totals["E003"]) < 0.15:
        details.append({
            "item": "E003 total_score correct (85.0)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Got {e3['total_score']}, expected 85.0"
        })
        total += 10
    else:
        details.append({
            "item": "E003 total_score correct (85.0)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Got {e3['total_score'] if e3 else 'missing'}, expected 85.0"
        })

    # Write result
    write_score(details, total)

def write_score(details, total):
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)

if __name__ == "__main__":
    check({})
