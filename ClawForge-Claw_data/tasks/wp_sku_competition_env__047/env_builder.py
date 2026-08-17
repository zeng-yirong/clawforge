import os
import json
import datetime

def build_env():
    # 创建目录结构
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，供 agent 写产物

    # ---------- brands ----------
    brands = [
        {
            "brand_id": "lum1",
            "brand_name": "LuminaSkin",
            "hero_category_id": "cat_serum",
            "hero_category_name": "Hydration Serum",
            "positioning": "Premium clinical skincare",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "derm1",
            "brand_name": "DermVeil",
            "hero_category_id": "cat_serum",
            "hero_category_name": "Hydration Serum",
            "positioning": "Dermatologist-recommended",
            "region_focus": "APAC",
            "price_tier": "mid-premium"
        },
        {
            "brand_id": "aqua1",
            "brand_name": "AquaPulse",
            "hero_category_id": "cat_serum",
            "hero_category_name": "Hydration Serum",
            "positioning": "Affordable everyday hydration",
            "region_focus": "APAC",
            "price_tier": "mid"
        },
        {
            "brand_id": "pure1",
            "brand_name": "PureLattice",
            "hero_category_id": "cat_moist",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Eco-friendly sunscreen",
            "region_focus": "APAC",
            "price_tier": "mid"
        },
        {
            "brand_id": "solar1",
            "brand_name": "SolarOat",
            "hero_category_id": "cat_moist",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Natural oat-based protection",
            "region_focus": "APAC",
            "price_tier": "value"
        }
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # ---------- skus ----------
    skus = [
        {
            "sku_id": "sku_lum_001",
            "brand_id": "lum1",
            "brand_name": "LuminaSkin",
            "category_id": "cat_serum",
            "category_name": "Hydration Serum",
            "sku_name": "Hydra Boost Serum",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Immediate hydration", "Anti-aging peptides"],
            "ingredients": ["Hyaluronic Acid", "Vitamin B5", "Ceramides"]
        },
        {
            "sku_id": "sku_derm_002",
            "brand_id": "derm1",
            "brand_name": "DermVeil",
            "category_id": "cat_serum",
            "category_name": "Hydration Serum",
            "sku_name": "Moisture Lock Serum",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Deep moisture barrier", "Fragrance-free"],
            "ingredients": ["Glycerin", "Squalane", "Niacinamide"]
        },
        {
            "sku_id": "sku_aqua_003",
            "brand_id": "aqua1",
            "brand_name": "AquaPulse",
            "category_id": "cat_serum",
            "category_name": "Hydration Serum",
            "sku_name": "Aqua Hydration Serum",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Lightweight gel", "Quick absorption"],
            "ingredients": ["Aloe Vera", "Green Tea Extract", "Panthenol"]
        },
        # 干扰 SKU：其他品牌同类产品？为了让唯一，我们不让其他品牌有活跃的 Hydration Serum
        {
            "sku_id": "sku_pure_004",
            "brand_id": "pure1",
            "brand_name": "PureLattice",
            "category_id": "cat_moist",
            "category_name": "UV Moisturizer",
            "sku_name": "UV Shield Moisturizer",
            "size_value": 50,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["SPF 50", "Broad spectrum"],
            "ingredients": ["Zinc Oxide", "Titanium Dioxide"]
        },
        {
            "sku_id": "sku_solar_005",
            "brand_id": "solar1",
            "brand_name": "SolarOat",
            "category_id": "cat_moist",
            "category_name": "UV Moisturizer",
            "sku_name": "Oat Sun Lotion",
            "size_value": 100,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Oat extract", "Gentle on skin"],
            "ingredients": ["Colloidal Oatmeal", "Shea Butter"]
        },
        # 干扰：LuminaSkin 另一个 Hydration Serum（已下架）
        {
            "sku_id": "sku_lum_006",
            "brand_id": "lum1",
            "brand_name": "LuminaSkin",
            "category_id": "cat_serum",
            "category_name": "Hydration Serum",
            "sku_name": "Hydra Boost Serum (Old Formula)",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "discontinued",
            "selling_points": ["Classic hydration"],
            "ingredients": ["Hyaluronic Acid", "Vitamin E"]
        }
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ---------- price books ----------
    # 存档版（过期）
    archive_entries = [
        {"sku_id": "sku_lum_001", "price": 33.00, "currency": "USD"},
        {"sku_id": "sku_derm_002", "price": 32.00, "currency": "USD"},
        {"sku_id": "sku_aqua_003", "price": 30.00, "currency": "USD"},
        {"sku_id": "sku_pure_004", "price": 22.00, "currency": "USD"},
        {"sku_id": "sku_solar_005", "price": 18.00, "currency": "USD"}
    ]
    # 当前版（生效）
    current_entries = [
        {"sku_id": "sku_lum_001", "price": 48.50, "currency": "USD"},
        {"sku_id": "sku_derm_002", "price": 42.00, "currency": "USD"},
        {"sku_id": "sku_aqua_003", "price": 39.90, "currency": "USD"},
        {"sku_id": "sku_pure_004", "price": 25.50, "currency": "USD"},
        {"sku_id": "sku_solar_005", "price": 20.00, "currency": "USD"}
    ]
    price_books = [
        {
            "price_book_id": "pb_arch_2026q1",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": archive_entries
        },
        {
            "price_book_id": "pb_live_2026q2",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": current_entries
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # ---------- 干扰文件 ----------
    accounts = [
        {"account_id": "acc001", "display_name": "Alice Wang", "department": "Marketing",
         "email": "alice.wang@northstar.example.com", "permissions": ["read", "write"],
         "default_region": "APAC", "voice": ["en", "zh"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    attachments = [
        {"path": "category_review_template.md", "title": "Category Review Template",
         "kind": "report_template",
         "description": "Template for competitive category review"},
        {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice",
         "kind": "pricing_notice",
         "description": "Notice about the current price book version"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    contacts = [
        {"contact_id": "c001", "name": "Alina Bose", "role": "Category Director",
         "email": "alina.bose@northstar.example.com"},
        {"contact_id": "c002", "name": "Jonas Li", "role": "Merchandising Ops",
         "email": "jonas.li@northstar.example.com"},
        {"contact_id": "c003", "name": "Mira Tan", "role": "Pricing Operations Lead",
         "email": "mira.tan@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
