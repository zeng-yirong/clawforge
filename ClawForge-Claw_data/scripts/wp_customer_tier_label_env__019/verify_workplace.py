import sys
import os
import json
import re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(workspace, rel_path)
    if not os.path.exists(full):
        return None
    with open(full, "r") as f:
        return json.load(f)

def check_result():
    scores = []
    total_score = 0
    max_total = 100

    # 1. 检查 reports/tier_labels.json 是否存在 (10分)
    result_path = os.path.join(workspace, "reports/tier_labels.json")
    if os.path.exists(result_path):
        scores.append({"item": "结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "reports/tier_labels.json 存在"})
    else:
        scores.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 直接写分返回
        write_score(scores, 0)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    try:
        with open(result_path, "r") as f:
            result_data = json.load(f)
        if not isinstance(result_data, list):
            raise ValueError("不是列表")
        scores.append({"item": "JSON格式与类型", "score": 10, "max_score": 10, "passed": True, "reason": "合法JSON且为列表"})
    except Exception as e:
        scores.append({"item": "JSON格式与类型", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(scores, 0)
        return

    # 3. 读取规则与原始数据，计算预期标签 (预计算，用于后面的比对)
    # 加载规则
    rules = load_json("rules/tier_rules.json")
    if not rules:
        scores.append({"item": "规则文件", "score": 0, "max_score": 10, "passed": False, "reason": "rules/tier_rules.json 缺失"})
        write_score(scores, 0)
        return

    # 加载客户列表
    customers_raw = load_json("data/customers/customers.json")
    if not customers_raw or "customers" not in customers_raw:
        scores.append({"item": "客户数据", "score": 0, "max_score": 10, "passed": False, "reason": "data/customers/customers.json 缺失或格式错误"})
        write_score(scores, 0)
        return
    valid_customer_ids = {c["customer_id"] for c in customers_raw["customers"]}
    customer_name_map = {c["customer_id"]: c["customer_name"] for c in customers_raw["customers"]}

    # 加载消费日志（过滤有效记录：正数金额，且客户ID有效）
    cons_raw = load_json("data/logs/consumption_logs.json")
    if not cons_raw or "consumption_logs" not in cons_raw:
        scores.append({"item": "消费日志", "score": 0, "max_score": 10, "passed": False, "reason": "consumption_logs 缺失"})
        write_score(scores, 0)
        return
    cons_filtered = {}
    for rec in cons_raw["consumption_logs"]:
        cid = rec.get("customer_id", "")
        spend = rec.get("quarter_spend_usd")
        if cid not in valid_customer_ids:
            continue
        if not isinstance(spend, int) or spend <= 0:
            continue
        # 取第一个有效记录（如果有多个重复，取第一个；这里只保留一个，且确保唯一）
        if cid not in cons_filtered:
            cons_filtered[cid] = spend

    # 加载活动日志（过滤有效记录：last_active_days 非负整数，risk_level 为 'low' 或 'high'，客户ID有效）
    act_raw = load_json("data/logs/activity_logs.json")
    if not act_raw or "activity_logs" not in act_raw:
        scores.append({"item": "活动日志", "score": 0, "max_score": 10, "passed": False, "reason": "activity_logs 缺失"})
        write_score(scores, 0)
        return
    act_filtered = {}
    for rec in act_raw["activity_logs"]:
        cid = rec.get("customer_id", "")
        risk = rec.get("risk_level", "")
        days = rec.get("last_active_days")
        if cid not in valid_customer_ids:
            continue
        if risk not in ("low", "high"):
            continue
        if not isinstance(days, int) or days < 0:
            continue
        if cid not in act_filtered:
            act_filtered[cid] = {"risk": risk, "days": days}

    # 计算每个客户的预期标签
    tiers = rules["tiers"]
    expected = {}
    for cid in sorted(valid_customer_ids):
        spend = cons_filtered.get(cid, 0)
        act = act_filtered.get(cid, {"risk": "low", "days": 999})  # 默认risk low，但活跃天数极大
        risk = act["risk"]
        days = act["days"]
        label = "Bronze"  # default
        for tier in tiers:
            if tier.get("default"):
                continue
            if spend >= tier["min_spend"] and days <= tier["max_active_days"] and risk in tier["allowed_risk"]:
                label = tier["name"]
                break
        expected[cid] = {
            "customer_id": cid,
            "customer_name": customer_name_map[cid],
            "tier_label": label
        }

    # 4. 检查结果数量 (10分)
    if len(result_data) == len(expected):
        scores.append({"item": "记录数量", "score": 10, "max_score": 10, "passed": True, "reason": f"共 {len(expected)} 条，符合客户总数"})
    else:
        scores.append({"item": "记录数量", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {len(expected)} 条，实际 {len(result_data)} 条"})
        write_score(scores, 0)
        return

    # 5. 检查每条记录的字段完整性 (10分)
    field_ok = True
    for rec in result_data:
        if not isinstance(rec, dict):
            field_ok = False
            break
        if "customer_id" not in rec or "customer_name" not in rec or "tier_label" not in rec:
            field_ok = False
            break
    if field_ok:
        scores.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "每条记录包含 customer_id, customer_name, tier_label"})
    else:
        scores.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "字段缺失或不规范"})
        write_score(scores, 0)
        return

    # 6. 比对每个客户的标签 (60分，每个客户12分，共5个)
    result_map = {rec["customer_id"]: rec for rec in result_data}
    for cid, exp in expected.items():
        if cid not in result_map:
            scores.append({"item": f"客户 {cid} 缺失", "score": 0, "max_score": 12, "passed": False, "reason": "未在结果中找到"})
            continue
        actual_label = result_map[cid].get("tier_label", "")
        if actual_label == exp["tier_label"]:
            scores.append({"item": f"客户 {cid} 标签正确", "score": 12, "max_score": 12, "passed": True, "reason": f"应为 {exp['tier_label']}，实际 {actual_label}"})
        else:
            scores.append({"item": f"客户 {cid} 标签错误", "score": 0, "max_score": 12, "passed": False, "reason": f"期望 {exp['tier_label']}，实际 {actual_label}"})

    # 7. 检查没有多余客户（防止混入脏数据中的不合法客户）
    extra_ids = set(result_map.keys()) - set(expected.keys())
    if extra_ids:
        # 每个额外客户扣2分，最多扣10分
        penalty = min(len(extra_ids) * 2, 10)
        scores.append({"item": "无多余客户", "score": 0, "max_score": 10, "passed": False, "reason": f"包含非法客户ID: {extra_ids}，扣{penalty}分"})
        # 从总分中扣除（但按总分100计算，我们已分配各项目，此处额外扣减）
        # 为简化，直接在总分扣
        # 但为了保持列表累加，我们加一条扣分项
        scores.append({"item": "多余客户扣分", "score": -penalty, "max_score": 0, "passed": False, "reason": f"扣{penalty}分"})
    else:
        scores.append({"item": "无多余客户", "score": 10, "max_score": 10, "passed": True, "reason": "结果中只有合法客户"})

    # 汇总计算总分
    total_score = sum(s["score"] for s in scores if isinstance(s["score"], int) or isinstance(s["score"], float))
    total_score = max(0, min(100, total_score))
    write_score(scores, total_score)

def write_score(scores, total):
    result = {
        "total_score": int(total),
        "details": scores
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification done. Total score: {total}")

if __name__ == "__main__":
    check_result()
