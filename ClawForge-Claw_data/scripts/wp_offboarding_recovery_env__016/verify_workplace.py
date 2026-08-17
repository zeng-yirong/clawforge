import sys
import os
import json
from datetime import datetime

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    results = []
    total_score = 0

    # ------------------------------------------------------------------
    # 1. Directory & file existence (10 pts)
    # ------------------------------------------------------------------
    required_files = [
        "data/offboarding/exit_requests.json",
        "data/offboarding/system_access.json",
        "data/offboarding/equipment_assignments.json",
        "handover_checklist.json"
    ]
    missing = []
    for f in required_files:
        if not os.path.isfile(f):
            missing.append(f)
    if missing:
        score = 0
        reason = f"Missing files: {', '.join(missing)}"
        results.append({"item": "Required files exist", "score": 0, "max_score": 10, "passed": False, "reason": reason})
    else:
        score = 10
        reason = "All required files present."
        results.append({"item": "Required files exist", "score": 10, "max_score": 10, "passed": True, "reason": reason})

    # ------------------------------------------------------------------
    # 2. JSON validity (5 pts) – all files must parse
    # ------------------------------------------------------------------
    valid = True
    for f in required_files:
        try:
            with open(f, "r") as fh:
                json.load(fh)
        except Exception as e:
            valid = False
            reason = f"{f} is not valid JSON: {e}"
            break
    if valid:
        results.append({"item": "All JSON files valid", "score": 5, "max_score": 5, "passed": True, "reason": "All files parse correctly."})
    else:
        results.append({"item": "All JSON files valid", "score": 0, "max_score": 5, "passed": False, "reason": reason})

    # ------------------------------------------------------------------
    # 3. Correct handling of approved employees (40 pts: 20 for systems, 20 for equipment)
    #    We use hard-coded ground truth for initial state.
    # ------------------------------------------------------------------
    # Ground truth initial data (must match env_builder exactly)
    INITIAL_EXIT = {
        "exit_requests": [
            {"employee_id": "EMP001", "employee_name": "Alice Smith",   "approval_status": "approved"},
            {"employee_id": "EMP002", "employee_name": "Bob Johnson",   "approval_status": "approved"},
            {"employee_id": "EMP003", "employee_name": "Charlie Brown", "approval_status": "pending"},
            {"employee_id": "EMP004", "employee_name": "Diana Prince",  "approval_status": "approved"},
            {"employee_id": "EMP005", "employee_name": "Eve Wilson",    "approval_status": "rejected"}
        ]
    }
    INITIAL_SYS = {
        "system_access": [
            {"employee_id": "EMP001", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP001", "system_name": "CRM",          "status": "active"},
            {"employee_id": "EMP002", "system_name": "CRM",          "status": "active"},
            {"employee_id": "EMP003", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP004", "system_name": "Admin Portal", "status": "inactive"},
            {"employee_id": "EMP005", "system_name": "CRM",          "status": "active"},
            {"employee_id": "EMP999", "system_name": "Admin Portal", "status": "active"}
        ]
    }
    INITIAL_EQP = {
        "equipment_assignments": [
            {"employee_id": "EMP001", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "EMP002", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "EMP003", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "EMP004", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "EMP005", "asset_tag": "LT-2041", "status": "assigned"}
        ]
    }

    # Approved employee IDs
    approved_ids = {e["employee_id"] for e in INITIAL_EXIT["exit_requests"] if e["approval_status"] == "approved"}

    # Read current state
    try:
        with open("data/offboarding/system_access.json") as f:
            current_sys = json.load(f)["system_access"]
        with open("data/offboarding/equipment_assignments.json") as f:
            current_eqp = json.load(f)["equipment_assignments"]
    except Exception:
        results.append({"item": "System/equipment files readable", "score": 0, "max_score": 40, "passed": False, "reason": "Cannot parse system_access or equipment_assignments."})
        # skip remaining checks for this section
        total_score = sum(r["score"] for r in results)
        write_score(total_score, results)
        return

    # ---- System access checks (20 pts) ----
    sys_correct = True
    sys_fail_reason = ""
    for rec in INITIAL_SYS["system_access"]:
        eid = rec["employee_id"]
        sys_name = rec["system_name"]
        # find corresponding record in current file
        matches = [c for c in current_sys if c["employee_id"] == eid and c["system_name"] == sys_name]
        if len(matches) != 1:
            sys_correct = False
            sys_fail_reason = f"Record for {eid}/{sys_name} missing or duplicated."
            break
        curr = matches[0]
        if eid in approved_ids:
            expected_status = "REVOKED"
        else:
            expected_status = rec["status"]  # should remain unchanged
        if curr["status"] != expected_status:
            sys_correct = False
            sys_fail_reason = f"Employee {eid} system {sys_name}: expected '{expected_status}', got '{curr['status']}'."
            break
    if sys_correct:
        results.append({"item": "System access revocation correct", "score": 20, "max_score": 20, "passed": True, "reason": "All approved employees have status REVOKED; others unchanged."})
    else:
        results.append({"item": "System access revocation correct", "score": 0, "max_score": 20, "passed": False, "reason": sys_fail_reason})

    # ---- Equipment checks (20 pts) ----
    eq_correct = True
    eq_fail_reason = ""
    for rec in INITIAL_EQP["equipment_assignments"]:
        eid = rec["employee_id"]
        tag = rec["asset_tag"]
        matches = [c for c in current_eqp if c["employee_id"] == eid and c["asset_tag"] == tag]
        if len(matches) != 1:
            eq_correct = False
            eq_fail_reason = f"Equipment record for {eid}/{tag} missing or duplicated."
            break
        curr = matches[0]
        if eid in approved_ids:
            expected_status = "RECLAIMED"
        else:
            expected_status = rec["status"]
        if curr["status"] != expected_status:
            eq_correct = False
            eq_fail_reason = f"Employee {eid} equipment {tag}: expected '{expected_status}', got '{curr['status']}'."
            break
    if eq_correct:
        results.append({"item": "Equipment reclaim correct", "score": 20, "max_score": 20, "passed": True, "reason": "All approved employees have status RECLAIMED; others unchanged."})
    else:
        results.append({"item": "Equipment reclaim correct", "score": 0, "max_score": 20, "passed": False, "reason": eq_fail_reason})

    # ------------------------------------------------------------------
    # 4. Handover checklist (45 pts: existence 5, schema 5, counts 35)
    # ------------------------------------------------------------------
    try:
        with open("handover_checklist.json") as f:
            checklist = json.load(f)
    except Exception as e:
        results.append({"item": "Handover checklist readable", "score": 0, "max_score": 5, "passed": False, "reason": f"Cannot read/parse handover_checklist.json: {e}"})
        # remaining parts get 0
        for item_label, max_pts in [("Checklist schema", 5), ("Checklist counts correct", 35)]:
            results.append({"item": item_label, "score": 0, "max_score": max_pts, "passed": False, "reason": "Checklist missing."})
    else:
        # Schema: should be a list of dicts with required keys
        schema_ok = True
        schema_reason = ""
        if not isinstance(checklist, list):
            schema_ok = False
            schema_reason = "Top-level should be a list."
        else:
            required_keys = {"employee_id", "employee_name", "system_revoked_count", "equipment_reclaimed_count", "completion_time"}
            for entry in checklist:
                if not isinstance(entry, dict):
                    schema_ok = False
                    schema_reason = "Each entry must be a dict."
                    break
                missing_keys = required_keys - set(entry.keys())
                if missing_keys:
                    schema_ok = False
                    schema_reason = f"Entry missing keys: {missing_keys}"
                    break
                # check types
                if not isinstance(entry.get("employee_id"), str) or not isinstance(entry.get("employee_name"), str):
                    schema_ok = False
                    schema_reason = "employee_id and employee_name must be strings."
                    break
                if not isinstance(entry.get("system_revoked_count"), int) or not isinstance(entry.get("equipment_reclaimed_count"), int):
                    schema_ok = False
                    schema_reason = "Counts must be integers."
                    break
                if not isinstance(entry.get("completion_time"), str) or not entry["completion_time"].strip():
                    schema_ok = False
                    schema_reason = "completion_time must be a non-empty string."
                    break
        if schema_ok:
            results.append({"item": "Checklist schema", "score": 5, "max_score": 5, "passed": True, "reason": "All entries have required fields with correct types."})
        else:
            results.append({"item": "Checklist schema", "score": 0, "max_score": 5, "passed": False, "reason": schema_reason})

        # Counts verification (35 pts)
        if not schema_ok:
            results.append({"item": "Checklist counts correct", "score": 0, "max_score": 35, "passed": False, "reason": "Schema invalid, cannot verify counts."})
        else:
            # Build expected counts from ground truth
            expected_counts = {}
            for eid in approved_ids:
                sys_count = sum(1 for rec in INITIAL_SYS["system_access"] if rec["employee_id"] == eid)
                eq_count = sum(1 for rec in INITIAL_EQP["equipment_assignments"] if rec["employee_id"] == eid)
                name = [e["employee_name"] for e in INITIAL_EXIT["exit_requests"] if e["employee_id"] == eid][0]
                expected_counts[eid] = {"employee_name": name, "system_revoked_count": sys_count, "equipment_reclaimed_count": eq_count}

            counts_ok = True
            counts_reason = ""
            # Check that exactly 3 entries
            if len(checklist) != len(expected_counts):
                counts_ok = False
                counts_reason = f"Expected {len(expected_counts)} entries, got {len(checklist)}."
            else:
                for entry in checklist:
                    eid = entry["employee_id"]
                    if eid not in expected_counts:
                        counts_ok = False
                        counts_reason = f"Unexpected employee {eid} in checklist."
                        break
                    exp = expected_counts[eid]
                    if entry["employee_name"] != exp["employee_name"]:
                        counts_ok = False
                        counts_reason = f"Employee {eid} name mismatch: expected '{exp['employee_name']}', got '{entry['employee_name']}'."
                        break
                    if entry["system_revoked_count"] != exp["system_revoked_count"]:
                        counts_ok = False
                        counts_reason = f"Employee {eid} system count: expected {exp['system_revoked_count']}, got {entry['system_revoked_count']}."
                        break
                    if entry["equipment_reclaimed_count"] != exp["equipment_reclaimed_count"]:
                        counts_ok = False
                        counts_reason = f"Employee {eid} equipment count: expected {exp['equipment_reclaimed_count']}, got {entry['equipment_reclaimed_count']}."
                        break
                if counts_ok:
                    results.append({"item": "Checklist counts correct", "score": 35, "max_score": 35, "passed": True, "reason": "All entries match expected counts for approved employees."})
                else:
                    results.append({"item": "Checklist counts correct", "score": 0, "max_score": 35, "passed": False, "reason": counts_reason})

    # ------------------------------------------------------------------
    # 5. Bonus: exit_requests.json should not be modified (0 pts, but reason)
    # ------------------------------------------------------------------
    try:
        with open("data/offboarding/exit_requests.json") as f:
            current_exit = json.load(f)
        if current_exit == INITIAL_EXIT:
            results.append({"item": "Exit requests untouched", "score": 0, "max_score": 0, "passed": True, "reason": "File not modified."})
        else:
            results.append({"item": "Exit requests untouched", "score": 0, "max_score": 0, "passed": False, "reason": "File was modified (not required but noted)."})
    except:
        results.append({"item": "Exit requests untouched", "score": 0, "max_score": 0, "passed": False, "reason": "Cannot read exit_requests.json"})

    # ------------------------------------------------------------------
    # 6. Distractor files (pending_requests.json) should not be created/modified (0 pts, informational)
    # ------------------------------------------------------------------
    if os.path.isfile("data/offboarding/pending_requests.json"):
        results.append({"item": "Pending requests file untouched", "score": 0, "max_score": 0, "passed": True, "reason": "Distractor file present and presumably untouched."})
    else:
        results.append({"item": "Pending requests file untouched", "score": 0, "max_score": 0, "passed": False, "reason": "pending_requests.json missing? (should still exist)"})

    # ------------------------------------------------------------------
    # Compute total (max 100)
    # ------------------------------------------------------------------
    total_score = sum(r["score"] for r in results)
    write_score(total_score, results)

def write_score(total, details):
    output = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
