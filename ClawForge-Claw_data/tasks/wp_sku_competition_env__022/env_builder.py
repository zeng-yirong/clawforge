import json
import os

def build_env():
    # --- data/ ---
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    # 干扰目录
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)

    # --- brands.json ---
    brands = {
        "brands": [
            {"brand_id": "LUM", "brand_name": "LuminaSkin", "hero_category_id": "cat_hs",
             "hero_category_name": "Hydration Serum", "positioning": "Premium", "region_focus": "APAC", "price_tier": "premium"},
            {"brand_id": "DERM", "brand_name": "DermVeil", "hero_category_id": "cat_hs",
             "hero_category_name": "Hydration Serum", "positioning": "Dermatologist-recommended", "region_focus": "APAC", "price_tier": "mid-premium"},
            # 干扰品牌
            {"brand_id": "AQUA", "brand_name": "AquaPulse", "hero_category_id": "cat_uv",
             "hero_category_name": "UV Moisturizer", "positioning": "Everyday hydration", "region_focus": "Global", "price_tier": "mid"},
            {"brand_id": "PURE", "brand_name": "PureLattice", "hero_category_id": "cat_hs",
             "hero_category_name": "Hydration Serum", "positioning": "Clean beauty", "region_focus": "EMEA", "price_tier": "value"},
        ]
    }
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # --- skus.json ---
    skus = {
        "skus": [
            # LuminaSkin Hydration Serum (active)
            {"sku_id": "LS-HS-001", "brand_id": "LUM", "brand_name": "LuminaSkin", "category_id": "cat_hs",
             "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Boost", "size_value": 30, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["24h moisture", "lightweight"],
             "ingredients": ["hyaluronic acid", "vitamin B5", "glycerin"]},
            {"sku_id": "LS-HS-002", "brand_id": "LUM", "brand_name": "LuminaSkin", "category_id": "cat_hs",
             "category_name": "Hydration Serum", "sku_name": "Lumina Radiance Drop", "size_value": 50, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["brightening", "fades dark spots"],
             "ingredients": ["niacinamide", "vitamin C", "licorice root"]},
            # DermVeil Hydration Serum (active)
            {"sku_id": "DV-HS-001", "brand_id": "DERM", "brand_name": "DermVeil", "category_id": "cat_hs",
             "category_name": "Hydration Serum", "sku_name": "DermVeil Moisture Lock", "size_value": 30, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["ceramide complex", "sensitive skin safe"],
             "ingredients": ["ceramides", "peptides", "aloe vera"]},
            {"sku_id": "DV-HS-002", "brand_id": "DERM", "brand_name": "DermVeil", "category_id": "cat_hs",
             "category_name": "Hydration Serum", "sku_name": "DermVeil Barrier Repair", "size_value": 40, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["skin barrier repair", "clinical test"],
             "ingredients": ["panthenol", "allantoin", "oat kernel extract"]},
            # 干扰：其他品牌 Hydration Serum (active)
            {"sku_id": "PL-HS-001", "brand_id": "PURE", "brand_name": "PureLattice", "category_id": "cat_hs",
             "category_name": "Hydration Serum", "sku_name": "Pure Lattice Hydra", "size_value": 30, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["vegan", "organic"],
             "ingredients": ["squalane", "rose water", "green tea"]},
            # 干扰：LuminaSkin 其他类别 (UV Moisturizer)
            {"sku_id": "LS-UV-001", "brand_id": "LUM", "brand_name": "LuminaSkin", "category_id": "cat_uv",
             "category_name": "UV Moisturizer", "sku_name": "Lumina Sun Shield", "size_value": 50, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["SPF 50", "non-greasy"],
             "ingredients": ["zinc oxide", "titanium dioxide", "aloe"]},
            # 干扰：已停产 SKU (LuminaSkin Hydration Serum)
            {"sku_id": "LS-HS-003", "brand_id": "LUM", "brand_name": "LuminaSkin", "category_id": "cat_hs",
             "category_name": "Hydration Serum", "sku_name": "Lumina Old Formula", "size_value": 30, "size_unit": "ml",
             "pack_count": 1, "status": "discontinued", "selling_points": ["original formula"],
             "ingredients": ["water", "ethanol", "fragrance"]},
        ]
    }
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # --- price_books.json ---
    price_books = {
        "price_books": [
            {
                "price_book_id": "PB-APAC-Q1-2026",
                "version": "APAC-Q1-2026-ARCHIVE",
                "region": "APAC",
                "status": "approved",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": [
                    {"sku_id": "LS-HS-001", "price": 28.99},
                    {"sku_id": "LS-HS-002", "price": 33.99},
                    {"sku_id": "DV-HS-001", "price": 31.50},
                    {"sku_id": "DV-HS-002", "price": 26.99},
                    {"sku_id": "PL-HS-001", "price": 19.99}
                ]
            },
            {
                "price_book_id": "PB-APAC-Q2-2026",
                "version": "APAC-Q2-2026-LIVE",
                "region": "APAC",
                "status": "approved",
                "is_current": True,
                "effective_from": "2026-04-01",
                "entries": [
                    {"sku_id": "LS-HS-001", "price": 30.00},
                    {"sku_id": "LS-HS-002", "price": 35.00},
                    {"sku_id": "DV-HS-001", "price": 32.00},
                    {"sku_id": "DV-HS-002", "price": 28.00},
                    {"sku_id": "PL-HS-001", "price": 22.00},
                    {"sku_id": "LS-UV-001", "price": 18.00}
                ]
            }
        ]
    }
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # --- 干扰文件 ---
    # accounts.json (空)
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    # contacts.json (空)
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)

if __name__ == "__main__":
    build_env()
