#!/usr/bin/env python3
import sys
import json
import os

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def find_key(obj, keys):
    for k in keys:
        if k in obj:
            return obj[k]
    return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ops_task_file = os.path.join(workspace, "ops", "onboarding_tasks.json")
    contracts_file = os.path.join(workspace, "data", "onboarding", "contracts.json")
    packs_file = os.path.join(workspace, "data", "onboarding", "permission_packs.json")
    equip_file = os.path.join(workspace, "data", "onboarding", "equipment_inventory.json")

    details = []
    total_score = 0

    # --- 1. File exists and valid JSON (10 pts) ---
    if not os.path.exists(ops_task_file):
        details.append({"item": "ops/onboarding_tasks.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        result = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    try:
        with open(ops_task_file, 'r') as f:
            agent_output = json.load(f)
        details.append({"item": "ops/onboarding_tasks.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "File found and parsed"})
        total_score += 10
    except json.JSONDecodeError as e:
        details.append({"item": "ops/onboarding_tasks.json valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        result = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # --- Load reference data ---
    try:
        contracts_data = load_json(contracts_file)["contracts"]
        packs_data = load_json(packs_file)["permission_packs"]
        equip_data = load_json(equip_file)["equipment_inventory"]
    except Exception as e:
        details.append({"item": "Reference data load", "score": 0, "max_score": 0, "passed": False, "reason": f"Error loading reference: {e}"})
        result = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # --- Build expected tasks ---
    signed_contracts = [c for c in contracts_data if c["status"] == "signed"]
    signed_contracts.sort(key=lambda x: x["employee_id"])
    packs_dict = {p["pack_id"]: p["systems"] for p in packs_data}
    equip_by_dept = {}
    for eq in equip_data:
        if eq["status"] == "available":
            dept = eq["department"]
            equip_by_dept.setdefault(dept, []).append(eq["asset_tag"])

    expected_tasks = []
    for c in signed_contracts:
        dept = c["department"]
        systems = packs_dict.get(dept, [])
        equip_list = equip_by_dept.get(dept, [])
        equipment = equip_list[0] if equip_list else None
        expected_tasks.append({
            "employee_id": c["employee_id"],
            "email": c["email"],
            "system_access": systems,
            "equipment": equipment
        })

    # --- Parse agent output (flexible wrapping) ---
    if isinstance(agent_output, dict):
        if "tasks" in agent_output:
            agent_tasks = agent_output["tasks"]
        elif "onboarding_tasks" in agent_output:
            agent_tasks = agent_output["onboarding_tasks"]
        else:
            # find first list value
            agent_tasks = next((v for v in agent_output.values() if isinstance(v, list)), [])
    elif isinstance(agent_output, list):
        agent_tasks = agent_output
    else:
        agent_tasks = []

    # --- 2. Number of tasks (10 pts) ---
    expected_count = len(expected_tasks)
    agent_count = len(agent_tasks)
    if agent_count == expected_count:
        details.append({"item": "Number of tasks matches signed employees", "score": 10, "max_score": 10, "passed": True, "reason": f"Expected {expected_count}, got {agent_count}"})
        total_score += 10
    else:
        details.append({"item": "Number of tasks matches signed employees", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_count}, got {agent_count}"})

    # --- 3. Field-level checks (80 pts: 4 fields × 2 employees × 10 pts each) ---
    for exp in expected_tasks:
        matched_agent = None
        for agent_task in agent_tasks:
            agent_emp_id = find_key(agent_task, ["employee_id", "emp_id", "employeeId", "id"])
            if agent_emp_id == exp["employee_id"]:
                matched_agent = agent_task
                break

        if matched_agent is None:
            # all 4 fields fail for this employee
            details.append({"item": f"Employee {exp['employee_id']} - employee_id", "score": 0, "max_score": 10, "passed": False, "reason": "Employee not found in agent output"})
            details.append({"item": f"Employee {exp['employee_id']} - email", "score": 0, "max_score": 10, "passed": False, "reason": "Employee not found"})
            details.append({"item": f"Employee {exp['employee_id']} - system access", "score": 0, "max_score": 10, "passed": False, "reason": "Employee not found"})
            details.append({"item": f"Employee {exp['employee_id']} - equipment", "score": 0, "max_score": 10, "passed": False, "reason": "Employee not found"})
            continue

        # email
        agent_email = find_key(matched_agent, ["email"])
        if agent_email == exp["email"]:
            details.append({"item": f"Employee {exp['employee_id']} - email", "score": 10, "max_score": 10, "passed": True, "reason": f"Expected {exp['email']}, got {agent_email}"})
            total_score += 10
        else:
            details.append({"item": f"Employee {exp['employee_id']} - email", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {exp['email']}, got {agent_email}"})

        # system access
        agent_systems = find_key(matched_agent, ["system_access", "systems", "permissions", "access"])
        if isinstance(agent_systems, list) and sorted(agent_systems) == sorted(exp["system_access"]):
            details.append({"item": f"Employee {exp['employee_id']} - system access", "score": 10, "max_score": 10, "passed": True, "reason": f"Systems match"})
            total_score += 10
        else:
            details.append({"item": f"Employee {exp['employee_id']} - system access", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {exp['system_access']}, got {agent_systems}"})

        # equipment
        agent_equip = find_key(matched_agent, ["equipment", "asset_tag", "device", "assigned_equipment"])
        if agent_equip == exp["equipment"]:
            details.append({"item": f"Employee {exp['employee_id']} - equipment", "score": 10, "max_score": 10, "passed": True, "reason": f"Expected {exp['equipment']}, got {agent_equip}"})
            total_score += 10
        else:
            details.append({"item": f"Employee {exp['employee_id']} - equipment", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {exp['equipment']}, got {agent_equip}"})

    # --- Write final score ---
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
