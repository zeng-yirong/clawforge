import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # ----- 1. 检查 cache 目录是否存在 (10分) -----
    cache_dir = os.path.join(workspace, "cache")
    dir_exists = os.path.isdir(cache_dir)
    details.append({
        "item": "cache 目录存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "cache 目录存在" if dir_exists else "cache 目录缺失"
    })
    total_score += 10 if dir_exists else 0

    # ----- 2. 检查 cache/citation_graph.json 是否存在 (10分) -----
    result_path = os.path.join(cache_dir, "citation_graph.json") if dir_exists else os.path.join(workspace, "cache", "citation_graph.json")
    file_exists = os.path.isfile(result_path)
    details.append({
        "item": "cache/citation_graph.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件缺失"
    })
    if not file_exists:
        # 无法继续检查，直接输出当前分数
        total_score += 0
        finalize(details, total_score, workspace)
        return

    # ----- 3. 解析 JSON 并验证格式 (10分) -----
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        total_score += 0
        finalize(details, total_score, workspace)
        return

    format_ok = isinstance(data, dict) and "edges" in data and isinstance(data["edges"], list)
    details.append({
        "item": "JSON 包含 edges 列表",
        "score": 10 if format_ok else 0,
        "max_score": 10,
        "passed": format_ok,
        "reason": "格式正确" if format_ok else "缺少 edges 键或 edges 不是列表"
    })
    if not format_ok:
        total_score += 10  # 前面文件存在已加10，这里不折腾，统一在末尾加
        # 但为了正确性，先不加，后面重新计算总分
        # 简单处理：如果格式不合法，直接返回
        finalize(details, total_score, workspace)
        return

    # ----- 4. 计算真实有效边 (从 papers.json 推导) -----
    papers_path = os.path.join(workspace, "data", "papers", "papers.json")
    try:
        with open(papers_path, "r") as f:
            papers_data = json.load(f)
    except Exception as e:
        details.append({
            "item": "读取 papers.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"无法读取 papers.json: {str(e)}"
        })
        finalize(details, total_score, workspace)
        return

    # 构建论文ID集合
    paper_ids = set()
    paper_list = papers_data.get("papers", [])
    for p in paper_list:
        pid = p.get("paper_id")
        if pid:
            paper_ids.add(pid)

    # 计算有效边
    expected_edges = set()
    for p in paper_list:
        src = p.get("paper_id")
        if not src:
            continue
        for tgt in p.get("citation_ids", []):
            if tgt in paper_ids and tgt != src:  # 不允许自引用（业务常见，可调整）
                expected_edges.add((src, tgt))

    # 注意：我们的数据里无自引用，所以直接按存在与否即可

    # ----- 5. 比较边数量 (10分) -----
    actual_edges_set = set()
    for edge in data["edges"]:
        if isinstance(edge, dict) and "source" in edge and "target" in edge:
            actual_edges_set.add((edge["source"], edge["target"]))

    count_ok = len(actual_edges_set) == len(expected_edges)
    details.append({
        "item": "边数量正确",
        "score": 10 if count_ok else 0,
        "max_score": 10,
        "passed": count_ok,
        "reason": f"期望 {len(expected_edges)} 条边，实际 {len(actual_edges_set)} 条"
    })
    total_score += 10 if count_ok else 0

    # ----- 6. 每条边正确性 (每条20分，共期望边数*20，但最多60分) -----
    correct_count = 0
    for edge_tuple in expected_edges:
        if edge_tuple in actual_edges_set:
            correct_count += 1

    edge_score = min(correct_count * 20, 60)  # 最多3条×20=60
    details.append({
        "item": f"边正确性 (正确 {correct_count}/{len(expected_edges)})",
        "score": edge_score,
        "max_score": 60,
        "passed": correct_count == len(expected_edges),
        "reason": f"正确 {correct_count} 条"
    })
    total_score += edge_score

    # 总分不能超过100
    total_score = min(total_score, 100)
    finalize(details, total_score, workspace)

def finalize(details, total_score, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"验证完成，总分: {total_score}")

if __name__ == "__main__":
    main()
