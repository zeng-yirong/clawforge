import os
import json

def build_env():
    # Create necessary directories
    for d in ["data", "data/pricing", "attachments", "reports"]:
        os.makedirs(d, exist_ok=True)

    # ==================== data/brands.json ====================
    brands = [
        {"brand_id": "BR-LS", "brand_name": "LuminaSkin", "hero_category_id": "CAT-HYDRATION", "hero_category_name": "Hydration Serum", "positioning": "Premium derma", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "BR-AP", "brand_name": "AquaPulse", "hero_category_id": "CAT-HYDRATION", "hero_category_name": "Hydration Serum", "positioning": "Hydration experts", "region_focus": "APAC", "price_tier": "mid-premium"},
        {"brand_id": "BR-DV", "brand_name": "DermVeil", "hero_category_id": "CAT-HYDRATION", "hero_category_name": "Hydration Serum", "positioning": "Barrier care", "region_focus": "APAC", "price_tier": "mid"},
        {"brand_id": "BR-PL", "brand_name": "PureLattice", "hero_category_id": "CAT-UV", "hero_category_name": "UV Moisturizer", "positioning": "Mineral protect", "region_focus": "APAC", "price_tier": "value"},
        {"brand_id": "BR-SO", "brand_name": "SolarOat", "hero_category_id": "CAT-HYDRATION", "hero_category_name": "Hydration Serum", "positioning": "Natural glow", "region_focus": "APAC", "price_tier": "mid"}
    ]
    with open("data/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # ==================== data/skus.json (includes duplicate for LS-001) ====================
    skus = [
        # LuminaSkin
        {"sku_id": "LS-001", "brand_id": "BR-LS", "brand_name": "LuminaSkin", "category_name": "Hydration Serum", "sku_name": "HydraBoost Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Intense hydration", "Fast absorption"], "ingredients": ["Hyaluronic Acid", "Vitamin B5"]},
        # duplicate (inactive)
        {"sku_id": "LS-001", "brand_id": "BR-LS", "brand_name": "LuminaSkin", "category_name": "Hydration Serum", "sku_name": "HydraBoost Serum (old batch)", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "inactive", "selling_points": ["Intense hydration"], "ingredients": ["Hyaluronic Acid"]},
        {"sku_id": "LS-002", "brand_id": "BR-LS", "brand_name": "LuminaSkin", "category_name": "Hydration Serum", "sku_name": "Glow Elixir", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Brightening", "Anti-aging"], "ingredients": ["Niacinamide", "Peptides"]},
        {"sku_id": "LS-003", "brand_id": "BR-LS", "brand_name": "LuminaSkin", "category_name": "UV Moisturizer", "sku_name": "Night Repair Serum", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Night recovery"], "ingredients": ["Retinol", "Ceramides"]},
        # AquaPulse
        {"sku_id": "AP-001", "brand_id": "BR-AP", "brand_name": "AquaPulse", "category_name": "Hydration Serum", "sku_name": "Aqua Burst", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Instant moisture burst", "Lightweight"], "ingredients": ["Water Lily Extract", "Glycerin"]},
        {"sku_id": "AP-002", "brand_id": "BR-AP", "brand_name": "AquaPulse", "category_name": "Hydration Serum", "sku_name": "Ocean Dew", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Deep ocean minerals", "pH balanced"], "ingredients": ["Sea Salt", "Algae Extract"]},
        # DermVeil
        {"sku_id": "DV-001", "brand_id": "BR-DV", "brand_name": "DermVeil", "category_name": "Hydration Serum", "sku_name": "Veil Hydrator", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Barrier support", "Soothing"], "ingredients": ["Ceramides", "Panthenol"]},
        {"sku_id": "DV-002", "brand_id": "BR-DV", "brand_name": "DermVeil", "category_name": "Hydration Serum", "sku_name": "Barrier Plus", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "inactive", "selling_points": ["Extra barrier"], "ingredients": ["Niacinamide", "Zinc"]},
        # PureLattice (wrong category)
        {"sku_id": "PL-001", "brand_id": "BR-PL", "brand_name": "PureLattice", "category_name": "UV Moisturizer", "sku_name": "Lattice Shield", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Mineral UV filter", "Matte finish"], "ingredients": ["Zinc Oxide", "Titanium Dioxide"]},
        # SolarOat (inactive)
        {"sku_id": "SO-001", "brand_id": "BR-SO", "brand_name": "SolarOat", "category_name": "Hydration Serum", "sku_name": "Sun Glow", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "inactive", "selling_points": ["Natural glow", "SPF 15"], "ingredients": ["Oat Extract", "Vitamin E"]}
    ]
    with open("data/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ==================== data/pricing/price_books.json ====================
    price_books = [
        {
            "price_book_id": "PB-APAC-Q2-2026",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "LS-001", "list_price": 39.99, "currency": "USD"},
                {"sku_id": "LS-002", "list_price": 54.99, "currency": "USD"},
                {"sku_id": "AP-001", "list_price": 29.99, "currency": "USD"},
                {"sku_id": "AP-002", "list_price": 34.99, "currency": "USD"},
                {"sku_id": "DV-001", "list_price": 44.99, "currency": "USD"}
            ]
        },
        {
            "price_book_id": "PB-APAC-Q1-2026",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "LS-001", "list_price": 37.99, "currency": "USD"},
                {"sku_id": "LS-002", "list_price": 52.99, "currency": "USD"},
                {"sku_id": "AP-001", "list_price": 27.99, "currency": "USD"},
                {"sku_id": "XX-000", "list_price": 99.99, "currency": "USD"}  # orphan entry
            ]
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # ==================== attachments/category_review_template.md ====================
    template = """# Category Review: {category}
## Competitive Landscape
| Brand | SKU Name | Price | Key Selling Points | Ingredients |
|-------|----------|-------|-------------------|-------------|
| ...   | ...      | ...   | ...               | ...         |
## Summary
- Total active SKUs: N
- Average price: $
"""
    with open("attachments/category_review_template.md", "w") as f:
        f.write(template)

if __name__ == "__main__":
    build_env()
