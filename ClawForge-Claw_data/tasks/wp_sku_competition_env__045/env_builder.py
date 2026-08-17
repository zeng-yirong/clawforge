import os
import json

def build_env():
    # ---------- data/brands ----------
    brands_dir = "data/brands"
    os.makedirs(brands_dir, exist_ok=True)
    brands = [
        {
            "brand_id": "lum-001",
            "brand_name": "LuminaSkin",
            "hero_category_id": "cat-hyd-001",
            "hero_category_name": "Hydration Serum",
            "positioning": "Premium dermo-cosmetics",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "aqu-001",
            "brand_name": "AquaPulse",
            "hero_category_id": "cat-hyd-001",
            "hero_category_name": "Hydration Serum",
            "positioning": "Mass-market hydration",
            "region_focus": "APAC",
            "price_tier": "mid"
        },
        {
            "brand_id": "xxx-001",
            "brand_name": "DermVeil",
            "hero_category_id": "cat-uv-001",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Luxury sun care",
            "region_focus": "EMEA",
            "price_tier": "premium"
        }
    ]
    with open(os.path.join(brands_dir, "brands.json"), "w") as f:
        json.dump({"brands": {b["brand_id"]: b for b in brands}}, f, indent=2)

    # ---------- data/skus ----------
    skus_dir = "data/skus"
    os.makedirs(skus_dir, exist_ok=True)
    skus = [
        # LuminaSkin – active Hydration Serum
        {
            "sku_id": "lum-hs-001",
            "brand_id": "lum-001",
            "brand_name": "LuminaSkin",
            "category_id": "cat-hyd-001",
            "category_name": "Hydration Serum",
            "sku_name": "Lumina Hydra Boost Serum",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Deep hydration", "Brightening"],
            "ingredients": ["Hyaluronic Acid", "Vitamin C"]
        },
        {
            "sku_id": "lum-hs-002",
            "brand_id": "lum-001",
            "brand_name": "LuminaSkin",
            "category_id": "cat-hyd-001",
            "category_name": "Hydration Serum",
            "sku_name": "Lumina Glow Serum",
            "size_value": 50,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Glow", "Anti-aging"],
            "ingredients": ["Niacinamide", "Retinol"]
        },
        # LuminaSkin – UV Moisturizer (wrong category, should be excluded)
        {
            "sku_id": "lum-uv-001",
            "brand_id": "lum-001",
            "brand_name": "LuminaSkin",
            "category_id": "cat-uv-001",
            "category_name": "UV Moisturizer",
            "sku_name": "Lumina UV Shield",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["SPF 50", "Matt finish"],
            "ingredients": ["Zinc Oxide", "Niacinamide"]
        },
        # AquaPulse – active Hydration Serum
        {
            "sku_id": "aqu-hs-001",
            "brand_id": "aqu-001",
            "brand_name": "AquaPulse",
            "category_id": "cat-hyd-001",
            "category_name": "Hydration Serum",
            "sku_name": "AquaPulse Hydra Burst",
            "size_value": 40,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Instant hydration", "Lightweight"],
            "ingredients": ["Aloe Vera", "Glycerin"]
        },
        {
            "sku_id": "aqu-hs-002",
            "brand_id": "aqu-001",
            "brand_name": "AquaPulse",
            "category_id": "cat-hyd-001",
            "category_name": "Hydration Serum",
            "sku_name": "AquaPulse Moisture Lock",
            "size_value": 60,
            "size_unit": "ml",
            "pack_count": 2,
            "status": "active",
            "selling_points": ["Lock in moisture", "Suitable for sensitive skin"],
            "ingredients": ["Ceramides", "Shea Butter"]
        },
        # AquaPulse – inactive SKU (status = inactive, should be excluded)
        {
            "sku_id": "aqu-hs-003",
            "brand_id": "aqu-001",
            "brand_name": "AquaPulse",
            "category_id": "cat-hyd-001",
            "category_name": "Hydration Serum",
            "sku_name": "AquaPulse Night Repair",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "inactive",
            "selling_points": ["Night repair", "Deep moisture"],
            "ingredients": ["Retinol", "Hyaluronic Acid"]
        }
    ]
    with open(os.path.join(skus_dir, "skus.json"), "w") as f:
        json.dump({"skus": {s["sku_id"]: s for s in skus}}, f, indent=2)

    # ---------- data/pricing ----------
    pricing_dir = "data/pricing"
    os.makedirs(pricing_dir, exist_ok=True)
    price_books = [
        {
            "price_book_id": "pb-apac-q1-2026",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "lum-hs-001", "price": 22.50},
                {"sku_id": "lum-hs-002", "price": 27.00},
                {"sku_id": "aqu-hs-001", "price": 18.50}
            ]
        },
        {
            "price_book_id": "pb-apac-q2-2026",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "lum-hs-001", "price": 24.80},
                {"sku_id": "lum-hs-002", "price": 29.50},
                {"sku_id": "lum-uv-001", "price": 19.00},
                {"sku_id": "aqu-hs-001", "price": 19.90},
                {"sku_id": "aqu-hs-002", "price": 22.00}
            ]
        }
    ]
    with open(os.path.join(pricing_dir, "price_books.json"), "w") as f:
        json.dump({"price_books": {pb["price_book_id"]: pb for pb in price_books}}, f, indent=2)

    # ---------- data/contacts (distractor) ----------
    contacts_dir = "data"
    contacts = [
        {"contact_id": "c001", "name": "Alina Bose", "role": "Category Director", "email": "alina.bose@northstar.example.com"},
        {"contact_id": "c002", "name": "Jonas Li", "role": "Merchandising Ops", "email": "jonas.li@northstar.example.com"},
        {"contact_id": "c003", "name": "Mira Tan", "role": "Pricing Operations Lead", "email": "mira.tan@northstar.example.com"}
    ]
    with open(os.path.join(contacts_dir, "contacts.json"), "w") as f:
        json.dump({"contacts": {c["contact_id"]: c for c in contacts}}, f, indent=2)

    # ---------- data/accounts (distractor) ----------
    accounts = [
        {"account_id": "a001", "display_name": "APAC Ops", "department": "Operations", "email": "apac.ops@northstar.example.com",
         "permissions": ["read_brand", "read_sku", "read_price"], "default_region": "APAC", "voice": ["en", "zh"]}
    ]
    with open(os.path.join(contacts_dir, "accounts.json"), "w") as f:
        json.dump({"accounts": {a["account_id"]: a for a in accounts}}, f, indent=2)

    # ---------- data/attachments (distractor) ----------
    attachments = [
        {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template",
         "description": "Standard template for category review"},
        {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice",
         "description": "Notice about the current price book version"}
    ]
    with open(os.path.join(contacts_dir, "attachments.json"), "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---------- ops/ directory (do not pre-create, let agent create) ----------
    # intentionally absent

if __name__ == "__main__":
    build_env()
