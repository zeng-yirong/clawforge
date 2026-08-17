import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    results = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops/ 目录是否存在 (10分)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        results.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "存在"})
        total_score += 10
    else:
        results.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # 2. 检查目标文件是否存在 (10分)
    target_file = ops_dir / "low_risk_credentials.json"
    if target_file.is_file():
        results.append({"item": "目标文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        results.append({"item": "目标文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续检查跳过，但结构保持
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f)
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        results.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可解析"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        results.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f)
        return

    # 4. 内容正确性 (70分)
    # 重新读取 vault.json 和 categories.json 计算期望结果
    try:
        with open(ws / "vault.json", "r", encoding="utf-8") as f:
            vault = json.load(f)
        with open(ws / "categories.json", "r", encoding="utf-8") as f:
            categories = json.load(f)
    except Exception as e:
        results.append({"item": "读取初始数据", "score": 0, "max_score": 70, "passed": False, "reason": f"无法读取初始文件: {e}"})
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f)
        return

    # 收集所有 low 优先级的 category_id
    low_priority_ids = set()
    for cat_id, cat_info in categories.items():
        if cat_info["priority"] == "low":
            low_priority_ids.add(cat_id)

    # 筛选凭据：category_id 在 low_priority_ids 中，且 category_id 在 categories 中存在（其实已经包含）
    expected_entries = []
    for cred in vault:
        if cred["category_id"] in low_priority_ids:
            expected_entries.append({
                "name": cred["name"],
                "username": cred["username"]
            })
    # 按 name 字典序排序
    expected_entries.sort(key=lambda x: x["name"])

    # 比对
    sub_score = 0
    # 4a. 长度匹配 (20分)
    if len(content) == len(expected_entries):
        results.append({"item": "记录数量一致", "score": 20, "max_score": 20, "passed": True, "reason": f"数量均为 {len(content)}"})
        sub_score += 20
    else:
        results.append({"item": "记录数量一致", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 {len(expected_entries)} 条，实际 {len(content)} 条"})

    # 4b. 每个元素包含 name 和 username (10分)
    all_have_fields = True
    for idx, entry in enumerate(content):
        if not isinstance(entry, dict) or "name" not in entry or "username" not in entry:
            all_have_fields = False
            break
    if all_have_fields:
        results.append({"item": "每个条目包含name和username", "score": 10, "max_score": 10, "passed": True, "reason": "字段齐全"})
        sub_score += 10
    else:
        results.append({"item": "每个条目包含name和username", "score": 0, "max_score": 10, "passed": False, "reason": "缺少必要字段"})

    # 4c. 排序正确 (10分)
    names = [e["name"] for e in content]
    if names == sorted(names):
        results.append({"item": "按name字典序排序", "score": 10, "max_score": 10, "passed": True, "reason": "排序正确"})
        sub_score += 10
    else:
        results.append({"item": "按name字典序排序", "score": 0, "max_score": 10, "passed": False, "reason": "排序错误"})

    # 4d. 值与预期完全匹配 (30分)
    # 使用集合比较，但顺序已检查，直接逐项比较
    match = True
    if len(content) != len(expected_entries):
        match = False
    else:
        for i in range(len(content)):
            if content[i] != expected_entries[i]:
                match = False
                break
    if match:
        results.append({"item": "值与预期完全一致", "score": 30, "max_score": 30, "passed": True, "reason": "所有条目匹配"})
        sub_score += 30
    else:
        results.append({"item": "值与预期完全一致", "score": 0, "max_score": 30, "passed": False, "reason": "存在差异"})

    total_score += sub_score

    # 写入评分结果
    with open(ws / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)

if __name__ == "__main__":
    main()
