import sys
import os
import json
import re
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    score_details = []
    total = 0

    # 1. 检查 output/citation_graph.json 是否存在
    target_path = ws / "output" / "citation_graph.json"
    if target_path.exists():
        score_details.append({
            "item": "output/citation_graph.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total += 10
    else:
        score_details.append({
            "item": "output/citation_graph.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，直接输出结果
        write_result(score_details, total)
        return

    # 2. 解析JSON合法性
    try:
        with open(target_path, "r") as f:
            graph = json.load(f)
        score_details.append({
            "item": "JSON格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析JSON"
        })
        total += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        write_result(score_details, total)
        return

    # 3. 结构检查：必须是字典，key是字符串，value是列表
    if isinstance(graph, dict) and all(
        isinstance(k, str) and isinstance(v, list) and all(isinstance(i, str) for i in v)
        for k, v in graph.items()
    ):
        score_details.append({
            "item": "输出结构正确（dict[str, list[str]]）",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "结构符合预期"
        })
        total += 10
    else:
        score_details.append({
            "item": "输出结构正确（dict[str, list[str]]）",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "结构不符合要求，key或value类型错误"
        })
        write_result(score_details, total)
        return

    # 4. 从 published 中重建期望图
    published_dir = ws / "papers" / "published"
    if not published_dir.exists():
        score_details.append({
            "item": "published目录存在",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "published目录不存在，无法验证"
        })
        write_result(score_details, total)
        return

    papers = {}
    for fpath in published_dir.glob("*.json"):
        with open(fpath, "r") as f:
            paper = json.load(f)
        pid = paper.get("paper_id")
        if pid:
            papers[pid] = paper

    # 计算期望图
    expected_graph = {}
    for pid, paper in papers.items():
        valid_citations = set()
        for cid in paper.get("citation_ids", []):
            # 排除自引用
            if cid == pid:
                continue
            # 排除不在papers集合中的引用
            if cid in papers:
                valid_citations.add(cid)
        # 去重后排序（为了后续比较方便，但值排序不影响结果）
        expected_graph[pid] = sorted(valid_citations)

    # 5. 检查自引用
    has_self = False
    for pid, cits in graph.items():
        if pid in cits:
            has_self = True
            break
    if not has_self:
        score_details.append({
            "item": "无自引用",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "输出中没有论文引用自身"
        })
        total += 10
    else:
        score_details.append({
            "item": "无自引用",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在自引用，需要去除"
        })

    # 6. 检查无效引用（引用不存在的论文ID）
    all_published_ids = set(papers.keys())
    invalid_refs = False
    for pid, cits in graph.items():
        for cid in cits:
            if cid not in all_published_ids:
                invalid_refs = True
                break
        if invalid_refs:
            break
    if not invalid_refs:
        score_details.append({
            "item": "无无效引用",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有引用的论文ID均在published集合中"
        })
        total += 10
    else:
        score_details.append({
            "item": "无无效引用",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "发现引用不存在的论文ID"
        })

    # 7. 核心：图完全匹配期望（50分）
    # 对agent输出也进行排序和整理，便于比较
    agent_graph_sorted = {k: sorted(set(v)) for k, v in graph.items()}
    # 但注意expect graph已经排序且去重
    if agent_graph_sorted == expected_graph:
        score_details.append({
            "item": "引用图完全正确",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": "输出与期望图完全一致"
        })
        total += 50
    else:
        # 计算匹配度（按边数）
        expected_edges = set()
        for pid, cits in expected_graph.items():
            for cid in cits:
                expected_edges.add((pid, cid))
        agent_edges = set()
        for pid, cits in agent_graph_sorted.items():
            for cid in cits:
                agent_edges.add((pid, cid))
        common = expected_edges & agent_edges
        extra = agent_edges - expected_edges
        missing = expected_edges - agent_edges
        if len(expected_edges) > 0:
            match_ratio = len(common) / len(expected_edges)
        else:
            match_ratio = 0
        part_score = int(round(50 * match_ratio))
        score_details.append({
            "item": "引用图正确性",
            "score": part_score,
            "max_score": 50,
            "passed": part_score == 50,
            "reason": f"边匹配 {len(common)}/{len(expected_edges)}，多余边 {len(extra)}，缺失边 {len(missing)}"
        })
        total += part_score

    # 8. 额外检查：是否有多余的论文ID（不在published中）
    extra_keys = set(agent_graph_sorted.keys()) - all_published_ids
    if extra_keys:
        # 扣分（最多扣10分，从已有总分中扣？但前面已经有结构分，这里作为扣分项）
        # 为了简单，在此扣10分，确保不超过0
        penalty = min(10, total)
        score_details.append({
            "item": "无多余论文ID",
            "score": -penalty,
            "max_score": 0,
            "passed": False,
            "reason": f"发现了不应存在的论文ID: {extra_keys}"
        })
        total -= penalty
    else:
        score_details.append({
            "item": "无多余论文ID",
            "score": 0,
            "max_score": 0,
            "passed": True,
            "reason": "所有key均为published中的论文ID"
        })

    # 确保总分在0-100
    total = max(0, min(100, total))
    write_result(score_details, total)

def write_result(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}")

if __name__ == "__main__":
    main()
