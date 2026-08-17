import os
import json
import shutil

def build_env():
    # 创建目录结构
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("ops", exist_ok=True)          # 干扰目录
    os.makedirs("db_dumps/enrichment", exist_ok=True)  # 干扰目录

    # =========== 品牌数据 ===========
    brands = {
        "brands": [
            {"brand_id": "brand_lumina", "brand_name": "LuminaSkin",
             "hero_category_id": "cat_hydration", "hero_category_name": "Hydration Serum",
             "positioning": "Premium dermocosmetics", "region_focus": "APAC",
             "price_tier": "premium"},
            {"brand_id": "brand_derm", "brand_name": "DermVeil",
             "hero_category_id": "cat_uv", "hero_category_name": "UV Moisturizer",
             "positioning": "Clinical skincare", "region_focus": "EMEA",
             "price_tier": "mid-premium"},
            {"brand_id": "brand_aqua", "brand_name": "AquaPulse",
             "hero_category_id": "cat_hydration", "hero_category_name": "Hydration Serum",
             "positioning": "Hydration specialist", "region_focus": "APAC",
             "price_tier": "value"}
        ]
    }
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # =========== SKU 数据（已包含最新卖点） ===========
    skus = {
        "skus": [
            {"sku_id": "sku_ls01", "brand_id": "brand_lumina", "brand_name": "LuminaSkin",
             "category_id": "cat_hydration", "category_name": "Hydration Serum",
             "sku_name": "LuminaSkin Hydro Boost", "size_value": 50, "size_unit": "ml",
             "pack_count": 1, "status": "active",
             "selling_points": ["Deep hydration", "Lightweight", "Dermatologist tested"],
             "ingredients": ["Hyaluronic Acid", "Glycerin"]},
            {"sku_id": "sku_ls02", "brand_id": "brand_lumina", "brand_name": "LuminaSkin",
             "category_id": "cat_hydration", "category_name": "Hydration Serum",
             "sku_name": "LuminaSkin Matte Balance", "size_value": 30, "size_unit": "ml",
             "pack_count": 1, "status": "active",
             "selling_points": ["Oil control", "Matt finish"],
             "ingredients": ["Salicylic Acid", "Niacinamide"]},
            {"sku_id": "sku_ls03", "brand_id": "brand_lumina", "brand_name": "LuminaSkin",
             "category_id": "cat_hydration", "category_name": "Hydration Serum",
             "sku_name": "LuminaSkin Brightening Essence", "size_value": 30, "size_unit": "ml",
             "pack_count": 1, "status": "active",
             "selling_points": ["Brightening", "Vitamin C"],
             "ingredients": ["Ascorbic Acid", "Ferulic Acid"]},
            # 干扰 SKU：不同品牌 / 不同品类
            {"sku_id": "sku_dv01", "brand_id": "brand_derm", "brand_name": "DermVeil",
             "category_id": "cat_uv", "category_name": "UV Moisturizer",
             "sku_name": "DermVeil Shield SPF50", "size_value": 50, "size_unit": "ml",
             "pack_count": 1, "status": "active",
             "selling_points": ["Broad spectrum", "Water resistant"],
             "ingredients": ["Zinc Oxide", "Titanium Dioxide"]},
            {"sku_id": "sku_aq01", "brand_id": "brand_aqua", "brand_name": "AquaPulse",
             "category_id": "cat_hydration", "category_name": "Hydration Serum",
             "sku_name": "AquaPulse Hydro Burst", "size_value": 75, "size_unit": "ml",
             "pack_count": 1, "status": "active",
             "selling_points": ["Quick absorption", "Alcohol-free"],
             "ingredients": ["Aloe Vera", "Panthenol"]}
        ]
    }
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # =========== 价格书 ===========
    # 旧价格书 (APAC-Q1-2026-ARCHIVE)
    old_entries = [
        {"sku_id": "sku_ls01", "price": 29.99, "currency": "USD"},
        {"sku_id": "sku_ls02", "price": 34.99, "currency": "USD"},
        {"sku_id": "sku_ls03", "price": 39.99, "currency": "USD"},
        {"sku_id": "sku_dv01", "price": 45.00, "currency": "USD"},
        {"sku_id": "sku_aq01", "price": 19.99, "currency": "USD"}
    ]
    old_price_book = {
        "price_books": [
            {"price_book_id": "pb_apac_q1_2026", "version": "APAC-Q1-2026-ARCHIVE",
             "region": "APAC", "status": "archived", "is_current": False,
             "effective_from": "2026-01-01", "entries": old_entries}
        ]
    }
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(old_price_book, f, indent=2)

    # 新价格书 (APAC-Q2-2026-LIVE) — 注意：只更新了 LuminaSkin 的 3 个 SKU
    new_entries = [
        {"sku_id": "sku_ls01", "price": 24.99, "currency": "USD"},   # 降价
        {"sku_id": "sku_ls02", "price": 34.99, "currency": "USD"},   # 不变
        {"sku_id": "sku_ls03", "price": 44.99, "currency": "USD"},   # 涨价
        {"sku_id": "sku_dv01", "price": 47.50, "currency": "USD"},
        {"sku_id": "sku_aq01", "price": 19.99, "currency": "USD"}
    ]
    new_price_book = {
        "price_books": [
            {"price_book_id": "pb_apac_q2_2026", "version": "APAC-Q2-2026-LIVE",
             "region": "APAC", "status": "approved", "is_current": True,
             "effective_from": "2026-04-01", "entries": new_entries}
        ]
    }
    # 为避免覆盖旧价格书，新价格书另存一个文件
    with open("data/pricing/price_books_live.json", "w") as f:
        json.dump(new_price_book, f, indent=2)

    # 干扰：再生成一个过期价格书（不同区域）
    junk_entries = [
        {"sku_id": "sku_ls01", "price": 27.99, "currency": "EUR"}
    ]
    junk_book = {
        "price_books": [
            {"price_book_id": "pb_emea_2025", "version": "EMEA-2025-FINAL",
             "region": "EMEA", "status": "archived", "is_current": False,
             "effective_from": "2025-06-01", "entries": junk_entries}
        ]
    }
    with open("data/pricing/price_books_emea_old.json", "w") as f:
        json.dump(junk_book, f, indent=2)

    # =========== 附件 ===========
    # 模板文件 category_review_template.md
    template_content = """# Category Review Template

Please output a JSON file with the following structure:

[
  {
    "sku_id": "string",
    "brand_name": "string",
    "category_name": "string",
    "old_price": number,
    "new_price": number,
    "price_change_percent": "string (e.g. '-16.7%')",
    "selling_points_updated": boolean
  }
]
Ensure that `price_change_percent` is a string with one decimal and a percent sign, calculated as ((new - old) / old) * 100.
"""
    with open("attachments/category_review_template.md", "w") as f:
        f.write(template_content)

    # 卖点变更记录 selling_point_changelog.md
    changelog_content = """# Selling Points Changelog (Q2 2026)

The following SKUs had their selling_points updated:

- sku_ls01: added "Dermatologist tested"
- sku_ls02: no change
- sku_ls03: no change
"""
    with open("attachments/selling_point_changelog.md", "w") as f:
        f.write(changelog_content)

    # 附件元数据（供环境参考，但 agent 不需要读）
    attachments_meta = {
        "attachments": [
            {"path": "attachments/category_review_template.md",
             "title": "Category Review Template", "kind": "report_template",
             "description": "Template for the category comparison report"},
            {"path": "attachments/selling_point_changelog.md",
             "title": "Selling Point Changelog", "kind": "pricing_notice",
             "description": "Record of which SKUs had selling points updated"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments_meta, f, indent=2)

    # =========== 干扰文件 ===========
    # 无用目录与文件
    with open("db_dumps/usage_2025.csv", "w") as f:
        f.write("date,sku_id,impressions\n2025-12-01,sku_ls01,1234\n")
    with open("db_dumps/enrichment/archived_brands.json", "w") as f:
        json.dump({"old_brands": ["SolarOat"]}, f)
    with open("ops/readme.txt", "w") as f:
        f.write("This folder is for operational outputs.\n")
    with open("reports/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
