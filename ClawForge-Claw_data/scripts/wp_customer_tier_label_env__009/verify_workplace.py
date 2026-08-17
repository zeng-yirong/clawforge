import sys
import os
import json
import csv
import re
from pathlib import Path
from collections import Counter

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. 检查输出文件是否存在 (20分)
    output_path = ws / "ops" / "tier_updates.json"
    if output_path.exists():
        details.append({"item": "输出文件存在", "score": 20, "max_score": 20, "passed": True, "reason": "ops/tier_updates.json 存在"})
        total_score += 20
    else:
        details.append({"item": "输出文件存在", "score": 0, "max_score": 20, "passed": False, "reason": "ops/tier_updates.json 未找到"})
        # 如果文件不存在，后续检查无意义，直接返回
        write_score(details, total_score, ws)
        return

    # 2. 文件格式合法且JSON可解析 (15分)
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 15, "max_score": 15, "passed": True, "reason": "文件可解析为JSON"})
        total_score += 15
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        write_score(details, total_score, ws)
        return

    # 3. 数据结构正确 (25分)
    # 期望的结构：{"updates": [{"customer_id": ..., "new_labels": [...]}]} 或者直接{"customer_id":..., "labels_to_add":...}
    # 两种格式都接受，但必须包含关键字段。我们要求包含 updates 数组，每个元素有customer_id和new_labels
    if not isinstance(data, dict):
        details.append({"item": "数据结构类型", "score": 0, "max_score": 25, "passed": False, "reason": "顶层应为JSON对象"})
        write_score(details, total_score, ws)
        return

    updates = None
    if "updates" in data:
        updates = data["updates"]
    elif "customer_id" in data and "labels_to_add" in data:
        # 单个对象包裹成列表
        updates = [data]
    else:
        details.append({"item": "数据结构字段", "score": 0, "max_score": 25, "passed": False, "reason": "未找到updates数组或customer_id/labels_to_add字段"})
        write_score(details, total_score, ws)
        return

    if not isinstance(updates, list) or len(updates) == 0:
        details.append({"item": "数据结构字段", "score": 0, "max_score": 25, "passed": False, "reason": "updates应为非空数组"})
        write_score(details, total_score, ws)
        return

    # 检查每个元素
    valid_structure = True
    for item in updates:
        if not isinstance(item, dict) or "customer_id" not in item or "new_labels" not in item:
            valid_structure = False
            break
        if not isinstance(item["new_labels"], list):
            valid_structure = False
            break

    if valid_structure:
        details.append({"item": "数据结构字段", "score": 25, "max_score": 25, "passed": True, "reason": "updates数组元素包含customer_id和new_labels列表"})
        total_score += 25
    else:
        details.append({"item": "数据结构字段", "score": 0, "max_score": 25, "passed": False, "reason": "字段缺失或类型错误"})
        write_score(details, total_score, ws)
        return

    # 4. 业务逻辑正确性 (40分)
    # 根据真实数据（live目录下的）计算正确答案
    # 加载真实的客户、活动、消费数据
    try:
        with open(ws / "data" / "customers" / "customers.json") as f:
            customers_data = json.load(f)
        customers = {c["customer_id"]: c for c in customers_data["customers"]}

        with open(ws / "data" / "logs" / "live" / "activity_logs.json") as f:
            activity_data = json.load(f)
        activity_map = {a["customer_id"]: a for a in activity_data["activity_logs"]}

        with open(ws / "data" / "logs" / "live" / "consumption_logs.json") as f:
            consumption_data = json.load(f)
        consumption_map = {c["customer_id"]: c for c in consumption_data["consumption_logs"]}
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        details.append({"item": "参考数据加载", "score": 0, "max_score": 40, "passed": False, "reason": f"无法加载参考数据: {str(e)}"})
        write_score(details, total_score, ws)
        return

    # 筛选条件：季度消费 > 50000, last_active_days <= 30, risk_level == "low"
    expected_updates = []
    for cid in customers:
        if cid not in activity_map or cid not in consumption_map:
            continue
        cons = consumption_map[cid]
        act = activity_map[cid]
        if cons["quarter_spend_usd"] > 50000 and act["last_active_days"] <= 30 and act["risk_level"] == "low":
            expected_updates.append({"customer_id": cid, "new_labels": ["priority_support"]})

    # 比较 agent 输出
    agent_updates = {item["customer_id"]: item["new_labels"] for item in updates}
    expected_ids = set(item["customer_id"] for item in expected_updates)
    agent_ids = set(agent_updates.keys())

    if expected_ids != agent_ids:
        details.append({"item": "客户ID匹配", "score": 0, "max_score": 40, "passed": False,
                        "reason": f"期望客户ID: {expected_ids}, 实际: {agent_ids}"})
        write_score(details, total_score, ws)
        return

    # 检查标签
    for item in expected_updates:
        cid = item["customer_id"]
        if cid not in agent_updates:
            details.append({"item": "客户ID存在", "score": 0, "max_score": 40, "passed": False, "reason": f"缺少客户 {cid}"})
            write_score(details, total_score, ws)
            return
        if agent_updates[cid] != item["new_labels"]:
            details.append({"item": "标签内容", "score": 0, "max_score": 40, "passed": False,
                            "reason": f"客户 {cid} 期望标签 {item['new_labels']}, 实际 {agent_updates[cid]}"})
            write_score(details, total_score, ws)
            return

    details.append({"item": "业务逻辑正确", "score": 40, "max_score": 40, "passed": True, "reason": "输出与基于live数据的计算结果完全一致"})
    total_score += 40

    write_score(details, total_score, ws)

def write_score(details, total_score, ws):
    # 确保total_score在0-100之间
    total_score = min(max(total_score, 0), 100)
    result = {"total_score": total_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}")

if __name__ == "__main__":
    main()
