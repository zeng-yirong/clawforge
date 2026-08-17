import sys
import os
import csv
import json
import re
from pathlib import Path

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
ws = Path(workspace)

def main():
    details = []
    total_score = 0

    # ----- 1. 目录结构检查 (10分) -----
    # 必须存在 reports/ 目录，且 reports/2024-Q1_summary.md 存在
    reports_dir = ws / "reports"
    target_file = reports_dir / "2024-Q1_summary.md"
    score = 0
    max_score = 10
    reason = ""
    if reports_dir.exists() and reports_dir.is_dir():
        if target_file.exists() and target_file.is_file():
            score = 10
            reason = "reports目录和目标报告文件存在"
        else:
            reason = "目标报告文件不存在"
    else:
        reason = "reports目录不存在"
    details.append({
        "item": "目录与文件存在",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reason
    })
    total_score += score

    # ----- 2. 格式合法性 (10分) -----
    # 读取Markdown文件，检查是否包含标题等基本结构
    score = 0
    max_score = 10
    reason = ""
    if target_file.exists():
        try:
            content = target_file.read_text(encoding="utf-8")
            # 检查是否以 # 开头（Markdown标题）
            lines = content.strip().split("\n")
            if lines and lines[0].strip().startswith("#"):
                score += 5
            # 检查是否包含表格（至少一个 '|'）
            if "|" in content:
                score += 5
            if score == 10:
                reason = "文件格式正确，包含标题和表格"
            else:
                reason = "缺少标题或表格"
        except Exception as e:
            reason = f"文件读取异常: {e}"
    else:
        reason = "文件不存在，无法检查格式"
    details.append({
        "item": "Markdown格式合法性",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reason
    })
    total_score += score

    # ----- 3. 数据清洗与聚合计算 (80分) -----
    # 读取三个账本文件（排除archive目录和干扰文件）
    ledgers_dir = ws / "data" / "ledgers"
    expected_ledgers = ["customer_ledger.csv", "product_ledger.csv", "ops_ledger.csv"]
    all_rows = []
    ledger_found = True
    for fname in expected_ledgers:
        fp = ledgers_dir / fname
        if not fp.exists():
            ledger_found = False
            break
    if not ledger_found:
        # 缺失账本文件，0分
        details.append({
            "item": "账本数据读取",
            "score": 0,
            "max_score": 80,
            "passed": False,
            "reason": "必要的账本文件缺失"
        })
        total_score += 0
        _write_score(total_score, details)
        return

    # 读取并清洗
    valid_metrics = {"revenue", "cost", "profit"}
    aggregated = {}  # metric_code -> sum
    for fname in expected_ledgers:
        fp = ledgers_dir / fname
        with open(fp, newline='') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None or header != ["period", "metric_code", "metric_value"]:
                continue
            for row in reader:
                if len(row) != 3:
                    continue
                period, code, val = row
                period = period.strip()
                code = code.strip()
                val = val.strip()
                # 过滤：仅保留 period == "2024-Q1"，metric_code 在有效集合内，val 为纯数字
                if period != "2024-Q1":
                    continue
                if code not in valid_metrics:
                    continue
                try:
                    numeric_val = int(val) if val.isdigit() else float(val)
                except ValueError:
                    continue
                # 检查是否为整数（题目设定都是整数）
                if not val.isdigit():
                    continue
                aggregated[code] = aggregated.get(code, 0) + numeric_val

    # 预期答案（基于env_builder的静态数据）：
    # customer: revenue=1000+500=1500, cost=400, profit=1100
    # product: revenue=2500, cost=1200, profit=1300 (注意：product中还有额外profit行? product中profit有两个1300? 检查：product_rows中有("2024-Q1","profit",1300)出现两次，所以product profit = 1300+1300=2600)
    # ops: revenue=3000+3000=6000? ops中有两行revenue: 3000和3000，所以revenue=6000; cost=1800; profit=1200
    # 合计：revenue = 1500+2500+6000 = 10000; cost = 400+1200+1800 = 3400; profit = 1100+2600+1200 = 4900
    expected = {
        "revenue": 10000,
        "cost": 3400,
        "profit": 4900
    }
    # 注意：可能还有别的metric如"revenu"、"profit"重复？我们按清洗后的结果对比
    # 检查报告文件中是否包含这些数值
    score = 0
    max_score = 80
    reason_parts = []
    # 从文件中提取数值
    try:
        content = target_file.read_text(encoding="utf-8")
        # 提取表格行，假设表格格式为 | metric | value |
        lines = content.split("\n")
        found_metrics = {}
        # 简单正则：匹配类似 | revenue | 10000 | 的行
        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                metric = parts[0].lower().strip()
                # 尝试解析数值
                val_str = parts[1].replace(",", "").replace("$", "").strip()
                try:
                    val = int(val_str)
                    if metric in valid_metrics:
                        found_metrics[metric] = val
                except ValueError:
                    continue
        # 比较
        correct_count = 0
        for metric, expected_val in expected.items():
            actual = found_metrics.get(metric)
            if actual == expected_val:
                correct_count += 1
                reason_parts.append(f"{metric}正确")
            else:
                reason_parts.append(f"{metric}期望{expected_val}，实际{actual}")
        if correct_count == 3:
            score = 80
            reason = "所有指标数值完全正确"
        else:
            score = correct_count * 25  # 每个指标25分
            reason = "; ".join(reason_parts)
    except Exception as e:
        reason = f"解析报告内容异常: {e}"
        score = 0

    details.append({
        "item": "指标聚合数值",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reason
    })
    total_score += score

    # 写结果
    _write_score(total_score, details)

def _write_score(total, details):
    result = {
        "total_score": min(total, 100),  # 保证不超过100
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
