import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- brands ----------
    brands = [
        {"brand_id": "B001", "brand_name": "LuminaSkin", "hero_category_id": "C001",
         "hero_category_name": "Hydration Serum", "positioning": "Premium",
         "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "B002", "brand_name": "AquaPulse", "hero_category_id": "C001",
         "hero_category_name": "Hydration Serum", "positioning": "Mid",
         "region_focus": "APAC", "price_tier": "mid"},
        {"brand_id": "B003", "brand_name": "DermVeil", "hero_category_id": "C002",
         "hero_category_name": "UV Moisturizer", "positioning": "Premium",
         "region_focus": "EMEA", "price_tier": "premium"},
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # ---------- pricing (two price books) ----------
    price_books = [
        {
            "price_book_id": "PB-APAC-Q1-2026",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "LS-001", "price": 24.00, "currency": "USD"},
                {"sku_id": "LS-002", "price": 30.00, "currency": "USD"},
                {"sku_id": "LS-003", "price": 17.50, "currency": "USD"},
                {"sku_id": "AP-011", "price": 15.00, "currency": "USD"},
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
                {"sku_id": "LS-001", "price": 25.50, "currency": "USD"},
                {"sku_id": "LS-002", "price": 32.00, "currency": "USD"},
                {"sku_id": "LS-003", "price": 18.75, "currency": "USD"},
                {"sku_id": "AP-011", "price": 15.80, "currency": "USD"},
                {"sku_id": "DV-101", "price": 40.00, "currency": "USD"},
            ]
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # ---------- skus (with duplicates and discontinued) ----------
    skus = [
        # LuminaSkin active
        {"sku_id": "LS-001", "brand_id": "B001", "brand_name": "LuminaSkin",
         "category_id": "C001", "category_name": "Hydration Serum",
         "sku_name": "LuminaSkin Hydra Boost 50ml", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["24h hydration", "oil-free"],
         "ingredients": ["Hyaluronic Acid", "Niacinamide", "Vitamin E"]},
        {"sku_id": "LS-002", "brand_id": "B001", "brand_name": "LuminaSkin",
         "category_id": "C001", "category_name": "Hydration Serum",
         "sku_name": "LuminaSkin Radiance Serum 30ml", "size_value": 30, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["Brightening", "Vitamin C boost"],
         "ingredients": ["Ascorbic Acid", "Ferulic Acid", "Vitamin E"]},
        {"sku_id": "LS-003", "brand_id": "B001", "brand_name": "LuminaSkin",
         "category_id": "C001", "category_name": "Hydration Serum",
         "sku_name": "LuminaSkin Night Repair 50ml", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["Overnight repair", "Anti-aging"],
         "ingredients": ["Retinol", "Peptides", "Ceramides"]},
        # Discontinued duplicate (same sku_id, old status)
        {"sku_id": "LS-001", "brand_id": "B001", "brand_name": "LuminaSkin",
         "category_id": "C001", "category_name": "Hydration Serum",
         "sku_name": "LuminaSkin Hydra Boost 50ml (old batch)", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "discontinued",
         "selling_points": ["24h hydration"],
         "ingredients": ["Hyaluronic Acid", "Niacinamide"]},
        # Other brands (interference)
        {"sku_id": "AP-011", "brand_id": "B002", "brand_name": "AquaPulse",
         "category_id": "C001", "category_name": "Hydration Serum",
         "sku_name": "AquaPulse Pure Hydration 100ml", "size_value": 100, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["Deep cleansing", "pH balanced"],
         "ingredients": ["Aloe Vera", "Glycerin"]},
        {"sku_id": "DV-101", "brand_id": "B003", "brand_name": "DermVeil",
         "category_id": "C002", "category_name": "UV Moisturizer",
         "sku_name": "DermVeil UV Shield SPF50", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["SPF50", "Matte finish"],
         "ingredients": ["Zinc Oxide", "Titanium Dioxide"]},
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ---------- dummy accounts & contacts (not needed but no harm) ----------
    accounts = [
        {"account_id": "ACC-001", "display_name": "NorthStar Procurement", "department": "Procurement",
         "email": "procurement@northstar.example.com", "permissions": ["read", "write"],
         "default_region": "APAC", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "C001", "name": "Alina Bose", "role": "Category Director",
         "email": "alina.bose@northstar.example.com"},
        {"contact_id": "C002", "name": "Jonas Li", "role": "Merchandising Ops",
         "email": "jonas.li@northstar.example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- attachments (reference template) ----------
    attachments = [
        {"path": "category_review_template.md", "title": "Category Review Template",
         "kind": "report_template",
         "description": "Standard template for competitor comparison"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

if __name__ == "__main__":
    build_env()
