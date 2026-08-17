import sys
import os
import json
import pathlib

def verify(workspace):
    ws = pathlib.Path(workspace)
    score_details = []
    total = 0

    # 1. 检查 cache 目录是否存在 (5分)
    cache_dir = ws / "cache"
    if cache_dir.is_dir():
        score_details.append({
            "item": "cache directory exists",
            "score": 5, "max_score": 5, "passed": True,
            "reason": "cache/ directory found"
        })
        total += 5
    else:
        score_details.append({
            "item": "cache directory exists",
            "score": 0, "max_score": 5, "passed": False,
            "reason": "cache/ directory not found"
        })

    # 2. 检查 citation_graph.json 是否存在 (10分)
    graph_file = cache_dir / "citation_graph.json"
    if graph_file.is_file():
        score_details.append({
            "item": "citation_graph.json exists",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "file found"
        })
        total += 10
    else:
        score_details.append({
            "item": "citation_graph.json exists",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "citation_graph.json not found"
        })
        # 如果文件不存在，后续检查无法进行，直接返回
        final_score = min(total, 100)
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": final_score, "details": score_details}, f, indent=2)
        return

    # 3. 检查 JSON 格式合法性 (15分)
    try:
        with open(graph_file, "r") as f:
            graph_data = json.load(f)
        score_details.append({
            "item": "JSON parseable",
            "score": 15, "max_score": 15, "passed": True,
            "reason": "valid JSON"
        })
        total += 15
    except Exception as e:
        score_details.append({
            "item": "JSON parseable",
            "score": 0, "max_score": 15, "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        final_score = min(total, 100)
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": final_score, "details": score_details}, f, indent=2)
        return

    # 4. 结构检查：必须包含 nodes 和 edges 两个字段 (15分)
    if not isinstance(graph_data, dict):
        score_details.append({
            "item": "graph structure",
            "score": 0, "max_score": 15, "passed": False,
            "reason": "graph_data is not a dict"
        })
    elif "nodes" not in graph_data or "edges" not in graph_data:
        score_details.append({
            "item": "graph structure",
            "score": 0, "max_score": 15, "passed": False,
            "reason": "missing 'nodes' or 'edges' key"
        })
    else:
        score_details.append({
            "item": "graph structure",
            "score": 15, "max_score": 15, "passed": True,
            "reason": "contains nodes and edges"
        })
        total += 15

    # 5. 节点内容正确性 (25分)
    # 预期节点列表（根据 current/papers.json）
    expected_nodes = [
        {"id": "p001", "title": "Deep Learning for NLP"},
        {"id": "p002", "title": "Attention Mechanisms"},
        {"id": "p003", "title": "Graph Neural Networks"},
        {"id": "p004", "title": "Reinforcement Learning Basics"},
        {"id": "p005", "title": "Quantum Computing"}
    ]
    # 构建预期节点集合用于比较（忽略顺序）
    expected_node_set = { (n["id"], n["title"]) for n in expected_nodes }

    nodes = graph_data.get("nodes", [])
    # 检查数量
    if len(nodes) != len(expected_nodes):
        score_details.append({
            "item": "nodes count",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"expected {len(expected_nodes)} nodes, got {len(nodes)}"
        })
        total += 0
    else:
        # 检查每个节点的合法性
        node_set = { (n.get("id"), n.get("title")) for n in nodes if isinstance(n, dict) }
        if node_set == expected_node_set:
            score_details.append({
                "item": "nodes count and content",
                "score": 10, "max_score": 10, "passed": True,
                "reason": "all 5 nodes match exactly"
            })
            total += 10
        else:
            score_details.append({
                "item": "nodes count and content",
                "score": 5, "max_score": 10, "passed": False,
                "reason": f"nodes mismatch. expected {expected_node_set}, got {node_set}"
            })
            total += 5

    # 6. 边内容正确性 (25分)
    # 预期边（无向？有向？引用有方向，我们按有向处理 source->target）
    # 根据真实数据：p001 -> p002, p001 -> p003; p002 -> p003, p002 -> p004; p003 -> p004; p005 -> p001, p005 -> p003
    # 注意：p004 引用空，没有边
    # 无效引用（不存在的ID）不画
    expected_edges = [
        {"source": "p001", "target": "p002"},
        {"source": "p001", "target": "p003"},
        {"source": "p002", "target": "p003"},
        {"source": "p002", "target": "p004"},
        {"source": "p003", "target": "p004"},
        {"source": "p005", "target": "p001"},
        {"source": "p005", "target": "p003"}
    ]
    expected_edge_set = { (e["source"], e["target"]) for e in expected_edges }

    edges = graph_data.get("edges", [])
    # 检查数量
    if len(edges) != len(expected_edges):
        score_details.append({
            "item": "edges count",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"expected {len(expected_edges)} edges, got {len(edges)}"
        })
        total += 0
    else:
        edge_set = { (e.get("source"), e.get("target")) for e in edges if isinstance(e, dict) }
        if edge_set == expected_edge_set:
            score_details.append({
                "item": "edges count and content",
                "score": 15, "max_score": 15, "passed": True,
                "reason": "all 7 edges match exactly"
            })
            total += 15
        else:
            score_details.append({
                "item": "edges count and content",
                "score": 5, "max_score": 15, "passed": False,
                "reason": f"edges mismatch. expected {expected_edge_set}, got {edge_set}"
            })
            total += 5

    # 7. 检查是否包含不应有的节点或边（例如来自干扰数据的节点） (20分)
    extra_penalty = 0
    # 任何不在 expected_node_set 中的节点
    node_set = { (n.get("id"), n.get("title")) for n in nodes if isinstance(n, dict) }
    for nid, title in node_set:
        if (nid, title) not in expected_node_set:
            extra_penalty += 10
    edge_set = { (e.get("source"), e.get("target")) for e in edges if isinstance(e, dict) }
    for s, t in edge_set:
        if (s, t) not in expected_edge_set:
            extra_penalty += 10
    if extra_penalty > 0:
        score_details.append({
            "item": "no extraneous data",
            "score": max(0, 20 - extra_penalty), "max_score": 20, "passed": extra_penalty == 0,
            "reason": f"found {extra_penalty} extra nodes/edges, penalty {extra_penalty}"
        })
        total += max(0, 20 - extra_penalty)
    else:
        score_details.append({
            "item": "no extraneous data",
            "score": 20, "max_score": 20, "passed": True,
            "reason": "no extra nodes or edges"
        })
        total += 20

    # 确保总分不超过100
    final_score = min(total, 100)
    with open(ws / "workplace_score.json", "w") as f:
        json.dump({"total_score": final_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
