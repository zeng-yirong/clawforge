import sys
import json
import os
import csv
import math
from decimal import Decimal, ROUND_HALF_UP

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops/diff_record.json 存在 (10分)
    diff_path = os.path.join(workspace, "ops", "diff_record.json")
    if os.path.isfile(diff_path):
        score_details.append({
            "item": "ops/diff_record.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"文件存在于 {diff_path}"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops/diff_record.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"文件不存在：{diff_path}"
        })
        # 如果文件不存在，后续无法检查，直接写结果返回
        write_score(score_details, total_score)
        return

    # 2. JSON 格式合法 (10分)
    try:
        with open(diff_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 解析有效",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件可正确解析为 JSON"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "JSON 解析有效",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败：{e}"
        })
        write_score(score_details, total_score)
        return

    # 3. 检查必需字段 (20分)  — 每个字段 4 分，共5个 = 20分
    required_fields = ["batch_a_id", "batch_b_id", "avg_accuracy_diff", "avg_latency_diff", "avg_cost_diff", "analyst"]
    field_scores = []
    for field in required_fields:
        if field in data:
            field_scores.append({"field": field, "present": True, "score": 4})
        else:
            field_scores.append({"field": field, "present": False, "score": 0})
    # 汇总字段分
    fields_score = sum([fs["score"] for fs in field_scores])
    # 记录每个字段的详细原因
    for fs in field_scores:
        reason = f"字段 '{fs['field']}' 存在" if fs["present"] else f"字段 '{fs['field']}' 缺失"
        score_details.append({
            "item": f"必需字段 {fs['field']}",
            "score": fs["score"],
            "max_score": 4,
            "passed": fs["present"],
            "reason": reason
        })
    total_score += fields_score

    # 4. batch_a_id 和 batch_b_id 正确 (10分)
    batch_a_correct = data.get("batch_a_id") == "batch_001"
    batch_b_correct = data.get("batch_b_id") == "batch_002"
    batch_id_score = 0
    if batch_a_correct:
        batch_id_score += 5
        score_details.append({
            "item": "batch_a_id 为 batch_001",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "匹配预期"
        })
    else:
        score_details.append({
            "item": "batch_a_id 为 batch_001",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"实际值: {data.get('batch_a_id')}"
        })
    if batch_b_correct:
        batch_id_score += 5
        score_details.append({
            "item": "batch_b_id 为 batch_002",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "匹配预期"
        })
    else:
        score_details.append({
            "item": "batch_b_id 为 batch_002",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"实际值: {data.get('batch_b_id')}"
        })
    total_score += batch_id_score

    # 5. 数值计算验证 (40分)  — 注意精度，使用 Decimal 避免浮点误差
    # 我们重新从 CSV 计算预期值
    csv_path = os.path.join(workspace, "data", "experiments", "experiment_results.csv")
    if not os.path.isfile(csv_path):
        # 如果环境 CSV 缺失，则无法对比，但 builder 正常时应该存在；这里给0分并说明
        num_score = 0
        score_details.append({
            "item": "avg_accuracy_diff 计算",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "无法读取 data/experiments/experiment_results.csv"
        })
        score_details.append({
            "item": "avg_latency_diff 计算",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "无法读取 CSV"
        })
        score_details.append({
            "item": "avg_cost_diff 计算",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "无法读取 CSV"
        })
    else:
        # 解析 CSV，只取 batch_001 / batch_002 的有效行
        batch_data = {"batch_001": [], "batch_002": []}
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bid = row.get("batch_id", "").strip()
                if bid not in batch_data:
                    continue
                try:
                    accuracy = float(row["accuracy"])
                    latency = float(row["latency_ms"])
                    cost = float(row["cost_usd"])
                except (ValueError, KeyError, TypeError):
                    continue  # 跳过脏数据
                batch_data[bid].append((accuracy, latency, cost))
        # 计算平均值
        def average(values):
            if not values:
                return None
            return sum(values) / len(values)

        expected = {}
        for bid in ["batch_001", "batch_002"]:
            records = batch_data[bid]
            if not records:
                expected[bid] = None
            else:
                accs = [r[0] for r in records]
                lats = [r[1] for r in records]
                costs = [r[2] for r in records]
                expected[bid] = (average(accs), average(lats), average(costs))

        if expected["batch_001"] and expected["batch_002"]:
            exp_acc_diff = expected["batch_001"][0] - expected["batch_002"][0]
            exp_lat_diff = expected["batch_001"][1] - expected["batch_002"][1]
            exp_cost_diff = expected["batch_001"][2] - expected["batch_002"][2]
        else:
            exp_acc_diff = exp_lat_diff = exp_cost_diff = None

        # 实际值
        act_acc_diff = data.get("avg_accuracy_diff")
        act_lat_diff = data.get("avg_latency_diff")
        act_cost_diff = data.get("avg_cost_diff")

        # 设置精度：保留4位小数
        def round4(x):
            return float(Decimal(str(x)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))

        # 检查每个指标（允许误差 0.0001）
        def check_diff(actual, expected, item_name, max_score):
            if actual is None or expected is None:
                return 0, f"缺少数值"
            act_rounded = round4(actual)
            exp_rounded = round4(expected)
            if act_rounded == exp_rounded:
                return max_score, f"正确: {act_rounded}"
            else:
                return 0, f"期望 {exp_rounded}, 实际 {act_rounded}"

        acc_score, acc_reason = check_diff(act_acc_diff, exp_acc_diff, "avg_accuracy_diff", 15)
        lat_score, lat_reason = check_diff(act_lat_diff, exp_lat_diff, "avg_latency_diff", 15)
        cost_score, cost_reason = check_diff(act_cost_diff, exp_cost_diff, "avg_cost_diff", 10)

        total_score += acc_score + lat_score + cost_score
        score_details.append({
            "item": "avg_accuracy_diff 计算",
            "score": acc_score,
            "max_score": 15,
            "passed": acc_score == 15,
            "reason": acc_reason
        })
        score_details.append({
            "item": "avg_latency_diff 计算",
            "score": lat_score,
            "max_score": 15,
            "passed": lat_score == 15,
            "reason": lat_reason
        })
        score_details.append({
            "item": "avg_cost_diff 计算",
            "score": cost_score,
            "max_score": 10,
            "passed": cost_score == 10,
            "reason": cost_reason
        })

    # 6. analyst 字段检查 (10分)
    act_analyst = data.get("analyst")
    if act_analyst == "Alice":
        score_details.append({
            "item": "analyst 字段值正确 (Alice)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "匹配预期"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "analyst 字段值正确 (Alice)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际值: {act_analyst}"
        })

    # 确保总分不超过100
    total_score = min(total_score, 100)
    write_score(score_details, total_score)

def write_score(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
