import sys
import os
import json
import re
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    max_total = 100
    details = []

    # ---------- 1. 检查文件存在 (10分) ----------
    files_ok = True
    for fname in ["review.md", "roadmap.mmd"]:
        fpath = os.path.join(workspace, fname)
        if not os.path.isfile(fpath):
            details.append({
                "item": f"File exists: {fname}",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"File {fname} not found"
            })
            files_ok = False
        else:
            details.append({
                "item": f"File exists: {fname}",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Found"
            })
    if not files_ok:
        # 如果任何一个文件缺失，后续无法进行，直接返回
        details.insert(0, {"item": "Overall", "score": 0, "max_score": 100, "passed": False, "reason": "Missing required files"})
        _write_score(workspace, 0, details)
        return

    # 读取标准答案：目标方向论文ID
    papers_path = os.path.join(workspace, "data/papers/papers.json")
    if not os.path.isfile(papers_path):
        details.append({"item": "Read papers.json", "score": 0, "max_score": 10, "passed": False, "reason": "papers.json missing"})
        _write_score(workspace, 0, details)
        return
    with open(papers_path, "r") as f:
        data = json.load(f)
    papers = data.get("papers", [])
    tar_ids = set()
    tar_papers_dict = {}
    for p in papers:
        if p.get("direction") == "tool_augmented_reasoning":
            pid = p["paper_id"]
            tar_ids.add(pid)
            tar_papers_dict[pid] = p

    # ---------- 2. 解析 review.md ----------
    review_path = os.path.join(workspace, "review.md")
    with open(review_path, "r") as f:
        review_text = f.read()
    # 提取所有 paper_\d{3} 形式的ID
    review_ids = set(re.findall(r'paper_\d{3}', review_text))
    # 检查是否完全匹配
    correct_ids = tar_ids == review_ids
    if correct_ids:
        details.append({
            "item": "review.md contains exactly the target paper IDs",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"IDs match: {sorted(tar_ids)}"
        })
    else:
        extra = review_ids - tar_ids
        missing = tar_ids - review_ids
        reason_parts = []
        if extra:
            reason_parts.append(f"Extra IDs: {sorted(extra)}")
        if missing:
            reason_parts.append(f"Missing IDs: {sorted(missing)}")
        details.append({
            "item": "review.md contains exactly the target paper IDs",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })

    # ---------- 3. 解析 roadmap.mmd ----------
    roadmap_path = os.path.join(workspace, "roadmap.mmd")
    with open(roadmap_path, "r") as f:
        roadmap_text = f.read()
    # 提取所有节点ID（出现在方括号内或者作为节点定义）
    # 兼容格式: paper_001[...] 或者 paper_001["..."] 或者 直接 paper_001
    node_ids = set(re.findall(r'paper_\d{3}', roadmap_text))
    # 检查节点ID集合是否与目标一致
    nodes_ok = node_ids == tar_ids
    if nodes_ok:
        details.append({
            "item": "roadmap.mmd contains all target paper IDs as nodes",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"Node IDs match: {sorted(tar_ids)}"
        })
    else:
        extra_nodes = node_ids - tar_ids
        missing_nodes = tar_ids - node_ids
        reason_parts = []
        if extra_nodes:
            reason_parts.append(f"Extra node IDs: {sorted(extra_nodes)}")
        if missing_nodes:
            reason_parts.append(f"Missing node IDs: {sorted(missing_nodes)}")
        details.append({
            "item": "roadmap.mmd contains all target paper IDs as nodes",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })

    # 检查是否存在至少一条引用边 (paper_xxx --> paper_yyy)
    edge_pattern = r'paper_\d{3}\s*-->.*paper_\d{3}'
    has_edge = bool(re.search(edge_pattern, roadmap_text))
    if has_edge:
        details.append({
            "item": "roadmap.mmd contains at least one citation edge",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Edge pattern found"
        })
    else:
        details.append({
            "item": "roadmap.mmd contains at least one citation edge",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "No edge matching pattern paper_\\d{3} --> paper_\\d{3} found"
        })

    # ---------- 4. 检查引用边是否至少覆盖一条真实引用（可选加分，但这里已经包含在上一条中）
    # 更细致的：验证至少一条边对应实际的 citation_ids
    # 我们提取所有边关系
    edge_matches = re.findall(r'(paper_\d{3})\s*-->\s*(.*?)(?:[\s\n]|$)', roadmap_text)
    # 简化：只要存在一条边的源和目标都在tar_ids中，并且目标在源的citation_ids中
    found_real_edge = False
    if edge_matches:
        for src, rest in edge_matches:
            # rest 可能包含多个目标，我们取第一个 paper_id
            tgt_match = re.search(r'paper_\d{3}', rest)
            if tgt_match:
                tgt = tgt_match.group()
                if src in tar_papers_dict and tgt in tar_papers_dict:
                    if tgt in tar_papers_dict[src].get("citation_ids", []):
                        found_real_edge = True
                        break
    if found_real_edge:
        details.append({
            "item": "At least one edge matches an actual citation in the data",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Edge corresponds to a real citation"
        })
    else:
        details.append({
            "item": "At least one edge matches an actual citation in the data",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "No edge aligns with the paper citation_ids"
        })

    # ---------- 5. 检查 review.md 和 roadmap.mmd 内容非空且合法 Markdown/Mermaid (5分) ----------
    content_ok = True
    if len(review_text.strip()) < 50:
        details.append({
            "item": "review.md content length >= 50 chars",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Too short"
        })
        content_ok = False
    else:
        details.append({
            "item": "review.md content length >= 50 chars",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "OK"
        })
    # roadmap.mmd 包含Mermaid图的基本语法（graph / flowchart / timeline 等）
    mermaid_keywords = ['graph', 'flowchart', 'timeline', 'sequenceDiagram', 'gantt']
    if any(kw in roadmap_text.lower() for kw in mermaid_keywords):
        details.append({
            "item": "roadmap.mmd contains Mermaid syntax",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Mermaid keyword found"
        })
    else:
        details.append({
            "item": "roadmap.mmd contains Mermaid syntax",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "No typical Mermaid keyword (graph/flowchart/timeline etc.)"
        })

    # ---------- 汇总总分 ----------
    total_score = sum(d["score"] for d in details)
    details.insert(0, {
        "item": "Overall",
        "score": total_score,
        "max_score": max_total,
        "passed": total_score >= 80,
        "reason": f"Scored {total_score}/{max_total}"
    })

    _write_score(workspace, total_score, details)
    print(f"Verification complete. Score: {total_score}/{max_total}")


def _write_score(workspace, score, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)


if __name__ == "__main__":
    main()
