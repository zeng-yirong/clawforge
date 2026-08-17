import json
import os

def build_env():
    # ---------- brands ----------
    brands = {
        "brands": [
            {"brand_id": "LUM01", "brand_name": "LuminaSkin", "hero_category_id": "CAT-HS", "hero_category_name": "Hydration Serum", "positioning": "Premium", "region_focus": "APAC", "price_tier": "premium"},
            {"brand_id": "PL01", "brand_name": "PureLattice", "hero_category_id": "CAT-HS", "hero_category_name": "Hydration Serum", "positioning": "Mid-premium", "region_focus": "APAC", "price_tier": "mid-premium"},
            {"brand_id": "AQ01", "brand_name": "AquaPulse", "hero_category_id": "CAT-HS", "hero_category_name": "Hydration Serum", "positioning": "Value", "region_focus": "APAC", "price_tier": "value"},
            {"brand_id": "DV01", "brand_name": "DermVeil", "hero_category_id": "CAT-UV", "hero_category_name": "UV Moisturizer", "positioning": "Premium", "region_focus": "EMEA", "price_tier": "premium"}
        ]
    }
    os.makedirs("brands", exist_ok=True)
    with open("brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # ---------- categories (not strictly required but for reference) ----------
    # We'll embed categories in skus directly.

    # ---------- skus ----------
    skus = {
        "skus": [
            # LuminaSkin - Hydration Serum (active)
            {"sku_id": "LUM-HS-001", "brand_id": "LUM01", "brand_name": "LuminaSkin", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Boost 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["deep hydration"], "ingredients": ["hyaluronic acid"]},
            {"sku_id": "LUM-HS-002", "brand_id": "LUM01", "brand_name": "LuminaSkin", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Boost 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["deep hydration"], "ingredients": ["hyaluronic acid"]},
            # LuminaSkin - Hydration Serum (discontinued – should be excluded)
            {"sku_id": "LUM-HS-003", "brand_id": "LUM01", "brand_name": "LuminaSkin", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Boost 75ml (old)", "size_value": 75, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["deep hydration"], "ingredients": ["hyaluronic acid"]},
            # PureLattice - Hydration Serum (active)
            {"sku_id": "PL-HS-001", "brand_id": "PL01", "brand_name": "PureLattice", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "PureLattice Hydro Gel 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["lightweight"], "ingredients": ["glycerin"]},
            {"sku_id": "PL-HS-002", "brand_id": "PL01", "brand_name": "PureLattice", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "PureLattice Hydro Gel 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["lightweight"], "ingredients": ["glycerin"]},
            # AquaPulse (not in scope) - active
            {"sku_id": "AQ-HS-001", "brand_id": "AQ01", "brand_name": "AquaPulse", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "AquaPulse Splash 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["refresh"], "ingredients": ["water"]},
            # other category
            {"sku_id": "DV-UV-001", "brand_id": "DV01", "brand_name": "DermVeil", "category_id": "CAT-UV", "category_name": "UV Moisturizer", "sku_name": "DermVeil Sun Shield 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF50"], "ingredients": ["zinc oxide"]}
        ]
    }
    os.makedirs("skus", exist_ok=True)
    with open("skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # ---------- price books ----------
    # Entries: list of {sku_id, price}
    price_books = {
        "price_books": [
            {
                "price_book_id": "PB-APAC-Q1-2026",
                "version": "APAC-Q1-2026-ARCHIVE",
                "region": "APAC",
                "status": "archived",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": [
                    {"sku_id": "LUM-HS-001", "price": 23.0},
                    {"sku_id": "LUM-HS-002", "price": 34.0},
                    {"sku_id": "LUM-HS-003", "price": 48.0},
                    {"sku_id": "PL-HS-001", "price": 20.0},
                    {"sku_id": "PL-HS-002", "price": 30.0},
                    {"sku_id": "AQ-HS-001", "price": 12.0}
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
                    {"sku_id": "LUM-HS-001", "price": 25.0},
                    {"sku_id": "LUM-HS-002", "price": 36.0},
                    # LUM-HS-003 not in current price book (discontinued)
                    {"sku_id": "PL-HS-001", "price": 22.0},
                    {"sku_id": "PL-HS-002", "price": 32.0},
                    {"sku_id": "AQ-HS-001", "price": 13.0}
                ]
            }
        ]
    }
    os.makedirs("pricing", exist_ok=True)
    with open("pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # ---------- attachments (optional flavor) ----------
    attachments = {
        "attachments": [
            {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template", "description": "Standard template for category comparison reports"},
            {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice", "description": "Notice about current APAC Q2 2026 price book"}
        ]
    }
    os.makedirs("attachments", exist_ok=True)
    with open("attachments/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # ---------- distractor: stale logs ----------
    os.makedirs("raw_logs", exist_ok=True)
    with open("raw_logs/price_load_2025.log", "w") as f:
        f.write("[2025-12-01] Loaded APAC-Q4-2025 price book\n")
    with open("raw_logs/price_load_2026.log", "w") as f:
        f.write("[2026-03-15] Loaded APAC-Q1-2026-ARCHIVE\n")

    # ---------- distractor: outdated brand forecast ----------
    os.makedirs("forecasts", exist_ok=True)
    with open("forecasts/old_brand_forecast.csv", "w") as f:
        f.write("brand,forecast_q1_2026\nLuminaSkin,100000\nPureLattice,80000\n")

if __name__ == "__main__":
    build_env()
