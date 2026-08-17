import json
import os
import sys

def load_records(filepath, wrapper_key):
    """从 JSON 文件中加载记录列表，返回按 customer_id 分组后取最后一条的字典"""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        data = json.load(f)
    records = data.get(wrapper_key, [])
    result = {}
    for rec in records:
        cid = rec.get("customer_id")
        if cid:
            result[cid] = rec  # 后面的覆盖前面的，达到取最后一次的效果
    return result

def compute_expected_tier(cid, consumption, activity):
    """根据消费和活动数据计算预期标签"""
    spend = consumption["quarter_spend_usd"]
    active = activity["last_active_days"]
    risk = activity["risk_level"]

    # VIP条件
    if spend > 50000 and active <= 30 and risk == "low":
        return "VIP"
    # Important条件
    if 20000 <= spend <= 50000 and active <= 60:
        return "Important"
    return "Standard"

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    # 切换工作区
    original_cwd = os.getcwd()
    os.chdir(workspace)

    score_details = []
    total_score = 0

    # 1. 输出文件存在
    output_path = "output/customer_tiers.json"
    if os.path.exists(output_path) and os.path.isfile(output_path):
        score_details.append({
            "item": "输出文件存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "output/customer_tiers.json 存在"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "输出文件存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "output/customer_tiers.json 不存在"
        })
        os.chdir(original_cwd)
        # 无输出文件，后续无法检查，直接结束
        final = {"total_score": total_score, "details": score_details}
        with open("workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # 2. JSON 合法性
    try:
        with open(output_path, 'r') as f:
            agent_output = json.load(f)
        if isinstance(agent_output, dict):
            score_details.append({
                "item": "JSON 合法性",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "解析成功且为字典"
            })
            total_score += 10
        else:
            score_details.append({
                "item": "JSON 合法性",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "结果不是字典"
            })
            os.chdir(original_cwd)
            final = {"total_score": total_score, "details": score_details}
            with open("workplace_score.json", "w") as f:
                json.dump(final, f, indent=2)
            return
    except Exception as e:
        score_details.append({
            "item": "JSON 合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        os.chdir(original_cwd)
        final = {"total_score": total_score, "details": score_details}
        with open("workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. 字段完整性：每个条目有 tier 和 reason 且 reason 非空
    agents_ids = set(agent_output.keys())
    field_issues = []
    for cid, entry in agent_output.items():
        if not isinstance(entry, dict):
            field_issues.append(f"{cid}: 值不是字典")
            continue
        if "tier" not in entry:
            field_issues.append(f"{cid}: 缺少 tier 字段")
        elif entry["tier"] not in ["VIP", "Important", "Standard"]:
            field_issues.append(f"{cid}: tier 值不在允许范围内")
        if "reason" not in entry:
            field_issues.append(f"{cid}: 缺少 reason 字段")
        elif not isinstance(entry["reason"], str) or len(entry["reason"].strip()) == 0:
            field_issues.append(f"{cid}: reason 为空或非字符串")
    field_score = 10 - len(field_issues)  # 每个问题扣1分，最多扣10分
    if field_score < 0:
        field_score = 0
    score_details.append({
        "item": "字段完整性",
        "score": field_score,
        "max_score": 10,
        "passed": len(field_issues) == 0,
        "reason": "全部字段合格" if not field_issues else "; ".join(field_issues)
    })
    total_score += field_score

    # 4. 加载原始数据，计算期望
    consumption_records = load_records("data/consumption_logs.json", "consumption_logs")
    activity_records = load_records("data/activity_logs.json", "activity_logs")

    # 有效客户：同时在两个文件中，且数据合法
    expected = {}
    for cid in set(consumption_records.keys()) & set(activity_records.keys()):
        cons = consumption_records[cid]
        act = activity_records[cid]
        spend = cons["quarter_spend_usd"]
        active = act["last_active_days"]
        if spend <= 0 or active < 0:
            continue
        tier = compute_expected_tier(cid, cons, act)
        expected[cid] = {"tier": tier, "reason": f"Computed as {tier}"}  # reason 不重要

    expected_ids = set(expected.keys())

    # 5. 过滤正确性：检查多余和遗漏
    agent_ids = set(agent_output.keys())
    extra_ids = agent_ids - expected_ids
    missing_ids = expected_ids - agent_ids
    filter_penalty = 0
    # 每个多余ID扣5分，最多扣15分；每个遗漏ID扣5分，最多扣15分；总分25分
    filter_penalty = 5 * len(extra_ids) + 5 * len(missing_ids)
    filter_score = max(25 - filter_penalty, 0)
    filter_reason_parts = []
    if extra_ids:
        filter_reason_parts.append(f"多余ID: {', '.join(sorted(extra_ids))}")
    if missing_ids:
        filter_reason_parts.append(f"遗漏ID: {', '.join(sorted(missing_ids))}")
    if not extra_ids and not missing_ids:
        filter_reason_parts.append("客户集合完全匹配")
    score_details.append({
        "item": "过滤正确性（客户集合匹配）",
        "score": filter_score,
        "max_score": 25,
        "passed": len(extra_ids) == 0 and len(missing_ids) == 0,
        "reason": "; ".join(filter_reason_parts)
    })
    total_score += filter_score

    # 6. 标签正确性：对共同ID比较tier
    common_ids = expected_ids & agent_ids
    tier_correct_count = 0
    tier_errors = []
    for cid in common_ids:
        agent_tier = agent_output[cid].get("tier")
        expected_tier = expected[cid]["tier"]
        if agent_tier == expected_tier:
            tier_correct_count += 1
        else:
            tier_errors.append(f"{cid}: agent={agent_tier}, expected={expected_tier}")
    # 满分50分，每个正确ID贡献 50 / max(len(expected_ids), 1) 分，但为了公平，取 max(1, len(expected_ids))
    if len(expected_ids) > 0:
        points_per_correct = 50.0 / len(expected_ids)
    else:
        points_per_correct = 0
    tier_score = int(round(points_per_correct * tier_correct_count))
    # 如果由于 round 导致超过50，限制为50
    if tier_score > 50:
        tier_score = 50
    if tier_score < 0:
        tier_score = 0
    score_details.append({
        "item": "标签正确性",
        "score": tier_score,
        "max_score": 50,
        "passed": tier_correct_count == len(expected_ids),
        "reason": f"正确 {tier_correct_count}/{len(expected_ids)}" if not tier_errors else "错误: " + "; ".join(tier_errors)
    })
    total_score += tier_score

    # 确保总分在0-100之间
    if total_score > 100:
        total_score = 100
    elif total_score < 0:
        total_score = 0

    final = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)

    os.chdir(original_cwd)

if __name__ == "__main__":
    main()
