import os
import json

def build_env():
    # Create data directories
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/brands", exist_ok=True)

    # Brands
    brands = [
        {"brand_id": "aqp_001", "brand_name": "AquaPulse", "hero_category_id": "cat_002", "hero_category_name": "UV Moisturizer", "positioning": "Hydration for all", "region_focus": "Global", "price_tier": "mid"},
        {"brand_id": "drm_001", "brand_name": "DermVeil", "hero_category_id": "cat_001", "hero_category_name": "Hydration Serum", "positioning": "Clinical skincare", "region_focus": "NA", "price_tier": "premium"},
        {"brand_id": "lum_001", "brand_name": "LuminaSkin", "hero_category_id": "cat_001", "hero_category_name": "Hydration Serum", "positioning": "Brightening & Hydration", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "prl_001", "brand_name": "PureLattice", "hero_category_id": "cat_002", "hero_category_name": "UV Moisturizer", "positioning": "Mineral based", "region_focus": "EU", "price_tier": "mid-premium"},
        {"brand_id": "sol_001", "brand_name": "SolarOat", "hero_category_id": "cat_001", "hero_category_name": "Hydration Serum", "positioning": "Natural Oats", "region_focus": "APAC", "price_tier": "value"},
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # SKUs
    skus = [
        {"sku_id": "lum_sku_01", "brand_id": "lum_001", "brand_name": "LuminaSkin", "category_id": "cat_001", "category_name": "Hydration Serum", "sku_name": "LuminaHydra Boost Serum 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Brightening", "Lightweight"], "ingredients": ["Niacinamide", "Hyaluronic Acid", "Vitamin C"]},
        {"sku_id": "lum_sku_02", "brand_id": "lum_001", "brand_name": "LuminaSkin", "category_id": "cat_001", "category_name": "Hydration Serum", "sku_name": "LuminaHydra Intense Serum 100ml", "size_value": 100, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Intense Hydration", "Anti-aging"], "ingredients": ["Retinol", "Peptides", "Squalane"]},
        {"sku_id": "lum_sku_03", "brand_id": "lum_001", "brand_name": "LuminaSkin", "category_id": "cat_001", "category_name": "Hydration Serum", "sku_name": "LuminaHydra Travel Duo 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 2, "status": "active", "selling_points": ["Travel-friendly", "Quick absorption"], "ingredients": ["Green Tea Extract", "Glycerin"]},
        {"sku_id": "drm_sku_01", "brand_id": "drm_001", "brand_name": "DermVeil", "category_id": "cat_001", "category_name": "Hydration Serum", "sku_name": "DermVeil Clarifying Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Clarifying", "Oil-control"], "ingredients": ["Salicylic acid", "Zinc"]},
        {"sku_id": "aqp_sku_01", "brand_id": "aqp_001", "brand_name": "AquaPulse", "category_id": "cat_002", "category_name": "UV Moisturizer", "sku_name": "AquaPulse Sun Gel SPF50", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF50", "Water-resistant"], "ingredients": ["Zinc Oxide", "Aloe Vera"]},
        {"sku_id": "prl_sku_01", "brand_id": "prl_001", "brand_name": "PureLattice", "category_id": "cat_002", "category_name": "UV Moisturizer", "sku_name": "PureLattice Mineral Shield", "size_value": 60, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Mineral", "Non-nano"], "ingredients": ["Titanium Dioxide", "Jojoba Oil"]},
        {"sku_id": "sol_sku_01", "brand_id": "sol_001", "brand_name": "SolarOat", "category_id": "cat_001", "category_name": "Hydration Serum", "sku_name": "SolarOat Soothing Oat Serum", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Soothing", "Oat-based"], "ingredients": ["Colloidal Oatmeal", "Calendula"]},
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # Price books
    price_books = [
        {
            "price_book_id": "pb_001",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "lum_sku_01", "price": 27.99},
                {"sku_id": "lum_sku_02", "price": 45.00},
                {"sku_id": "lum_sku_03", "price": 35.00},
                {"sku_id": "drm_sku_01", "price": 32.99},
                {"sku_id": "aqp_sku_01", "price": 18.50},
                {"sku_id": "prl_sku_01", "price": 22.00},
                {"sku_id": "sol_sku_01", "price": 14.99}
            ]
        },
        {
            "price_book_id": "pb_002",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "lum_sku_01", "price": 29.99},
                {"sku_id": "lum_sku_02", "price": 49.99},
                {"sku_id": "lum_sku_03", "price": 39.99},
                {"sku_id": "drm_sku_01", "price": 34.99},
                {"sku_id": "aqp_sku_01", "price": 19.50},
                {"sku_id": "prl_sku_01", "price": 23.50},
                {"sku_id": "sol_sku_01", "price": 15.99}
            ]
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # Attachments (flavor)
    os.makedirs("attachments", exist_ok=True)
    with open("attachments/current_pricebook_notice.md", "w") as f:
        f.write("# Current Price Book Notice\n\nPlease always use the price book with `is_current: true`.\nThat is APAC-Q2-2026-LIVE.\n")
    with open("attachments/category_review_template.md", "w") as f:
        f.write("# Category Review Template\n\nThis template is for internal use.\n")

    # Accounts and contacts (for depth)
    os.makedirs("data/accounts", exist_ok=True)
    accounts = [
        {"account_id": "alina_b", "display_name": "Alina Bose", "department": "Category Management", "email": "alina.bose@northstar.example.com", "permissions": ["read", "write"], "default_region": "APAC", "voice": ["en", "zh"]},
        {"account_id": "jonas_l", "display_name": "Jonas Li", "department": "Merchandising Ops", "email": "jonas.li@northstar.example.com", "permissions": ["read"], "default_region": "APAC", "voice": ["en"]}
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c_001", "name": "Alina Bose", "role": "Category Director", "email": "alina.bose@northstar.example.com"},
        {"contact_id": "c_002", "name": "Jonas Li", "role": "Merchandising Ops", "email": "jonas.li@northstar.example.com"},
        {"contact_id": "c_003", "name": "Mira Tan", "role": "Pricing Operations Lead", "email": "mira.tan@northstar.example.com"}
    ]
    os.makedirs("data/contacts", exist_ok=True)
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # Create empty reports directory
    os.makedirs("reports", exist_ok=True)

    # Distractor directory with wrong report (uses archived prices)
    os.makedirs("old_reports", exist_ok=True)
    wrong_report = {
        "brand_name": "LuminaSkin",
        "category_name": "Hydration Serum",
        "skus": [
            {"sku_id": "lum_sku_01", "sku_name": "LuminaHydra Boost Serum 50ml", "size": "50ml", "price": 27.99, "selling_points": ["Brightening", "Lightweight"], "ingredients": ["Niacinamide", "Hyaluronic Acid", "Vitamin C"]},
            {"sku_id": "lum_sku_02", "sku_name": "LuminaHydra Intense Serum 100ml", "size": "100ml", "price": 45.00, "selling_points": ["Intense Hydration", "Anti-aging"], "ingredients": ["Retinol", "Peptides", "Squalane"]},
            {"sku_id": "lum_sku_03", "sku_name": "LuminaHydra Travel Duo 30ml", "size": "30ml", "price": 35.00, "selling_points": ["Travel-friendly", "Quick absorption"], "ingredients": ["Green Tea Extract", "Glycerin"]}
        ],
        "summary": {"count": 3, "average_price": 35.99}
    }
    with open("old_reports/category_comparison_lumina_serum.json", "w") as f:
        json.dump(wrong_report, f, indent=2)

if __name__ == "__main__":
    build_env()
