#!/usr/bin/env python3
import sys
import os
import json
import csv
import io
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 ops/report.json 是否存在 (10分)
    report_path = os.path.join(workspace, "ops", "report.json")
    if os.path.isfile(report_path):
        details.append({
            "item": "report.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/report.json 已找到"
        })
        total_score += 10
    else:
        details.append({
            "item": "report.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/report.json 不存在"
        })
        # 如果文件不存在，后续检查无法进行，直接结束
        _write_score(workspace, total_score, details)
        sys.exit(0)

    # 2. 解析 JSON 格式 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "report.json 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析为 JSON"
        })
        total_score += 10
    except (json.JSONDecodeError, IOError) as e:
        details.append({
            "item": "report.json 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        _write_score(workspace, total_score, details)
        sys.exit(0)

    # 3. 检查字段完整性 (competitor_id, avg_cost, avg_cost_other, cost_difference_percent) (10分)
    required_fields = ["competitor_id", "avg_cost", "avg_cost_other", "cost_difference_percent"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        details.append({
            "item": "必需字段完整",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"包含所有必需字段: {required_fields}"
        })
        total_score += 10
    else:
        details.append({
            "item": "必需字段完整",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"缺少字段: {missing}"
        })
        # 继续检查已存在字段

    # 4. competitor_id 应为 "comp_002" (10分)
    if data.get("competitor_id") == "comp_002":
        details.append({
            "item": "competitor_id 正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "competitor_id 为 comp_002"
        })
        total_score += 10
    else:
        details.append({
            "item": "competitor_id 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 comp_002, 实际 {data.get('competitor_id')}"
        })

    # 5. 计算期望的 avg_cost (comp_002 有效用户平均) (25分)
    users_dir = os.path.join(workspace, "data", "users")
    comp002_costs = []
    comp001_costs = []
    if os.path.isdir(users_dir):
        for fname in os.listdir(users_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(users_dir, fname)
                try:
                    with open(fpath, "r") as f:
                        user = json.load(f)
                    # 只取数据 "comp_002" 或 "comp_001"
                    cid = user.get("competitor_id")
                    cost_raw = user.get("acquisition_cost")
                    # 跳过缺失或非数字
                    if cost_raw is None:
                        continue
                    try:
                        cost = float(cost_raw)
                    except (ValueError, TypeError):
                        continue
                    if cid == "comp_002":
                        comp002_costs.append(cost)
                    elif cid == "comp_001":
                        comp001_costs.append(cost)
                except Exception:
                    continue

    if not comp002_costs or not comp001_costs:
        details.append({
            "item": "用户数据完整性",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"comp002 有效用户数={len(comp002_costs)}, comp001 有效用户数={len(comp001_costs)}"
        })
        _write_score(workspace, total_score, details)
        sys.exit(0)

    expected_avg_002 = sum(comp002_costs) / len(comp002_costs)
    expected_avg_001 = sum(comp001_costs) / len(comp001_costs)
    expected_diff = (expected_avg_002 - expected_avg_001) / expected_avg_001 * 100
    # 保留两位小数
    expected_diff = round(expected_diff, 2)
    expected_avg_002 = round(expected_avg_002, 2)
    expected_avg_001 = round(expected_avg_001, 2)

    # 检查 avg_cost (25分)
    actual_avg_002 = data.get("avg_cost")
    if isinstance(actual_avg_002, (int, float)) and math.isclose(actual_avg_002, expected_avg_002, abs_tol=0.005):
        details.append({
            "item": "avg_cost 计算正确",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"comp_002 平均获客成本 = {actual_avg_002}（期望 {expected_avg_002}）"
        })
        total_score += 25
    else:
        details.append({
            "item": "avg_cost 计算正确",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"实际 {actual_avg_002}, 期望 {expected_avg_002}"
        })

    # 6. 检查 avg_cost_other (20分)
    actual_avg_001 = data.get("avg_cost_other")
    if isinstance(actual_avg_001, (int, float)) and math.isclose(actual_avg_001, expected_avg_001, abs_tol=0.005):
        details.append({
            "item": "avg_cost_other 计算正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"CloudMajor 平均获客成本 = {actual_avg_001}（期望 {expected_avg_001}）"
        })
        total_score += 20
    else:
        details.append({
            "item": "avg_cost_other 计算正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"实际 {actual_avg_001}, 期望 {expected_avg_001}"
        })

    # 7. 检查 cost_difference_percent (15分)
    actual_diff = data.get("cost_difference_percent")
    if isinstance(actual_diff, (int, float)) and math.isclose(actual_diff, expected_diff, abs_tol=0.01):
        details.append({
            "item": "cost_difference_percent 计算正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"差异百分比 = {actual_diff}%（期望 {expected_diff}%）"
        })
        total_score += 15
    else:
        details.append({
            "item": "cost_difference_percent 计算正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"实际 {actual_diff}, 期望 {expected_diff}"
        })

    # 写入最终结果
    _write_score(workspace, total_score, details)


def _write_score(workspace, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")


if __name__ == "__main__":
    main()
