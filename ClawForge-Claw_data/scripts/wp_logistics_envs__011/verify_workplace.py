import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "ops", "summary_report.json")
    details = []
    total = 0
    max_total = 100

    # 1. 文件存在 (10分)
    if os.path.isfile(report_path):
        details.append({"item": "文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/summary_report.json 存在"})
        total += 10
    else:
        details.append({"item": "文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/summary_report.json 不存在"})
        # 如果文件不存在，后续检查跳过，直接输出
        _write_score(details, total, workspace)
        return

    # 2. JSON 合法性 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON 合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        _write_score(details, total, workspace)
        return

    # 检查 actions 字段存在且为列表
    if "actions" not in data or not isinstance(data["actions"], list):
        details.append({"item": "字段结构", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 actions 字段或不是列表"})
        _write_score(details, total, workspace)
        return

    actions = data["actions"]
    if len(actions) != 5:
        details.append({"item": "actions 数量", "score": 0, "max_score": 10, "passed": False, "reason": f"期望5个action，实际{len(actions)}个"})
        _write_score(details, total, workspace)
        return
    details.append({"item": "actions 数量", "score": 10, "max_score": 10, "passed": True, "reason": "包含5个action"})
    total += 10

    # 定义每个 action 的期望检查
    expected = [
        {"type": "approve_return", "target": "ret_001", "extra": {"reason_contains": "defective", "suggested_resolution": "approved"}},
        {"type": "inspect_return", "target": "ret_003", "extra": {"reason_contains": "wrong item", "suggested_resolution": "exchange"}},
        {"type": "update_shipment", "target": "ship_005", "extra": {"new_status": "shipped", "carrier": "FedEx"}},
        {"type": "adjust_inventory", "target": "SKU-1002", "extra": {"warehouse_id": "wh_001", "adjustment_type": "damage", "quantity_change": -5}},
        {"type": "generate_report", "target": "inventory_reconciliation", "extra": {"report_type": "inventory_reconciliation"}}
    ]

    action_dict = {a.get("type"): a for a in actions}
    # 检查每个期望类型是否存在
    for exp in expected:
        t = exp["type"]
        if t not in action_dict:
            details.append({"item": f"action类型 {t}", "score": 0, "max_score": 5, "passed": False, "reason": f"缺少type={t}的action"})
        else:
            act = action_dict[t]
            # 检查 target
            target_ok = str(act.get("target", "")) == exp["target"]
            if not target_ok:
                details.append({"item": f"{t} target", "score": 0, "max_score": 5, "passed": False, "reason": f"期望target={exp['target']}，实际={act.get('target')}"})
            else:
                details.append({"item": f"{t} target", "score": 5, "max_score": 5, "passed": True, "reason": f"target正确"})
                total += 5

            # 检查 extra 字段
            extra = exp["extra"]
            extra_ok = all(str(act.get(k, "")) == str(v) for k, v in extra.items())
            if extra_ok:
                details.append({"item": f"{t} 额外字段", "score": 5, "max_score": 5, "passed": True, "reason": "额外字段匹配"})
                total += 5
            else:
                detail_str = "; ".join([f"{k}: 期望 {v} 实际 {act.get(k)}" for k, v in extra.items() if str(act.get(k, "")) != str(v)])
                details.append({"item": f"{t} 额外字段", "score": 0, "max_score": 5, "passed": False, "reason": f"字段不匹配: {detail_str}"})

    _write_score(details, total, workspace)

def _write_score(details, total, workspace):
    score_data = {"total_score": total, "details": details}
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
