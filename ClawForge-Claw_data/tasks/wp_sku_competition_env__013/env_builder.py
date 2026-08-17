import os
import json
import random

def build_env():
    # Create required directories
    for d in ["data/brands", "data/skus", "data/pricing", "ops"]:
        os.makedirs(d, exist_ok=True)

    # --- Brands ---
    brands = [
        {"brand_id": "LS001", "brand_name": "LuminaSkin", "hero_category_id": "HC001",
         "hero_category_name": "Hydration Serum", "positioning": "Premium hydration", "region_focus": "APAC", "price_tier": "mid-premium"},
        {"brand_id": "AP001", "brand_name": "AquaPulse", "hero_category_id": "HC001",
         "hero_category_name": "Hydration Serum", "positioning": "Affordable hydration", "region_focus": "APAC", "price_tier": "mid"},
        {"brand_id": "DV001", "brand_name": "DermVeil", "hero_category_id": "HC002",
         "hero_category_name": "UV Moisturizer", "positioning": "Dermatologist endorsed", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "PL001", "brand_name": "PureLattice", "hero_category_id": "HC002",
         "hero_category_name": "UV Moisturizer", "positioning": "Clean beauty", "region_focus": "EU", "price_tier": "value"},
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # --- SKUs ---
    # LuminaSkin: 2 Hydration Serum, 1 UV Moisturizer (distractor)
    # AquaPulse: 3 Hydration Serum
    # DermVeil: 2 UV Moisturizer
    # PureLattice: 1 UV Moisturizer
    skus = [
        {"sku_id": "LS-HS-001", "brand_id": "LS001", "brand_name": "LuminaSkin", "category_id": "HC001",
         "category_name": "Hydration Serum", "sku_name": "HydraGlow Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Intense hydration", "Lightweight"], "ingredients": ["Hyaluronic Acid", "Glycerin"]},
        {"sku_id": "LS-HS-002", "brand_id": "LS001", "brand_name": "LuminaSkin", "category_id": "HC001",
         "category_name": "Hydration Serum", "sku_name": "Deep Hydra Boost", "size_value": 50, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Overnight repair"], "ingredients": ["Ceramides", "Niacinamide"]},
        {"sku_id": "LS-UV-001", "brand_id": "LS001", "brand_name": "LuminaSkin", "category_id": "HC002",
         "category_name": "UV Moisturizer", "sku_name": "UV Shield", "size_value": 30, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["SPF 50"], "ingredients": ["Zinc Oxide"]},
        {"sku_id": "AP-HS-001", "brand_id": "AP001", "brand_name": "AquaPulse", "category_id": "HC001",
         "category_name": "Hydration Serum", "sku_name": "Aqua Hydration", "size_value": 30, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Ocean minerals"], "ingredients": ["Seaweed Extract", "Aloe Vera"]},
        {"sku_id": "AP-HS-002", "brand_id": "AP001", "brand_name": "AquaPulse", "category_id": "HC001",
         "category_name": "Hydration Serum", "sku_name": "Ocean Burst", "size_value": 50, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Vitamin C boost"], "ingredients": ["Ascorbic Acid", "Ferulic Acid"]},
        {"sku_id": "AP-HS-003", "brand_id": "AP001", "brand_name": "AquaPulse", "category_id": "HC001",
         "category_name": "Hydration Serum", "sku_name": "Wave Soother", "size_value": 100, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Sensitive skin"], "ingredients": ["Oat Extract", "Panthenol"]},
        {"sku_id": "DV-UV-001", "brand_id": "DV001", "brand_name": "DermVeil", "category_id": "HC002",
         "category_name": "UV Moisturizer", "sku_name": "Sun Shield Pro", "size_value": 50, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Dermatologist tested"], "ingredients": ["Titanium Dioxide"]},
        {"sku_id": "PL-UV-001", "brand_id": "PL001", "brand_name": "PureLattice", "category_id": "HC002",
         "category_name": "UV Moisturizer", "sku_name": "Pure Sun", "size_value": 30, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Organic"], "ingredients": ["Coconut Oil"]},
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # --- Price Books ---
    # Current (live)
    current_entries = [
        {"sku_id": "LS-HS-001", "price": 24.99},
        {"sku_id": "LS-HS-002", "price": 29.99},
        {"sku_id": "LS-UV-001", "price": 19.99},
        {"sku_id": "AP-HS-001", "price": 22.50},
        {"sku_id": "AP-HS-002", "price": 25.99},
        {"sku_id": "AP-HS-003", "price": 28.50},
        {"sku_id": "DV-UV-001", "price": 35.00},
        {"sku_id": "PL-UV-001", "price": 18.00},
    ]
    # Archived (distractor – same SKUs but lower prices)
    archived_entries = [
        {"sku_id": "LS-HS-001", "price": 22.99},
        {"sku_id": "LS-HS-002", "price": 27.99},
        {"sku_id": "AP-HS-001", "price": 20.00},
        {"sku_id": "AP-HS-002", "price": 23.99},
        {"sku_id": "AP-HS-003", "price": 26.00},
        {"sku_id": "DV-UV-001", "price": 33.00},
    ]
    price_books = [
        {"price_book_id": "PB-APAC-Q2-2026", "version": "APAC-Q2-2026-LIVE", "region": "APAC",
         "status": "approved", "is_current": True, "effective_from": "2026-04-01",
         "entries": current_entries},
        {"price_book_id": "PB-APAC-Q1-2026", "version": "APAC-Q1-2026-ARCHIVE", "region": "APAC",
         "status": "archived", "is_current": False, "effective_from": "2026-01-01",
         "entries": archived_entries},
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # Create a placeholder for agent output directory
    open("ops/.gitkeep", "w").close()

if __name__ == "__main__":
    build_env()
