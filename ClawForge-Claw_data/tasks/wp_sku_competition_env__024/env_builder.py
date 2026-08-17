import os
import json
import random

def build_env():
    # Ensure directories exist
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ========== Brands ==========
    # Two brands: LuminaSkin (target) and DermVeil (distractor)
    # Also include a brand with similar naming to test filtering
    brands = [
        {
            "brand_id": "BR-LUM-001",
            "brand_name": "LuminaSkin",
            "hero_category_id": "CAT-HYDR-01",
            "hero_category_name": "Hydration Serum",
            "positioning": "Premium brightening",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "BR-DER-002",
            "brand_name": "DermVeil",
            "hero_category_id": "CAT-UV-02",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Dermatological protection",
            "region_focus": "APAC",
            "price_tier": "mid-premium"
        },
        # Distractor: old brand that no longer exists but still in file
        {
            "brand_id": "BR-LUM-OLD",
            "brand_name": "LuminaSkin Pro",
            "hero_category_id": "CAT-HYDR-01",
            "hero_category_name": "Hydration Serum",
            "positioning": "Legacy line",
            "region_focus": "APAC",
            "price_tier": "mid"
        }
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # ========== SKUs ==========
    # LuminaSkin active SKUs: 3 items with known prices (will match price book)
    # LuminaSkin discontinued SKU: 1 item (should be excluded)
    # DermVeil SKUs: some active (should be excluded by brand filter)
    skus = [
        # LuminaSkin active
        {"sku_id": "SKU-LUM-001", "brand_id": "BR-LUM-001", "brand_name": "LuminaSkin",
         "category_id": "CAT-HYDR-01", "category_name": "Hydration Serum",
         "sku_name": "Brightening Glow Serum", "size_value": 30, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["Vitamin C", "Niacinamide"], "ingredients": ["Ascorbic Acid", "Niacinamide", "Hyaluronic Acid"]},
        {"sku_id": "SKU-LUM-002", "brand_id": "BR-LUM-001", "brand_name": "LuminaSkin",
         "category_id": "CAT-HYDR-01", "category_name": "Hydration Serum",
         "sku_name": "Radiance Booster", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["Peptides", "Squalane"], "ingredients": ["Palmitoyl Tripeptide-1", "Squalane", "Ceramides"]},
        {"sku_id": "SKU-LUM-003", "brand_id": "BR-LUM-001", "brand_name": "LuminaSkin",
         "category_id": "CAT-UV-02", "category_name": "UV Moisturizer",
         "sku_name": "Sun Shield SPF50", "size_value": 40, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["Broad Spectrum", "Matte Finish"], "ingredients": ["Zinc Oxide", "Titanium Dioxide", "Aloe Vera"]},
        # LuminaSkin discontinued (distractor)
        {"sku_id": "SKU-LUM-004", "brand_id": "BR-LUM-001", "brand_name": "LuminaSkin",
         "category_id": "CAT-HYDR-01", "category_name": "Hydration Serum",
         "sku_name": "Legacy Nourish", "size_value": 30, "size_unit": "ml",
         "pack_count": 1, "status": "discontinued",
         "selling_points": ["Old formula"], "ingredients": ["Water", "Glycerin"]},
        # DermVeil active (distractor)
        {"sku_id": "SKU-DER-001", "brand_id": "BR-DER-002", "brand_name": "DermVeil",
         "category_id": "CAT-UV-02", "category_name": "UV Moisturizer",
         "sku_name": "Protect+SPF30", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["Lightweight"], "ingredients": ["Avobenzone", "Octocrylene"]},
        # Extra distractor: SKU with brand_id that matches old brand name (should be ignored because brand_id differs)
        {"sku_id": "SKU-LUM-005", "brand_id": "BR-LUM-OLD", "brand_name": "LuminaSkin Pro",
         "category_id": "CAT-HYDR-01", "category_name": "Hydration Serum",
         "sku_name": "Pro Serum", "size_value": 30, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["Advanced"], "ingredients": ["Retinol"]}
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ========== Price Books ==========
    # Only one should be current and approved: APAC-Q2-2026-LIVE
    # Contains entries for LuminaSkin active SKUs (prices match later calculations)
    # Also include entries for DermVeil and for discontinued SKUs (should be excluded)
    # Also include an archived version (Q1) with different prices and discontinued SKU price
    live_entries = [
        {"sku_id": "SKU-LUM-001", "retail_price": 29.99, "currency": "USD"},
        {"sku_id": "SKU-LUM-002", "retail_price": 39.99, "currency": "USD"},
        {"sku_id": "SKU-LUM-003", "retail_price": 24.99, "currency": "USD"},
        # DermVeil entry (should not appear in LuminaSkin report)
        {"sku_id": "SKU-DER-001", "retail_price": 19.99, "currency": "USD"},
        # Old SKU (discontinued) price – should not be included because SKU is not active
        {"sku_id": "SKU-LUM-004", "retail_price": 14.99, "currency": "USD"}
    ]
    archived_entries = [
        {"sku_id": "SKU-LUM-001", "retail_price": 27.50, "currency": "USD"},
        {"sku_id": "SKU-LUM-002", "retail_price": 37.00, "currency": "USD"},
        {"sku_id": "SKU-LUM-003", "retail_price": 22.50, "currency": "USD"},
        {"sku_id": "SKU-LUM-004", "retail_price": 12.99, "currency": "USD"}
    ]
    price_books = [
        {
            "price_book_id": "PB-APAC-Q2-2026",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": live_entries
        },
        {
            "price_book_id": "PB-APAC-Q1-2026",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": archived_entries
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # ========== Distractor files ==========
    # Add some irrelevant CSVs to test focus
    with open("data/inventory_backup.csv", "w") as f:
        f.write("sku,warehouse,qty\nSKU-LUM-001,WH01,100\nSKU-DER-001,WH02,50\n")
    with open("data/notes_old.txt", "w") as f:
        f.write("This is an old note about Q1 pricing.\n")

if __name__ == "__main__":
    build_env()
