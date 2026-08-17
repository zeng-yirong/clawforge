import os
import json
import random
random.seed(42)

def build_env():
    # ----- brands -----
    brands = {
        "LuminaSkin": {
            "brand_id": "lum",
            "brand_name": "LuminaSkin",
            "hero_category_id": "cat_hydration_serum",
            "hero_category_name": "Hydration Serum",
            "positioning": "premium clinical",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        "AquaPulse": {
            "brand_id": "aqua",
            "brand_name": "AquaPulse",
            "hero_category_id": "cat_hydration_serum",
            "hero_category_name": "Hydration Serum",
            "positioning": "mass hydrating",
            "region_focus": "APAC",
            "price_tier": "mid"
        },
        "DermVeil": {
            "brand_id": "derm",
            "brand_name": "DermVeil",
            "hero_category_id": "cat_hydration_serum",
            "hero_category_name": "Hydration Serum",
            "positioning": "derm-recommended",
            "region_focus": "APAC",
            "price_tier": "mid-premium"
        }
    }
    # extra brand as distractor
    brands["PureLattice"] = {
        "brand_id": "pure",
        "brand_name": "PureLattice",
        "hero_category_id": "cat_uv_moisturizer",
        "hero_category_name": "UV Moisturizer",
        "positioning": "clean beauty",
        "region_focus": "APAC",
        "price_tier": "value"
    }

    os.makedirs("data/brands", exist_ok=True)
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": list(brands.values())}, f, indent=2)

    # ----- skus -----
    # categories: Hydration Serum (cat_hydration_serum) and UV Moisturizer (cat_uv_moisturizer)
    skus = []
    # LuminaSkin Hydration Serum active (3)
    lum_skus = [
        ("lum", "LS-001", "LuminaSkin HydraGlow", 55.0, "active"),
        ("lum", "LS-002", "LuminaSkin AquaBurst", 44.0, "active"),
        ("lum", "LS-003", "LuminaSkin PlumpShot", 60.0, "active"),
    ]
    # LuminaSkin discontinued
    lum_skus.append(("lum", "LS-004", "LuminaSkin OldFormula", 20.0, "discontinued"))
    for brand_id, sku_id, name, price, status in lum_skus:
        skus.append({
            "sku_id": sku_id,
            "brand_id": brand_id,
            "brand_name": "LuminaSkin",
            "category_id": "cat_hydration_serum",
            "category_name": "Hydration Serum",
            "sku_name": name,
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": status,
            "selling_points": ["hydrating", "brightening"],
            "ingredients": ["hyaluronic acid", "niacinamide"]
        })
    # AquaPulse active Hydration Serum
    aqua_skus = [
        ("aqua", "AQ-001", "AquaPulse FreshDew", 35.0, "active"),
        ("aqua", "AQ-002", "AquaPulse OceanMist", 40.0, "active"),
    ]
    for brand_id, sku_id, name, price, status in aqua_skus:
        skus.append({
            "sku_id": sku_id,
            "brand_id": brand_id,
            "brand_name": "AquaPulse",
            "category_id": "cat_hydration_serum",
            "category_name": "Hydration Serum",
            "sku_name": name,
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": status,
            "selling_points": ["lightweight", "oil-free"],
            "ingredients": ["glycerin", "water"]
        })
    # DermVeil active Hydration Serum
    derm_skus = [
        ("derm", "DV-001", "DermVeil BarrierShield", 42.0, "active"),
        ("derm", "DV-002", "DermVeil CalmWater", 38.0, "active"),
    ]
    for brand_id, sku_id, name, price, status in derm_skus:
        skus.append({
            "sku_id": sku_id,
            "brand_id": brand_id,
            "brand_name": "DermVeil",
            "category_id": "cat_hydration_serum",
            "category_name": "Hydration Serum",
            "sku_name": name,
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": status,
            "selling_points": ["ceramide", "soothing"],
            "ingredients": ["ceramide NP", "panthenol"]
        })
    # Distractor: UV Moisturizer SKUs for AquaPulse and DermVeil
    distractor_skus = [
        ("aqua", "AQ-003", "AquaPulse SunShield", 28.0, "active", "cat_uv_moisturizer", "UV Moisturizer"),
        ("derm", "DV-003", "DermVeil UVGuard", 32.0, "active", "cat_uv_moisturizer", "UV Moisturizer"),
    ]
    for brand_id, sku_id, name, price, status, cat_id, cat_name in distractor_skus:
        skus.append({
            "sku_id": sku_id,
            "brand_id": brand_id,
            "brand_name": "AquaPulse" if brand_id == "aqua" else "DermVeil",
            "category_id": cat_id,
            "category_name": cat_name,
            "sku_name": name,
            "size_value": 50,
            "size_unit": "ml",
            "pack_count": 1,
            "status": status,
            "selling_points": ["SPF 30"],
            "ingredients": ["zinc oxide"]
        })

    os.makedirs("data/skus", exist_ok=True)
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ----- price books -----
    # archived Q1 (is_current=False)
    archived_entries = [
        {"sku_id": "LS-001", "price": 50.0, "currency": "USD"},
        {"sku_id": "LS-002", "price": 41.0, "currency": "USD"},
        {"sku_id": "AQ-001", "price": 33.0, "currency": "USD"},
        {"sku_id": "AQ-002", "price": 38.0, "currency": "USD"},
        {"sku_id": "DV-001", "price": 40.0, "currency": "USD"},
        {"sku_id": "DV-002", "price": 36.0, "currency": "USD"},
    ]
    # live Q2 (is_current=True)
    live_entries = [
        {"sku_id": "LS-001", "price": 55.0, "currency": "USD"},
        {"sku_id": "LS-002", "price": 44.0, "currency": "USD"},
        {"sku_id": "LS-003", "price": 60.0, "currency": "USD"},
        {"sku_id": "AQ-001", "price": 35.0, "currency": "USD"},
        {"sku_id": "AQ-002", "price": 40.0, "currency": "USD"},
        {"sku_id": "DV-001", "price": 42.0, "currency": "USD"},
        {"sku_id": "DV-002", "price": 38.0, "currency": "USD"},
    ]
    price_books = [
        {
            "price_book_id": "pb_archived_q1",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": archived_entries
        },
        {
            "price_book_id": "pb_live_q2",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": live_entries
        }
    ]
    os.makedirs("data/pricing", exist_ok=True)
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # ----- dummy attachment (distractor) -----
    os.makedirs("data", exist_ok=True)
    with open("data/attachments.json", "w") as f:
        json.dump({
            "attachments": [
                {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template", "description": "Template for Q2 category review"},
                {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice", "description": "Notice about price book update"}
            ]
        }, f, indent=2)

    # ensure target output directory exists
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
