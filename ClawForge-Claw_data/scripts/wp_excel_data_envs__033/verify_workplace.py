import csv
import json
import math
import sys
import os

def verify(workspace: str):
    details = []
    total_score = 0

    # ----- 1. 检查目录结构 (10分) -----
    csv_path = os.path.join(workspace, "cleaned_data.csv")
    json_path = os.path.join(workspace, "region_summary.json")
    csv_exists = os.path.isfile(csv_path)
    json_exists = os.path.isfile(json_path)
    if csv_exists:
        details.append({"item": "cleaned_data.csv 存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
    else:
        details.append({"item": "cleaned_data.csv 存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件未找到"})
    if json_exists:
        details.append({"item": "region_summary.json 存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
    else:
        details.append({"item": "region_summary.json 存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件未找到"})

    if not (csv_exists and json_exists):
        # 后续检查无法进行，直接返回
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ----- 2. 格式合法性 & 基础解析 (10分) -----
    # CSV 解析
    try:
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            cleaned_rows = list(reader)
        csv_valid = True
        csv_row_count = len(cleaned_rows)
    except Exception as e:
        csv_valid = False
        csv_row_count = 0

    if csv_valid and csv_row_count > 0:
        details.append({"item": "cleaned_data.csv 格式合法", "score": 5, "max_score": 5, "passed": True, "reason": f"解析成功，共 {csv_row_count} 行"})
        total_score += 5
    else:
        details.append({"item": "cleaned_data.csv 格式合法", "score": 0, "max_score": 5, "passed": False, "reason": f"解析失败或为空: {str(e) if not csv_valid else '空文件'}"})

    # JSON 解析
    try:
        with open(json_path) as f:
            region_summary = json.load(f)
        json_valid = isinstance(region_summary, dict)
    except Exception as e:
        json_valid = False

    if json_valid:
        details.append({"item": "region_summary.json 格式合法", "score": 5, "max_score": 5, "passed": True, "reason": "JSON 解析成功，为字典"})
        total_score += 5
    else:
        details.append({"item": "region_summary.json 格式合法", "score": 0, "max_score": 5, "passed": False, "reason": "JSON 解析失败或类型错误"})
        # 后续计算无法进行
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ----- 3. 去重正确性 (20分) -----
    # 预期唯一行数 = 10 (原始10条，重复被去除)
    expected_row_count = 10
    if csv_row_count == expected_row_count:
        details.append({"item": "去重后行数正确", "score": 10, "max_score": 10, "passed": True, "reason": f"行数为{expected_row_count}"})
        total_score += 10
    else:
        details.append({"item": "去重后行数正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望{expected_row_count}行，实际{csv_row_count}行"})

    # 检查是否有重复的 transaction_id (不允许重复)
    transaction_ids = [r.get("transaction_id", "") for r in cleaned_rows]
    if len(transaction_ids) == len(set(transaction_ids)):
        details.append({"item": "事务ID无重复", "score": 5, "max_score": 5, "passed": True, "reason": "所有 transaction_id 唯一"})
        total_score += 5
    else:
        details.append({"item": "事务ID无重复", "score": 0, "max_score": 5, "passed": False, "reason": "存在重复 transaction_id"})
    # 检查是否包含原始10条中的每条（通过 transaction_id 集合）
    expected_ids = {"T001","T002","T003","T004","T005","T006","T007","T008","T009","T010"}
    actual_ids = set(transaction_ids)
    if actual_ids == expected_ids:
        details.append({"item": "包含所有原始事务", "score": 5, "max_score": 5, "passed": True, "reason": "包含正确的10个事务ID"})
        total_score += 5
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        details.append({"item": "包含所有原始事务", "score": 0, "max_score": 5, "passed": False, "reason": f"缺失 {missing}, 多余 {extra}"})

    # ----- 4. 缺失值填充正确性 (20分) -----
    # 构建一个查询字典 transaction_id -> row
    row_map = {r.get("transaction_id", ""): r for r in cleaned_rows}

    def check_field(tid, field, expected, max_score, item_desc):
        nonlocal total_score
        row = row_map.get(tid)
        if not row:
            details.append({"item": item_desc, "score": 0, "max_score": max_score, "passed": False, "reason": f"未找到事务 {tid}"})
            return
        actual = row.get(field, "").strip()
        if actual == str(expected):
            details.append({"item": item_desc, "score": max_score, "max_score": max_score, "passed": True, "reason": f"正确: {field}={actual}"})
            total_score += max_score
        else:
            details.append({"item": item_desc, "score": 0, "max_score": max_score, "passed": False, "reason": f"期望 {field}={expected}，实际={actual}"})

    # T004: customer_name 应为 Alice Johnson, sales_amount 应为 0
    check_field("T004", "customer_name", "Alice Johnson", 5, "T004 客户名填充")
    check_field("T004", "sales_amount", "0", 5, "T004 销售额填充")
    # T005: customer_name 应为 Bob Smith, sales_amount 应为 0
    check_field("T005", "customer_name", "Bob Smith", 5, "T005 客户名填充")
    check_field("T005", "sales_amount", "0", 5, "T005 销售额填充")

    # ----- 5. 汇总计算正确性 (40分) -----
    # 预期汇总值（使用 Decimal 精确计算）
    from decimal import Decimal, getcontext
    getcontext().prec = 10

    expected_summary = {
        "North": {"total_revenue": Decimal("300.50"), "average_order": Decimal("100.16666666666667")},  # 100.50+0+200.00
        "South": {"total_revenue": Decimal("277.00"), "average_order": Decimal("92.33333333333333")},   # 250+12+15
        "East":  {"total_revenue": Decimal("45.00"), "average_order": Decimal("22.5")},                 # 45+0
        "West":  {"total_revenue": Decimal("30.00"), "average_order": Decimal("15.0")}                  # 0+30
    }

    for region, expected in expected_summary.items():
        # 检查 region 是否存在
        if region not in region_summary:
            details.append({"item": f"汇总存在区域 {region}", "score": 0, "max_score": 5, "passed": False, "reason": "区域不存在"})
            continue
        actual = region_summary[region]
        # 检查 total_revenue
        total_field = "total_revenue"
        if total_field not in actual:
            details.append({"item": f"{region} total_revenue 字段", "score": 0, "max_score": 5, "passed": False, "reason": "字段缺失"})
            continue
        try:
            actual_total = Decimal(str(actual[total_field]))
        except:
            details.append({"item": f"{region} total_revenue 字段", "score": 0, "max_score": 5, "passed": False, "reason": "数值无法转换"})
            continue
        if actual_total == expected["total_revenue"]:
            details.append({"item": f"{region} total_revenue", "score": 5, "max_score": 5, "passed": True, "reason": f"正确: {actual_total}"})
            total_score += 5
        else:
            details.append({"item": f"{region} total_revenue", "score": 0, "max_score": 5, "passed": False, "reason": f"期望 {expected['total_revenue']}，实际 {actual_total}"})

        # 检查 average_order
        avg_field = "average_order"
        if avg_field not in actual:
            details.append({"item": f"{region} average_order 字段", "score": 0, "max_score": 5, "passed": False, "reason": "字段缺失"})
            continue
        try:
            actual_avg = Decimal(str(actual[avg_field]))
        except:
            details.append({"item": f"{region} average_order 字段", "score": 0, "max_score": 5, "passed": False, "reason": "数值无法转换"})
            continue
        # 允许浮点误差 1e-6
        if math.isclose(float(actual_avg), float(expected["average_order"]), rel_tol=1e-6):
            details.append({"item": f"{region} average_order", "score": 5, "max_score": 5, "passed": True, "reason": f"正确: {actual_avg}"})
            total_score += 5
        else:
            details.append({"item": f"{region} average_order", "score": 0, "max_score": 5, "passed": False, "reason": f"期望 {expected['average_order']}，实际 {actual_avg}"})

    # 写入评分
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
