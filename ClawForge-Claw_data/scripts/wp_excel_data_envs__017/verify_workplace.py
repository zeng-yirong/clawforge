import os
import sys
import csv
import json
import math

def verify_workplace(workspace: str) -> dict:
    details = []
    total_score = 0

    # --- 1. 目录 / 文件结构检查 (10分) ---
    output_dir = os.path.join(workspace, "output")
    clean_csv = os.path.join(output_dir, "sales_clean.csv")
    summary_json = os.path.join(output_dir, "regional_summary.json")

    # 1.1 output 目录存在 (2分)
    if os.path.isdir(output_dir):
        details.append({"item": "output directory exists", "score": 2, "max_score": 2, "passed": True, "reason": "output directory found"})
        total_score += 2
    else:
        details.append({"item": "output directory exists", "score": 0, "max_score": 2, "passed": False, "reason": "output directory missing"})

    # 1.2 sales_clean.csv 存在 (4分)
    if os.path.isfile(clean_csv):
        details.append({"item": "sales_clean.csv exists", "score": 4, "max_score": 4, "passed": True, "reason": "file found"})
        total_score += 4
    else:
        details.append({"item": "sales_clean.csv exists", "score": 0, "max_score": 4, "passed": False, "reason": "file missing"})

    # 1.3 regional_summary.json 存在 (4分)
    if os.path.isfile(summary_json):
        details.append({"item": "regional_summary.json exists", "score": 4, "max_score": 4, "passed": True, "reason": "file found"})
        total_score += 4
    else:
        details.append({"item": "regional_summary.json exists", "score": 0, "max_score": 4, "passed": False, "reason": "file missing"})

    # 如果关键文件缺失则提前返回，避免后续解析报错
    if not (os.path.isfile(clean_csv) and os.path.isfile(summary_json)):
        details.append({"item": "Overall file structure", "score": 0, "max_score": 0, "passed": False, "reason": "core files missing"})
        return {"total_score": total_score, "details": details}

    # --- 2. 清理后 CSV 检查 (40分) ---
    # 2.1 CSV 格式合法 (5分)
    try:
        with open(clean_csv, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        passed_format = True
        reason_format = "CSV parsed successfully"
        score_format = 5
    except Exception as e:
        passed_format = False
        reason_format = f"CSV parse error: {e}"
        score_format = 0
    details.append({"item": "sales_clean.csv format validity", "score": score_format, "max_score": 5, "passed": passed_format, "reason": reason_format})
    total_score += score_format
    if not passed_format:
        return {"total_score": total_score, "details": details}

    # 2.2 列头正确 (5分)
    expected_headers = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "subcategory", "region", "city", "customer_id", "customer_name",
        "sales_amount", "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]
    actual_headers = list(rows[0].keys()) if rows else []
    if actual_headers == expected_headers:
        details.append({"item": "CSV headers correct", "score": 5, "max_score": 5, "passed": True, "reason": "headers match"})
        total_score += 5
    else:
        details.append({"item": "CSV headers correct", "score": 0, "max_score": 5, "passed": False, "reason": f"expected {expected_headers}, got {actual_headers}"})

    # 2.3 去重正确：无重复 transaction_id (10分)
    tids = [r["transaction_id"] for r in rows]
    if len(tids) == len(set(tids)):
        details.append({"item": "No duplicate transaction_id in cleaned data", "score": 10, "max_score": 10, "passed": True, "reason": "all transaction_ids unique"})
        total_score += 10
    else:
        duplicates = [tid for tid in set(tids) if tids.count(tid) > 1]
        details.append({"item": "No duplicate transaction_id in cleaned data", "score": 0, "max_score": 10, "passed": False, "reason": f"duplicates found: {duplicates}"})

    # 2.4 保留的重复记录中日期为最新 (5分)
    # 已知 T001 应保留 2025-01-03 的 110.0；T002 应保留 2025-01-05 (但 amount 空)；T003 应保留 2025-01-04 的 300.0
    # T010 应保留 2025-01-01 的 550.0
    expected_latest = {
        "T001": {"date": "2025-01-03", "sales_amount": "110.0"},
        "T002": {"date": "2025-01-05", "sales_amount": ""},
        "T003": {"date": "2025-01-04", "sales_amount": "300.0"},
        "T010": {"date": "2025-01-01", "sales_amount": "550.0"},
    }
    passed_latest = True
    reasons_latest = []
    for row in rows:
        tid = row["transaction_id"]
        if tid in expected_latest:
            exp = expected_latest[tid]
            if row["date"] != exp["date"] or row["sales_amount"] != exp["sales_amount"]:
                passed_latest = False
                reasons_latest.append(f"{tid}: date {row['date']} vs expected {exp['date']}, amount {row['sales_amount']} vs expected {exp['sales_amount']}")
    if passed_latest:
        details.append({"item": "Duplicate rows resolved to latest date/amount", "score": 5, "max_score": 5, "passed": True, "reason": "all duplicates correctly handled"})
        total_score += 5
    else:
        details.append({"item": "Duplicate rows resolved to latest date/amount", "score": 0, "max_score": 5, "passed": False, "reason": "; ".join(reasons_latest)})

    # 2.5 缺失 sales_amount 被正确填充 (15分)
    # 根据预期填充结果：T002 缺失，产品 P001，清理后 P001 非空值来自 T001(110.0) 和 T006(120.0) => avg=115.0
    # T005 缺失，产品 P002，清理后 P002 非空值来自 T003(300.0) 和 T007(250.0) => avg=275.0
    # 注意：本环境 builder 不包含其他 P002 非空？有 T003 (300) 和 T007 (250)，所以平均 = 275.0
    expected_fill = {
        "T002": "115.0",
        "T005": "275.0"
    }
    fill_ok = True
    fill_reasons = []
    for row in rows:
        tid = row["transaction_id"]
        if tid in expected_fill:
            exp_amount = expected_fill[tid]
            # 允许浮点比较
            try:
                actual = float(row["sales_amount"]) if row["sales_amount"] else 0.0
                expected = float(exp_amount)
                if abs(actual - expected) > 0.01:
                    fill_ok = False
                    fill_reasons.append(f"{tid}: got {row['sales_amount']}, expected {exp_amount}")
            except ValueError:
                fill_ok = False
                fill_reasons.append(f"{tid}: non-numeric value {row['sales_amount']}")
    if fill_ok:
        details.append({"item": "Missing sales_amount filled with product average", "score": 15, "max_score": 15, "passed": True, "reason": "all missing values correctly imputed"})
        total_score += 15
    else:
        details.append({"item": "Missing sales_amount filled with product average", "score": 0, "max_score": 15, "passed": False, "reason": "; ".join(fill_reasons)})

    # --- 3. 汇总 JSON 检查 (50分) ---
    # 3.1 JSON 格式合法 (5分)
    try:
        with open(summary_json, "r") as f:
            summary = json.load(f)
        passed_json = True
        reason_json = "JSON parsed successfully"
        score_json = 5
    except Exception as e:
        passed_json = False
        reason_json = f"JSON parse error: {e}"
        score_json = 0
    details.append({"item": "regional_summary.json format validity", "score": score_json, "max_score": 5, "passed": passed_json, "reason": reason_json})
    total_score += score_json
    if not passed_json:
        return {"total_score": total_score, "details": details}

    # 3.2 结构检查：应为字典，key 为 region (5分)
    if isinstance(summary, dict):
        details.append({"item": "JSON structure (dict)", "score": 5, "max_score": 5, "passed": True, "reason": "valid dict"})
        total_score += 5
    else:
        details.append({"item": "JSON structure (dict)", "score": 0, "max_score": 5, "passed": False, "reason": f"expected dict, got {type(summary)}"})

    # 3.3 分组平均值计算正确 (40分)
    # 已知清理后数据集（包括填充后）：
    # 我们手动构建清理后的完整数据 (按前述规则)
    # 交易列表（去重保留最新）：
    clean_rows_data = [
        {"transaction_id": "T001", "region": "East", "sales_amount": 110.0},
        {"transaction_id": "T002", "region": "East", "sales_amount": 115.0},   # 填充
        {"transaction_id": "T003", "region": "West", "sales_amount": 300.0},
        {"transaction_id": "T004", "region": "North", "sales_amount": 150.0},
        {"transaction_id": "T005", "region": "West", "sales_amount": 275.0},    # 填充
        {"transaction_id": "T006", "region": "South", "sales_amount": 120.0},
        {"transaction_id": "T007", "region": "North", "sales_amount": 250.0},
        {"transaction_id": "T008", "region": "East", "sales_amount": 180.0},
        {"transaction_id": "T009", "region": "South", "sales_amount": 160.0},
        {"transaction_id": "T010", "region": "East", "sales_amount": 550.0},
    ]
    # 注意：T011 是旧备份，不应出现在清理后数据中（数据日期太早且与当前任务无关，但 agent 可能包含？prompt 明确“别动其他文件”，所以不应包含）
    # 检查清理后 CSV 中是否只有上述 10 条交易？我们可额外检查行数，但这里只要求平均值。
    # 计算每个区域的平均值
    expected_avg = {}
    region_amounts = {}
    for r in clean_rows_data:
        reg = r["region"]
        amt = r["sales_amount"]
        region_amounts.setdefault(reg, []).append(amt)
    for reg, vals in region_amounts.items():
        expected_avg[reg] = round(sum(vals) / len(vals), 2)

    # 实际 summary 中的数值
    passed_avg = True
    avg_reasons = []
    for region, expected_val in expected_avg.items():
        actual_val = summary.get(region)
        if actual_val is None:
            passed_avg = False
            avg_reasons.append(f"region '{region}' missing")
            continue
        try:
            actual_float = float(actual_val)
            if abs(actual_float - expected_val) > 0.02:
                passed_avg = False
                avg_reasons.append(f"region '{region}': got {actual_float}, expected {expected_val}")
        except (TypeError, ValueError):
            passed_avg = False
            avg_reasons.append(f"region '{region}': non-numeric value {actual_val}")
    # 检查是否有额外 region（如 agent 错误地包含了旧备份中的 region）
    for region in summary:
        if region not in expected_avg:
            passed_avg = False
            avg_reasons.append(f"unexpected region '{region}' in summary")

    if passed_avg:
        details.append({"item": "Regional average sales amount correct", "score": 40, "max_score": 40, "passed": True, "reason": "all regions match expected"})
        total_score += 40
    else:
        details.append({"item": "Regional average sales amount correct", "score": 0, "max_score": 40, "passed": False, "reason": "; ".join(avg_reasons)})

    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify_workplace(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {output_path}")
