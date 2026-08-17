import sys
import os
import json
import csv
import re
from pathlib import Path
from decimal import Decimal, InvalidOperation

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace).resolve()
    details = []
    total_score = 0
    max_total = 100

    # ---- 1. 检查报告文件是否存在 (10分) ----
    report_path = ws / "reports" / "q1_report.md"
    if report_path.exists():
        details.append({
            "item": "报告文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "reports/q1_report.md 存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "报告文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "找不到 reports/q1_report.md"
        })
        # 如果文件不存在，后续检查无法进行，直接输出结果
        _write_score(total_score, details)
        return

    # ---- 2. 解析 Markdown 表格 (10分) ----
    content = report_path.read_text(encoding="utf-8")
    # 期望表格结构： | Metric Code | Total Value | Status |
    # 提取所有表格行 (从 | 开始到 | 结束)
    lines = content.splitlines()
    table_rows = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            # 过滤仅含分隔符的线 (如 |---|---|---|---|)
            if re.match(r'^\|[\s\-:]+\|$', stripped):
                continue
            table_rows.append(stripped)
    if len(table_rows) < 3:
        details.append({
            "item": "表格行数足够",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"表格行数仅 {len(table_rows)}，无法提取有效数据"
        })
        _write_score(total_score, details)
        return
    # 通常第一行是表头，第二行是分隔线，第三行起是数据
    # 尝试找到表头行: 包含 Metric Code
    header_idx = None
    for i, row in enumerate(table_rows):
        if "metric code" in row.lower() or "metric_code" in row.lower():
            header_idx = i
            break
    if header_idx is None:
        details.append({
            "item": "表格包含正确表头",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到包含 'Metric Code' 的表头行"
        })
        _write_score(total_score, details)
        return
    # 数据行从 header_idx + 2 开始 (跳过分隔线)
    data_start = header_idx + 2
    if data_start >= len(table_rows):
        details.append({
            "item": "表格有数据行",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "表头后没有数据行"
        })
        _write_score(total_score, details)
        return
    # 解析每一行
    parsed_metrics = {}
    for row in table_rows[data_start:]:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) < 3:
            continue
        metric_code = cells[0].strip()
        total_value_str = cells[1].strip()
        status = cells[2].strip() if len(cells) > 2 else ""
        # 尝试转为 Decimal
        try:
            total_value = Decimal(total_value_str)
        except InvalidOperation:
            total_value = None
        if metric_code and total_value is not None:
            parsed_metrics[metric_code] = {"value": total_value, "status": status}
    if len(parsed_metrics) == 0:
        details.append({
            "item": "解析出有效指标",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未能从表格中解析出任何 metric_code 及其数值"
        })
        _write_score(total_score, details)
        return
    else:
        details.append({
            "item": "解析出有效指标",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"解析出 {len(parsed_metrics)} 个指标"
        })
        total_score += 10

    # ---- 3. 检查数值正确性 (50分) ----
    # 预期正确结果 (根据 env_builder 数据计算)
    # 注意: 重复行只计一次，无效行忽略
    # customer: revenue(1000), cost(500无效值忽略), profit(300)
    # ops: uptime(99.9), errors(5)
    # product: revenue(2000), units(150)
    # 合并后: revenue=1000+2000=3000, cost=500, profit=300, uptime=99.9, errors=5, units=150
    expected = {
        "revenue": Decimal("3000"),
        "cost": Decimal("500"),
        "profit": Decimal("300"),
        "uptime": Decimal("99.9"),
        "errors": Decimal("5"),
        "units": Decimal("150"),
    }
    correct_values = 0
    for metric, exp_val in expected.items():
        if metric not in parsed_metrics:
            continue
        val = parsed_metrics[metric]["value"]
        if val == exp_val:
            correct_values += 1
    value_score = int(round((correct_values / len(expected)) * 50))
    details.append({
        "item": "数值正确性",
        "score": value_score,
        "max_score": 50,
        "passed": value_score == 50,
        "reason": f"正确指标数: {correct_values}/{len(expected)}"
    })
    total_score += value_score

    # ---- 4. 检查状态标注 (20分) ----
    # 预期状态:
    # revenue: 有重复行 (customer 中重复), 应标 "Duplicate" 或类似
    # cost: 有无效值行, 应标 "Invalid" 或类似
    # profit: 无异常, 应标 "Valid" 或 "OK"
    # uptime: 有重复行, 标 "Duplicate"
    # errors: 无异常, 标 "Valid"
    # units: 无异常, 标 "Valid"
    expected_status = {
        "revenue": "duplicate",   # 只要包含 "duplicate" (大小写)
        "cost": "invalid",
        "profit": "valid",
        "uptime": "duplicate",
        "errors": "valid",
        "units": "valid",
    }
    correct_status = 0
    for metric, exp_key in expected_status.items():
        if metric not in parsed_metrics:
            continue
        status = parsed_metrics[metric]["status"].lower()
        if exp_key in status:
            correct_status += 1
    status_score = int(round((correct_status / len(expected_status)) * 20))
    details.append({
        "item": "状态标注正确性",
        "score": status_score,
        "max_score": 20,
        "passed": status_score == 20,
        "reason": f"正确状态数: {correct_status}/{len(expected_status)}"
    })
    total_score += status_score

    # ---- 5. 额外扣分项：多出无关指标不扣分，但若缺少必要指标扣分 (已在数值中体现) ----
    # 没有其他检查项了

    # 汇总
    total_score = min(total_score, 100)  # 上限
    _write_score(total_score, details)

def _write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
