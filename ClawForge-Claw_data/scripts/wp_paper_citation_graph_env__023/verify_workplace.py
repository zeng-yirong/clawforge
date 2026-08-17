import json
import os
import sys
from pathlib import Path

def load_expected(workspace: str):
    """从最新论文库计算期望的节点和边（去重、排除不存在和自引用）"""
    papers_path = Path(workspace) / "data/papers/papers.json"
    if not papers_path.exists():
        return None, None
    with open(papers_path) as f:
        data = json.load(f)
    all_papers = data.get("papers", [])
    valid_ids = {p["paper_id"] for p in all_papers}
    
    nodes = [{"id": pid} for pid in sorted(valid_ids)]  # 按字母排序方便比较
    edges_set = set()
    for p in all_papers:
        src = p["paper_id"]
        for tgt in p.get("citation_ids", []):
            if tgt in valid_ids and tgt != src:
                edges_set.add((src, tgt))
    sorted_edges = [{"source": s, "target": t} for s, t in sorted(edges_set)]
    return nodes, sorted_edges

def verify(workspace: str) -> dict:
    errors = []
    scores = []
    total_score = 0

    # 1. 检查目录结构 (10分) - cache目录必须存在
    cache_dir = Path(workspace) / "cache"
    dir_exists = cache_dir.is_dir()
    scores.append({
        "item": "cache directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "cache directory found" if dir_exists else "cache directory missing"
    })

    # 2. 检查目标文件是否存在 (10分)
    target_file = cache_dir / "citation_graph.json"
    file_exists = target_file.is_file()
    scores.append({
        "item": "citation_graph.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "file found" if file_exists else "file missing"
    })
    if not file_exists:
        total_score = sum(s["score"] for s in scores)
        return {"total_score": total_score, "details": scores}

    # 3. JSON合法性 (10分)
    try:
        with open(target_file) as f:
            graph = json.load(f)
        json_ok = True
        reason = "valid JSON"
    except (json.JSONDecodeError, IOError) as e:
        json_ok = False
        reason = f"JSON parse error: {e}"
    scores.append({
        "item": "JSON is valid",
        "score": 10 if json_ok else 0,
        "max_score": 10,
        "passed": json_ok,
        "reason": reason
    })
    if not json_ok:
        total_score = sum(s["score"] for s in scores)
        return {"total_score": total_score, "details": scores}

    # 4. 结构检查：必须包含 nodes 和 edges 字段 (10分)
    has_nodes = isinstance(graph.get("nodes"), list)
    has_edges = isinstance(graph.get("edges"), list)
    struct_ok = has_nodes and has_edges
    scores.append({
        "item": "graph has nodes and edges lists",
        "score": 10 if struct_ok else 0,
        "max_score": 10,
        "passed": struct_ok,
        "reason": "structure ok" if struct_ok else "missing nodes or edges list"
    })
    if not struct_ok:
        total_score = sum(s["score"] for s in scores)
        return {"total_score": total_score, "details": scores}

    # 5. 计算期望值
    expected_nodes, expected_edges = load_expected(workspace)
    if expected_nodes is None:
        scores.append({
            "item": "papers.json readable",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "cannot load papers.json"
        })
        total_score = sum(s["score"] for s in scores)
        return {"total_score": total_score, "details": scores}

    # 6. 节点验证 (20分)
    actual_node_ids = {n["id"] for n in graph["nodes"]}
    expected_node_ids = {n["id"] for n in expected_nodes}
    node_id_match = actual_node_ids == expected_node_ids
    node_score = 20 if node_id_match else 0
    if not node_id_match:
        extra = actual_node_ids - expected_node_ids
        missing = expected_node_ids - actual_node_ids
        reason = f"node mismatch: extra={extra}, missing={missing}"
    else:
        reason = "all node ids correct"
    scores.append({
        "item": "node set matches expected (all paper_ids from papers.json)",
        "score": node_score,
        "max_score": 20,
        "passed": node_id_match,
        "reason": reason
    })

    # 7. 边验证 (50分)
    actual_edges_set = {(e["source"], e["target"]) for e in graph["edges"]}
    expected_edges_set = {(e["source"], e["target"]) for e in expected_edges}
    edge_match = actual_edges_set == expected_edges_set
    edge_score = 50 if edge_match else 0
    if not edge_match:
        extra = actual_edges_set - expected_edges_set
        missing = expected_edges_set - actual_edges_set
        reason = f"edge mismatch: extra={extra}, missing={missing}"
    else:
        reason = "all edges correct ({} edges)".format(len(expected_edges))
    scores.append({
        "item": "edge set exactly matches expected (valid citations only, no dupes)",
        "score": edge_score,
        "max_score": 50,
        "passed": edge_match,
        "reason": reason
    })

    total_score = sum(s["score"] for s in scores)
    return {"total_score": total_score, "details": scores}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Score written to workplace_score.json")
