import csv
import json
import os
import sys
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. 检查输出目录是否存在
    output_dir = ws / "output"
    if output_dir.is_dir():
        details.append({"item": "output目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "output目录已创建"})
        total_score += 10
    else:
        details.append({"item": "output目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "output目录不存在"})

    # 2. 检查region_avg.csv文件是否存在
    result_file = output_dir / "region_avg.csv"
    if result_file.is_file():
        details.append({"item": "region_avg.csv文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
        total_score += 10
    else:
        details.append({"item": "region_avg.csv文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续检查无法进行，直接返回
        score_obj = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score_obj, f, indent=2)
        return

    # 3. 检查CSV格式合法性
    try:
        with open(result_file, "r", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        details.append({"item": "CSV格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "能够正确解析CSV"})
        total_score += 10
    except Exception as e:
        details.append({"item": "CSV格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        score_obj = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score_obj, f, indent=2)
        return

    # 4. 检查表头
    expected_header = ["region", "avg_sales_amount"]
    if header == expected_header:
        details.append({"item": "CSV表头正确", "score": 10, "max_score": 10, "passed": True, "reason": f"表头为{expected_header}"})
        total_score += 10
    else:
        details.append({"item": "CSV表头正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{expected_header}，实际{header}"})

    # 5. 检查去重与补全后的记录数（原始10条，2条重复 → 8条；2条缺失region可查表补全；1条缺销售额 → 删除，最终7条）
    # 但这里我们不直接读原始数据，而是验证结果中的地区数及数值是否与预期一致。
    # 预期结果：根据env_builder构造的数据，经过正确处理后：
    # - 唯一订单：T001, T002, T003, T004, T005(T005缺失销售额应删除), T006, T007, T008 (T001和T003各有一条重复)
    # - 补全region：T001(product_id=P01 -> East), T003(product_id=P03 -> South)
    # - 删除T005(销售额为空)
    # 剩余订单：T001(East,120.5), T002(West,85.0), T003(South,300.0), T004(East,95.0), T006(North,250.0), T007(South,180.0), T008(West,95.5)
    # 分组平均值：
    # East: (120.5+95.0)/2 = 107.75
    # West: (85.0+95.5)/2 = 90.25
    # South: (300.0+180.0)/2 = 240.0
    # North: (250.0)/1 = 250.0
    expected = {
        "East": 107.75,
        "West": 90.25,
        "South": 240.0,
        "North": 250.0
    }
    # 解析结果
    result = {}
    try:
        for row in rows:
            if len(row) != 2:
                continue
            region, val = row[0].strip(), row[1].strip()
            result[region] = float(val)
    except Exception as e:
        details.append({"item": "数据解析", "score": 0, "max_score": 20, "passed": False, "reason": f"解析数值失败: {e}"})
        score_obj = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score_obj, f, indent=2)
        return

    # 检查区域数量
    if set(result.keys()) == set(expected.keys()):
        details.append({"item": "区域完整性", "score": 20, "max_score": 20, "passed": True, "reason": f"包含所有区域 {list(expected.keys())}"})
        total_score += 20
    else:
        missing = set(expected.keys()) - set(result.keys())
        extra = set(result.keys()) - set(expected.keys())
        reason = f"缺失{missing}，多余{extra}" if missing or extra else ""
        details.append({"item": "区域完整性", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 检查平均值精确性
    correct = True
    for region, avg in expected.items():
        if region in result:
            if abs(result[region] - avg) > 0.001:
                correct = False
                break
        else:
            correct = False
            break
    if correct:
        details.append({"item": "平均值计算准确", "score": 30, "max_score": 30, "passed": True, "reason": f"所有区域平均值与预期一致"})
        total_score += 30
    else:
        details.append({"item": "平均值计算准确", "score": 0, "max_score": 30, "passed": False, "reason": f"预期{expected}，实际{result}"})

    # 写入评分
    score_obj = {"total_score": total_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(score_obj, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
