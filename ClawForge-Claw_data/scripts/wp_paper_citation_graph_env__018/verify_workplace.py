import sys
import os
import json

def load_papers(workspace):
    path = os.path.join(workspace, "papers", "papers.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("papers", [])

def compute_ground_truth(papers):
    """从原始数据计算正确的节点和边（按规则清洗后）"""
    # 收集所有有效 paper_id
    valid_ids = {p["paper_id"] for p in papers}
    nodes = sorted(valid_ids)  # 按 id 升序

    # 构建节点 title 映射
    title_map = {p["paper_id"]: p["title"] for p in papers}

    # 收集有效边（去重、去自环、去悬空）
    edge_set = set()
    for p in papers:
        src = p["paper_id"]
        for tgt in p["citation_ids"]:
            if tgt == src:
                continue          # 自环
            if tgt not in valid_ids:
                continue          # 悬空
            edge_set.add((src, tgt))
    # 排序
    sorted_edges = sorted(edge_set, key=lambda x: (x[0], x[1]))
    return nodes, title_map, sorted_edges

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 citation_graph.json 是否存在
    graph_path = os.path.join(workspace, "citation_graph.json")
    if not os.path.exists(graph_path):
        details.append({
            "item": "citation_graph.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 直接输出并退出
        dump_score(total_score, details)
        return
    else:
        details.append({
            "item": "citation_graph.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists"
        })
        total_score += 10

    # 2. 解析 JSON
    try:
        with open(graph_path, "r") as f:
            graph = json.load(f)
    except Exception as e:
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        dump_score(total_score, details)
        return

    if not isinstance(graph, dict) or "nodes" not in graph or "edges" not in graph:
        details.append({
            "item": "Valid JSON structure (keys: nodes, edges)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing required keys 'nodes' or 'edges'"
        })
        dump_score(total_score, details)
        return
    else:
        details.append({
            "item": "Valid JSON structure",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Has nodes and edges"
        })
        total_score += 10

    # 3. 加载原始数据并计算 ground truth
    papers = load_papers(workspace)
    if papers is None:
        details.append({
            "item": "Load papers data",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "Cannot find papers/papers.json in workspace"
        })
        dump_score(total_score, details)
        return

    true_nodes, title_map, true_edges = compute_ground_truth(papers)

    # 4. 检查 nodes
    nodes = graph.get("nodes", [])
    node_score = 0
    node_max = 30
    # 检查节点数量和 id 正确性
    if len(nodes) != len(true_nodes):
        node_score = 0
        reason = f"Node count mismatch: expected {len(true_nodes)}, got {len(nodes)}"
    else:
        # 检查每个节点的 id 和 title
        all_ok = True
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                all_ok = False
                reason = f"Node at index {i} is not a dict"
                break
            expected_id = true_nodes[i]
            expected_title = title_map[expected_id]
            if node.get("id") != expected_id or node.get("title") != expected_title:
                all_ok = False
                reason = f"Node mismatch at index {i}: expected ({expected_id}, {expected_title}), got ({node.get('id')}, {node.get('title')})"
                break
        if all_ok:
            node_score = node_max
            reason = "All nodes correct (ids and titles)"
        else:
            node_score = 0
    details.append({
        "item": "Nodes correctness",
        "score": node_score,
        "max_score": node_max,
        "passed": node_score == node_max,
        "reason": reason
    })
    total_score += node_score

    # 5. 检查 edges
    edges = graph.get("edges", [])
    edge_score = 0
    edge_max = 50
    if len(edges) != len(true_edges):
        edge_score = 0
        reason = f"Edge count mismatch: expected {len(true_edges)}, got {len(edges)}"
    else:
        all_ok = True
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                all_ok = False
                reason = f"Edge at index {i} is not a dict"
                break
            expected_src, expected_tgt = true_edges[i]
            if edge.get("source") != expected_src or edge.get("target") != expected_tgt:
                all_ok = False
                reason = f"Edge mismatch at index {i}: expected ({expected_src},{expected_tgt}), got ({edge.get('source')},{edge.get('target')})"
                break
        if all_ok:
            edge_score = edge_max
            reason = "All edges correct (source, target, order)"
        else:
            edge_score = 0
    details.append({
        "item": "Edges correctness",
        "score": edge_score,
        "max_score": edge_max,
        "passed": edge_score == edge_max,
        "reason": reason
    })
    total_score += edge_score

    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

def dump_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
