#!/usr/bin/env python3
import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # ============ 1. 目录结构检查 (10分) ============
    analysis_dir = os.path.join(workspace, "analysis")
    graph_path = os.path.join(analysis_dir, "citation_graph.json")
    dir_ok = os.path.isdir(analysis_dir)
    file_ok = os.path.isfile(graph_path)
    if dir_ok and file_ok:
        score_details.append({
            "item": "output directory and file exist",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"analysis/citation_graph.json exists"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "output directory and file exist",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"analysis/ dir? {dir_ok}, file? {file_ok}"
        })
        # 如果文件不存在，直接输出分数并退出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # ============ 2. JSON 合法性 (10分) ============
    try:
        with open(graph_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON syntax & structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    if not isinstance(data, dict) or "nodes" not in data or "edges" not in data:
        score_details.append({
            "item": "JSON structure (nodes & edges keys)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing 'nodes' or 'edges' keys"
        })
    else:
        score_details.append({
            "item": "JSON structure (nodes & edges keys)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Has nodes and edges keys"
        })
        total_score += 10

    # ============ 3. 节点正确性 (20分) ============
    expected_nodes = [
        {"paper_id": "P001", "title": "Deep Learning for Citation Networks", "year": 2017},
        {"paper_id": "P004", "title": "Graph Neural Networks in Literature Mining", "year": 2018},
        {"paper_id": "P005", "title": "Attention Mechanisms for Citation Analysis", "year": 2019},
        {"paper_id": "P006", "title": "Temporal Dynamics of Research Impact", "year": 2020},
        {"paper_id": "P007", "title": "Benchmarking Citation Graph Datasets", "year": 2021},
    ]
    nodes = data.get("nodes", [])
    # 按 paper_id 排序以便比较
    sorted_nodes = sorted(nodes, key=lambda x: x.get("paper_id", ""))
    # 检查数量
    node_count_ok = len(sorted_nodes) == 5
    # 检查每个节点字段正确
    node_match = True
    for i, exp in enumerate(expected_nodes):
        if i >= len(sorted_nodes):
            node_match = False
            break
        actual = sorted_nodes[i]
        if actual.get("paper_id") != exp["paper_id"] or \
           actual.get("title") != exp["title"] or \
           actual.get("year") != exp["year"]:
            node_match = False
            break

    if node_count_ok and node_match:
        score_details.append({
            "item": "nodes exact set (5 papers, correct IDs/titles/years)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "All 5 expected nodes present and correct"
        })
        total_score += 20
    else:
        reason = f"node count expected 5, got {len(sorted_nodes)}; match={node_match}"
        score_details.append({
            "item": "nodes exact set (5 papers, correct IDs/titles/years)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": reason
        })

    # ============ 4. 边数量 (20分) ============
    expected_edges = [
        {"source": "P001", "target": "P004"},
        {"source": "P001", "target": "P005"},
        {"source": "P004", "target": "P005"},
        {"source": "P004", "target": "P006"},
        {"source": "P005", "target": "P001"},
        {"source": "P006", "target": "P007"},
        {"source": "P007", "target": "P001"},
        {"source": "P007", "target": "P004"},
    ]
    edges = data.get("edges", [])
    # 排序边 (source, target)
    sorted_edges = sorted(edges, key=lambda e: (e.get("source",""), e.get("target","")))
    if len(sorted_edges) == 8:
        score_details.append({
            "item": "edges count equals 8",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Exactly 8 edges present"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "edges count equals 8",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected 8 edges, got {len(sorted_edges)}"
        })

    # ============ 5. 边精确匹配 (40分, 每条边5分) ============
    edge_points = 0
    max_edge_points = 40
    # 构建 expected set of tuples
    expected_set = {(e["source"], e["target"]) for e in expected_edges}
    actual_set = {(e.get("source",""), e.get("target","")) for e in sorted_edges}
    # 每个漏掉或多余的扣5分，最多扣40
    missing = expected_set - actual_set
    extra = actual_set - expected_set
    penalty = (len(missing) + len(extra)) * 5
    if penalty > 40:
        penalty = 40
    edge_points = max_edge_points - penalty
    if edge_points < 0:
        edge_points = 0
    passed_edges = (penalty == 0)
    reason_edges = f"missing={missing}, extra={extra}" if not passed_edges else "All edges match exactly"
    score_details.append({
        "item": "edges exact set (8 expected, no missing/extra)",
        "score": edge_points,
        "max_score": 40,
        "passed": passed_edges,
        "reason": reason_edges
    })
    total_score += edge_points

    # 写结果
    final_score = min(total_score, 100)  # 最多100
    result = {
        "total_score": final_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
