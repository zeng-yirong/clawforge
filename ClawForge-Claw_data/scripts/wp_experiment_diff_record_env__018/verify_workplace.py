import sys
import json
import csv
import os
import pathlib
from statistics import mean

def load_csv_data(workspace, filename):
    path = os.path.join(workspace, filename)
    if not os.path.isfile(path):
        return None
    rows = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 确保必要字段存在
            required = ['batch_id', 'group_id', 'accuracy', 'latency_ms', 'cost_usd']
            if all(k in row for k in required):
                rows.append(row)
    return rows

def validate_and_score(workspace):
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (5 分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops directory found"})
        total_score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops directory missing"})

    # 2. 检查 diff_record.json 是否存在且合法 (15 分)
    diff_path = os.path.join(workspace, "ops/diff_record.json")
    if not os.path.isfile(diff_path):
        details.append({"item": "diff_record.json exists", "score": 0, "max_score": 15, "passed": False, "reason": "file not found"})
        total_score += 0
        # 后续无法进行，返回当前分数
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    try:
        with open(diff_path) as f:
            diff_data = json.load(f)
    except (json.JSONDecodeError, ValueError):
        details.append({"item": "diff_record.json is valid JSON", "score": 0, "max_score": 15, "passed": False, "reason": "invalid JSON"})
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    if not isinstance(diff_data, dict) or "diffs" not in diff_data:
        details.append({"item": "diff_record.json structure", "score": 0, "max_score": 15, "passed": False, "reason": "missing 'diffs' key or not a dict"})
        total_score += 0
    else:
        details.append({"item": "diff_record.json is valid JSON and has 'diffs' key", "score": 15, "max_score": 15, "passed": True, "reason": "valid structure"})
        total_score += 15

    # 3. 加载 CSV 主文件并计算预期答案 (占大分 80)
    csv_data = load_csv_data(workspace, "data/experiments/experiment_results.csv")
    if csv_data is None:
        details.append({"item": "CSV file found", "score": 0, "max_score": 5, "passed": False, "reason": "main CSV not found"})
        total_score += 0
    elif len(csv_data) == 0:
        details.append({"item": "CSV has data", "score": 0, "max_score": 5, "passed": False, "reason": "CSV empty"})
        total_score += 0
    else:
        details.append({"item": "CSV file found and has rows", "score": 5, "max_score": 5, "passed": True, "reason": "CSV loadable"})
        total_score += 5

        # 数据清洗：只保留 batch_id 为 batch_001 或 batch_002，且 accuracy 在 [0,1] 内，latency_ms > 0，cost_usd >=0
        clean_rows = []
        for row in csv_data:
            try:
                bid = row['batch_id']
                gid = row['group_id']
                acc = float(row['accuracy'])
                lat = float(row['latency_ms'])
                cost = float(row['cost_usd'])
            except (ValueError, KeyError):
                continue
            if bid not in ('batch_001', 'batch_002'):
                continue
            if not (0.0 <= acc <= 1.0):
                continue
            if lat <= 0:
                continue
            if cost < 0:
                continue
            clean_rows.append({
                'batch_id': bid,
                'group_id': gid,
                'accuracy': acc,
                'latency_ms': lat,
                'cost_usd': cost
            })

        # 按 batch_id 和 group_id 分组计算均值
        from collections import defaultdict
        batch_groups = defaultdict(list)
        for row in clean_rows:
            key = (row['batch_id'], row['group_id'])
            batch_groups[key].append(row)

        # 计算每个 (batch, group) 的均值
        agg = {}
        for (bid, gid), rows in batch_groups.items():
            agg[(bid, gid)] = {
                'accuracy': mean(r['accuracy'] for r in rows),
                'latency_ms': mean(r['latency_ms'] for r in rows),
                'cost_usd': mean(r['cost_usd'] for r in rows)
            }

        # 计算差值：batch_002 - batch_001
        groups = sorted(set(g for (b, g) in agg.keys()))
        expected_diffs = []
        for gid in groups:
            key1 = ('batch_001', gid)
            key2 = ('batch_002', gid)
            if key1 not in agg or key2 not in agg:
                continue  # 缺数据则跳过
            v1 = agg[key1]
            v2 = agg[key2]
            expected_diffs.append({
                "group_id": gid,
                "accuracy_diff": round(v2['accuracy'] - v1['accuracy'], 4),
                "latency_diff": round(v2['latency_ms'] - v1['latency_ms'], 2),
                "cost_diff": round(v2['cost_usd'] - v1['cost_usd'], 4)
            })

        # 4. 比对预期与实际 (80 分, 根据准确度分配)
        if 'diffs' not in diff_data:
            diff_list = []
        else:
            diff_list = diff_data['diffs']
            if not isinstance(diff_list, list):
                diff_list = []

        # 排序以便比对
        actual_sorted = sorted(diff_list, key=lambda x: x.get('group_id', ''))
        expected_sorted = sorted(expected_diffs, key=lambda x: x['group_id'])

        # 检查组数
        if len(actual_sorted) != len(expected_sorted):
            details.append({"item": "Number of groups in diff", "score": 0, "max_score": 10, "passed": False, "reason": f"expected {len(expected_sorted)} groups, got {len(actual_sorted)}"})
            total_score += 0
        else:
            details.append({"item": "Number of groups in diff", "score": 10, "max_score": 10, "passed": True, "reason": "group count matches"})
            total_score += 10

        # 逐个字段比对（70 分）
        field_score = 70
        field_max = 70
        per_group_score = field_max / (len(expected_sorted) if expected_sorted else 1)
        correct_count = 0
        for i, exp in enumerate(expected_sorted):
            if i >= len(actual_sorted):
                break
            act = actual_sorted[i]
            group_ok = True
            for key in ['group_id', 'accuracy_diff', 'latency_diff', 'cost_diff']:
                exp_val = exp[key]
                act_val = act.get(key)
                # 允许浮点数微小误差 0.001
                if isinstance(exp_val, float) and isinstance(act_val, (int, float)):
                    if abs(exp_val - float(act_val)) > 1e-4:
                        group_ok = False
                        break
                else:
                    if exp_val != act_val:
                        group_ok = False
                        break
            if group_ok:
                correct_count += 1

        score_from_groups = round((correct_count / len(expected_sorted)) * field_max) if expected_sorted else 0
        total_score += score_from_groups
        details.append({"item": "Diff values accuracy", "score": score_from_groups, "max_score": field_max,
                        "passed": (correct_count == len(expected_sorted)),
                        "reason": f"correct groups: {correct_count}/{len(expected_sorted)}"})

    # 最终总分
    final_score = min(total_score, 100)
    result = {"total_score": final_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {final_score}/100 written to workplace_score.json")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    validate_and_score(workspace)
