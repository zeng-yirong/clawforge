import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 citation_graph.json 是否存在
    graph_path = os.path.join(workspace, "citation_graph.json")
    if not os.path.isfile(graph_path):
        details.append({
            "item": "产出文件存在性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "根目录下未找到 citation_graph.json"
        })
        # 后续项都无法检查，直接跳过
        return write_score(workspace, 0, details)

    details.append({
        "item": "产出文件存在性",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "citation_graph.json 存在"
    })

    # 2. JSON 格式合法性
    try:
        with open(graph_path, "r") as f:
            graph = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        return write_score(workspace, sum(d["score"] for d in details), details)

    details.append({
        "item": "JSON 格式合法",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON 解析成功"
    })

    # 3. 检查必备字段 nodes 和 edges
    if not isinstance(graph, dict):
        details.append({
            "item": "根结构类型",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "根对象必须是 JSON 对象（dict）"
        })
        return write_score(workspace, sum(d["score"] for d in details), details)

    if "nodes" not in graph or "edges" not in graph:
        details.append({
            "item": "必备字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 'nodes' 或 'edges' 字段"
        })
        return write_score(workspace, sum(d["score"] for d in details), details)

    details.append({
        "item": "必备字段",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "包含 nodes 和 edges"
    })

    nodes = graph["nodes"]
    edges = graph["edges"]

    # 4. 节点数量与 ID 集合
    if not isinstance(nodes, list) or not isinstance(edges, list):
        details.append({
            "item": "类型检查",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "nodes 和 edges 必须是数组"
        })
        return write_score(workspace, sum(d["score"] for d in details), details)

    expected_node_ids = {"p001", "p002", "p003"}
    actual_node_ids = {n["id"] for n in nodes if "id" in n}
    if actual_node_ids == expected_node_ids:
        details.append({
            "item": "节点集合正确性",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"节点 ID 集合为 {sorted(expected_node_ids)}，符合预期"
        })
    else:
        details.append({
            "item": "节点集合正确性",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望节点 {sorted(expected_node_ids)}，实际 {sorted(actual_node_ids)}"
        })

    # 5. 边集合正确性
    expected_edges = {("p001","p002"), ("p001","p003"), ("p002","p003"), ("p003","p001")}
    actual_edges = set()
    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        if src and tgt:
            actual_edges.add((src, tgt))

    if actual_edges == expected_edges:
        details.append({
            "item": "边集合正确性",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"边集合为 {sorted(expected_edges)}，完全匹配"
        })
    else:
        details.append({
            "item": "边集合正确性",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"期望边 {sorted(expected_edges)}，实际 {sorted(actual_edges)}"
        })

    # 6. 检查节点是否包含 title 字段（至少每个节点有）
    missing_title = [n["id"] for n in nodes if "title" not in n]
    if not missing_title:
        details.append({
            "item": "节点标题字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有节点都包含 title 字段"
        })
    else:
        details.append({
            "item": "节点标题字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"以下节点缺少 title: {missing_title}"
        })

    total_score = sum(d["score"] for d in details)
    write_score(workspace, total_score, details)

def write_score(workspace, total_score, details):
    output_path = os.path.join(workspace, "workplace_score.json")
    report = {
        "total_score": min(total_score, 100),
        "details": details
    }
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Total score: {report['total_score']}/100")
    return

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
