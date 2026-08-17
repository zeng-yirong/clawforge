import json, os, random

def build_env():
    # --- brands ---
    brands = [
        {"brand_id": "lum001", "brand_name": "LuminaSkin", "hero_category_id": "cat01", "hero_category_name": "Hydration Serum", "positioning": "premium", "price_tier": "premium"},
        {"brand_id": "aqp002", "brand_name": "AquaPulse", "hero_category_id": "cat02", "hero_category_name": "UV Moisturizer", "positioning": "mass", "price_tier": "mid"},
        {"brand_id": "drm003", "brand_name": "DermVeil", "hero_category_id": "cat01", "hero_category_name": "Hydration Serum", "positioning": "clinical", "price_tier": "mid-premium"},
    ]
    os.makedirs("data/brands", exist_ok=True)
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": {b["brand_id"]: b for b in brands}}, f)

    # --- SKUs (LuminaSkin: 5 total, 3 active) ---
    skus = [
        {"sku_id": "lum-s01", "brand_id": "lum001", "brand_name": "LuminaSkin", "category_id": "cat01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Brightening", "Lightweight"], "ingredients": ["Niacinamide", "Hyaluronic Acid"]},
        {"sku_id": "lum-s02", "brand_id": "lum001", "brand_name": "LuminaSkin", "category_id": "cat01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Serum 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Brightening", "Deep hydration"], "ingredients": ["Niacinamide", "Hyaluronic Acid", "Ceramide"]},
        {"sku_id": "lum-s03", "brand_id": "lum001", "brand_name": "LuminaSkin", "category_id": "cat02", "category_name": "UV Moisturizer", "sku_name": "LuminaSkin UV Shield SPF50", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF50", "Non-greasy"], "ingredients": ["Zinc Oxide", "Vitamin E"]},
        {"sku_id": "lum-s04", "brand_id": "lum001", "brand_name": "LuminaSkin", "category_id": "cat01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Hydra Serum 30ml (discontinued)", "size_value": 30, "size_unit": "ml", "pack_count": 2, "status": "discontinued", "selling_points": ["Old formula"], "ingredients": ["Glycerin", "Water"]},
        {"sku_id": "lum-s05", "brand_id": "lum001", "brand_name": "LuminaSkin", "category_id": "cat02", "category_name": "UV Moisturizer", "sku_name": "LuminaSkin UV Shield SPF30 (old)", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["SPF30", "Light"], "ingredients": ["Titanium Dioxide"]},
    ]
    # 干扰品牌 SKU
    for b in ["aqp002", "drm003"]:
        for i in range(3):
            skus.append({
                "sku_id": f"{b}-s{i+1:02d}", "brand_id": b, "brand_name": brands[brands.index([x for x in brands if x["brand_id"]==b][0])]["brand_name"],
                "category_id": "cat01", "category_name": "Hydration Serum",
                "sku_name": f"{b} Product {i+1}", "size_value": 30, "size_unit": "ml", "pack_count": 1,
                "status": "active", "selling_points": ["Test"], "ingredients": ["Water"]
            })
    os.makedirs("data/skus", exist_ok=True)
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": {s["sku_id"]: s for s in skus}}, f)

    # --- Price Books ---
    entries_live = [
        {"sku_id": "lum-s01", "price": 24.99},
        {"sku_id": "lum-s02", "price": 39.99},
        {"sku_id": "lum-s03", "price": 19.99},
        # 故意加入一条 discontinued SKU 的价格 (不应使用)
        {"sku_id": "lum-s04", "price": 15.00},
    ]
    entries_archive = [
        {"sku_id": "lum-s01", "price": 22.50},
        {"sku_id": "lum-s02", "price": 35.00},
        {"sku_id": "lum-s03", "price": 18.50},
        {"sku_id": "lum-s05", "price": 14.00},
    ]
    price_books = [
        {"price_book_id": "pb-apac-q2-2026-live", "version": "APAC-Q2-2026-LIVE", "region": "APAC", "status": "approved", "is_current": True, "effective_from": "2026-04-01", "entries": entries_live},
        {"price_book_id": "pb-apac-q1-2026-archive", "version": "APAC-Q1-2026-ARCHIVE", "region": "APAC", "status": "archived", "is_current": False, "effective_from": "2026-01-01", "entries": entries_archive},
    ]
    os.makedirs("data/pricing", exist_ok=True)
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": {pb["price_book_id"]: pb for pb in price_books}}, f)

    # --- 额外干扰项：attachments 和 contacts（不影响任务但增加文件树）---
    os.makedirs("data", exist_ok=True)
    attachments = [
        {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template", "description": "Template for category analysis"},
        {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice", "description": "Notice about Q2 price book"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f)
    accounts = [
        {"account_id": "acct1", "display_name": "Mira Tan", "department": "Pricing", "email": "mira.tan@northstar.example.com", "permissions": ["pricing"], "default_region": "APAC", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": {a["account_id"]: a for a in accounts}}, f)
    contacts = [
        {"contact_id": "c01", "name": "Mira Tan", "role": "Pricing Operations Lead", "email": "mira.tan@northstar.example.com"},
        {"contact_id": "c02", "name": "Alina Bose", "role": "Category Director", "email": "alina.bose@northstar.example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": {c["contact_id"]: c for c in contacts}}, f)

if __name__ == "__main__":
    build_env()
