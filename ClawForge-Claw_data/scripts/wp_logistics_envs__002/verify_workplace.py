import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查目录结构：ops/ 存在
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    score_details.append({
        "item": "Directory ops/ exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops/ directory found" if dir_exists else "ops/ directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 ops/pending_actions.json 存在且合法 JSON
    json_path = os.path.join(ops_path, "pending_actions.json")
    file_exists = os.path.isfile(json_path)
    json_parsed = None
    if file_exists:
        try:
            with open(json_path, "r") as f:
                json_parsed = json.load(f)
            json_valid = True
        except (json.JSONDecodeError, Exception):
            json_valid = False
    else:
        json_valid = False

    score_details.append({
        "item": "ops/pending_actions.json exists and is valid JSON",
        "score": 10 if file_exists and json_valid else 0,
        "max_score": 10,
        "passed": file_exists and json_valid,
        "reason": "File valid" if file_exists and json_valid else
                  ("File not found" if not file_exists else "Invalid JSON")
    })
    if file_exists and json_valid:
        total_score += 10

    if not json_parsed or not isinstance(json_parsed, dict):
        # 后续评分无法进行，直接输出
        score_details.append({"item": "Overall (no further checks)", "score": 0, "max_score": 80, "passed": False, "reason": "Missing or invalid root object"})
        total_score = min(total_score, 100)
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 检查必需顶层键存在
    required_keys = ["returns_actions", "shipments_actions", "inventory_actions", "reconciliation"]
    missing_keys = [k for k in required_keys if k not in json_parsed]
    if missing_keys:
        score_details.append({
            "item": "Top-level keys present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing keys: {missing_keys}"
        })
        total_score = min(total_score + 0, 100)
    else:
        score_details.append({
            "item": "Top-level keys present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All required keys found"
        })
        total_score += 10

    # 3. Returns actions
    ret_actions = json_parsed.get("returns_actions", [])
    ret_score = 0
    ret_max = 30
    ret_reason = ""
    # 检查两个必需退货条目
    found_ret = {}
    for act in ret_actions:
        rid = act.get("return_id")
        if rid == "ret_001":
            found_ret["ret_001"] = act
        elif rid == "ret_003":
            found_ret["ret_003"] = act

    if "ret_001" in found_ret:
        act001 = found_ret["ret_001"]
        # 必须包含 action 字段值为 "approve" 和 status 字段值为 "approved"
        if act001.get("action") == "approve" and act001.get("status") == "approved":
            ret_score += 15
            ret_reason += "ret_001 correctly approved; "
        else:
            ret_reason += "ret_001 action/status mismatch; "
    else:
        ret_reason += "ret_001 missing; "

    if "ret_003" in found_ret:
        act003 = found_ret["ret_003"]
        # 必须包含 action="inspect", resolution="exchange"
        if act003.get("action") == "inspect" and act003.get("resolution") == "exchange":
            ret_score += 15
            ret_reason += "ret_003 correctly inspected; "
        else:
            ret_reason += "ret_003 action/resolution mismatch; "
    else:
        ret_reason += "ret_003 missing; "

    # 检查没有多余退货条目 (ret_002, ret_004 等不应出现) — 宽松，不扣分，但作为提示
    extra_ret_ids = [a["return_id"] for a in ret_actions if a.get("return_id") not in ("ret_001", "ret_003")]
    if extra_ret_ids:
        ret_reason += f"Unexpected returns: {extra_ret_ids}; "
    # 如果没有错误，ret_reason 可能为空
    if not ret_reason:
        ret_reason = "All return actions correct"
    score_details.append({
        "item": "Returns actions correctness",
        "score": ret_score,
        "max_score": ret_max,
        "passed": ret_score == ret_max,
        "reason": ret_reason.strip().rstrip("; ") if ret_reason else ""
    })
    total_score += ret_score

    # 4. Shipments actions
    ship_actions = json_parsed.get("shipments_actions", [])
    ship_score = 0
    ship_max = 20
    ship_reason = ""
    found_ship = None
    for act in ship_actions:
        if act.get("shipment_id") == "ship_005":
            found_ship = act
            break
    if found_ship:
        if found_ship.get("status") == "shipped" and found_ship.get("carrier") == "FedEx":
            ship_score = 20
            ship_reason = "ship_005 correctly updated to shipped"
        else:
            ship_reason = f"ship_005 status={found_ship.get('status')}, carrier={found_ship.get('carrier')} (expected shipped/FedEx)"
    else:
        ship_reason = "ship_005 not found"
    # 检查多余
    extra_ship_ids = [a["shipment_id"] for a in ship_actions if a.get("shipment_id") not in ("ship_005",)]
    if extra_ship_ids:
        ship_reason += f"; Unexpected shipments: {extra_ship_ids}"
    score_details.append({
        "item": "Shipments action correctness",
        "score": ship_score,
        "max_score": ship_max,
        "passed": ship_score == ship_max,
        "reason": ship_reason
    })
    total_score += ship_score

    # 5. Inventory actions
    inv_actions = json_parsed.get("inventory_actions", [])
    inv_score = 0
    inv_max = 20
    inv_reason = ""
    found_inv = None
    for act in inv_actions:
        if act.get("sku") == "SKU-1002" and act.get("warehouse_id") == "wh_001":
            found_inv = act
            break
    if found_inv:
        if found_inv.get("adjustment_type") == "damage" and found_inv.get("quantity_change") == -5:
            inv_score = 20
            inv_reason = "SKU-1002 correctly adjusted: damage, -5"
        else:
            inv_reason = f"SKU-1002 adjustment: type={found_inv.get('adjustment_type')}, qty={found_inv.get('quantity_change')}"
    else:
        inv_reason = "SKU-1002 (wh_001) not found"
    extra_inv = [a["sku"] for a in inv_actions if not (a.get("sku")=="SKU-1002" and a.get("warehouse_id")=="wh_001")]
    if extra_inv:
        inv_reason += f"; Unexpected inventory adjustments: {extra_inv}"
    score_details.append({
        "item": "Inventory action correctness",
        "score": inv_score,
        "max_score": inv_max,
        "passed": inv_score == inv_max,
        "reason": inv_reason
    })
    total_score += inv_score

    # 6. Reconciliation report
    reconc = json_parsed.get("reconciliation", {})
    reconc_score = 0
    reconc_max = 10
    reconc_reason = ""
    # 预期数值: total_refund=49.99, total_inventory_adjustment=-125.00, net_discrepancy=-75.01
    expected_refund = 49.99
    expected_inv_adj = -125.00  # -5 * 25.00
    expected_net = -75.01
    # 允许浮点精度误差 0.01
    actual_refund = reconc.get("total_refund")
    actual_inv_adj = reconc.get("total_inventory_adjustment")
    actual_net = reconc.get("net_discrepancy")
    refund_ok = isinstance(actual_refund, (int, float)) and abs(actual_refund - expected_refund) <= 0.01
    inv_adj_ok = isinstance(actual_inv_adj, (int, float)) and abs(actual_inv_adj - expected_inv_adj) <= 0.01
    net_ok = isinstance(actual_net, (int, float)) and abs(actual_net - expected_net) <= 0.01
    if refund_ok and inv_adj_ok and net_ok:
        reconc_score = 10
        reconc_reason = "Reconciliation numbers match expected"
    else:
        reconc_reason = f"Expected refund={expected_refund}, inv_adj={expected_inv_adj}, net={expected_net}; got refund={actual_refund}, inv_adj={actual_inv_adj}, net={actual_net}"
    score_details.append({
        "item": "Reconciliation report correctness",
        "score": reconc_score,
        "max_score": reconc_max,
        "passed": reconc_score == reconc_max,
        "reason": reconc_reason
    })
    total_score += reconc_score

    # 确保总分不超过 100
    total_score = min(total_score, 100)

    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
