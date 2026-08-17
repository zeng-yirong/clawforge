import sys
import os
import json
import csv
import re
import math

def verify(workspace):
    results = []
    total_score = 0

    # 1. 检查目录 cache 是否存在 (10分)
    cache_dir = os.path.join(workspace, "cache")
    if os.path.isdir(cache_dir):
        results.append({"item": "cache directory exists", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10
    else:
        results.append({"item": "cache directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "cache directory not found"})

    # 2. 检查文件 cache/business_report.md 是否存在 (10分)
    report_path = os.path.join(workspace, "cache", "business_report.md")
    if os.path.isfile(report_path):
        results.append({"item": "business_report.md exists", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10
    else:
        results.append({"item": "business_report.md exists", "score": 0, "max_score": 10, "passed": False, "reason": "report file missing"})
        # 如果文件不存在，直接返回
        # 但是为了继续其它项，我们仍尝试读取（会失败）
        report_content = ""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
    except:
        report_content = ""

    # 3. 检查文件内容是否包含Markdown表格 (10分)
    table_pattern = r'\|[^|]+\|[^|]+\|'  # 简单匹配至少一行表格
    if re.search(table_pattern, report_content):
        results.append({"item": "Markdown table present", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10
    else:
        results.append({"item": "Markdown table present", "score": 0, "max_score": 10, "passed": False, "reason": "no table found in report"})

    # 4. 检查表头是否包含 Metric Code 和 Value (10分)
    lines = report_content.strip().splitlines()
    header_found = False
    for line in lines:
        if 'Metric Code' in line and 'Value' in line:
            header_found = True
            break
    if header_found:
        results.append({"item": "table header contains Metric Code and Value", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10
    else:
        results.append({"item": "table header contains Metric Code and Value", "score": 0, "max_score": 10, "passed": False, "reason": "header missing required columns"})

    # 5. 提取表格行并验证 (45分 + 5分排序 + 5分行数 = 55分)
    # 期望的指标及其值（按metric_code字母序）
    expected = {
        "c_avg_order": 75.5,
        "c_count": 200,
        "c_revenue": 1500,
        "o_cost": 800,
        "o_latency": 12.5,
        "o_uptime": 99.98,
        "p_returns": 30,
        "p_sales": 3000,
        "p_units": 500
    }
    sorted_expected_codes = sorted(expected.keys())

    # 解析表格：找所有形如 | code | value | 的行（跳过分隔行）
    rows = []
    for line in lines:
        line = line.strip()
        if line.startswith('|') and line.endswith('|'):
            # 移除首尾|，按|分割
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:  # 至少 code 和 value
                rows.append(parts)
    # 过滤表头行和分隔行（如果包含---）
    data_rows = []
    for row in rows:
        # 跳过表头行
        if 'Metric Code' in row[1] or '---' in row[1]:
            continue
        if len(row) >= 3:
            code = row[1].strip()
            value_str = row[2].strip()
            # 尝试解析数值
            try:
                value = float(value_str)
                data_rows.append((code, value))
            except ValueError:
                pass
    # 按code排序
    data_rows.sort(key=lambda x: x[0])
    extracted_codes = [x[0] for x in data_rows]
    extracted_values = [x[1] for x in data_rows]

    # 5.1 行数正确性 (10分)
    row_count_expected = len(expected)
    if len(data_rows) == row_count_expected:
        results.append({"item": "number of metric rows", "score": 10, "max_score": 10, "passed": True, "reason": f"found {len(data_rows)} rows"})
        total_score += 10
    else:
        results.append({"item": "number of metric rows", "score": 0, "max_score": 10, "passed": False, "reason": f"expected {row_count_expected} rows, got {len(data_rows)}"})

    # 5.2 排序正确性 (5分)
    if extracted_codes == sorted_expected_codes:
        results.append({"item": "metric codes sorted alphabetically", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        total_score += 5
    else:
        results.append({"item": "metric codes sorted alphabetically", "score": 0, "max_score": 5, "passed": False, "reason": f"order mismatch, got {extracted_codes[:5]}..."})

    # 5.3 每个指标值的准确性 (每个5分，共45分)
    for code in sorted_expected_codes:
        expected_val = expected[code]
        # 从data_rows中找对应code
        found = None
        for c, v in data_rows:
            if c == code:
                found = v
                break
        if found is not None and math.isclose(found, expected_val, rel_tol=1e-6):
            results.append({"item": f"metric {code} value", "score": 5, "max_score": 5, "passed": True, "reason": f"value {found} matches {expected_val}"})
            total_score += 5
        else:
            results.append({"item": f"metric {code} value", "score": 0, "max_score": 5, "passed": False, "reason": f"expected {expected_val}, got {found}"})

    # 汇总
    total_score = min(total_score, 100)  # 防溢出
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
