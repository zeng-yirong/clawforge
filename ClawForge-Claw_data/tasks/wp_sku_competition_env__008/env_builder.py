import os
import json

def build_env():
    # ---- brands ----
    brands = [
        {
            "brand_id": "dermveil",
            "brand_name": "DermVeil",
            "hero_category_id": "cat_uv_moisturizer",
            "hero_category_name": "UV Moisturizer",
            "positioning": "dermatologist-recommended",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "luminaskin",
            "brand_name": "LuminaSkin",
            "hero_category_id": "cat_hydration_serum",
            "hero_category_name": "Hydration Serum",
            "positioning": "luxury botanical",
            "region_focus": "APAC",
            "price_tier": "mid-premium"
        },
        {
            "brand_id": "aquapulse",
            "brand_name": "AquaPulse",
            "hero_category_id": "cat_uv_moisturizer",
            "hero_category_name": "UV Moisturizer",
            "positioning": "affordable hydration",
            "region_focus": "APAC",
            "price_tier": "value"
        }
    ]
    os.makedirs("data/brands", exist_ok=True)
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # ---- skus ----
    skus = [
        # DermVeil UV Moisturizer
        {
            "sku_id": "DVM-101",
            "brand_id": "dermveil",
            "brand_name": "DermVeil",
            "category_id": "cat_uv_moisturizer",
            "category_name": "UV Moisturizer",
            "sku_name": "DermVeil UV Shield SPF50",
            "size_value": 50,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["broad spectrum", "water resistant"],
            "ingredients": ["zinc oxide", "titanium dioxide"]
        },
        {
            "sku_id": "DVM-102",
            "brand_id": "dermveil",
            "brand_name": "DermVeil",
            "category_id": "cat_uv_moisturizer",
            "category_name": "UV Moisturizer",
            "sku_name": "DermVeil Daily UV Lotion",
            "size_value": 75,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["lightweight", "non-greasy"],
            "ingredients": ["avobenzone", "octocrylene"]
        },
        # DermVeil Hydration Serum (interference)
        {
            "sku_id": "DVM-201",
            "brand_id": "dermveil",
            "brand_name": "DermVeil",
            "category_id": "cat_hydration_serum",
            "category_name": "Hydration Serum",
            "sku_name": "DermVeil Hydra Boost",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["deep hydration", "hyaluronic acid"],
            "ingredients": ["sodium hyaluronate", "glycerin"]
        },
        # LuminaSkin UV Moisturizer (interference – different brand)
        {
            "sku_id": "LSK-001",
            "brand_id": "luminaskin",
            "brand_name": "LuminaSkin",
            "category_id": "cat_uv_moisturizer",
            "category_name": "UV Moisturizer",
            "sku_name": "LuminaSkin Brightening SPF30",
            "size_value": 50,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["brightening", "vitamin C"],
            "ingredients": ["ascorbic acid", "ferulic acid"]
        },
        # AquaPulse UV Moisturizer (interference – different brand)
        {
            "sku_id": "AQP-001",
            "brand_id": "aquapulse",
            "brand_name": "AquaPulse",
            "category_id": "cat_uv_moisturizer",
            "category_name": "UV Moisturizer",
            "sku_name": "AquaPulse Daily Defense SPF20",
            "size_value": 100,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["affordable", "lightweight"],
            "ingredients": ["octinoxate", "oxybenzone"]
        }
    ]
    os.makedirs("data/skus", exist_ok=True)
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ---- price books ----
    price_books = [
        {
            "price_book_id": "pb_apac_q1_2026",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "DVM-101", "price": 30.00},
                {"sku_id": "DVM-102", "price": 27.00},
                {"sku_id": "DVM-201", "price": 42.00},
                {"sku_id": "LSK-001", "price": 33.00},
                {"sku_id": "AQP-001", "price": 14.50}
            ]
        },
        {
            "price_book_id": "pb_apac_q2_2026",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "DVM-101", "price": 32.50},
                {"sku_id": "DVM-102", "price": 28.80},
                {"sku_id": "DVM-201", "price": 45.00},
                {"sku_id": "LSK-001", "price": 35.00},
                {"sku_id": "AQP-001", "price": 15.00}
            ]
        }
    ]
    os.makedirs("data/pricing", exist_ok=True)
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # ---- additional stray files to simulate real workspace ----
    os.makedirs("data/drafts", exist_ok=True)
    with open("data/drafts/old_notes.md", "w") as f:
        f.write("# DermVeil Q1 review notes\nOutdated content.\n")

    # contacts and accounts (not used but present)
    contacts = [
        {"contact_id": "c001", "name": "Jonas Li", "role": "Merchandising Ops", "email": "jonas.li@northstar.example.com"},
        {"contact_id": "c002", "name": "Alina Bose", "role": "Category Director", "email": "alina.bose@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    accounts = [
        {"account_id": "a001", "display_name": "Northstar APAC", "department": "Merchandising", "email": "apac@northstar.example.com",
         "permissions": ["read", "write"], "default_region": "APAC", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
