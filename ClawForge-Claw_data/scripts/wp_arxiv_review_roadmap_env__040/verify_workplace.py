import sys
import os
import json
import re

def load_papers(workspace):
    """从工作区加载 papers.json，返回 (correct_list, message)"""
    papers_path = os.path.join(workspace, "data", "papers", "papers.json")
    if not os.path.isfile(papers_path):
        return None, "data/papers/papers.json 不存在"
    with open(papers_path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return None, "data/papers/papers.json 不是合法 JSON"
    if "papers" not in data:
        return None, "data/papers/papers.json 缺少 papers 字段"
    # 筛选 direction='efficient_vision' 且 abstract 非空（非空字符串即可）
    candidates = [p for p in data["papers"] if p.get("direction") == "efficient_vision" and p.get("abstract", "").strip()]
    # 按 year 升序，同年按 paper_id 字母序
    candidates.sort(key=lambda p: (p["year"], p["paper_id"]))
    # 提取 paper_id 列表作为正确答案
    correct_ids = [p["paper_id"] for p in candidates]
    return correct_ids, ""

def parse_review(workspace):
    """从 review.md 中提取 paper_id 列表，返回 (ids, error)"""
    path = os.path.join(workspace, "reviews", "review.md")
    if not os.path.isfile(path):
        return None, "reviews/review.md 不存在"
    with open(path, "r") as f:
        content = f.read()
    # 尝试解析表格：寻找包含 | 的行，第二列是 paper_id（假设表头第一列可能是序号或空，第二列是 Paper ID）
    lines = content.splitlines()
    ids = []
    for line in lines:
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            # 跳过表头（包含 'Paper ID' 或 'ID' 或 'paper_id'）
            if any(kw in line.lower() for kw in ["paper id", "paper_id", "id"]):
                continue
            if len(cells) >= 2:
                # 第二列应该是 paper_id
                candidate = cells[1]
                # 检查是否匹配 ev\d+ 模式
                if re.fullmatch(r"ev\d+", candidate):
                    ids.append(candidate)
    if not ids:
        return None, "review.md 中未找到任何 evXXX 格式的 paper_id（请确保表格第二列为 paper_id）"
    return ids, ""

def parse_roadmap(workspace):
    """从 roadmap.mmd 中提取 paper_id 列表，返回 (ids, error)"""
    path = os.path.join(workspace, "reviews", "roadmap.mmd")
    if not os.path.isfile(path):
        return None, "reviews/roadmap.mmd 不存在"
    with open(path, "r") as f:
        content = f.read()
    # 匹配形如 ev001[....] 的节点定义
    ids = re.findall(r"\b(ev\d+)\[", content)
    return ids, ""

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 目录结构 (10分)
    reviews_dir = os.path.join(workspace, "reviews")
    if os.path.isdir(reviews_dir):
        details.append({"item": "reviews 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到 reviews/ 目录"})
        total_score += 10
    else:
        details.append({"item": "reviews 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reviews/ 目录"})

    # 2. 加载正确列表
    correct_ids, err = load_papers(workspace)
    if err:
        details.append({"item": "加载正确答案", "score": 0, "max_score": 10, "passed": False, "reason": err})
        # 无法继续，写入结果并退出
        _write_score(details, total_score, workspace)
        return
    details.append({"item": "加载正确答案", "score": 10, "max_score": 10, "passed": True, "reason": f"正确论文共 {len(correct_ids)} 篇: {', '.join(correct_ids)}"})
    total_score += 10

    # 3. review.md 存在且合法 (15分)
    review_ids, err = parse_review(workspace)
    if err:
        details.append({"item": "review.md 格式与内容", "score": 0, "max_score": 15, "passed": False, "reason": err})
    else:
        if review_ids == correct_ids:
            details.append({"item": "review.md 格式与内容", "score": 15, "max_score": 15, "passed": True, "reason": "提取的 paper_id 与正确答案完全一致"})
            total_score += 15
        else:
            # 部分匹配：按正确个数给分
            common = set(review_ids) & set(correct_ids)
            if len(common) == len(correct_ids) and set(review_ids) == set(correct_ids):
                # 顺序错误
                details.append({"item": "review.md 格式与内容", "score": 10, "max_score": 15, "passed": False, "reason": f"包含全部正确论文但顺序不对: 期望 {correct_ids}, 得到 {review_ids}"})
                total_score += 10
            else:
                miss = set(correct_ids) - set(review_ids)
                extra = set(review_ids) - set(correct_ids)
                reason = f"缺少 {len(miss)} 篇: {', '.join(miss)} ; 多出 {len(extra)} 篇: {', '.join(extra)}"
                details.append({"item": "review.md 格式与内容", "score": 0, "max_score": 15, "passed": False, "reason": reason})

    # 4. roadmap.mmd 存在且合法 (15分)
    roadmap_ids, err = parse_roadmap(workspace)
    if err:
        details.append({"item": "roadmap.mmd 格式与内容", "score": 0, "max_score": 15, "passed": False, "reason": err})
    else:
        # 同样比较
        if roadmap_ids == correct_ids:
            details.append({"item": "roadmap.mmd 格式与内容", "score": 15, "max_score": 15, "passed": True, "reason": "提取的 paper_id 与正确答案完全一致"})
            total_score += 15
        else:
            common = set(roadmap_ids) & set(correct_ids)
            if len(common) == len(correct_ids) and set(roadmap_ids) == set(correct_ids):
                details.append({"item": "roadmap.mmd 格式与内容", "score": 10, "max_score": 15, "passed": False, "reason": f"包含全部正确论文但顺序不对: 期望 {correct_ids}, 得到 {roadmap_ids}"})
                total_score += 10
            else:
                miss = set(correct_ids) - set(roadmap_ids)
                extra = set(roadmap_ids) - set(correct_ids)
                reason = f"缺少 {len(miss)} 篇: {', '.join(miss)} ; 多出 {len(extra)} 篇: {', '.join(extra)}"
                details.append({"item": "roadmap.mmd 格式与内容", "score": 0, "max_score": 15, "passed": False, "reason": reason})

    # 5. 一致性检查：review 与 roadmap 列表是否一致 (10分)
    if review_ids is not None and roadmap_ids is not None:
        if review_ids == roadmap_ids:
            details.append({"item": "review 与 roadmap 列表一致性", "score": 10, "max_score": 10, "passed": True, "reason": "两个文件包含相同 paper_id 列表"})
            total_score += 10
        else:
            details.append({"item": "review 与 roadmap 列表一致性", "score": 0, "max_score": 10, "passed": False, "reason": f"review: {review_ids}, roadmap: {roadmap_ids}"})
    else:
        details.append({"item": "review 与 roadmap 列表一致性", "score": 0, "max_score": 10, "passed": False, "reason": "无法比较（至少一个文件解析失败）"})

    # 6. 额外加分项：review.md 中是否包含表格表头 (5分) —— 可选，但作为细粒度
    # 但为了方便，我们直接认为前面已经涵盖了，这里不再加

    # 总分100，我们分了10+10+15+15+10=60，还缺40分？我们重新调整权重：
    # 目录10, 答案加载10, review内容30, roadmap内容30, 一致性20 = 100
    # 修改上面：review 和 roadmap 分别给30分，一致性20分
    # 但为了不重写，我们简单把总分归一化到100：当前最大60，我们按比例放大？不行，应该重新分配权重。
    # 重新来：在输出前调整 details 中的 max_score 和 score 比例。为了简单，我们保持现有逻辑，然后最后总分乘以100/60？不，这样不准确。
    # 最好重新设计权重。直接修改上面代码吧，但为了节省时间，我们在此处重新计算：将上述所有项的最大值设为：目录10, 答案10, review30, roadmap30, 一致性20 = 100。
    # 修改细节：review和roadmap的max_score改为30，一致性改为20。同时调整得分比例。
    # 但我们已经计算了，需要重新写。由于这是最终输出，我们在此重写一遍，确保权重正确。
    # 重写下面的 main 逻辑，以正确权重输出。为了避免混乱，我在这里完整重写 verify 脚本。

def _write_score(details, total_score, workspace):
    """写入分数文件"""
    result = {"total_score": total_score, "details": details}
    path = os.path.join(workspace, "workplace_score.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    # 重新整理权重版本
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 目录结构 (10分)
    reviews_dir = os.path.join(workspace, "reviews")
    if os.path.isdir(reviews_dir):
        details.append({"item": "reviews 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到 reviews/ 目录"})
        total_score += 10
    else:
        details.append({"item": "reviews 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reviews/ 目录"})

    # 2. 加载正确答案 (10分)
    correct_ids, err = load_papers(workspace)
    if err:
        details.append({"item": "加载正确答案", "score": 0, "max_score": 10, "passed": False, "reason": err})
        _write_score(details, total_score, workspace)
        sys.exit(0)
    details.append({"item": "加载正确答案", "score": 10, "max_score": 10, "passed": True, "reason": f"正确论文共 {len(correct_ids)} 篇: {', '.join(correct_ids)}"})
    total_score += 10

    # 3. review.md (30分)
    review_ids, err = parse_review(workspace)
    if err:
        details.append({"item": "review.md 内容正确", "score": 0, "max_score": 30, "passed": False, "reason": err})
    else:
        if review_ids == correct_ids:
            details.append({"item": "review.md 内容正确", "score": 30, "max_score": 30, "passed": True, "reason": "提取的 paper_id 与正确答案完全一致（含顺序）"})
            total_score += 30
        else:
            common = set(review_ids) & set(correct_ids)
            if len(common) == len(correct_ids) and set(review_ids) == set(correct_ids):
                details.append({"item": "review.md 内容正确", "score": 20, "max_score": 30, "passed": False, "reason": f"包含全部正确论文但顺序不对: 期望 {correct_ids}, 得到 {review_ids}"})
                total_score += 20
            else:
                miss = set(correct_ids) - set(review_ids)
                extra = set(review_ids) - set(correct_ids)
                reason = f"缺少 {len(miss)} 篇: {', '.join(miss)} ; 多出 {len(extra)} 篇: {', '.join(extra)}"
                details.append({"item": "review.md 内容正确", "score": 0, "max_score": 30, "passed": False, "reason": reason})

    # 4. roadmap.mmd (30分)
    roadmap_ids, err = parse_roadmap(workspace)
    if err:
        details.append({"item": "roadmap.mmd 内容正确", "score": 0, "max_score": 30, "passed": False, "reason": err})
    else:
        if roadmap_ids == correct_ids:
            details.append({"item": "roadmap.mmd 内容正确", "score": 30, "max_score": 30, "passed": True, "reason": "提取的 paper_id 与正确答案完全一致（含顺序）"})
            total_score += 30
        else:
            common = set(roadmap_ids) & set(correct_ids)
            if len(common) == len(correct_ids) and set(roadmap_ids) == set(correct_ids):
                details.append({"item": "roadmap.mmd 内容正确", "score": 20, "max_score": 30, "passed": False, "reason": f"包含全部正确论文但顺序不对: 期望 {correct_ids}, 得到 {roadmap_ids}"})
                total_score += 20
            else:
                miss = set(correct_ids) - set(roadmap_ids)
                extra = set(roadmap_ids) - set(correct_ids)
                reason = f"缺少 {len(miss)} 篇: {', '.join(miss)} ; 多出 {len(extra)} 篇: {', '.join(extra)}"
                details.append({"item": "roadmap.mmd 内容正确", "score": 0, "max_score": 30, "passed": False, "reason": reason})

    # 5. 一致性 (20分)
    if review_ids is not None and roadmap_ids is not None:
        if review_ids == roadmap_ids:
            details.append({"item": "review 与 roadmap 列表一致", "score": 20, "max_score": 20, "passed": True, "reason": "两个文件包含相同 paper_id 列表（含顺序）"})
            total_score += 20
        else:
            details.append({"item": "review 与 roadmap 列表一致", "score": 0, "max_score": 20, "passed": False, "reason": f"review: {review_ids}, roadmap: {roadmap_ids}"})
    else:
        details.append({"item": "review 与 roadmap 列表一致", "score": 0, "max_score": 20, "passed": False, "reason": "无法比较（至少一个文件解析失败）"})

    # 总分已经计算，写入
    _write_score(details, total_score, workspace)
