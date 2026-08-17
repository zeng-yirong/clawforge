import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查必要目录结构（10分）
    required_dirs = ["papers", "cache"]
    all_dirs_exist = all(os.path.isdir(os.path.join(workspace, d)) for d in required_dirs)
    if all_dirs_exist:
        score += 10
        details.append({"item": "必要目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "papers/ and cache/ exist"})
    else:
        missing = [d for d in required_dirs if not os.path.isdir(os.path.join(workspace, d))]
        details.append({"item": "必要目录存在", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing directories: {missing}"})

    # 2. 检查产物文件是否存在（10分）
    target_file = os.path.join(workspace, "cache", "citation_graph.json")
    if os.path.isfile(target_file):
        score += 10
        details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "cache/citation_graph.json found"})
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "cache/citation_graph.json not found"})
        # 如果文件不存在，后续检查无法进行，直接输出分数并退出
        total = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        print(f"Score: {total}/100")
        return

    # 3. 检查JSON格式（10分）
    try:
        with open(target_file, "r") as f:
            graph = json.load(f)
        score += 10
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "Successfully parsed JSON"})
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
        total = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return

    # 4. 检查结构是否有nodes和edges字段（10分）
    if isinstance(graph, dict) and "nodes" in graph and "edges" in graph:
        score += 10
        details.append({"item": "必要字段存在", "score": 10, "max_score": 10, "passed": True, "reason": "Has 'nodes' and 'edges' keys"})
    else:
        details.append({"item": "必要字段存在", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'nodes' or 'edges' key"})
        total = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # 5. 节点集正确性（20分）
    # 期望节点：根据论文清单（paper_001~paper_005）共5个，且每个节点必须有id字段
    expected_node_ids = {"paper_001", "paper_002", "paper_003", "paper_004", "paper_005"}
    node_ids = set()
    node_errors = []
    for n in nodes:
        if not isinstance(n, dict) or "id" not in n:
            node_errors.append(f"Node missing 'id': {n}")
            continue
        node_ids.add(n["id"])
    # 检查多余节点
    extra_nodes = node_ids - expected_node_ids
    if extra_nodes:
        node_errors.append(f"Extra node(s): {extra_nodes}")
    # 检查缺失节点
    missing_nodes = expected_node_ids - node_ids
    if missing_nodes:
        node_errors.append(f"Missing node(s): {missing_nodes}")
    if not node_errors and len(node_ids) == 5 and node_ids == expected_node_ids:
        score += 20
        details.append({"item": "节点集合正确", "score": 20, "max_score": 20, "passed": True, "reason": "Exactly 5 correct nodes"})
    else:
        score += 0
        details.append({"item": "节点集合正确", "score": 0, "max_score": 20, "passed": False, "reason": f"Issues: {'; '.join(node_errors)}"})

    # 6. 边集正确性（30分）
    # 预期边（有向，去重，只保留目标ID在expected_node_ids中的边）
    # 从原始数据计算：
    # paper_001: cites [paper_002, paper_003] -> (001-002, 001-003)
    # paper_002: cites [paper_003] -> (002-003)
    # paper_003: cites [paper_004, paper_005] -> (003-004, 003-005)
    # paper_004: cites [paper_002, paper_999] -> 只保留 paper_002 -> (004-002)
    # paper_005: cites [paper_001, paper_002, paper_005] -> (005-001, 005-002, 005-005)
    expected_edges = {
        ("paper_001", "paper_002"),
        ("paper_001", "paper_003"),
        ("paper_002", "paper_003"),
        ("paper_003", "paper_004"),
        ("paper_003", "paper_005"),
        ("paper_004", "paper_002"),
        ("paper_005", "paper_001"),
        ("paper_005", "paper_002"),
        ("paper_005", "paper_005")
    }
    edge_set = set()
    edge_errors = []
    for e in edges:
        if not isinstance(e, dict) or "source" not in e or "target" not in e:
            edge_errors.append(f"Edge missing source/target: {e}")
            continue
        s = e["source"]
        t = e["target"]
        edge_set.add((s, t))
    # 检查多余边
    extra_edges = edge_set - expected_edges
    if extra_edges:
        edge_errors.append(f"Extra edge(s): {extra_edges}")
    # 检查缺失边
    missing_edges = expected_edges - edge_set
    if missing_edges:
        edge_errors.append(f"Missing edge(s): {missing_edges}")
    # 边数也要检查，以防有重复边（虽然去重后应等于期望边数）
    if len(edge_set) != len(expected_edges):
        edge_errors.append(f"Edge count mismatch: got {len(edge_set)}, expected {len(expected_edges)}")
    if not edge_errors and edge_set == expected_edges:
        score += 30
        details.append({"item": "边集正确", "score": 30, "max_score": 30, "passed": True, "reason": "All 9 expected edges present, no extras"})
    else:
        score += 0
        details.append({"item": "边集正确", "score": 0, "max_score": 30, "passed": False, "reason": f"Issues: {'; '.join(edge_errors)}"})

    # 7. 无多余字段或不符合规范的节点/边（10分）
    extra_fields = False
    for n in nodes:
        if set(n.keys()) != {"id"}:
            extra_fields = True
            break
    for e in edges:
        if set(e.keys()) != {"source", "target"}:
            extra_fields = True
            break
    if not extra_fields:
        score += 10
        details.append({"item": "无多余字段", "score": 10, "max_score": 10, "passed": True, "reason": "All nodes only have 'id', edges only 'source' and 'target'"})
    else:
        details.append({"item": "无多余字段", "score": 0, "max_score": 10, "passed": False, "reason": "Found extra fields in nodes or edges"})

    # 写入最终评分
    total_score = score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Total score: {total_score}/100")

if __name__ == "__main__":
    main()
