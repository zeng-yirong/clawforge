import os
import json
import shutil

def build_env():
    # 清理已有内容
    for dir_name in ["data", "outputs"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # 创建目录
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # ========== brands ==========
    brands = [
        {"brand_id": "br_aquapulse", "brand_name": "AquaPulse", "hero_category_id": "cat_01", "hero_category_name": "Hydration Serum", "positioning": "mass", "region_focus": "APAC", "price_tier": "value"},
        {"brand_id": "br_lumina", "brand_name": "LuminaSkin", "hero_category_id": "cat_01", "hero_category_name": "Hydration Serum", "positioning": "premium", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "br_dermveil", "brand_name": "DermVeil", "hero_category_id": "cat_02", "hero_category_name": "UV Moisturizer", "positioning": "derm", "region_focus": "EMEA", "price_tier": "mid-premium"},
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # ========== SKUs ==========
    skus = [
        # LuminaSkin active Hydration Serum (目标)
        {"sku_id": "sku_ls_001", "brand_id": "br_lumina", "brand_name": "LuminaSkin", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Boost 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["24h hydration", "lightweight", "non-greasy"], "ingredients": ["Hyaluronic Acid", "Glycerin", "Niacinamide"]},
        {"sku_id": "sku_ls_002", "brand_id": "br_lumina", "brand_name": "LuminaSkin", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Boost 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["intense moisture", "soothing", "visible glow"], "ingredients": ["Hyaluronic Acid", "Ceramides", "Vitamin E"]},
        {"sku_id": "sku_ls_003", "brand_id": "br_lumina", "brand_name": "LuminaSkin", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Boost 75ml", "size_value": 75, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["all-day hydration", "barrier repair", "suitable for sensitive skin"], "ingredients": ["Hyaluronic Acid", "Panthenol", "Aloe Vera"]},
        {"sku_id": "sku_ls_004", "brand_id": "br_lumina", "brand_name": "LuminaSkin", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Boost 100ml", "size_value": 100, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["maximum hydration", "anti-aging", "plumping effect"], "ingredients": ["Hyaluronic Acid", "Peptides", "Collagen"]},
        # LuminaSkin discontinued (干扰)
        {"sku_id": "sku_ls_005", "brand_id": "br_lumina", "brand_name": "LuminaSkin", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Boost Trial 15ml", "size_value": 15, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["trial size", "travel friendly"], "ingredients": ["Hyaluronic Acid", "Glycerin"]},
        # LuminaSkin UV Moisturizer (不同类别，干扰)
        {"sku_id": "sku_ls_006", "brand_id": "br_lumina", "brand_name": "LuminaSkin", "category_id": "cat_02", "category_name": "UV Moisturizer", "sku_name": "LuminaSkin UV Shield 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF 50", "broad spectrum", "matte finish"], "ingredients": ["Zinc Oxide", "Titanium Dioxide"]},
        # AquaPulse active (其他品牌，干扰)
        {"sku_id": "sku_aq_001", "brand_id": "br_aquapulse", "brand_name": "AquaPulse", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "AquaPulse Splash 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["water burst", "fresh sensation"], "ingredients": ["Watermelon Extract", "Lactic Acid"]},
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ========== Price Books ==========
    price_books = [
        {
            "price_book_id": "pb_apac_q1_2026",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": False,   # 旧版，不是当前
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "sku_ls_001", "price": 19.99, "currency": "USD"},
                {"sku_id": "sku_ls_002", "price": 29.99, "currency": "USD"},
                {"sku_id": "sku_ls_003", "price": 39.99, "currency": "USD"},
                {"sku_id": "sku_ls_004", "price": 49.99, "currency": "USD"},
                {"sku_id": "sku_ls_005", "price": 9.99, "currency": "USD"},
                {"sku_id": "sku_aq_001", "price": 15.99, "currency": "USD"},
            ]
        },
        {
            "price_book_id": "pb_apac_q2_2026",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,    # 当前有效
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "sku_ls_001", "price": 21.99, "currency": "USD"},
                {"sku_id": "sku_ls_002", "price": 32.99, "currency": "USD"},
                {"sku_id": "sku_ls_003", "price": 43.99, "currency": "USD"},
                {"sku_id": "sku_ls_004", "price": 55.99, "currency": "USD"},
                {"sku_id": "sku_aq_001", "price": 16.99, "currency": "USD"},
            ]
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

if __name__ == "__main__":
    build_env()
