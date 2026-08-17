import sys
import os
import json
import re
from pathlib import Path

def load_papers(workspace):
    """加载原始论文数据，用于年份对照和正确答案"""
    path = os.path.join(workspace, "data", "papers", "papers.json")
    if not os.path.isfile(path):
        return None, None
    with open(path, "r") as f:
        data = json.load(f)
    papers = data.get("papers", [])
    # 构建 id->year 映射
    year_map = {}
    for p in papers:
        year_map[p["paper_id"]] = p["year"]
    # 确定正确答案：方向 tool_augmented_reasoning, year>=2020, abstract 非空
    correct_ids = set()
    for p in papers:
        if (p["direction"] == "tool_augmented_reasoning" and
            p["year"] >= 2020 and
            p["abstract"].strip()):
            correct_ids.add(p["paper_id"])
    return correct_ids, year_map

def extract_ids_from_text(text):
    """提取文本中所有形如 paper_\d+ 的 ID"""
    pattern = r'paper_\d+'
    return set(re.findall(pattern, text))

def extract_ordered_ids_from_text(text):
    """提取文本中所有出现顺序的 paper_id 列表（用于顺序检查）"""
    pattern = r'paper_\d+'
    return re.findall(pattern, text)

def extract_node_ids_from_mermaid(text):
    """从 Mermaid 中提取节点内的 paper_id（eg. paper_001[...] 或 paper_001((...))）"""
    # 匹配 node_id[...] 或 node_id((...)) 等形式，但只关心 paper_\d+
    pattern = r'paper_\d+'
    return set(re.findall(pattern, text))

def extract_edge_sequence_from_mermaid(text):
    """提取 Mermaid 中所有形如 paper_xxx-->paper_yyy 的边，按出现顺序返回列表"""
    # 允许空格和换行
    edge_pattern = r'paper_\d+\s*-->\s*paper_\d+'
    matches = re.findall(edge_pattern, text)
    # 每对返回 (from, to)
    edges = []
    for m in matches:
        parts = re.split(r'\s*-->\s*', m)
        edges.append((parts[0].strip(), parts[1].strip()))
    return edges

def verify(workspace):
    details = []
    total_score = 0

    # --- 检查 results 目录 ---
    results_dir = os.path.join(workspace, "results")
    dir_exists = os.path.isdir(results_dir)
    details.append({
        "item": "results directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Directory found" if dir_exists else "Missing results/ directory"
    })
    if dir_exists:
        total_score += 10

    # --- 检查 review.md ---
    review_path = os.path.join(results_dir, "review.md")
    review_exists = os.path.isfile(review_path)
    details.append({
        "item": "review.md exists",
        "score": 10 if review_exists else 0,
        "max_score": 10,
        "passed": review_exists,
        "reason": "File found" if review_exists else "Missing review.md"
    })
    if review_exists:
        total_score += 10

    # --- 检查 roadmap.mmd ---
    mmd_path = os.path.join(results_dir, "roadmap.mmd")
    mmd_exists = os.path.isfile(mmd_path)
    details.append({
        "item": "roadmap.mmd exists",
        "score": 10 if mmd_exists else 0,
        "max_score": 10,
        "passed": mmd_exists,
        "reason": "File found" if mmd_exists else "Missing roadmap.mmd"
    })
    if mmd_exists:
        total_score += 10

    # 如果两个核心文件都不存在，直接返回
    if not (review_exists and mmd_exists):
        final_score = total_score
        result = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Total: {final_score}/100")
        return

    # --- 加载正确答案 ---
    correct_ids, year_map = load_papers(workspace)
    if correct_ids is None:
        details.append({
            "item": "Load papers.json",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Cannot read data/papers/papers.json"
        })
        final_score = total_score
        result = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Total: {final_score}/100")
        return
    else:
        # 额外加分：能够读取原始数据（但已经计在目录检查中，这里直接使用）
        pass

    # --- 检查 review.md 内容 ---
    with open(review_path, "r") as f:
        review_text = f.read()

    # 检查非空
    txt_len = len(review_text.strip())
    details.append({
        "item": "review.md is non-empty",
        "score": 5 if txt_len > 50 else 0,
        "max_score": 5,
        "passed": txt_len > 50,
        "reason": f"Content length {txt_len} chars" if txt_len > 50 else "Too short (<50 chars)"
    })
    if txt_len > 50:
        total_score += 5

    # 提取 ID 集合
    review_ids = extract_ids_from_text(review_text)
    ids_match = (review_ids == correct_ids)
    details.append({
        "item": "review.md paper IDs exactly match correct set",
        "score": 30 if ids_match else 0,
        "max_score": 30,
        "passed": ids_match,
        "reason": f"Found IDs: {sorted(review_ids)}; expected: {sorted(correct_ids)}" if not ids_match else "All correct papers included"
    })
    if ids_match:
        total_score += 30

    # 检查 ID 顺序（按年份升序）
    if ids_match:
        ordered_ids_in_review = extract_ordered_ids_from_text(review_text)
        # 去重但保留首次出现顺序
        seen = set()
        unique_ordered = []
        for pid in ordered_ids_in_review:
            if pid not in seen:
                seen.add(pid)
                unique_ordered.append(pid)
        # 按年份排序后的正确顺序
        correct_ordered = sorted(correct_ids, key=lambda pid: (year_map[pid], pid))  # 同一年按 ID 字母
        order_correct = (unique_ordered == correct_ordered)
        details.append({
            "item": "review.md paper order by year (ascending)",
            "score": 10 if order_correct else 0,
            "max_score": 10,
            "passed": order_correct,
            "reason": f"Order found: {unique_ordered}; expected: {correct_ordered}" if not order_correct else "Order correct"
        })
        if order_correct:
            total_score += 10
    else:
        details.append({
            "item": "review.md paper order by year (skipped due to wrong set)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Paper set mismatch, cannot check order"
        })

    # --- 检查 roadmap.mmd ---
    with open(mmd_path, "r") as f:
        mmd_text = f.read()

    # 检查非空
    mmd_len = len(mmd_text.strip())
    details.append({
        "item": "roadmap.mmd is non-empty",
        "score": 5 if mmd_len > 50 else 0,
        "max_score": 5,
        "passed": mmd_len > 50,
        "reason": f"Content length {mmd_len} chars" if mmd_len > 50 else "Too short (<50 chars)"
    })
    if mmd_len > 50:
        total_score += 5

    # 提取节点 ID 集合
    mmd_node_ids = extract_node_ids_from_mermaid(mmd_text)
    node_match = (mmd_node_ids == correct_ids)
    details.append({
        "item": "roadmap.mmd node IDs exactly match correct set",
        "score": 25 if node_match else 0,
        "max_score": 25,
        "passed": node_match,
        "reason": f"Found node IDs: {sorted(mmd_node_ids)}; expected: {sorted(correct_ids)}" if not node_match else "All correct papers present as nodes"
    })
    if node_match:
        total_score += 25

    # 检查边顺序（按年份升序的链）
    if node_match:
        edges = extract_edge_sequence_from_mermaid(mmd_text)
        # 期望的边：按年份升序连接所有正确 ID
        correct_ordered = sorted(correct_ids, key=lambda pid: (year_map[pid], pid))
        expected_edges = []
        for i in range(len(correct_ordered)-1):
            expected_edges.append((correct_ordered[i], correct_ordered[i+1]))
        edge_match = (edges == expected_edges)
        details.append({
            "item": "roadmap.mmd edges follow correct chronological order",
            "score": 10 if edge_match else 0,
            "max_score": 10,
            "passed": edge_match,
            "reason": f"Edges found: {edges}; expected: {expected_edges}" if not edge_match else "Edge order correct"
        })
        if edge_match:
            total_score += 10
        else:
            # 如果边不对但节点对，给部分分（但不给满分）
            # 这里不额外扣分，只给0分
            pass
    else:
        details.append({
            "item": "roadmap.mmd edge order (skipped due to node mismatch)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Node set mismatch, cannot verify edges"
        })

    # 总分封顶 100
    final_score = min(total_score, 100)
    result = {"total_score": final_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total: {final_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
