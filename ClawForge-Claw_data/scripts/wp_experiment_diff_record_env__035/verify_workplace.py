import sys
import os
import json
import csv
import math
from pathlib import Path

def read_csv_safe(filepath):
    """忽略注释行、空行、格式错误行，返回列表字典"""
    rows = []
    with open(filepath, 'r', newline='') as f:
        reader = csv.DictReader(row for row in f if not row.startswith('#') and row.strip())
        for line_no, row in enumerate(reader, start=2):
            # 检查必要字段是否都存在
            if not all(k in row for k in ['batch_id','group_id','accuracy','latency_ms','cost_usd']):
                continue
            # 尝试转换数值，失败则跳过
            try:
                row['accuracy'] = float(row['accuracy'])
                row['latency_ms'] = float(row['latency_ms'])
                row['cost_usd'] = float(row['cost_usd'])
            except (ValueError, TypeError):
                continue
            rows.append(row)
    return rows

def build_expected_diff(rows):
    """从清洗后的rows中提取batch_A和batch_B，按group计算差值"""
    batch_a = {}
    batch_b = {}
    for r in rows:
        if r['batch_id'] == 'batch_A':
            batch_a[r['group_id']] = (r['accuracy'], r['latency_ms'], r['cost_usd'])
        elif r['batch_id'] == 'batch_B':
            batch_b[r['group_id']] = (r['accuracy'], r['latency_ms'], r['cost_usd'])
    # 取两个批次都出现的group
    common_groups = sorted(set(batch_a.keys()) & set(batch_b.keys()))
    diffs = []
    for g in common_groups:
        acc_a, lat_a, cost_a = batch_a[g]
        acc_b, lat_b, cost_b = batch_b[g]
        diffs.append({
            "group_id": g,
            "accuracy_diff": round(acc_b - acc_a, 10),
            "latency_ms_diff": round(lat_b - lat_a, 10),
            "cost_usd_diff": round(cost_b - cost_a, 10)
        })
    return {
        "batch_a": "batch_A",
        "batch_b": "batch_B",
        "diffs": diffs
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "ops", "diff_record.json")
    csv_path = os.path.join(workspace, "data", "experiments", "experiment_results.csv")

    details = []
    total = 0

    # 1. 检查产物目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found ops/"})
        total += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing ops/"})

    # 2. 检查产物文件是否存在
    if os.path.isfile(result_path):
        details.append({"item": "diff_record.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found"})
        total += 5
    else:
        details.append({"item": "diff_record.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing"})
        # 没有文件则后续无法验证，直接输出
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    # 3. 解析产物JSON
    try:
        with open(result_path, "r") as f:
            agent_result = json.load(f)
        details.append({"item": "valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "Parsed OK"})
        total += 5
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": f"Parse error: {str(e)}"})
        # 仍然输出得分
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    # 4. 检查必要字段
    required_keys = ["batch_a", "batch_b", "diffs"]
    missing = [k for k in required_keys if k not in agent_result]
    if not missing:
        details.append({"item": "top-level fields present", "score": 10, "max_score": 10, "passed": True, "reason": "Contains batch_a, batch_b, diffs"})
        total += 10
    else:
        details.append({"item": "top-level fields present", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing: {missing}"})
        # 无法继续比较，输出
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    # 5. 检查batch标识
    if agent_result["batch_a"] == "batch_A" and agent_result["batch_b"] == "batch_B":
        details.append({"item": "batch identifiers correct", "score": 10, "max_score": 10, "passed": True, "reason": "batch_A vs batch_B"})
        total += 10
    else:
        details.append({"item": "batch identifiers correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {agent_result['batch_a']} / {agent_result['batch_b']}"})

    # 6. 计算期望差异
    if not os.path.isfile(csv_path):
        details.append({"item": "diff accuracy", "score": 0, "max_score": 60, "passed": False, "reason": "Missing source CSV"})
        total += 0
    else:
        try:
            raw_rows = read_csv_safe(csv_path)
            expected = build_expected_diff(raw_rows)
            agent_diffs = agent_result.get("diffs", [])

            # 按group_id排序比较
            exp_by_group = {d["group_id"]: d for d in expected["diffs"]}
            agent_by_group = {d["group_id"]: d for d in agent_diffs}

            common_groups = set(exp_by_group.keys()) & set(agent_by_group.keys())
            extra_groups = set(agent_by_group.keys()) - set(exp_by_group.keys())
            missing_groups = set(exp_by_group.keys()) - set(agent_by_group.keys())

            group_score = 0
            max_group_score = 60  # 每个group 20分（共3个），额外扣分
            # 每个group检查三个差值
            for g in sorted(common_groups):
                exp = exp_by_group[g]
                act = agent_by_group[g]
                field_ok = True
                for field in ["accuracy_diff", "latency_ms_diff", "cost_usd_diff"]:
                    if field not in act:
                        field_ok = False
                        break
                    if not math.isclose(exp[field], act[field], rel_tol=1e-9, abs_tol=1e-9):
                        field_ok = False
                        break
                if field_ok:
                    group_score += 20
                    reason = f"group {g} all diffs match"
                else:
                    reason = f"group {g} mismatch (expected {exp}, got {act})"
                # 更新details汇总
                details.append({"item": f"group {g} diff", "score": 20 if field_ok else 0, "max_score": 20, "passed": field_ok, "reason": reason})
            # 处理额外group（扣分）
            for g in extra_groups:
                details.append({"item": f"unexpected group {g}", "score": 0, "max_score": 0, "passed": False, "reason": "Extra group not in expectation"})
                group_score -= 10  # 每个额外组扣10分
            # 处理缺失group（扣分）
            for g in missing_groups:
                details.append({"item": f"missing group {g}", "score": 0, "max_score": 0, "passed": False, "reason": "Required group absent"})
                group_score -= 10

            group_score = max(0, group_score)  # 不低于0
            total += group_score
        except Exception as e:
            details.append({"item": "diff calculation", "score": 0, "max_score": 60, "passed": False, "reason": f"Error: {str(e)}"})
            total += 0

    # 7. 写入最终得分
    total = min(100, total)  # 封顶100
    score = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score, f, indent=2)

if __name__ == "__main__":
    main()
