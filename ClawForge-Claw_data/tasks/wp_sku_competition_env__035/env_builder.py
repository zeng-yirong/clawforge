import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. brands
    brands = [
        {"brand_id": "lum", "brand_name": "LuminaSkin", "hero_category_id": "cat_01", "hero_category_name": "Hydration Serum", "positioning": "高端保湿", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "aqp", "brand_name": "AquaPulse", "hero_category_id": "cat_02", "hero_category_name": "UV Moisturizer", "positioning": "中端防晒", "region_focus": "APAC", "price_tier": "mid-premium"},
        {"brand_id": "drm", "brand_name": "DermVeil", "hero_category_id": "cat_01", "hero_category_name": "Hydration Serum", "positioning": "药妆", "region_focus": "EMEA", "price_tier": "premium"},
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # 2. skus (多个品牌，LuminaSkin 有5个，包含一个discontinued)
    skus = [
        # LuminaSkin
        {"sku_id": "LS-HYDR-100", "brand_id": "lum", "brand_name": "LuminaSkin", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "Hydra Boost Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["深层补水", "清爽不黏腻"], "ingredients": ["透明质酸", "甘油"]},
        {"sku_id": "LS-HYDR-200", "brand_id": "lum", "brand_name": "LuminaSkin", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "Hydra Boost Serum 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["大容量", "持续保湿"], "ingredients": ["透明质酸", "维生素B5"]},
        {"sku_id": "LS-UV-100", "brand_id": "lum", "brand_name": "LuminaSkin", "category_id": "cat_02", "category_name": "UV Moisturizer", "sku_name": "UV Shield SPF50", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["高倍防晒", "清爽"], "ingredients": ["氧化锌", "二氧化钛"]},
        {"sku_id": "LS-UV-200", "brand_id": "lum", "brand_name": "LuminaSkin", "category_id": "cat_02", "category_name": "UV Moisturizer", "sku_name": "UV Shield SPF30", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["日常防晒", "温和"], "ingredients": ["氧化锌"]},
        {"sku_id": "LS-HYDR-OLD", "brand_id": "lum", "brand_name": "LuminaSkin", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "Old Formula Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["经典配方"], "ingredients": ["透明质酸"]},
        # AquaPulse (干扰)
        {"sku_id": "AQ-UV-100", "brand_id": "aqp", "brand_name": "AquaPulse", "category_id": "cat_02", "category_name": "UV Moisturizer", "sku_name": "Sun Guard SPF40", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["防水", "清爽"], "ingredients": ["氧化锌", "维生素E"]},
        {"sku_id": "AQ-UV-200", "brand_id": "aqp", "brand_name": "AquaPulse", "category_id": "cat_02", "category_name": "UV Moisturizer", "sku_name": "Sun Guard SPF25", "size_value": 75, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["大容量", "家庭装"], "ingredients": ["二氧化钛"]},
        # DermVeil (干扰)
        {"sku_id": "DR-HYDR-001", "brand_id": "drm", "brand_name": "DermVeil", "category_id": "cat_01", "category_name": "Hydration Serum", "sku_name": "Repair Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["修复屏障", "温和"], "ingredients": ["神经酰胺", "透明质酸"]},
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # 3. price_books (两个版本)
    price_books = [
        {
            "price_book_id": "pb_apac_q1_2026",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "LS-HYDR-100", "price": 42.00, "currency": "USD"},
                {"sku_id": "LS-HYDR-200", "price": 55.00, "currency": "USD"},
                {"sku_id": "LS-UV-100", "price": 33.00, "currency": "USD"},
                {"sku_id": "LS-UV-200", "price": 26.00, "currency": "USD"},
                {"sku_id": "LS-HYDR-OLD", "price": 38.00, "currency": "USD"},  # 停产旧价
                {"sku_id": "AQ-UV-100", "price": 22.00, "currency": "USD"},
                {"sku_id": "AQ-UV-200", "price": 18.00, "currency": "USD"},
                {"sku_id": "DR-HYDR-001", "price": 60.00, "currency": "USD"},
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
                {"sku_id": "LS-HYDR-100", "price": 45.00, "currency": "USD"},
                {"sku_id": "LS-HYDR-200", "price": 58.00, "currency": "USD"},
                {"sku_id": "LS-UV-100", "price": 35.00, "currency": "USD"},
                {"sku_id": "LS-UV-200", "price": 28.00, "currency": "USD"},
                # 注意：旧SKU不在其中
                {"sku_id": "AQ-UV-100", "price": 24.00, "currency": "USD"},
                {"sku_id": "AQ-UV-200", "price": 20.00, "currency": "USD"},
                {"sku_id": "DR-HYDR-001", "price": 62.00, "currency": "USD"},
            ]
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # 4. attachments (可选，用作干扰)
    attachments = [
        {"path": "data/attachments/category_review_template.md", "title": "Category Review Template", "kind": "report_template", "description": "A template for category review reports."},
        {"path": "data/attachments/current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice", "description": "Notice about the current price book."}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 5. contacts (干扰)
    contacts = [
        {"contact_id": "c1", "name": "Alina Bose", "role": "Category Director", "email": "alina.bose@northstar.example.com"},
        {"contact_id": "c2", "name": "Jonas Li", "role": "Merchandising Ops", "email": "jonas.li@northstar.example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 6. accounts (干扰)
    accounts = [
        {"account_id": "acc_01", "display_name": "Alice", "department": "Pricing", "email": "alice@example.com", "permissions": ["read"], "default_region": "APAC", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 创建两个空附件文件
    for att in attachments:
        with open(att["path"], "w") as f:
            f.write(f"# {att['title']}\n\nPlaceholder.\n")

if __name__ == "__main__":
    build_env()
