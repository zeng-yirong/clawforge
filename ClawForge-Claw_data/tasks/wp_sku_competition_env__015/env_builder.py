import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 输出目录，留空

    # 1. brands
    brands = [
        {"brand_id": "LUM001", "brand_name": "LuminaSkin", "hero_category_id": "CAT01",
         "hero_category_name": "Hydration Serum", "positioning": "Premium",
         "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "AQU001", "brand_name": "AquaPulse", "hero_category_id": "CAT02",
         "hero_category_name": "UV Moisturizer", "positioning": "Mass",
         "region_focus": "APAC", "price_tier": "mid"},
        {"brand_id": "DER001", "brand_name": "DermVeil", "hero_category_id": "CAT03",
         "hero_category_name": "Hydration Serum", "positioning": "Dermocosmetic",
         "region_focus": "EMEA", "price_tier": "premium"}
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # 2. skus
    skus = [
        {"sku_id": "LUM-SK-001", "brand_id": "LUM001", "brand_name": "LuminaSkin",
         "category_id": "CAT01", "category_name": "Hydration Serum",
         "sku_name": "HydraGlow Serum 30ml", "size_value": 30, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["24h hydration", "hyaluronic acid"],
         "ingredients": ["water", "glycerin", "hyaluronic acid"]},
        {"sku_id": "LUM-SK-002", "brand_id": "LUM001", "brand_name": "LuminaSkin",
         "category_id": "CAT01", "category_name": "Hydration Serum",
         "sku_name": "HydraGlow Serum 50ml", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["intensive moisture"],
         "ingredients": ["water", "squalane", "vitamin E"]},
        {"sku_id": "LUM-SK-003", "brand_id": "LUM001", "brand_name": "LuminaSkin",
         "category_id": "CAT02", "category_name": "UV Moisturizer",
         "sku_name": "UV Shield SPF50 40ml", "size_value": 40, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["broad spectrum", "lightweight"],
         "ingredients": ["zinc oxide", "titanium dioxide"]},
        {"sku_id": "LUM-SK-004", "brand_id": "LUM001", "brand_name": "LuminaSkin",
         "category_id": "CAT02", "category_name": "UV Moisturizer",
         "sku_name": "UV Shield SPF50 75ml", "size_value": 75, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["family size", "water resistant"],
         "ingredients": ["zinc oxide", "aloe vera"]},
        # 干扰 SKU 不属于 LuminaSkin
        {"sku_id": "AQU-SK-001", "brand_id": "AQU001", "brand_name": "AquaPulse",
         "category_id": "CAT02", "category_name": "UV Moisturizer",
         "sku_name": "AquaGlow SPF30 60ml", "size_value": 60, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["oil-free"],
         "ingredients": ["water", "octinoxate"]},
        {"sku_id": "AQU-SK-002", "brand_id": "AQU001", "brand_name": "AquaPulse",
         "category_id": "CAT02", "category_name": "UV Moisturizer",
         "sku_name": "AquaGlow SPF50 60ml", "size_value": 60, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["high protection"],
         "ingredients": ["water", "octocrylene"]},
        {"sku_id": "DER-SK-001", "brand_id": "DER001", "brand_name": "DermVeil",
         "category_id": "CAT01", "category_name": "Hydration Serum",
         "sku_name": "Derma Boost 30ml", "size_value": 30, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["collagen boost"],
         "ingredients": ["water", "collagen", "niacinamide"]},
        {"sku_id": "DER-SK-002", "brand_id": "DER001", "brand_name": "DermVeil",
         "category_id": "CAT01", "category_name": "Hydration Serum",
         "sku_name": "Derma Boost 60ml", "size_value": 60, "size_unit": "ml",
         "pack_count": 1, "status": "discontinued",
         "selling_points": ["intensive repair"],
         "ingredients": ["water", "peptides"]}
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # 3. price books
    price_books = [
        {
            "price_book_id": "PB01",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "LUM-SK-001", "price": 20.00},
                {"sku_id": "LUM-SK-002", "price": 28.00},
                {"sku_id": "LUM-SK-003", "price": 38.00},
                {"sku_id": "LUM-SK-004", "price": 14.50},
                {"sku_id": "AQU-SK-001", "price": 12.00}
            ]
        },
        {
            "price_book_id": "PB02",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                # LuminaSkin 三个出现在通知中
                {"sku_id": "LUM-SK-001", "price": 22.00},   # 错误: 通知 24.50
                {"sku_id": "LUM-SK-002", "price": 30.00},   # 未出现在通知中
                {"sku_id": "LUM-SK-003", "price": 42.00},   # 错误: 通知 39.00
                {"sku_id": "LUM-SK-004", "price": 15.75},   # 正确: 通知 15.75
                # 其他品牌干扰
                {"sku_id": "AQU-SK-001", "price": 13.50},
                {"sku_id": "AQU-SK-002", "price": 16.00},
                {"sku_id": "DER-SK-001", "price": 45.00},
                {"sku_id": "DER-SK-002", "price": 55.00}
            ]
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # 4. attachments 描述
    attachments_info = [
        {
            "path": "data/attachments/current_pricebook_notice.md",
            "title": "Current Price Book Notice",
            "kind": "pricing_notice",
            "description": "LuminaSkin corrected prices for APAC Q2 2026"
        },
        {
            "path": "data/attachments/category_review_template.md",
            "title": "Category Review Template",
            "kind": "report_template",
            "description": "Template for category performance review"
        }
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments_info}, f, indent=2)

    # 5. 创建实际附件文件
    notice_content = """# LuminaSkin – Correct Prices for APAC Q2 2026

| SKU ID | Correct Price (USD) |
|--------|---------------------|
| LUM-SK-001 | 24.50 |
| LUM-SK-003 | 39.00 |
| LUM-SK-004 | 15.75 |
"""
    with open("data/attachments/current_pricebook_notice.md", "w") as f:
        f.write(notice_content)

    # 创建一个干扰附件（无需内容）
    with open("data/attachments/category_review_template.md", "w") as f:
        f.write("# Category Review Template\n\n_This is a template._")

if __name__ == "__main__":
    build_env()
