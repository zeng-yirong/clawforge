import json
import os
import sys

def main():
    # 工作区路径
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "output/competition_report.json")
    score_details = []
    total_score = 0
    max_total = 100

    # 1. 文件存在性 (10分)
    if not os.path.exists(result_path):
        score_details.append({
            "item": "output/competition_report.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 直接结束，剩余项无法检查
        _write_score(score_details, total_score, max_total)
        return
    else:
        score_details.append({
            "item": "output/competition_report.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10

    # 2. JSON 合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 10
    except json.JSONDecodeError as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        _write_score(score_details, total_score, max_total)
        return

    # 3. 顶层结构 (10分)
    required_keys = ["brands", "price_difference"]
    if not all(k in data for k in required_keys):
        missing = [k for k in required_keys if k not in data]
        score_details.append({
            "item": "顶层键存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"缺少键 {missing}"
        })
        total_score += 0
    else:
        score_details.append({
            "item": "顶层键存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "包含 brands 和 price_difference"
        })
        total_score += 10

    # 4. brands 结构 (20分)
    brands = data.get("brands", {})
    expected_brands = ["LuminaSkin", "DermVeil"]
    present_brands = list(brands.keys())
    if sorted(present_brands) == sorted(expected_brands):
        score_details.append({
            "item": "brands 包含两个正确品牌",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"品牌列表: {present_brands}"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "brands 包含两个正确品牌",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际品牌: {present_brands}"
        })

    # 每个品牌必须包含 sku_count, average_price, skus
    brand_structure_ok = True
    for brand in expected_brands:
        bdata = brands.get(brand, {})
        for field in ["sku_count", "average_price", "skus"]:
            if field not in bdata:
                brand_structure_ok = False
                break
        if not brand_structure_ok:
            break
    if brand_structure_ok:
        score_details.append({
            "item": "每个品牌包含 sku_count, average_price, skus",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "结构正确"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "每个品牌包含 sku_count, average_price, skus",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在缺失字段"
        })

    # 5. SKU 数量与详情的正确性 (30分)
    # LuminaSkin: 应只有2个active Hydration Serum SKU (LS-HS-001, LS-HS-002)
    # DermVeil: 2个active (DV-HS-001, DV-HS-002)
    # 检查 sku_count 和 skus 列表长度
    lumina = brands.get("LuminaSkin", {})
    derm = brands.get("DermVeil", {})
    score_skus = 0
    max_skus = 30

    # 检查数量
    lumina_count = lumina.get("sku_count", -1)
    derm_count = derm.get("sku_count", -1)
    if lumina_count == 2 and derm_count == 2:
        score_skus += 10
        # 检查 skus 列表长度
        if len(lumina.get("skus", [])) == 2 and len(derm.get("skus", [])) == 2:
            score_skus += 10
            # 检查每个 SKU 是否包含必要字段并且价格正确
            # 预期价格: LS-HS-001 -> 30.00, LS-HS-002 -> 35.00, DV-HS-001 -> 32.00, DV-HS-002 -> 28.00
            expected_prices = {
                "LS-HS-001": 30.00,
                "LS-HS-002": 35.00,
                "DV-HS-001": 32.00,
                "DV-HS-002": 28.00
            }
            price_ok = True
            for sku_info in lumina["skus"]:
                sid = sku_info.get("sku_id")
                price = sku_info.get("price")
                if sid not in expected_prices or abs(price - expected_prices[sid]) > 1e-6:
                    price_ok = False
                    break
            for sku_info in derm["skus"]:
                sid = sku_info.get("sku_id")
                price = sku_info.get("price")
                if sid not in expected_prices or abs(price - expected_prices[sid]) > 1e-6:
                    price_ok = False
                    break
            if price_ok:
                score_skus += 10
            else:
                score_skus += 0
        else:
            score_skus += 0
    else:
        score_skus = 0

    score_details.append({
        "item": "SKU 数量与价格正确",
        "score": score_skus,
        "max_score": 30,
        "passed": score_skus == 30,
        "reason": f"Lumina count={lumina_count} (期望2), Derm count={derm_count} (期望2); 价格匹配={price_ok if 'price_ok' in dir() else 'N/A'}"
    })
    total_score += score_skus

    # 6. 平均价格正确性 (15分)
    # LuminaSkin avg = (30+35)/2 = 32.5; DermVeil avg = (32+28)/2 = 30.0
    expected_avg = {"LuminaSkin": 32.5, "DermVeil": 30.0}
    avg_ok = True
    for brand, exp in expected_avg.items():
        actual = brands.get(brand, {}).get("average_price", None)
        if actual is None or abs(actual - exp) > 1e-6:
            avg_ok = False
            break
    if avg_ok:
        score_details.append({
            "item": "平均价格正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"LuminaSkin={brands['LuminaSkin']['average_price']}, DermVeil={brands['DermVeil']['average_price']}"
        })
        total_score += 15
    else:
        score_details.append({
            "item": "平均价格正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"实际 Lumina={brands.get('LuminaSkin',{}).get('average_price')}, 期望32.5; Derm={brands.get('DermVeil',{}).get('average_price')}, 期望30.0"
        })

    # 7. price_difference 正确性 (15分)
    # expected diff = 32.5 - 30.0 = 2.5 (Lumina - Derm)
    diff = data.get("price_difference", None)
    expected_diff = 2.5
    if diff is not None and abs(diff - expected_diff) < 1e-6:
        score_details.append({
            "item": "价格差正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"price_difference = {diff}"
        })
        total_score += 15
    else:
        score_details.append({
            "item": "价格差正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"实际 {diff}, 期望 {expected_diff}"
        })

    # 写入结果
    _write_score(score_details, total_score, max_total)

def _write_score(details, total, max_total):
    total = min(total, max_total)
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"总分: {total}/{max_total}")

if __name__ == "__main__":
    main()
