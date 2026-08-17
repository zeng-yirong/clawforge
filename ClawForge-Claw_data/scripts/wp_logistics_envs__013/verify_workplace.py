import sys
import json
import os
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # Helper to add item
    def add_item(item_name, max_score, passed, reason):
        details.append({
            "item": item_name,
            "score": max_score if passed else 0,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return passed

    # 1. Directory structure: ops/ exists
    ops_dir = os.path.join(workspace, "ops")
    dir_ok = os.path.isdir(ops_dir)
    add_item("ops directory exists", 5, dir_ok, "" if dir_ok else "ops/ not found")

    # 2. File ops/task_resolutions.json exists
    result_path = os.path.join(ops_dir, "task_resolutions.json")
    file_ok = os.path.isfile(result_path)
    add_item("task_resolutions.json exists", 5, file_ok, "" if file_ok else "File not found")
    if not file_ok:
        # We still need to output a valid score structure
        write_score(details, workspace)
        return

    # 3. JSON validity and root structure
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        json_ok = True
    except Exception as e:
        json_ok = False
        reason = f"Invalid JSON: {e}"
    add_item("JSON parseable", 10, json_ok, "" if json_ok else reason)
    if not json_ok:
        write_score(details, workspace)
        return

    has_tasks = isinstance(data, dict) and "tasks" in data
    add_item("Root has 'tasks' key", 5, has_tasks, "" if has_tasks else "Missing 'tasks' key")
    if not has_tasks:
        write_score(details, workspace)
        return

    tasks = data["tasks"]
    is_array = isinstance(tasks, list)
    add_item("tasks is an array", 5, is_array, "" if is_array else "'tasks' is not a list")
    if not is_array:
        write_score(details, workspace)
        return

    # 4. Task count must be exactly 5
    expected_count = 5
    count_ok = len(tasks) == expected_count
    add_item("Exactly 5 tasks", 10, count_ok,
             f"Expected {expected_count}, found {len(tasks)}" if not count_ok else "")

    # 5. Check each required task type
    # Build a lookup by type
    by_type = {}
    for i, t in enumerate(tasks):
        if isinstance(t, dict) and "type" in t:
            by_type[t["type"]] = t
    required_types = ["approve_return", "inspect_return", "update_shipment", "adjust_inventory", "reconciliation_report"]

    for rtype in required_types:
        if rtype not in by_type:
            add_item(f"Task type '{rtype}' present", 3, False, "Missing required task type")
        else:
            add_item(f"Task type '{rtype}' present", 3, True, "")

    # Now detailed checks per type
    def check_approve_return(task):
        pts = 0
        detail = task.get("details", {})
        # return_id must be ret_001
        if detail.get("return_id") == "ret_001":
            pts += 2
        # must include 'defective' and 'approved' in some string field (case-insensitive)
        notes = str(detail.get("notes", "") + " " + detail.get("reason", "") + " " + detail.get("resolution", ""))
        has_defective = "defective" in notes.lower()
        has_approved = "approved" in notes.lower()
        if has_defective:
            pts += 2
        if has_approved:
            pts += 2
        # total 6 for this subtask, we split into 2+2+2 but we'll score as chunk
        return pts, f"return_id=ret_001({detail.get('return_id')}), defective={has_defective}, approved={has_approved}"

    def check_inspect_return(task):
        pts = 0
        detail = task.get("details", {})
        if detail.get("return_id") == "ret_003":
            pts += 2
        notes = str(detail.get("notes", "") + " " + detail.get("reason", "") + " " + detail.get("resolution", ""))
        has_wrong_item = "wrong item" in notes.lower()
        has_exchange = "exchange" in notes.lower()
        if has_wrong_item:
            pts += 2
        if has_exchange:
            pts += 2
        return pts, f"return_id=ret_003({detail.get('return_id')}), wrong item={has_wrong_item}, exchange={has_exchange}"

    def check_update_shipment(task):
        pts = 0
        detail = task.get("details", {})
        if detail.get("shipment_id") == "ship_005":
            pts += 2
        if detail.get("status") == "shipped":
            pts += 2
        notes = str(detail.get("notes", "") + " " + detail.get("carrier", "") + " " + detail.get("status", ""))
        has_shipped = "shipped" in notes.lower()
        has_fedex = "fedex" in notes.lower()
        if has_shipped:
            pts += 1
        if has_fedex:
            pts += 1
        return pts, f"shipment_id=ship_005({detail.get('shipment_id')}), status=shipped({detail.get('status')}), shipped_word={has_shipped}, fedex={has_fedex}"

    def check_adjust_inventory(task):
        pts = 0
        detail = task.get("details", {})
        if detail.get("sku") == "SKU-1002":
            pts += 2
        if detail.get("warehouse") == "wh_001":
            pts += 1
        if detail.get("quantity") == -5:
            pts += 2
        notes = str(detail.get("notes", "") + " " + detail.get("reason", "") + " " + detail.get("status", ""))
        has_damage = "damage" in notes.lower()
        has_adjusted = "adjusted" in notes.lower()
        if has_damage:
            pts += 1
        if has_adjusted:
            pts += 1
        return pts, f"sku=SKU-1002({detail.get('sku')}), warehouse=wh_001({detail.get('warehouse')}), quantity=-5({detail.get('quantity')}), damage={has_damage}, adjusted={has_adjusted}"

    def check_reconciliation(task):
        pts = 0
        detail = task.get("details", {})
        # Expect report_type or type field indicating inventory_reconciliation
        if detail.get("report_type") == "inventory_reconciliation":
            pts += 1
        # must contain 'reconciliation' and 'discrepancy' in any text field
        text = json.dumps(task).lower()
        has_reconciliation = "reconciliation" in text
        has_discrepancy = "discrepancy" in text
        if has_reconciliation:
            pts += 2
        if has_discrepancy:
            pts += 2
        return pts, f"report_type=inventory_reconciliation({detail.get('report_type')}), reconciliation={has_reconciliation}, discrepancy={has_discrepancy}"

    check_functions = {
        "approve_return": (check_approve_return, 6),
        "inspect_return": (check_inspect_return, 6),
        "update_shipment": (check_update_shipment, 6),
        "adjust_inventory": (check_adjust_inventory, 6),
        "reconciliation_report": (check_reconciliation, 5),
    }

    for rtype, (func, max_pts) in check_functions.items():
        if rtype in by_type:
            actual_pts, reason = func(by_type[rtype])
            passed = actual_pts >= max_pts
            add_item(f"Task '{rtype}' detail check", max_pts, passed,
                     f"scored {actual_pts}/{max_pts}: {reason}" if not passed else "")
        else:
            add_item(f"Task '{rtype}' detail check", max_pts, False, "Task not present, details skipped")

    # Compute total score from details
    total = sum(d["score"] for d in details)
    # Clamp to 100
    total = min(total, 100)

    # Write score
    write_score(details, workspace, total_score=total)

def write_score(details, workspace, total_score=None):
    if total_score is None:
        total_score = sum(d["score"] for d in details)
        total_score = min(total_score, 100)
    score_obj = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(score_obj, f, indent=2)

if __name__ == "__main__":
    verify()
