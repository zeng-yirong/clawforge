import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace)
    score_details = []
    total_score = 0

    # ---------- 1. 检查产物文件是否存在 (10分) ----------
    result_path = workspace / "tool_augmented_reasoning_review.json"
    if result_path.exists():
        score_details.append({
            "item": "产物文件 existence",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件 tool_augmented_reasoning_review.json 存在"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "产物文件 existence",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件 tool_augmented_reasoning_review.json 不存在"
        })
        # 后续检查无法进行，直接写结果
        write_score(workspace, total_score, score_details)
        return

    # ---------- 2. JSON 合法性 (10分) ----------
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 合法性",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON 解析成功"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "JSON 合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        write_score(workspace, total_score, score_details)
        return

    # ---------- 3. papers 数组长度 (20分) ----------
    papers = data.get("papers")
    if not isinstance(papers, list):
        score_details.append({
            "item": "papers 数组存在且为列表",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "缺少 papers 字段或不是列表"
        })
    else:
        expected_count = 3  # 只有 tar_001, tar_002, tar_003 有效
        if len(papers) == expected_count:
            score_details.append({
                "item": "papers 数组长度",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": f"正确包含 {expected_count} 篇论文"
            })
            total_score += 20
        else:
            score_details.append({
                "item": "papers 数组长度",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"期望 {expected_count} 篇，实际 {len(papers)} 篇"
            })

    # ---------- 4. 年份升序及摘要有效性 (15分 + 15分) ----------
    if len(papers) >= 2:
        years = [p.get("year") for p in papers]
        abstracts = [p.get("abstract", "") for p in papers]
        # 检查每个 year 是 int 且 >= 2019 <= 2024 (实际只有2021-2023)
        year_ok = all(isinstance(y, int) and 2019 <= y <= 2024 for y in years)
        sorted_ok = years == sorted(years)
        abstract_ok = all(isinstance(a, str) and len(a.strip()) > 0 for a in abstracts)

        year_score = 0
        if year_ok and sorted_ok:
            year_score = 15
            total_score += 15
        score_details.append({
            "item": "年份格式与升序",
            "score": year_score,
            "max_score": 15,
            "passed": year_ok and sorted_ok,
            "reason": f"年份列表: {years}, 格式正确且升序" if (year_ok and sorted_ok) else f"年份问题: {years}"
        })

        abstract_score = 0
        if abstract_ok:
            abstract_score = 15
            total_score += 15
        score_details.append({
            "item": "abstract 非空",
            "score": abstract_score,
            "max_score": 15,
            "passed": abstract_ok,
            "reason": "所有 abstract 非空" if abstract_ok else "存在空的 abstract"
        })
    else:
        # 长度不足时酌情给0
        score_details.append({
            "item": "年份升序",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "papers 数量不足无法判断顺序"
        })
        score_details.append({
            "item": "abstract 非空",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "papers 数量不足无法判断"
        })

    # ---------- 5. roadmap 数组 (15分) ----------
    roadmap = data.get("roadmap")
    if not isinstance(roadmap, list):
        score_details.append({
            "item": "roadmap 存在且为列表",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "缺少 roadmap 字段或不是列表"
        })
    else:
        expected_roadmap = [
            {"year": 2021, "title": "Tool Augmented Reasoning with LLMs"},
            {"year": 2022, "title": "Enhancing Reasoning via Tool Use"},
            {"year": 2023, "title": "A Survey of Tool-Augmented Reasoning"}
        ]
        # 允许 roadmap 中元素格式略有差异（如只包含 year 和 title），但不能缺少
        matched = True
        if len(roadmap) != len(expected_roadmap):
            matched = False
        else:
            for i, item in enumerate(roadmap):
                exp = expected_roadmap[i]
                if item.get("year") != exp["year"] or item.get("title") != exp["title"]:
                    matched = False
                    break
        if matched:
            score_details.append({
                "item": "roadmap 内容正确",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "roadmap 包含正确的三年节点"
            })
            total_score += 15
        else:
            score_details.append({
                "item": "roadmap 内容正确",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"roadmap 内容与期望不符: 期望 {expected_roadmap}, 实际 {roadmap}"
            })

    # ---------- 6. 无多余顶层字段 (15分) ----------
    allowed_top_keys = {"papers", "roadmap"}
    actual_keys = set(data.keys())
    extra = actual_keys - allowed_top_keys
    if not extra:
        score_details.append({
            "item": "无多余顶层字段",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "仅包含 papers 和 roadmap"
        })
        total_score += 15
    else:
        score_details.append({
            "item": "无多余顶层字段",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"存在多余字段: {extra}"
        })

    # 确保总分不超过100
    final_score = min(total_score, 100)
    write_score(workspace, final_score, score_details)

def write_score(workspace, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
