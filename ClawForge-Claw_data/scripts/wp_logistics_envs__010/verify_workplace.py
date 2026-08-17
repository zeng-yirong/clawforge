import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(workspace, rel_path)
    with open(full, "r") as f:
        return json.load(f)

def write_score(score, details):
    result = {"total_score": max(0, min(100, score)), "details": details}
    path = os.path.join(workspace, "workplace_score.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2)

def main():
    details = []
    total = 0

    # 1. 文件存在 (10分)
    plan_path = "ops/action_plan.json"
    full_plan = os.path.join(workspace, plan_path)
    if os.path.isfile(full_plan):
        details.append({"item": "文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/action_plan.json 存在"})
        total += 10
    else:
        details.append({"item": "文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ops/action_plan.json"})
        write_score(total, details)
        return

    # 2. JSON 格式合法 (10分)
    try:
        with open(full_plan, "r") as f:
            plan = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        write_score(total, details)
        return

    # 3. actions 字段存在且为列表 (10分)
    actions = plan.get("actions")
    if not isinstance(actions, list):
        details.append({"item": "actions字段", "score": 0, "max_score": 10, "passed": False, "reason": "缺少actions字段或不是列表"})
        write_score(total, details)
        return
    details.append({"item": "actions字段", "score": 10, "max_score": 10, "passed": True, "reason": "actions是列表"})
    total += 10

    # 4. actions 数量正确 (10分)
    expected_count = 4
    if len(actions) != expected_count:
        details.append({"item": "actions数量", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{expected_count}个动作，实际{len(actions)}个"})
    else:
        details.append({"item": "actions数量", "score": 10, "max_score": 10, "passed": True, "reason": f"数量正确"})
        total += 10

    # 5. 尝试读取原始数据，构建期望动作列表 (用于后续匹配)
    try:
        returns = load_json("data/returns/returns.json")["returns"]
        shipments = load_json("data/shipments/shipments.json")["shipments"]
        inventory = load_json("data/inventory/inventory.json")["inventory"]
    except Exception as e:
        details.append({"item": "读取原始数据", "score": 0, "max_score": 0, "passed": False, "reason": f"无法加载数据文件: {str(e)}"})
        write_score(total, details)
        return

    # 期望动作（根据数据和业务规则唯一确定）
    expected_actions = [
        {"action": "approve_return", "return_id": "ret_001", "new_status": "approved", "resolution": "refund_approved"},
        {"action": "inspect_return", "return_id": "ret_003", "new_status": "pending_inspection", "resolution": "exchange"},
        {"action": "update_shipment_status", "shipment_id": "ship_005", "new_status": "shipped"},
        {"action": "adjust_inventory", "sku": "SKU-1002", "warehouse": "wh_001", "adjustment": -5, "type": "damage"}
    ]

    # 辅助：判断一个实际动作是否匹配期望（允许额外字段，但必须包含所有期望字段且值相等）
    def matches(exp, act):
        for k, v in exp.items():
            if k not in act or act[k] != v:
                return False
        return True

    # 为每个期望动作寻找匹配
    matched = [False] * len(expected_actions)
    for i, exp in enumerate(expected_actions):
        for act in actions:
            if matches(exp, act):
                matched[i] = True
                break

    # 每个正确动作 15 分，共 60 分
    action_score = 0
    act_names = [
        "批准退货 ret_001",
        "检查退货 ret_003",
        "更新发货 ship_005",
        "调整库存 SKU-1002"
    ]
    for i, m in enumerate(matched):
        if m:
            action_score += 15
            details.append({"item": f"动作{i+1}: {act_names[i]}", "score": 15, "max_score": 15, "passed": True, "reason": "核心字段匹配期望"})
        else:
            details.append({"item": f"动作{i+1}: {act_names[i]}", "score": 0, "max_score": 15, "passed": False, "reason": "未匹配到正确字段或值"})
    total += action_score

    # 额外动作惩罚（最多扣10分）
    extra = len(actions) - expected_count
    if extra > 0:
        penalty = min(extra * 5, 10)
        total -= penalty
        details.append({"item": "额外动作惩罚", "score": -penalty, "max_score": 0, "passed": False, "reason": f"存在{extra}个额外动作，扣{penalty}分"})

    # 写入最终分数
    write_score(total, details)

if __name__ == "__main__":
    main()
