import sys
import os
import json
import csv
import math
from collections import defaultdict

def verify(workspace):
    score = 0
    max_score = 100
    details = []

    # 1. 检查必需目录和文件 (15分)
    # 目录 analysis 存在
    if os.path.isdir(os.path.join(workspace, "analysis")):
        score += 5
        details.append({"item": "analysis directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "OK"})
    else:
        details.append({"item": "analysis directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing directory analysis"})

    # 文件 category_summary.json 存在
    result_path = os.path.join(workspace, "analysis", "category_summary.json")
    if os.path.isfile(result_path):
        score += 10
        details.append({"item": "category_summary.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "OK"})
    else:
        details.append({"item": "category_summary.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 后续无法检查，直接结束
        details.append({"item": "data correctness", "score": 0, "max_score": 75, "passed": False, "reason": "Result file missing"})
        total = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(total, f, indent=2)
        return

    # 2. 读取结果和隐藏答案 (先检查结果合法性，再比对)
    try:
        with open(result_path, "r") as f:
            result = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON parse", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        score += 0
        # 其他项无法继续
        details.append({"item": "data correctness", "score": 0, "max_score": 65, "passed": False, "reason": "Result invalid"})
        total = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(total, f, indent=2)
        return

    # 检查 result 是否为列表
    if not isinstance(result, list):
        details.append({"item": "JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "Expected a list of category entries"})
        score += 0
        details.append({"item": "data correctness", "score": 0, "max_score": 65, "passed": False, "reason": "Invalid structure"})
        total = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(total, f, indent=2)
        return
    else:
        score += 10
        details.append({"item": "JSON parse & structure", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON list"})

    # 3. 读取隐藏答案
    solution_path = os.path.join(workspace, "_meta", "solution.json")
    if not os.path.isfile(solution_path):
        details.append({"item": "solution reference", "score": 0, "max_score": 0, "passed": False, "reason": "Solution file missing (internal error)"})
        # 无法比对，但可以尝试从原始数据重新计算？为简化，此处不实现
        total = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(total, f, indent=2)
        return

    with open(solution_path, "r") as f:
        expected = json.load(f)

    # 4. 检查类别数匹配 (10分)
    result_cats = {item["category"] for item in result}
    expected_cats = {item["category"] for item in expected}
    if result_cats == expected_cats:
        score += 10
        details.append({"item": "category set match", "score": 10, "max_score": 10, "passed": True, "reason": "All expected categories present"})
    else:
        missing = expected_cats - result_cats
        extra = result_cats - expected_cats
        reason = f"Missing: {missing}, Extra: {extra}" if missing else f"Extra: {extra}"
        details.append({"item": "category set match", "score": 0, "max_score": 10, "passed": False, "reason": reason})
        # 后面单项检查会因缺少类别而失败，但不影响总分数上限

    # 5. 检查每个类别的字段及数值 (最多 65 分，每个类别等分)
    # 先按类别建立 expected 字典
    exp_dict = {e["category"]: e for e in expected}
    category_count = len(expected)
    if category_count == 0:
        # 无类别时特殊处理：允许空列表？
        if len(result) == 0:
            score += 65
            details.append({"item": "no categories", "score": 65, "max_score": 65, "passed": True, "reason": "Both result and expected are empty"})
        else:
            details.append({"item": "unexpected categories", "score": 0, "max_score": 65, "passed": False, "reason": "Expected empty, got categories"})
    else:
        points_per_cat = 65 // category_count  # 整除，余数舍去
        remainder = 65 % category_count
        for i, (cat, exp) in enumerate(exp_dict.items()):
            max_this = points_per_cat + (1 if i < remainder else 0)
            item_name = f"Category '{cat}' correctness"
            # 在 result 中找到对应条目
            found = None
            for r in result:
                if r.get("category") == cat:
                    found = r
                    break
            if found is None:
                details.append({"item": item_name, "score": 0, "max_score": max_this, "passed": False, "reason": f"Missing category '{cat}' in result"})
                continue
            # 检查字段
            if "total_sales" not in found or "average_order" not in found:
                details.append({"item": item_name, "score": 0, "max_score": max_this, "passed": False, "reason": "Missing required fields"})
                continue
            # 数值比较（允许 0.01 容忍误差）
            ts_ok = math.isclose(found["total_sales"], exp["total_sales"], abs_tol=0.01)
            ao_ok = math.isclose(found["average_order"], exp["average_order"], abs_tol=0.01)
            if ts_ok and ao_ok:
                score += max_this
                details.append({"item": item_name, "score": max_this, "max_score": max_this, "passed": True, "reason": f"total_sales={found['total_sales']}, average_order={found['average_order']}"})
            else:
                reason = f"Expected total_sales={exp['total_sales']} got {found['total_sales']}; " \
                         f"Expected average_order={exp['average_order']} got {found['average_order']}"
                details.append({"item": item_name, "score": 0, "max_score": max_this, "passed": False, "reason": reason})

    # 写入最终分数
    total = {"total_score": score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(total, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
