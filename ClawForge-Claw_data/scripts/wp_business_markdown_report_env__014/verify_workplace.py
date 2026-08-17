import sys
import os
import json
import re

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. 检查 ops/ 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops/ 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "ops/ 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ops/ 目录"})
    
    # 2. 检查 quarterly_report.md 文件存在 (20分)
    report_path = os.path.join(workspace, "ops", "quarterly_report.md")
    if os.path.isfile(report_path):
        details.append({"item": "quarterly_report.md 文件存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在"})
        total_score += 20
    else:
        details.append({"item": "quarterly_report.md 文件存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        # 后续检查跳过
        return {"total_score": total_score, "details": details}

    # 3. 读取文件内容，检查是否为合法 Markdown (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        if content.strip():
            details.append({"item": "文件可读且非空 (合法Markdown)", "score": 10, "max_score": 10, "passed": True, "reason": "内容非空"})
            total_score += 10
        else:
            details.append({"item": "文件可读且非空", "score": 0, "max_score": 10, "passed": False, "reason": "文件为空"})
            return {"total_score": total_score, "details": details}
    except Exception as e:
        details.append({"item": "文件可读且非空", "score": 0, "max_score": 10, "passed": False, "reason": f"读取失败: {e}"})
        return {"total_score": total_score, "details": details}

    # 4. 解析 Markdown 表格，提取数据行 (20分)
    lines = content.splitlines()
    data_rows = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            # 跳过表头行（包含 period, metric, value）
            if "period" in stripped.lower() and "metric" in stripped.lower():
                in_table = True
                continue
            if in_table and stripped.replace("-","").replace("|","").strip() == "":
                # 分隔行
                continue
            if in_table:
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                if len(cells) >= 3:
                    data_rows.append(cells)
    if len(data_rows) >= 3:
        details.append({"item": "表格解析成功，包含足够数据行", "score": 20, "max_score": 20, "passed": True, "reason": f"找到 {len(data_rows)} 行"})
        total_score += 20
    else:
        details.append({"item": "表格解析成功，包含足够数据行", "score": 0, "max_score": 20, "passed": False, "reason": f"数据行不足（{len(data_rows)}）"})
        return {"total_score": total_score, "details": details}

    # 5. 计算指标总和，并验证是否等于208 (30分)
    computed_sum = 0
    valid_rows = 0
    expected_sum = 208
    for cells in data_rows:
        period = cells[0].strip()
        if period != "2025-Q1":
            continue
        try:
            val = int(cells[2])
            computed_sum += val
            valid_rows += 1
        except (ValueError, IndexError):
            continue
    if computed_sum == expected_sum and valid_rows >= 5:
        details.append({"item": "数值提取与总和计算", "score": 30, "max_score": 30, "passed": True, "reason": f"累加和为 {computed_sum}，预期 {expected_sum}"})
        total_score += 30
    else:
        details.append({"item": "数值提取与总和计算", "score": 0, "max_score": 30, "passed": False, "reason": f"累加和 {computed_sum}≠{expected_sum}，有效行 {valid_rows}"})
        return {"total_score": total_score, "details": details}

    # 6. 检查报告中是否有明确的 Total 行且数值正确 (20分)
    total_pattern = re.compile(r'(?i)total\s*[:\-]?\s*(\d+)')
    totals_found = total_pattern.findall(content)
    if totals_found:
        last_total = int(totals_found[-1])
        if last_total == expected_sum:
            details.append({"item": "报告中 Total 行数值正确", "score": 20, "max_score": 20, "passed": True, "reason": f"Total: {last_total}"})
            total_score += 20
        else:
            details.append({"item": "报告中 Total 行数值正确", "score": 10, "max_score": 20, "passed": False, "reason": f"Total 数值为 {last_total}，预期 {expected_sum}"})
            total_score += 10
    else:
        details.append({"item": "报告中 Total 行数值正确", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 Total 行"})
    
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
