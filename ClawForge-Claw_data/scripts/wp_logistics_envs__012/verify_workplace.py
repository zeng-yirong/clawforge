import sys, os, json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def run_verify():
    details = []
    total = 0

    # 1. Directory and file existence (10 points)
    ops_dir = os.path.join(workspace, "ops")
    plan_path = os.path.join(ops_dir, "action_plan.json")
    if os.path.isdir(ops_dir) and os.path.isfile(plan_path):
        details.append({
            "item": "ops/action_plan.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found"
        })
        total += 10
    else:
        details.append({
            "item": "ops/action_plan.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing file or directory"
        })
        write_score(total, details)
        return

    # 2. JSON format (10 points)
    with open(plan_path, "r") as f:
        content = f.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        details.append({
            "item": "Valid JSON format",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        write_score(total, details)
        return

    if isinstance(data, dict) and "actions" in data and isinstance(data["actions"], list):
        details.append({
            "item": "JSON structure contains actions array",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid structure"
        })
        total += 10
    else:
        details.append({
            "item": "JSON structure contains actions array",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing or invalid actions array"
        })
        # Still try to get actions if possible
        actions = data.get("actions", []) if isinstance(data, dict) else []
    actions = data.get("actions", []) if isinstance(data, dict) else []

    # 3. Four expected actions (20 points each, 80 total)
    expected = [
        {
            "action": "approve_return",
            "target": "ret_001",
            "params": {"resolution": "refund_approved"}
        },
        {
            "action": "inspect_return",
            "target": "ret_003",
            "params": {"resolution": "exchange"}
        },
        {
            "action": "update_shipment_status",
            "target": "ship_005",
            "params": {"new_status": "shipped"}
        },
        {
            "action": "adjust_inventory",
            "target": "SKU-1002",
            "params": {"warehouse": "wh_001", "change": -5, "reason": "damage"}
        }
    ]

    for exp in expected:
        found = False
        for act in actions:
            if not isinstance(act, dict):
                continue
            if act.get("action") == exp["action"] and act.get("target") == exp["target"]:
                params = act.get("params", {})
                if isinstance(params, dict) and all(params.get(k) == v for k, v in exp["params"].items()):
                    found = True
                    break
        if found:
            details.append({
                "item": f"Action '{exp['action']}' for {exp['target']}",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "Correct"
            })
            total += 20
        else:
            details.append({
                "item": f"Action '{exp['action']}' for {exp['target']}",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Missing or incorrect parameters"
            })

    write_score(total, details, workspace)

def write_score(total, details, workspace="."):
    out = {
        "total_score": min(total, 100),
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    run_verify()
