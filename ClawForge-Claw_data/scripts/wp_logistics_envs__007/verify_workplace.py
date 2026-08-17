import sys
import os
import json

def find_action(actions, action_types, target_key, target_value):
    """Find first action matching any of the given action_types and target_key==target_value."""
    for act in actions:
        if not isinstance(act, dict):
            continue
        # determine action type
        action_type = act.get("action") or act.get("type") or act.get("operation") or ""
        if isinstance(action_type, str) and action_type.lower() in [t.lower() for t in action_types]:
            # check target
            target = act.get("target") or act.get(target_key) or act.get("id") or act.get("return_id") or act.get("shipment_id") or act.get("sku") or ""
            if str(target) == str(target_value):
                return act
    return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0
    max_total = 100

    # --- 1. Existence of ops/action_plan.json (10 pts) ---
    plan_path = os.path.join(workspace, "ops", "action_plan.json")
    if os.path.isfile(plan_path):
        details.append({"item": "File ops/action_plan.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
        total += 10
    else:
        details.append({"item": "File ops/action_plan.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found."})
        # Cannot proceed, but still collect other checks with 0
        # For remaining checks, assume empty
        actions = []
    # --- 2. Parse JSON (10 pts) ---
    if os.path.isfile(plan_path):
        try:
            with open(plan_path, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                actions = data
            elif isinstance(data, dict):
                actions = data.get("actions", data.get("items", []))
            else:
                actions = []
            details.append({"item": "JSON is valid and contains actions list", "score": 10, "max_score": 10, "passed": True, "reason": f"Parsed actions count: {len(actions)}"})
            total += 10
        except Exception as e:
            details.append({"item": "JSON is valid and contains actions list", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {str(e)}"})
            actions = []
    else:
        details.append({"item": "JSON is valid and contains actions list", "score": 0, "max_score": 10, "passed": False, "reason": "File missing."})
        actions = []

    # --- 3. Check each required operation (20 pts each, total 80) ---
    # 3a. Approve return ret_001 (20 pts)
    act_approve = find_action(actions,
                              action_types=["approve_return", "approve", "approv_return", "approve_return"],
                              target_key="return_id", target_value="ret_001")
    if act_approve:
        pts = 20
        # Check required fields or values
        status = act_approve.get("status") or act_approve.get("resolution") or act_approve.get("new_status") or ""
        # Expected: status/resolution should be "approved", "refund_approved" or contain "approv"
        if "approv" in status.lower() or "refund" in status.lower():
            pts = 20
        else:
            pts -= 5  # partly correct
        details.append({"item": "Approve return ret_001", "score": pts, "max_score": 20, "passed": pts == 20,
                        "reason": f"Action found, status/resolution: {status}"})
        total += pts
    else:
        details.append({"item": "Approve return ret_001", "score": 0, "max_score": 20, "passed": False, "reason": "No matching action found for ret_001"})

    # 3b. Inspect return ret_003 (20 pts)
    act_inspect = find_action(actions,
                              action_types=["inspect_return", "inspect", "inspect_return", "inspect_item"],
                              target_key="return_id", target_value="ret_003")
    if act_inspect:
        pts = 20
        status = act_inspect.get("status") or act_inspect.get("resolution") or act_inspect.get("new_status") or ""
        # Expected inspection leads to exchange; status might be "pending_inspection" or resolution "exchange"
        if "inspect" in status.lower() or "exchange" in status.lower() or "pending" in status.lower():
            pts = 20
        else:
            pts -= 5
        details.append({"item": "Inspect return ret_003", "score": pts, "max_score": 20, "passed": pts == 20,
                        "reason": f"Action found, status/resolution: {status}"})
        total += pts
    else:
        details.append({"item": "Inspect return ret_003", "score": 0, "max_score": 20, "passed": False, "reason": "No matching action found for ret_003"})

    # 3c. Update shipment ship_005 to shipped with FedEx (20 pts)
    act_ship = find_action(actions,
                           action_types=["update_shipment", "update_shipment_status", "update", "ship"],
                           target_key="shipment_id", target_value="ship_005")
    if act_ship:
        pts = 20
        status = act_ship.get("status") or act_ship.get("new_status") or ""
        carrier = act_ship.get("carrier") or act_ship.get("carrier_name") or act_ship.get("courier") or ""
        # must be "shipped" and carrier "FedEx"
        if "shipped" in status.lower() and "fedex" in carrier.lower():
            pts = 20
        elif "shipped" in status.lower():
            pts = 12  # status correct but carrier missing/wrong
        elif "fedex" in carrier.lower():
            pts = 12  # carrier correct but status not shipped
        else:
            pts = 5   # action present but both wrong
        details.append({"item": "Update shipment ship_005 to shipped with FedEx", "score": pts, "max_score": 20, "passed": (pts == 20),
                        "reason": f"Action found, status: {status}, carrier: {carrier}"})
        total += pts
    else:
        details.append({"item": "Update shipment ship_005 to shipped with FedEx", "score": 0, "max_score": 20, "passed": False, "reason": "No matching action found for ship_005"})

    # 3d. Adjust inventory SKU-1002 by -5 damage (20 pts)
    act_inv = find_action(actions,
                          action_types=["adjust_inventory", "adjust", "inventory_adjust", "damage_adjust"],
                          target_key="sku", target_value="SKU-1002")
    if act_inv:
        pts = 20
        change = act_inv.get("change") or act_inv.get("quantity_change") or act_inv.get("adjustment") or act_inv.get("qty") or 0
        warehouse = act_inv.get("warehouse") or act_inv.get("warehouse_id") or ""
        reason = act_inv.get("reason") or act_inv.get("note") or ""
        # Expected: change = -5 (or 5 with sign), warehouse wh_001, reason contains "damage"
        change_ok = False
        if isinstance(change, (int, float)):
            if change == -5 or change == 5:
                change_ok = True
        elif isinstance(change, str):
            try:
                val = int(change)
                if val == -5 or val == 5:
                    change_ok = True
            except:
                pass
        wh_ok = "wh_001" in warehouse
        reason_ok = "damage" in reason.lower()
        if change_ok and wh_ok and reason_ok:
            pts = 20
        elif change_ok and wh_ok:
            pts = 15
        elif change_ok:
            pts = 10
        else:
            pts = 5
        details.append({"item": "Adjust inventory SKU-1002 by -5 damage", "score": pts, "max_score": 20, "passed": (pts == 20),
                        "reason": f"Action found, change: {change}, warehouse: {warehouse}, reason: {reason}"})
        total += pts
    else:
        details.append({"item": "Adjust inventory SKU-1002 by -5 damage", "score": 0, "max_score": 20, "passed": False, "reason": "No matching action found for SKU-1002"})

    # --- Write score file ---
    total = min(total, max_total)
    result = {"total_score": total, "details": details}
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/{max_total}")
    sys.exit(0 if total == max_total else 1)

if __name__ == "__main__":
    main()
