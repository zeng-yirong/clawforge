import sys
import os
import json
import re
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # ------------------------------------------------------------
    # 1. 检查产物文件是否存在 (10 分)
    # ------------------------------------------------------------
    review_path = os.path.join(workspace, "review.md")
    roadmap_path = os.path.join(workspace, "roadmap.mmd")

    exists_review = os.path.isfile(review_path)
    exists_roadmap = os.path.isfile(roadmap_path)
    if exists_review:
        details.append({"item": "review.md exists", "score": 5, "max_score": 5, "passed": True, "reason": "File present."})
        total_score += 5
    else:
        details.append({"item": "review.md exists", "score": 0, "max_score": 5, "passed": False, "reason": "review.md not found."})

    if exists_roadmap:
        details.append({"item": "roadmap.mmd exists", "score": 5, "max_score": 5, "passed": True, "reason": "File present."})
        total_score += 5
    else:
        details.append({"item": "roadmap.mmd exists", "score": 0, "max_score": 5, "passed": False, "reason": "roadmap.mmd not found."})

    if not (exists_review and exists_roadmap):
        # 没有核心文件，直接结束
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ------------------------------------------------------------
    # 2. 读取数据定义真实答案
    # ------------------------------------------------------------
    papers_path = os.path.join(workspace, "data/papers/papers.json")
    if not os.path.isfile(papers_path):
        details.append({"item": "Load papers.json", "score": 0, "max_score": 10, "passed": False, "reason": "papers.json not found."})
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    with open(papers_path, "r", encoding="utf-8") as f:
        papers_data = json.load(f)
    papers_list = papers_data.get("papers", [])

    # 真实目标：direction == "tool_augmented_reasoning" 且 2019 <= year <= 2024
    true_target_ids = set()
    for p in papers_list:
        direction = p.get("direction")
        year = p.get("year")
        if direction == "tool_augmented_reasoning" and isinstance(year, int) and 2019 <= year <= 2024:
            true_target_ids.add(p["paper_id"])

    # 合法格式检查：review 中的论文 ID 必须以 ### 开头
    with open(review_path, "r", encoding="utf-8") as f:
        review_content = f.read()

    # 提取所有 ### 后面的单词 (假设为论文ID)
    review_ids = set(re.findall(r'^###\s+(\S+)', review_content, re.MULTILINE))
    # 兼容可能出现的 ### paper_id (title) 形式
    if not review_ids:
        # 尝试更宽松的匹配： ### paper_id 或者 ### paper_id[title]
        review_ids = set(re.findall(r'^###\s+(\w+)', review_content, re.MULTILINE))

    # roadmap.mmd 中的节点提取 (假定节点格式为 id[label] 或 id("label"))
    with open(roadmap_path, "r", encoding="utf-8") as f:
        roadmap_content = f.read()
    roadmap_ids = set(re.findall(r'(\w+)\[', roadmap_content))
    roadmap_ids |= set(re.findall(r'(\w+)\(', roadmap_content))  # 备用格式

    # ------------------------------------------------------------
    # 3. 评分项
    # ------------------------------------------------------------
    # 3.1 内容格式: review 至少有 6 个 ### 行 (目标 6 篇) (5 分)
    num_review_sections = len(review_ids)
    format_ok = num_review_sections >= len(true_target_ids)
    if format_ok:
        details.append({"item": "review section count >= 6", "score": 5, "max_score": 5, "passed": True, "reason": f"Found {num_review_sections} sections."})
        total_score += 5
    else:
        details.append({"item": "review section count >= 6", "score": 0, "max_score": 5, "passed": False, "reason": f"Only {num_review_sections} sections, expected at least {len(true_target_ids)}."})

    # 3.2 review 包含所有真实目标 ID (20 分, 每个目标 约 3.33 分)
    missing_target = true_target_ids - review_ids
    extra_ids_review = review_ids - true_target_ids
    for tid in true_target_ids:
        if tid in review_ids:
            details.append({"item": f"review contains target {tid}", "score": 3, "max_score": 3, "passed": True, "reason": "Present."})
            total_score += 3
        else:
            details.append({"item": f"review contains target {tid}", "score": 0, "max_score": 3, "passed": False, "reason": f"Missing in review."})

    # 补足剩余分数 (20分已经分配6*3=18, 加2分作为额外奖励如果全部正确)
    if len(missing_target) == 0:
        details.append({"item": "review has no missing target", "score": 2, "max_score": 2, "passed": True, "reason": "All targets present."})
        total_score += 2
    else:
        details.append({"item": "review has no missing target", "score": 0, "max_score": 2, "passed": False, "reason": f"Missing: {missing_target}"})

    # 3.3 review 没有引入干扰 ID (15 分, 每出现一个非目标扣 3 分)
    penalty_review = 0
    for eid in extra_ids_review:
        # 允许额外的 section 如果它只是标题没有 id？但我们已经提取了 id，额外的 id 就是干扰
        penalty_review += 3
    review_extra_score = max(0, 15 - penalty_review)
    details.append({"item": "review no extra (distractor) IDs", "score": review_extra_score, "max_score": 15, "passed": penalty_review == 0, "reason": f"Extra IDs: {extra_ids_review if extra_ids_review else 'None'}"})
    total_score += review_extra_score

    # 3.4 roadmap 包含所有真实目标 ID (20 分, 每个 约 3.33)
    missing_roadmap = true_target_ids - roadmap_ids
    extra_roadmap = roadmap_ids - true_target_ids
    for tid in true_target_ids:
        if tid in roadmap_ids:
            details.append({"item": f"roadmap contains target {tid}", "score": 3, "max_score": 3, "passed": True, "reason": "Present."})
            total_score += 3
        else:
            details.append({"item": f"roadmap contains target {tid}", "score": 0, "max_score": 3, "passed": False, "reason": f"Missing in roadmap."})

    if len(missing_roadmap) == 0:
        details.append({"item": "roadmap no missing target", "score": 2, "max_score": 2, "passed": True, "reason": "All targets present."})
        total_score += 2
    else:
        details.append({"item": "roadmap no missing target", "score": 0, "max_score": 2, "passed": False, "reason": f"Missing: {missing_roadmap}"})

    # 3.5 roadmap 没有干扰 ID (15 分)
    penalty_roadmap = 0
    for eid in extra_roadmap:
        penalty_roadmap += 3
    roadmap_extra_score = max(0, 15 - penalty_roadmap)
    details.append({"item": "roadmap no extra (distractor) IDs", "score": roadmap_extra_score, "max_score": 15, "passed": penalty_roadmap == 0, "reason": f"Extra IDs: {extra_roadmap if extra_roadmap else 'None'}"})
    total_score += roadmap_extra_score

    # 3.6 额外检查 review 中是否提到了年份 (非强制，但可以给1分奖励？暂不)
    # 这里不检查，因为已经足够区分。

    # 确保总分不超过100
    total_score = min(total_score, 100)
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
