import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # ------------------------------------------------------------
    # 1. 目录和文件存在性 (10)
    # ------------------------------------------------------------
    ops_dir = os.path.join(workspace, "ops")
    result_path = os.path.join(ops_dir, "overbudget.json")
    item = {"item": "ops/overbudget.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if os.path.isdir(ops_dir) and os.path.isfile(result_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "文件存在"
    else:
        item["reason"] = "文件或目录缺失"
    score_details.append(item)
    if item["passed"]:
        total_score += 10

    # ------------------------------------------------------------
    # 2. JSON 合法性 (10)
    # ------------------------------------------------------------
    item = {"item": "overbudget.json 为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "JSON解析成功"
    except Exception as e:
        item["reason"] = f"JSON解析失败: {e}"
        # 如果文件不存在或格式错误，直接返回总分
        write_score(total_score, score_details, workspace)
        return
    score_details.append(item)
    total_score += 10

    # ------------------------------------------------------------
    # 3. 内容为列表 (10)
    # ------------------------------------------------------------
    item = {"item": "根元素为列表", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if isinstance(data, list):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "是列表"
    else:
        item["reason"] = f"根元素类型为 {type(data).__name__}"
    score_details.append(item)
    if item["passed"]:
        total_score += 10

    # ------------------------------------------------------------
    # 4. 列表长度 (10)
    # ------------------------------------------------------------
    item = {"item": "超支项数量正确（1项）", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if len(data) == 1:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "长度为1"
    else:
        item["reason"] = f"长度为 {len(data)}，期望1"
    score_details.append(item)
    if item["passed"]:
        total_score += 10

    # ------------------------------------------------------------
    # 5. 字段验证与数值计算 (60)
    # ------------------------------------------------------------
    entry = data[0] if data else {}

    # 5a. 超支类别 (20)
    item = {"item": "超支类别为 accommodation", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if entry.get("category") == "accommodation":
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "类别正确"
    else:
        item["reason"] = f"类别为 {entry.get('category')}"
    score_details.append(item)
    if item["passed"]:
        total_score += 20

    # 5b. actual 数值 (15)
    item = {"item": "actual 为 2200.0", "score": 0, "max_score": 15, "passed": False, "reason": ""}
    actual = entry.get("actual")
    if isinstance(actual, (int, float)) and math.isclose(actual, 2200.0, rel_tol=1e-6):
        item["score"] = 15
        item["passed"] = True
        item["reason"] = f"actual = {actual}"
    else:
        item["reason"] = f"actual = {actual} (期望 2200.0)"
    score_details.append(item)
    if item["passed"]:
        total_score += 15

    # 5c. budget 数值 (15)
    item = {"item": "budget 为 1600.0", "score": 0, "max_score": 15, "passed": False, "reason": ""}
    budget = entry.get("budget")
    if isinstance(budget, (int, float)) and math.isclose(budget, 1600.0, rel_tol=1e-6):
        item["score"] = 15
        item["passed"] = True
        item["reason"] = f"budget = {budget}"
    else:
        item["reason"] = f"budget = {budget} (期望 1600.0)"
    score_details.append(item)
    if item["passed"]:
        total_score += 15

    # 5d. overspend 数值 (10)
    item = {"item": "overspend 为 600.0", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    overspend = entry.get("overspend")
    if isinstance(overspend, (int, float)) and math.isclose(overspend, 600.0, rel_tol=1e-6):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"overspend = {overspend}"
    else:
        item["reason"] = f"overspend = {overspend} (期望 600.0)"
    score_details.append(item)
    if item["passed"]:
        total_score += 10

    # 确保总分不超过100
    total_score = min(total_score, 100)
    write_score(total_score, score_details, workspace)

def write_score(total, details, workspace):
    output = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
