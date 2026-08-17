import sys
import os
import json
import re
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workdir = Path(workspace)
    score_details = []
    total_score = 0

    # 1. 检查 outputs 目录存在 (10分)
    outputs_dir = workdir / "outputs"
    if outputs_dir.is_dir():
        score_details.append({
            "item": "outputs directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Outputs directory found"
        })
    else:
        score_details.append({
            "item": "outputs directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Outputs directory not found"
        })

    # 2. 检查 review.md 存在 (10分)
    review_path = outputs_dir / "review.md"
    if review_path.is_file():
        score_details.append({
            "item": "review.md exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "review.md found"
        })
    else:
        score_details.append({
            "item": "review.md exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "review.md not found"
        })

    # 3. 检查 roadmap.mermaid 存在 (10分)
    roadmap_path = outputs_dir / "roadmap.mermaid"
    if roadmap_path.is_file():
        score_details.append({
            "item": "roadmap.mermaid exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "roadmap.mermaid found"
        })
    else:
        score_details.append({
            "item": "roadmap.mermaid exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "roadmap.mermaid not found"
        })

    # 如果 review.md 存在，解析内容
    review_ok = False
    roadmap_ok = False
    review_score = 0
    roadmap_score = 0

    # 先加载预期论文列表（从 papers.json 中筛选 direction='tool_augmented_reasoning'，排除年份>2025和重复id）
    papers_path = workdir / "data" / "papers.json"
    expected_papers = []
    if papers_path.is_file():
        with open(papers_path, "r") as f:
            papers_data = json.load(f)
        all_papers = papers_data.get("papers", [])
        # 去重：保留第一个出现的 paper_id
        seen_ids = set()
        unique_papers = []
        for p in all_papers:
            pid = p.get("paper_id")
            if pid not in seen_ids:
                seen_ids.add(pid)
                unique_papers.append(p)
        # 筛选方向为 tool_augmented_reasoning，年份≤2025（排除异常年份）
        for p in unique_papers:
            if p.get("direction") == "tool_augmented_reasoning" and isinstance(p.get("year"), int) and p["year"] <= 2025:
                expected_papers.append((p["year"], p["title"]))
        # 按年份排序
        expected_papers.sort(key=lambda x: x[0])
    else:
        score_details.append({
            "item": "papers.json source",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "papers.json not found, cannot validate review content"
        })

    if not expected_papers:
        # 如果没有预期论文，给0分但记录
        pass

    # 解析 review.md
    if review_path.is_file():
        with open(review_path, "r") as f:
            review_text = f.read()
        # 提取列表项，格式 "- 年份: 标题" 或 "- 年份 : 标题"
        pattern = r'^-\s*(\d{4})\s*:\s*(.+)$'
        found_items = re.findall(pattern, review_text, re.MULTILINE)
        # 转换为 (year, title) 元组，去除标题两端空格
        found_list = []
        for y, t in found_items:
            year = int(y)
            title = t.strip()
            found_list.append((year, title))
        # 比较 found_list 与 expected_papers
        if len(expected_papers) == len(found_list):
            match = True
            for (ey, et), (fy, ft) in zip(expected_papers, found_list):
                # 标题归一化比较（忽略大小写和空格）
                if ey != fy or et.lower().replace(" ", "") != ft.lower().replace(" ", ""):
                    match = False
                    break
            if match:
                review_score = 40
                review_ok = True
                score_details.append({
                    "item": "review.md content (list and order)",
                    "score": 40,
                    "max_score": 40,
                    "passed": True,
                    "reason": f"Found {len(found_list)} papers matching expected ones in correct order"
                })
            else:
                score_details.append({
                    "item": "review.md content (list and order)",
                    "score": 0,
                    "max_score": 40,
                    "passed": False,
                    "reason": "List items do not match expected papers or order"
                })
        elif len(found_list) > 0:
            # 部分匹配，给部分分数（每正确一篇10分，排序正确额外10分，这里简化：最多40分）
            correct_count = 0
            for (ey, et) in expected_papers:
                for (fy, ft) in found_list:
                    if ey == fy and et.lower().replace(" ", "") == ft.lower().replace(" ", ""):
                        correct_count += 1
                        break
            review_score = min(correct_count * 10, 30)  # 最多30分（3篇），排序正确再+10
            # 检查顺序是否正确（按年份）
            order_ok = True
            last_year = -1
            for (y, _) in found_list:
                if y < last_year:
                    order_ok = False
                    break
                last_year = y
            if order_ok:
                review_score += 10
            review_score = min(review_score, 40)
            score_details.append({
                "item": "review.md content (list and order)",
                "score": review_score,
                "max_score": 40,
                "passed": review_score == 40,
                "reason": f"Found {correct_count}/{len(expected_papers)} correct papers, order {'ok' if order_ok else 'not ok'}"
            })
        else:
            score_details.append({
                "item": "review.md content (list and order)",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": "No list items found in review.md"
            })

    # 解析 roadmap.mermaid
    if roadmap_path.is_file():
        with open(roadmap_path, "r") as f:
            roadmap_text = f.read()
        # 尝试提取 timeline 块内容
        # 通常格式： timeline\n  2021 : Title\n  2022 : Title
        # 也可以包含多个 section，我们提取所有类似 "年份 : 标题" 的行
        pattern2 = r'^\s*(\d{4})\s*:\s*(.+?)\s*$'
        found_road_items = re.findall(pattern2, roadmap_text, re.MULTILINE)
        road_list = [(int(y), t.strip()) for y, t in found_road_items]
        if len(road_list) == len(expected_papers):
            match = True
            for (ey, et), (fy, ft) in zip(expected_papers, road_list):
                if ey != fy or et.lower().replace(" ", "") != ft.lower().replace(" ", ""):
                    match = False
                    break
            if match:
                roadmap_score = 40
                roadmap_ok = True
                score_details.append({
                    "item": "roadmap.mermaid content (timeline nodes and order)",
                    "score": 40,
                    "max_score": 40,
                    "passed": True,
                    "reason": "Timeline nodes match expected papers in correct order"
                })
            else:
                score_details.append({
                    "item": "roadmap.mermaid content (timeline nodes and order)",
                    "score": 0,
                    "max_score": 40,
                    "passed": False,
                    "reason": "Timeline nodes do not match expected papers"
                })
        elif len(road_list) > 0:
            correct_count = 0
            for (ey, et) in expected_papers:
                for (fy, ft) in road_list:
                    if ey == fy and et.lower().replace(" ", "") == ft.lower().replace(" ", ""):
                        correct_count += 1
                        break
            roadmap_score = min(correct_count * 10, 30)
            # 检查顺序
            order_ok = True
            last_year = -1
            for (y, _) in road_list:
                if y < last_year:
                    order_ok = False
                    break
                last_year = y
            if order_ok:
                roadmap_score += 10
            roadmap_score = min(roadmap_score, 40)
            score_details.append({
                "item": "roadmap.mermaid content (timeline nodes and order)",
                "score": roadmap_score,
                "max_score": 40,
                "passed": roadmap_score == 40,
                "reason": f"Found {correct_count}/{len(expected_papers)} correct nodes, order {'ok' if order_ok else 'not ok'}"
            })
        else:
            score_details.append({
                "item": "roadmap.mermaid content (timeline nodes and order)",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": "No timeline nodes found in roadmap.mermaid"
            })

    # 计算总分
    total_score = sum(d["score"] for d in score_details)

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(workdir / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    verify()
