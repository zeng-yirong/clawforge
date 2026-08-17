import sys
import json
import os
from pathlib import Path

def verify(workspace):
    errors = []
    scores = []
    total_score = 0

    def add_item(name, score, max_score, passed, reason):
        scores.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        nonlocal total_score
        total_score += score

    # ---- 1. 目录存在性 (10分) ----
    ops_dir = Path(workspace) / "ops"
    reports_dir = Path(workspace) / "reports"
    if ops_dir.is_dir():
        add_item("ops/ 目录存在", 5, 5, True, "目录已创建")
    else:
        add_item("ops/ 目录存在", 0, 5, False, "缺少 ops/ 目录")
    if reports_dir.is_dir():
        add_item("reports/ 目录存在", 5, 5, True, "目录已创建")
    else:
        add_item("reports/ 目录存在", 0, 5, False, "缺少 reports/ 目录")

    # ---- 2. 文件存在性 (20分) ----
    dispatch_path = ops_dir / "dispatch.json"
    reconciliation_path = reports_dir / "reconciliation.json"
    if dispatch_path.is_file():
        add_item("ops/dispatch.json 存在", 10, 10, True, "文件存在")
    else:
        add_item("ops/dispatch.json 存在", 0, 10, False, "文件缺失")
    if reconciliation_path.is_file():
        add_item("reports/reconciliation.json 存在", 10, 10, True, "文件存在")
    else:
        add_item("reports/reconciliation.json 存在", 0, 10, False, "文件缺失")
        # 后续检查跳过
        return _finish(scores, total_score)

    # ---- 3. dispatch.json 内容检查 (35分) ----
    try:
        with open(dispatch_path) as f:
            dispatch = json.load(f)
    except Exception as e:
        add_item("dispatch.json 解析", 0, 35, False, f"JSON解析失败: {e}")
        return _finish(scores, total_score)

    if not isinstance(dispatch, list):
        add_item("dispatch.json 是数组", 0, 35, False, "根元素不是数组")
        return _finish(scores, total_score)

    add_item("dispatch.json 是数组", 5, 5, True, "根元素为数组长度{}".format(len(dispatch)))
    if len(dispatch) < 4:
        add_item("dispatch.json 最少4个操作", 0, 5, False, f"实际长度{len(dispatch)}")
    elif len(dispatch) > 4:
        add_item("dispatch.json 恰好4个操作", 3, 5, True, f"实际长度{len(dispatch)} (额外项不扣分)")
    else:
        add_item("dispatch.json 恰好4个操作", 5, 5, True, "共4个操作")

    # 定义预期操作
    expected_ops = [
        {"action": "approve_return", "return_id": "ret_001", "reason": "defective", "resolution": "refund_approved"},
        {"action": "inspect_return", "return_id": "ret_003", "reason": "wrong item", "expected_resolution": "exchange"},
        {"action": "update_shipment_status", "shipment_id": "ship_005", "new_status": "shipped", "carrier": "FedEx"},
        {"action": "adjust_inventory", "sku": "SKU-1002", "warehouse_id": "wh_001", "adjustment_type": "damage", "quantity_change": -5}
    ]

    # 为简化验证，我们使用集合匹配，但保留顺序不要求完全一致
    matched = [False] * 4
    for op in dispatch:
        op_action = op.get("action")
        idx = None
        for i, e in enumerate(expected_ops):
            if e["action"] == op_action and not matched[i]:
                # 进一步验证ID字段
                if op_action == "approve_return":
                    if op.get("return_id") == e["return_id"]:
                        idx = i
                elif op_action == "inspect_return":
                    if op.get("return_id") == e["return_id"]:
                        idx = i
                elif op_action == "update_shipment_status":
                    if op.get("shipment_id") == e["shipment_id"]:
                        idx = i
                elif op_action == "adjust_inventory":
                    if op.get("sku") == e["sku"] and op.get("warehouse_id") == e["warehouse_id"]:
                        idx = i
        if idx is not None:
            matched[idx] = True

    # 检查每个操作是否被匹配
    action_score_per = 3  # 每个action类型及ID正确给3分
    detail_score_per = 4  # 每个操作额外字段给4分
    for i, e in enumerate(expected_ops):
        if matched[i]:
            add_item(f"操作'{e['action']}' ID正确", action_score_per, action_score_per, True, "匹配")
            # 检查额外字段
            actual_op = None
            for op in dispatch:
                if op.get("action") == e["action"]:
                    # 根据action类型判断
                    if e["action"] == "approve_return" and op.get("return_id") == e["return_id"]:
                        actual_op = op
                        break
                    elif e["action"] == "inspect_return" and op.get("return_id") == e["return_id"]:
                        actual_op = op
                        break
                    elif e["action"] == "update_shipment_status" and op.get("shipment_id") == e["shipment_id"]:
                        actual_op = op
                        break
                    elif e["action"] == "adjust_inventory" and op.get("sku") == e["sku"]:
                        actual_op = op
                        break
            if actual_op:
                extra_ok = True
                extra_fields = {k: v for k, v in e.items() if k not in ["action", "return_id", "shipment_id", "sku", "warehouse_id"]}
                for k, v in extra_fields.items():
                    if actual_op.get(k) != v:
                        extra_ok = False
                        break
                if extra_ok:
                    add_item(f"操作'{e['action']}'额外字段正确", detail_score_per, detail_score_per, True, "全部匹配")
                else:
                    add_item(f"操作'{e['action']}'额外字段正确", 0, detail_score_per, False, f"期望{extra_fields}, 实际{actual_op}")
            else:
                add_item(f"操作'{e['action']}'额外字段正确", 0, detail_score_per, False, "未找到对应操作")
        else:
            add_item(f"操作'{e['action']}' ID正确", 0, action_score_per, False, "缺失或ID不匹配")
            add_item(f"操作'{e['action']}'额外字段正确", 0, detail_score_per, False, "缺失")

    # ---- 4. reconciliation.json 内容检查 (35分) ----
    try:
        with open(reconciliation_path) as f:
            rec = json.load(f)
    except Exception as e:
        add_item("reconciliation.json 解析", 0, 35, False, f"JSON解析失败: {e}")
        return _finish(scores, total_score)

    # 检查report_type
    if rec.get("report_type") == "inventory_reconciliation":
        add_item("包含 report_type 字段", 3, 3, True, "正确")
    else:
        add_item("包含 report_type 字段", 0, 3, False, f"期望'inventory_reconciliation', 实际{rec.get('report_type')}")

    warehouses_list = rec.get("warehouses")
    if not isinstance(warehouses_list, list):
        add_item("warehouses 是数组", 0, 5, False, "缺失或不是数组")
        return _finish(scores, total_score)
    add_item("warehouses 是数组", 5, 5, True, f"包含{len(warehouses_list)}个仓库")

    # 期望三个仓库的数据
    expected_wh = {
        "wh_001": {"name": "Central Fulfillment Hub", "actual_available": 83, "system_utilization": 80, "discrepancy": 3},
        "wh_002": {"name": "East Distribution Center", "actual_available": 10, "system_utilization": 10, "discrepancy": 0},
        "wh_003": {"name": "West Distribution Center", "actual_available": 0, "system_utilization": 5, "discrepancy": -5}
    }

    found_wh = {}
    for wh in warehouses_list:
        wh_id = wh.get("warehouse_id")
        if wh_id in expected_wh:
            found_wh[wh_id] = wh

    for wh_id, exp in expected_wh.items():
        if wh_id not in found_wh:
            add_item(f"仓库 {wh_id} 存在", 0, 3, False, "缺失")
            continue
        actual = found_wh[wh_id]
        # 检查字段
        fields_ok = True
        for field in ["warehouse_id", "name", "actual_available", "system_utilization", "discrepancy"]:
            if field not in actual:
                fields_ok = False
        if fields_ok:
            add_item(f"仓库 {wh_id} 包含所有必要字段", 3, 3, True, "")
        else:
            add_item(f"仓库 {wh_id} 包含所有必要字段", 0, 3, False, f"缺失字段: {set(exp.keys())-set(actual.keys())}")
            continue
        # 检查数值
        numeric_ok = True
        for field in ["actual_available", "system_utilization", "discrepancy"]:
            if actual.get(field) != exp[field]:
                numeric_ok = False
        if numeric_ok and actual.get("name") == exp["name"]:
            add_item(f"仓库 {wh_id} 数值和名称正确", 7, 7, True, "")
        else:
            add_item(f"仓库 {wh_id} 数值和名称正确", 0, 7, False, f"期望{exp}, 实际{actual}")

    # total_discrepancy
    total_disc = rec.get("total_discrepancy")
    if total_disc == -2:
        add_item("total_discrepancy 正确", 5, 5, True, "值为-2")
    else:
        add_item("total_discrepancy 正确", 0, 5, False, f"期望-2, 实际{total_disc}")

    return _finish(scores, total_score)

def _finish(scores, total_score):
    # 确保总分在0-100内
    total_score = min(max(round(total_score), 0), 100)
    result = {
        "total_score": total_score,
        "details": scores
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
