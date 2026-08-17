import sys
import os
import json
import math

def verify(workspace):
    score_details = []
    total_score = 0

    # 1. 检查 reports/competitive_analysis.json 是否存在
    expected_path = os.path.join(workspace, "reports", "competitive_analysis.json")
    if os.path.isfile(expected_path):
        score_details.append({
            "item": "reports/competitive_analysis.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已找到"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "reports/competitive_analysis.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 无法继续检查，返回
        write_score(workspace, total_score, score_details)
        return

    # 2. 合法性：JSON 解析
    try:
        with open(expected_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 格式有效",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析 JSON"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "JSON 格式有效",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        write_score(workspace, total_score, score_details)
        return

    # 3. JSON 顶层结构检查
    required_top_keys = ["average_market_share", "average_revenue", "competitors"]
    missing_keys = [k for k in required_top_keys if k not in data]
    if not missing_keys and isinstance(data.get("competitors"), list):
        score_details.append({
            "item": "JSON 顶层结构正确（包含 average_market_share, average_revenue, competitors 列表）",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "顶层字段齐全且 competitors 为列表"
        })
        total_score += 20
    else:
        reason = f"缺失字段: {missing_keys}" if missing_keys else "competitors 不是列表"
        score_details.append({
            "item": "JSON 顶层结构正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": reason
        })
        write_score(workspace, total_score, score_details)
        return

    competitors = data["competitors"]

    # 4. 筛选正确性：共 2 个竞品，且为 CloudMajor 和 TechCorp
    correct_names = {"CloudMajor", "TechCorp"}
    found_names = {c.get("name") for c in competitors}
    if found_names == correct_names:
        score_details.append({
            "item": "筛选出正确的竞品（仅 CloudMajor 和 TechCorp）",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"竞品名称正确: {sorted(found_names)}"
        })
        total_score += 30
    else:
        extra = found_names - correct_names
        missing = correct_names - found_names
        reason_parts = []
        if extra:
            reason_parts.append(f"多余竞品: {extra}")
        if missing:
            reason_parts.append(f"缺少竞品: {missing}")
        reason = "; ".join(reason_parts) if reason_parts else "竞品名称不正确"
        score_details.append({
            "item": "筛选出正确的竞品",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": reason
        })
        write_score(workspace, total_score, score_details)
        return

    # 5. 数值计算准确性
    # 预期的平均值：market_share=(0.35+0.25)/2=0.30; revenue=(5000+4000)/2=4500
    expected_avg_share = 0.30
    expected_avg_revenue = 4500.00
    tol = 1e-6
    share_ok = abs(data.get("average_market_share", -1) - expected_avg_share) < tol
    revenue_ok = abs(data.get("average_revenue", -1) - expected_avg_revenue) < tol

    # 检查每个竞品的字段值是否正确
    competitor_values_ok = True
    expected_competitors = {
        "CloudMajor": {"market_cap": 600, "growth_rate": 25, "market_share": 0.35, "revenue": 5000},
        "TechCorp": {"market_cap": 700, "growth_rate": 22, "market_share": 0.25, "revenue": 4000}
    }
    for comp in competitors:
        name = comp.get("name")
        if name not in expected_competitors:
            competitor_values_ok = False
            break
        for key, val in expected_competitors[name].items():
            if abs(comp.get(key, -1e9) - val) > 1e-6:
                competitor_values_ok = False
                break
        if not competitor_values_ok:
            break

    if share_ok and revenue_ok and competitor_values_ok:
        score_details.append({
            "item": "数值计算和字段值准确",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"平均市场份额={data['average_market_share']:.2f}, 平均营收={data['average_revenue']:.2f}, 所有竞品字段正确"
        })
        total_score += 30
    else:
        reasons = []
        if not share_ok:
            reasons.append(f"average_market_share={data.get('average_market_share')}，期望={expected_avg_share}")
        if not revenue_ok:
            reasons.append(f"average_revenue={data.get('average_revenue')}，期望={expected_avg_revenue}")
        if not competitor_values_ok:
            reasons.append("竞品对象内字段值不匹配")
        score_details.append({
            "item": "数值计算和字段值准确",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "; ".join(reasons)
        })

    write_score(workspace, total_score, score_details)

def write_score(workspace, total, details):
    output = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"评分完成，总分: {total}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
