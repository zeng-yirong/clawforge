import sys
import json
import os
import math

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    max_total = 100

    # 1. 检查 reports/price_compare_Q2_2026.json 是否存在 (10分)
    report_path = os.path.join(workspace, "reports", "price_compare_Q2_2026.json")
    if os.path.isfile(report_path):
        details.append({"item": "Output file exists", "score": 10, "max_score": 10,
                        "passed": True, "reason": "File found at reports/price_compare_Q2_2026.json"})
        score += 10
    else:
        details.append({"item": "Output file exists", "score": 0, "max_score": 10,
                        "passed": False, "reason": "File not found"})
        # 如果文件不存在，后续都无法验证，直接返回
        total = sum(d["score"] for d in details)
        result = {"total_score": total, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 解析 JSON 合法性 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON parse valid", "score": 10, "max_score": 10,
                        "passed": True, "reason": "Valid JSON"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON parse valid", "score": 0, "max_score": 10,
                        "passed": False, "reason": f"Invalid JSON: {e}"})
        total = sum(d["score"] for d in details)
        result = {"total_score": total, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查是否为列表，且长度正确 (10分)
    if not isinstance(data, list):
        details.append({"item": "Data is a list", "score": 0, "max_score": 10,
                        "passed": False, "reason": "Top level is not a list"})
        score += 0
    else:
        expected_count = 3  # 只有 LuminaSkin Hydration Serum 的 3 个 SKU
        if len(data) == expected_count:
            details.append({"item": "Record count correct", "score": 10, "max_score": 10,
                            "passed": True, "reason": f"Found {len(data)} records (expected {expected_count})"})
            score += 10
        else:
            details.append({"item": "Record count correct", "score": 0, "max_score": 10,
                            "passed": False, "reason": f"Found {len(data)} records, expected {expected_count}"})

    # 定义期望字段列表
    required_fields = ["sku_id", "brand_name", "category_name", "old_price",
                       "new_price", "price_change_percent", "selling_points_updated"]
    # 4. 字段完整性 (20分) — 每条记录都要包含全部字段
    field_score = 20
    field_passed = True
    field_reasons = []
    for idx, rec in enumerate(data):
        missing = [f for f in required_fields if f not in rec]
        if missing:
            field_passed = False
            field_reasons.append(f"Record {idx} missing fields: {missing}")
    if field_passed:
        details.append({"item": "All required fields present in every record",
                        "score": field_score, "max_score": field_score,
                        "passed": True, "reason": "All records contain the 7 required fields"})
        score += field_score
    else:
        details.append({"item": "All required fields present in every record",
                        "score": 0, "max_score": field_score,
                        "passed": False,
                        "reason": "; ".join(field_reasons)})

    # 5. 数值准确性 (30分) — 检查每条记录的 old_price, new_price, price_change_percent
    # 已知正确值
    correct_records = {
        "sku_ls01": {"old_price": 29.99, "new_price": 24.99,
                     "price_change_percent": "-16.7%",
                     "selling_points_updated": True},
        "sku_ls02": {"old_price": 34.99, "new_price": 34.99,
                     "price_change_percent": "0.0%",
                     "selling_points_updated": False},
        "sku_ls03": {"old_price": 39.99, "new_price": 44.99,
                     "price_change_percent": "12.5%",
                     "selling_points_updated": False}
    }

    num_score = 0
    max_num_score = 30
    num_details = []
    for rec in data:
        sku = rec.get("sku_id")
        if sku not in correct_records:
            num_details.append(f"Unexpected sku_id {sku}")
            continue
        expected = correct_records[sku]
        # 检查 old_price (允许浮点误差 0.005)
        if abs(rec.get("old_price", -1) - expected["old_price"]) > 0.005:
            num_details.append(f"{sku} old_price mismatch: got {rec.get('old_price')}, expected {expected['old_price']}")
        # 检查 new_price
        if abs(rec.get("new_price", -1) - expected["new_price"]) > 0.005:
            num_details.append(f"{sku} new_price mismatch: got {rec.get('new_price')}, expected {expected['new_price']}")
        # 检查 price_change_percent (精确字符串匹配)
        if rec.get("price_change_percent") != expected["price_change_percent"]:
            num_details.append(f"{sku} price_change_percent mismatch: got '{rec.get('price_change_percent')}', expected '{expected['price_change_percent']}'")
        # 检查 selling_points_updated
        if rec.get("selling_points_updated") != expected["selling_points_updated"]:
            num_details.append(f"{sku} selling_points_updated mismatch: got {rec.get('selling_points_updated')}, expected {expected['selling_points_updated']}")

    if len(num_details) == 0:
        num_score = max_num_score
        details.append({"item": "Price & percentage & selling flag accuracy",
                        "score": num_score, "max_score": max_num_score,
                        "passed": True, "reason": "All 3 records match expected values"})
        score += num_score
    else:
        # 按错误数量扣分：每个错误扣 10 分，最多扣到 0
        errors = len(num_details)
        deducted = min(errors * 10, max_num_score)
        num_score = max_num_score - deducted
        details.append({"item": "Price & percentage & selling flag accuracy",
                        "score": num_score, "max_score": max_num_score,
                        "passed": False, "reason": "; ".join(num_details[:5])})
        score += num_score

    # 6. 可选加分：检查是否包含非目标品牌/品类 (如果有则扣分，这里我们检查没有多余记录)
    extra_passed = True
    for rec in data:
        if rec.get("brand_name") != "LuminaSkin" or rec.get("category_name") != "Hydration Serum":
            extra_passed = False
            break
    if extra_passed:
        # 不加分，但可记录
        pass
    else:
        # 扣分：从总分中直接扣除 10 分（但已经计入前面记录数？为了明确，增加一个扣分项）
        details.append({"item": "No extra records from other brands/categories",
                        "score": 0, "max_score": 0,
                        "passed": False, "reason": "Found records with brand_name or category_name not LuminaSkin/Hydration Serum"})
        # 因为前面记录数已经扣分，这里不再重复扣，仅提示

    # 汇总总分（确保不超过100）
    total = sum(d["score"] for d in details)
    total = min(total, max_total)
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
