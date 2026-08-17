import sys
import os
import json
import re
import csv

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. reports 目录
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        details.append({"item": "reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Reports directory present"})
        score += 10
    else:
        details.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing reports directory"})

    # 2. 报告文件
    report_path = os.path.join(workspace, "reports", "april_revenue_report.md")
    if os.path.isfile(report_path):
        details.append({"item": "april_revenue_report.md exists", "score": 10, "max_score": 10, "passed": True, "reason": "Report file present"})
        score += 10
    else:
        details.append({"item": "april_revenue_report.md exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing report file"})
        total_score = score
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 读取内容
    with open(report_path, "r") as f:
        content = f.read()

    # 4. 标题
    if "# April 2024 Revenue Summary" in content:
        details.append({"item": "Report title correct", "score": 10, "max_score": 10, "passed": True, "reason": "Title found"})
        score += 10
    else:
        details.append({"item": "Report title correct", "score": 0, "max_score": 10, "passed": False, "reason": "Missing title"})

    # 5. Total Revenue 行
    rev_match = re.search(r'Total Revenue\s*:\s*(\d+)', content)
    if rev_match:
        actual_total = int(rev_match.group(1))
        details.append({"item": "Total Revenue line present and numeric", "score": 10, "max_score": 10, "passed": True, "reason": f"Found Total Revenue: {actual_total}"})
        score += 10
    else:
        details.append({"item": "Total Revenue line present and numeric", "score": 0, "max_score": 10, "passed": False, "reason": "Missing or non-numeric Total Revenue"})
        actual_total = None

    # 6. Period 行
    if "**Period**: 2024-04" in content:
        details.append({"item": "Period line correct", "score": 5, "max_score": 5, "passed": True, "reason": "Period 2024-04 found"})
        score += 5
    else:
        details.append({"item": "Period line correct", "score": 0, "max_score": 5, "passed": False, "reason": "Period missing or wrong"})

    # 7. 计算期望值
    expected_total = 0
    for ledger_file in ["customer_ledger.csv", "product_ledger.csv", "ops_ledger.csv"]:
        ledger_path = os.path.join(workspace, "data", "ledgers", ledger_file)
        if not os.path.isfile(ledger_path):
            continue
        with open(ledger_path, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) < 3:
                    continue
                period, code, value_str = row[0].strip(), row[1].strip(), row[2].strip()
                if period == "2024-04" and code == "revenue":
                    try:
                        expected_total += int(value_str)
                    except (ValueError, TypeError):
                        continue

    # 8. 数值比对
    if actual_total is not None:
        if actual_total == expected_total:
            details.append({"item": "Total Revenue value matches expected", "score": 55, "max_score": 55, "passed": True, "reason": f"Expected {expected_total}, got {actual_total}"})
            score += 55
        else:
            details.append({"item": "Total Revenue value matches expected", "score": 0, "max_score": 55, "passed": False, "reason": f"Expected {expected_total}, got {actual_total}"})
    else:
        details.append({"item": "Total Revenue value matches expected", "score": 0, "max_score": 55, "passed": False, "reason": "Could not compare because actual value missing"})

    total_score = min(score, 100)
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
