import sys
import os
import json
import csv
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. Check report file exists (10 points)
    report_path = os.path.join(workspace, "reports", "q3_brief.md")
    if os.path.isfile(report_path):
        details.append({"item": "Report file exists", "score": 10, "max_score": 10, "passed": True, "reason": "reports/q3_brief.md 存在"})
        total_score += 10
    else:
        details.append({"item": "Report file exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/q3_brief.md 未找到"})
        # If file missing, skip further checks
        write_score(details, total_score, workspace)
        return

    # 2. Read report content and locate JSON block (10 points)
    with open(report_path, "r") as f:
        content = f.read()
    # Find JSON code block
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        details.append({"item": "JSON code block present", "score": 10, "max_score": 10, "passed": True, "reason": "找到 ```json ... ``` 代码块"})
        total_score += 10
    else:
        details.append({"item": "JSON code block present", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 JSON 代码块"})
        write_score(details, total_score, workspace)
        return

    # 3. Parse JSON (10 points)
    try:
        data = json.loads(json_match.group(1))
        if not isinstance(data, dict):
            raise ValueError("Not a dict")
        details.append({"item": "JSON 解析成功", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式合法"})
        total_score += 10
    except Exception:
        details.append({"item": "JSON 解析成功", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败"})
        write_score(details, total_score, workspace)
        return

    # 4. Validate period field (10 points)
    period = data.get("period")
    if period == "2023-Q3":
        details.append({"item": "Period 正确", "score": 10, "max_score": 10, "passed": True, "reason": "period 字段为 2023-Q3"})
        total_score += 10
    else:
        details.append({"item": "Period 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 2023-Q3，实际 {period}"})
        # Continue checking other parts even if period wrong

    # 5. Check data integrity: read ledgers and compute expected values (60 points split)
    # Only Q3 rows with numeric metric_value are expected
    expected = {"customer": {}, "ops": {}, "product": {}}
    ledger_mapping = {
        "data/ledgers/customer_ledger.csv": "customer",
        "data/ledgers/ops_ledger.csv": "ops",
        "data/ledgers/product_ledger.csv": "product"
    }
    for csv_path, category in ledger_mapping.items():
        full_path = os.path.join(workspace, csv_path)
        if not os.path.isfile(full_path):
            continue
        with open(full_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                period_val = row.get("period", "").strip()
                metric = row.get("metric_code", "").strip()
                raw_val = row.get("metric_value", "").strip()
                if period_val != "2023-Q3":
                    continue
                # Accept only numeric (int or float)
                try:
                    # Convert to float first, then int if integral to avoid decimals losing
                    val = float(raw_val)
                    if val == int(val):
                        val = int(val)
                except (ValueError, TypeError):
                    continue
                # Sum if same metric appears multiple times (though in our data each code appears once valid)
                if metric not in expected[category]:
                    expected[category][metric] = 0
                expected[category][metric] += val

    # Build expected JSON structure
    expected_json = {"period": "2023-Q3"}
    for cat in ["customer", "ops", "product"]:
        if expected[cat]:
            expected_json[cat] = expected[cat]
        # else leave empty dict -> agent may omit? We'll allow if agent includes empty categories

    # Compare
    # We'll score 60 points: 20 points for customer, 20 for ops, 20 for product
    cat_scores = {"customer": 20, "ops": 20, "product": 20}
    for cat, max_pts in cat_scores.items():
        actual_cat = data.get(cat, {})
        expected_cat = expected_json.get(cat, {})
        if isinstance(actual_cat, dict) and actual_cat == expected_cat:
            details.append({"item": f"{cat} 指标正确", "score": max_pts, "max_score": max_pts, "passed": True, "reason": f"匹配期望值: {expected_cat}"})
            total_score += max_pts
        else:
            # Partial credit possible if some metrics match
            matched = 0
            total_metrics = len(expected_cat)
            if total_metrics == 0 and actual_cat == {}:
                matched = 1
            else:
                for key, val in expected_cat.items():
                    if key in actual_cat and actual_cat[key] == val:
                        matched += 1
            if total_metrics > 0:
                partial = int(max_pts * matched / total_metrics)
            else:
                partial = max_pts if matched else 0
            details.append({"item": f"{cat} 指标正确", "score": partial, "max_score": max_pts, "passed": (partial == max_pts), "reason": f"期望: {expected_cat}, 实际: {actual_cat}"})
            total_score += partial

    # Ensure total_score capped at 100
    total_score = min(total_score, 100)
    write_score(details, total_score, workspace)

def write_score(details, total, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    main()
