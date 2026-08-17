import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("old_backups", exist_ok=True)  # 干扰目录

    # 1. 品牌数据
    brands = {
        "brands": [
            {"brand_id": "lumina_skin", "brand_name": "LuminaSkin", "hero_category_id": "cat_hs", "hero_category_name": "Hydration Serum", "positioning": "premium", "region_focus": "APAC", "price_tier": "premium"},
            {"brand_id": "derm_veil", "brand_name": "DermVeil", "hero_category_id": "cat_hs", "hero_category_name": "Hydration Serum", "positioning": "mid-premium", "region_focus": "APAC", "price_tier": "mid-premium"},
            {"brand_id": "aqua_pulse", "brand_name": "AquaPulse", "hero_category_id": "cat_uvm", "hero_category_name": "UV Moisturizer", "positioning": "value", "region_focus": "APAC", "price_tier": "value"}
        ]
    }
    with open("data/brands.json", "w") as f:
        json.dump(brands, f)

    # 2. SKU 数据 (包含干扰: inactive 和无关类别)
    skus = {
        "skus": [
            # LuminaSkin Hydration Serum (active)
            {"sku_id": "LS-HS-001", "brand_id": "lumina_skin", "brand_name": "LuminaSkin", "category_id": "cat_hs", "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Boost", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": [], "ingredients": []},
            {"sku_id": "LS-HS-002", "brand_id": "lumina_skin", "brand_name": "LuminaSkin", "category_id": "cat_hs", "category_name": "Hydration Serum", "sku_name": "Lumina Night Repair", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": [], "ingredients": []},
            {"sku_id": "LS-HS-003", "brand_id": "lumina_skin", "brand_name": "LuminaSkin", "category_id": "cat_hs", "category_name": "Hydration Serum", "sku_name": "Lumina Radiance Essence", "size_value": 30, "size_unit": "ml", "pack_count": 2, "status": "active", "selling_points": [], "ingredients": []},
            # LuminaSkin 另一个类别 (干扰)
            {"sku_id": "LS-UV-001", "brand_id": "lumina_skin", "brand_name": "LuminaSkin", "category_id": "cat_uvm", "category_name": "UV Moisturizer", "sku_name": "Lumina Sun Shield", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": [], "ingredients": []},
            # LuminaSkin inactive (干扰)
            {"sku_id": "LS-HS-004", "brand_id": "lumina_skin", "brand_name": "LuminaSkin", "category_id": "cat_hs", "category_name": "Hydration Serum", "sku_name": "Lumina Old Formula", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "inactive", "selling_points": [], "ingredients": []},
            # DermVeil Hydration Serum (active)
            {"sku_id": "DV-HS-001", "brand_id": "derm_veil", "brand_name": "DermVeil", "category_id": "cat_hs", "category_name": "Hydration Serum", "sku_name": "DermVeil Moisture Lock", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": [], "ingredients": []},
            {"sku_id": "DV-HS-002", "brand_id": "derm_veil", "brand_name": "DermVeil", "category_id": "cat_hs", "category_name": "Hydration Serum", "sku_name": "DermVeil Hydra Glow", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": [], "ingredients": []},
            # AquaPulse (干扰品牌，类别不同)
            {"sku_id": "AP-UV-001", "brand_id": "aqua_pulse", "brand_name": "AquaPulse", "category_id": "cat_uvm", "category_name": "UV Moisturizer", "sku_name": "AquaPulse Sun Gel", "size_value": 100, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": [], "ingredients": []}
        ]
    }
    with open("data/skus.json", "w") as f:
        json.dump(skus, f)

    # 3. 价格书 (两个版本)
    price_books = {
        "price_books": [
            {
                "price_book_id": "pb_apac_q1_2026",
                "version": "APAC-Q1-2026-ARCHIVE",
                "region": "APAC",
                "status": "archived",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": [
                    {"sku_id": "LS-HS-001", "price": 45.0, "currency": "USD"},
                    {"sku_id": "LS-HS-002", "price": 58.0, "currency": "USD"},
                    {"sku_id": "LS-HS-003", "price": 72.0, "currency": "USD"},
                    {"sku_id": "DV-HS-001", "price": 42.0, "currency": "USD"},
                    {"sku_id": "DV-HS-002", "price": 55.0, "currency": "USD"}
                ]
            },
            {
                "price_book_id": "pb_apac_q2_2026",
                "version": "APAC-Q2-2026-LIVE",
                "region": "APAC",
                "status": "approved",
                "is_current": True,
                "effective_from": "2026-04-01",
                "entries": [
                    {"sku_id": "LS-HS-001", "price": 48.0, "currency": "USD"},
                    {"sku_id": "LS-HS-002", "price": 62.0, "currency": "USD"},
                    {"sku_id": "LS-HS-003", "price": 79.0, "currency": "USD"},
                    {"sku_id": "DV-HS-001", "price": 44.0, "currency": "USD"},
                    {"sku_id": "DV-HS-002", "price": 59.0, "currency": "USD"}
                ]
            }
        ]
    }
    with open("data/price_books.json", "w") as f:
        json.dump(price_books, f)

    # 4. 干扰文件
    with open("old_backups/notes.txt", "w") as f:
        f.write("This is old scratchpad, ignore.\n")
    with open("data/extraneous_cache.json", "w") as f:
        json.dump({"temp": "dummy"}, f)
    with open("data/.hidden_pricing_draft.json", "w") as f:
        json.dump({"draft": True}, f)

if __name__ == "__main__":
    build_env()
