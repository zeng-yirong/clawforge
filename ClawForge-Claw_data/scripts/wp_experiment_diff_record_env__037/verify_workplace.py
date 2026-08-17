import sys
import json
import csv
import os
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
details = []
total_score = 0

def record(item, score, max_score, passed, reason):
    details.append({"item": item, "score": score, "max_score": max_score, "passed": passed, "reason": reason})
    return score

# 1. 检查关键目录和文件是否存在
# 1a ops/ 目录
ops_dir = os.path.join(workspace, "ops")
if os.path.isdir(ops_dir):
    total_score += record("ops/ 目录存在", 5, 5, True, "目录已创建")
else:
    total_score += record("ops/ 目录存在", 0, 5, False, "未找到 ops/ 目录")

# 1b diff_report.json 存在且可解析
report_path = os.path.join(ops_dir, "diff_report.json")
if not os.path.isfile(report_path):
    total_score += record("ops/diff_report.json 存在", 0, 10, False, "文件未找到")
    total_score += record("JSON 格式合法", 0, 5, False, "文件不存在")
    total_score += record("数据结构正确", 0, 10, False, "文件不存在")
    total_score += record("每组必填字段存在", 0, 20, False, "文件不存在")
    total_score += record("正确计算 accuracy_change", 0, 20, False, "文件不存在")
    total_score += record("正确计算 latency_change", 0, 15, False, "文件不存在")
    total_score += record("正确计算 cost_change", 0, 10, False, "文件不存在")
    total_score += record("排序正确（降幅从大到小）", 0, 5, False, "文件不存在")
else:
    total_score += record("ops/diff_report.json 存在", 10, 10, True, "文件存在")
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        total_score += record("JSON 格式合法", 5, 5, True, "解析成功")
    except (json.JSONDecodeError, Exception) as e:
        total_score += record("JSON 格式合法", 0, 5, False, f"JSON 解析失败: {e}")
        # 后续检查跳过
        total_score += record("数据结构正确", 0, 10, False, "JSON 不可用")
        total_score += record("每组必填字段存在", 0, 20, False, "JSON 不可用")
        total_score += record("正确计算 accuracy_change", 0, 20, False, "JSON 不可用")
        total_score += record("正确计算 latency_change", 0, 15, False, "JSON 不可用")
        total_score += record("正确计算 cost_change", 0, 10, False, "JSON 不可用")
        total_score += record("排序正确（降幅从大到小）", 0, 5, False, "JSON 不可用")
        # 写入分数后退出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        sys.exit(0)

    # 2. 解析 CSV 计算期望结果
    csv_path = os.path.join(workspace, "data/experiments/experiment_results.csv")
    try:
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        total_score += record("读取 experiment_results.csv", 0, 0, False, f"无法读取 CSV: {e}")
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        sys.exit(0)

    # 过滤有效行：只保留 batch_001 和 batch_002，且 accuracy/latency/cost 可转为 float
    def is_valid(row):
        try:
            float(row["accuracy"])
            float(row["latency_ms"])
            float(row["cost_usd"])
            return row["batch_id"] in ("batch_001", "batch_002")
        except (ValueError, KeyError):
            return False

    valid_rows = [row for row in rows if is_valid(row)]

    # 按 batch_id 和 group_id 分组
    batch_data = {}  # batch_id -> {group_id -> {accuracy, latency, cost}}
    for row in valid_rows:
        bid = row["batch_id"]
        gid = row["group_id"]
        acc = float(row["accuracy"])
        lat = float(row["latency_ms"])
        cost = float(row["cost_usd"])
        batch_data.setdefault(bid, {})[gid] = {"accuracy": acc, "latency": lat, "cost": cost}

    b1 = batch_data.get("batch_001", {})
    b2 = batch_data.get("batch_002", {})

    # 只取共同 group
    common_groups = set(b1.keys()) & set(b2.keys())
    expected_list = []
    for gid in common_groups:
        acc_change = b2[gid]["accuracy"] - b1[gid]["accuracy"]
        lat_change = b2[gid]["latency"] - b1[gid]["latency"]
        cost_change = b2[gid]["cost"] - b1[gid]["cost"]
        expected_list.append({
            "group_id": gid,
            "accuracy_change": round(acc_change, 4),
            "latency_change": round(lat_change, 4),
            "cost_change": round(cost_change, 4)
        })
    # 按 accuracy_change 降序（负值越大越前）
    expected_list.sort(key=lambda x: x["accuracy_change"])

    # 3. 验证 agent 输出
    # 3a 数据结构正确：必须是列表
    if not isinstance(data, list):
        total_score += record("数据结构正确", 0, 10, False, f"期望列表，得到 {type(data).__name__}")
        total_score += record("每组必填字段存在", 0, 20, False, "数据结构错误")
        total_score += record("正确计算 accuracy_change", 0, 20, False, "数据结构错误")
        total_score += record("正确计算 latency_change", 0, 15, False, "数据结构错误")
        total_score += record("正确计算 cost_change", 0, 10, False, "数据结构错误")
        total_score += record("排序正确（降幅从大到小）", 0, 5, False, "数据结构错误")
    else:
        total_score += record("数据结构正确", 10, 10, True, "是列表")
        # 3b 长度匹配
        if len(data) != len(expected_list):
            total_score += record("每组必填字段存在", 0, 20, False, f"组数不匹配: 期望 {len(expected_list)}，实际 {len(data)}")
            total_score += record("正确计算 accuracy_change", 0, 20, False, "组数不匹配")
            total_score += record("正确计算 latency_change", 0, 15, False, "组数不匹配")
            total_score += record("正确计算 cost_change", 0, 10, False, "组数不匹配")
            total_score += record("排序正确（降幅从大到小）", 0, 5, False, "组数不匹配")
        else:
            # 逐项检查字段存在
            fields_ok = True
            for i, actual in enumerate(data):
                if not isinstance(actual, dict):
                    fields_ok = False
                    break
                for key in ["group_id", "accuracy_change", "latency_change", "cost_change"]:
                    if key not in actual:
                        fields_ok = False
                        break
                if not fields_ok:
                    break
            if fields_ok:
                total_score += record("每组必填字段存在", 20, 20, True, "所有组都有 group_id, accuracy_change, latency_change, cost_change")
            else:
                total_score += record("每组必填字段存在", 0, 20, False, "某些组缺少必需字段")

            # 计算数值比较的权重
            acc_score_pen = 0
            lat_score_pen = 0
            cost_score_pen = 0
            sort_ok = True
            for i, (exp, act) in enumerate(zip(expected_list, data)):
                # 检查 group_id 顺序一致性（用于排序判定）
                if i > 0:
                    if act.get("group_id") != exp["group_id"]:
                        sort_ok = False
                # 数值比较 (允许浮点误差 1e-4)
                for key, max_err in [("accuracy_change", 1e-4), ("latency_change", 1e-4), ("cost_change", 1e-4)]:
                    exp_val = exp[key]
                    act_val = act.get(key)
                    if act_val is None or not isinstance(act_val, (int, float)):
                        if key == "accuracy_change": acc_score_pen = 1
                        elif key == "latency_change": lat_score_pen = 1
                        else: cost_score_pen = 1
                    elif abs(exp_val - act_val) > max_err:
                        if key == "accuracy_change": acc_score_pen = 1
                        elif key == "latency_change": lat_score_pen = 1
                        else: cost_score_pen = 1

            if acc_score_pen:
                total_score += record("正确计算 accuracy_change", 0, 20, False, "存在偏差或字段错误")
            else:
                total_score += record("正确计算 accuracy_change", 20, 20, True, "所有组的 accuracy_change 准确")

            if lat_score_pen:
                total_score += record("正确计算 latency_change", 0, 15, False, "存在偏差或字段错误")
            else:
                total_score += record("正确计算 latency_change", 15, 15, True, "所有组的 latency_change 准确")

            if cost_score_pen:
                total_score += record("正确计算 cost_change", 0, 10, False, "存在偏差或字段错误")
            else:
                total_score += record("正确计算 cost_change", 10, 10, True, "所有组的 cost_change 准确")

            if sort_ok and len(data) == len(expected_list):
                total_score += record("排序正确（降幅从大到小）", 5, 5, True, "列表顺序与预期一致")
            else:
                total_score += record("排序正确（降幅从大到小）", 0, 5, False, "组顺序错误")

# 写入最终分数
total_score = min(total_score, 100)
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": details}, f, indent=2)
