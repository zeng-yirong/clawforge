import json
import os
import sys

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1) 检查 ops/ 目录是否存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 ops/ 目录"})

    # 2) 检查 ops/eu_impact_assessment.json 是否存在 (5分)
    report_path = os.path.join(ops_dir, "eu_impact_assessment.json")
    if os.path.isfile(report_path):
        details.append({"item": "report file exists", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        score += 5
    else:
        details.append({"item": "report file exists", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 ops/eu_impact_assessment.json"})
        # 如果文件不存在，后面的检查无法进行，直接输出
        print(json.dumps({"total_score": score, "details": details}))
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 3) JSON 格式合法性 (5分)
    try:
        report = load_json(report_path)
        details.append({"item": "JSON format valid", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        score += 5
    except Exception as e:
        details.append({"item": "JSON format valid", "score": 0, "max_score": 5, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        print(json.dumps({"total_score": score, "details": details}))
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 4) 检查 policies 数组 (20分): 长度应为2，每个元素包含 policy_id 和 affected_competitors
    if "policies" not in report or not isinstance(report["policies"], list):
        details.append({"item": "policies array", "score": 0, "max_score": 20, "passed": False, "reason": "缺失 policies 字段或类型错误"})
    else:
        policies = report["policies"]
        if len(policies) != 2:
            details.append({"item": "policies array length", "score": 0, "max_score": 10, "passed": False, "reason": f"期望2条政策，实际{len(policies)}条"})
        else:
            details.append({"item": "policies array length", "score": 10, "max_score": 10, "passed": True, "reason": f"长度正确"})
            score += 10

        # 验证每条政策的内容
        expected_policies = [
            {"policy_id": "pol-001", "title": "EU Digital Markets Act Compliance", "affected_competitors": ["comp-001", "comp-002"]},
            {"policy_id": "pol-004", "title": "EU AI Liability Directive", "affected_competitors": ["comp-003"]}
        ]
        policies_ok = True
        for exp in expected_policies:
            found = None
            for p in policies:
                if p.get("policy_id") == exp["policy_id"]:
                    found = p
                    break
            if not found:
                policies_ok = False
                details.append({"item": f"政策 {exp['policy_id']} 存在", "score": 0, "max_score": 5, "passed": False, "reason": f"未找到 policy_id={exp['policy_id']}"})
                continue
            # 检查 affected_competitors
            ac = found.get("affected_competitors", [])
            if sorted(ac) == sorted(exp["affected_competitors"]):
                details.append({"item": f"政策 {exp['policy_id']} 的 affected_competitors", "score": 5, "max_score": 5, "passed": True, "reason": ""})
                score += 5
            else:
                policies_ok = False
                details.append({"item": f"政策 {exp['policy_id']} 的 affected_competitors", "score": 0, "max_score": 5, "passed": False, "reason": f"期望{sorted(exp['affected_competitors'])}, 实际{sorted(ac)}"})
        if policies_ok:
            details.append({"item": "policies 全部正确", "score": 0, "max_score": 0, "passed": True, "reason": ""})  # 不计分，仅状态

    # 5) 检查 competitors_summary 数组 (剩余70分)
    if "competitors_summary" not in report or not isinstance(report["competitors_summary"], list):
        details.append({"item": "competitors_summary array", "score": 0, "max_score": 70, "passed": False, "reason": "缺失 competitors_summary 字段或类型错误"})
    else:
        summary = report["competitors_summary"]
        # 长度应为3（comp-001,comp-002,comp-003）
        if len(summary) != 3:
            details.append({"item": "competitors_summary length", "score": 0, "max_score": 10, "passed": False, "reason": f"期望3个竞品，实际{len(summary)}"})
        else:
            details.append({"item": "competitors_summary length", "score": 10, "max_score": 10, "passed": True, "reason": ""})
            score += 10

        # 从原始数据计算每个竞品的平均值（排除脏数据）
        # 重置计算
        computed = {}
        users_dir = os.path.join(workspace, "data/users")
        if os.path.isdir(users_dir):
            for fname in os.listdir(users_dir):
                if fname.endswith(".json"):
                    try:
                        u = load_json(os.path.join(users_dir, fname))
                    except:
                        continue
                    cid = u.get("competitor_id")
                    cost = u.get("acquisition_cost")
                    if cid not in ["comp-001","comp-002","comp-003"]:
                        continue
                    if cost is None or not isinstance(cost, (int, float)):
                        continue
                    if cost < 0 or cost > 10000:
                        continue
                    if cid not in computed:
                        computed[cid] = {"sum": 0, "count": 0}
                    computed[cid]["sum"] += cost
                    computed[cid]["count"] += 1

        # 竞品数据中的 market_share
        comp_data = {}
        competitors_dir = os.path.join(workspace, "data/competitors")
        if os.path.isdir(competitors_dir):
            for fname in os.listdir(competitors_dir):
                if fname.endswith(".json"):
                    try:
                        c = load_json(os.path.join(competitors_dir, fname))
                        comp_data[c["competitor_id"]] = c
                    except:
                        continue

        expected_summaries = []
        for cid in ["comp-001", "comp-002", "comp-003"]:
            avg = round(computed[cid]["sum"] / computed[cid]["count"], 2) if cid in computed and computed[cid]["count"]>0 else 0
            share = comp_data.get(cid, {}).get("market_share", 0)
            name = comp_data.get(cid, {}).get("name", "")
            expected_summaries.append({
                "competitor_id": cid,
                "name": name,
                "avg_acquisition_cost": avg,
                "market_share": share
            })

        # 逐项比较
        for exp in expected_summaries:
            found = None
            for s in summary:
                if s.get("competitor_id") == exp["competitor_id"]:
                    found = s
                    break
            if not found:
                details.append({"item": f"competitor {exp['competitor_id']} in summary", "score": 0, "max_score": 15, "passed": False, "reason": f"未找到 competitor_id={exp['competitor_id']}"})
                continue
            # 检查 name
            name_ok = found.get("name") == exp["name"]
            # 检查 avg_acquisition_cost (精确比较浮点数，允许小误差？这里用 round 保证一致)
            cost_ok = abs(found.get("avg_acquisition_cost", -1) - exp["avg_acquisition_cost"]) < 0.01
            share_ok = abs(found.get("market_share", -1) - exp["market_share"]) < 0.01
            if name_ok and cost_ok and share_ok:
                details.append({"item": f"competitor {exp['competitor_id']} 数据正确", "score": 15, "max_score": 15, "passed": True, "reason": ""})
                score += 15
            else:
                reason_parts = []
                if not name_ok:
                    reason_parts.append(f"name期望'{exp['name']}', 实际'{found.get('name')}'")
                if not cost_ok:
                    reason_parts.append(f"avg_acquisition_cost期望{exp['avg_acquisition_cost']}, 实际{found.get('avg_acquisition_cost')}")
                if not share_ok:
                    reason_parts.append(f"market_share期望{exp['market_share']}, 实际{found.get('market_share')}")
                details.append({"item": f"competitor {exp['competitor_id']} 数据正确", "score": 0, "max_score": 15, "passed": False, "reason": "; ".join(reason_parts)})

    # 最终总分
    total_score = min(score, 100)  # 确保不超过100
    # 写入结果
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
