import json, os, random
from pathlib import Path

def build_env():
    # ------- 品牌数据 -------
    brands = [
        {"brand_id": "BR-AQUA", "brand_name": "AquaPulse", "hero_category_id": "CAT-HS", "hero_category_name": "Hydration Serum", "positioning": "海洋滋养", "region_focus": "APAC", "price_tier": "mid"},
        {"brand_id": "BR-DERM", "brand_name": "DermVeil", "hero_category_id": "CAT-HS", "hero_category_name": "Hydration Serum", "positioning": "屏障修复", "region_focus": "EMEA", "price_tier": "premium"},
        {"brand_id": "BR-LUMI", "brand_name": "LuminaSkin", "hero_category_id": "CAT-HS", "hero_category_name": "Hydration Serum", "positioning": "科技亮肤", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "BR-PURE", "brand_name": "PureLattice", "hero_category_id": "CAT-HS", "hero_category_name": "Hydration Serum", "positioning": "纯净配方", "region_focus": "NA", "price_tier": "value"},
        {"brand_id": "BR-SOLA", "brand_name": "SolarOat", "hero_category_id": "CAT-HS", "hero_category_name": "Hydration Serum", "positioning": "日间防护", "region_focus": "APAC", "price_tier": "mid-premium"},
    ]

    # ------- SKU 数据 -------
    # 注意：只关心 Hydration Serum（CAT-HS），但会混入 UV Moisturizer 和 inactive 干扰
    skus = [
        # LuminaSkin (2个正式 + 1个inactive干扰)
        {"sku_id": "SKU-LUMI-01", "brand_id": "BR-LUMI", "brand_name": "LuminaSkin", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Glow Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["专利玻尿酸", "维C焕亮", "水光肌", "低敏配方"], "ingredients": ["玻尿酸", "维生素C", "神经酰胺"]},
        {"sku_id": "SKU-LUMI-02", "brand_id": "BR-LUMI", "brand_name": "LuminaSkin", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Hydra Boost Serum", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["三倍锁水", "快速吸收", "无油配方"], "ingredients": ["甘油", "透明质酸", "角鲨烷"]},
        {"sku_id": "SKU-LUMI-03", "brand_id": "BR-LUMI", "brand_name": "LuminaSkin", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Legacy Hydra", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "inactive", "selling_points": ["老版保湿", "基础款"], "ingredients": ["甘油", "水"]},

        # AquaPulse (2个正式)
        {"sku_id": "SKU-AQUA-01", "brand_id": "BR-AQUA", "brand_name": "AquaPulse", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Marine Serum", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["深海矿物质", "强效保湿"], "ingredients": ["海水提取物", "海藻糖"]},
        {"sku_id": "SKU-AQUA-02", "brand_id": "BR-AQUA", "brand_name": "AquaPulse", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Ocean Hydrator", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["海洋酵素", "舒缓", "全天保湿", "清爽质地", "SPF15"], "ingredients": ["酵素复合物", "芦荟", "黄瓜"]},

        # DermVeil (1个正式 + 1个UV品类干扰)
        {"sku_id": "SKU-DERM-01", "brand_id": "BR-DERM", "brand_name": "DermVeil", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Barrier Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["屏障修复", "脂质补充", "舒缓泛红"], "ingredients": ["神经酰胺", "胆固醇", "脂肪酸"]},
        {"sku_id": "SKU-DERM-02", "brand_id": "BR-DERM", "brand_name": "DermVeil", "category_id": "CAT-UV", "category_name": "UV Moisturizer", "sku_name": "UV Shield", "size_value": 60, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["广谱防晒", "清爽"], "ingredients": ["氧化锌", "二氧化钛"]},

        # PureLattice (2个正式)
        {"sku_id": "SKU-PURE-01", "brand_id": "BR-PURE", "brand_name": "PureLattice", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Pure Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["10种纯植物提取", "无香精", "敏感肌适用"], "ingredients": ["积雪草", "绿茶", "洋甘菊"]},
        {"sku_id": "SKU-PURE-02", "brand_id": "BR-PURE", "brand_name": "PureLattice", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Radiance Serum", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["维C衍生物", "提亮", "抗氧化", "温和去角质"], "ingredients": ["VC-IP", "乳酸", "烟酰胺"]},

        # SolarOat (1个正式 + 1个类别正确但status inactive干扰)
        {"sku_id": "SKU-SOLA-01", "brand_id": "BR-SOLA", "brand_name": "SolarOat", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Sun Defense Serum", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["天然燕麦", "UV保护", "舒缓日晒"], "ingredients": ["燕麦β-葡聚糖", "维生素E", "芦荟"]},
        {"sku_id": "SKU-SOLA-02", "brand_id": "BR-SOLA", "brand_name": "SolarOat", "category_id": "CAT-HS", "category_name": "Hydration Serum", "sku_name": "Morning Dew Serum", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "inactive", "selling_points": ["旧版", "保湿"], "ingredients": ["水", "甘油"]},
    ]

    # ------- 价格书 -------
    # 当前有效价格书 (APAC-Q2-2026-LIVE)
    live_entries = [
        {"sku_id": "SKU-LUMI-01", "price": 68.0},
        {"sku_id": "SKU-LUMI-02", "price": 72.5},
        {"sku_id": "SKU-AQUA-01", "price": 45.0},
        {"sku_id": "SKU-AQUA-02", "price": 52.0},
        {"sku_id": "SKU-DERM-01", "price": 89.0},
        {"sku_id": "SKU-PURE-01", "price": 33.0},
        {"sku_id": "SKU-PURE-02", "price": 39.0},
        {"sku_id": "SKU-SOLA-01", "price": 55.0},
    ]
    live_price_book = {
        "price_book_id": "PB-APAC-Q2-2026",
        "version": "APAC-Q2-2026-LIVE",
        "region": "APAC",
        "status": "approved",
        "is_current": True,
        "effective_from": "2026-04-01",
        "entries": live_entries
    }

    # 旧归档价格书 (APAC-Q1-2026-ARCHIVE)
    archive_entries = [
        {"sku_id": "SKU-LUMI-01", "price": 65.0},
        {"sku_id": "SKU-AQUA-01", "price": 42.0},
        {"sku_id": "SKU-DERM-01", "price": 85.0},
        {"sku_id": "SKU-SOLA-01", "price": 53.0},
    ]
    archive_price_book = {
        "price_book_id": "PB-APAC-Q1-2026",
        "version": "APAC-Q1-2026-ARCHIVE",
        "region": "APAC",
        "status": "archived",
        "is_current": False,
        "effective_from": "2026-01-01",
        "entries": archive_entries
    }

    price_books = [live_price_book, archive_price_book]

    # ------- 写入文件 -------
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    with open("data/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    with open("data/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    with open("data/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # 额外加一个无关的附件文件作为干扰
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/category_review_template.md", "w") as f:
        f.write("# Category Review Template\n\nFill in details here...")

if __name__ == "__main__":
    build_env()
