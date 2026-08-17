import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- brands.json ----------
    brands = {
        "brands": [
            {"brand_id": "LS", "brand_name": "LuminaSkin", "hero_category_id": "HC01",
             "hero_category_name": "Hydration Serum", "positioning": "Premium",
             "region_focus": "APAC", "price_tier": "premium"},
            {"brand_id": "DV", "brand_name": "DermVeil", "hero_category_id": "HC02",
             "hero_category_name": "UV Moisturizer", "positioning": "Clinical",
             "region_focus": "APAC", "price_tier": "mid-premium"},
            {"brand_id": "AP", "brand_name": "AquaPulse", "hero_category_id": "HC01",
             "hero_category_name": "Hydration Serum", "positioning": "Mass",
             "region_focus": "Global", "price_tier": "value"},
            {"brand_id": "PL", "brand_name": "PureLattice", "hero_category_id": "HC02",
             "hero_category_name": "UV Moisturizer", "positioning": "Sustainable",
             "region_focus": "APAC", "price_tier": "mid"},
            {"brand_id": "SO", "brand_name": "SolarOat", "hero_category_id": "HC01",
             "hero_category_name": "Hydration Serum", "positioning": "Natural",
             "region_focus": "EMEA", "price_tier": "value"},
        ]
    }
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # ---------- skus.json ----------
    skus = {
        "skus": [
            {"sku_id": "LS-001", "brand_id": "LS", "brand_name": "LuminaSkin",
             "category_id": "HC01", "category_name": "Hydration Serum",
             "sku_name": "Hydrating Serum 30ml", "size_value": 30, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["Instant hydration"],
             "ingredients": ["Hyaluronic Acid", "Glycerin"]},
            {"sku_id": "LS-002", "brand_id": "LS", "brand_name": "LuminaSkin",
             "category_id": "HC01", "category_name": "Hydration Serum",
             "sku_name": "Brightening Cream 50ml", "size_value": 50, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["Brightening"],
             "ingredients": ["Vitamin C", "Niacinamide"]},
            {"sku_id": "LS-003", "brand_id": "LS", "brand_name": "LuminaSkin",
             "category_id": "HC02", "category_name": "UV Moisturizer",
             "sku_name": "Sunscreen SPF50 100ml", "size_value": 100, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["SPF50"],
             "ingredients": ["Zinc Oxide", "Titanium Dioxide"]},
            {"sku_id": "DV-001", "brand_id": "DV", "brand_name": "DermVeil",
             "category_id": "HC02", "category_name": "UV Moisturizer",
             "sku_name": "Repair Night Mask 30ml", "size_value": 30, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["Repair"],
             "ingredients": ["Retinol", "Peptides"]},
            {"sku_id": "DV-002", "brand_id": "DV", "brand_name": "DermVeil",
             "category_id": "HC01", "category_name": "Hydration Serum",
             "sku_name": "Vitamin C Serum 20ml", "size_value": 20, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["Antioxidant"],
             "ingredients": ["Ascorbic Acid", "Ferulic Acid"]},
            {"sku_id": "DV-003", "brand_id": "DV", "brand_name": "DermVeil",
             "category_id": "HC01", "category_name": "Hydration Serum",
             "sku_name": "Eye Cream 15ml", "size_value": 15, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["Anti-aging"],
             "ingredients": ["Caffeine", "Ceramides"]},
            {"sku_id": "AP-001", "brand_id": "AP", "brand_name": "AquaPulse",
             "category_id": "HC01", "category_name": "Hydration Serum",
             "sku_name": "Aqua Tonic 200ml", "size_value": 200, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["Refreshing"],
             "ingredients": ["Aloe", "Green Tea"]},
            {"sku_id": "PL-001", "brand_id": "PL", "brand_name": "PureLattice",
             "category_id": "HC02", "category_name": "UV Moisturizer",
             "sku_name": "Pure Moisturizer 75ml", "size_value": 75, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["Eco-friendly"],
             "ingredients": ["Shea Butter", "Jojoba Oil"]},
            {"sku_id": "SO-001", "brand_id": "SO", "brand_name": "SolarOat",
             "category_id": "HC01", "category_name": "Hydration Serum",
             "sku_name": "Solar Cleanser 150ml", "size_value": 150, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["Gentle"],
             "ingredients": ["Oat Extract", "Chamomile"]},
            {"sku_id": "SO-002", "brand_id": "SO", "brand_name": "SolarOat",
             "category_id": "HC02", "category_name": "UV Moisturizer",
             "sku_name": "Solar Lotion 200ml", "size_value": 200, "size_unit": "ml",
             "pack_count": 1, "status": "active", "selling_points": ["Lightweight"],
             "ingredients": ["Aloe", "Vitamin E"]},
        ]
    }
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # ---------- price_books.json ----------
    def entry(sku_id, price, currency="USD", unit="cents"):
        return {"sku_id": sku_id, "price": price, "currency": currency, "unit": unit}

    old_entries = [
        entry("LS-001", 3500),
        entry("LS-002", 4200),
        entry("LS-003", 2800),
        entry("DV-001", 5500),
        entry("DV-002", 3200),
        entry("DV-003", 2100),
        entry("AP-001", 1800),
        entry("PL-001", 3000),
        entry("SO-001", 1500),
    ]
    # 新价格书包含脏数据：字符串价格、新出现的SKU、重复价格（故意设置相同值避免歧义）
    new_entries = [
        entry("LS-001", 2400),
        entry("LS-002", 3400),        # drop = 19.0%  < 20%
        entry("LS-003", 2200),        # drop = 21.4%
        entry("DV-001", 3800),        # drop = 30.9%
        entry("DV-002", 2900),        # drop =  9.4%
        entry("DV-003", 1500),        # drop = 28.6%
        entry("AP-001", 1600),        # drop = 11.1% 品牌不符
        entry("PL-001", 2400),        # drop = 20.0% 等于20%不算
        entry("SO-001", 1200),        # drop = 20.0% 等于20%不算
        entry("SO-002", "unknown"),   # 脏数据，非数字
        entry("LS-001", 2400),        # 重复，但价格相同，不影响
    ]

    price_books = {
        "price_books": [
            {
                "price_book_id": "APAC-Q1-2026-ARCHIVE",
                "version": "APAC-Q1-2026-ARCHIVE",
                "region": "APAC",
                "status": "archived",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": old_entries
            },
            {
                "price_book_id": "APAC-Q2-2026-LIVE",
                "version": "APAC-Q2-2026-LIVE",
                "region": "APAC",
                "status": "approved",
                "is_current": True,
                "effective_from": "2026-04-01",
                "entries": new_entries
            }
        ]
    }
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # ---------- 模板附件 ----------
    template = {
        "schema_version": "1.0",
        "report_header": "Price Drops >20% for LuminaSkin & DermVeil (Q1 vs Q2 2026)",
        "generated_at": "PLACEHOLDER_DATETIME",
        "drops": [
            {
                "sku_id": "PLACEHOLDER",
                "sku_name": "PLACEHOLDER",
                "old_price": 0,
                "new_price": 0,
                "drop_percent": 0.0
            }
        ]
    }
    with open("data/attachments/price_drop_template.json", "w") as f:
        json.dump(template, f, indent=2)
