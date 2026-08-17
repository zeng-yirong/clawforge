import os
import sys
import json

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(WORKSPACE, rel_path)
    if not os.path.isfile(full):
        return None
    with open(full) as f:
        return json.load(f)

def evaluate():
    details = []
    total_score = 0

    # ============ 1. 目录结构检查 (10分) ============
    score = 0
    max_score = 10
    reasons = []
    required_dirs = ["data", "policies", "ops"]
    for d in required_dirs:
        if os.path.isdir(os.path.join(WORKSPACE, d)):
            score += 3
        else:
            reasons.append(f"缺少目录 {d}")
    total_score += score
    details.append({
        "item": "目录结构完整性",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reasons if reasons else "所有必需目录存在"
    })

    # ============ 2. agent的产物文件 ops/booking_summary.json 必须存在 (10分) ============
    score = 0
    max_score = 10
    path = os.path.join(WORKSPACE, "ops/booking_summary.json")
    if os.path.isfile(path):
        score = 10
    details.append({
        "item": "产物文件存在",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": "文件 ops/booking_summary.json 存在" if score else "文件缺失"
    })

    # ============ 3. JSON 合法性及必要字段 (15分) ============
    score = 0
    max_score = 15
    reasons = []
    data = load_json("ops/booking_summary.json")
    if data is None:
        reasons.append("无法解析JSON")
    else:
        required_keys = ["selected_flight", "total_cost", "policy_compliant", "approval_required", "excess_amount"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            reasons.append(f"缺少字段: {missing}")
        else:
            score = 15
    details.append({
        "item": "JSON结构及字段完整性",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reasons if reasons else "所有必需字段存在"
    })

    # 如果前面失败则不再继续深入，但为了鲁棒，后面检查会跳过
    if data is None:
        # 填充剩余项目为0分
        for item_name, max_s in [("航班选择正确性", 20), ("总价计算正确性", 20),
                                  ("政策合规性判断", 15), ("审批信息正确性", 10)]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "前置检查失败"
            })
        total_score = sum(d["score"] for d in details)
        # 写结果
        result = {
            "total_score": total_score,
            "details": details
        }
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ============ 4. 航班选择正确性 (20分) ============
    # 唯一正确答案：SkyBook的SKY203，因为总价最低且合规（总价=2800+40+25=2865）
    # 或SkyBook的SKY101（总价=3200+45+30=3275）也合规但较贵；政策max_cost=5000，两者都合规。
    # 但根据业务常识，应选最便宜的合规航班（SKY203总价2865），且不超过requires_approval_above(3000)，故approval_required应为false。
    # 但如果选SKY101（3275>3000则需要审批）。需要agent自行决定。我们设定唯一答案：选SKY203，总价2865，合规，无需审批，excess_amount=0。
    score = 0
    max_score = 20
    reasons = []
    sf = data.get("selected_flight", {})
    # 检查关键字段
    if sf.get("flight_no") == "SKY203" and sf.get("platform") == "SkyBook":
        score += 10
    else:
        reasons.append(f"航班号/platform不匹配，得到 {sf.get('flight_no')}/{sf.get('platform')}，期望SKY203/SkyBook")
    if sf.get("origin") == "JFK" and sf.get("destination") == "LHR" and sf.get("cabin_class") == "business":
        score += 5
    else:
        reasons.append("起降地或舱位错误")
    if sf.get("departure_date") == "2026-06-15":
        score += 5
    else:
        reasons.append("出发日期错误")
    details.append({
        "item": "航班选择正确性",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reasons if reasons else "正确选择了最优惠合规航班"
    })

    # ============ 5. 总价计算正确性 (20分) ============
    expected_total = 2800.0 + 40.0 + 25.0  # SKY203
    actual_total = data.get("total_cost")
    score = 0
    max_score = 20
    if isinstance(actual_total, (int, float)) and abs(actual_total - expected_total) < 0.01:
        score = 20
        reason = f"总价正确 ({expected_total})"
    else:
        reason = f"总价错误，期望 {expected_total}，实际 {actual_total}"
    details.append({
        "item": "总价计算正确性",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reason
    })

    # ============ 6. 政策合规性判断 (15分) ============
    score = 0
    max_score = 15
    compliant = data.get("policy_compliant")
    if compliant is True:
        score += 10
    else:
        reasons = ["policy_compliant 应为 true"]
    # 检查是否引用了正确的政策版本
    policy_ref = data.get("policy_reference", {})
    if policy_ref.get("policy_id") == "travel_policy_business_v3" and policy_ref.get("version") == "3.2":
        score += 5
    else:
        reasons = reasons if reasons else []
        reasons.append("政策引用不正确")
    details.append({
        "item": "政策合规性判断",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reasons if reasons else "合规判断正确且引用了最新政策"
    })

    # ============ 7. 审批信息正确性 (10分) ============
    score = 0
    max_score = 10
    approval = data.get("approval_required")
    excess = data.get("excess_amount")
    # 因为总价2865 < 3000，所以不需要审批，excess应为0
    if approval is False and excess == 0:
        score = 10
        reason = "无需审批，超额金额为0"
    else:
        score = 0
        reason = f"审批信息错误: approval_required={approval}, excess_amount={excess}, 期望 false和0"
    details.append({
        "item": "审批信息正确性",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reason
    })

    # ============ 汇总 ============
    total_score = sum(d["score"] for d in details)
    # 输出分数
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    evaluate()
