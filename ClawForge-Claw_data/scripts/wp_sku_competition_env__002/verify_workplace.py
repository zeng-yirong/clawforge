import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "ops", "lumina_competitor_report.json")
    details = []
    total_score = 0

    # 1. 检查文件存在 (10分)
    if os.path.isfile(report_path):
        details.append({"item": "报告文件存在", "score": 10, "max_score": 10, "passed": True, "reason": f"文件存在: {report_path}"})
        total_score += 10
    else:
        details.append({"item": "报告文件存在", "score": 0, "max_score": 10, "passed": False, "reason": f"文件不存在: {report_path}"})
        # 后续检查无法进行，直接结束
        write_score(total_score, details)
        return

    # 2. JSON 格式合法 (10分)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件解析成功"})
        total_score += 10
    except json.JSONDecodeError as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        write_score(total_score, details)
        return

    # 3. 必填字段存在 (10分)
    required_keys = ["report_type", "price_book", "category", "brands"]
    if all(k in report for k in required_keys):
        details.append({"item": "必填字段存在", "score": 10, "max_score": 10, "passed": True, "reason": "包含 report_type, price_book, category, brands"})
        total_score += 10
    else:
        missing = [k for k in required_keys if k not in report]
        details.append({"item": "必填字段存在", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing}"})

    # 4. 品类和价格册版本正确 (10分)
    cat_ok = report.get("category") == "UV Moisturizer"
    pb_ok = report.get("price_book") == "APAC-Q2-2026-LIVE"
    if cat_ok and pb_ok:
        details.append({"item": "品类与价格册版本", "score": 10, "max_score": 10, "passed": True, "reason": f"category='{report.get('category')}', price_book='{report.get('price_book')}'"})
        total_score += 10
    else:
        details.append({"item": "品类与价格册版本", "score": 0, "max_score": 10, "passed": False, "reason": f"category='{report.get('category')}', price_book='{report.get('price_book')}' 期望 'UV Moisturizer' 和 'APAC-Q2-2026-LIVE'"})

    # 5. 包含三个品牌, 且品牌名正确 (10分)
    brands = report.get("brands", {})
    expected_brands = ["LuminaSkin", "DermVeil", "AquaPulse"]
    if all(b in brands for b in expected_brands) and len(brands) == 3:
        details.append({"item": "品牌数量与名称", "score": 10, "max_score": 10, "passed": True, "reason": "包含 LuminaSkin, DermVeil, AquaPulse"})
        total_score += 10
    else:
        actual = list(brands.keys())
        details.append({"item": "品牌数量与名称", "score": 0, "max_score": 10, "passed": False, "reason": f"实际品牌: {actual}, 期望: {expected_brands}"})

    # 6. 每个品牌的 SKU 数量及价格正确 (30分, 每个品牌10分)
    # 已知真实数据:
    # LuminaSkin: LS-UV-001 (24.99), LS-UV-002 (29.99), LS-UV-003 (19.99) → 3个
    # DermVeil: DV-UV-101 (22.99), DV-UV-102 (27.99) → 2个
    # AquaPulse: AP-UV-201 (21.99) → 1个
    brand_skus_expected = {
        "LuminaSkin": {"sku_ids": ["LS-UV-001", "LS-UV-002", "LS-UV-003"],
                       "prices": {"LS-UV-001": 24.99, "LS-UV-002": 29.99, "LS-UV-003": 19.99}},
        "DermVeil": {"sku_ids": ["DV-UV-101", "DV-UV-102"],
                     "prices": {"DV-UV-101": 22.99, "DV-UV-102": 27.99}},
        "AquaPulse": {"sku_ids": ["AP-UV-201"],
                      "prices": {"AP-UV-201": 21.99}}
    }
    score_item_skus = 10
    for brand_name, expected in brand_skus_expected.items():
        brand_data = brands.get(brand_name, {})
        skus_data = brand_data.get("skus", [])
        # 检查 SKU 数量
        if len(skus_data) != len(expected["sku_ids"]):
            details.append({"item": f"{brand_name} SKU 数量", "score": 0, "max_score": score_item_skus, "passed": False,
                            "reason": f"期望 {len(expected['sku_ids'])} 个, 实际 {len(skus_data)} 个"})
            continue
        # 检查每个 SKU 的 ID 和价格
        all_ok = True
        for sku in skus_data:
            sid = sku.get("sku_id")
            price = sku.get("current_price")
            if sid not in expected["prices"]:
                all_ok = False
                break
            if price != expected["prices"][sid]:
                all_ok = False
                break
        if all_ok:
            details.append({"item": f"{brand_name} SKU 明细", "score": score_item_skus, "max_score": score_item_skus, "passed": True,
                            "reason": f"SKU 数量和价格正确"})
            total_score += score_item_skus
        else:
            details.append({"item": f"{brand_name} SKU 明细", "score": 0, "max_score": score_item_skus, "passed": False,
                            "reason": "SKU ID 或价格与期望不符"})

    # 7. 平均价格计算 (20分, 每个品牌约6.67, 但按总20分配)
    expected_avg = {
        "LuminaSkin": round((24.99 + 29.99 + 19.99) / 3, 2),  # 24.99
        "DermVeil": round((22.99 + 27.99) / 2, 2),           # 25.49
        "AquaPulse": 21.99                                    # 21.99
    }
    avg_score_unit = 20 // 3  # 6
    avg_remainder = 20 % 3    # 2 for first brand
    for i, (brand_name, avg_expected) in enumerate(expected_avg.items()):
        max_s = avg_score_unit + (1 if i == 0 else 0) if i < 2 else avg_score_unit + 1  # 7,6,7
        # Wait, distribute: 20 = 7+7+6 or 7+6+7. Simpler: check each individually scoring 7,7,6
        # Use fixed: first 7, second 7, third 6
        if i == 0:
            max_s = 7
        elif i == 1:
            max_s = 7
        else:
            max_s = 6
        brand_data = brands.get(brand_name, {})
        avg_actual = brand_data.get("avg_price")
        if avg_actual is not None and abs(avg_actual - avg_expected) < 0.005:
            details.append({"item": f"{brand_name} 平均价格", "score": max_s, "max_score": max_s, "passed": True,
                            "reason": f"avg_price = {avg_actual}"})
            total_score += max_s
        else:
            details.append({"item": f"{brand_name} 平均价格", "score": 0, "max_score": max_s, "passed": False,
                            "reason": f"期望 {avg_expected}, 实际 {avg_actual}"})

    # 写入结果
    output = {"total_score": min(total_score, 100), "details": details}
    write_score(output["total_score"], details)

def write_score(total, details):
    output_path = "workplace_score.json"
    with open(output_path, "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
