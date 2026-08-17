import os
import json
import shutil

def build_env():
    # 确保工作区干净
    for d in ["data", "data/pricing", "ops"]:
        os.makedirs(d, exist_ok=True)

    # --- brands.json ---
    brands = [
        {
            "brand_id": "lum001",
            "brand_name": "LuminaSkin",
            "hero_category_id": "cat001",
            "hero_category_name": "Hydration Serum",
            "positioning": "Premium dermatological care",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "aqu001",
            "brand_name": "AquaPulse",
            "hero_category_id": "cat002",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Hydration for active lifestyles",
            "region_focus": "APAC",
            "price_tier": "mid-premium"
        },
        {
            "brand_id": "der001",
            "brand_name": "DermVeil",
            "hero_category_id": "cat001",
            "hero_category_name": "Hydration Serum",
            "positioning": "Clinical strength formulas",
            "region_focus": "APAC",
            "price_tier": "premium"
        },
        {
            "brand_id": "pur001",
            "brand_name": "PureLattice",
            "hero_category_id": "cat001",
            "hero_category_name": "Hydration Serum",
            "positioning": "Clean beauty, transparent ingredients",
            "region_focus": "APAC",
            "price_tier": "mid"
        },
        {
            "brand_id": "sol001",
            "brand_name": "SolarOat",
            "hero_category_id": "cat002",
            "hero_category_name": "UV Moisturizer",
            "positioning": "Budget-friendly sun protection",
            "region_focus": "APAC",
            "price_tier": "value"
        }
    ]
    with open("data/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # --- skus.json ---
    skus = [
        # LuminaSkin Hydration Serum (目标产品)
        {
            "sku_id": "lum-hs-100",
            "brand_id": "lum001",
            "brand_name": "LuminaSkin",
            "category_id": "cat001",
            "category_name": "Hydration Serum",
            "sku_name": "LuminaSkin Hydration Serum 30ml",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Deep hydration", "Fast absorbing"],
            "ingredients": ["Hyaluronic Acid", "Niacinamide"]
        },
        # LuminaSkin 另一款 Hydration Serum 但已停产（干扰）
        {
            "sku_id": "lum-hs-200",
            "brand_id": "lum001",
            "brand_name": "LuminaSkin",
            "category_id": "cat001",
            "category_name": "Hydration Serum",
            "sku_name": "LuminaSkin Hydration Serum 50ml (discontinued)",
            "size_value": 50,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "discontinued",
            "selling_points": ["Concentrated formula"],
            "ingredients": ["Hyaluronic Acid", "Vitamin C"]
        },
        # AquaPulse 同类竞品（active）
        {
            "sku_id": "aqu-hs-100",
            "brand_id": "aqu001",
            "brand_name": "AquaPulse",
            "category_id": "cat001",
            "category_name": "Hydration Serum",
            "sku_name": "AquaPulse Hydra Boost 30ml",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Ocean minerals", "Caffeine"],
            "ingredients": ["Seaweed Extract", "Caffeine"]
        },
        # DermVeil 同类竞品（active）
        {
            "sku_id": "der-hs-100",
            "brand_id": "der001",
            "brand_name": "DermVeil",
            "category_id": "cat001",
            "category_name": "Hydration Serum",
            "sku_name": "DermVeil Pro Hydrate 30ml",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Clinically tested", "Barrier repair"],
            "ingredients": ["Ceramides", "Peptides"]
        },
        # PureLattice 同类竞品（active）
        {
            "sku_id": "pur-hs-100",
            "brand_id": "pur001",
            "brand_name": "PureLattice",
            "category_id": "cat001",
            "category_name": "Hydration Serum",
            "sku_name": "PureLattice Dew Serum 30ml",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Vegan", "Recyclable packaging"],
            "ingredients": ["Aloe Vera", "Glycerin"]
        },
        # SolarOat 同类竞品（active）
        {
            "sku_id": "sol-hs-100",
            "brand_id": "sol001",
            "brand_name": "SolarOat",
            "category_id": "cat001",
            "category_name": "Hydration Serum",
            "sku_name": "SolarOat Light Serum 30ml",
            "size_value": 30,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["Oat milk extract", "Gentle formula"],
            "ingredients": ["Colloidal Oatmeal", "Panthenol"]
        },
        # 其他品牌 UV Moisturizer 类别的 SKU（干扰，同一品牌但不同类别）
        {
            "sku_id": "aqu-uv-100",
            "brand_id": "aqu001",
            "brand_name": "AquaPulse",
            "category_id": "cat002",
            "category_name": "UV Moisturizer",
            "sku_name": "AquaPulse Sun Shield 50ml",
            "size_value": 50,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["SPF 50", "Water resistant"],
            "ingredients": ["Zinc Oxide", "Vitamin E"]
        },
        {
            "sku_id": "sol-uv-100",
            "brand_id": "sol001",
            "brand_name": "SolarOat",
            "category_id": "cat002",
            "category_name": "UV Moisturizer",
            "sku_name": "SolarOat Daily Protector 60ml",
            "size_value": 60,
            "size_unit": "ml",
            "pack_count": 1,
            "status": "active",
            "selling_points": ["SPF 30", "Non-greasy"],
            "ingredients": ["Avobenzone", "Oat extract"]
        }
    ]
    with open("data/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # --- price_books.json (含干扰存档版本) ---
    live_entries = [
        {"sku_id": "lum-hs-100", "sku_name": "LuminaSkin Hydration Serum 30ml", "brand_name": "LuminaSkin", "price": 45.00},
        {"sku_id": "lum-hs-200", "sku_name": "LuminaSkin Hydration Serum 50ml", "brand_name": "LuminaSkin", "price": 62.00},
        {"sku_id": "aqu-hs-100", "sku_name": "AquaPulse Hydra Boost 30ml", "brand_name": "AquaPulse", "price": 38.00},
        {"sku_id": "der-hs-100", "sku_name": "DermVeil Pro Hydrate 30ml", "brand_name": "DermVeil", "price": 42.00},
        {"sku_id": "pur-hs-100", "sku_name": "PureLattice Dew Serum 30ml", "brand_name": "PureLattice", "price": 40.00},
        {"sku_id": "sol-hs-100", "sku_name": "SolarOat Light Serum 30ml", "brand_name": "SolarOat", "price": 35.00},
        {"sku_id": "aqu-uv-100", "sku_name": "AquaPulse Sun Shield 50ml", "brand_name": "AquaPulse", "price": 28.00},
        {"sku_id": "sol-uv-100", "sku_name": "SolarOat Daily Protector 60ml", "brand_name": "SolarOat", "price": 22.00}
    ]
    archive_entries = [
        {"sku_id": "lum-hs-100", "sku_name": "LuminaSkin Hydration Serum 30ml", "brand_name": "LuminaSkin", "price": 49.00},
        {"sku_id": "aqu-hs-100", "sku_name": "AquaPulse Hydra Boost 30ml", "brand_name": "AquaPulse", "price": 36.00}
    ]
    price_books = [
        {
            "price_book_id": "pb-live-q2",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": live_entries
        },
        {
            "price_book_id": "pb-archive-q1",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": archive_entries
        }
    ]
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # --- 附件模板（仅为丰富环境，不要求使用） ---
    os.makedirs("data/attachments", exist_ok=True)
    template_content = """# Category Review Template
Brand: {{brand}}
Category: {{category}}
Date: {{date}}
...
"""
    with open("data/attachments/category_review_template.md", "w") as f:
        f.write(template_content)

    # 附件索引
    attachments = [
        {
            "path": "data/attachments/category_review_template.md",
            "title": "Category Review Template",
            "kind": "report_template",
            "description": "Standard template for category competitive reviews"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

if __name__ == "__main__":
    build_env()
