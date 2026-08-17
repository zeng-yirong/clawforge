import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "output", "selected_papers.json")
    details = []
    total_score = 0

    # 1. 检查 output 目录是否存在（10分）
    output_dir = os.path.join(workspace, "output")
    if os.path.isdir(output_dir):
        details.append({"item": "output 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "output 目录已创建"})
        total_score += 10
    else:
        details.append({"item": "output 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "output 目录不存在"})

    # 2. 检查 selected_papers.json 是否存在且为合法 JSON（20分）
    if not os.path.isfile(result_path):
        details.append({"item": "selected_papers.json 存在且合法", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        # 写入分数并退出（后续无法继续检查）
        _write_score(details, total_score, workspace)
        return

    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            details.append({"item": "selected_papers.json 存在且合法", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 顶层不是数组"})
            _write_score(details, total_score, workspace)
            return
        details.append({"item": "selected_papers.json 存在且合法", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在且为合法 JSON 数组"})
        total_score += 20
    except (json.JSONDecodeError, IOError) as e:
        details.append({"item": "selected_papers.json 存在且合法", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析错误: {str(e)}"})
        _write_score(details, total_score, workspace)
        return

    # 3. 检查每项是否包含必要字段 paper_id, title, citations（15分）
    required_fields = {"paper_id", "title", "citations"}
    all_have_fields = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            all_have_fields = False
            break
        if not required_fields.issubset(item.keys()):
            all_have_fields = False
            break
    if all_have_fields and len(data) > 0:
        details.append({"item": "每项包含 paper_id, title, citations", "score": 15, "max_score": 15, "passed": True, "reason": "所有元素均包含所需字段"})
        total_score += 15
    else:
        details.append({"item": "每项包含 paper_id, title, citations", "score": 0, "max_score": 15, "passed": False, "reason": "缺失字段或元素不是字典"})

    # 4. 检查数据内容是否正确（55分，细粒度）
    # 预期结果：按 citations 降序排列的 4 篇论文（年份2021-2023，direction=tool_augmented_reasoning）
    expected = [
        {"paper_id": "123", "title": "Tool-Augmented Reasoning", "citations": 50},
        {"paper_id": "456", "title": "Reasoning with External Tools", "citations": 30},
        {"paper_id": "789", "title": "Augmented Reasoning in NLP", "citations": 20},
        {"paper_id": "112", "title": "Reasoning via Tool Integration", "citations": 10},
    ]

    if len(data) != len(expected):
        details.append({"item": "数据内容完全正确", "score": 0, "max_score": 55, "passed": False, "reason": f"数组长度不符，期望 {len(expected)} 项，实际 {len(data)} 项"})
        _write_score(details, total_score, workspace)
        return

    match = True
    for i, (actual, exp) in enumerate(zip(data, expected)):
        if (actual.get("paper_id") != exp["paper_id"] or
            actual.get("title") != exp["title"] or
            actual.get("citations") != exp["citations"]):
            match = False
            reason = f"第 {i+1} 项不匹配：期望 {exp}，实际 {{'paper_id': {actual.get('paper_id')}, 'title': {actual.get('title')}, 'citations': {actual.get('citations')}}}"
            break

    if match:
        details.append({"item": "数据内容完全正确", "score": 55, "max_score": 55, "passed": True, "reason": "论文列表、顺序、字段值均与预期一致"})
        total_score += 55
    else:
        details.append({"item": "数据内容完全正确", "score": 0, "max_score": 55, "passed": False, "reason": reason})

    _write_score(details, total_score, workspace)


def _write_score(details, total_score, workspace):
    # 确保总分不超过100且为整数
    total_score = min(total_score, 100)
    result = {"total_score": total_score, "details": details}
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
