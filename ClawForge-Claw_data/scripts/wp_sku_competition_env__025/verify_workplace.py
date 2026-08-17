import os
import sys
import json
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def check_path(*parts):
    return os.path.join(workspace, *parts)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_verification():
    score_items = []
    total_score = 0
    max_total = 100

    # 1. 目录 reports/ 存在 (10分)
    reports_dir = check_path("reports")
    if os.path.isdir(reports_dir):
        score_items.append({"item": "reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "reports/ directory found"})
        total_score += 10
    else:
        score_items.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/ directory not found"})

    # 2. 目标文件存在且 JSON 合法 (15分)
    target_file = check_path("reports", "lumina_skin_pricing_summary.json")
    if not os.path.isfile(target_file):
        score_items.append({"item": "lumina_skin_pricing_summary.json exists and valid JSON", "score": 0, "max_score": 15, "passed": False, "reason": "file not found"})
        # 后续检查跳过，直接输出
        final_score = total_score
        write_result(score_items, final_score)
        return

    try:
        data = load_json(target_file)
        score_items.append({"item": "lumina_skin_pricing_summary.json exists and valid JSON", "score": 15, "max_score": 15, "passed": True, "reason": "file exists and parseable JSON"})
        total_score += 15
    except (json.JSONDecodeError, Exception) as e:
        score_items.append({"item": "lumina_skin_pricing_summary.json exists and valid JSON", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON decode error: {e}"})
        write_result(score_items, total_score)
        return

    # 3. 检查必要字段 (20分) – brand, skus, total_price, average_price
    required_fields = ["brand", "skus", "total_price", "average_price"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        score_items.append({"item": "required fields present", "score": 0, "max_score": 20, "passed": False, "reason": f"missing fields: {missing}"})
        total_score += 0
    else:
        score_items.append({"item": "required fields present", "score": 20, "max_score": 20, "passed": True, "reason": "all required fields (brand, skus, total_price, average_price) present"})
        total_score += 20

    # 4. brand 正确 (10分)
    brand = data.get("brand", "")
    if brand == "LuminaSkin":
        score_items.append({"item": "brand is LuminaSkin", "score": 10, "max_score": 10, "passed": True, "reason": f"brand = {brand}"})
        total_score += 10
    else:
        score_items.append({"item": "brand is LuminaSkin", "score": 0, "max_score": 10, "passed": False, "reason": f"brand = {brand}, expected LuminaSkin"})

    # 5. skus 数组内容检验 (20分)
    skus = data.get("skus", [])
    # 应包含3个SKU且每个都有 sku_id 和 price
    expected_ids = ["SKU-LS-001", "SKU-LS-002", "SKU-LS-003"]
    expected_prices = { "SKU-LS-001": 45.0, "SKU-LS-002": 55.0, "SKU-LS-003": 60.0 }
    sku_field_score = 0
    reasons = []
    # 检查数量
    if len(skus) != 3:
        reasons.append(f"expected 3 SKUs, got {len(skus)}")
    else:
        sku_field_score += 5
    # 检查每个 SKU 的结构
    sku_dict = {}
    for s in skus:
        if not isinstance(s, dict):
            reasons.append("skus entry not a dict")
            continue
        sid = s.get("sku_id")
        price = s.get("price")
        if sid is None or price is None:
            reasons.append("missing sku_id or price in sku entry")
            continue
        sku_dict[sid] = price
    # 检查是否包含所有 expected_ids
    missing_ids = [eid for eid in expected_ids if eid not in sku_dict]
    if missing_ids:
        reasons.append(f"missing SKU ids: {missing_ids}")
    else:
        sku_field_score += 5
    # 检查价格
    price_ok = True
    for eid, eprice in expected_prices.items():
        actual_price = sku_dict.get(eid)
        if actual_price is None:
            price_ok = False
            reasons.append(f"{eid} price missing")
        elif abs(actual_price - eprice) > 1e-6:
            price_ok = False
            reasons.append(f"{eid} price {actual_price} != expected {eprice}")
    if price_ok:
        sku_field_score += 10
    else:
        sku_field_score += 0
    score_items.append({"item": "skus array correct (3 SKUs, correct IDs, correct prices)", "score": sku_field_score, "max_score": 20, "passed": sku_field_score >= 15, "reason": "; ".join(reasons) if reasons else "all checks passed"})
    total_score += sku_field_score

    # 6. total_price 正确 (15分)
    expected_total = 45.0 + 55.0 + 60.0  # 160.0
    total_price = data.get("total_price")
    if isinstance(total_price, (int, float)) and abs(total_price - expected_total) < 1e-6:
        score_items.append({"item": "total_price correct", "score": 15, "max_score": 15, "passed": True, "reason": f"total_price = {total_price}"})
        total_score += 15
    else:
        score_items.append({"item": "total_price correct", "score": 0, "max_score": 15, "passed": False, "reason": f"total_price = {total_price}, expected {expected_total}"})

    # 7. average_price 正确 (10分)
    expected_avg = expected_total / 3.0  # 53.3333...
    avg_price = data.get("average_price")
    if isinstance(avg_price, (int, float)) and abs(avg_price - expected_avg) < 1e-6:
        score_items.append({"item": "average_price correct", "score": 10, "max_score": 10, "passed": True, "reason": f"average_price = {avg_price}"})
        total_score += 10
    else:
        score_items.append({"item": "average_price correct", "score": 0, "max_score": 10, "passed": False, "reason": f"average_price = {avg_price}, expected {expected_avg}"})

    # 额外干净度检查（扣分项，但这里只做提醒不扣分，可忽略）
    # 8. 不应包含无关的字段如 "currency" 或多余键，但不强制，不扣分

    # 确保总分不超过100
    final_score = min(total_score, 100)
    write_result(score_items, final_score)


def write_result(items, total):
    result = {
        "total_score": total,
        "details": items
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {total}/100")

if __name__ == "__main__":
    run_verification()
