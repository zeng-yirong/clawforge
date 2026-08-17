import sys
import json
import csv
import os
from decimal import Decimal, ROUND_HALF_UP

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })
        # 如果目录不存在，后续检查直接跳过
        # 但为了完整性，继续检查文件存在性（文件路径中会包含目录）
        # 将文件存在性判断为失败
        result_path = os.path.join(workspace, "ops", "average_sales.json")
        if not os.path.isfile(result_path):
            score_details.append({
                "item": "average_sales.json exists",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "File not found because ops/ directory missing"
            })
            # 直接返回，因为无法继续
            final_score = total_score
            write_result(workspace, final_score, score_details)
            return

    # 2. 检查文件存在
    result_path = os.path.join(workspace, "ops", "average_sales.json")
    if os.path.isfile(result_path):
        score_details.append({
            "item": "average_sales.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "average_sales.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 无法继续，写结果返回
        final_score = total_score
        write_result(workspace, final_score, score_details)
        return

    # 3. 解析 JSON 合法性
    try:
        with open(result_path, "r") as f:
            agent_result = json.load(f)
        if not isinstance(agent_result, dict):
            raise ValueError("JSON root is not a dict")
        score_details.append({
            "item": "JSON format valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON object"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "JSON format valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        final_score = total_score
        write_result(workspace, final_score, score_details)
        return

    # 4. 读取原始数据并计算期望值
    data_path = os.path.join(workspace, "data", "raw_data", "sales_raw.csv")
    if not os.path.isfile(data_path):
        score_details.append({
            "item": "Raw data source exists",
            "score": 0,
            "max_score": 0,  # 不扣分，但无法计算；视为错误环境
            "passed": False,
            "reason": "Raw data file missing, cannot compute expected values"
        })
        final_score = total_score
        write_result(workspace, final_score, score_details)
        return

    # 去重：以整行元组为唯一标识
    unique_rows = set()
    category_sums = {}
    category_counts = {}
    with open(data_path, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)  # 跳过表头
        # 确定 category 和 sales_amount 的列索引
        try:
            cat_idx = header.index("category")
            amt_idx = header.index("sales_amount")
        except ValueError as e:
            score_details.append({
                "item": "Raw data headers valid",
                "score": 0,
                "max_score": 0,
                "passed": False,
                "reason": f"Missing expected column: {str(e)}"
            })
            final_score = total_score
            write_result(workspace, final_score, score_details)
            return

        for row in reader:
            if len(row) < max(cat_idx, amt_idx) + 1:
                continue  # 跳过不完整行
            row_tuple = tuple(row)
            if row_tuple in unique_rows:
                continue  # 跳过重复
            unique_rows.add(row_tuple)
            category = row[cat_idx].strip()
            try:
                amount = float(row[amt_idx])
            except ValueError:
                continue  # 忽略非数值
            category_sums[category] = category_sums.get(category, 0) + amount
            category_counts[category] = category_counts.get(category, 0) + 1

    # 计算期望平均值（四舍五入到两位小数）
    expected = {}
    for cat in category_sums:
        avg = category_sums[cat] / category_counts[cat]
        # 使用 Decimal 确保正确舍入
        avg_dec = Decimal(str(avg)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        expected[cat] = float(avg_dec)  # 转为 float 方便比较（但注意精度）
    
    # 5. 检查键集合是否完全一致
    agent_keys = set(agent_result.keys())
    expected_keys = set(expected.keys())
    if agent_keys == expected_keys:
        score_details.append({
            "item": "Category keys match expected set",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Keys exactly match: {sorted(expected_keys)}"
        })
        total_score += 10
    else:
        missing = expected_keys - agent_keys
        extra = agent_keys - expected_keys
        reason_parts = []
        if missing:
            reason_parts.append(f"missing keys: {sorted(missing)}")
        if extra:
            reason_parts.append(f"extra keys: {sorted(extra)}")
        score_details.append({
            "item": "Category keys match expected set",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })

    # 6. 逐个检查平均值（每个category 20分，共60分）
    cat_score_weight = 20  # 每个20分
    max_cat_score = len(expected_keys) * cat_score_weight
    cat_passed = 0
    for cat in expected_keys:
        expected_val = expected[cat]
        agent_val = agent_result.get(cat)
        if agent_val is None:
            score_details.append({
                "item": f"Average for category '{cat}'",
                "score": 0,
                "max_score": cat_score_weight,
                "passed": False,
                "reason": f"Missing key"
            })
            continue
        # 比较是否近似相等（允许浮点误差，但期望值是精确的两位小数）
        # 使用 round(agent_val, 2) 与 expected_val 比较
        if round(agent_val, 2) == expected_val:
            score_details.append({
                "item": f"Average for category '{cat}'",
                "score": cat_score_weight,
                "max_score": cat_score_weight,
                "passed": True,
                "reason": f"Expected {expected_val}, got {agent_val}"
            })
            cat_passed += cat_score_weight
        else:
            score_details.append({
                "item": f"Average for category '{cat}'",
                "score": 0,
                "max_score": cat_score_weight,
                "passed": False,
                "reason": f"Expected {expected_val}, got {agent_val}"
            })
    total_score += cat_passed

    # 写入结果
    write_result(workspace, total_score, score_details)

def write_result(workspace, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
