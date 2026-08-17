import sys
import os
import csv
import json
from collections import defaultdict

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 1) 检查结果目录和文件是否存在 (10分)
    result_path = os.path.join(workspace, "results", "averages.json")
    if os.path.isfile(result_path):
        details.append({
            "item": "结果文件存在 (results/averages.json)",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "文件存在"
        })
        score += 10
    else:
        details.append({
            "item": "结果文件存在 (results/averages.json)",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，直接结束
        finalize(score, max_score, details)
        return

    # 2) 解析 JSON 并验证结构 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            details.append({
                "item": "JSON 可解析且为字典",
                "score": 10, "max_score": 10, "passed": True,
                "reason": "符合要求"
            })
            score += 10
        else:
            details.append({
                "item": "JSON 可解析且为字典",
                "score": 0, "max_score": 10, "passed": False,
                "reason": "JSON 不是字典类型"
            })
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 可解析且为字典",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        finalize(score, max_score, details)
        return

    # 3) 读取原始数据并计算期望结果 (过程隐含：去重 + 填充缺失金额)
    try:
        # 读取 products 价目表
        products = {}
        with open(os.path.join(workspace, "raw_data", "products.csv"), newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                products[row["product_id"]] = float(row["standard_price"])

        # 读取 sales.csv
        sales_rows = []
        with open(os.path.join(workspace, "raw_data", "sales.csv"), newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sales_rows.append(row)

        # 去重（完全相同的行视为重复，保留第一个）
        seen = set()
        unique_rows = []
        for row in sales_rows:
            row_tuple = tuple(row.values())
            if row_tuple not in seen:
                seen.add(row_tuple)
                unique_rows.append(row)

        # 填充缺失金额并分组
        amounts_by_product = defaultdict(list)
        for row in unique_rows:
            amount_str = row["sales_amount"].strip()
            if amount_str == "":
                pid = row["product_id"]
                if pid in products:
                    amount = products[pid]
                else:
                    # 没有价目表则跳过（不影响数据，但 agent 应填充，若不填充则结果错误）
                    continue
            else:
                amount = float(amount_str)
            amounts_by_product[row["product_id"]].append(amount)

        # 计算平均值
        expected = {}
        for pid, vals in amounts_by_product.items():
            expected[pid] = sum(vals) / len(vals)

    except Exception as e:
        details.append({
            "item": "原始数据读取与计算",
            "score": 0, "max_score": 50, "passed": False,
            "reason": f"计算预期值时出错: {str(e)}"
        })
        finalize(score, max_score, details)
        return

    # 4) 检查键的集合 (20分：正确键15分，无多余键5分)
    expected_keys = set(expected.keys())
    actual_keys = set(data.keys())
    key_score = 0
    key_reason = ""
    # 检查是否包含所有期望键
    if expected_keys.issubset(actual_keys):
        key_score += 15
        key_reason = "包含所有必要产品"
    else:
        missing = expected_keys - actual_keys
        key_score += 0
        key_reason = f"缺少键: {missing}"
    # 检查是否有额外键
    extra = actual_keys - expected_keys
    if extra:
        key_reason += f" 额外键: {extra}"
        # 不扣分，但提示
    else:
        key_score += 5
        key_reason += " 无多余键"
    details.append({
        "item": "产品键完整性",
        "score": key_score, "max_score": 20, "passed": key_score == 20,
        "reason": key_reason
    })
    score += key_score

    # 5) 检查每个键的值精确匹配 (50分)
    value_score = 0
    value_reason = ""
    value_max = 50
    passed_all = True
    for pid in expected_keys:
        exp_val = expected[pid]
        act_val = data.get(pid)
        if act_val is None:
            passed_all = False
            value_reason += f"{pid}缺失; "
            continue
        # 允许浮点误差 1e-9
        if abs(act_val - exp_val) < 1e-9:
            value_score += value_max / len(expected_keys)  # 均匀分配，这里平均每个25分
        else:
            passed_all = False
            value_reason += f"{pid}期望{exp_val}，实际{act_val}; "
    if value_reason == "":
        value_reason = "所有值精确匹配"
    details.append({
        "item": "平均值数值准确",
        "score": round(value_score),
        "max_score": value_max,
        "passed": passed_all,
        "reason": value_reason
    })
    score += round(value_score)

    finalize(score, max_score, details)

def finalize(score, max_score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"总分: {score}/{max_score}")

if __name__ == "__main__":
    main()
