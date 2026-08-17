import sys, os, json, csv, math, pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    wd = pathlib.Path(workspace)
    details = []
    total_score = 0

    # 1. 目录结构检查（10分）
    dirs_required = ["ops"]
    missing_dirs = [d for d in dirs_required if not (wd / d).is_dir()]
    if missing_dirs:
        details.append({"item": "目录结构", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少目录: {missing_dirs}"})
    else:
        details.append({"item": "目录结构", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 目录存在"})
        total_score += 10

    # 2. 结果文件存在性 & JSON合法性（10分）
    result_file = wd / "ops" / "booking_recommendation.json"
    if not result_file.is_file():
        details.append({"item": "结果文件", "score": 0, "max_score": 10, "passed": False, "reason": "ops/booking_recommendation.json 不存在"})
        print(json.dumps({"total_score": total_score, "details": details}))
        sys.exit(0)
    try:
        with open(result_file) as f:
            result = json.load(f)
        details.append({"item": "JSON合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件可解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        # 无法继续，输出当前分数
        write_score(total_score, details, workspace)
        return

    # 3. 检查结果中必要的字段（避免KeyError）
    required_fields = ["selected_platform_id", "total_cost", "policy_id", "policy_compliant", "remaining_budget"]
    missing_fields = [f for f in required_fields if f not in result]
    if missing_fields:
        details.append({"item": "必要字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {missing_fields}"})
    else:
        details.append({"item": "必要字段", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必需字段"})
        total_score += 10

    # 4. 平台选择正确性（30分）—— 必须选 skybook_001，且避开非活跃skybook_002
    if result.get("selected_platform_id") == "skybook_001":
        details.append({"item": "平台选择", "score": 30, "max_score": 30, "passed": True, "reason": "选择了正确的活跃平台SkyBook"})
        total_score += 30
    elif result.get("selected_platform_id") == "skybook_002":
        details.append({"item": "平台选择", "score": 0, "max_score": 30, "passed": False, "reason": "选择了非活跃平台skybook_002"})
    else:
        details.append({"item": "平台选择", "score": 0, "max_score": 30, "passed": False, "reason": f"选择了错误的平台: {result.get('selected_platform_id')}"})

    # 5. 总成本计算（20分）—— expected 1150.0
    expected_cost = 1150.0  # base 1100 + trans 20 + service 30 - discount 0
    actual_cost = result.get("total_cost")
    if isinstance(actual_cost, (int, float)) and math.isclose(actual_cost, expected_cost, rel_tol=1e-6):
        details.append({"item": "总成本计算", "score": 20, "max_score": 20, "passed": True, "reason": f"总成本正确 {actual_cost}"})
        total_score += 20
    else:
        details.append({"item": "总成本计算", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 {expected_cost}, 实际 {actual_cost}"})

    # 6. 政策引用（10分）—— 必须用 business policy
    if result.get("policy_id") == "travel_policy_acme_business":
        details.append({"item": "政策引用", "score": 10, "max_score": 10, "passed": True, "reason": "使用了正确的商务旅行政策"})
        total_score += 10
    else:
        details.append({"item": "政策引用", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 travel_policy_acme_business, 实际 {result.get('policy_id')}"})

    # 7. 剩余预算计算（20分）
    # 预期：总预算10000 - 历史花费(1500+500) = 8000，再扣除本次1150 => 6850
    expected_remaining = 6850.0
    actual_remaining = result.get("remaining_budget")
    if isinstance(actual_remaining, (int, float)) and math.isclose(actual_remaining, expected_remaining, rel_tol=1e-6):
        details.append({"item": "剩余预算计算", "score": 20, "max_score": 20, "passed": True, "reason": f"剩余预算正确 {actual_remaining}"})
        total_score += 20
    else:
        details.append({"item": "剩余预算计算", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 {expected_remaining}, 实际 {actual_remaining}"})

    # 可选：检查合规性和是否需要审批（非加分项，但可以记录）
    # 确保 total_score 不超过100
    total_score = min(total_score, 100)
    write_score(total_score, details, workspace)

def write_score(score, details, workspace):
    output = {"total_score": int(score), "details": details}
    with open(pathlib.Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output))

if __name__ == "__main__":
    main()
