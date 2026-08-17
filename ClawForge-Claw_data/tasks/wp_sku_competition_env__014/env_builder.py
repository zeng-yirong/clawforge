import json, os, shutil

def build_env():
    # clean slate
    shutil.rmtree("data", ignore_errors=True)
    shutil.rmtree("ops", ignore_errors=True)

    # --- brands ---
    brands = [
        {
            "brand_id": "BR001",
            "brand_name": "LuminaSkin",
            "hero_category_id": "CAT002",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Premium",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "BR002",
            "brand_name": "DermVeil",
            "hero_category_id": "CAT001",
            "hero_category_name": "Hydration Serum",
            "positioning": "Clinical",
            "region_focus": "EMEA",
            "price_tier": "mid-premium"
        },
        {
            "brand_id": "BR003",
            "brand_name": "AquaPulse",
            "hero_category_id": "CAT002",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Everyday",
            "region_focus": "APAC",
            "price_tier": "value"
        }
    ]
    os.makedirs("data/brands", exist_ok=True)
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # --- skus ---
    skus = [
        # LuminaSkin UV Moisturizer (target)
        {
            "sku_id": "SKU001",
            "brand_id": "BR001",
            "brand_name": "LuminaSkin",
            "category_id": "CAT002",
            "category_name": "UV Moisturizer",
            "sku_name": "Lumina UV Shield SPF50",
            "size_value": 50,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Broad spectrum protection", "Water resistant up to 80 min"],
            "ingredients": ["Zinc Oxide", "Titanium Dioxide", "Aloe Vera", "Vitamin E"]
        },
        {
            "sku_id": "SKU002",
            "brand_id": "BR001",
            "brand_name": "LuminaSkin",
            "category_id": "CAT002",
            "category_name": "UV Moisturizer",
            "sku_name": "Lumina Day Defense SPF30",
            "size_value": 75,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Lightweight daily moisturizer", "Non-greasy finish"],
            "ingredients": ["Avobenzone", "Octocrylene", "Glycerin", "Niacinamide"]
        },
        # LuminaSkin Hydration Serum –干扰（相同品牌不同类别）
        {
            "sku_id": "SKU003",
            "brand_id": "BR001",
            "brand_name": "LuminaSkin",
            "category_id": "CAT001",
            "category_name": "Hydration Serum",
            "sku_name": "Lumina Hydro Boost Serum",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Intense hydration", "Fast absorbing"],
            "ingredients": ["Hyaluronic Acid", "Ceramides", "Squalane"]
        },
        # DermVeil UV Moisturizer – 干扰（不同品牌相同类别）
        {
            "sku_id": "SKU004",
            "brand_id": "BR002",
            "brand_name": "DermVeil",
            "category_id": "CAT002",
            "category_name": "UV Moisturizer",
            "sku_name": "DermVeil Sun Protect SPF40",
            "size_value": 50,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Dermatologist tested", "Oil-free"],
            "ingredients": ["Homosalate", "Octisalate", "Zinc Oxide"]
        },
        # AquaPulse UV Moisturizer – 干扰（不同品牌相同类别）
        {
            "sku_id": "SKU005",
            "brand_id": "BR003",
            "brand_name": "AquaPulse",
            "category_id": "CAT002",
            "category_name": "UV Moisturizer",
            "sku_name": "AquaPulse Daily Shield SPF25",
            "size_value": 100,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Budget-friendly", "Lightweight"],
            "ingredients": ["Ensulizole", "Glycerin", "Tocopherol"]
        }
    ]
    os.makedirs("data/skus", exist_ok=True)
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # --- price books ---
    price_books = [
        {
            "price_book_id": "PB001",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "SKU001", "price": 24.99, "currency": "USD"},
                {"sku_id": "SKU002", "price": 19.99, "currency": "USD"},
                {"sku_id": "SKU003", "price": 29.99, "currency": "USD"},
                {"sku_id": "SKU004", "price": 22.49, "currency": "USD"},
                {"sku_id": "SKU005", "price": 12.99, "currency": "USD"}
            ]
        },
        {
            "price_book_id": "PB002",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "SKU001", "price": 29.99, "currency": "USD"},
                {"sku_id": "SKU002", "price": 24.99, "currency": "USD"},
                {"sku_id": "SKU003", "price": 34.99, "currency": "USD"},
                {"sku_id": "SKU004", "price": 26.49, "currency": "USD"},
                {"sku_id": "SKU005", "price": 14.99, "currency": "USD"}
            ]
        }
    ]
    os.makedirs("data/pricing", exist_ok=True)
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # --- attachments (optional, for realism) ---
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/category_review_template.md", "w") as f:
        f.write("# Category Review: {brand_name} - {category_name}\n\n")
        f.write("## SKU Overview\n| SKU ID | Name | Price | Selling Points |\n|--------|------|-------|----------------|\n")
        f.write("## Ingredients Analysis\n")

    # ensure output directory exists (agent will create if not, but we help)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
