import os
import json

def build_env():
    # 确保所有目录存在
    dirs = [
        "data",
        "data/brands",
        "data/skus",
        "data/pricing",
        "data/accounts",
        "data/contacts",
        "reports"  # 空目录
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1) brands.json —— 五个品牌，两个品类
    brands = [
        {"brand_id": "b_lumina",   "brand_name": "LuminaSkin",  "hero_category_id": "cat_hydration", "hero_category_name": "Hydration Serum", "positioning": "Premium", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "b_aqua",     "brand_name": "AquaPulse",   "hero_category_id": "cat_hydration", "hero_category_name": "Hydration Serum", "positioning": "Mid",     "region_focus": "APAC", "price_tier": "mid-premium"},
        {"brand_id": "b_derm",     "brand_name": "DermVeil",    "hero_category_id": "cat_uv",        "hero_category_name": "UV Moisturizer",  "positioning": "Clinical","region_focus": "EMEA", "price_tier": "premium"},
        {"brand_id": "b_pure",     "brand_name": "PureLattice", "hero_category_id": "cat_uv",        "hero_category_name": "UV Moisturizer",  "positioning": "Value",   "region_focus": "APAC", "price_tier": "value"},
        {"brand_id": "b_solar",    "brand_name": "SolarOat",    "hero_category_id": "cat_hydration", "hero_category_name": "Hydration Serum", "positioning": "Eco",     "region_focus": "EU",   "price_tier": "mid"}
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # 2) skus.json —— 每个品牌若干 SKU，部分为其他品类或已下架
    skus = [
        # LuminaSkin (Hydration Serum) —— 3 个活跃
        {"sku_id": "LS-H01", "brand_id": "b_lumina", "brand_name": "LuminaSkin", "category_id": "cat_hydration", "category_name": "Hydration Serum", "sku_name": "Deep Hydra Shot",    "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["24h moisture", "collagen boost"], "ingredients": ["hyaluronic acid", "vitamin B5"]},
        {"sku_id": "LS-H02", "brand_id": "b_lumina", "brand_name": "LuminaSkin", "category_id": "cat_hydration", "category_name": "Hydration Serum", "sku_name": "Radiance Boost",     "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["glow finish", "anti-pollution"], "ingredients": ["niacinamide", "vitamin C"]},
        {"sku_id": "LS-H03", "brand_id": "b_lumina", "brand_name": "LuminaSkin", "category_id": "cat_hydration", "category_name": "Hydration Serum", "sku_name": "Ceramide Repair",   "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["barrier repair", "soothing"], "ingredients": ["ceramide NP", "panthenol"]},
        # AquaPulse (Hydration Serum) —— 2 个活跃
        {"sku_id": "AP-H01", "brand_id": "b_aqua",   "brand_name": "AquaPulse",  "category_id": "cat_hydration", "category_name": "Hydration Serum", "sku_name": "Marine Splash",    "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["ocean minerals", "lightweight"], "ingredients": ["sea kelp", "glycerin"]},
        {"sku_id": "AP-H02", "brand_id": "b_aqua",   "brand_name": "AquaPulse",  "category_id": "cat_hydration", "category_name": "Hydration Serum", "sku_name": "Coral Relief",     "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["calming", "reef-safe"], "ingredients": ["aloe vera", "centella"]},
        # SolarOat (Hydration Serum) —— 1 个，但已下架（干扰）
        {"sku_id": "SO-H01", "brand_id": "b_solar",  "brand_name": "SolarOat",   "category_id": "cat_hydration", "category_name": "Hydration Serum", "sku_name": "Oat Hydrator",     "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["oat milk", "gentle"], "ingredients": ["oat extract", "squalane"]},
        # DermVeil (UV Moisturizer) —— 干扰
        {"sku_id": "DV-U01", "brand_id": "b_derm",   "brand_name": "DermVeil",   "category_id": "cat_uv",        "category_name": "UV Moisturizer",  "sku_name": "Sheer Shield",    "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF 50", "matte"], "ingredients": ["zinc oxide", "titanium dioxide"]},
        # PureLattice (UV Moisturizer) —— 干扰
        {"sku_id": "PL-U01", "brand_id": "b_pure",   "brand_name": "PureLattice","category_id": "cat_uv",        "category_name": "UV Moisturizer",  "sku_name": "Mineral Block",   "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["non-nano", "reef safe"], "ingredients": ["zinc oxide", "iron oxides"]},
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # 3) price_books.json —— 两个版本：ARCHIVE (已归档) 和 LIVE (当前)
    price_books = [
        {
            "price_book_id": "pb_archive",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                # 包含所有 SKU 的旧价（包括已下架的 SolarOat）
                {"sku_id": "LS-H01", "price": 27.99, "currency": "USD"},
                {"sku_id": "LS-H02", "price": 32.99, "currency": "USD"},
                {"sku_id": "LS-H03", "price": 37.99, "currency": "USD"},
                {"sku_id": "AP-H01", "price": 25.99, "currency": "USD"},
                {"sku_id": "AP-H02", "price": 30.99, "currency": "USD"},
                {"sku_id": "SO-H01", "price": 22.99, "currency": "USD"},
                {"sku_id": "DV-U01", "price": 45.99, "currency": "USD"},
                {"sku_id": "PL-U01", "price": 18.99, "currency": "USD"},
            ]
        },
        {
            "price_book_id": "pb_live",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                # 仅包括活跃的 Hydration Serum SKU (排除下架 & 其他品类)
                {"sku_id": "LS-H01", "price": 29.99, "currency": "USD"},
                {"sku_id": "LS-H02", "price": 34.99, "currency": "USD"},
                {"sku_id": "LS-H03", "price": 39.99, "currency": "USD"},
                {"sku_id": "AP-H01", "price": 27.99, "currency": "USD"},
                {"sku_id": "AP-H02", "price": 32.99, "currency": "USD"},
                # 故意不包含 SO-H01 (已下架) 和 UV 品类
            ]
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # 4) 干扰文件 —— accounts, contacts, attachments (内容简化，仅供存在)
    accounts = [
        {"account_id": "acc_01", "display_name": "Jonas Li", "department": "Merchandising Ops", "email": "jonas.li@northstar.example.com", "permissions": ["read"], "default_region": "APAC", "voice": []}
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c_alina", "name": "Alina Bose", "role": "Category Director", "email": "alina.bose@northstar.example.com"},
        {"contact_id": "c_jonas", "name": "Jonas Li", "role": "Merchandising Ops", "email": "jonas.li@northstar.example.com"},
        {"contact_id": "c_mira", "name": "Mira Tan", "role": "Pricing Operations Lead", "email": "mira.tan@northstar.example.com"}
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    attachments = [
        {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template", "description": "Standard template for category analysis."},
        {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice", "description": "Notice about live pricing update."}
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

if __name__ == "__main__":
    build_env()
