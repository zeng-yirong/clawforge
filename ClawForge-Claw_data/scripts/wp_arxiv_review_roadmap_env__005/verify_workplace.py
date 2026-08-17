import sys
import os
import json
import re
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base = Path(workspace).resolve()
    details = []
    total_score = 0

    # 1. 检查 ops 目录存在 (10分)
    ops_dir = base / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory missing"
        })

    # 2. 检查 review.md 存在 (10分)
    review_path = ops_dir / "review.md"
    if review_path.is_file():
        details.append({
            "item": "ops/review.md exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "review.md found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/review.md exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "review.md not found"
        })

    # 3. 检查 roadmap.mmd 存在 (10分)
    roadmap_path = ops_dir / "roadmap.mmd"
    if roadmap_path.is_file():
        details.append({
            "item": "ops/roadmap.mmd exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "roadmap.mmd found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/roadmap.mmd exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "roadmap.mmd not found"
        })

    # 如果文件缺失则直接返回剩余0分
    if not review_path.is_file() or not roadmap_path.is_file():
        write_score(total_score, details)
        return

    # 4. 读取 papers.json 并筛选目标论文：direction='tool_augmented_reasoning' 且 year>=2020 (30分)
    papers_path = base / "data/papers/papers.json"
    if not papers_path.is_file():
        details.append({
            "item": "data/papers/papers.json exists",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "papers.json not found"
        })
        write_score(total_score, details)
        return

    with open(papers_path) as f:
        data = json.load(f)
    all_papers = data.get("papers", [])
    # 过滤条件：direction 精确匹配、year 存在且 >= 2020
    target_papers = []
    for p in all_papers:
        if p.get("direction") == "tool_augmented_reasoning" and "year" in p:
            year = p["year"]
            if year >= 2020:
                target_papers.append(p)
    # 按年份排序
    target_papers.sort(key=lambda x: x["year"])
    expected_titles = {p["title"] for p in target_papers}
    expected_years = {p["year"] for p in target_papers}

    # 5. 解析 review.md 内容 (30分)
    with open(review_path, encoding="utf-8") as f:
        review_content = f.read()

    # 提取所有形如 "- title (year)" 或 "title (year)" 的行
    # 允许格式: - Title (2020)
    found_items = set()
    # 用正则匹配：行首可选 - 或数字列表，然后任意，最后括号内四位数字年份
    pattern = r'(?:^|\n)\s*(?:[-*]\s*)?(.+?)\s*\((\d{4})\)'
    matches = re.findall(pattern, review_content, re.MULTILINE)
    for title, year_str in matches:
        title = title.strip()
        year = int(year_str)
        # 仅当title在期望集合中才计入（避免干扰项）
        if title in expected_titles and year in expected_years:
            found_items.add(title)

    # 检查是否包含了所有期望论文
    missing = expected_titles - found_items
    extra = found_items - expected_titles  # 实际不应有额外，但如果有也扣分

    if not missing and not extra:
        details.append({
            "item": "review.md contains all target papers",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"All {len(expected_titles)} papers listed"
        })
        total_score += 30
    else:
        reason_parts = []
        if missing:
            reason_parts.append(f"Missing papers: {missing}")
        if extra:
            reason_parts.append(f"Unexpected papers: {extra}")
        details.append({
            "item": "review.md contains all target papers",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })

    # 6. 解析 roadmap.mmd 内容 (30分)
    with open(roadmap_path, encoding="utf-8") as f:
        roadmap_content = f.read()

    # 期望的Mermaid语法：包含 timeline 或 graph TD，以及年份节点
    # 简单检查是否包含每个年份的标记
    # 提取所有年份后跟冒号或横线的模式
    year_pattern = r'(\d{4})\s*[:：]\s*'
    roadmap_years = set()
    for match in re.finditer(year_pattern, roadmap_content):
        roadmap_years.add(int(match.group(1)))

    # 也尝试提取 timeline 块中的年份
    if not roadmap_years:
        # 可能是 graph TD 风格：N(2020: ...)
        year_pattern2 = r'(\d{4})\s*[:：]'
        for match in re.finditer(year_pattern2, roadmap_content):
            roadmap_years.add(int(match.group(1)))

    # 期望年份集合
    expected_years_set = {p["year"] for p in target_papers}
    missing_years = expected_years_set - roadmap_years
    # 额外年份（如果agent错误地加了其他年份，不扣分但也不加分）
    # 这里主要检查是否全部期望年份都出现
    if not missing_years:
        details.append({
            "item": "roadmap.mmd contains all years from target papers",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"All years {expected_years_set} present"
        })
        total_score += 30
    else:
        details.append({
            "item": "roadmap.mmd contains all years from target papers",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Missing years: {missing_years}"
        })

    # 写入结果
    write_score(total_score, details)

def write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
