import sys
import json
import os
import re
from pathlib import Path

def load_papers(workspace):
    papers_path = os.path.join(workspace, "data/papers/papers.json")
    with open(papers_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["papers"]

def filter_valid_papers(papers):
    valid = []
    for p in papers:
        # 检查必要字段
        if not all(k in p for k in ("paper_id", "title", "year", "abstract", "direction", "citation_ids")):
            continue
        if p["direction"] != "tool_augmented_reasoning":
            continue
        if not (2020 <= p["year"] <= 2024):
            continue
        valid.append(p)
    return valid

def build_expected_review(valid):
    # 按年份升序，同年按 paper_id 升序
    sorted_papers = sorted(valid, key=lambda x: (x["year"], x["paper_id"]))
    lines = []
    for p in sorted_papers:
        abstract_trunc = p["abstract"][:100]
        lines.append(f"- **{p['title']} ({p['year']})**: {abstract_trunc}")
    return "\n".join(lines)

def build_expected_graph(valid):
    node_ids = set()
    edges = set()  # (from, to)
    for p in valid:
        node_ids.add(p["paper_id"])
    for p in valid:
        for cited in p["citation_ids"]:
            if cited in node_ids:
                edges.add((p["paper_id"], cited))
    # 对节点和边排序以保证一致性（对验证不影响，但输出时可用于检查）
    sorted_nodes = sorted(node_ids)
    sorted_edges = sorted(edges)
    return sorted_nodes, sorted_edges

def parse_review(review_path):
    """解析 review.md，返回列表 (title, year, abstract_part)"""
    results = []
    if not os.path.exists(review_path):
        return None
    with open(review_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 查找所有以 "- **" 开头的行
    pattern = r'^\- \*\*(.+?) \((\d{4})\)\*\*: (.+)$'
    for line in content.splitlines():
        m = re.match(pattern, line.strip())
        if m:
            title = m.group(1).strip()
            year = int(m.group(2))
            abstract = m.group(3).strip()
            results.append((title, year, abstract))
    return results

def parse_mermaid(mermaid_path):
    """解析 roadmap.mermaid，返回 (节点集合, 边集合)"""
    if not os.path.exists(mermaid_path):
        return None, None
    with open(mermaid_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 提取节点定义：类似 p1[...] 或 p1[...] 前面可能有空格
    node_pattern = r'([a-zA-Z_]\w*)\['
    nodes = set(re.findall(node_pattern, content))
    # 提取边：类似 p1-->p2
    edge_pattern = r'([a-zA-Z_]\w*)-->(\(?[a-zA-Z_]\w*\)?)'
    edges = set()
    for m in re.finditer(edge_pattern, content):
        src = m.group(1)
        tgt = m.group(2).strip('()')
        edges.add((src, tgt))
    return nodes, edges

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查文件存在性 (20分)
    review_path = os.path.join(workspace, "review.md")
    mermaid_path = os.path.join(workspace, "roadmap.mermaid")
    score_review_exists = 10 if os.path.exists(review_path) else 0
    details.append({
        "item": "review.md exists",
        "score": score_review_exists,
        "max_score": 10,
        "passed": score_review_exists == 10,
        "reason": "File review.md found" if score_review_exists else "review.md not found"
    })
    score_mermaid_exists = 10 if os.path.exists(mermaid_path) else 0
    details.append({
        "item": "roadmap.mermaid exists",
        "score": score_mermaid_exists,
        "max_score": 10,
        "passed": score_mermaid_exists == 10,
        "reason": "File roadmap.mermaid found" if score_mermaid_exists else "roadmap.mermaid not found"
    })
    total_score += score_review_exists + score_mermaid_exists

    # 如果文件缺失，继续检查但跳过后续解析
    papers = load_papers(workspace)
    valid = filter_valid_papers(papers)
    expected_review = build_expected_review(valid)
    expected_nodes, expected_edges = build_expected_graph(valid)

    # 2. review.md 格式与内容 (40分)
    if os.path.exists(review_path):
        parsed = parse_review(review_path)
        if parsed is not None and len(parsed) > 0:
            format_score = 5
            details.append({
                "item": "review.md format (list entries)",
                "score": format_score,
                "max_score": 5,
                "passed": True,
                "reason": f"Found {len(parsed)} entries"
            })
            total_score += format_score

            # 检查条目数量是否等于有效论文数量
            expected_count = len(valid)
            count_score = 5 if len(parsed) == expected_count else 0
            details.append({
                "item": f"review.md entry count (expected {expected_count})",
                "score": count_score,
                "max_score": 5,
                "passed": count_score == 5,
                "reason": f"Got {len(parsed)} entries" if count_score else f"Expected {expected_count}, got {len(parsed)}"
            })
            total_score += count_score

            # 构建预期条目列表，按顺序比较
            expected_entries = []
            for p in sorted(valid, key=lambda x: (x["year"], x["paper_id"])):
                abstract_trunc = p["abstract"][:100]
                expected_entries.append((p["title"], p["year"], abstract_trunc))

            content_correct = True
            for i, (exp_title, exp_year, exp_abs) in enumerate(expected_entries):
                if i >= len(parsed):
                    content_correct = False
                    break
                act_title, act_year, act_abs = parsed[i]
                if act_title != exp_title or act_year != exp_year or act_abs != exp_abs:
                    content_correct = False
                    break
            content_score = 30 if content_correct else 0
            details.append({
                "item": "review.md content matches expected (titles, years, abstract prefix)",
                "score": content_score,
                "max_score": 30,
                "passed": content_correct,
                "reason": "All entries match" if content_correct else "Mismatch found"
            })
            total_score += content_score
        else:
            details.append({
                "item": "review.md format",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "Could not parse any entries from review.md"
            })
            # 还有 count 和 content 也得0分
            details.append({
                "item": "review.md entry count",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "No parseable entries"
            })
            details.append({
                "item": "review.md content matches",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": "No valid entries to compare"
            })
    else:
        # 文件不存在，剩余相关项都0分
        details.append({
            "item": "review.md format",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "File missing"
        })
        details.append({
            "item": "review.md entry count",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "File missing"
        })
        details.append({
            "item": "review.md content matches",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "File missing"
        })

    # 3. roadmap.mermaid 检查 (40分)
    if os.path.exists(mermaid_path):
        nodes, edges = parse_mermaid(mermaid_path)
        if nodes is not None:
            # 检查 graph LR 关键词
            with open(mermaid_path, "r") as f:
                content = f.read()
            has_graph_lr = "graph LR" in content
            graph_score = 5 if has_graph_lr else 0
            details.append({
                "item": "roadmap.mermaid contains 'graph LR'",
                "score": graph_score,
                "max_score": 5,
                "passed": has_graph_lr,
                "reason": "Contains graph LR" if has_graph_lr else "Missing graph LR"
            })
            total_score += graph_score

            # 节点集比较
            exp_nodes_set = set(expected_nodes)
            nodes_match = nodes == exp_nodes_set
            node_score = 15 if nodes_match else 0
            details.append({
                "item": "roadmap.mermaid node set matches expected",
                "score": node_score,
                "max_score": 15,
                "passed": nodes_match,
                "reason": f"Nodes match (count {len(exp_nodes_set)})" if nodes_match else f"Expected {exp_nodes_set}, got {nodes}"
            })
            total_score += node_score

            # 边集比较
            exp_edges_set = set(expected_edges)
            edges_match = edges == exp_edges_set
            edge_score = 20 if edges_match else 0
            details.append({
                "item": "roadmap.mermaid edge set matches expected",
                "score": edge_score,
                "max_score": 20,
                "passed": edges_match,
                "reason": f"Edges match (count {len(exp_edges_set)})" if edges_match else f"Expected {exp_edges_set}, got {edges}"
            })
            total_score += edge_score
        else:
            details.append({
                "item": "roadmap.mermaid parse",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "Could not parse nodes/edges"
            })
            details.append({
                "item": "roadmap.mermaid node set",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "Parse failed"
            })
            details.append({
                "item": "roadmap.mermaid edge set",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Parse failed"
            })
    else:
        details.append({
            "item": "roadmap.mermaid contains 'graph LR'",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "File missing"
        })
        details.append({
            "item": "roadmap.mermaid node set",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "File missing"
        })
        details.append({
            "item": "roadmap.mermaid edge set",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "File missing"
        })

    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    main()
