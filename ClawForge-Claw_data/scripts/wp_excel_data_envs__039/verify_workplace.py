import os
import json
import csv
import sys
from collections import defaultdict
from math import isclose

def remove_duplicates(records):
    """保留每个 transaction_id 中 date 最新的记录"""
    best = {}
    for r in records:
        tid = r["transaction_id"]
        if tid not in best or r["date"] > best[tid]["date"]:
            best[tid] = r
    return list(best.values())

def fill_missing_amounts(records):
    """按 category 平均填充缺失的 sales_amount"""
    # 计算每个 category 的非缺失平均值
    cat_sums = defaultdict(float)
    cat_counts = defaultdict(int)
    for r in records:
        amt = r["sales_amount"]
        if amt is not None:
            cat_sums[r["category"]] += amt
            cat_counts[r["category"]] += 1
    cat_avg = {c: cat_sums[c] / cat_counts[c] for c in cat_sums if cat_counts[c] > 0}
    
    filled = []
    for r in records:
        if r["sales_amount"] is None:
            r["sales_amount"] = round(cat_avg.get(r["category"], 0), 2)
        filled.append(r)
    return filled

def compute_monthly_summary(records):
    """按月聚合"""
    monthly = defaultdict(lambda: {"total": 0.0, "count": 0})
    for r in records:
        month = r["date"][:7]
        monthly[month]["total"] += r["sales_amount"]
        monthly[month]["count"] += 1
    result = []
    for month in sorted(monthly.keys()):
        info = monthly[month]
        avg = info["total"] / info["count"] if info["count"] > 0 else 0.0
        result.append({
            "month": month,
            "total_sales": round(info["total"], 2),
            "order_count": info["count"],
            "average_order_value": round(avg, 2)
        })
    return result

def load_csv(workspace, rel_path):
    filepath = os.path.join(workspace, rel_path)
    rows = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 处理 sales_amount：空字符串或缺失变为 None
            sa = row.get("sales_amount", "").strip()
            row["sales_amount"] = float(sa) if sa else None
            rows.append(row)
    return rows

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    # ========== 结构检查 ==========
    score_details = []
    
    # 1. reports 目录存在
    reports_dir = os.path.join(workspace, "reports")
    dir_exists = os.path.isdir(reports_dir)
    score_details.append({
        "item": "reports directory exists",
        "max_score": 10,
        "score": 10 if dir_exists else 0,
        "passed": dir_exists,
        "reason": "Directory exists" if dir_exists else "Missing reports/ directory"
    })
    if not dir_exists:
        score_details.append({"item": "monthly_summary.json exists", "max_score": 10, "score": 0, "passed": False, "reason": "Skipped due to missing directory"})
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    # 2. monthly_summary.json 存在
    summary_path = os.path.join(workspace, "reports", "monthly_summary.json")
    file_exists = os.path.isfile(summary_path)
    score_details.append({
        "item": "monthly_summary.json exists",
        "max_score": 10,
        "score": 10 if file_exists else 0,
        "passed": file_exists,
        "reason": "File found" if file_exists else "Missing reports/monthly_summary.json"
    })
    if not file_exists:
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    # 3. JSON 格式合法
    try:
        with open(summary_path) as f:
            data = json.load(f)
        json_valid = True
    except:
        json_valid = False
    score_details.append({
        "item": "JSON format valid",
        "max_score": 10,
        "score": 10 if json_valid else 0,
        "passed": json_valid,
        "reason": "Valid JSON" if json_valid else "Invalid JSON content"
    })
    if not json_valid:
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    # 4. 结构包含 monthly_summary 列表
    has_summary = isinstance(data, dict) and "monthly_summary" in data
    score_details.append({
        "item": "Contains 'monthly_summary' key",
        "max_score": 5,
        "score": 5 if has_summary else 0,
        "passed": has_summary,
        "reason": "Key present" if has_summary else "Missing 'monthly_summary' key"
    })
    if not has_summary:
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    summary_list = data["monthly_summary"]
    if not isinstance(summary_list, list):
        score_details.append({"item": "monthly_summary is list", "max_score": 5, "score": 0, "passed": False, "reason": "Not a list"})
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return
    score_details.append({"item": "monthly_summary is list", "max_score": 5, "score": 5, "passed": True, "reason": "Type correct"})

    # ========== 数据计算 ==========
    # 读取原始 CSV 并清理
    try:
        raw_records = load_csv(workspace, "data/sales_raw.csv")
    except:
        score_details.append({"item": "Read raw sales data", "max_score": 10, "score": 0, "passed": False, "reason": "Cannot read data/sales_raw.csv"})
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    deduped = remove_duplicates(raw_records)
    filled = fill_missing_amounts(deduped)
    expected_monthly = compute_monthly_summary(filled)

    # 比较月份数量
    expected_months = {m["month"] for m in expected_monthly}
    actual_months = {m["month"] for m in summary_list}
    months_match = (expected_months == actual_months)
    score_details.append({
        "item": "Month list matches",
        "max_score": 10,
        "score": 10 if months_match else 0,
        "passed": months_match,
        "reason": "All months correct" if months_match else f"Expected {expected_months}, got {actual_months}"
    })

    # 构建实际月份字典便于比较
    actual_map = {m["month"]: m for m in summary_list}
    expected_map = {m["month"]: m for m in expected_monthly}

    total_sales_correct = 0
    order_count_correct = 0
    avg_value_correct = 0
    max_months = len(expected_monthly)
    total_sales_max = 30
    order_count_max = 15
    avg_value_max = 25

    # 每个月份逐项比较
    for month in expected_months:
        exp = expected_map[month]
        act = actual_map.get(month)
        if act is None:
            # 月份缺失，该月份总分0
            continue
        # total_sales
        if isclose(exp["total_sales"], act["total_sales"], rel_tol=1e-6, abs_tol=0.005):
            total_sales_correct += (total_sales_max / max_months)
        # order_count
        if exp["order_count"] == act["order_count"]:
            order_count_correct += (order_count_max / max_months)
        # average_order_value
        if isclose(exp["average_order_value"], act["average_order_value"], rel_tol=1e-6, abs_tol=0.005):
            avg_value_correct += (avg_value_max / max_months)

    total_sales_score = round(total_sales_correct)
    order_count_score = round(order_count_correct)
    avg_value_score = round(avg_value_correct)

    score_details.append({
        "item": "Total sales accuracy",
        "max_score": total_sales_max,
        "score": total_sales_score,
        "passed": total_sales_score == total_sales_max,
        "reason": f"Got {total_sales_score}/{total_sales_max} for total sales"
    })
    score_details.append({
        "item": "Order count accuracy",
        "max_score": order_count_max,
        "score": order_count_score,
        "passed": order_count_score == order_count_max,
        "reason": f"Got {order_count_score}/{order_count_max} for order count"
    })
    score_details.append({
        "item": "Average order value accuracy",
        "max_score": avg_value_max,
        "score": avg_value_score,
        "passed": avg_value_score == avg_value_max,
        "reason": f"Got {avg_value_score}/{avg_value_max} for average order value"
    })

    total_score = sum(d["score"] for d in score_details)
    # 写入评分
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
