import os
import json
import math

def build_env():
    # ---- brands ----
    os.makedirs("brands", exist_ok=True)
    brands = [
        {
            "brand_id": "BR-LS-01",
            "brand_name": "LuminaSkin",
            "hero_category_id": "CAT-HYDRATION",
            "hero_category_name": "Hydration Serum",
            "positioning": "luxury",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "BR-DV-02",
            "brand_name": "DermVeil",
            "hero_category_id": "CAT-HYDRATION",
            "hero_category_name": "Hydration Serum",
            "positioning": "clinical",
            "region_focus": "APAC",
            "price_tier": "mid-premium"
        },
        {
            "brand_id": "BR-AP-03",
            "brand_name": "AquaPulse",
            "hero_category_id": "CAT-UV",
            "hero_category_name": "UV Moisturizer",
            "positioning": "mass",
            "region_focus": "APAC",
            "price_tier": "value"
        }
    ]
    with open("brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # ---- skus ----
    os.makedirs("skus", exist_ok=True)
    skus = [
        # LuminaSkin Hydration Serum (active)
        {"sku_id": "LS-001", "brand_id": "BR-LS-01", "brand_name": "LuminaSkin", "category_id": "CAT-HYDRATION", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Boost", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["deep hydration", "lightweight"], "ingredients": ["hyaluronic acid", "glycerin"]},
        {"sku_id": "LS-002", "brand_id": "BR-LS-01", "brand_name": "LuminaSkin", "category_id": "CAT-HYDRATION", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Plump & Glow", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["plumping", "radiance"], "ingredients": ["niacinamide", "ceramides"]},
        {"sku_id": "LS-003", "brand_id": "BR-LS-01", "brand_name": "LuminaSkin", "category_id": "CAT-HYDRATION", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Dew Drops", "size_value": 30, "size_unit": "ml", "pack_count": 2, "status": "active", "selling_points": ["dewy finish", "quick absorption"], "ingredients": ["peptides", "squalane"]},
        # LuminaSkin UV Moisturizer (distractor – wrong category)
        {"sku_id": "LS-004", "brand_id": "BR-LS-01", "brand_name": "LuminaSkin", "category_id": "CAT-UV", "category_name": "UV Moisturizer", "sku_name": "LuminaSkin Sun Shield", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF50", "lightweight"], "ingredients": ["zinc oxide", "vitamin E"]},
        # LuminaSkin discontinued (old version of LS-001)
        {"sku_id": "LS-001", "brand_id": "BR-LS-01", "brand_name": "LuminaSkin", "category_id": "CAT-HYDRATION", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Boost (v1)", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["deep hydration"], "ingredients": ["hyaluronic acid"]},
        # DermVeil Hydration Serum (active)
        {"sku_id": "DV-101", "brand_id": "BR-DV-02", "brand_name": "DermVeil", "category_id": "CAT-HYDRATION", "category_name": "Hydration Serum", "sku_name": "DermVeil Repair Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["repair", "calming"], "ingredients": ["centella asiatica", "peptides"]},
        {"sku_id": "DV-102", "brand_id": "BR-DV-02", "brand_name": "DermVeil", "category_id": "CAT-HYDRATION", "category_name": "Hydration Serum", "sku_name": "DermVeil Hydra Barrier", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["barrier support", "moisture lock"], "ingredients": ["ceramides", "beta-glucan"]},
        # DermVeil UV Moisturizer (distractor)
        {"sku_id": "DV-103", "brand_id": "BR-DV-02", "brand_name": "DermVeil", "category_id": "CAT-UV", "category_name": "UV Moisturizer", "sku_name": "DermVeil UV Defend", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF40", "matte"], "ingredients": ["titanium dioxide", "glycerin"]},
        # AquaPulse (irrelevant brand)
        {"sku_id": "AP-001", "brand_id": "BR-AP-03", "brand_name": "AquaPulse", "category_id": "CAT-UV", "category_name": "UV Moisturizer", "sku_name": "AquaPulse Daily UV", "size_value": 60, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["affordable", "SPF30"], "ingredients": ["avobenzone", "aloe"]}
    ]
    with open("skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # ---- pricing ----
    os.makedirs("pricing", exist_ok=True)
    price_books = [
        {
            "price_book_id": "PB-APAC-Q1-ARCHIVE",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "LS-001", "price": 22.50},
                {"sku_id": "DV-101", "price": 23.00}
            ]
        },
        {
            "price_book_id": "PB-APAC-Q2-LIVE",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "LS-001", "price": 24.99},
                {"sku_id": "LS-002", "price": 26.50},
                {"sku_id": "LS-003", "price": 27.50},
                {"sku_id": "DV-101", "price": 25.49},
                {"sku_id": "DV-102", "price": 29.49},
                {"sku_id": "LS-004", "price": 19.99},   # UV Moisturizer – should be excluded by category
                {"sku_id": "DV-103", "price": 28.00},   # UV Moisturizer – should be excluded
                {"sku_id": "AP-001", "price": 14.50}    # AquaPulse – irrelevant brand
            ]
        }
    ]
    with open("pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # ---- extra distractor files ----
    os.makedirs("logs", exist_ok=True)
    with open("logs/backup_readme.txt", "w") as f:
        f.write("This directory contains old session logs. Ignore.")

if __name__ == "__main__":
    build_env()
