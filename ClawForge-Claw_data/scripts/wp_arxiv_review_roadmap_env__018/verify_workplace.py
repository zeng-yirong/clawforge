import sys
import os
import json
import re
from pathlib import Path

def verify(workspace: str):
    """评分：检查output目录、两个文件、内容正确性（论文列表、摘要、mermaid timeline）"""
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. output 目录存在 (10分)
    output_dir = ws / "output"
    if output_dir.exists() and output_dir.is_dir():
        details.append({"item": "output目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "output目录已创建"})
        total_score += 10
    else:
        details.append({"item": "output目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "output目录不存在"})
        # 后续检查文件会失败，但先给0分继续

    # 2. review.md 文件存在 (15分)
    review_path = output_dir / "review.md"
    if review_path.exists() and review_path.is_file():
        details.append({"item": "review.md存在", "score": 15, "max_score": 15, "passed": True, "reason": "review.md已生成"})
        total_score += 15
    else:
        details.append({"item": "review.md存在", "score": 0, "max_score": 15, "passed": False, "reason": "review.md不存在"})
        review_text = ""
    if review_path.exists():
        review_text = review_path.read_text(encoding="utf-8")
    else:
        review_text = ""

    # 3. roadmap.mermaid 文件存在 (15分)
    roadmap_path = output_dir / "roadmap.mermaid"
    if roadmap_path.exists() and roadmap_path.is_file():
        details.append({"item": "roadmap.mermaid存在", "score": 15, "max_score": 15, "passed": True, "reason": "roadmap.mermaid已生成"})
        total_score += 15
    else:
        details.append({"item": "roadmap.mermaid存在", "score": 0, "max_score": 15, "passed": False, "reason": "roadmap.mermaid不存在"})

    # 读取参考数据（从工作区的 papers 和 attachments）
    papers_path = ws / "papers" / "papers.json"
    attachments_json_path = ws / "data" / "attachments.json"
    if not papers_path.exists() or not attachments_json_path.exists():
        # 环境本身缺失，直接返回低分
        score = total_score
        details.append({"item": "环境依赖检查", "score": 0, "max_score": 0, "passed": False, "reason": "缺少papers.json或attachments.json"})
        result = {"total_score": score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    with open(papers_path) as f:
        papers_data = json.load(f)
    with open(attachments_json_path) as f:
        att_data = json.load(f)

    papers_list = papers_data.get("papers", [])
    # 筛选 efficient_vision 方向
    ev_papers = [p for p in papers_list if p.get("direction") == "efficient_vision"]
    # 按年份排序，同年按标题排序
    ev_papers_sorted = sorted(ev_papers, key=lambda p: (p["year"], p["title"]))

    # 获取这些论文的附件摘要内容
    # 构建附件映射: paper_id -> (file_path, content)
    att_map = {}
    for att in att_data.get("attachments", []):
        pid = att.get("paper_id")
        path = att.get("path")
        if pid and path:
            full_path = ws / path
            if full_path.exists():
                att_map[pid] = full_path.read_text(encoding="utf-8")
            else:
                att_map[pid] = ""

    # 4. 检查 review.md 内容 (重点 40分)
    # 4a. 必须包含每个论文的标题 (20分，每个4分)
    score_titles = 0
    max_title_score = 20
    title_issues = []
    for p in ev_papers_sorted:
        title = p["title"]
        if title in review_text:
            score_titles += 4
        else:
            title_issues.append(f"缺失论文标题: {title}")
    details.append({
        "item": "review.md包含所有efficient_vision论文标题",
        "score": score_titles,
        "max_score": max_title_score,
        "passed": score_titles == max_title_score,
        "reason": "正确" if score_titles == max_title_score else "; ".join(title_issues)
    })
    total_score += score_titles

    # 4b. 必须包含从附件中提取的摘要 (20分，每个4分)
    score_abstracts = 0
    max_abs_score = 20
    abs_issues = []
    for p in ev_papers_sorted:
        pid = p["paper_id"]
        expected_abs = att_map.get(pid, "")
        if not expected_abs:
            abs_issues.append(f"论文 {pid} 的附件内容为空")
            continue
        # 检查摘要中至少80%的连续20个字符出现在review中（防止截断匹配）
        # 更鲁邦：取前100个字符
        key_part = expected_abs[:100]
        if key_part in review_text:
            score_abstracts += 4
        else:
            # 尝试更精确：按空格分隔的前20个连续词
            words = key_part.split()
            if len(words) >= 20:
                phrase = " ".join(words[:20])
                if phrase in review_text:
                    score_abstracts += 4
                else:
                    abs_issues.append(f"论文 {pid} 的摘要未在review中找到")
            else:
                if expected_abs[:50] in review_text:
                    score_abstracts += 4
                else:
                    abs_issues.append(f"论文 {pid} 的摘要未在review中找到")
    details.append({
        "item": "review.md包含从附件中提取的摘要",
        "score": score_abstracts,
        "max_score": max_abs_score,
        "passed": score_abstracts == max_abs_score,
        "reason": "正确" if score_abstracts == max_abs_score else "; ".join(abs_issues)
    })
    total_score += score_abstracts

    # 5. 检查 roadmap.mermaid 内容 (20分)
    # 5a. 必须包含 timeline关键字 (5分)
    roadmap_text = ""
    if roadmap_path.exists():
        roadmap_text = roadmap_path.read_text(encoding="utf-8")
    has_timeline = "timeline" in roadmap_text
    details.append({
        "item": "roadmap.mermaid包含'timeline'",
        "score": 5 if has_timeline else 0,
        "max_score": 5,
        "passed": has_timeline,
        "reason": "包含timeline" if has_timeline else "未包含timeline关键字"
    })
    total_score += 5 if has_timeline else 0

    # 5b. 检查年份和标题 (15分，每个论文3分)
    score_roadmap_entries = 0
    max_roadmap_entries = 15
    entry_issues = []
    for p in ev_papers_sorted:
        year_str = str(p["year"])
        title_short = p["title"]  # 完整标题可能太长，检查是否包含
        # Mermaid timeline条目格式: "year : Title" 或 "year : Title (note)"
        pattern = re.compile(r'^\s*' + re.escape(year_str) + r'\s*:\s*.*' + re.escape(p["title"][:30]), re.IGNORECASE | re.MULTILINE)
        # 更灵活：检查行是否包含年份和标题的一部分
        found = False
        for line in roadmap_text.split('\n'):
            line = line.strip()
            if line.startswith(year_str + ":") or line.startswith(year_str + " :"):
                if p["title"][:20] in line:
                    found = True
                    break
        if found:
            score_roadmap_entries += 3
        else:
            entry_issues.append(f"路线图中缺失论文 {p['paper_id']} 的条目")
    details.append({
        "item": "roadmap.mermaid包含所有论文的时间节点",
        "score": score_roadmap_entries,
        "max_score": max_roadmap_entries,
        "passed": score_roadmap_entries == max_roadmap_entries,
        "reason": "正确" if score_roadmap_entries == max_roadmap_entries else "; ".join(entry_issues)
    })
    total_score += score_roadmap_entries

    # 汇总
    result = {
        "total_score": min(total_score, 100),
        "details": details
    }
    # 写入评分文件
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
