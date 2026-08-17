import sys, json, os, re
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    total = 0

    ws = Path(workspace)

    # 1. 目录结构: ops/ 目录是否存在
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        total += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ directory missing"})

    # 2. 目标文件存在
    target_file = ops_dir / "current_lumina_skus.json"
    if target_file.is_file():
        details.append({"item": "current_lumina_skus.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total += 10
    else:
        details.append({"item": "current_lumina_skus.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # 后续无法检查，直接返回
        return {"total_score": total, "details": details}

    # 3. JSON 合法性
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parsed successfully"})
        total += 10
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        return {"total_score": total, "details": details}

    # 4. 必须包含 average_price 字段（顶层）
    if "average_price" in data:
        avg = data["average_price"]
        details.append({"item": "average_price field present", "score": 5, "max_score": 5, "passed": True, "reason": f"found: {avg}"})
        total += 5
    else:
        details.append({"item": "average_price field present", "score": 0, "max_score": 5, "passed": False, "reason": "missing average_price"})

    # 5. SKU 列表必须存在且为非空列表
    sku_items = data.get("skus", data.get("items", data.get("products", [])))
    if not isinstance(sku_items, list):
        details.append({"item": "SKU list is an array", "score": 0, "max_score": 5, "passed": False, "reason": "not a list"})
        total_so_far = total
        return {"total_score": total, "details": details}
    details.append({"item": "SKU list is an array", "score": 5, "max_score": 5, "passed": True, "reason": f"found {len(sku_items)} items"})
    total += 5

    # 6. 正确数量：只应包含 3 个 active LuminaSkin SKU（lum-s01, lum-s02, lum-s03）
    expected_ids = {"lum-s01", "lum-s02", "lum-s03"}
    actual_ids = set()
    items_valid = True
    for item in sku_items:
        sid = item.get("sku_id")
        if sid:
            actual_ids.add(sid)
    if actual_ids == expected_ids:
        details.append({"item": "correct SKU count and IDs", "score": 15, "max_score": 15, "passed": True, "reason": "exactly the 3 active LuminaSkin SKUs"})
        total += 15
    else:
        details.append({"item": "correct SKU count and IDs", "score": 0, "max_score": 15, "passed": False, "reason": f"expected {expected_ids}, got {actual_ids}"})
        items_valid = False

    # 7. 每个 SKU 对象必须包含必要字段：sku_id, sku_name, selling_points, ingredients, price
    field_checks = ["sku_id", "sku_name", "selling_points", "ingredients", "price"]
    if items_valid:
        all_fields_ok = True
        missing = set()
        for item in sku_items:
            for f in field_checks:
                if f not in item:
                    missing.add(f)
        if not missing:
            details.append({"item": "required fields present in each SKU", "score": 10, "max_score": 10, "passed": True, "reason": "all 5 fields found"})
            total += 10
        else:
            details.append({"item": "required fields present in each SKU", "score": 0, "max_score": 10, "passed": False, "reason": f"missing fields: {missing}"})
            all_fields_ok = False
        # 额外：不允许包含 discontinued SKU（如 lum-s04, lum-s05）
        bad_ids = {"lum-s04", "lum-s05"}
        if bad_ids.intersection(actual_ids):
            details.append({"item": "no discontinued SKU included", "score": 0, "max_score": 10, "passed": False, "reason": f"found discontinued IDs: {actual_ids.intersection(bad_ids)}"})
        else:
            details.append({"item": "no discontinued SKU included", "score": 10, "max_score": 10, "passed": True, "reason": "only active SKUs"})
            total += 10

    # 8. 价格数值正确（必须取自 LIVE 价格手册）
    expected_prices = {"lum-s01": 24.99, "lum-s02": 39.99, "lum-s03": 19.99}
    if items_valid and all_fields_ok:
        price_ok = True
        for item in sku_items:
            sid = item["sku_id"]
            expected = expected_prices.get(sid)
            actual = item.get("price")
            if expected is None:
                continue
            # 允许浮点误差 0.001
            if abs(actual - expected) > 0.001:
                price_ok = False
                break
        if price_ok:
            details.append({"item": "correct prices from LIVE price book", "score": 15, "max_score": 15, "passed": True, "reason": "all prices match expected"})
            total += 15
        else:
            details.append({"item": "correct prices from LIVE price book", "score": 0, "max_score": 15, "passed": False, "reason": "price mismatch (maybe used archive or wrong book)"})

    # 9. 平均价格计算正确 (24.99 + 39.99 + 19.99) / 3 = 84.97 / 3 = 28.323333..., 保留两位小数 28.32
    if "average_price" in data and items_valid:
        expected_avg = round((24.99 + 39.99 + 19.99) / 3, 2)  # 28.32
        if abs(data["average_price"] - expected_avg) < 0.005:
            details.append({"item": "average_price calculation", "score": 10, "max_score": 10, "passed": True, "reason": f"{data['average_price']} matches {expected_avg}"})
            total += 10
        else:
            details.append({"item": "average_price calculation", "score": 0, "max_score": 10, "passed": False, "reason": f"got {data['average_price']}, expected {expected_avg}"})
    else:
        details.append({"item": "average_price calculation", "score": 0, "max_score": 10, "passed": False, "reason": "average_price missing or SKU list invalid"})

    # 10. 禁止使用 archive 价格或包含其他品牌
    # 已经在 ID 检查中隐含了，再加一条总结
    # 可选：确保没有意外字段（如 price_history）
    # 不扣分，仅提醒

    total = min(total, 100)
    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
