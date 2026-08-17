import sys
import os
import json

def score_item(name, score, max_score, passed, reason):
    return {"item": name, "score": score, "max_score": max_score, "passed": passed, "reason": reason}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # 1. 检查 cache 目录是否存在 (10分)
    cache_dir = os.path.join(workspace, "cache")
    if os.path.isdir(cache_dir):
        details.append(score_item("cache directory exists", 10, 10, True, "Directory found"))
        total += 10
    else:
        details.append(score_item("cache directory exists", 0, 10, False, "Missing cache/ directory"))
        total += 0

    # 2. 检查 citation_graph.json 是否存在 (10分)
    graph_path = os.path.join(cache_dir, "citation_graph.json")
    if os.path.isfile(graph_path):
        details.append(score_item("citation_graph.json exists", 10, 10, True, "File found"))
        total += 10
    else:
        details.append(score_item("citation_graph.json exists", 0, 10, False, "File not found"))
        total += 0
        # 不再继续检查
        results = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(results, f, indent=2)
        return

    # 3. JSON 格式合法性 (10分)
    try:
        with open(graph_path, "r") as f:
            data = json.load(f)
        details.append(score_item("JSON format valid", 10, 10, True, "Valid JSON"))
        total += 10
    except Exception as e:
        details.append(score_item("JSON format valid", 0, 10, False, f"Invalid JSON: {e}"))
        total += 0
        results = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(results, f, indent=2)
        return

    # 4. 包含 nodes 和 edges 字段 (10分)
    if "nodes" in data and "edges" in data:
        details.append(score_item("Has nodes and edges fields", 10, 10, True, "Both present"))
        total += 10
    else:
        details.append(score_item("Has nodes and edges fields", 0, 10, False, "Missing nodes or edges field"))
        total += 0

    # 5. 节点正确性 (20分)
    valid_paper_ids = {"p001", "p002", "p003", "p004", "p005_alias"}
    reported_node_ids = {node.get("id") for node in data.get("nodes", [])}
    if reported_node_ids == valid_paper_ids:
        details.append(score_item("Nodes contain exactly all valid papers", 20, 20, True, "Correct node set"))
        total += 20
    elif reported_node_ids.issuperset(valid_paper_ids):
        extra = reported_node_ids - valid_paper_ids
        details.append(score_item("Nodes contain all valid papers but have extra nodes", 10, 20, False, f"Extra nodes: {extra}"))
        total += 10
    elif reported_node_ids.issubset(valid_paper_ids):
        missing = valid_paper_ids - reported_node_ids
        details.append(score_item("Nodes missing some valid papers", 5, 20, False, f"Missing: {missing}"))
        total += 5
    else:
        details.append(score_item("Nodes set incorrect", 0, 20, False, "Nodes do not match valid papers"))
        total += 0

    # 6. 边正确性 (30分)
    # 期望边: (source, target)
    expected_edges = {("p001","p002"), ("p001","p003"), ("p002","p004"), ("p005_alias","p001")}
    reported_edges = set()
    for edge in data.get("edges", []):
        src = edge.get("source")
        tgt = edge.get("target")
        if src and tgt:
            reported_edges.add((src, tgt))
    if reported_edges == expected_edges:
        details.append(score_item("Edges exactly match expected", 30, 30, True, "All edges correct"))
        total += 30
    elif reported_edges.issuperset(expected_edges):
        extra_edges = reported_edges - expected_edges
        details.append(score_item("Edges have extra invalid edges", 15, 30, False, f"Extra edges: {extra_edges}"))
        total += 15
    elif reported_edges.issubset(expected_edges):
        missing_edges = expected_edges - reported_edges
        details.append(score_item("Edges missing some expected edges", 10, 30, False, f"Missing: {missing_edges}"))
        total += 10
    else:
        details.append(score_item("Edges largely incorrect", 0, 30, False, f"Reported: {reported_edges}, Expected: {expected_edges}"))
        total += 0

    # 7. 无多余无效字段/节点 (10分)
    # 检查节点中是否有非字符串id或额外字段（只要求id即可，不扣分）
    # 主要看是否有节点与边之外的数据结构污染，简单通过
    extra_keys = set(data.keys()) - {"nodes", "edges"}
    if extra_keys:
        details.append(score_item("No extra top-level keys", 5, 10, False, f"Extra keys: {extra_keys}"))
        total += 5
    else:
        details.append(score_item("No extra top-level keys", 10, 10, True, "Clean structure"))
        total += 10

    # 输出结果
    total = min(total, 100)  # 确保不超过100
    results = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
