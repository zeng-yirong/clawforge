import sys
import os
import json
import csv
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

details = []
total_score = 0

def add_detail(item, score, max_score, passed, reason):
    global total_score
    details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    total_score += score

# 1. 检查 ops 目录是否存在 (10分)
ops_dir = os.path.join(workspace, "ops")
if os.path.isdir(ops_dir):
    add_detail("ops directory exists", 10, 10, True, "ops directory found")
else:
    add_detail("ops directory exists", 0, 10, False, "ops directory missing")
    # 如果目录不存在，后续文件检查无意义，但仍继续以给出完整反馈
    # 但为避免后续异常，先返回？不，继续但文件检查会失败

# 2. 检查 diff_record.json 是否存在且合法 JSON (10分)
json_path = os.path.join(ops_dir, "diff_record.json")
if os.path.isfile(json_path):
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        add_detail("diff_record.json valid JSON", 10, 10, True, "File exists and is valid JSON")
    except (json.JSONDecodeError, ValueError) as e:
        add_detail("diff_record.json valid JSON", 0, 10, False, f"Invalid JSON: {e}")
        data = None
else:
    add_detail("diff_record.json exists", 0, 10, False, "diff_record.json not found")
    data = None

# 3. 构建预期结果（基于 env_builder 铺出的数据）
# 从原始 CSV 读取数据并计算
csv_path = os.path.join(workspace, "data/experiments/experiment_results.csv")
expected_diff = {}  # key: group_id (str), value: dict of changed metrics
if os.path.isfile(csv_path):
    rows_by_batch = {"batch_A": {}, "batch_B": {}}
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch = row["batch_id"].strip()
            group = row["group_id"].strip()
            # 跳过缺失值的行
            if not row["accuracy"] or not row["latency_ms"] or not row["cost_usd"]:
                continue
            acc = float(row["accuracy"])
            lat = float(row["latency_ms"])
            cost = float(row["cost_usd"])
            if batch in rows_by_batch:
                # 如果 group 已存在（重复行），取第一条（因为重复行完全一样）
                if group not in rows_by_batch[batch]:
                    rows_by_batch[batch][group] = (acc, lat, cost)

    # 计算共同 group
    common_groups = set(rows_by_batch["batch_A"].keys()) & set(rows_by_batch["batch_B"].keys())
    for g in sorted(common_groups, key=int):
        acc_a, lat_a, cost_a = rows_by_batch["batch_A"][g]
        acc_b, lat_b, cost_b = rows_by_batch["batch_B"][g]
        diff = {}
        acc_diff = round(acc_b - acc_a, 4)
        lat_diff = round(lat_b - lat_a, 4)
        cost_diff = round(cost_b - cost_a, 4)
        if abs(acc_diff) > 0.05:
            diff["accuracy_diff"] = acc_diff
        if abs(lat_diff) > 10:
            diff["latency_ms_diff"] = lat_diff
        if abs(cost_diff) > 0.1:
            diff["cost_usd_diff"] = cost_diff
        if diff:
            expected_diff[g] = diff
    # 注意：group1: acc_diff=0.07, lat=-5, cost=0.05 -> 只记录 accuracy
    # group2: acc=-0.01, lat=-11, cost=0.05 -> 只记录 latency
    # group3: acc=0.06, lat=-9, cost=0.15 -> accuracy + cost
    # group4,5 无变化
    # 所以预期：{"1": {"accuracy_diff": 0.07}, "2": {"latency_ms_diff": -11.0}, "3": {"accuracy_diff": 0.06, "cost_usd_diff": 0.15}}
else:
    add_detail("CSV source file exists", 0, 0, False, "Cannot read CSV for expected calculation")

# 4. 验证结果 (60分)
# 4.1 group_id 集合一致性 (20分)
if data is not None and expected_diff:
    actual_groups = set(str(k) for k in data.keys())
    expected_groups = set(expected_diff.keys())
    if actual_groups == expected_groups:
        add_detail("Group ID set matches", 20, 20, True, f"Groups present: {actual_groups}")
    else:
        missing = expected_groups - actual_groups
        extra = actual_groups - expected_groups
        msg = f"Groups mismatch. Missing: {missing}, Extra: {extra}"
        add_detail("Group ID set matches", 0, 20, False, msg)

    # 4.2 每个 group 的指标值逐项检查 (40分, 每个指标5分, 共三个group*? 实际group1 1个指标, group2 1个, group3 2个, 共4个指标)
    # 为简化权重，我们给每个 group 中的每个 expected 指标 10 分，最多 40 分 (group1 1个, group2 1个, group3 2个)
    # 但如果 agent 缺少指标或多出指标都扣分
    metric_points = 0
    max_metric_points = 0
    for g, exp_dict in expected_diff.items():
        if not data.get(g):
            # 完全缺失
            add_detail(f"Group {g} present", 0, 10*len(exp_dict), False, f"Group {g} missing from result")
            max_metric_points += 10*len(exp_dict)
            continue
        actual_dict = data[g]
        for metric, expected_val in exp_dict.items():
            max_metric_points += 10
            if metric not in actual_dict:
                add_detail(f"Group {g} {metric}", 0, 10, False, f"Missing metric {metric}")
            else:
                actual_val = float(actual_dict[metric])
                if math.isclose(actual_val, expected_val, rel_tol=1e-4, abs_tol=1e-4):
                    metric_points += 10
                    add_detail(f"Group {g} {metric}", 10, 10, True, f"Expected {expected_val}, got {actual_val}")
                else:
                    add_detail(f"Group {g} {metric}", 0, 10, False, f"Expected {expected_val}, got {actual_val}")
        # 检查是否有多余的指标（agent 添加了不该有的）
        extra_metrics = [m for m in actual_dict if m not in exp_dict and m in ("accuracy_diff","latency_ms_diff","cost_usd_diff")]
        for em in extra_metrics:
            # 额外指标每个扣5分（从总可能中扣，但避免负分，这里直接扣5分）
            metric_points -= 5
            add_detail(f"Group {g} extra metric {em}", -5, 0, False, f"Unexpected metric {em} present")
    # 确保不超最低0分
    metric_points = max(0, metric_points)
    # 我们已通过 add_detail 记录了每个子项，但总分还没有汇总？我们直接在之后汇总
    # 注意 add_detail 中累计了 total_score，所以上述加点直接反映到 total_score。
    # 我们将最后的 metric_points 视为已经通过上面 add_detail 累计了分数，所以不用再重复加。
    # 但为了清晰，我们使用 add_detail 时已经加了分数，所以下面 total_score 已经包含了。
else:
    # 如果 data 为 None，直接扣完30分
    add_detail("Result data available for verification", 0, 60, False, "No valid result data to compare")

# 如果之前缺失目录或文件，已经扣过分，总分会反映。

# 确保总分在0-100
total_score = min(100, max(0, total_score))
# 写入结果
result = {
    "total_score": total_score,
    "details": details
}
output_path = os.path.join(workspace, "workplace_score.json")
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)

# 简单打印
print(f"Total score: {total_score}/100")
