import sys
import os
import json
import csv
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores = []
    total_score = 0

    # ---------- 检查目录结构 ----------
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        scores.append({"item": "ops 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops 目录已创建"})
        total_score += 10
    else:
        scores.append({"item": "ops 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ops 目录"})

    # ---------- 结果文件存在且合法 JSON ----------
    result_path = os.path.join(workspace, "ops", "batch_diff.json")
    if not os.path.isfile(result_path):
        scores.append({"item": "batch_diff.json 存在且合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续无法继续，直接输出
        write_score(scores, total_score, workspace)
        return

    try:
        with open(result_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        scores.append({"item": "batch_diff.json 存在且合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        write_score(scores, total_score, workspace)
        return

    scores.append({"item": "batch_diff.json 存在且合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且 JSON 合法"})
    total_score += 10

    # ---------- 字段结构 ----------
    if not isinstance(data, dict):
        scores.append({"item": "JSON 包含 diff_records 列表", "score": 0, "max_score": 20, "passed": False, "reason": "根对象不是字典"})
        write_score(scores, total_score, workspace)
        return

    records = data.get("diff_records")
    if not isinstance(records, list):
        scores.append({"item": "JSON 包含 diff_records 列表", "score": 0, "max_score": 20, "passed": False, "reason": "缺少 diff_records 键或不是列表"})
        write_score(scores, total_score, workspace)
        return

    # 检查每个记录字段
    required_fields = ["group_id", "accuracy_diff", "latency_diff", "cost_diff"]
    structure_ok = True
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            structure_ok = False
            reason = f"记录 {i} 不是字典"
            break
        for fld in required_fields:
            if fld not in rec:
                structure_ok = False
                reason = f"记录 {i} 缺少字段 {fld}"
                break
        if not structure_ok:
            break
    if structure_ok:
        scores.append({"item": "diff_records 结构正确", "score": 20, "max_score": 20, "passed": True, "reason": "所有记录包含必要字段"})
        total_score += 20
    else:
        scores.append({"item": "diff_records 结构正确", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # ---------- 数值计算准确性（40分） ----------
    # 从原始 CSV 重构 ground truth
    csv_path = os.path.join(workspace, "data", "experiments", "experiment_results.csv")
    if not os.path.isfile(csv_path):
        scores.append({"item": "数值计算准确（40分）", "score": 0, "max_score": 40, "passed": False, "reason": "原始 CSV 丢失"})
        write_score(scores, total_score, workspace)
        return

    # 读取有效数据（跳过脏行）
    alpha = {}
    beta = {}
    try:
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bid = row.get("batch_id", "").strip()
                gid = row.get("group_id", "").strip()
                if not bid or not gid:
                    continue
                try:
                    acc = float(row["accuracy"])
                    lat = float(row["latency_ms"])
                    cost = float(row["cost_usd"])
                except (ValueError, TypeError, KeyError):
                    continue
                if bid == "batch_alpha":
                    alpha[gid] = (acc, lat, cost)
                elif bid == "batch_beta":
                    beta[gid] = (acc, lat, cost)
                # 忽略其他批次
    except Exception as e:
        scores.append({"item": "数值计算准确（40分）", "score": 0, "max_score": 40, "passed": False, "reason": f"读取 CSV 失败: {e}"})
        write_score(scores, total_score, workspace)
        return

    # 计算期望差异 (beta - alpha)
    expected = {}
    for gid in alpha:
        if gid in beta:
            acc_diff = round(beta[gid][0] - alpha[gid][0], 2)
            lat_diff = round(beta[gid][1] - alpha[gid][1], 2)
            cost_diff = round(beta[gid][2] - alpha[gid][2], 2)
            expected[gid] = (acc_diff, lat_diff, cost_diff)

    # 检查 agent 输出
    correct_count = 0
    total_checks = len(expected) * 3  # 每个组3个指标
    for rec in records:
        gid = rec.get("group_id", "")
        if gid not in expected:
            continue
        exp_acc, exp_lat, exp_cost = expected[gid]
        # 误差容忍 0.005（保留两位相当于 ±0.005）
        if abs(rec.get("accuracy_diff", 1e9) - exp_acc) < 0.005:
            correct_count += 1
        if abs(rec.get("latency_diff", 1e9) - exp_lat) < 0.005:
            correct_count += 1
        if abs(rec.get("cost_diff", 1e9) - exp_cost) < 0.005:
            correct_count += 1

    # 同时检查是否漏掉了组
    missing_groups = set(expected.keys()) - {r.get("group_id") for r in records}
    extra_groups = {r.get("group_id") for r in records} - set(expected.keys())

    calc_score = round(40 * correct_count / total_checks) if total_checks > 0 else 0
    detail_reason = f"正确指标 {correct_count}/{total_checks}，缺失组 {missing_groups}，多余组 {extra_groups}"

    if correct_count == total_checks and not missing_groups and not extra_groups:
        passed = True
        calc_score = 40
    else:
        passed = False

    scores.append({"item": "数值计算准确（40分）", "score": calc_score, "max_score": 40, "passed": passed, "reason": detail_reason})
    total_score += calc_score

    # ---------- 多余记录扣分已在上述计算中体现，不再单独扣分 ----------

    # ---------- 所有组都被覆盖？已在上面体现 ----------
    # 额外：检查是否包含来自脏数据的组（broken/extra）
    dirty_groups = {"broken", "extra"}
    for rec in records:
        if rec.get("group_id") in dirty_groups:
            # 扣分（实际上上面已经因为额外组导致 extra_groups 非空，已经影响了 passed 和 calc_score）
            pass

    # 最终总分
    total_score = sum(it["score"] for it in scores)
    write_score(scores, total_score, workspace)


def write_score(scores, total_score, workspace):
    result = {
        "total_score": total_score,
        "details": scores
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
