"""
wp_paper_citation_graph_env__020 验证脚本
检查 agent 是否从 papers/papers.json 中提取有效论文并生成引用图存于 cache/citation_graph.json
评分规则：目录结构10分，文件存在10分，JSON合法性10分，节点正确性30分，边正确性40分
"""
import sys
import os
import json
import re

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_valid_papers(papers_dict):
    """根据规则筛选有效论文：ID匹配 ^P-\d{3}$，year在2000-2023之间，所有必需字段存在"""
    required_fields = ["title", "direction", "year", "keywords", "abstract", "citation_ids"]
    valid = {}
    for pid, info in papers_dict.items():
        # ID格式
        if not re.match(r'^P-\d{3}$', pid):
            continue
        # 所有必需字段存在
        missing = [f for f in required_fields if f not in info]
        if missing:
            continue
        # year 必须是整数且在范围内
        year = info.get("year")
        if not isinstance(year, int) or year < 2000 or year > 2023:
            continue
        valid[pid] = info
    return valid

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 目录结构 (10分)
    cache_dir = os.path.join(workspace, "cache")
    if os.path.isdir(cache_dir):
        details.append({"item": "cache directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ok"})
        score += 10
    else:
        details.append({"item": "cache directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "cache directory not found"})

    # 2. 文件存在 (10分)
    graph_path = os.path.join(cache_dir, "citation_graph.json")
    if os.path.isfile(graph_path):
        details.append({"item": "citation_graph.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "ok"})
        score += 10
    else:
        details.append({"item": "citation_graph.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # 如果文件不存在，后续无法检查，直接返回
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # 3. JSON合法性 (10分)
    try:
        graph = load_json(graph_path)
        if isinstance(graph, dict) and "nodes" in graph and "edges" in graph:
            details.append({"item": "graph JSON valid and has nodes & edges", "score": 10, "max_score": 10, "passed": True, "reason": "ok"})
            score += 10
        else:
            details.append({"item": "graph JSON valid and has nodes & edges", "score": 0, "max_score": 10, "passed": False, "reason": "missing 'nodes' or 'edges' keys"})
    except Exception as e:
        details.append({"item": "graph JSON valid and has nodes & edges", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})

    # 4. 节点正确性 (30分)
    # 先加载原始 papers.json
    papers_path = os.path.join(workspace, "papers", "papers.json")
    try:
        raw = load_json(papers_path)
        all_papers = raw.get("papers", {})
    except:
        details.append({"item": "nodes correct", "score": 0, "max_score": 30, "passed": False, "reason": "cannot read papers/papers.json"})
        # 继续检查边但无节点信息，边也无法检查
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    valid_papers = get_valid_papers(all_papers)
    valid_ids = set(valid_papers.keys())
    nodes = graph.get("nodes", [])
    node_ids = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        pid = node.get("paper_id") or node.get("id")
        title = node.get("title")
        if pid and title:
            node_ids.add(pid)
    if node_ids == valid_ids:
        details.append({"item": "nodes correct", "score": 30, "max_score": 30, "passed": True, "reason": f"all {len(valid_ids)} valid papers present, no extras"})
        score += 30
    else:
        missing = valid_ids - node_ids
        extra = node_ids - valid_ids
        reason = f"missing: {missing}, extra: {extra}" if missing or extra else "unknown mismatch"
        details.append({"item": "nodes correct", "score": 0, "max_score": 30, "passed": False, "reason": reason})

    # 5. 边正确性 (40分)
    # 构建期望边集合
    expected_edges = set()
    for pid, info in valid_papers.items():
        for cite in info.get("citation_ids", []):
            if cite in valid_ids:
                expected_edges.add((pid, cite))
    agent_edges = graph.get("edges", [])
    agent_edge_set = set()
    for edge in agent_edges:
        src = edge.get("source") or edge.get("from")
        tgt = edge.get("target") or edge.get("to")
        if src and tgt:
            agent_edge_set.add((src, tgt))
    if agent_edge_set == expected_edges:
        details.append({"item": "edges correct", "score": 40, "max_score": 40, "passed": True, "reason": f"all {len(expected_edges)} edges correct"})
        score += 40
    else:
        missing_edges = expected_edges - agent_edge_set
        extra_edges = agent_edge_set - expected_edges
        reason = f"missing edges: {missing_edges}, extra edges: {extra_edges}" if missing_edges or extra_edges else "unknown mismatch"
        details.append({"item": "edges correct", "score": 0, "max_score": 40, "passed": False, "reason": reason})

    total_score = sum(d["score"] for d in details)
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
