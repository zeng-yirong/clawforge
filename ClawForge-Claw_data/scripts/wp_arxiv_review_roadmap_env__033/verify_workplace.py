import sys
import os
import json
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = {"total_score": 0, "details": []}

    # 1. 检查 output 目录是否存在
    output_dir = os.path.join(workspace, "output")
    if os.path.isdir(output_dir):
        results["details"].append({"item": "output目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "output目录已创建"})
    else:
        results["details"].append({"item": "output目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "output目录不存在"})
        # 如果目录不存在，后续检查无法进行，直接评分
        results["total_score"] = sum(d["score"] for d in results["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(results, f, indent=2)
        return

    # 2. 检查 review.md 存在且非空
    review_path = os.path.join(output_dir, "review.md")
    if os.path.isfile(review_path) and os.path.getsize(review_path) > 0:
        results["details"].append({"item": "review.md文件存在且非空", "score": 10, "max_score": 10, "passed": True, "reason": "review.md存在"})
    else:
        results["details"].append({"item": "review.md文件存在且非空", "score": 0, "max_score": 10, "passed": False, "reason": "review.md缺失或为空"})

    # 3. 检查 roadmap.mmd 存在且非空
    roadmap_path = os.path.join(output_dir, "roadmap.mmd")
    if os.path.isfile(roadmap_path) and os.path.getsize(roadmap_path) > 0:
        results["details"].append({"item": "roadmap.mmd文件存在且非空", "score": 10, "max_score": 10, "passed": True, "reason": "roadmap.mmd存在"})
    else:
        results["details"].append({"item": "roadmap.mmd文件存在且非空", "score": 0, "max_score": 10, "passed": False, "reason": "roadmap.mmd缺失或为空"})

    # 如果review或roadmap缺失，后续内容检查跳过，直接计算总分
    if not (os.path.isfile(review_path) and os.path.isfile(roadmap_path)):
        results["total_score"] = sum(d["score"] for d in results["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(results, f, indent=2)
        return

    # 读取初始论文数据（工作区中由 builder 生成的）
    papers_path = os.path.join(workspace, "data", "papers", "papers.json")
    with open(papers_path, "r") as f:
        data = json.load(f)
    raw_papers = data["papers"]

    # 按规则筛选有效论文（direction=efficient_vision, year不为None, 去重保留首次出现）
    seen_ids = set()
    valid_papers = []
    for p in raw_papers:
        pid = p["paper_id"]
        if p["direction"] == "efficient_vision" and p["year"] is not None and pid not in seen_ids:
            seen_ids.add(pid)
            valid_papers.append(p)
    # 按 year 升序排序
    valid_papers.sort(key=lambda x: x["year"])
    expected_ids = [p["paper_id"] for p in valid_papers]

    # 构建期望引用边（只保留两端都在 expected_ids 中的边）
    expected_edges = set()
    for p in valid_papers:
        for cited in p.get("citation_ids", []):
            if cited in expected_ids:
                expected_edges.add((p["paper_id"], cited))

    # 解析 review.md
    with open(review_path, "r") as f:
        review_content = f.read()
    # 提取所有 paper_xxx 形式的ID（按出现顺序）
    found_ids = re.findall(r'paper_\d+', review_content)
    # 去重但保留顺序（去重后顺序可能与found_ids首次出现顺序一致）
    seen_in_review = set()
    unique_found_ids = []
    for pid in found_ids:
        if pid not in seen_in_review:
            seen_in_review.add(pid)
            unique_found_ids.append(pid)

    # 比较论文列表
    if unique_found_ids == expected_ids:
        results["details"].append({"item": "review中论文ID列表完全正确（顺序一致）", "score": 30, "max_score": 30, "passed": True, "reason": "提取的ID列表与期望完全一致"})
    elif set(unique_found_ids) == set(expected_ids):
        results["details"].append({"item": "review中论文ID列表元素正确但顺序错误", "score": 15, "max_score": 30, "passed": False, "reason": "ID集合相同但顺序不符"})
    else:
        missing = set(expected_ids) - set(unique_found_ids)
        extra = set(unique_found_ids) - set(expected_ids)
        reason = f"缺失ID: {missing}, 多余ID: {extra}" if missing or extra else "其他错误"
        results["details"].append({"item": "review中论文ID列表不正确", "score": 0, "max_score": 30, "passed": False, "reason": reason})

    # 解析 roadmap.mmd
    with open(roadmap_path, "r") as f:
        roadmap_content = f.read()

    # 提取 mermaid 代码块
    mermaid_blocks = re.findall(r'```mermaid\s*(.*?)```', roadmap_content, re.DOTALL)
    if not mermaid_blocks:
        # 尝试没有代码块的情况
        mermaid_blocks = [roadmap_content]

    # 从所有块中提取节点ID和边
    node_pattern = re.compile(r'([a-zA-Z_]\w*)\s*[\[(]')
    edge_pattern = re.compile(r'(\w+)\s*-->\s*(\w+)')
    nodes_in_roadmap = set()
    edges_in_roadmap = set()
    for block in mermaid_blocks:
        for match in node_pattern.finditer(block):
            node = match.group(1)
            if node.startswith("paper_"):
                nodes_in_roadmap.add(node)
        for match in edge_pattern.finditer(block):
            src, dst = match.groups()
            if src.startswith("paper_") and dst.startswith("paper_"):
                edges_in_roadmap.add((src, dst))

    # 比较节点集合
    if nodes_in_roadmap == set(expected_ids):
        results["details"].append({"item": "roadmap中节点集合正确", "score": 20, "max_score": 20, "passed": True, "reason": "节点与期望完全一致"})
    else:
        missing_nodes = set(expected_ids) - nodes_in_roadmap
        extra_nodes = nodes_in_roadmap - set(expected_ids)
        reason = f"缺失节点: {missing_nodes}, 多余节点: {extra_nodes}" if missing_nodes or extra_nodes else "其他错误"
        results["details"].append({"item": "roadmap中节点集合不正确", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 比较边集合
    if edges_in_roadmap == expected_edges:
        results["details"].append({"item": "roadmap中边集合正确", "score": 20, "max_score": 20, "passed": True, "reason": "边与期望完全一致"})
    elif edges_in_roadmap and edges_in_roadmap.issubset(expected_edges) and expected_edges.issubset(edges_in_roadmap):
        # 判断是否方向相反？这里严格要求方向一致
        results["details"].append({"item": "roadmap中边集合不正确", "score": 0, "max_score": 20, "passed": False, "reason": "边集合不匹配"})
    else:
        missing_edges = expected_edges - edges_in_roadmap
        extra_edges = edges_in_roadmap - expected_edges
        reason = f"缺失边: {missing_edges}, 多余边: {extra_edges}" if missing_edges or extra_edges else "其他错误"
        results["details"].append({"item": "roadmap中边集合不正确", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 计算总分
    results["total_score"] = sum(d["score"] for d in results["details"])

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
