import os
import json

def build_env():
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)

    brands = {
        "brands": {
            "LUM01": {"brand_id": "LUM01", "brand_name": "LuminaSkin", "hero_category_id": "cat_hydra", "hero_category_name": "Hydration Serum", "positioning": "premium", "region_focus": "APAC", "price_tier": "premium"},
            "DER01": {"brand_id": "DER01", "brand_name": "DermVeil", "hero_category_id": "cat_hydra", "hero_category_name": "Hydration Serum", "positioning": "mid-premium", "region_focus": "APAC", "price_tier": "mid-premium"},
            "AQU01": {"brand_id": "AQU01", "brand_name": "AquaPulse", "hero_category_id": "cat_uv", "hero_category_name": "UV Moisturizer", "positioning": "value", "region_focus": "APAC", "price_tier": "value"},
            "PUR01": {"brand_id": "PUR01", "brand_name": "PureLattice", "hero_category_id": "cat_hydra", "hero_category_name": "Hydration Serum", "positioning": "premium", "region_focus": "APAC", "price_tier": "premium"},
            "SOL01": {"brand_id": "SOL01", "brand_name": "SolarOat", "hero_category_id": "cat_uv", "hero_category_name": "UV Moisturizer", "positioning": "value", "region_focus": "APAC", "price_tier": "value"}
        }
    }
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    skus = {
        "skus": {
            "LUM-HS-030": {"sku_id": "LUM-HS-030", "brand_id": "LUM01", "brand_name": "LuminaSkin", "category_id": "cat_hydra", "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Deep hydration", "Vitamin B5"], "ingredients": ["Water", "Hyaluronic Acid"]},
            "LUM-HS-050": {"sku_id": "LUM-HS-050", "brand_id": "LUM01", "brand_name": "LuminaSkin", "category_id": "cat_hydra", "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Serum 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Intense moisture", "Fast absorbing"], "ingredients": ["Water", "Glycerin", "Ceramide"]},
            "LUM-HS-075": {"sku_id": "LUM-HS-075", "brand_id": "LUM01", "brand_name": "LuminaSkin", "category_id": "cat_hydra", "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Serum 75ml", "size_value": 75, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["All-day hydration", "Lightweight"], "ingredients": ["Water", "Aloe Vera", "Vitamin E"]},
            "LUM-UV-100": {"sku_id": "LUM-UV-100", "brand_id": "LUM01", "brand_name": "LuminaSkin", "category_id": "cat_uv", "category_name": "UV Moisturizer", "sku_name": "Lumina UV Shield 100ml", "size_value": 100, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF 50", "Broad spectrum"], "ingredients": ["Zinc Oxide", "Titanium Dioxide"]},
            "LUM-HS-030-O": {"sku_id": "LUM-HS-030-O", "brand_id": "LUM01", "brand_name": "LuminaSkin", "category_id": "cat_hydra", "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Serum 30ml (Old Formula)", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["Basic hydration"], "ingredients": ["Water", "Alcohol"]},
            "DER-HS-030": {"sku_id": "DER-HS-030", "brand_id": "DER01", "brand_name": "DermVeil", "category_id": "cat_hydra", "category_name": "Hydration Serum", "sku_name": "DermVeil Hydra Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Barrier repair", "Ceramide rich"], "ingredients": ["Water", "Ceramides", "Niacinamide"]},
            "DER-HS-050": {"sku_id": "DER-HS-050", "brand_id": "DER01", "brand_name": "DermVeil", "category_id": "cat_hydra", "category_name": "Hydration Serum", "sku_name": "DermVeil Hydra Serum 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Soothing", "Redness reduction"], "ingredients": ["Water", "Oat Extract", "Panthenol"]},
            "DER-HS-075": {"sku_id": "DER-HS-075", "brand_id": "DER01", "brand_name": "DermVeil", "category_id": "cat_hydra", "category_name": "Hydration Serum", "sku_name": "DermVeil Hydra Serum 75ml", "size_value": 75, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Long-lasting moisture", "Non-greasy"], "ingredients": ["Water", "Squalane", "Glycerin"]},
            "DER-UV-100": {"sku_id": "DER-UV-100", "brand_id": "DER01", "brand_name": "DermVeil", "category_id": "cat_uv", "category_name": "UV Moisturizer", "sku_name": "DermVeil UV Shield 100ml", "size_value": 100, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF 30", "Moisturizing"], "ingredients": ["Avobenzone", "Octisalate"]},
            "DER-HS-030-O": {"sku_id": "DER-HS-030-O", "brand_id": "DER01", "brand_name": "DermVeil", "category_id": "cat_hydra", "category_name": "Hydration Serum", "sku_name": "DermVeil Hydra Serum 30ml (Old)", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["Basic"], "ingredients": ["Water", "Propylene Glycol"]},
            "AQU-UV-200": {"sku_id": "AQU-UV-200", "brand_id": "AQU01", "brand_name": "AquaPulse", "category_id": "cat_uv", "category_name": "UV Moisturizer", "sku_name": "AquaPulse UV Lotion 200ml", "size_value": 200, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Water resistant", "SPF 50+"], "ingredients": ["Homosalate", "Octocrylene"]},
            "PUR-HS-040": {"sku_id": "PUR-HS-040", "brand_id": "PUR01", "brand_name": "PureLattice", "category_id": "cat_hydra", "category_name": "Hydration Serum", "sku_name": "PureLattice Hydra Serum 40ml", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Anti-aging", "Firming"], "ingredients": ["Retinol", "Vitamin C"]},
            "SOL-UV-150": {"sku_id": "SOL-UV-150", "brand_id": "SOL01", "brand_name": "SolarOat", "category_id": "cat_uv", "category_name": "UV Moisturizer", "sku_name": "SolarOat Sun Milk 150ml", "size_value": 150, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Natural", "Mineral"], "ingredients": ["Zinc Oxide", "Coconut Oil"]}
        }
    }
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    price_books = {
        "price_books": {
            "PB-APAC-Q1-2026": {
                "price_book_id": "PB-APAC-Q1-2026",
                "version": "APAC-Q1-2026-ARCHIVE",
                "region": "APAC",
                "status": "archived",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": [
                    {"sku_id": "LUM-HS-030", "price": 22.99, "currency": "USD"},
                    {"sku_id": "LUM-HS-050", "price": 37.99, "currency": "USD"},
                    {"sku_id": "LUM-HS-075", "price": 52.99, "currency": "USD"},
                    {"sku_id": "LUM-HS-030-O", "price": 18.00, "currency": "USD"},
                    {"sku_id": "DER-HS-030", "price": 19.50, "currency": "USD"},
                    {"sku_id": "DER-HS-050", "price": 32.50, "currency": "USD"},
                    {"sku_id": "DER-HS-075", "price": 44.00, "currency": "USD"},
                    {"sku_id": "DER-HS-030-O", "price": 15.00, "currency": "USD"},
                    {"sku_id": "AQU-UV-200", "price": 14.99, "currency": "USD"}
                ]
            },
            "PB-APAC-Q2-2026": {
                "price_book_id": "PB-APAC-Q2-2026",
                "version": "APAC-Q2-2026-LIVE",
                "region": "APAC",
                "status": "approved",
                "is_current": True,
                "effective_from": "2026-04-01",
                "entries": [
                    {"sku_id": "LUM-HS-030", "price": 24.99, "currency": "USD"},
                    {"sku_id": "LUM-HS-050", "price": 39.99, "currency": "USD"},
                    {"sku_id": "LUM-HS-075", "price": 54.99, "currency": "USD"},
                    {"sku_id": "LUM-UV-100", "price": 19.99, "currency": "USD"},
                    {"sku_id": "DER-HS-030", "price": 21.50, "currency": "USD"},
                    {"sku_id": "DER-HS-050", "price": 34.50, "currency": "USD"},
                    {"sku_id": "DER-HS-075", "price": 47.00, "currency": "USD"},
                    {"sku_id": "DER-UV-100", "price": 18.00, "currency": "USD"},
                    {"sku_id": "AQU-UV-200", "price": 15.99, "currency": "USD"},
                    {"sku_id": "PUR-HS-040", "price": 45.00, "currency": "USD"},
                    {"sku_id": "SOL-UV-150", "price": 12.99, "currency": "USD"}
                ]
            }
        }
    }
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    with open("data/notes.txt", "w") as f:
        f.write("This folder contains log notes from previous analysis.\n")

if __name__ == "__main__":
    build_env()
