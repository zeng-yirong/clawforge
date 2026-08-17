import os
import json
import random

def build_env():
    # Create directory structure
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- brands.json ----
    brands = [
        {
            "brand_id": "b_lum_001",
            "brand_name": "LuminaSkin",
            "hero_category_id": "cat_serum_01",
            "hero_category_name": "Hydration Serum",
            "positioning": "Premium clinical hydration",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "b_der_002",
            "brand_name": "DermVeil",
            "hero_category_id": "cat_serum_01",
            "hero_category_name": "Hydration Serum",
            "positioning": "Dermatologist-recommended essentials",
            "region_focus": "APAC",
            "price_tier": "mid-premium"
        },
        {
            "brand_id": "b_aqu_003",
            "brand_name": "AquaPulse",
            "hero_category_id": "cat_moist_02",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Daily UV protection",
            "region_focus": "APAC",
            "price_tier": "mid"
        },
        {
            "brand_id": "b_pur_004",
            "brand_name": "PureLattice",
            "hero_category_id": "cat_serum_01",
            "hero_category_name": "Hydration Serum",
            "positioning": "Clean beauty hydrogel",
            "region_focus": "APAC",
            "price_tier": "mid"
        },
        {
            "brand_id": "b_sol_005",
            "brand_name": "SolarOat",
            "hero_category_id": "cat_moist_02",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Mineral SPF everyday",
            "region_focus": "APAC",
            "price_tier": "value"
        }
    ]
    with open("data/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # ---- skus.json ----
    skus = [
        # LuminaSkin – Hydration Serum (active)
        {"sku_id": "sku_lum_hs01", "brand_id": "b_lum_001", "brand_name": "LuminaSkin", "category_id": "cat_serum_01", "category_name": "Hydration Serum", "sku_name": "Intense Hydration Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["24h moisture lock"], "ingredients": ["Hyaluronic Acid", "Vitamin B5"]},
        {"sku_id": "sku_lum_hs02", "brand_id": "b_lum_001", "brand_name": "LuminaSkin", "category_id": "cat_serum_01", "category_name": "Hydration Serum", "sku_name": "Intense Hydration Serum 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["24h moisture lock"], "ingredients": ["Hyaluronic Acid", "Vitamin B5"]},
        {"sku_id": "sku_lum_hs03", "brand_id": "b_lum_001", "brand_name": "LuminaSkin", "category_id": "cat_serum_01", "category_name": "Hydration Serum", "sku_name": "Intense Hydration Serum Duo", "size_value": 30, "size_unit": "ml", "pack_count": 2, "status": "active", "selling_points": ["Gift size", "Perfect travel"], "ingredients": ["Hyaluronic Acid", "Ceramide"]},
        # LuminaSkin – UV Moisturizer (干扰，不相关类别)
        {"sku_id": "sku_lum_uv01", "brand_id": "b_lum_001", "brand_name": "LuminaSkin", "category_id": "cat_moist_02", "category_name": "UV Moisturizer", "sku_name": "UV Defense Moisturizer 40ml", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF50", "Matte finish"], "ingredients": ["Zinc Oxide", "Niacinamide"]},
        # DermVeil – Hydration Serum (active)
        {"sku_id": "sku_der_hs01", "brand_id": "b_der_002", "brand_name": "DermVeil", "category_id": "cat_serum_01", "category_name": "Hydration Serum", "sku_name": "Calm Hydra Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Sensitive skin safe"], "ingredients": ["Centella Asiatica", "Panthenol"]},
        {"sku_id": "sku_der_hs02", "brand_id": "b_der_002", "brand_name": "DermVeil", "category_id": "cat_serum_01", "category_name": "Hydration Serum", "sku_name": "Calm Hydra Serum 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Sensitive skin safe"], "ingredients": ["Centella Asiatica", "Panthenol"]},
        # DermVeil – Hydration Serum (discontinued, 干扰)
        {"sku_id": "sku_der_hs03", "brand_id": "b_der_002", "brand_name": "DermVeil", "category_id": "cat_serum_01", "category_name": "Hydration Serum", "sku_name": "Calm Hydra Serum 75ml (old)", "size_value": 75, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["Limited edition"], "ingredients": ["Centella Asiatica"]},
        # AquaPulse – UV Moisturizer (active)
        {"sku_id": "sku_aqu_uv01", "brand_id": "b_aqu_003", "brand_name": "AquaPulse", "category_id": "cat_moist_02", "category_name": "UV Moisturizer", "sku_name": "Aqua Shield SPF30", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Water resistant"], "ingredients": ["Avobenzone", "Vitamin E"]},
        # PureLattice – Hydration Serum (active)
        {"sku_id": "sku_pur_hs01", "brand_id": "b_pur_004", "brand_name": "PureLattice", "category_id": "cat_serum_01", "category_name": "Hydration Serum", "sku_name": "Hydrogel Boost 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Lightweight", "Instant glow"], "ingredients": ["Glycerin", "Aloe Vera"]},
        # SolarOat – UV Moisturizer (active)
        {"sku_id": "sku_sol_uv01", "brand_id": "b_sol_005", "brand_name": "SolarOat", "category_id": "cat_moist_02", "category_name": "UV Moisturizer", "sku_name": "Mineral SPF50", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Non-nano zinc"], "ingredients": ["Zinc Oxide", "Shea Butter"]}
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # ---- price_books.json ----
    # 所有active的Hydration Serum SKU的价格（美分单位，便于整数运算，但输出时转成美元浮点）
    price_entries_current = [
        {"sku_id": "sku_lum_hs01", "price_cents": 2999},
        {"sku_id": "sku_lum_hs02", "price_cents": 3450},
        {"sku_id": "sku_lum_hs03", "price_cents": 2499},
        {"sku_id": "sku_der_hs01", "price_cents": 2750},
        {"sku_id": "sku_der_hs02", "price_cents": 3100},
        # 也包括不相关的SKU（干扰）
        {"sku_id": "sku_aqu_uv01", "price_cents": 2200},
        {"sku_id": "sku_pur_hs01", "price_cents": 2600},
        {"sku_id": "sku_sol_uv01", "price_cents": 1900},
        # discontinued 的 SKU 也存在，但agent应排除
        {"sku_id": "sku_der_hs03", "price_cents": 2000}
    ]
    # 存档价格册（archived） – 价格不同，但agent应忽略
    price_entries_archive = [
        {"sku_id": "sku_lum_hs01", "price_cents": 3200},
        {"sku_id": "sku_lum_hs02", "price_cents": 3600},
        {"sku_id": "sku_der_hs01", "price_cents": 2600},
        {"sku_id": "sku_der_hs02", "price_cents": 3000}
    ]
    price_books = [
        {
            "price_book_id": "pb_apac_2026_01",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": price_entries_archive
        },
        {
            "price_book_id": "pb_apac_2026_02",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": price_entries_current
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # 额外放置一些干扰文件（非结构化的文本）
    with open("data/attachments.json", "w") as f:
        json.dump([{
            "path": "attachments/category_review_template.md",
            "title": "Category Review Template",
            "kind": "report_template",
            "description": "Template for category performance review"
        }], f, indent=2)

    # 创建一个无关的日志文件
    os.makedirs("logs", exist_ok=True)
    with open("logs/metrics_2026_q2.csv", "w") as f:
        f.write("date,brand,impressions,clicks\n2026-04-01,LuminaSkin,12000,450\n")

if __name__ == "__main__":
    build_env()
