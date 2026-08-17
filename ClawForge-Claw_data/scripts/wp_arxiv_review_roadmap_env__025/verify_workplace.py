import os
import sys
import json

def verify(workspace: str):
    details = []
    total_score = 0

    # 1. ops 目录存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    item = {"item": "目录 'ops' 存在", "max_score": 10}
    if os.path.isdir(ops_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "找到 ops 目录"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "ops 目录缺失"
    details.append(item)
    total_score += item["score"]

    # 2. 产物文件存在 (10分)
    target_file = os.path.join(workspace, "ops", "top_cited_paper.json")
    item = {"item": "文件 ops/top_cited_paper.json 存在", "max_score": 10}
    if os.path.isfile(target_file):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "文件存在"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "文件缺失"
    details.append(item)
    total_score += item["score"]

    # 如果文件不存在，后续检查直接赋值0分并结束
    if not os.path.isfile(target_file):
        # 补充未检查项
        for name in ["JSON 格式合法", "包含字段 paper_id", "包含字段 title", "包含字段 citation_count",
                      "paper_id 值正确", "title 值正确", "citation_count 值正确", "无多余字段"]:
            details.append({"item": name, "max_score": 10, "score": 0, "passed": False, "reason": "前置文件缺失"})
        final_score = 0
        score_data = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_data, f, indent=2)
        print(f"Final score: {final_score}/100")
        return

    # 3. JSON 格式合法 (10分)
    item = {"item": "JSON 格式合法", "max_score": 10}
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "JSON 解析成功"
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"JSON 解析错误: {str(e)}"
        details.append(item)
        # 后续都不成立
        for name in ["包含字段 paper_id", "包含字段 title", "包含字段 citation_count",
                      "paper_id 值正确", "title 值正确", "citation_count 值正确", "无多余字段"]:
            details.append({"item": name, "max_score": 10, "score": 0, "passed": False, "reason": "JSON 无效"})
        total_score += item["score"]
        final_score = total_score
        score_data = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_data, f, indent=2)
        print(f"Final score: {final_score}/100")
        return

    details.append(item)
    total_score += item["score"]

    # 4-6. 检查字段存在 (每个10分)
    required_fields = ["paper_id", "title", "citation_count"]
    for field in required_fields:
        item = {"item": f"包含字段 '{field}'", "max_score": 10}
        if field in data:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = f"字段 '{field}' 存在"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"字段 '{field}' 缺失"
        details.append(item)
        total_score += item["score"]

    # 7. paper_id 值正确 (20分)
    expected_paper_id = "TAR-003"
    item = {"item": "paper_id 值正确 (应为 TAR-003)", "max_score": 20}
    actual = data.get("paper_id")
    if actual == expected_paper_id:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = f"paper_id 为 {actual}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"期望 {expected_paper_id}，实际 {actual}"
    details.append(item)
    total_score += item["score"]

    # 8. title 值正确 (10分)
    expected_title = "Chain-of-Thought with Tool Augmentation"
    item = {"item": "title 值正确", "max_score": 10}
    actual = data.get("title")
    if actual == expected_title:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"title 为 '{actual}'"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"期望 '{expected_title}'，实际 '{actual}'"
    details.append(item)
    total_score += item["score"]

    # 9. citation_count 值正确 (20分)
    expected_count = 3  # 被 TAR-001 和 TAR-002 和 EFF-001 引用，共3次（EFF-001引用它，TAR-001，TAR-002都引用）
    item = {"item": "citation_count 值正确 (应为 3)", "max_score": 20}
    actual = data.get("citation_count")
    if isinstance(actual, int) and actual == expected_count:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = f"citation_count 为 {actual}"
    elif isinstance(actual, (int, float)) and int(actual) == expected_count:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = f"citation_count 为 {actual}（整数等价）"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"期望 {expected_count}，实际 {actual}"
    details.append(item)
    total_score += item["score"]

    # 10. 无多余字段 (10分)
    expected_keys = {"paper_id", "title", "citation_count"}
    actual_keys = set(data.keys())
    extra = actual_keys - expected_keys
    item = {"item": "无多余字段", "max_score": 10}
    if not extra:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "字段集合完全匹配"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"发现多余字段: {extra}"
    details.append(item)
    total_score += item["score"]

    final_score = total_score
    score_data = {"total_score": final_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Final score: {final_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
