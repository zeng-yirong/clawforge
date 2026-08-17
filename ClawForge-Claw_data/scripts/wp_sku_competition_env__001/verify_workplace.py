import sys
import os
import json
import csv
from pathlib import Path

def check_file_exists(workspace, relative_path, description):
    full_path = os.path.join(workspace, relative_path)
    exists = os.path.isfile(full_path)
    return exists, full_path

def load_json(workspace, relative_path):
    full_path = os.path.join(workspace, relative_path)
    if not os.path.isfile(full_path):
        return None
    with open(full_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def evaluate():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构存在性 (10分)
    dirs_to_check = ["outputs"]
    for d in dirs_to_check:
        exists = os.path.isdir(os.path.join(workspace, d))
        passed = exists
        score = 5 if passed else 0
        total_score += score
        details.append({
            "item": f"Directory '{d}' exists",
            "score": score,
            "max_score": 5,
            "passed": passed,
            "reason": "Directory found" if passed else f"Missing directory: {d}"
        })

    # 2. 报告文件存在 (10分)
    report_rel = "outputs/competition_report.json"
    exists, full_path = check_file_exists(workspace, report_rel, "Competition report")
    passed = exists
    score = 10 if passed else 0
    total_score += score
    details.append({
        "item": f"File '{report_rel}' exists",
        "score": score,
        "max_score": 10,
        "passed": passed,
        "reason": "File found" if passed else "File not found"
    })
    if not exists:
        # 如果文件不存在，不再继续深入检查
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f, indent=2)
        sys.exit(0)

    # 3. JSON 合法性 (10分)
    data = load_json(workspace, report_rel)
    if data is None:
        total_score += 0
        details.append({
            "item": "Report JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File is not valid JSON"
        })
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f, indent=2)
        sys.exit(0)
    else:
        total_score += 10
        details.append({
            "item": "Report JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON"
        })

    # 4. 数据结构检查：是否为列表 (5分)
    items = data
    if not isinstance(items, list):
        total_score += 0
        details.append({
            "item": "Report root is a list",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Root element is not a list"
        })
        # 仍然尝试继续？ 但这里简单处理，直接输出
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f, indent=2)
        sys.exit(0)
    else:
        total_score += 5
        details.append({
            "item": "Report root is a list",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Root is list"
        })

    # 5. 列表长度（正确为4） (10分)
    expected_len = 4
    actual_len = len(items)
    if actual_len == expected_len:
        total_score += 10
        details.append({
            "item": f"List has exactly {expected_len} items",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found {actual_len} items"
        })
    else:
        total_score += 0
        details.append({
            "item": f"List has exactly {expected_len} items",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected {expected_len}, got {actual_len}"
        })

    # 6. 排序正确性：按size_value升序 (10分)
    sorted_correct = True
    size_values = []
    for i, item in enumerate(items):
        sv = item.get("size_value")
        if sv is None:
            sorted_correct = False
            break
        size_values.append(sv)
    if sorted_correct and all(size_values[i] <= size_values[i+1] for i in range(len(size_values)-1)):
        total_score += 10
        details.append({
            "item": "Items sorted by size_value ascending",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Sort order correct"
        })
    else:
        total_score += 0
        details.append({
            "item": "Items sorted by size_value ascending",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Sort order incorrect or missing size_value"
        })

    # 7. 逐项检查：必须包含4个特定SKU，且字段正确 (40分)
    expected_skus = ["sku_ls_001", "sku_ls_002", "sku_ls_003", "sku_ls_004"]
    expected_prices = [21.99, 32.99, 43.99, 55.99]  # 对应当前价格
    expected_selling_points = [
        ["24h hydration", "lightweight", "non-greasy"],
        ["intense moisture", "soothing", "visible glow"],
        ["all-day hydration", "barrier repair", "suitable for sensitive skin"],
        ["maximum hydration", "anti-aging", "plumping effect"]
    ]
    item_fields_ok = True
    score_per_item = 10  # 40/4
    item_details = []
    for idx, exp_sku in enumerate(expected_skus):
        item = items[idx]
        # 检查sku_id
        if item.get("sku_id") != exp_sku:
            item_fields_ok = False
            item_details.append(f"Item {idx}: expected sku_id '{exp_sku}', got '{item.get('sku_id')}'")
            continue
        # 检查price
        if abs(item.get("price", -1) - expected_prices[idx]) > 0.001:
            item_fields_ok = False
            item_details.append(f"Item {idx}: expected price {expected_prices[idx]}, got {item.get('price')}")
        # 检查selling_points前三个
        sp = item.get("selling_points", [])
        if sp != expected_selling_points[idx]:
            item_fields_ok = False
            item_details.append(f"Item {idx}: selling_points mismatch")
        # 可选检查其他字段如sku_name, size_value, pack_count等，但评分只针对核心
    if item_fields_ok:
        total_score += 40
        details.append({
            "item": "Each item has correct sku_id, price and selling_points",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": "All 4 items match expected values"
        })
    else:
        total_score += 0
        details.append({
            "item": "Each item has correct sku_id, price and selling_points",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "; ".join(item_details) if item_details else "Multiple field mismatches"
        })

    # 8. 额外字段冗余惩罚：不允许额外字段如discontinued等 (5分) 做奖励
    total_extra = 0
    for item in items:
        # 允许的字段集
        allowed = {"sku_id", "sku_name", "size_value", "size_unit", "pack_count", "price", "selling_points", "currency", "category_name", "brand_name"}
        item_keys = set(item.keys())
        extras = item_keys - allowed
        if extras:
            total_extra += len(extras)
    if total_extra == 0:
        total_score += 5
        details.append({
            "item": "No unexpected extra fields in any item",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "All fields are within expected set"
        })
    else:
        total_score += 0
        details.append({
            "item": "No unexpected extra fields in any item",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Found {total_extra} extra field(s) beyond allowed set"
        })

    # 总分写入文件
    final_score = total_score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    evaluate()
