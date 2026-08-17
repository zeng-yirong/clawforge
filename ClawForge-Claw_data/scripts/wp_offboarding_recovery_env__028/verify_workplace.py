"""
Verification script for offboarding recovery environment task.
Checks that agent produced the correct handover checklist.
"""
import sys
import os
import json

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def build_expected_checklist(exit_req_path, sys_access_path, equip_path):
    """Based on input data, compute the expected actions for each approved employee."""
    er = load_json(exit_req_path)["exit_requests"]
    sa = load_json(sys_access_path)["system_access"]
    eq = load_json(equip_path)["equipment_assignments"]

    # Build maps for quick lookup
    sys_map = {}  # employee_id -> list of system records
    for rec in sa:
        eid = rec["employee_id"]
        sys_map.setdefault(eid, []).append(rec)

    eq_map = {}  # employee_id -> list of equipment records
    for rec in eq:
        eid = rec["employee_id"]
        eq_map.setdefault(eid, []).append(rec)

    # Only approved employees
    approved_ids = {r["employee_id"] for r in er if r["approval_status"] == "approved"}

    expected = []
    for eid in sorted(approved_ids):
        actions = []
        # Revoke active system access
        if eid in sys_map:
            for rec in sys_map[eid]:
                if rec["status"] == "active":
                    actions.append(f"revoke_access:{rec['system_name']}")
        # Reclaim assigned equipment
        if eid in eq_map:
            for rec in eq_map[eid]:
                if rec["status"] == "assigned":
                    actions.append(f"reclaim_equipment:{rec['asset_tag']}")
        if actions:
            expected.append({"employee_id": eid, "actions": sorted(actions)})
    return sorted(expected, key=lambda x: x["employee_id"])

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. Check ops directory exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    dir_ok = os.path.isdir(ops_dir)
    details.append({
        "item": "ops/ directory exists",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "" if dir_ok else "Missing ops/ directory in workspace root."
    })
    if not dir_ok:
        # No point checking further
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        print(f"Total: {total}/100")
        sys.exit(0)

    # 2. Check file exists and is valid JSON (10 points)
    checklist_path = os.path.join(workspace, "ops", "handover_checklist.json")
    file_ok = os.path.isfile(checklist_path)
    json_ok = False
    agent_data = None
    if file_ok:
        try:
            agent_data = load_json(checklist_path)
            json_ok = True
        except (json.JSONDecodeError, Exception):
            json_ok = False
    fscore = 10 if file_ok and json_ok else (5 if file_ok else 0)
    details.append({
        "item": "ops/handover_checklist.json exists and valid JSON",
        "score": fscore,
        "max_score": 10,
        "passed": (file_ok and json_ok),
        "reason": "OK" if (file_ok and json_ok) else ("File missing" if not file_ok else "Invalid JSON content")
    })

    if not json_ok:
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        print(f"Total: {total}/100")
        sys.exit(0)

    # 3. Validate structure of agent's output – must be a list of objects with employee_id and actions (10 points)
    struct_ok = isinstance(agent_data, list) and all(
        isinstance(e, dict) and "employee_id" in e and "actions" in e and isinstance(e["actions"], list)
        for e in agent_data
    )
    details.append({
        "item": "Output is list of {employee_id, actions} objects",
        "score": 10 if struct_ok else 0,
        "max_score": 10,
        "passed": struct_ok,
        "reason": "OK" if struct_ok else "Structure does not match expected schema."
    })
    if not struct_ok:
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        print(f"Total: {total}/100")
        sys.exit(0)

    # 4. Build expected checklist from original data (files in workspace)
    # Paths relative to workspace
    exit_req_path = os.path.join(workspace, "data/offboarding/exit_requests.json")
    sys_access_path = os.path.join(workspace, "data/offboarding/system_access.json")
    equip_path = os.path.join(workspace, "data/offboarding/equipment_assignments.json")
    try:
        expected = build_expected_checklist(exit_req_path, sys_access_path, equip_path)
    except Exception as e:
        # If original data missing, cannot score; treat as 0
        details.append({
            "item": "Matching against expected data",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": f"Could not read original data files: {e}"
        })
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        print(f"Total: {total}/100")
        sys.exit(0)

    # 5. Compare agent output to expected (70 points)
    # Normalize both: sort by employee_id, and actions sorted
    def normalize(lst):
        return sorted(
            [{"employee_id": e["employee_id"], "actions": sorted(e["actions"])} for e in lst],
            key=lambda x: x["employee_id"]
        )
    agent_norm = normalize(agent_data)
    expected_norm = expected  # already sorted

    match = (agent_norm == expected_norm)
    # If not match, compute penalty based on count of extra/missing elements
    penalty = 0
    if not match:
        # Compare sets of tuples (employee_id, frozenset actions) for simpler diff
        agent_set = set((e["employee_id"], frozenset(e["actions"])) for e in agent_norm)
        exp_set = set((e["employee_id"], frozenset(e["actions"])) for e in expected_norm)
        missing = exp_set - agent_set
        extra = agent_set - exp_set
        penalty = 10 * (len(missing) + len(extra))
        if penalty > 70:
            penalty = 70

    match_score = int((1 - (penalty/70)) * 70) if not match else 70
    reason_str = "Perfect match" if match else f"Missing {len(missing)} items, extra {len(extra)} items -> penalty {penalty}"
    details.append({
        "item": "Checklist content matches expected actions",
        "score": match_score,
        "max_score": 70,
        "passed": match,
        "reason": reason_str
    })

    total = sum(d["score"] for d in details)
    # Write result
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    print(f"Total: {total}/100")

if __name__ == "__main__":
    main()
