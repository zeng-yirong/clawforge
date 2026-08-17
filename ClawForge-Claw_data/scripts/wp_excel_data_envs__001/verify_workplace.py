import json
import csv
import math
import sys
import os
from collections import OrderedDict

def load_csv(workspace):
    path = os.path.join(workspace, "data", "raw_sales.csv")
    if not os.path.exists(path):
        return None, f"Missing {path}"
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows, None

def compute_expected(rows):
    # 1. 去重（按整行去重，保留首次出现的）
    seen = set()
    unique_rows = []
    for row in rows:
        # 用排序后的键值对元组作为唯一标识（忽略行顺序）
        key = tuple(row.items())
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)
    # 2. 过滤无效：金额不能为空/负数/无法转浮点
    valid_rows = []
    for row in unique_rows:
        amount_str = row.get("sales_amount", "").strip()
        if amount_str == "":
            continue
        try:
            amount = float(amount_str)
        except ValueError:
            continue
        if amount <= 0:
            continue
        # discount 必须是有效整数
        disc_str = row.get("discount", "").strip()
        if disc_str == "":
            continue
        try:
            disc = int(disc_str)
        except ValueError:
            continue
        if disc < 0 or disc > 100:
            continue
        valid_rows.append(row)
    # 3. 计算每个类别的平均折扣后价格
    category_groups = {}
    for row in valid_rows:
        category = row.get("category", "").strip()
        if category == "":
            continue
        amount = float(row["sales_amount"])
        disc = int(row["discount"])
        discounted = amount * (1 - disc / 100.0)
        category_groups.setdefault(category, []).append(discounted)
    expected = {}
    for cat, vals in category_groups.items():
        expected[cat] = sum(vals) / len(vals)
    return expected

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 检查输出文件
    output_path = os.path.join(workspace, "products_avg.json")
    if not os.path.exists(output_path):
        score_details.append({
            "item": "products_avg.json exists",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "File not found"
        })
        total_score += 0
    else:
        score_details.append({
            "item": "products_avg.json exists",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "File exists"
        })
        total_score += 10

        # 解析 JSON
        try:
            with open(output_path) as f:
                result = json.load(f)
        except (json.JSONDecodeError, ValueError):
            score_details.append({
                "item": "JSON format valid",
                "score": 0, "max_score": 10, "passed": False,
                "reason": "Invalid JSON"
            })
            total_score += 0
            print(json.dumps({"total_score": total_score, "details": score_details}))
            return

        score_details.append({
            "item": "JSON format valid",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "Valid JSON"
        })
        total_score += 10

        # 检查是否为字典
        if not isinstance(result, dict):
            score_details.append({
                "item": "Result is a dictionary",
                "score": 0, "max_score": 10, "passed": False,
                "reason": f"Expected dict, got {type(result).__name__}"
            })
            total_score += 0
        else:
            score_details.append({
                "item": "Result is a dictionary",
                "score": 10, "max_score": 10, "passed": True,
                "reason": "Is dict"
            })
            total_score += 10

            # 计算预期结果
            rows, err = load_csv(workspace)
            if err:
                score_details.append({
                    "item": "Raw data accessible",
                    "score": 0, "max_score": 10, "passed": False,
                    "reason": err
                })
                total_score += 0
            else:
                score_details.append({
                    "item": "Raw data accessible",
                    "score": 10, "max_score": 10, "passed": True,
                    "reason": "Loaded raw_sales.csv"
                })
                total_score += 10

                expected = compute_expected(rows)
                expected_keys = set(expected.keys())
                actual_keys = set(result.keys())
                if expected_keys != actual_keys:
                    missing = expected_keys - actual_keys
                    extra = actual_keys - expected_keys
                    score_details.append({
                        "item": "Category keys match",
                        "score": 0, "max_score": 20, "passed": False,
                        "reason": f"Missing keys: {missing}, Extra keys: {extra}"
                    })
                    total_score += 0
                else:
                    score_details.append({
                        "item": "Category keys match",
                        "score": 20, "max_score": 20, "passed": True,
                        "reason": "All category keys present"
                    })
                    total_score += 20

                    # 逐个检查数值
                    for cat in expected:
                        expected_val = expected[cat]
                        actual_val = result[cat]
                        if isinstance(actual_val, (int, float)):
                            if math.isclose(expected_val, actual_val, rel_tol=1e-9):
                                score_details.append({
                                    "item": f"Value for '{cat}'",
                                    "score": 20, "max_score": 20, "passed": True,
                                    "reason": f"Expected {expected_val}, got {actual_val}"
                                })
                                total_score += 20
                            else:
                                score_details.append({
                                    "item": f"Value for '{cat}'",
                                    "score": 0, "max_score": 20, "passed": False,
                                    "reason": f"Expected {expected_val}, got {actual_val}"
                                })
                                total_score += 0
                        else:
                            score_details.append({
                                "item": f"Value for '{cat}'",
                                "score": 0, "max_score": 20, "passed": False,
                                "reason": f"Value is not numeric: {actual_val}"
                            })
                            total_score += 0

    # 输出结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    print(f"Total score: {total_score}/100")

if __name__ == "__main__":
    main()
