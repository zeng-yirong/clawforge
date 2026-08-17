#!/usr/bin/env python3
"""
Verifier for wp_compete_track_envs__014.
Checks that the agent produced ops/target_leads.json with correct filtering.
"""
import json
import os
import sys
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # Helper to add result
    def add(item, score, max_score, passed, reason):
        nonlocal total_score
        results.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        total_score += score

    # ------------- item 1: ops/ directory exists (5 points) -------------
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        add("ops/ 目录存在", 5, 5, True, "")
    else:
        add("ops/ 目录存在", 0, 5, False, "ops/ 目录不存在")
        # If directory missing, skip further checks
        finalize(results, total_score, workspace)
        return

    # ------------- item 2: ops/target_leads.json exists (5 points) -------------
    target_path = os.path.join(workspace, "ops", "target_leads.json")
    if os.path.isfile(target_path):
        add("target_leads.json 文件存在", 5, 5, True, "")
    else:
        add("target_leads.json 文件存在", 0, 5, False, "文件不存在")
        finalize(results, total_score, workspace)
        return

    # ------------- item 3: valid JSON (10 points) -------------
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        add("JSON 格式合法", 0, 10, False, f"解析失败: {e}")
        finalize(results, total_score, workspace)
        return

    if not isinstance(data, list):
        add("JSON 是列表", 0, 10, False, "根元素不是列表")
        finalize(results, total_score, workspace)
        return
    add("JSON 是合法的列表", 10, 10, True, "")

    # ------------- item 4: list non-empty (5 points) -------------
    if len(data) > 0:
        add("列表非空", 5, 5, True, "")
    else:
        add("列表非空", 0, 5, False, "列表为空")

    # ------------- item 5: each entry has required fields (20 points) -------------
    required_fields = ["user_id", "name", "competitor_name", "growth_rate"]
    field_ok = True
    for idx, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_ok = False
            reason = f"第 {idx} 项不是字典"
            break
        missing = [f for f in required_fields if f not in entry]
        if missing:
            field_ok = False
            reason = f"第 {idx} 项缺少字段: {missing}"
            break
    if field_ok:
        add("每条记录包含规定的四个字段", 20, 20, True, "")
    else:
        add("每条记录包含规定的四个字段", 0, 20, False, reason)

    # ------------- item 6: data correctness (match expected) (30 points) -------------
    # Expected output (sorted by user_id)
    expected = [
        {"user_id": "U002", "name": "Bob Williams", "competitor_name": "DataFlow AI", "growth_rate": 0.25},
        {"user_id": "U003", "name": "Carol Martinez", "competitor_name": "SmartSaaS", "growth_rate": 0.30},
        {"user_id": "U005", "name": "Emma Brown", "competitor_name": "DataFlow AI", "growth_rate": 0.25}
    ]

    # Sort both by user_id for comparison
    data_sorted = sorted(data, key=lambda x: x.get("user_id", ""))
    incorrect_items = []
    if len(data_sorted) != len(expected):
        incorrect_items.append(f"记录数量不符: 期望 {len(expected)}, 实际 {len(data_sorted)}")
    else:
        for i, (e, d) in enumerate(zip(expected, data_sorted)):
            if e["user_id"] != d.get("user_id"):
                incorrect_items.append(f"第 {i+1} 条 user_id 不符")
            if e["name"] != d.get("name"):
                incorrect_items.append(f"第 {i+1} 条 name 不符")
            if e["competitor_name"] != d.get("competitor_name"):
                incorrect_items.append(f"第 {i+1} 条 competitor_name 不符")
            # Compare growth_rate with tolerance
            if not math.isclose(e["growth_rate"], d.get("growth_rate", -1), rel_tol=1e-5):
                incorrect_items.append(f"第 {i+1} 条 growth_rate 不符: 期望 {e['growth_rate']}, 实际 {d.get('growth_rate')}")

    if not incorrect_items:
        add("数据内容完全正确", 30, 30, True, "")
    else:
        add("数据内容完全正确", 0, 30, False, "; ".join(incorrect_items[:5]))

    # ------------- item 7: sorted by user_id ascending (10 points) -------------
    if len(data_sorted) > 0:
        ids = [d.get("user_id","") for d in data_sorted]
        if all(ids[i] <= ids[i+1] for i in range(len(ids)-1)):
            add("按 user_id 升序排列", 10, 10, True, "")
        else:
            add("按 user_id 升序排列", 0, 10, False, "排序错误")
    else:
        add("按 user_id 升序排列", 0, 10, False, "无数据可排序")

    # ------------- item 8: no extra records (10 points) -------------
    # Check that all entries in data_sorted have user_id in expected set
    expected_ids = {e["user_id"] for e in expected}
    actual_ids = [d.get("user_id","") for d in data_sorted]
    extra = [uid for uid in actual_ids if uid not in expected_ids]
    if not extra:
        add("无多余记录", 10, 10, True, "")
    else:
        add("无多余记录", 0, 10, False, f"包含多余的 user_id: {extra}")

    # Finalize
    finalize(results, total_score, workspace)

def finalize(results, total_score, workspace):
    # Ensure total_score is integer between 0 and 100
    total_score = min(max(int(total_score), 0), 100)
    output = {
        "total_score": total_score,
        "details": results
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
