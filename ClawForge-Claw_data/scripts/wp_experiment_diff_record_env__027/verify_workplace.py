import json
import csv
import sys
import os
from math import isclose

def verify(workspace):
    details = []
    total_score = 0

    # 辅助函数
    def add_result(item, score, max_score, passed, reason):
        details.append({"item": item, "score": score, "max_score": max_score, "passed": passed, "reason": reason})
        return score

    # ----- 1. 目录结构 (10分) -----
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        total_score += add_result("目录 'ops/' 存在", 10, 10, True, "ops 目录已创建")
    else:
        total_score += add_result("目录 'ops/' 存在", 0, 10, False, "缺少 ops 目录")

    # ----- 2. 产物文件存在 (10分) -----
    json_path = os.path.join(ops_path, "diff_record.json")
    if os.path.isfile(json_path):
        total_score += add_result("产物文件 ops/diff_record.json 存在", 10, 10, True, "文件存在")
    else:
        total_score += add_result("产物文件 ops/diff_record.json 存在", 0, 10, False, "文件不存在")
        # 后续无法进行，直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # ----- 3. JSON合法性 (10分) -----
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            total_score += add_result("JSON 格式合法且为数组", 10, 10, True, "成功解析为列表")
        else:
            total_score += add_result("JSON 格式合法且为数组", 0, 10, False, "根元素不是列表")
            # 不能继续
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump({"total_score": total_score, "details": details}, f, indent=2)
            return
    except json.JSONDecodeError as e:
        total_score += add_result("JSON 格式合法", 0, 10, False, f"JSON 解析错误: {e}")
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # ----- 4. 条目数量 (10分) -----
    expected_count = 15  # 5 batches * 3 groups
    actual_count = len(data)
    if actual_count == expected_count:
        total_score += add_result(f"条目数量为 {expected_count}", 10, 10, True, f"包含 {actual_count} 条")
    else:
        total_score += add_result(f"条目数量为 {expected_count}", 0, 10, False, f"实际 {actual_count} 条")

    # ----- 5. 字段完整性 (10分) -----
    required_fields = {"batch_id", "group_id", "accuracy_diff", "latency_diff", "cost_diff"}
    all_fields_ok = True
    missing_fields = set()
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            all_fields_ok = False
            missing_fields.add(f"第{i+1}项不是字典")
            continue
        missing = required_fields - set(entry.keys())
        if missing:
            all_fields_ok = False
            missing_fields.update(f"第{i+1}项缺少字段 {missing}")
    if all_fields_ok:
        total_score += add_result("所有条目包含必要字段", 10, 10, True, "字段齐全")
    else:
        total_score += add_result("所有条目包含必要字段", 0, 10, False, f"字段缺失: {missing_fields}")

    # ----- 6. 核心差值计算 (50分) -----
    # 标准答案：按batch_id排序（batch_001,002,003,004,005），每个batch内按group_id排序（A,B,C）
    # 手工计算差值（基准为前一批次，第一批差值为0）
    # 数据来源：builder中的干净行（忽略干扰）
    clean_rows = [
        ["batch_001","A",0.95,120,0.50],
        ["batch_001","B",0.88,150,0.60],
        ["batch_001","C",0.92,130,0.55],
        ["batch_002","A",0.96,110,0.48],
        ["batch_002","B",0.90,140,0.58],
        ["batch_002","C",0.93,125,0.52],
        ["batch_003","A",0.94,130,0.55],
        ["batch_003","B",0.87,160,0.65],
        ["batch_003","C",0.91,140,0.60],
        ["batch_004","A",0.97,105,0.45],
        ["batch_004","B",0.89,145,0.62],
        ["batch_004","C",0.94,115,0.50],
        ["batch_005","A",0.93,135,0.58],
        ["batch_005","B",0.86,170,0.70],
        ["batch_005","C",0.90,150,0.65],
    ]
    # 分组：batch -> group -> (acc, lat, cost)
    batch_groups = {}
    for r in clean_rows:
        b, g, acc, lat, cost = r[0], r[1], float(r[2]), float(r[3]), float(r[4])
        batch_groups.setdefault(b, {})[g] = (acc, lat, cost)
    # 按batch_id排序
    sorted_batches = sorted(batch_groups.keys())
    # 构造标准答案列表
    expected_list = []
    prev_batch = None
    for batch in sorted_batches:
        groups = batch_groups[batch]
        for g in sorted(groups.keys()):
            acc, lat, cost = groups[g]
            if prev_batch is None:
                acc_diff, lat_diff, cost_diff = 0.0, 0.0, 0.0
            else:
                prev_acc, prev_lat, prev_cost = batch_groups[prev_batch][g]
                acc_diff = round(acc - prev_acc, 6)
                lat_diff = round(lat - prev_lat, 6)
                cost_diff = round(cost - prev_cost, 6)
            expected_list.append({
                "batch_id": batch,
                "group_id": g,
                "accuracy_diff": acc_diff,
                "latency_diff": lat_diff,
                "cost_diff": cost_diff
            })
        prev_batch = batch

    # 对agent输出也按相同规则排序，以便比较
    def sort_key(e):
        return (e.get("batch_id",""), e.get("group_id",""))
    sorted_agent = sorted(data, key=sort_key)

    # 比较
    correct_count = 0
    max_items = len(expected_list)
    for i, (exp, act) in enumerate(zip(expected_list, sorted_agent)):
        if (exp["batch_id"] == act.get("batch_id") and
            exp["group_id"] == act.get("group_id") and
            isclose(exp["accuracy_diff"], float(act.get("accuracy_diff", 0)), rel_tol=1e-6) and
            isclose(exp["latency_diff"], float(act.get("latency_diff", 0)), rel_tol=1e-6) and
            isclose(exp["cost_diff"], float(act.get("cost_diff", 0)), rel_tol=1e-6)):
            correct_count += 1

    # 得分 = (correct / max_items) * 50
    diff_score = int(round((correct_count / max_items) * 50))
    if correct_count == max_items:
        total_score += add_result("所有差值计算正确", 50, 50, True, f"全部 {max_items} 项匹配")
    else:
        total_score += add_result(f"差值计算（正确 {correct_count}/{max_items}）", diff_score, 50,
                                  False, f"有 {max_items - correct_count} 项不匹配")

    # 写入结果
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Final score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
