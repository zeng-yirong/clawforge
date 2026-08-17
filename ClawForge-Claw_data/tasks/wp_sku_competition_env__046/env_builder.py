import json
import os
import shutil

def build_env():
    # 清理现有内容（如果存在）
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("ops"):
        shutil.rmtree("ops")

    # 创建必要目录
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)  # 附件目录，但不会用到
    os.makedirs("ops", exist_ok=True)

    # ========== 1. brands.json ==========
    brands = [
        {
            "brand_id": "br_lumina",
            "brand_name": "LuminaSkin",
            "hero_category_id": "cat_hydro",
            "hero_category_name": "Hydration Serum",
            "positioning": "premium dermocosmetics",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "br_aqua",
            "brand_name": "AquaPulse",
            "hero_category_id": "cat_uv",
            "hero_category_name": "UV Moisturizer",
            "positioning": "mass market",
            "region_focus": "EU",
            "price_tier": "value"
        },
        {
            "brand_id": "br_derm",
            "brand_name": "DermVeil",
            "hero_category_id": "cat_hydro",
            "hero_category_name": "Hydration Serum",
            "positioning": "clinical",
            "region_focus": "NA",
            "price_tier": "premium"
        },
        # 干扰：已废弃品牌
        {
            "brand_id": "br_obsolete",
            "brand_name": "PureLattice",
            "hero_category_id": "cat_uv",
            "hero_category_name": "UV Moisturizer",
            "positioning": "legacy",
            "region_focus": "APAC",
            "price_tier": "mid"
        }
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # ========== 2. skus.json ==========
    # 注意：只有 LuminaSkin 的 active SKU 应被提取
    skus = [
        # LuminaSkin active
        {"sku_id": "LS-1001", "brand_id": "br_lumina", "brand_name": "LuminaSkin",
         "category_id": "cat_hydro", "category_name": "Hydration Serum",
         "sku_name": "HydraGlow Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Boost hydration by 200%", "Lightweight gel texture", "Non-comedogenic"],
         "ingredients": ["Hyaluronic Acid", "Niacinamide", "Glycerin", "Ceramide NP"]},
        {"sku_id": "LS-1002", "brand_id": "br_lumina", "brand_name": "LuminaSkin",
         "category_id": "cat_uv", "category_name": "UV Moisturizer",
         "sku_name": "UV Shield SPF50+ 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Broad spectrum UVA/UVB", "Water resistant 80min", "Matte finish"],
         "ingredients": ["Zinc Oxide", "Titanium Dioxide", "Vitamin E", "Aloe Vera"]},
        # LuminaSkin discontinued (不应出现)
        {"sku_id": "LS-2001", "brand_id": "br_lumina", "brand_name": "LuminaSkin",
         "category_id": "cat_hydro", "category_name": "Hydration Serum",
         "sku_name": "Retinol Night Serum 30ml (Old)", "size_value": 30, "size_unit": "ml", "pack_count": 1,
         "status": "discontinued",
         "selling_points": ["Anti-aging", "Deep repair"],
         "ingredients": ["Retinol", "Vitamin C"]},
        # 其他品牌 active (干扰, 不应出现)
        {"sku_id": "AQ-5001", "brand_id": "br_aqua", "brand_name": "AquaPulse",
         "category_id": "cat_uv", "category_name": "UV Moisturizer",
         "sku_name": "Aqua Gel SPF30", "size_value": 75, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Oil-free", "Hydrating boost"],
         "ingredients": ["Water", "Glycerin", "Dimethicone"]},
        {"sku_id": "DV-7001", "brand_id": "br_derm", "brand_name": "DermVeil",
         "category_id": "cat_hydro", "category_name": "Hydration Serum",
         "sku_name": "DermVeil HA Concentrate", "size_value": 15, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Clinical grade", "Fast absorption"],
         "ingredients": ["Hyaluronic Acid", "Panthenol"]},
        # 已废弃品牌 (不应出现)
        {"sku_id": "PL-0001", "brand_id": "br_obsolete", "brand_name": "PureLattice",
         "category_id": "cat_uv", "category_name": "UV Moisturizer",
         "sku_name": "Lattice Shield", "size_value": 60, "size_unit": "ml", "pack_count": 1,
         "status": "active", "selling_points": ["Mineral based", "Eco-friendly"],
         "ingredients": ["Zinc Oxide", "Jojoba Oil"]}
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ========== 3. price_books.json ==========
    # 正确价格书：APAC-Q2-2026-LIVE, approved, is_current=true
    # 干扰：archive版本，其他状态等
    price_books = [
        {
            "price_book_id": "pb_apac_q1_archive",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "LS-1001", "price": 45.00, "currency": "USD"},
                {"sku_id": "LS-1002", "price": 38.00, "currency": "USD"}
            ]
        },
        {
            "price_book_id": "pb_apac_q2_live",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "LS-1001", "price": 49.90, "currency": "USD"},
                {"sku_id": "LS-1002", "price": 42.50, "currency": "USD"},
                # 注意：LS-2001 已 discontinued，但price book中也可能包含，但Agent应过滤掉
                {"sku_id": "LS-2001", "price": 35.00, "currency": "USD"}
            ]
        },
        # 干扰：其他区域价格书
        {
            "price_book_id": "pb_na_q2_draft",
            "version": "NA-Q2-2026-DRAFT",
            "region": "NA",
            "status": "draft",
            "is_current": False,
            "effective_from": "2026-04-15",
            "entries": [
                {"sku_id": "DV-7001", "price": 89.00, "currency": "USD"}
            ]
        },
        # 干扰：旧版本且不当前
        {
            "price_book_id": "pb_apac_q4_2025",
            "version": "APAC-Q4-2025-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2025-10-01",
            "entries": [
                {"sku_id": "LS-1001", "price": 42.00, "currency": "USD"}
            ]
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # ========== 4. 干扰附件（未在prompt要求，但存在） ==========
    attachments = [
        {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template",
         "description": "Template for competitive category review"},
        {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice",
         "description": "Notice about Q2 pricebook activation"}
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ========== 5. 其他非必要的干扰文件（例如 contacts, accounts） ==========
    contacts = [
        {"contact_id": "c_alina", "name": "Alina Bose", "role": "Category Director",
         "email": "alina.bose@northstar.example.com"},
        {"contact_id": "c_jonas", "name": "Jonas Li", "role": "Merchandising Ops",
         "email": "jonas.li@northstar.example.com"},
        {"contact_id": "c_mira", "name": "Mira Tan", "role": "Pricing Operations Lead",
         "email": "mira.tan@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    accounts = [
        {"account_id": "acc_001", "display_name": "Mira Tan", "department": "Pricing",
         "email": "mira.tan@northstar.example.com", "permissions": ["admin"], "default_region": "APAC", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 一些额外垃圾文件（干扰）
    with open("ops/old_backup.zip", "w") as f:
        f.write("fake zip content")
    with open("data/pricing/notes.txt", "w") as f:
        f.write("Draft notes - ignore")

if __name__ == "__main__":
    build_env()
