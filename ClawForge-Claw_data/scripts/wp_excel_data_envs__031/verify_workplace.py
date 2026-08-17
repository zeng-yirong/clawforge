import sys
import os
import json
import csv
from collections import Counter

def verify(workspace: str):
    details = []
    total_score = 0

    # ---------- 1. 目录结构 (10分) ----------
    analysis_dir = os.path.join(workspace, "analysis")
    if os.path.isdir(analysis_dir):
        details.append({"item": "analysis directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "analysis/ directory present"})
        total_score += 10
    else:
        details.append({"item": "analysis directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "analysis/ directory missing"})
        return total_score, details  # 后续依赖此目录，直接返回

    # ---------- 2. 清理后的 CSV 文件 (20分) ----------
    cleaned_csv_path = os.path.join(analysis_dir, "cleaned_sales.csv")
    if not os.path.isfile(cleaned_csv_path):
        details.append({"item": "cleaned_sales.csv exists", "score": 0, "max_score": 20, "passed": False, "reason": "file missing"})
        return total_score, details
    try:
        with open(cleaned_csv_path, newline="") as f:
            reader = list(csv.DictReader(f))
        if len(reader) == 0:
            raise ValueError("empty csv")
        fieldnames_ok = all(k in reader[0] for k in ["transaction_id", "sales_amount", "product_name", "category"])
        if not fieldnames_ok:
            raise ValueError("missing required fields")
        details.append({"item": "cleaned_sales.csv format valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid CSV with required fields"})
        total_score += 10
    except Exception as e:
        details.append({"item": "cleaned_sales.csv format valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Could not parse: {str(e)}"})
        return total_score, details

    # ---------- 3. 去重验证 (15分) ----------
    tids = [r["transaction_id"] for r in reader]
    dup_tids = [tid for tid, cnt in Counter(tids).items() if cnt > 1]
    if dup_tids:
        details.append({"item": "No duplicate transaction_id", "score": 0, "max_score": 15, "passed": False, "reason": f"Duplicate IDs found: {dup_tids}"})
    else:
        details.append({"item": "No duplicate transaction_id", "score": 15, "max_score": 15, "passed": True, "reason": "All transaction_id unique"})
        total_score += 15

    # ---------- 4. 缺失值填充验证 (15分) ----------
    missing_sales = [r for r in reader if r["sales_amount"] in ("", None) or float(r["sales_amount"]) is None]
    missing_name = [r for r in reader if r["product_name"] in ("", None)]
    if missing_sales or missing_name:
        details.append({"item": "Missing values filled", "score": 0, "max_score": 15, "passed": False, "reason": f"Still have missing: sales_amount empty? {len(missing_sales)}, product_name empty? {len(missing_name)}"})
    else:
        # 检查 T006 的 sales_amount 是否为 0，T007 的 product_name 是否为 "Unknown"
        t006 = next((r for r in reader if r["transaction_id"] == "T006"), None)
        t007 = next((r for r in reader if r["transaction_id"] == "T007"), None)
        if t006 and t007:
            if float(t006["sales_amount"]) == 0.0 and t007["product_name"] == "Unknown":
                details.append({"item": "Missing values filled", "score": 15, "max_score": 15, "passed": True, "reason": "T006.sales_amount=0, T007.product_name='Unknown'"})
                total_score += 15
            else:
                details.append({"item": "Missing values filled", "score": 8, "max_score": 15, "passed": False, "reason": f"T006.sales_amount={t006['sales_amount']}, T007.product_name={t007['product_name']}"})
        else:
            details.append({"item": "Missing values filled", "score": 0, "max_score": 15, "passed": False, "reason": "Missing expected rows T006 or T007"})

    # ---------- 5. summary.json 计算 (40分) ----------
    summary_path = os.path.join(analysis_dir, "summary.json")
    if not os.path.isfile(summary_path):
        details.append({"item": "summary.json exists", "score": 0, "max_score": 40, "passed": False, "reason": "file missing"})
        return total_score, details
    try:
        with open(summary_path) as f:
            summary = json.load(f)
    except Exception as e:
        details.append({"item": "summary.json valid JSON", "score": 0, "max_score": 40, "passed": False, "reason": f"JSON parse error: {str(e)}"})
        return total_score, details

    # 计算期望的 category totals (基于 cleaned 数据)
    # 使用 reader 中的记录（已经过去重和填充）
    expect_totals = {}
    for r in reader:
        cat = r["category"]
        amt = float(r["sales_amount"]) if r["sales_amount"] else 0.0
        expect_totals[cat] = expect_totals.get(cat, 0.0) + amt

    # 检查 summary 是否包含所有类别的值，并按降序排列（检查顺序）
    # summary 可以是 {"category": total} 形式或者数组形式？prompt说"最常见的 `{"category": total}`"，即字典。
    if not isinstance(summary, dict):
        details.append({"item": "summary format dictionary", "score": 0, "max_score": 10, "passed": False, "reason": "expected dict, got " + str(type(summary))})
        # 但是后面仍然可检查 key/value，所以继续
    # 检查每个 key 的数值是否匹配
    mismatch = []
    for cat, expected in expect_totals.items():
        actual = summary.get(cat, None)
        if actual is None or abs(float(actual) - expected) > 1e-6:
            mismatch.append(f"{cat}: expected {expected}, got {actual}")
    if mismatch:
        details.append({"item": "Category totals correct", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(mismatch)})
    else:
        details.append({"item": "Category totals correct", "score": 20, "max_score": 20, "passed": True, "reason": "All category totals match cleaned data"})
        total_score += 20

    # 检查是否按降序排列 (prompt要求)
    sorted_keys = sorted(summary.keys(), key=lambda k: summary[k], reverse=True)
    if list(summary.keys()) != sorted_keys:
        details.append({"item": "Categories sorted descending", "score": 0, "max_score": 10, "passed": False, "reason": f"Keys order: {list(summary.keys())}, expected descending by value"})
    else:
        details.append({"item": "Categories sorted descending", "score": 10, "max_score": 10, "passed": True, "reason": "Order is descending by total sales"})
        total_score += 10

    # ---------- 6. 总分 ----------
    # 确保总分0-100
    final_score = min(100, max(0, total_score))
    result = {
        "total_score": final_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    return final_score, details


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score, details = verify(workspace)
    print(f"Total score: {total_score}/100")
    # 已写入 workplace_score.json
