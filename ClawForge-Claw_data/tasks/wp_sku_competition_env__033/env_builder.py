import os
import json
import shutil

def build_env():
    # 清空工作区（从头构建）
    target = os.getcwd()  # 已在 
    for item in os.listdir(target):
        path = os.path.join(target, item)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    # ---------- 目录结构 ----------
    os.makedirs("data/skus")
    os.makedirs("data/pricing")
    os.makedirs("data/attachments")
    os.makedirs("data/contacts")
    os.makedirs("data/brands")
    os.makedirs("reports")  # 空目录，等着 agent 写入

    # ---------- 品牌 ----------
    brands = [
        {"brand_id": "B001", "brand_name": "AquaPulse", "hero_category_id": "C01", "hero_category_name": "Hydration Serum", "positioning": "mass", "region_focus": "APAC", "price_tier": "mid"},
        {"brand_id": "B002", "brand_name": "DermVeil", "hero_category_id": "C02", "hero_category_name": "UV Moisturizer", "positioning": "premium", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "B003", "brand_name": "LuminaSkin", "hero_category_id": "C01", "hero_category_name": "Hydration Serum", "positioning": "luxury", "region_focus": "EMEA", "price_tier": "premium"},
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # ---------- SKU（DermVeil 有 6 个 SKU，其中 2 个 discontinued，1 个重复ID陷阱）----------
    skus = [
        # DermVeil active SKUs
        {"sku_id": "DV-1001", "brand_id": "B002", "brand_name": "DermVeil", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "UV Shield SPF50", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["broad spectrum", "water resistant"], "ingredients": ["zinc oxide", "titanium dioxide"]},
        {"sku_id": "DV-1002", "brand_id": "B002", "brand_name": "DermVeil", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "Day Repair SPF30", "size_value": 75, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["anti-aging", "lightweight"], "ingredients": ["hyaluronic acid", "niacinamide"]},
        {"sku_id": "DV-1003", "brand_id": "B002", "brand_name": "DermVeil", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "Night Renew Cream", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["retinol", "peptide complex"], "ingredients": ["retinol", "peptide"]},
        # DermVeil discontinued
        {"sku_id": "DV-1004", "brand_id": "B002", "brand_name": "DermVeil", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "Classic Sunblock", "size_value": 100, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["basic protection"], "ingredients": ["avobenzone"]},
        {"sku_id": "DV-1005", "brand_id": "B002", "brand_name": "DermVeil", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "Old Formula SPF30", "size_value": 60, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["outdated"], "ingredients": ["oxybenzone"]},
        # 干扰：重复 sku_id 但另一个品牌（错误关联）
        {"sku_id": "DV-1001", "brand_id": "B003", "brand_name": "LuminaSkin", "category_id": "C01", "category_name": "Hydration Serum", "sku_name": "Glow Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["brightening"], "ingredients": ["vitamin c"]},
        # 其他品牌 SKU
        {"sku_id": "AQ-001", "brand_id": "B001", "brand_name": "AquaPulse", "category_id": "C01", "category_name": "Hydration Serum", "sku_name": "Hydro Boost", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["hydration"], "ingredients": ["glycerin"]},
    ]
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ---------- 价格册 ----------
    price_books = [
        # 归档版（Q1）
        {
            "price_book_id": "PB-ARCHIVE",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "DV-1001", "unit_price": 18.50, "currency": "USD"},
                {"sku_id": "DV-1002", "unit_price": 22.00, "currency": "USD"},
                {"sku_id": "DV-1004", "unit_price": 12.00, "currency": "USD"},  # discontinued SKU 在旧册中
            ]
        },
        # Q2 当前生效
        {
            "price_book_id": "PB-LIVE",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "DV-1001", "unit_price": 19.99, "currency": "USD"},
                {"sku_id": "DV-1002", "unit_price": 24.50, "currency": "USD"},
                {"sku_id": "DV-1003", "unit_price": 34.00, "currency": "USD"},
                # 干扰：也包含了 discontinued 的 SKU (DV-1004) 但价格不同，agent 需通过 SKU status 过滤
                {"sku_id": "DV-1004", "unit_price": 13.50, "currency": "USD"},
                # 干扰：重复的 sku_id 跨品牌，但 price_book 只认 sku_id，agent 可能误信 LuminaSkin 的 DV-1001
                # 注意：实际 LuminaSkin 的 DV-1001 不在当前 price_book 中，但单独有一条 entry 指向 DV-1001 – 没有品牌关联，需要 SKU 表来判断
                # 价格册里没有歧义，都是 DV-1001 但是只有一条，不过 SKU 表中有两条 DV-1001，agent 需根据 brand_id 筛选 DermVeil
            ]
        },
        # 另一个品牌的当前价格册（干扰）
        {
            "price_book_id": "PB-LIVE-AQUA",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "AQ-001", "unit_price": 15.00, "currency": "USD"},
            ]
        },
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # ---------- 附件（干扰）----------
    attachments = [
        {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template", "description": "Template for quarterly review"},
        {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice", "description": "Notice about Q2 price book release"}
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---------- 联系方式（无关）----------
    contacts = [
        {"contact_id": "C001", "name": "Alina Bose", "role": "Category Director", "email": "alina.bose@northstar.example.com"},
        {"contact_id": "C002", "name": "Jonas Li", "role": "Merchandising Ops", "email": "jonas.li@northstar.example.com"},
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
