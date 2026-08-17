#!/usr/bin/env python3
import json
import os
import sys
import re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def check_dir(path):
    return os.path.isdir(os.path.join(workspace, path))

def check_file(path):
    return os.path.isfile(os.path.join(workspace, path))

def read_file(path):
    with open(os.path.join(workspace, path), "r", encoding="utf-8") as f:
        return f.read()

def parse_review(text):
    lines = text.splitlines()
    key_papers = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if "Key Papers" in stripped:
                in_section = True
            else:
                in_section = False
        elif in_section and stripped.startswith("- "):
            match = re.match(r"- (\w+): (.+)", stripped)
            if match:
                key_papers.append((match.group(1), match.group(2).strip()))
    return key_papers

def parse_roadmap(text):
    nodes = {}
    edges = []
    for line in text.splitlines():
        stripped = line.strip()
        # 节点：P001["title"] 或 P001['title']，兼容无引号
        m = re.match(r'(\w+)\[["\']?(.+?)["\']?\]', stripped)
        if m:
            nodes[m.group(1)] = m.group(2).strip()
        # 边：A --> B
        m = re.match(r'(\w+)\s*-->\s*(\w+)', stripped)
        if m:
            edges.append((m.group(1), m.group(2)))
    return nodes, edges

# 期望数据（与 env_builder 完全一致）
expected_papers = {
    "P001": "MobileNetV3",
    "P002": "EfficientNetV2",
    "P003": "ConvNeXt",
    "P004": "RepVGG",
    "P005": "EdgeNeXt"
}
expected_edges = {
    ("P002", "P001"),
    ("P003", "P002"),
    ("P004", "P001"),
    ("P004", "P003"),
    ("P005", "P004")
}

score_details = []
total_score = 0

# 1. 检查 ops 目录
if check_dir("ops"):
    score_details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录已创建"})
    total_score += 10
else:
    score_details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录不存在"})

# 2. 检查 review.md
if check_file("ops/review.md"):
    try:
        content = read_file("ops/review.md")
        if content.strip():
            score_details.append({"item": "review.md存在且非空", "score": 10, "max_score": 10, "passed": True, "reason": "review.md存在"})
            total_score += 10
        else:
            score_details.append({"item": "review.md存在但空", "score": 5, "max_score": 10, "passed": False, "reason": "文件为空"})
    except:
        score_details.append({"item": "review.md读取失败", "score": 0, "max_score": 10, "passed": False, "reason": "无法读取"})
else:
    score_details.append({"item": "review.md文件", "score": 0, "max_score": 10, "passed": False, "reason": "review.md不存在"})

# 3. 检查 roadmap.mmd
if check_file("ops/roadmap.mmd"):
    try:
        content = read_file("ops/roadmap.mmd")
        if content.strip():
            score_details.append({"item": "roadmap.mmd存在且非空", "score": 10, "max_score": 10, "passed": True, "reason": "roadmap.mmd存在"})
            total_score += 10
        else:
            score_details.append({"item": "roadmap.mmd存在但空", "score": 5, "max_score": 10, "passed": False, "reason": "文件为空"})
    except:
        score_details.append({"item": "roadmap.mmd读取失败", "score": 0, "max_score": 10, "passed": False, "reason": "无法读取"})
else:
    score_details.append({"item": "roadmap.mmd文件", "score": 0, "max_score": 10, "passed": False, "reason": "roadmap.mmd不存在"})

# 4. 解析 review 论文列表 (30分)
review_score = 0
review_max = 30
if check_file("ops/review.md"):
    review_text = read_file("ops/review.md")
    parsed = parse_review(review_text)
    parsed_dict = {pid: title for pid, title in parsed}
    issues = []
    # 检查期望论文
    for pid, title in expected_papers.items():
        if pid in parsed_dict:
            if parsed_dict[pid] == title:
                review_score += 5
            else:
                review_score += 2
                issues.append(f"{pid}标题错误(期望'{title}',得到'{parsed_dict[pid]}')")
        else:
            issues.append(f"{pid}缺失")
    # 额外论文扣分
    extra = [pid for pid in parsed_dict if pid not in expected_papers]
    if extra:
        review_score -= 5 * len(extra)
        issues.append(f"包含额外论文: {extra}")
    review_score = max(0, min(review_score, review_max))
    reason = "论文列表完全正确" if issues == [] else "; ".join(issues)
    score_details.append({"item": "review论文列表", "score": review_score, "max_score": review_max, "passed": review_score == review_max, "reason": reason})
    total_score += review_score
else:
    score_details.append({"item": "review论文列表", "score": 0, "max_score": review_max, "passed": False, "reason": "review.md不存在"})

# 5. 解析 roadmap (40分)
roadmap_score = 0
roadmap_max = 40
if check_file("ops/roadmap.mmd"):
    roadmap_text = read_file("ops/roadmap.mmd")
    nodes, edges = parse_roadmap(roadmap_text)
    
    # 5a. 节点 (20分)
    node_score = 0
    node_max = 20
    node_issues = []
    for pid, title in expected_papers.items():
        if pid in nodes:
            if nodes[pid] == title:
                node_score += 4
            else:
                node_score += 1
                node_issues.append(f"{pid}标题错误(期望'{title}',得到'{nodes[pid]}')")
        else:
            node_issues.append(f"{pid}节点缺失")
    extra_nodes = [p for p in nodes if p not in expected_papers]
    if extra_nodes:
        node_score -= 2 * len(extra_nodes)
        node_issues.append(f"额外节点: {extra_nodes}")
    node_score = max(0, min(node_score, node_max))
    reason = "节点完全正确" if node_issues == [] else "; ".join(node_issues)
    score_details.append({"item": "roadmap节点", "score": node_score, "max_score": node_max, "passed": node_score == node_max, "reason": reason})
    roadmap_score += node_score
    total_score += node_score
    
    # 5b. 边 (20分)
    edge_score = 0
    edge_max = 20
    edge_issues = []
    edge_set = set(edges)
    for e in expected_edges:
        if e in edge_set:
            edge_score += 4
        else:
            edge_issues.append(f"缺失边 {e[0]}->{e[1]}")
    extra_edges = edge_set - expected_edges
    if extra_edges:
        edge_score -= 2 * len(extra_edges)
        edge_issues.append(f"额外边: {extra_edges}")
    edge_score = max(0, min(edge_score, edge_max))
    reason = "边完全正确" if edge_issues == [] else "; ".join(edge_issues)
    score_details.append({"item": "roadmap边", "score": edge_score, "max_score": edge_max, "passed": edge_score == edge_max, "reason": reason})
    roadmap_score += edge_score
    total_score += edge_score
else:
    score_details.append({"item": "roadmap解析", "score": 0, "max_score": roadmap_max, "passed": False, "reason": "roadmap.mmd不存在"})

# 写出结果
result = {
    "total_score": total_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
