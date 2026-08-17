#!/usr/bin/env python3
import sys
import os
import json
import csv
from decimal import Decimal, ROUND_HALF_UP

def round_dec(value, places=3):
    # 将值转为 Decimal 然后四舍五入
    if isinstance(value, Decimal):
        return value.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    return Decimal(str(value)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    details = []

    # 1. 检查 ops 目录是否存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops 目录已创建"})
        total_score += 5
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops 目录缺失"})

    # 2. 检查 diff_record.json 文件是否存在 (10分)
    result_path = os.path.join(ops_dir, "diff_record.json")
    if os.path.isfile(result_path):
        details.append({"item": "diff_record.json 文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在于预期路径"})
        total_score += 10
    else:
        details.append({"item": "diff_record.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": f"未找到 {result_path}"})
        # 后续检查无法进行，直接结束
        final_score = total_score
        output = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 3. 解析 JSON 合法性 (15分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 15, "max_score": 15, "passed": True, "reason": "正确解析 JSON"})
        total_score += 15
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败: {e}"})
        final_score = total_score
        output = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 4. 验证数据结构 (20分)
    # 期望结构：一个列表，每个元素是字典，包含 group_id, accuracy_diff, latency_diff, cost_diff
    if not isinstance(data, list):
        details.append({"item": "数据结构为列表", "score": 0, "max_score": 20, "passed": False, "reason": "顶层不是列表"})
        final_score = total_score
        output = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return
    expected_groups = ["alpha", "beta", "gamma"]
    if len(data) != 3:
        details.append({"item": "数据结构包含 3 个场景", "score": 0, "max_score": 20, "passed": False, "reason": f"列表长度 {len(data)}，预期 3"})
        final_score = total_score
        output = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return
    # 检查每个元素是否包含必要字段
    required_fields = ["group_id", "accuracy_diff", "latency_diff", "cost_diff"]
    struct_ok = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            struct_ok = False
            break
        for field in required_fields:
            if field not in item:
                struct_ok = False
                break
        if not struct_ok:
            break
    if struct_ok:
        details.append({"item": "数据结构符合要求（列表+字典含必要字段）", "score": 20, "max_score": 20, "passed": True, "reason": "字段齐全"})
        total_score += 20
    else:
        details.append({"item": "数据结构符合要求", "score": 0, "max_score": 20, "passed": False, "reason": "缺少必要字段或格式错误"})
        final_score = total_score
        output = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 5. 数值正确性 (50分)
    # 从 CSV 中读取有效数据，计算预期差异
    csv_path = os.path.join(workspace, "data/experiments/experiment_results.csv")
    if not os.path.isfile(csv_path):
        details.append({"item": "数值计算", "score": 0, "max_score": 50, "passed": False, "reason": "CSV 文件缺失，无法验证"})
        final_score = total_score
        output = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 解析 CSV，过滤有效行
    batch1 = "batch_2024Q1"
    batch2 = "batch_2024Q2"
    # 收集有效数据：batch, group -> (accuracy, latency, cost)
    def is_valid(val):
        if val is None or val.strip() == "":
            return False
        try:
            float(val)
            return True
        except:
            return False

    records = {batch1: {}, batch2: {}}
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bid = row.get("batch_id", "").strip()
            if bid not in (batch1, batch2):
                continue
            gid = row.get("group_id", "").strip()
            acc = row.get("accuracy", "").strip()
            lat = row.get("latency_ms", "").strip()
            cost = row.get("cost_usd", "").strip()
            if not (is_valid(acc) and is_valid(lat) and is_valid(cost)):
                continue
            # 如果该 batch+group 已存在，跳过（取第一个有效行）
            if gid in records[bid]:
                continue
            records[bid][gid] = {
                "accuracy": Decimal(acc),
                "latency": Decimal(lat),
                "cost": Decimal(cost)
            }

    # 检查每个 group 是否在两个 batch 中都存在
    all_groups = set()
    for bid in [batch1, batch2]:
        all_groups.update(records[bid].keys())
    if len(all_groups) != 3 or not all_groups.issuperset(expected_groups):
        details.append({"item": "数值计算", "score": 0, "max_score": 50, "passed": False, "reason": "CSV 中无法提取出 3 个完整 group 的有效数据"})
        final_score = total_score
        output = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 计算预期差异 (batch2 - batch1)
    expected_diffs = {}
    for gid in expected_groups:
        if gid not in records[batch1] or gid not in records[batch2]:
            # 理论上不可能
            continue
        r1 = records[batch1][gid]
        r2 = records[batch2][gid]
        acc_diff = round_dec(r2["accuracy"] - r1["accuracy"])
        lat_diff = round_dec(r2["latency"] - r1["latency"])
        cost_diff = round_dec(r2["cost"] - r1["cost"])
        expected_diffs[gid] = {
            "accuracy_diff": float(acc_diff),
            "latency_diff": float(lat_diff),
            "cost_diff": float(cost_diff)
        }

    # 逐一检查 Agent 输出
    score_per_group = 50 / 3  # 约 16.6667，向下取整？为了整数，我们按 item 分
    # 我们按字段检查，每个字段约 4.1667，不便于整数。改为每个 group 全对得 16 分，余2分作为 bonus？
    # 简化：每个 group 全对得 16 分（共48），额外2分给完全正确。但更清晰：每个 group 内部三个字段都正确则得16分，否则0分。共48分，剩余2分作为所有group完全正确的奖励。
    # 我们直接计算分数：每个字段正确给1.666，不好。改为每个 group 16分，共48，再奖励2分。
    group_score = 16
    bonus = 2
    group_passed_count = 0
    for item in data:
        gid = item["group_id"]
        if gid not in expected_diffs:
            continue
        exp = expected_diffs[gid]
        # 比较数值，允许浮点容差
        def approx_equal(a, b, eps=1e-9):
            # 转为 Decimal 比较更精确
            return abs(Decimal(str(a)) - Decimal(str(b))) < Decimal('0.0001')
        acc_ok = approx_equal(item.get("accuracy_diff", "NaN"), exp["accuracy_diff"])
        lat_ok = approx_equal(item.get("latency_diff", "NaN"), exp["latency_diff"])
        cost_ok = approx_equal(item.get("cost_diff", "NaN"), exp["cost_diff"])
        if acc_ok and lat_ok and cost_ok:
            group_passed_count += 1
    # 积分
    numeric_score = group_passed_count * group_score
    if group_passed_count == 3:
        numeric_score += bonus  # 全对加奖励
    details.append({
        "item": "数值计算准确性",
        "score": numeric_score,
        "max_score": 50,
        "passed": (group_passed_count == 3),
        "reason": f"3 个 group 中完全正确 {group_passed_count} 个"
    })
    total_score += numeric_score

    # 输出最终分数
    final_score = total_score
    output = {"total_score": final_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
