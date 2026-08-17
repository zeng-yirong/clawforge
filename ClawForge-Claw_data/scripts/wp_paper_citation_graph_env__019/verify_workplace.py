import sys, json, os, math
from pathlib import Path

def load_papers(workspace):
    papers_path = Path(workspace) / "data" / "papers" / "papers.json"
    if not papers_path.exists():
        return None
    with open(papers_path, "r") as f:
        data = json.load(f)
    return data.get("papers", [])

def compute_expected(papers):
    # 构建所有有效 paper_id 集合
    valid_ids = {p["paper_id"] for p in papers}
    nodes = sorted(valid_ids)

    # 计算有效边：源存在，目标存在，且源≠目标，按源升序、目标升序
    edges = []
    for p in papers:
        src = p["paper_id"]
        for tgt in p.get("citation_ids", []):
            if tgt in valid_ids and tgt != src:
                edges.append((src, tgt))
    edges.sort(key=lambda x: (x[0], x[1]))
    return nodes, edges

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []

    # 1. 检查 cache 目录是否存在 (10分)
    cache_dir = Path(workspace) / "cache"
    if cache_dir.is_dir():
        details.append({"item": "cache 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "cache 目录已创建"})
    else:
        details.append({"item": "cache 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 cache 目录"})

    # 2. 检查 cache/citation_graph.json 存在且合法 JSON (10分)
    graph_path = cache_dir / "citation_graph.json"
    graph_valid = False
    if graph_path.exists():
        try:
            with open(graph_path, "r") as f:
                graph_data = json.load(f)
            graph_valid = True
            details.append({"item": "citation_graph.json 合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且解析成功"})
        except (json.JSONDecodeError, ValueError):
            details.append({"item": "citation_graph.json 合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 格式错误"})
    else:
        details.append({"item": "citation_graph.json 合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})

    # 如果 graph 无效，则后续检查无法进行，直接返回
    if not graph_valid:
        total_score = sum(d["score"] for d in details)
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        sys.exit(0)

    # 加载论文并计算预期结果
    papers = load_papers(workspace)
    if papers is None:
        details.append({"item": "读取论文数据", "score": 0, "max_score": 10, "passed": False, "reason": "data/papers/papers.json 不存在"})
        total_score = sum(d["score"] for d in details)
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        sys.exit(0)

    expected_nodes, expected_edges = compute_expected(papers)
    expected_nodes_set = set(expected_nodes)
    expected_edges_set = set(expected_edges)

    # 3. 检查 nodes 字段 (20分)
    node_score = 0
    node_reason = ""
    actual_nodes = graph_data.get("nodes", [])
    actual_nodes_set = set(actual_nodes)
    if actual_nodes_set == expected_nodes_set:
        node_score = 20
        node_reason = "节点集合与所有论文 ID 完全一致"
    elif actual_nodes_set.issuperset(expected_nodes_set):
        extra = actual_nodes_set - expected_nodes_set
        node_score = 15
        node_reason = f"包含多余节点: {extra}"
    elif actual_nodes_set.issubset(expected_nodes_set):
        missing = expected_nodes_set - actual_nodes_set
        node_score = 10
        node_reason = f"缺少节点: {missing}"
    else:
        node_score = 5
        node_reason = "节点集合既有缺失也有多余"
    details.append({"item": "节点集合正确性", "score": node_score, "max_score": 20, "passed": node_score == 20, "reason": node_reason})

    # 4. 检查 edges 数量 (30分)
    edge_count_score = 0
    edge_count_reason = ""
    actual_edges_raw = graph_data.get("edges", [])
    actual_edges = []
    for e in actual_edges_raw:
        if isinstance(e, dict) and "source" in e and "target" in e:
            actual_edges.append((e["source"], e["target"]))
        else:
            edge_count_reason = "边的格式不正确"
    actual_edges_set = set(actual_edges)
    expected_count = len(expected_edges)
    actual_count = len(actual_edges_set)
    if actual_count == expected_count:
        edge_count_score = 30
        edge_count_reason = f"边的数量正确 ({actual_count})"
    elif abs(actual_count - expected_count) <= 1:
        edge_count_score = 20
        edge_count_reason = f"边的数量接近，预期 {expected_count}，实际 {actual_count}"
    else:
        edge_count_score = 5
        edge_count_reason = f"边的数量偏差大，预期 {expected_count}，实际 {actual_count}"
    details.append({"item": "边的数量正确性", "score": edge_count_score, "max_score": 30, "passed": edge_count_score == 30, "reason": edge_count_reason})

    # 5. 检查边的具体内容 (30分)
    edge_content_score = 0
    edge_content_reason = ""
    if actual_edges_set == expected_edges_set:
        edge_content_score = 30
        edge_content_reason = "边的集合与预期完全一致"
    else:
        missing_edges = expected_edges_set - actual_edges_set
        extra_edges = actual_edges_set - expected_edges_set
        if len(missing_edges) == 0 and len(extra_edges) > 0:
            edge_content_score = 25
            edge_content_reason = f"多出了 {len(extra_edges)} 条边: {extra_edges}"
        elif len(missing_edges) > 0 and len(extra_edges) == 0:
            edge_content_score = 20
            edge_content_reason = f"缺失了 {len(missing_edges)} 条边: {missing_edges}"
        else:
            edge_content_score = 10
            edge_content_reason = f"缺失 {len(missing_edges)} 条，多余 {len(extra_edges)} 条"
    details.append({"item": "边的具体内容正确性", "score": edge_content_score, "max_score": 30, "passed": edge_content_score == 30, "reason": edge_content_reason})

    # 计算总分
    total_score = sum(d["score"] for d in details)
    total_max = sum(d["max_score"] for d in details)
    # 确保总分整数
    total_score = min(100, total_score)

    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
