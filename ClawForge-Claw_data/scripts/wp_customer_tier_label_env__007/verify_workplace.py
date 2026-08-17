import sys
import os
import json

def check_path(ws, path):
    full = os.path.join(ws, path)
    if os.path.exists(full):
        return full, True
    return full, False

def read_json(ws, path):
    full = os.path.join(ws, path)
    try:
        with open(full, 'r') as f:
            return json.load(f), True
    except:
        return None, False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 目录结构检查（ops 目录）
    ops_dir, exists = check_path(workspace, "ops")
    if exists:
        details.append({"item": "ops/ 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录已创建"})
        total_score += 5
    else:
        details.append({"item": "ops/ 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "目录不存在"})

    # 2. 产物文件存在性
    label_path, exists = check_path(workspace, "ops/label_updates.json")
    if exists:
        details.append({"item": "ops/label_updates.json 存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件已生成"})
        total_score += 5
    else:
        details.append({"item": "ops/label_updates.json 存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})
        # 后续检查无法进行，返回当前分数
        score_out = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_out, f, indent=2)
        print(json.dumps(score_out, indent=2))
        return

    # 3. 文件合法性（JSON 解析）
    data, valid = read_json(workspace, "ops/label_updates.json")
    if valid and isinstance(data, dict):
        details.append({"item": "ops/label_updates.json 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "有效的 JSON 对象"})
        total_score += 10
    else:
        details.append({"item": "ops/label_updates.json 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "不是有效的 JSON 对象"})
        score_out = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_out, f, indent=2)
        print(json.dumps(score_out, indent=2))
        return

    # 4. 检查是否有 'updates' 键且是列表
    if "updates" not in data or not isinstance(data["updates"], list):
        details.append({"item": "updates 字段存在且为列表", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 updates 键或类型错误"})
        total_score += 0
        score_out = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_out, f, indent=2)
        print(json.dumps(score_out, indent=2))
        return
    else:
        details.append({"item": "updates 字段存在且为列表", "score": 10, "max_score": 10, "passed": True, "reason": "结构正确"})
        total_score += 10

    # 5. 加载原始数据，计算预期结果
    # 读取 customers, consumption_logs, activity_logs
    customers, ok1 = read_json(workspace, "data/customers/customers.json")
    cons_logs, ok2 = read_json(workspace, "data/logs/consumption_logs.json")
    act_logs, ok3 = read_json(workspace, "data/logs/activity_logs.json")
    if not (ok1 and ok2 and ok3):
        details.append({"item": "读取原始数据", "score": 0, "max_score": 5, "passed": False, "reason": "原始数据缺失"})
        total_score += 0
    else:
        # 构建消费和活动字典
        cons_dict = {c["customer_id"]: c["quarter_spend_usd"] for c in cons_logs}
        act_dict = {a["customer_id"]: a for a in act_logs}

        expected_updates = []
        # 规则函数
        def compute_label(cust, spend, act):
            if spend >= 80000 and act["risk_level"] == "low" and act["last_active_days"] <= 7:
                return ["premium"]
            if spend >= 80000 and act["risk_level"] == "high":
                return ["attention"]
            if 50000 <= spend < 80000 and act["risk_level"] == "low" and act["last_active_days"] <= 30:
                return ["standard"]
            return None  # 不更新

        for cust in customers:
            cid = cust["customer_id"]
            spend = cons_dict.get(cid)
            act = act_dict.get(cid)
            if spend is None or act is None:
                continue
            new_label = compute_label(cust, spend, act)
            if new_label is not None:
                expected_updates.append({"customer_id": cid, "new_labels": new_label})

        # 对预期按 customer_id 排序
        expected_updates_sorted = sorted(expected_updates, key=lambda x: x["customer_id"])
        # agent 结果也排序
        agent_updates_sorted = sorted(data["updates"], key=lambda x: x["customer_id"])

        # 先检查条目数
        if len(agent_updates_sorted) != len(expected_updates_sorted):
            details.append({"item": "更新条目数正确", "score": 0, "max_score": 30, "passed": False, "reason": f"数量不匹配: agent {len(agent_updates_sorted)}, 预期 {len(expected_updates_sorted)}"})
            total_score += 0
        else:
            details.append({"item": "更新条目数正确", "score": 10, "max_score": 10, "passed": True, "reason": f"数量 = {len(expected_updates_sorted)}"})
            total_score += 10

            # 逐条检查
            detail_correct = True
            for i, (exp, agent) in enumerate(zip(expected_updates_sorted, agent_updates_sorted)):
                cid = exp["customer_id"]
                if agent.get("customer_id") != cid:
                    details.append({"item": f"客户 {cid} ID 匹配", "score": 0, "max_score": 0, "passed": False, "reason": f"顺序或ID错误: 预期 {cid}, 得到 {agent.get('customer_id')}"})
                    detail_correct = False
                    continue
                if agent.get("new_labels") != exp["new_labels"]:
                    details.append({"item": f"客户 {cid} 标签正确", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 {exp['new_labels']}, 得到 {agent.get('new_labels')}"})
                    total_score += 0
                    detail_correct = False
                else:
                    details.append({"item": f"客户 {cid} 标签正确", "score": 10, "max_score": 10, "passed": True, "reason": f"标签 {exp['new_labels']} 正确"})
                    total_score += 10
            if detail_correct:
                pass  # 已有加分

    # 额外检查：不允许有无关客户
    agent_ids = set(u.get("customer_id") for u in data["updates"])
    expected_ids = set(u["customer_id"] for u in expected_updates_sorted)
    if agent_ids != expected_ids:
        extra = agent_ids - expected_ids
        missing = expected_ids - agent_ids
        details.append({"item": "无多余或缺失的客户", "score": 0, "max_score": 20, "passed": False, "reason": f"多余: {extra}, 缺失: {missing}"})
        total_score += 0
    else:
        details.append({"item": "无多余或缺失的客户", "score": 15, "max_score": 15, "passed": True, "reason": "客户集合完全匹配"})
        total_score += 15

    # 输出结果
    score_out = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_out, f, indent=2)
    print(json.dumps(score_out, indent=2))

if __name__ == "__main__":
    main()
