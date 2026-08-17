import sys
import os
import json
import csv
import math
from pathlib import Path

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
ws = Path(workspace)

def parse_experiment_csv(csv_path):
    """解析CSV，跳过空行和以#开头的行，返回 { (batch_id, group_id): accuracy } 字典"""
    records = {}
    if not csv_path.exists():
        return records
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        header_parsed = False
        batch_idx = group_idx = acc_idx = -1
        for row in reader:
            # 跳过完全空行
            if not row:
                continue
            # 跳过以#开头的行（注释）
            if row[0].startswith("#"):
                continue
            if not header_parsed:
                # 标准表头：batch_id, group_id, accuracy, latency_ms, cost_usd
                try:
                    batch_idx = row.index("batch_id")
                    group_idx = row.index("group_id")
                    acc_idx = row.index("accuracy")
                except ValueError:
                    # 如果不是标准表头，尝试找类似的
                    continue
                header_parsed = True
                continue
            if len(row) <= max(batch_idx, group_idx, acc_idx):
                continue
            batch_id = row[batch_idx].strip()
            group_id = row[group_idx].strip()
            try:
                accuracy = float(row[acc_idx])
            except ValueError:
                continue
            records[(batch_id, group_id)] = accuracy
    return records

def compute_expected_result(records):
    """根据所有记录计算应该输出的结果：同时出现在两个batch中的组，计算batch_002 - batch_001，返回最大差值的组和差值，以及该组是否唯一"""
    batch_ids = set(b for (b,g) in records.keys())
    # 找出共同组
    group_batches = {}
    for (b, g), acc in records.items():
        group_batches.setdefault(g, {})[b] = acc
    diffs = {}
    for g, batches in group_batches.items():
        if "batch_001" in batches and "batch_002" in batches:
            diffs[g] = batches["batch_002"] - batches["batch_001"]
    if not diffs:
        return None, None, False
    max_diff = max(diffs.values())
    max_groups = [g for g, d in diffs.items() if math.isclose(d, max_diff, rel_tol=1e-9)]
    # 确保唯一（题目设计应唯一）
    if len(max_groups) == 1:
        return max_groups[0], max_diff, True
    else:
        return max_groups[0], max_diff, False  # 非唯一，但仍返回第一个

detail = []

# 1. ops 目录是否存在 (5分)
ops_dir = ws / "ops"
detail.append({
    "item": "ops directory exists",
    "max_score": 5,
    "score": 5 if ops_dir.is_dir() else 0,
    "passed": ops_dir.is_dir(),
    "reason": "ops目录存在" if ops_dir.is_dir() else "ops目录不存在"
})

# 2. diff_result.json 是否存在 (5分)
result_file = ops_dir / "diff_result.json"
detail.append({
    "item": "diff_result.json exists",
    "max_score": 5,
    "score": 5 if result_file.is_file() else 0,
    "passed": result_file.is_file(),
    "reason": "文件存在" if result_file.is_file() else "文件不存在"
})

score = sum(d["score"] for d in detail)

if result_file.is_file():
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        detail.append({
            "item": "JSON is valid",
            "max_score": 10,
            "score": 10,
            "passed": True,
            "reason": "JSON解析成功"
        })
    except Exception as e:
        detail.append({
            "item": "JSON is valid",
            "max_score": 10,
            "score": 0,
            "passed": False,
            "reason": f"JSON解析失败: {e}"
        })
        data = None
else:
    data = None

if data is not None:
    # 3. 字段检查
    fields_ok = True
    field_reasons = []
    if not isinstance(data, dict):
        detail.append({"item": "Content is a JSON object", "max_score": 10, "score": 0, "passed": False, "reason": "输出不是字典"})
        fields_ok = False
    else:
        # 检查 group_id
        has_group = "group_id" in data
        has_change = "accuracy_change" in data
        if has_group and has_change:
            detail.append({
                "item": "Contains group_id and accuracy_change",
                "max_score": 20,
                "score": 20,
                "passed": True,
                "reason": "字段齐全"
            })
        else:
            detail.append({
                "item": "Contains group_id and accuracy_change",
                "max_score": 20,
                "score": 0,
                "passed": False,
                "reason": f"缺少字段: group_id={has_group}, accuracy_change={has_change}"
            })
            fields_ok = False
        # 额外字段检查（扣分项，但这里作为加分项的一部分）
        extra_keys = set(data.keys()) - {"group_id", "accuracy_change"}
        if extra_keys:
            detail.append({
                "item": "No extra fields",
                "max_score": 10,
                "score": 0,
                "passed": False,
                "reason": f"存在多余字段: {extra_keys}"
            })
        else:
            detail.append({
                "item": "No extra fields",
                "max_score": 10,
                "score": 10,
                "passed": True,
                "reason": "无多余字段"
            })
        
        if fields_ok:
            # 4. 动态验证正确性
            csv_path = ws / "data/experiments/experiment_results.csv"
            records = parse_experiment_csv(csv_path)
            expected_group, expected_change, unique = compute_expected_result(records)
            if expected_group is None:
                detail.append({
                    "item": "Computed correct answer (no valid groups)",
                    "max_score": 50,
                    "score": 0,
                    "passed": False,
                    "reason": "从CSV中无法找到同时出现在两个batch的组"
                })
            else:
                # 检查 group_id
                group_match = str(data["group_id"]) == expected_group
                change_match = math.isclose(float(data["accuracy_change"]), expected_change, rel_tol=1e-9)
                if group_match and change_match:
                    detail.append({
                        "item": "Group ID correct",
                        "max_score": 20,
                        "score": 20,
                        "passed": True,
                        "reason": f"group_id = {expected_group}"
                    })
                    detail.append({
                        "item": "Accuracy change correct",
                        "max_score": 30,
                        "score": 30,
                        "passed": True,
                        "reason": f"accuracy_change = {expected_change}"
                    })
                else:
                    # 分别扣分
                    if not group_match:
                        detail.append({
                            "item": "Group ID correct",
                            "max_score": 20,
                            "score": 0,
                            "passed": False,
                            "reason": f"期望 {expected_group}, 得到 {data.get('group_id')}"
                        })
                    else:
                        detail.append({
                            "item": "Group ID correct",
                            "max_score": 20,
                            "score": 20,
                            "passed": True,
                            "reason": f"group_id = {expected_group}"
                        })
                    if not change_match:
                        detail.append({
                            "item": "Accuracy change correct",
                            "max_score": 30,
                            "score": 0,
                            "passed": False,
                            "reason": f"期望 {expected_change}, 得到 {data.get('accuracy_change')}"
                        })
                    else:
                        detail.append({
                            "item": "Accuracy change correct",
                            "max_score": 30,
                            "score": 30,
                            "passed": True,
                            "reason": f"accuracy_change = {expected_change}"
                        })
    # 如果data不是字典，额外字段检查已经跳过，直接给0
else:
    detail.append({"item": "Content is a JSON object", "max_score": 10, "score": 0, "passed": False, "reason": "无法读取数据"})

total_score = sum(d["score"] for d in detail)
# 确保总分100
total_score = min(total_score, 100)

result = {
    "total_score": total_score,
    "details": detail
}

with open(ws / "workplace_score.json", "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"得分: {total_score}/100")
sys.exit(0 if total_score == 100 else 1)
