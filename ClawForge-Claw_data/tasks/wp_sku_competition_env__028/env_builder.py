import json
import os

def build_env():
    # Create directory structure
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty, agent will create file

    # brands.json
    brands = {
        "brands": [
            {
                "brand_id": "lum1",
                "brand_name": "LuminaSkin",
                "hero_category_id": "cat_hydro",
                "hero_category_name": "Hydration Serum",
                "positioning": "premium",
                "region_focus": "APAC",
                "price_tier": "premium"
            },
            {
                "brand_id": "aqua1",
                "brand_name": "AquaPulse",
                "hero_category_id": "cat_uv",
                "hero_category_name": "UV Moisturizer",
                "positioning": "mid",
                "region_focus": "NA",
                "price_tier": "mid"
            },
            {
                "brand_id": "derm1",
                "brand_name": "DermVeil",
                "hero_category_id": "cat_hydro",
                "hero_category_name": "Hydration Serum",
                "positioning": "value",
                "region_focus": "EU",
                "price_tier": "value"
            },
            {
                "brand_id": "pure1",
                "brand_name": "PureLattice",
                "hero_category_id": "cat_uv",
                "hero_category_name": "UV Moisturizer",
                "positioning": "mid-premium",
                "region_focus": "APAC",
                "price_tier": "mid-premium"
            },
            {
                "brand_id": "solar1",
                "brand_name": "SolarOat",
                "hero_category_id": "cat_hydro",
                "hero_category_name": "Hydration Serum",
                "positioning": "value",
                "region_focus": "APAC",
                "price_tier": "value"
            }
        ]
    }
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # skus.json
    skus = {
        "skus": [
            # Active LuminaSkin
            {
                "sku_id": "LS-HY-100",
                "brand_id": "lum1",
                "brand_name": "LuminaSkin",
                "category_id": "cat_hydro",
                "category_name": "Hydration Serum",
                "sku_name": "LuminaSkin Hydra Boost 100ml",
                "size_value": 100,
                "size_unit": "ml",
                "pack_count": 1,
                "status": "active",
                "selling_points": ["Deep hydration", "Lightweight"],
                "ingredients": ["Hyaluronic Acid", "Vitamin B5"]
            },
            {
                "sku_id": "LS-UV-50",
                "brand_id": "lum1",
                "brand_name": "LuminaSkin",
                "category_id": "cat_uv",
                "category_name": "UV Moisturizer",
                "sku_name": "LuminaSkin UV Shield 50ml",
                "size_value": 50,
                "size_unit": "ml",
                "pack_count": 1,
                "status": "active",
                "selling_points": ["SPF 50", "Non-greasy"],
                "ingredients": ["Zinc Oxide", "Aloe Vera"]
            },
            {
                "sku_id": "LS-HY-30",
                "brand_id": "lum1",
                "brand_name": "LuminaSkin",
                "category_id": "cat_hydro",
                "category_name": "Hydration Serum",
                "sku_name": "LuminaSkin Hydra Boost 30ml",
                "size_value": 30,
                "size_unit": "ml",
                "pack_count": 1,
                "status": "active",
                "selling_points": ["Travel size", "Quick absorption"],
                "ingredients": ["Hyaluronic Acid", "Niacinamide"]
            },
            # Discontinued LuminaSkin (must be excluded)
            {
                "sku_id": "LS-DIS-001",
                "brand_id": "lum1",
                "brand_name": "LuminaSkin",
                "category_id": "cat_hydro",
                "category_name": "Hydration Serum",
                "sku_name": "LuminaSkin Old Formula",
                "size_value": 100,
                "size_unit": "ml",
                "pack_count": 1,
                "status": "discontinued",
                "selling_points": ["Old"],
                "ingredients": ["Old ingredient"]
            },
            {
                "sku_id": "LS-DIS-002",
                "brand_id": "lum1",
                "brand_name": "LuminaSkin",
                "category_id": "cat_uv",
                "category_name": "UV Moisturizer",
                "sku_name": "LuminaSkin Sunblock Old",
                "size_value": 75,
                "size_unit": "ml",
                "pack_count": 1,
                "status": "discontinued",
                "selling_points": ["Old"],
                "ingredients": []
            },
            # Other brand SKU (must be excluded)
            {
                "sku_id": "AQ-HY-200",
                "brand_id": "aqua1",
                "brand_name": "AquaPulse",
                "category_id": "cat_hydro",
                "category_name": "Hydration Serum",
                "sku_name": "AquaPulse Hydra 200ml",
                "size_value": 200,
                "size_unit": "ml",
                "pack_count": 1,
                "status": "active",
                "selling_points": ["Cooling", "Refreshing"],
                "ingredients": ["Water", "Glycerin"]
            },
            {
                "sku_id": "DM-UV-30",
                "brand_id": "derm1",
                "brand_name": "DermVeil",
                "category_id": "cat_uv",
                "category_name": "UV Moisturizer",
                "sku_name": "DermVeil Sunscreen 30ml",
                "size_value": 30,
                "size_unit": "ml",
                "pack_count": 1,
                "status": "active",
                "selling_points": ["Gentle", "Hypoallergenic"],
                "ingredients": ["Titanium Dioxide", "Shea Butter"]
            }
        ]
    }
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # price_books.json
    price_books = {
        "price_books": [
            {
                "price_book_id": "pb_apac_q2_live",
                "version": "APAC-Q2-2026-LIVE",
                "region": "APAC",
                "status": "approved",
                "is_current": True,
                "effective_from": "2026-04-01",
                "entries": [
                    {"sku_id": "LS-HY-100", "unit_price": 49.99, "currency": "USD"},
                    {"sku_id": "LS-UV-50", "unit_price": 39.99, "currency": "USD"},
                    {"sku_id": "LS-HY-30", "unit_price": 29.99, "currency": "USD"}
                ]
            },
            {
                "price_book_id": "pb_apac_q1_archive",
                "version": "APAC-Q1-2026-ARCHIVE",
                "region": "APAC",
                "status": "archived",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": [
                    {"sku_id": "LS-DIS-001", "unit_price": 44.99, "currency": "USD"},
                    {"sku_id": "LS-DIS-002", "unit_price": 34.99, "currency": "USD"},
                    {"sku_id": "AQ-HY-200", "unit_price": 20.00, "currency": "USD"}
                ]
            },
            {
                "price_book_id": "pb_eu_q2_live",
                "version": "EU-Q2-2026-LIVE",
                "region": "EU",
                "status": "approved",
                "is_current": True,
                "effective_from": "2026-04-01",
                "entries": [
                    {"sku_id": "LS-HY-100", "unit_price": 45.00, "currency": "EUR"}
                ]
            }
        ]
    }
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # Decoy file to add noise
    decoy_attachments = {
        "attachments": [
            {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template", "description": "Template for category reviews"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(decoy_attachments, f, indent=2)

if __name__ == "__main__":
    build_env()
