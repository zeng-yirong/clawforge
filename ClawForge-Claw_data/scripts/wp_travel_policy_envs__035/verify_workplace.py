import sys
import os
import json
import math

def score_check(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查 (满分10)
    required_dirs = ["data/platforms", "data/policies", "ops"]
    dir_ok = True
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dir_ok = False
    if dir_ok:
        details.append({"item": "目录结构存在", "score": 10, "max_score": 10, "passed": True, "reason": "所有必要目录都存在"})
        total_score += 10
    else:
        details.append({"item": "目录结构存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少必要目录"})

    # 2. 结果文件存在且格式合法 (满分10)
    result_path = os.path.join(workspace, "ops/booking_decision.json")
    if not os.path.isfile(result_path):
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/booking_decision.json 不存在"})
        # 无法继续，返回
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return
    try:
        with open(result_path, "r") as f:
            decision = json.load(f)
        details.append({"item": "结果文件格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "结果文件格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 3. 必需字段存在 (满分10)
    required_fields = ["selected_platform", "total_cost", "policy_id", "requires_approval", "auto_approved"]
    missing = [f for f in required_fields if f not in decision]
    if not missing:
        details.append({"item": "必需字段完整", "score": 10, "max_score": 10, "passed": True, "reason": "所有必需字段存在"})
        total_score += 10
    else:
        details.append({"item": "必需字段完整", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing}"})
        # 但继续评分可能不可靠，先跳过后续计算
        # 后续检查将因缺少字段而失败，但继续
        # 这里我们仍继续，但后面会扣分

    # 4. 平台选择正确性 (满分30)
    # 期望 selected_platform = "SkyBook"
    expected_platform = "SkyBook"
    if decision.get("selected_platform") == expected_platform:
        details.append({"item": "平台选择正确", "score": 30, "max_score": 30, "passed": True, "reason": f"选择了最低成本的活跃平台 {expected_platform}"})
        total_score += 30
    else:
        details.append({"item": "平台选择正确", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {expected_platform}，实际 {decision.get('selected_platform')}"})

    # 5. 总成本计算正确 (满分30)
    # 预期总成本 = SkyBook: base_price=4500, transaction_fee=50, service_fee=100, 折扣5% (应用于总价?)
    # 根据平台定义：discounts = [{"type": "percentage", "value": 0.05}]，我们假定折扣应用于 base+手续费+服务费的总和。
    # 无其他折扣/促销作用于 SkyBook。所以 total = (4500+50+100)*(1-0.05)=4650*0.95=4417.5? 但实际折扣可能只应用于base？为了唯一，我们明确：
    # 通常折扣是应用于票价 base_price，但为了简单且无歧义，我们定义：总成本 = (base_price + transaction_fee + service_fee) * (1 - 折扣比例)
    # 但折扣比例0.05，所以 (4500+50+100)=4650, 4650*0.95=4417.5。但这样有小数点。为了便于比较，我们允许浮点数误差。
    # 但我们可以重新检查平台数据：SkyBook折扣类型是percentage，value=0.05。但还有促销空列表。所以唯一答案应为4417.5。
    # 然而我们也可以定义为折扣只应用于base_price，那么 total = 4500*0.95 + 50 + 100 = 4275+150=4425。需要唯一。
    # 必须在prompt中暗示？但prompt不能泄露。但env_builder已定义，agent需自行推断。为了客观，我们选择常见解释：折扣应用于总费用。我们取4417.5。
    # 但为了便于比较，我们使用 math.isclose 容忍误差。
    expected_cost = 4417.5  # (4500+50+100)*0.95
    actual_cost = decision.get("total_cost")
    if actual_cost is not None and math.isclose(actual_cost, expected_cost, rel_tol=1e-3):
        details.append({"item": "总成本计算正确", "score": 30, "max_score": 30, "passed": True, "reason": f"计算值 {actual_cost} 与期望 {expected_cost} 一致"})
        total_score += 30
    else:
        details.append({"item": "总成本计算正确", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {expected_cost}，实际 {actual_cost}"})

    # 6. 政策选择正确 (满分10)
    # 应选择 acme_business_v2 (最新版)
    expected_policy = "acme_business_v2"
    if decision.get("policy_id") == expected_policy:
        details.append({"item": "政策选择正确", "score": 10, "max_score": 10, "passed": True, "reason": f"选择了最新商务政策 {expected_policy}"})
        total_score += 10
    else:
        details.append({"item": "政策选择正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_policy}，实际 {decision.get('policy_id')}"})

    # 7. 审批状态判断 (满分10)
    # requires_approval应为true (因为总成本>3000), auto_approved应为false
    # 注意：若总成本 > requires_approval_above 且 <= max_cost_per_booking，则需要批准，auto_approved=false
    # 这里总成本4417.5 > 3000 且 < 5000，所以 requires_approval=True, auto_approved=False
    expected_requires = True
    expected_auto = False
    actual_requires = decision.get("requires_approval")
    actual_auto = decision.get("auto_approved")
    if actual_requires == expected_requires and actual_auto == expected_auto:
        details.append({"item": "审批状态正确", "score": 10, "max_score": 10, "passed": True, "reason": f"requires_approval={actual_requires}, auto_approved={actual_auto}"})
        total_score += 10
    else:
        details.append({"item": "审批状态正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 (requires={expected_requires}, auto={expected_auto})，实际 ({actual_requires}, {actual_auto})"})

    # 最终结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_check(workspace)
