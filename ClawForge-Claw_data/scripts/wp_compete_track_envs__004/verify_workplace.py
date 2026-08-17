import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 reports 目录是否存在 (10分)
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        details.append({"item": "reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "reports/ 目录存在"})
        total_score += 10
    else:
        details.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/ 目录不存在"})
        # 如果目录不存在，后续检查无法进行，直接返回
        return total_score, details

    # 2. 检查 policy_impact_summary.json 是否存在 (10分)
    summary_path = os.path.join(reports_dir, "policy_impact_summary.json")
    if os.path.isfile(summary_path):
        details.append({"item": "policy_impact_summary.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "policy_impact_summary.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        return total_score, details

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(summary_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        return total_score, details

    # 4. 检查是否包含 affected_competitors 字段或类似结构 (20分)
    # 允许两种格式：顶层列表，或包含 "affected_competitors" 键
    competitors_list = None
    if isinstance(data, list):
        competitors_list = data
    elif isinstance(data, dict):
        if "affected_competitors" in data:
            competitors_list = data["affected_competitors"]
        elif "competitors" in data:
            competitors_list = data["competitors"]
        # 如果都不是，尝试直接取字典的值列表 (可能只有一个键)
        else:
            for v in data.values():
                if isinstance(v, list):
                    competitors_list = v
                    break
    if competitors_list is not None and len(competitors_list) > 0:
        details.append({"item": "Contains a list of affected competitors", "score": 20, "max_score": 20, "passed": True, "reason": f"找到列表，包含 {len(competitors_list)} 个条目"})
        total_score += 20
    else:
        details.append({"item": "Contains a list of affected competitors", "score": 0, "max_score": 20, "passed": False, "reason": "未找到竞品列表"})
        # 后面无法继续，但可返回
        return total_score, details

    # 5. 检查是否包含正确的竞品名称 "DataFlow AI" (30分)
    # 同时检查其 impact_level 是否为 "high" (若列表项是字典，则检查键；若列表项是字符串，则直接检查名称)
    found_correct = False
    impact_high_correct = False
    for item in competitors_list:
        if isinstance(item, dict):
            name = item.get("name") or item.get("competitor_name") or ""
            impact = item.get("impact_level") or item.get("impact") or ""
            if "DataFlow AI" in name:
                found_correct = True
                if "high" in str(impact).lower():
                    impact_high_correct = True
        elif isinstance(item, str):
            if "DataFlow AI" in item:
                found_correct = True
                # 如果只有字符串，我们允许 impact_level 在别处，但简化处理：认为准确名称就足够
                impact_high_correct = True  # 宽松处理

    if found_correct:
        details.append({"item": "Contains 'DataFlow AI' as affected competitor", "score": 30, "max_score": 30, "passed": True, "reason": "竞品名称正确"})
        total_score += 30
    else:
        details.append({"item": "Contains 'DataFlow AI' as affected competitor", "score": 0, "max_score": 30, "passed": False, "reason": "未找到 DataFlow AI"})

    if impact_high_correct:
        details.append({"item": "Impact level for DataFlow AI is 'high'", "score": 20, "max_score": 20, "passed": True, "reason": "影响等级正确"})
        total_score += 20
    else:
        # 如果名字都对了但缺少 impact_level，给部分分？为了细化，这里给 0
        details.append({"item": "Impact level for DataFlow AI is 'high'", "score": 0, "max_score": 20, "passed": False, "reason": "未正确标明影响等级为 high"})

    # 6. 额外加分：确保没有把干扰竞品（CloudMajor、SmartSaaS、TechCorp）错误列入？我们可以在细节中加扣分项，但为了简化，这里不额外扣分。
    # 但可以检查如果列表只有一个条目且是 DataFlow AI，加10分（可选）
    if len(competitors_list) == 1 and found_correct:
        details.append({"item": "Only one competitor listed (correct precision)", "score": 10, "max_score": 10, "passed": True, "reason": "结果精确只包含一个竞品"})
        total_score += 10
    else:
        # 即使有多个，不扣分，但也不加分
        details.append({"item": "Only one competitor listed (correct precision)", "score": 0, "max_score": 10, "passed": False, "reason": f"列表包含 {len(competitors_list)} 个竞品，期望仅1个"})

    # 总分封顶100
    final_score = min(total_score, 100)
    return final_score, details

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score, details = verify(workspace)
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
