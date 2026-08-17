import sys
import os
import json
import csv
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

def round_to_2(num):
    # 保留两位小数，四舍五入
    return float(Decimal(str(num)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目标目录和文件是否存在 (10分)
    expected_file = ws / "report" / "region_summary.csv"
    dir_exists = (ws / "report").is_dir()
    file_exists = expected_file.is_file()
    if dir_exists and file_exists:
        details.append({"item": "目录 report/ 存在且 region_summary.csv 存在", "score": 10, "max_score": 10, "passed": True, "reason": "目标文件存在"})
        total_score += 10
    else:
        missing = []
        if not dir_exists:
            missing.append("report/ 目录")
        if not file_exists:
            missing.append("report/region_summary.csv 文件")
        details.append({"item": "目录和文件存在检查", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失: {', '.join(missing)}"})
        # 文件不存在，剩余检查无法进行，直接输出结果
        result = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 检查 CSV 格式合法性 (10分)
    try:
        with open(expected_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if len(rows) < 2:
            raise ValueError("至少需要标题行和一行数据")
        header = rows[0]
        if header != ["region", "total_sales", "avg_sales"]:
            details.append({"item": "CSV 标题行正确", "score": 0, "max_score": 10, "passed": False, "reason": f"标题行应为 ['region','total_sales','avg_sales']，实际为 {header}"})
        else:
            details.append({"item": "CSV 标题行正确", "score": 10, "max_score": 10, "passed": True, "reason": "标题行匹配"})
            total_score += 10
    except Exception as e:
        details.append({"item": "CSV 可正常解析", "score": 0, "max_score": 10, "passed": False, "reason": f"文件无法解析为 CSV: {str(e)}"})
        # 后续解析无法进行，输出结果
        result = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查数据行数（应包含4个区域：North, South, East, West）(15分)
    data_rows = rows[1:]
    regions_found = set(row[0] for row in data_rows if len(row) >= 3)
    expected_regions = {"North", "South", "East", "West"}
    if regions_found != expected_regions:
        details.append({"item": "包含全部四个区域", "score": 0, "max_score": 15, "passed": False, "reason": f"缺少区域: {expected_regions - regions_found}, 多余区域: {regions_found - expected_regions}"})
    else:
        details.append({"item": "包含全部四个区域", "score": 15, "max_score": 15, "passed": True, "reason": "North, South, East, West 均出现"})
        total_score += 15

    # 4. 精确验证数值 (65分)
    # 根据 env_builder 生成的原始数据（去重后）计算期望结果
    # 原始记录（去重后）：
    # T001: North, 120.50
    # T002: South, 85.00
    # T003: East, 200.00
    # T004: West, 350.00
    # T005: North, 75.50
    # T006: South, 45.00
    # T007: East, 180.00
    # T008: West, 110.00
    # 计算：
    # North: total = 120.50+75.50 = 196.00, avg = 196.00/2 = 98.00
    # South: total = 85.00+45.00 = 130.00, avg = 130.00/2 = 65.00
    # East: total = 200.00+180.00 = 380.00, avg = 380.00/2 = 190.00
    # West: total = 350.00+110.00 = 460.00, avg = 460.00/2 = 230.00
    expected = {
        "North": {"total_sales": 196.00, "avg_sales": 98.00},
        "South": {"total_sales": 130.00, "avg_sales": 65.00},
        "East": {"total_sales": 380.00, "avg_sales": 190.00},
        "West": {"total_sales": 460.00, "avg_sales": 230.00},
    }
    numeric_ok = True
    numeric_score = 0
    # 每个区域细分：total 和 avg 各占大约 8.125分（65/8=8.125），但为了整数，我们分配 8 分每个共8项？但总65不好分，可以按区域4个，每个区域16.25分。我们简化为每个区域16分（total占8，avg占8），共64分，再补1分给整体格式。或直接每个区域共16分，共64分，再加1分总体格式（可在前面含入）。避免小数，我们设定每个区域16分（total 8, avg 8），共64，剩余1分放在整体格式（如没有多余行等）。实际我们将64分分配到8个字段，每个8分。
    # 更简单：每个区域 total_sales 8分，avg_sales 8分，共8*8=64，加上整体行数正确1分=65。
    # 但我们前面已分配15分行数检查，这里改为精确数值检查65分：每个区域16分（total8+avg8），共64，再加1分无多余行。
    for row in data_rows:
        if len(row) != 3:
            details.append({"item": "每行三列", "score": 0, "max_score": 1, "passed": False, "reason": "存在行数不是三列的"})
            numeric_ok = False
            continue
        region, total_s, avg_s = row
        try:
            t = float(total_s)
            a = float(avg_s)
        except:
            details.append({"item": f"区域 {region} 数值可转换", "score": 0, "max_score": 1, "passed": False, "reason": "数值无法转为浮点数"})
            numeric_ok = False
            continue
        if region in expected:
            exp = expected[region]
            t_ok = round_to_2(t) == round_to_2(exp["total_sales"])
            a_ok = round_to_2(a) == round_to_2(exp["avg_sales"])
            if t_ok and a_ok:
                details.append({"item": f"区域 {region} 数值正确", "score": 16, "max_score": 16, "passed": True, "reason": f"total_sales={total_s}, avg_sales={avg_s}"})
                numeric_score += 16
            else:
                details.append({"item": f"区域 {region} 数值错误", "score": 0, "max_score": 16, "passed": False, "reason": f"预期 total={exp['total_sales']}, avg={exp['avg_sales']}; 实际 total={total_s}, avg={avg_s}"})
                numeric_ok = False
        else:
            details.append({"item": f"多余区域 {region}", "score": 0, "max_score": 1, "passed": False, "reason": "出现了预期外的区域"})
            numeric_ok = False
    # 检查是否有多余行（比如重复区域）
    if len(data_rows) != 4:
        details.append({"item": "数据行数恰好为4", "score": 0, "max_score": 1, "passed": False, "reason": f"实际行数 {len(data_rows)}，预期4"})
    else:
        details.append({"item": "数据行数恰好为4", "score": 1, "max_score": 1, "passed": True, "reason": "4行数据"})
        numeric_score += 1
    total_score += numeric_score

    # 累加数值检查得分
    # 注意：details中添加了多项，但numeric_score变量已经累加16*4+1=65如果全部正确
    result = {"total_score": total_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
