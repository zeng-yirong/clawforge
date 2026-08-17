import sys
import json
import os
import re
from pathlib import Path

def load_expected(workspace):
    """从工作区读取 papers.json，返回方向为 tool_augmented_reasoning 的论文列表，按年份排序"""
    papers_path = Path(workspace) / "data" / "papers" / "papers.json"
    if not papers_path.exists():
        return []
    with open(papers_path, "r") as f:
        data = json.load(f)
    papers = data.get("papers", [])
    # 筛选目标方向
    target = [p for p in papers if p["direction"] == "tool_augmented_reasoning"]
    # 按年份升序
    target.sort(key=lambda x: x["year"])
    return target

def parse_review(workspace):
    """解析 review.md，返回 (标题行, [(year, title)]) 或 None"""
    path = Path(workspace) / "review.md"
    if not path.exists():
        return None
    with open(path, "r") as f:
        lines = f.readlines()
    # 找标题
    title_line = None
    items = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and "tool-augmented reasoning" in stripped.lower():
            title_line = stripped
        m = re.match(r'^- \*\*(\d{4})\*\*：(.+)$', stripped)
        if m:
            items.append((int(m.group(1)), m.group(2).strip()))
    if title_line is None:
        return None
    return (title_line, items)

def parse_roadmap(workspace):
    """解析 roadmap.md，返回 timeline 节点列表 [(year, title)] 或 None"""
    path = Path(workspace) / "roadmap.md"
    if not path.exists():
        return None
    with open(path, "r") as f:
        content = f.read()
    # 提取 mermaid 代码块
    mermaid_match = re.search(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
    if not mermaid_match:
        return None
    mermaid_block = mermaid_match.group(1)
    lines = mermaid_block.split('\n')
    # 找 timeline 部分
    in_timeline = False
    nodes = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("timeline"):
            in_timeline = True
            continue
        if in_timeline and stripped.startswith("title"):
            continue  # 跳过标题行
        if in_timeline:
            m = re.match(r'^(\d{4})\s*:\s*(.+)$', stripped)
            if m:
                nodes.append((int(m.group(1)), m.group(2).strip()))
    return nodes if nodes else None

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    expected = load_expected(workspace)
    if not expected:
        # 没有目标论文，直接失败
        details = [{"item": "读取expected论文", "score": 0, "max_score": 100, "passed": False, "reason": "data/papers/papers.json 不存在或没有 tool_augmented_reasoning 论文"}]
        total = 0
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return

    details = []
    total = 0
    # 1. review.md 存在 (5)
    review_path = Path(workspace) / "review.md"
    review_exists = review_path.exists()
    details.append({
        "item": "review.md 文件存在",
        "score": 5 if review_exists else 0,
        "max_score": 5,
        "passed": review_exists,
        "reason": "存在" if review_exists else "不存在"
    })
    total += 5 if review_exists else 0

    # 2. roadmap.md 存在 (5)
    roadmap_path = Path(workspace) / "roadmap.md"
    roadmap_exists = roadmap_path.exists()
    details.append({
        "item": "roadmap.md 文件存在",
        "score": 5 if roadmap_exists else 0,
        "max_score": 5,
        "passed": roadmap_exists,
        "reason": "存在" if roadmap_exists else "不存在"
    })
    total += 5 if roadmap_exists else 0

    # 如果 review 存在，检查内容
    review_parsed = parse_review(workspace) if review_exists else None
    if review_parsed:
        title_line, review_items = review_parsed
        # 3. 标题正确 (10)
        title_ok = "tool-augmented reasoning" in title_line.lower()
        details.append({
            "item": "review.md 标题包含 'Tool-Augmented Reasoning'",
            "score": 10 if title_ok else 0,
            "max_score": 10,
            "passed": title_ok,
            "reason": f"标题行: {title_line}" if title_ok else "未找到正确标题"
        })
        total += 10 if title_ok else 0

        # 4. 论文条数正确 (5) + 顺序正确 (5) + 内容匹配 (10) = 20? 我们分成两项
        # 4a. 条目数量等于 expected 数量 (5)
        count_ok = len(review_items) == len(expected)
        details.append({
            "item": "review.md 论文条目数量正确",
            "score": 5 if count_ok else 0,
            "max_score": 5,
            "passed": count_ok,
            "reason": f"条目数 {len(review_items)}，期望 {len(expected)}"
        })
        total += 5 if count_ok else 0

        # 4b. 每个条目的年份和标题按顺序匹配 (15)
        match_score = 0
        max_match = 15
        if count_ok:
            for i, (yr, title) in enumerate(review_items):
                if i < len(expected):
                    exp = expected[i]
                    if yr == exp["year"] and title == exp["title"]:
                        match_score += 5  # 每个论文5分，共15
        details.append({
            "item": "review.md 论文年份和标题与 expected 完全匹配（顺序）",
            "score": match_score,
            "max_score": max_match,
            "passed": match_score == max_match,
            "reason": f"匹配得分 {match_score}/{max_match}"
        })
        total += match_score
    else:
        # review 文件不存在，所有相关项0分
        for item_name, max_s in [("review.md 标题包含 'Tool-Augmented Reasoning'", 10),
                                 ("review.md 论文条目数量正确", 5),
                                 ("review.md 论文年份和标题与 expected 完全匹配", 15)]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "review.md 不存在或解析失败"
            })

    # 如果 roadmap 存在，检查内容
    roadmap_parsed = parse_roadmap(workspace) if roadmap_exists else None
    if roadmap_parsed:
        nodes = roadmap_parsed
        # 5. Mermaid 代码块包含 timeline (5) + 节点数正确 (5) + 节点内容匹配 (15) = 25? 我们设3项
        # 5a. 存在 timeline 结构 (已解析成功即算)
        details.append({
            "item": "roadmap.md 包含有效的 Mermaid timeline",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "成功解析 timeline 节点"
        })
        total += 5

        # 5b. 节点数量正确 (5)
        node_count_ok = len(nodes) == len(expected)
        details.append({
            "item": "roadmap.md timeline 节点数量正确",
            "score": 5 if node_count_ok else 0,
            "max_score": 5,
            "passed": node_count_ok,
            "reason": f"节点数 {len(nodes)}，期望 {len(expected)}"
        })
        total += 5 if node_count_ok else 0

        # 5c. 节点年份和标题顺序匹配 (15)
        node_match_score = 0
        max_node = 15
        if node_count_ok:
            for i, (yr, title) in enumerate(nodes):
                if i < len(expected):
                    exp = expected[i]
                    if yr == exp["year"] and title == exp["title"]:
                        node_match_score += 5
        details.append({
            "item": "roadmap.md timeline 节点年份和标题与 expected 完全匹配",
            "score": node_match_score,
            "max_score": max_node,
            "passed": node_match_score == max_node,
            "reason": f"匹配得分 {node_match_score}/{max_node}"
        })
        total += node_match_score
    else:
        for item_name, max_s in [("roadmap.md 包含有效的 Mermaid timeline", 5),
                                 ("roadmap.md timeline 节点数量正确", 5),
                                 ("roadmap.md timeline 节点内容匹配", 15)]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "roadmap.md 不存在或解析失败"
            })

    # 额外：检查是否有混入其他方向论文（基于review和roadmap），但已经在匹配项中覆盖

    # 写入结果
    result = {
        "total_score": total,
        "details": details
    }
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total}")

if __name__ == "__main__":
    verify()
