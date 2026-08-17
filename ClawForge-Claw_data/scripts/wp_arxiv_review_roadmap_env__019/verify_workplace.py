import os
import sys
import json
import re

def load_papers(workspace):
    with open(os.path.join(workspace, "papers/papers.json")) as f:
        data = json.load(f)
    return data["papers"]

def get_target_paper_ids(papers):
    target = set()
    for p in papers:
        if p["direction"] == "tool_augmented_reasoning":
            target.add(p["paper_id"])
    return target

def parse_review_md(text):
    lines = text.split('\n')
    paper_ids = []
    for line in lines:
        if '|' in line:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            for cell in cells:
                match = re.search(r'(paper_\d+)', cell)
                if match:
                    paper_ids.append(match.group(1))
                    break
    return paper_ids

def parse_roadmap_mermaid(text):
    nodes = set()
    for match in re.finditer(r'\["([^"]+)"\]', text):
        nodes.add(match.group(1))
    return nodes

def verify(workspace):
    details = []
    total_score = 0

    # ==== 目录与文件存在性 (15分) ====
    outputs_dir = os.path.join(workspace, "outputs")
    if os.path.isdir(outputs_dir):
        details.append({"item": "outputs directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "OK"})
        total_score += 5
    else:
        details.append({"item": "outputs directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing outputs dir"})

    review_path = os.path.join(outputs_dir, "review.md")
    if os.path.isfile(review_path):
        details.append({"item": "review.md exists", "score": 5, "max_score": 5, "passed": True, "reason": "OK"})
        total_score += 5
    else:
        details.append({"item": "review.md exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing review.md"})

    roadmap_path = os.path.join(outputs_dir, "roadmap.mermaid")
    if os.path.isfile(roadmap_path):
        details.append({"item": "roadmap.mermaid exists", "score": 5, "max_score": 5, "passed": True, "reason": "OK"})
        total_score += 5
    else:
        details.append({"item": "roadmap.mermaid exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing roadmap.mermaid"})

    # ==== 加载基准数据 ====
    papers = load_papers(workspace)
    target_ids = get_target_paper_ids(papers)  # 5个正确的ID
    id_year = {p["paper_id"]: p["year"] for p in papers}

    # ==== 检查 review.md 内容 (55分) ====
    if os.path.isfile(review_path):
        with open(review_path) as f:
            review_text = f.read()

        # 论文ID匹配 (30分)
        review_ids = parse_review_md(review_text)
        review_set = set(review_ids)
        missing = target_ids - review_set
        extra = review_set - target_ids
        if not missing and not extra:
            details.append({"item": "Review contains correct paper IDs", "score": 30, "max_score": 30, "passed": True, "reason": "All target IDs present, no extra"})
            total_score += 30
        else:
            reason = []
            if missing: reason.append(f"Missing: {missing}")
            if extra: reason.append(f"Extra: {extra}")
            details.append({"item": "Review contains correct paper IDs", "score": 0, "max_score": 30, "passed": False, "reason": "; ".join(reason)})

        # 年份排序 (15分)
        sorted_target = sorted(target_ids, key=lambda x: id_year[x])
        review_ordered = [pid for pid in review_ids if pid in target_ids]
        if review_ordered == sorted_target:
            details.append({"item": "Review papers sorted by year", "score": 15, "max_score": 15, "passed": True, "reason": "Order matches ascending year"})
            total_score += 15
        else:
            details.append({"item": "Review papers sorted by year", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected order {sorted_target}, got {review_ordered}"})

        # 表格列数检查 (10分)
        lines = review_text.split('\n')
        table_rows = [line for line in lines if '|' in line and line.strip().startswith('|')]
        data_rows = [line for line in table_rows if '---' not in line]
        col_counts = [len([c.strip() for c in line.split('|') if c.strip()]) for line in data_rows]
        if all(c >= 4 for c in col_counts):
            details.append({"item": "Review table has proper columns (>=4)", "score": 10, "max_score": 10, "passed": True, "reason": "All data rows have at least 4 columns"})
            total_score += 10
        else:
            details.append({"item": "Review table has proper columns (>=4)", "score": 0, "max_score": 10, "passed": False, "reason": f"Column counts: {col_counts}"})
    else:
        details.append({"item": "Review contains correct paper IDs", "score": 0, "max_score": 30, "passed": False, "reason": "review.md not found"})
        details.append({"item": "Review papers sorted by year", "score": 0, "max_score": 15, "passed": False, "reason": "review.md not found"})
        details.append({"item": "Review table has proper columns (>=4)", "score": 0, "max_score": 10, "passed": False, "reason": "review.md not found"})

    # ==== 检查 roadmap.mermaid 内容 (30分) ====
    if os.path.isfile(roadmap_path):
        with open(roadmap_path) as f:
            roadmap_text = f.read()
        roadmap_nodes = parse_roadmap_mermaid(roadmap_text)
        expected_labels = set()
        for pid in target_ids:
            expected_labels.add(f"{id_year[pid]} - {pid}")
        missing_nodes = expected_labels - roadmap_nodes
        extra_nodes = roadmap_nodes - expected_labels
        if not missing_nodes and not extra_nodes:
            details.append({"item": "Roadmap contains all target nodes", "score": 20, "max_score": 20, "passed": True, "reason": "All target nodes present, no extra"})
            total_score += 20
        else:
            reason = []
            if missing_nodes: reason.append(f"Missing: {missing_nodes}")
            if extra_nodes: reason.append(f"Extra: {extra_nodes}")
            details.append({"item": "Roadmap contains all target nodes", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(reason)})

        # 节点标签格式 (10分)
        format_ok = True
        for label in roadmap_nodes:
            if not re.match(r'^\d{4} - paper_\d+$', label):
                format_ok = False
                break
        if format_ok:
            details.append({"item": "Roadmap node label format correct", "score": 10, "max_score": 10, "passed": True, "reason": "All labels follow 'Year - ID' pattern"})
            total_score += 10
        else:
            details.append({"item": "Roadmap node label format correct", "score": 0, "max_score": 10, "passed": False, "reason": "Some labels do not match required pattern"})
    else:
        details.append({"item": "Roadmap contains all target nodes", "score": 0, "max_score": 20, "passed": False, "reason": "roadmap.mermaid not found"})
        details.append({"item": "Roadmap node label format correct", "score": 0, "max_score": 10, "passed": False, "reason": "roadmap.mermaid not found"})

    # ==== 写入结果 ====
    result = {"total_score": total_score, "details": details}
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
