import json
import os
import sys
import re

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查必要目录结构 (10分)
    score = 0
    max_score = 10
    reason = ""
    papers_dir = os.path.join(workspace, "papers")
    graph_dir = os.path.join(workspace, "graph")
    if os.path.isdir(papers_dir) and os.path.isdir(graph_dir):
        score = 10
        reason = "papers/ 和 graph/ 目录均存在"
    else:
        reason = "缺少目录: " + ("" if os.path.isdir(papers_dir) else "papers/ ") + ("" if os.path.isdir(graph_dir) else "graph/")
    details.append({"item": "目录结构", "score": score, "max_score": max_score, "passed": score == max_score, "reason": reason})
    total_score += score

    # 2. 检查输出文件 graph/citation_graph.json 是否存在且合法 JSON (20分)
    output_path = os.path.join(workspace, "graph", "citation_graph.json")
    score = 0
    max_score = 20
    reason = ""
    try:
        if not os.path.isfile(output_path):
            raise FileNotFoundError("文件不存在")
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "nodes" not in data or "edges" not in data:
            raise ValueError("缺少 nodes 或 edges 字段")
        if not isinstance(data["nodes"], list) or not isinstance(data["edges"], list):
            raise ValueError("nodes 或 edges 必须是数组")
        score = 20
        reason = "文件存在且 JSON 结构正确"
    except Exception as e:
        reason = f"文件读取/解析失败: {str(e)}"
    details.append({"item": "输出文件格式", "score": score, "max_score": max_score, "passed": score == max_score, "reason": reason})
    total_score += score

    # 如果上一步失败，后续检查无意义，直接返回
    if score < 20:
        total_score = int(round(total_score))
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 检查节点列表 (30分)：必须包含所有有效论文，且每个节点有 id 和 title
    score = 0
    max_score = 30
    reason_parts = []
    nodes = data["nodes"]
    # 有效论文 ID (根据 papers 目录下可解析的 JSON 文件确定)
    valid_papers = {}
    for fname in os.listdir(papers_dir):
        fpath = os.path.join(papers_dir, fname)
        if not fname.endswith(".json"):
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                paper = json.load(f)
            if not isinstance(paper, dict) or "paper_id" not in paper or "title" not in paper:
                continue
            pid = paper["paper_id"]
            # 跳过损坏文件（我们已知 P006 是坏的，但通用判断：如果有 paper_id 且 title 非空，暂时保留）
            # 但为了准确，我们硬编码让验证器识别有效论文为 P001-P005（因为 P006 的 JSON 是不完整，无法解析）
            # 更健壮的做法：实际尝试解析，P006 文件是语法错误，json.load 会抛异常，所以不会被加入
            valid_papers[pid] = paper["title"]
        except (json.JSONDecodeError, ValueError):
            continue  # 忽略格式错误文件

    node_ids = {node.get("id") for node in nodes if isinstance(node, dict)}
    node_titles = {node.get("id"): node.get("title") for node in nodes if isinstance(node, dict)}
    # 检查是否所有有效论文都在节点中
    missing = [pid for pid in valid_papers if pid not in node_ids]
    extra = [pid for pid in node_ids if pid not in valid_papers]
    title_errors = []
    for pid, title in valid_papers.items():
        if pid in node_titles and node_titles[pid] != title:
            title_errors.append(f"{pid}: 期望标题 '{title}'，实际 '{node_titles[pid]}'")
    if not missing and not extra and not title_errors:
        score = 30
        reason_parts.append("节点列表完全正确")
    else:
        if missing:
            reason_parts.append(f"缺少节点: {missing}")
        if extra:
            reason_parts.append(f"多余节点: {extra}")
        if title_errors:
            reason_parts.extend(title_errors)
    reason = "; ".join(reason_parts) if reason_parts else ""
    details.append({"item": "节点列表", "score": score, "max_score": max_score, "passed": score == max_score, "reason": reason})
    total_score += score

    # 4. 检查边列表 (40分)
    score = 0
    max_score = 40
    edges = data["edges"]
    # 预期边：根据有效的论文citation_ids计算，仅保留目标ID在有效论文中的边
    expected_edges = set()
    # 重新读取有效论文的citation_ids（避免重复解析）
    valid_papers_full = {}
    for fname in os.listdir(papers_dir):
        fpath = os.path.join(papers_dir, fname)
        if not fname.endswith(".json"):
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                paper = json.load(f)
            if not isinstance(paper, dict) or "paper_id" not in paper or "citation_ids" not in paper:
                continue
            pid = paper["paper_id"]
            if pid in valid_papers:  # 只考虑有效论文的引用
                for target in paper["citation_ids"]:
                    if target in valid_papers:
                        expected_edges.add((pid, target))
        except (json.JSONDecodeError, ValueError):
            continue

    actual_edges = set()
    for edge in edges:
        if isinstance(edge, dict) and "source" in edge and "target" in edge:
            actual_edges.add((edge["source"], edge["target"]))
    missing_edges = expected_edges - actual_edges
    extra_edges = actual_edges - expected_edges
    if not missing_edges and not extra_edges:
        score = 40
        reason = "边列表完全正确"
    else:
        reason_parts = []
        if missing_edges:
            reason_parts.append(f"缺少边: {sorted(missing_edges)}")
        if extra_edges:
            reason_parts.append(f"多余边: {sorted(extra_edges)}")
        reason = "; ".join(reason_parts)
    details.append({"item": "边列表", "score": score, "max_score": max_score, "passed": score == max_score, "reason": reason})
    total_score += score

    total_score = int(round(total_score))
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
