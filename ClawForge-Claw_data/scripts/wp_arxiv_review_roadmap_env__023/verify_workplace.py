import sys
import os
import json

def verify(workspace: str):
    scores = []
    total = 0

    # 1. output 目录是否存在（10分）
    output_dir = os.path.join(workspace, "output")
    if os.path.isdir(output_dir):
        scores.append({"item": "output 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "output/ 目录已创建"})
        total += 10
    else:
        scores.append({"item": "output 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 output/ 目录"})
        # 如果目录不存在，后面无法检查文件，但继续检查细节会报错，所以提前返回
        write_score(workspace, scores, total)
        return

    # 2. review.json 文件存在（10分）
    review_path = os.path.join(workspace, "output", "review.json")
    if os.path.isfile(review_path):
        scores.append({"item": "review.json 文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "output/review.json 已创建"})
        total += 10
    else:
        scores.append({"item": "review.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 output/review.json"})
        write_score(workspace, scores, total)
        return

    # 3. JSON 格式合法（10分）
    try:
        with open(review_path, "r") as f:
            data = json.load(f)
        scores.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可正确解析为 JSON"})
        total += 10
    except json.JSONDecodeError as e:
        scores.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        write_score(workspace, scores, total)
        return

    # 4. 包含必要字段 direction, papers_used, roadmap（10分）
    missing_fields = []
    for field in ["direction", "papers_used", "roadmap"]:
        if field not in data:
            missing_fields.append(field)
    if not missing_fields:
        scores.append({"item": "包含必要字段", "score": 10, "max_score": 10, "passed": True, "reason": "字段 direction, papers_used, roadmap 均存在"})
        total += 10
    else:
        scores.append({"item": "包含必要字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {', '.join(missing_fields)}"})
        write_score(workspace, scores, total)
        return

    # 5. direction 正确（10分）
    if data["direction"] == "efficient_vision":
        scores.append({"item": "direction 正确", "score": 10, "max_score": 10, "passed": True, "reason": "direction 为 'efficient_vision'"})
        total += 10
    else:
        scores.append({"item": "direction 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"direction 应为 'efficient_vision'，实际为 '{data['direction']}'"})
        # 继续检查其他项，但方向错误可能影响论文选择，但论文列表仍可能正确？我们仍继续评分

    # 6. papers_used 列表长度正确（10分）
    expected_papers = ["paper_001", "paper_002", "paper_003", "paper_004", "paper_005"]  # 按年份排序
    papers_used = data.get("papers_used", [])
    if len(papers_used) == 5:
        scores.append({"item": "papers_used 长度正确", "score": 10, "max_score": 10, "passed": True, "reason": "包含5篇论文"})
        total += 10
    else:
        scores.append({"item": "papers_used 长度正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望5篇，实际 {len(papers_used)} 篇"})

    # 7. papers_used 每个ID正确且顺序正确（每个ID 6分，共30分）
    correct_order = True
    for i, expected_id in enumerate(expected_papers):
        if i < len(papers_used) and papers_used[i] == expected_id:
            scores.append({"item": f"papers_used[{i}] 正确 ({expected_id})", "score": 6, "max_score": 6, "passed": True, "reason": f"位置{i}为 {expected_id}"})
            total += 6
        else:
            actual_id = papers_used[i] if i < len(papers_used) else "缺失"
            scores.append({"item": f"papers_used[{i}] 正确 ({expected_id})", "score": 0, "max_score": 6, "passed": False, "reason": f"期望 {expected_id}，实际 {actual_id}"})
            correct_order = False

    # 8. roadmap 非空（10分）
    if isinstance(data.get("roadmap"), list) and len(data["roadmap"]) > 0:
        scores.append({"item": "roadmap 非空", "score": 10, "max_score": 10, "passed": True, "reason": "roadmap 为包含至少一个阶段的列表"})
        total += 10
    else:
        scores.append({"item": "roadmap 非空", "score": 0, "max_score": 10, "passed": False, "reason": "roadmap 为空或不是列表"})

    write_score(workspace, scores, total)

def write_score(workspace, details, total_score):
    score_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
