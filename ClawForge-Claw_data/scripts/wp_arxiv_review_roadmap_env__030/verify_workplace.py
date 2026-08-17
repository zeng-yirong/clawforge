import sys
import os
import json
import re

def check_review(workspace: str) -> tuple:
    """
    验证 reviews/review.md
    期望内容：包含一个按年份升序排列的论文列表，每行格式为 "- YYYY: [paper_id] title"
    有效论文（efficient_vision, 2019-2023, 去重后）共5篇：
    v1:2019, v2:2020, v3:2021, v4:2022, v5:2023
    """
    path = os.path.join(workspace, "reviews", "review.md")
    if not os.path.isfile(path):
        return 0, "文件 reviews/review.md 不存在", 0
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 用正则提取所有行 - YYYY: [id] title
    pattern = r"^- (\d{4}): \[([^\]]+)\] (.+)$"
    matches = re.findall(pattern, content, re.MULTILINE)
    if not matches:
        return 0, "未找到符合格式的论文条目", 0

    # 提取年份和paper_id
    records = [(int(y), pid, title.strip()) for y, pid, title in matches]

    # 检查是否按年份升序
    years = [r[0] for r in records]
    if years != sorted(years):
        return 0, "论文未按年份升序排列", 0

    # 检查论文ID是否为我们期望的5篇（允许重复条目？agent应该去重，但这里只检查唯一性）
    expected_ids = ["v1", "v2", "v3", "v4", "v5"]
    found_ids = [r[1] for r in records]
    # 去重
    unique_ids = list(dict.fromkeys(found_ids))  # 保持顺序
    if unique_ids != expected_ids:
        return 0, f"论文ID列表不匹配，期望 {expected_ids}，实际 {unique_ids}", 0

    # 检查年份对应正确（v1-2019, v2-2020, ...）
    expected_year_map = {"v1": 2019, "v2": 2020, "v3": 2021, "v4": 2022, "v5": 2023}
    for pid, year in zip(unique_ids, years[:len(unique_ids)]):
        if year != expected_year_map[pid]:
            return 0, f"{pid} 年份错误：期望 {expected_year_map[pid]}，实际 {year}", 0

    # 检查标题是否包含关键字符（可选，但加强验证）
    # 我们信任 agent 使用了正确的标题，但可以检查 v1 是否有 "EfficientNet"
    # 不强制精确匹配，以免过于严格
    return 1, "reviews/review.md 内容完全正确", 30

def check_roadmap(workspace: str) -> tuple:
    """
    验证 roadmaps/timeline.mmd
    期望：Mermaid时间线图，节点按年份从左到右排列，节点标签包含 paper_id 和标题前20字符
    """
    path = os.path.join(workspace, "roadmaps", "timeline.mmd")
    if not os.path.isfile(path):
        return 0, "文件 roadmaps/timeline.mmd 不存在", 0
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 期望节点格式：节点ID[标签] 或 节点ID(["标签"])
    # 简单验证：检查是否包含每个 paper_id 作为节点
    expected_ids = ["v1", "v2", "v3", "v4", "v5"]
    for pid in expected_ids:
        if pid not in content:
            return 0, f"未找到论文 {pid} 的节点", 0

    # 检查是否有箭头连接（>= 4 条）
    arrow_count = content.count("-->")
    if arrow_count < 4:
        return 0, f"箭头数量不足，期望至少4条，实际 {arrow_count}", 0

    # 可进一步检查年份顺序（节点出现顺序），但这里简单通过
    return 1, "roadmaps/timeline.mmd 基本结构合理", 20

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查（10分）
    dirs_ok = True
    required_dirs = ["reviews", "roadmaps"]
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_ok = False
            details.append({"item": f"目录 {d} 存在", "score": 0, "max_score": 5, "passed": False, "reason": f"缺少目录 {d}"})
        else:
            details.append({"item": f"目录 {d} 存在", "score": 5, "max_score": 5, "passed": True, "reason": "存在"})
    if not dirs_ok:
        # 如果目录不存在，直接返回
        details.append({"item": "总体结构", "score": 0, "max_score": 10, "passed": False, "reason": "缺少关键目录"})
        # 但仍然继续检查文件，但可能报错
        total_score = sum(d["score"] for d in details)
        write_score(total_score, details)
        return

    # 2. review 检查（30分）
    passed_review, reason_review, score_review = check_review(workspace)
    details.append({"item": "reviews/review.md 内容", "score": score_review, "max_score": 30, "passed": passed_review == 1, "reason": reason_review})
    total_score += score_review

    # 3. roadmap 检查（20分）
    passed_roadmap, reason_roadmap, score_roadmap = check_roadmap(workspace)
    details.append({"item": "roadmaps/timeline.mmd 内容", "score": score_roadmap, "max_score": 20, "passed": passed_roadmap == 1, "reason": reason_roadmap})
    total_score += score_roadmap

    # 4. 额外检查：是否引入了不该有的文件（比如 cache 中的旧数据或附件，但 agent 可能复制了附件，我们不扣分）
    # 我们只关心是否有多余的、明显错误的文件（如 agent 生成了 .json 结果等）
    # 加分项：如果 agent 没有将无关文件放入 reviews 或 roadmaps，可加10分
    extra_pass = True
    for fname in os.listdir(os.path.join(workspace, "reviews")):
        if fname not in ["review.md", ".gitkeep"]:
            extra_pass = False
            break
    for fname in os.listdir(os.path.join(workspace, "roadmaps")):
        if fname not in ["timeline.mmd", ".gitkeep"]:
            extra_pass = False
            break
    if extra_pass:
        details.append({"item": "产物目录干净，无多余文件", "score": 10, "max_score": 10, "passed": True, "reason": "只有期望的文件"})
        total_score += 10
    else:
        details.append({"item": "产物目录干净，无多余文件", "score": 0, "max_score": 10, "passed": False, "reason": "存在未预期的文件"})

    # 5. 综合检查：是否所有期望的 paper_id 都出现在至少一个产物中
    # 已经在 review 和 roadmap 中检查过，这里不再重复

    # 6. 额外加分：检查 review 中是否提到了摘要关键词（非强制，但可以给附加分）
    # 我们设计为可选加分，但为了简化，不实现

    # 确保总分不超过100
    total_score = min(total_score, 100)

    write_score(total_score, details)

def write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
