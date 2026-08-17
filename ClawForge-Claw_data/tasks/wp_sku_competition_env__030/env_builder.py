import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)

    # ---- brands.json (干扰项) ----
    brands = {
        "brands": [
            {"brand_id": "b_aqua", "brand_name": "AquaPulse", "hero_category_id": "cat_001", "hero_category_name": "Hydration Serum", "positioning": "mass", "region_focus": "EMEA", "price_tier": "mid"},
            {"brand_id": "b_lumina", "brand_name": "LuminaSkin", "hero_category_id": "cat_002", "hero_category_name": "UV Moisturizer", "positioning": "prestige", "region_focus": "APAC", "price_tier": "premium"},
            {"brand_id": "b_derm", "brand_name": "DermVeil", "hero_category_id": "cat_001", "hero_category_name": "Hydration Serum", "positioning": "derm", "region_focus": "NA", "price_tier": "mid-premium"},
        ]
    }
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # ---- skus.json ----
    # LuminaSkin 5 SKUs，其中 3 个含 Niacinamide，2 个不含
    # 其他品牌各 2 个 SKU 作为干扰
    skus = {
        "skus": [
            # AquaPulse
            {"sku_id": "sku_aq_001", "brand_id": "b_aqua", "brand_name": "AquaPulse", "category_id": "cat_001", "category_name": "Hydration Serum", "sku_name": "Aqua Boost", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["lightweight", "oil-free"], "ingredients": ["Water", "Glycerin", "Hyaluronic Acid"]},
            {"sku_id": "sku_aq_002", "brand_id": "b_aqua", "brand_name": "AquaPulse", "category_id": "cat_001", "category_name": "Hydration Serum", "sku_name": "Aqua Glow", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["brightening"], "ingredients": ["Water", "Vitamin C", "Niacinamide", "Glycerin"]},
            # LuminaSkin
            {"sku_id": "sku_lm_001", "brand_id": "b_lumina", "brand_name": "LuminaSkin", "category_id": "cat_002", "category_name": "UV Moisturizer", "sku_name": "UV Shield SPF50", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["broad spectrum", "water resistant"], "ingredients": ["Zinc Oxide", "Titanium Dioxide", "Niacinamide", "Aloe Vera"]},
            {"sku_id": "sku_lm_002", "brand_id": "b_lumina", "brand_name": "LuminaSkin", "category_id": "cat_002", "category_name": "UV Moisturizer", "sku_name": "Day Repair SPF30", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["anti-aging", "moisturizing"], "ingredients": ["Retinol", "Niacinamide", "Peptides", "Squalane"]},
            {"sku_id": "sku_lm_003", "brand_id": "b_lumina", "brand_name": "LuminaSkin", "category_id": "cat_002", "category_name": "UV Moisturizer", "sku_name": "Night Renew", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["deep hydration"], "ingredients": ["Ceramides", "Niacinamide", "Panthenol"]},
            {"sku_id": "sku_lm_004", "brand_id": "b_lumina", "brand_name": "LuminaSkin", "category_id": "cat_002", "category_name": "UV Moisturizer", "sku_name": "Mattify Lotion", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["oil control"], "ingredients": ["Salicylic Acid", "Kaolin", "Zinc PCA"]},
            {"sku_id": "sku_lm_005", "brand_id": "b_lumina", "brand_name": "LuminaSkin", "category_id": "cat_002", "category_name": "UV Moisturizer", "sku_name": "Sensitive Skin Cream", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["gentle", "fragrance-free"], "ingredients": ["Shea Butter", "Oat Extract", "Allantoin"]},
            # DermVeil
            {"sku_id": "sku_dv_001", "brand_id": "b_derm", "brand_name": "DermVeil", "category_id": "cat_001", "category_name": "Hydration Serum", "sku_name": "Calm Hydrator", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["sensitive skin"], "ingredients": ["Centella Asiatica", "Niacinamide", "Hyaluronic Acid"]},
            {"sku_id": "sku_dv_002", "brand_id": "b_derm", "brand_name": "DermVeil", "category_id": "cat_001", "category_name": "Hydration Serum", "sku_name": "Retinol Night", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["anti-aging"], "ingredients": ["Retinol", "Squalane", "Vitamin E"]},
        ]
    }
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # ---- price_books.json ----
    # 两个价格书：一个 archivced（Q1），一个 live（Q2）
    # live 版 entries 只包含 LuminaSkin 的 5 个 SKU（答案唯一）
    # archivced 版 entries 包含 AquaPulse 和 DermVeil 的 SKU 作为干扰
    # entries 结构：每个元素是 {"sku_id": ..., "price": ...}
    price_books = {
        "price_books": [
            {
                "price_book_id": "pb_ap_q1_2026",
                "version": "APAC-Q1-2026-ARCHIVE",
                "region": "APAC",
                "status": "archived",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": [
                    {"sku_id": "sku_aq_001", "price": 29.99},
                    {"sku_id": "sku_aq_002", "price": 34.99},
                    {"sku_id": "sku_dv_001", "price": 45.00},
                    {"sku_id": "sku_dv_002", "price": 55.00}
                ]
            },
            {
                "price_book_id": "pb_ap_q2_2026",
                "version": "APAC-Q2-2026-LIVE",
                "region": "APAC",
                "status": "approved",
                "is_current": True,
                "effective_from": "2026-04-01",
                "entries": [
                    {"sku_id": "sku_lm_001", "price": 68.00},
                    {"sku_id": "sku_lm_002", "price": 72.00},
                    {"sku_id": "sku_lm_003", "price": 65.00},
                    {"sku_id": "sku_lm_004", "price": 42.00},
                    {"sku_id": "sku_lm_005", "price": 55.00}
                ]
            }
        ]
    }
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # ---- 额外干扰目录和文件 ----
    os.makedirs("logs", exist_ok=True)
    with open("logs/slow_query_20260401.log", "w") as f:
        f.write("# placeholder")

    # 创建 ops 目录（但不放任何文件，agent 需要自己写）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
