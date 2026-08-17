import json
import sys
import os
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(val, ndigits=1):
    d = Decimal(str(val))
    return float(d.quantize(Decimal(10) ** (-ndigits), rounding=ROUND_HALF_UP))

def main():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    score = 0
    details = []

    # ---------- 1. 检查目标文件是否存在 ----------
    report_path = workspace / "ops" / "price_drops_report.json"
    if not report_path.exists():
        details.append({"item": "目标文件存在", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"文件 {report_path} 不存在"})
        # 文件不存在直接结束，后续无法检查
        write_score(workspace, 0, details)
        return
    else:
        details.append({"item": "目标文件存在", "score": 10, "max_score": 10, "passed": True,
                        "reason": "文件存在"})
        score += 10

    # ---------- 2. 检查JSON合法性 ----------
    try:
        with open(report_path) as f:
            report = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True,
                        "reason": "解析成功"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"JSON解析失败: {e}"})
        write_score(workspace, score, details)
        return

    # ---------- 3. 检查 schema_version ----------
    if report.get("schema_version") == "1.0":
        details.append({"item": "schema_version正确", "score": 5, "max_score": 5, "passed": True,
                        "reason": "版本号匹配"})
        score += 5
    else:
        details.append({"item": "schema_version正确", "score": 0, "max_score": 5, "passed": False,
                        "reason": f"版本号应为1.0，实际为{report.get('schema_version')}"})

    # ---------- 4. 检查 generated_at 不是占位符 ----------
    gen = report.get("generated_at", "")
    if gen and gen != "PLACEHOLDER_DATETIME":
        details.append({"item": "generated_at已填写", "score": 5, "max_score": 5, "passed": True,
                        "reason": "已填写时间戳"})
        score += 5
    else:
        details.append({"item": "generated_at已填写", "score": 0, "max_score": 5, "passed": False,
                        "reason": "generated_at仍为占位符或为空"})

    # ---------- 5. 检查drops数组存在且格式正确 ----------
    drops = report.get("drops")
    if not isinstance(drops, list) or len(drops) == 0:
        details.append({"item": "drops数组非空", "score": 0, "max_score": 10, "passed": False,
                        "reason": "drops不存在或为空"})
        write_score(workspace, score, details)
        return
    else:
        details.append({"item": "drops数组非空", "score": 10, "max_score": 10, "passed": True,
                        "reason": f"drops数组长度{len(drops)}"})
        score += 10

    # ---------- 加载原始数据，计算预期结果 ----------
    # 加载品牌数据
    brands_path = workspace / "data" / "brands" / "brands.json"
    with open(brands_path) as f:
        brands_data = json.load(f)
    target_brand_ids = set()
    for b in brands_data["brands"]:
        if b["brand_name"] in ("LuminaSkin", "DermVeil"):
            target_brand_ids.add(b["brand_id"])

    # 加载SKU数据
    skus_path = workspace / "data" / "skus" / "skus.json"
    with open(skus_path) as f:
        skus_data = json.load(f)
    sku_info = {}
    for s in skus_data["skus"]:
        sku_info[s["sku_id"]] = {
            "sku_name": s["sku_name"],
            "brand_id": s["brand_id"],
            "brand_name": s["brand_name"]
        }

    # 加载价格书
    pb_path = workspace / "data" / "pricing" / "price_books.json"
    with open(pb_path) as f:
        pb_data = json.load(f)
    books = pb_data["price_books"]
    old_book = next(b for b in books if b["price_book_id"] == "APAC-Q1-2026-ARCHIVE")
    new_book = next(b for b in books if b["price_book_id"] == "APAC-Q2-2026-LIVE")

    # 构建价格映射（保留第一个有效数字价格）
    def build_price_map(entries):
        pm = {}
        for e in entries:
            sku = e["sku_id"]
            price = e["price"]
            # 只取第一个有效数字
            if sku not in pm and isinstance(price, (int, float)) and price > 0:
                pm[sku] = price
        return pm

    old_prices = build_price_map(old_book["entries"])
    new_prices = build_price_map(new_book["entries"])

    # 计算预期结果
    expected = []
    for sku_id in old_prices:
        if sku_id not in new_prices:
            continue
        old = old_prices[sku_id]
        new = new_prices[sku_id]
        if old <= 0:
            continue
        drop_pct = (old - new) / old * 100
        if drop_pct > 20:
            info = sku_info.get(sku_id)
            if info and info["brand_id"] in target_brand_ids:
                expected.append({
                    "sku_id": sku_id,
                    "sku_name": info["sku_name"],
                    "old_price": old,
                    "new_price": new,
                    "drop_percent": round_half_up(drop_pct, 1)
                })

    # 按降幅降序排序
    expected.sort(key=lambda x: x["drop_percent"], reverse=True)

    # ---------- 6. 检查SKU品牌范围 ----------
    reported_sku_ids = {d["sku_id"] for d in drops}
    expected_sku_ids = {d["sku_id"] for d in expected}
    # 多余的报告
    extra = reported_sku_ids - expected_sku_ids
    # 缺失的报告
    missing = expected_sku_ids - reported_sku_ids
    brand_ok = True
    brand_loss = 0
    max_brand = 15

    # 检查是否所有报告SKU都属于目标品牌（通过验证是否在预期列表中，因为预期列表已过滤）
    # 同时检查没有其他品牌的SKU
    for d in drops:
        sku = d.get("sku_id", "")
        info = sku_info.get(sku)
        if info is None:
            brand_ok = False
            brand_loss += 5
        elif info["brand_id"] not in target_brand_ids:
            brand_ok = False
            brand_loss += 5
    if missing:
        brand_loss += 5
        brand_ok = False
    if brand_ok:
        details.append({"item": "品牌范围正确（仅LuminaSkin/DermVeil）", "score": 15, "max_score": 15,
                        "passed": True, "reason": "无多余SKU，无缺失"})
        score += 15
    else:
        detail_reason = []
        if extra:
            detail_reason.append(f"多余SKU: {extra}")
        if missing:
            detail_reason.append(f"缺失SKU: {missing}")
        detail_reason.append(f"扣分{min(15, brand_loss)}")
        details.append({"item": "品牌范围正确（仅LuminaSkin/DermVeil）", "score": max(0, 15-brand_loss),
                        "max_score": 15, "passed": False, "reason": "; ".join(detail_reason)})

    # ---------- 7. 检查每个entry的字段完整性 ----------
    required_fields = {"sku_id", "sku_name", "old_price", "new_price", "drop_percent"}
    field_errors = 0
    for i, d in enumerate(drops):
        missing_fields = required_fields - set(d.keys())
        if missing_fields:
            field_errors += 1
        # 检查数据类型
        if not isinstance(d.get("old_price"), (int, float)):
            field_errors += 1
        if not isinstance(d.get("new_price"), (int, float)):
            field_errors += 1
        if not isinstance(d.get("drop_percent"), (int, float)):
            field_errors += 1
    if field_errors == 0:
        details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True,
                        "reason": "所有条目标字段齐全且类型正确"})
        score += 10
    else:
        details.append({"item": "字段完整性", "score": max(0, 10 - field_errors*2),
                        "max_score": 10, "passed": False, "reason": f"发现{field_errors}个条目标字段缺失或类型错误"})

    # ---------- 8. 检查数值正确性（逐一比对） ----------
    numerical_score = 20
    if not expected:
        numerical_score = 0
        details.append({"item": "数值正确性", "score": 0, "max_score": 20, "passed": False,
                        "reason": "预期结果为空，但drops非空或数据错误"})
    else:
        # 构建预期字典方便查找
        exp_by_sku = {d["sku_id"]: d for d in expected}
        errors = 0
        for d in drops:
            sku = d["sku_id"]
            exp = exp_by_sku.get(sku)
            if not exp:
                errors += 1
                continue
            # 检查价格
            if d.get("old_price") != exp["old_price"]:
                errors += 1
            if d.get("new_price") != exp["new_price"]:
                errors += 1
            # 检查降幅（允许0.1舍入误差）
            reported_pct = d.get("drop_percent")
            expected_pct = exp["drop_percent"]
            if abs(round_half_up(reported_pct, 1) - expected_pct) > 0.05:
                errors += 1
            # 检查名称
            if d.get("sku_name") != exp["sku_name"]:
                errors += 1
        if errors == 0:
            details.append({"item": "数值正确性", "score": 20, "max_score": 20, "passed": True,
                            "reason": "所有数值与预期一致"})
            score += 20
        else:
            detail_score = max(0, 20 - errors * 5)
            details.append({"item": "数值正确性", "score": detail_score, "max_score": 20,
                            "passed": False, "reason": f"发现{errors}个数值不一致"})

    # ---------- 9. 排序检查 ----------
    sort_ok = True
    for i in range(len(drops)-1):
        if drops[i].get("drop_percent", 0) < drops[i+1].get("drop_percent", 0):
            sort_ok = False
            break
    if sort_ok:
        details.append({"item": "降幅降序排序", "score": 10, "max_score": 10, "passed": True,
                        "reason": "排序正确"})
        score += 10
    else:
        details.append({"item": "降幅降序排序", "score": 0, "max_score": 10, "passed": False,
                        "reason": "未按降幅从大到小排序"})

    # ---------- 汇总 ----------
    final_score = min(100, max(0, score))
    write_score(workspace, final_score, details)


def write_score(workspace, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Verification complete. Score: {total_score}/100")


if __name__ == "__main__":
    main()
