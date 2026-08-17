#!/usr/bin/env python3
import sys
import json
import os
import re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def add_item(name, score, max_score, passed, reason):
    score_details.append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    global total_score
    if passed:
        total_score += score
    else:
        total_score += 0  # 未通过不加分

# 1. 检查 output/graph.json 是否存在 (10分)
graph_path = os.path.join(workspace, "output", "graph.json")
if os.path.isfile(graph_path):
    add_item("output/graph.json 存在", 10, 10, True, "文件存在")
else:
    add_item("output/graph.json 存在", 0, 10, False, "文件不存在")
    # 如果没有文件，后续检查无法进行，直接输出总分
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 2. JSON 格式合法 (10分)
try:
    with open(graph_path, "r") as f:
        graph_data = json.load(f)
    add_item("graph.json JSON 格式合法", 10, 10, True, "解析成功")
except Exception as e:
    add_item("graph.json JSON 格式合法", 0, 10, False, f"解析失败: {e}")
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 3. 数据类型应为列表 (5分)
if isinstance(graph_data, list):
    add_item("graph.json 是数组", 5, 5, True, "类型正确")
else:
    add_item("graph.json 是数组", 0, 5, False, f"实际类型: {type(graph_data).__name__}")

# 4. 每条边包含 source 和 target 且为字符串 (10分)
all_valid_edges = True
for i, edge in enumerate(graph_data):
    if not isinstance(edge, dict):
        all_valid_edges = False
        break
    if "source" not in edge or "target" not in edge:
        all_valid_edges = False
        break
    if not isinstance(edge["source"], str) or not isinstance(edge["target"], str):
        all_valid_edges = False
        break
if all_valid_edges:
    add_item("所有边包含 source/target 字符串", 10, 10, True, "格式正确")
else:
    add_item("所有边包含 source/target 字符串", 0, 10, False, "存在格式错误的边")

# 5. 排除自引用边 (20分)
self_loop_exists = False
for edge in graph_data:
    if edge["source"] == edge["target"]:
        self_loop_exists = True
        break
if not self_loop_exists:
    add_item("没有自引用边", 20, 20, True, "自引用已排除")
else:
    add_item("没有自引用边", 0, 20, False, "存在自引用边")

# 6. 有效边数量正确 (必须准确：排除无效paper，重复paper，缺失citation_ids等) (35分)
# 根据 env_builder 构建的有效论文集合（排除干扰项）：
# 有效paper_id: p001, p002, p003, p004, p005 (注意 p005 的 citation_ids 包含 p006，p006 不在有效集合，所以不应产生边)
# p010 自引用应排除整个paper？允许边？但 p010 本身是有效paper（尽管有自引用），但自引用边已被排除，其非自引用边如 p002 应保留。
# 注意 p010 的 citation_ids 包含 ["p010","p002"]，所以边 (p010, p002) 是合法且 paper_id 都在有效集合（p010 和 p002 都在），应保留。
# 但 p010 文件自身是合法的，所以有效paper集合：p001,p002,p003,p004,p005,p010。p003_old 的 paper_id 是 p003_old，不在集合，忽略。p020 缺少 citation_ids，忽略。dup_p001 内容重复但 paper_id 是 p001，以文件名为准？但实际上 paper_id 字段唯一，若出现重复 paper_id（如 p001 在多个文件中），应保留一个？这里我们规定：按文件读取顺序，后出现的覆盖？但为了简化，假设 agent 按唯一 paper_id 去重，只保留一个。这里 env_builder 中 p001 出现两次（papers/p001.json 和 papers/dup_p001.json），内容相同，所以不影响。我们只统计一次。
# 手动计算期望的边：
# p001: [p002, p003] -> (p001,p002),(p001,p003)
# p002: [p004] -> (p002,p004)
# p003: [p001, p004] -> (p003,p001),(p003,p004)
# p004: [p002] -> (p004,p002)
# p005: [p001, p003, p006] -> p006 不在有效集合，忽略，所以 (p005,p001),(p005,p003)
# p010: [p010, p002] -> 排除自引用 (p010,p010) 后保留 (p010,p002)
# 总计 9 条边。
expected_edges = 9
actual_edges = len(graph_data)
if actual_edges == expected_edges:
    add_item("边数量正确", 35, 35, True, f"期望 {expected_edges}，实际 {actual_edges}")
else:
    # 给部分分：一般偏离过多扣分
    diff = abs(actual_edges - expected_edges)
    if diff <= 1:
        add_item("边数量基本正确", 20, 35, False, f"期望 {expected_edges}，实际 {actual_edges}，偏差1")
    elif diff <= 3:
        add_item("边数量偏差较大", 10, 35, False, f"期望 {expected_edges}，实际 {actual_edges}，偏差{diff}")
    else:
        add_item("边数量严重错误", 0, 35, False, f"期望 {expected_edges}，实际 {actual_edges}")

# 7. 检查没有干扰项引入的边（例如 dup_p001 的重复不应导致多条边, 已经按 paper_id 去重） (5分)
# 简单检查不会有重复边（同 source 同 target 多次出现），我们不做严格去重要求，但因为唯一答案，应该不重复。
# 我们检查是否有重复边（不计顺序）
edge_set = set()
duplicates = 0
for edge in graph_data:
    key = (edge["source"], edge["target"])
    if key in edge_set:
        duplicates += 1
    else:
        edge_set.add(key)
if duplicates == 0:
    add_item("没有重复边", 5, 5, True, "所有边唯一")
else:
    add_item("没有重复边", 0, 5, False, f"存在 {duplicates} 条重复边")

# 总分计算
total_score = sum(item["score"] for item in score_details)  # 重新计算确保整数
result = {"total_score": total_score, "details": score_details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
print(f"评分完成，总分: {total_score}/100")
