import json
import os
import sys
import math

def verify(workspace: str):
    results = []
    total_score = 0

    # 1. 检查 ops/regulatory_impact.json 是否存在
    target_path = os.path.join(workspace, "ops", "regulatory_impact.json")
    if not os.path.exists(target_path):
        results.append({
            "item": "存在结果文件 ops/regulatory_impact.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 无法继续判定，直接输出
        write_score(total_score, results, workspace)
        return

    results.append({
        "item": "存在结果文件 ops/regulatory_impact.json",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "文件存在"
    })

    # 2. 解析JSON
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        results.append({
            "item": "JSON格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {e}"
        })
        write_score(total_score, results, workspace)
        return

    results.append({
        "item": "JSON格式合法",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "合法JSON"
    })

    # 3. 检查必要字段（允许自定义字段名，但必须包含三个关键值）
    # 我们期望字段包括：影响竞品列表、平均市场份额、营收最高竞品
    # 通过模糊匹配：找包含 "competitor" 或 "affected" 的 key，包含 "average" 或 "mean" 的 key，包含 "highest" 或 "top" 或 "max" 的 key
    # 更稳妥：直接检查三个值的类型
    affected_found = False
    avg_share_found = False
    top_revenue_found = False

    affected_competitors = None
    avg_market_share = None
    highest_revenue_competitor = None

    for key, value in data.items():
        # 尝试识别 受影响竞品列表
        if isinstance(value, list) and len(value) > 0 and all(isinstance(v, str) for v in value):
            # 可能是竞品名称列表
            if ("competitor" in key.lower() or "affected" in key.lower() or "list" in key.lower()):
                affected_competitors = value
                affected_found = True
        # 尝试识别平均市场份额
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            # 如果是小数且小于1，可能是市场份额
            if 0 < value < 1:
                if "average" in key.lower() or "mean" in key.lower() or "share" in key.lower():
                    avg_market_share = value
                    avg_share_found = True
        # 尝试识别营收最高竞品名称
        if isinstance(value, str) and ("revenue" in key.lower() or "highest" in key.lower() or "top" in key.lower() or "max" in key.lower()):
            highest_revenue_competitor = value
            top_revenue_found = True
        # 备选：如果键包含 'highest' 且值是字符串
        if isinstance(value, str) and ("revenue" in key.lower()):
            highest_revenue_competitor = value
            top_revenue_found = True

    # 如果以上启发式失败，尝试直接使用预设的字段名（允许用户不同命名）
    # 但为了准确，我们再检查一次：数据中必须包含受影响的竞品名称列表（从政策文件中推导出）
    # 预设答案：影响竞品为 DataFlow AI 和 TechCorp
    expected_competitors = ["DataFlow AI", "TechCorp"]
    expected_avg_share = 0.17  # (0.12+0.22)/2 = 0.17
    expected_top_revenue = "TechCorp"  # revenue 65B vs 12B

    # 先用匹配计算
    # 如果 affected_competitors 存在，检查内容
    if affected_competitors:
        # 对两者进行匹配（无视顺序）
        actual_set = set(affected_competitors)
        expected_set = set(expected_competitors)
        if actual_set == expected_set:
            results.append({
                "item": "受影响竞品列表正确",
                "score": 25,
                "max_score": 25,
                "passed": True,
                "reason": f"竞品列表为 {sorted(affected_competitors)}"
            })
        else:
            results.append({
                "item": "受影响竞品列表正确",
                "score": 0,
                "max_score": 25,
                "passed": False,
                "reason": f"期望 {expected_competitors}，实际 {affected_competitors}"
            })
    else:
        results.append({
            "item": "受影响竞品列表正确",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": "未找到受影响竞品列表"
        })

    # 平均市场份额
    if avg_market_share is not None:
        if math.isclose(avg_market_share, expected_avg_share, rel_tol=1e-3):
            results.append({
                "item": "平均市场份额计算正确",
                "score": 25,
                "max_score": 25,
                "passed": True,
                "reason": f"平均市场份额为 {avg_market_share}"
            })
        else:
            results.append({
                "item": "平均市场份额计算正确",
                "score": 0,
                "max_score": 25,
                "passed": False,
                "reason": f"期望 {expected_avg_share}，实际 {avg_market_share}"
            })
    else:
        results.append({
            "item": "平均市场份额计算正确",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": "未找到平均市场份额字段"
        })

    # 营收最高竞品
    if highest_revenue_competitor is not None:
        if highest_revenue_competitor == expected_top_revenue:
            results.append({
                "item": "营收最高竞品名称正确",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": f"营收最高竞品为 {highest_revenue_competitor}"
            })
        else:
            results.append({
                "item": "营收最高竞品名称正确",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"期望 {expected_top_revenue}，实际 {highest_revenue_competitor}"
            })
    else:
        results.append({
            "item": "营收最高竞品名称正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "未找到营收最高竞品字段"
        })

    # 汇总得分
    total_score = sum(r["score"] for r in results)
    write_score(total_score, results, workspace)

def write_score(total, details, workspace):
    score_obj = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_obj, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
