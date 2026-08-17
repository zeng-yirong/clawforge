import sys
import json
import os
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 结果文件路径
    result_path = os.path.join(workspace, "citation_graph.json")

    # 1. 文件存在性 (10分)
    if os.path.isfile(result_path):
        details.append({
            "item": "citation_graph.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        score += 10
    else:
        details.append({
            "item": "citation_graph.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 没有文件无法继续评分，直接输出
        _write_score(score, details, workspace)
        return

    # 2. JSON 合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
        score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        _write_score(score, details, workspace)
        return

    # 3. 必须包含 nodes 和 edges 字段 (10分)
    if "nodes" in data and "edges" in data:
        details.append({
            "item": "包含 nodes 和 edges 字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "字段存在"
        })
        score += 10
    else:
        details.append({
            "item": "包含 nodes 和 edges 字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"缺少字段: {set(['nodes','edges']) - set(data.keys())}"
        })
        _write_score(score, details, workspace)
        return

    # 4. nodes 数量应为 4 (20分)
    expected_node_ids = {"001", "002", "003", "004"}
    actual_nodes = data.get("nodes", [])
    actual_node_ids = set(node.get("id") for node in actual_nodes)

    if len(actual_nodes) == 4 and actual_node_ids == expected_node_ids:
        details.append({
            "item": "节点数量为4且ID集合正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"节点ID: {sorted(actual_node_ids)}"
        })
        score += 20
    else:
        # 部分得分：数量正确但ID不对，或反之
        id_correct = actual_node_ids == expected_node_ids
        count_correct = len(actual_nodes) == 4
        pts = 0
        if count_correct:
            pts += 10
        if id_correct:
            pts += 10
        details.append({
            "item": "节点数量为4且ID集合正确",
            "score": pts,
            "max_score": 20,
            "passed": False,
            "reason": f"节点数={len(actual_nodes)}, ID集={actual_node_ids}"
        })
        score += pts

    # 5. 节点标题必须准确匹配 (10分)
    title_map = {
        "001": "Deep Learning",
        "002": "Transformer",
        "003": "Attention Is All You Need",
        "004": "Graph Neural Networks"
    }
    node_title_errors = []
    for node in actual_nodes:
        nid = node.get("id")
        expected_title = title_map.get(nid)
        if expected_title is None:
            node_title_errors.append(f"未知节点ID {nid}")
        elif node.get("title") != expected_title:
            node_title_errors.append(f"节点 {nid} 标题应为 '{expected_title}', 实际为 '{node.get('title')}'")
    if not node_title_errors:
        details.append({
            "item": "节点标题准确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有节点标题正确"
        })
        score += 10
    else:
        details.append({
            "item": "节点标题准确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "; ".join(node_title_errors)
        })

    # 6. edges 正确性 (30分)
    expected_edges = {
        ("001", "002"),
        ("001", "003"),
        ("002", "001"),
        ("004", "001"),
        ("004", "003")
    }
    actual_edges = set()
    edge_errors = []
    for edge in data.get("edges", []):
        source = edge.get("source")
        target = edge.get("target")
        if source is None or target is None:
            edge_errors.append("边缺少 source 或 target")
        else:
            actual_edges.add((source, target))
    # 检查是否有多余边
    extra = actual_edges - expected_edges
    missing = expected_edges - actual_edges
    if not extra and not missing:
        details.append({
            "item": "引用边准确 (仅包含有效边)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"边数={len(expected_edges)}, 全部匹配"
        })
        score += 30
    else:
        pts = 30
        details_text = []
        if extra:
            pts -= 15
            details_text.append(f"多余边: {extra}")
        if missing:
            pts -= 15
            details_text.append(f"缺失边: {missing}")
        details.append({
            "item": "引用边准确 (仅包含有效边)",
            "score": max(0, pts),
            "max_score": 30,
            "passed": False,
            "reason": "; ".join(details_text)
        })
        score += max(0, pts)

    # 写总分
    _write_score(score, details, workspace)


def _write_score(total, details, workspace):
    output = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
