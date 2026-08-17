import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 预期答案（唯一，7条有效边，按source→target排序）
    expected_edges = [
        ("p001", "p002"),
        ("p001", "p003"),
        ("p002", "p001"),
        ("p002", "p003"),
        ("p003", "p001"),
        ("p003", "p002"),
        ("p004", "p001"),
    ]
    expected_set = set(expected_edges)

    result_path = os.path.join(workspace, "output", "citation_graph.json")

    # 1. 检查 output 目录
    output_dir = os.path.join(workspace, "output")
    if os.path.isdir(output_dir):
        details.append({"item": "output directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "output/ found"})
        score += 5
    else:
        details.append({"item": "output directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "output/ not found"})

    # 2. 检查文件存在
    if os.path.isfile(result_path):
        details.append({"item": "citation_graph.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "file exists"})
        score += 5
    else:
        details.append({"item": "citation_graph.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "file not found"})
        # 后续检查无法进行，跳到最后写入总分
        _write_score(score, details, workspace)
        return

    # 3. 解析 JSON
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "JSON parse successful"})
        score += 5
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": f"JSON error: {e}"})
        _write_score(score, details, workspace)
        return

    # 4. 检查顶层键
    if isinstance(data, dict) and "edges" in data:
        details.append({"item": "top-level object with 'edges' key", "score": 5, "max_score": 5, "passed": True, "reason": "found edges key"})
        score += 5
    else:
        details.append({"item": "top-level object with 'edges' key", "score": 0, "max_score": 5, "passed": False, "reason": "missing edges key or not a dict"})
        _write_score(score, details, workspace)
        return

    edges = data["edges"]
    if not isinstance(edges, list):
        details.append({"item": "edges is a list", "score": 0, "max_score": 5, "passed": False, "reason": "edges is not a list"})
        _write_score(score, details, workspace)
        return
    else:
        details.append({"item": "edges is a list", "score": 5, "max_score": 5, "passed": True, "reason": "edges is a list"})
        score += 5

    # 5. 每条边格式
    format_ok = True
    for i, edge in enumerate(edges):
        if not (isinstance(edge, dict) and "source" in edge and "target" in edge and isinstance(edge["source"], str) and isinstance(edge["target"], str)):
            format_ok = False
            break
    if format_ok:
        details.append({"item": "each edge has source and target strings", "score": 5, "max_score": 5, "passed": True, "reason": "format correct"})
        score += 5
    else:
        details.append({"item": "each edge has source and target strings", "score": 0, "max_score": 5, "passed": False, "reason": "bad edge format"})

    # 6. 去重检查
    edge_tuples = [(e["source"], e["target"]) for e in edges]
    if len(edge_tuples) == len(set(edge_tuples)):
        details.append({"item": "no duplicate edges", "score": 5, "max_score": 5, "passed": True, "reason": "all edges unique"})
        score += 5
    else:
        details.append({"item": "no duplicate edges", "score": 0, "max_score": 5, "passed": False, "reason": "found duplicate edges"})

    # 7. 排序检查
    sorted_tuples = sorted(edge_tuples, key=lambda x: (x[0], x[1]))
    if edge_tuples == sorted_tuples:
        details.append({"item": "edges sorted by source then target", "score": 5, "max_score": 5, "passed": True, "reason": "correct order"})
        score += 5
    else:
        details.append({"item": "edges sorted by source then target", "score": 0, "max_score": 5, "passed": False, "reason": "order incorrect"})

    # 8. 边数量
    if len(edge_tuples) == len(expected_edges):
        details.append({"item": "correct number of edges", "score": 10, "max_score": 10, "passed": True, "reason": f"found {len(edge_tuples)} edges"})
        score += 10
    else:
        details.append({"item": "correct number of edges", "score": 0, "max_score": 10, "passed": False, "reason": f"expected {len(expected_edges)}, got {len(edge_tuples)}"})

    # 9. 每个预期边都存在（按2分/条）
    edge_set = set(edge_tuples)
    passed_edges = 0
    for e in expected_set:
        if e in edge_set:
            passed_edges += 1
    if passed_edges == len(expected_set):
        details.append({"item": "all expected edges present", "score": 14, "max_score": 14, "passed": True, "reason": f"all {len(expected_set)} expected edges found"})
        score += 14
    else:
        details.append({"item": "all expected edges present", "score": 0, "max_score": 14, "passed": False, "reason": f"found {passed_edges}/{len(expected_set)} expected edges"})

    # 10. 没有多余边
    extra = edge_set - expected_set
    if len(extra) == 0:
        details.append({"item": "no extra edges", "score": 10, "max_score": 10, "passed": True, "reason": "no unexpected edges"})
        score += 10
    else:
        details.append({"item": "no extra edges", "score": 0, "max_score": 10, "passed": False, "reason": f"found {len(extra)} extra edges: {extra}"})

    # 11. 不得包含自引用 p003->p003
    if ("p003", "p003") in edge_set:
        details.append({"item": "no self-citation (p003->p003)", "score": 0, "max_score": 5, "passed": False, "reason": "self-citation found"})
    else:
        details.append({"item": "no self-citation (p003->p003)", "score": 5, "max_score": 5, "passed": True, "reason": "self-citation correctly excluded"})
        score += 5

    # 12. 不得包含无效引用 p999
    if any(s == "p999" or t == "p999" for s, t in edge_set):
        details.append({"item": "no invalid paper p999", "score": 0, "max_score": 5, "passed": False, "reason": "edge containing p999 found"})
    else:
        details.append({"item": "no invalid paper p999", "score": 5, "max_score": 5, "passed": True, "reason": "p999 correctly excluded"})
        score += 5

    # 13. 不得受旧版干扰 (p001->p005 来自 old.bak)
    if ("p001", "p005") in edge_set:
        details.append({"item": "not influenced by old backup (p001->p005)", "score": 0, "max_score": 5, "passed": False, "reason": "old backup edge found"})
    else:
        details.append({"item": "not influenced by old backup (p001->p005)", "score": 5, "max_score": 5, "passed": True, "reason": "backup correctly ignored"})
        score += 5

    # 写入最终得分
    _write_score(score, details, workspace)

def _write_score(score, details, workspace):
    result = {
        "total_score": score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {score}/100")

if __name__ == "__main__":
    main()
