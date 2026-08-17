import json
import os
import sys
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    max_total = 100

    # 1. 检查预期目录结构 (10分)
    required_dirs = ["ops"]
    all_dirs_exist = True
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            all_dirs_exist = False
            break
    if all_dirs_exist:
        score_details.append({"item": "目录结构正确", "score": 10, "max_score": 10, "passed": True, "reason": "ops 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "目录结构正确", "score": 0, "max_score": 10, "passed": False, "reason": "缺失必备目录 ops"})

    # 2. 检查目标报告文件存在性 (5分)
    report_path = os.path.join(workspace, "ops/market_intel_summary.json")
    if os.path.isfile(report_path):
        score_details.append({"item": "报告文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops/market_intel_summary.json 已生成"})
        total_score += 5
    else:
        score_details.append({"item": "报告文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到文件 ops/market_intel_summary.json"})
        # 后续检查无法进行，直接输出结果
        _write_score(workspace, total_score, score_details)
        return

    # 3. 解析 JSON 文件 (5分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON 格式合法", "score": 5, "max_score": 5, "passed": True, "reason": "文件可正确解析为JSON"})
        total_score += 5
    except Exception as e:
        score_details.append({"item": "JSON 格式合法", "score": 0, "max_score": 5, "passed": False, "reason": f"JSON解析失败: {e}"})
        _write_score(workspace, total_score, score_details)
        return

    # 4. 检查顶层键 (10分)
    required_keys = ["ai_ml_competitors", "eu_high_impact_policies", "referral_users_count"]
    missing_keys = [k for k in required_keys if k not in data]
    if not missing_keys:
        score_details.append({"item": "报告的顶层键完整", "score": 10, "max_score": 10, "passed": True, "reason": f"包含所有必需键: {required_keys}"})
        total_score += 10
    else:
        score_details.append({"item": "报告的顶层键完整", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少键: {missing_keys}"})
        # 后续检查无法继续
        _write_score(workspace, total_score, score_details)
        return

    # 5. 检查 ai_ml_competitors 字段 (30分)
    comp = data.get("ai_ml_competitors", {})
    comp_subkeys = ["avg_market_share", "total_revenue", "count"]
    comp_missing = [k for k in comp_subkeys if k not in comp]
    if comp_missing:
        score_details.append({"item": "ai_ml_competitors 子字段", "score": 0, "max_score": 30, "passed": False, "reason": f"缺少子字段: {comp_missing}"})
    else:
        # 预期值
        expected_count = 3
        expected_revenue = 850000000 + 420000000 + 150000000  # 1420000000
        expected_avg_share = (0.12 + 0.08 + 0.05) / 3  # 0.083333...
        # 允许浮点误差 0.001
        actual_count = comp.get("count")
        actual_revenue = comp.get("total_revenue")
        actual_avg = comp.get("avg_market_share")
        errors = []
        sub_score = 30
        if actual_count != expected_count:
            errors.append(f"count 预期 {expected_count}，实际 {actual_count}")
            sub_score -= 10
        if actual_revenue != expected_revenue:
            errors.append(f"total_revenue 预期 {expected_revenue}，实际 {actual_revenue}")
            sub_score -= 10
        if not (math.isclose(actual_avg, expected_avg_share, abs_tol=1e-4)):
            errors.append(f"avg_market_share 预期 {expected_avg_share}，实际 {actual_avg}")
            sub_score -= 10
        if sub_score < 0:
            sub_score = 0
        reason = "数值正确" if not errors else "; ".join(errors)
        score_details.append({
            "item": "ai_ml_competitors 数值正确",
            "score": sub_score,
            "max_score": 30,
            "passed": sub_score == 30,
            "reason": reason
        })
        total_score += sub_score

    # 6. 检查 eu_high_impact_policies (20分)
    eu_policies = data.get("eu_high_impact_policies")
    expected_eu = 1  # 只有 eu_dma 满足 (high, EU, active)
    if isinstance(eu_policies, int) and eu_policies == expected_eu:
        score_details.append({
            "item": "eu_high_impact_policies",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"预期 {expected_eu}，实际 {eu_policies}"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "eu_high_impact_policies",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"预期 {expected_eu}，实际 {eu_policies}"
        })

    # 7. 检查 referral_users_count (20分)
    referral_users = data.get("referral_users_count")
    expected_referral = 3  # alice, bob, david (frank 带空格不算，grace 拼写错误不算，henry 缺失不算)
    if isinstance(referral_users, int) and referral_users == expected_referral:
        score_details.append({
            "item": "referral_users_count",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"预期 {expected_referral}，实际 {referral_users}"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "referral_users_count",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"预期 {expected_referral}，实际 {referral_users}"
        })

    # 输出结果
    _write_score(workspace, total_score, score_details)


def _write_score(workspace, total_score, details):
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Total score: {total_score}/100")


if __name__ == "__main__":
    main()
