import os
import json
import shutil

def build_env():
    # 清理可能存在的旧目录
    shutil.rmtree("data", ignore_errors=True)
    shutil.rmtree("reports", ignore_errors=True)

    # ---------- 创建 data 目录 ----------
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/brands", exist_ok=True)

    # ---------- brands.json ----------
    brands = {
        "brands": [
            {"brand_id": "B001", "brand_name": "AquaPulse", "hero_category_id": "C01", "hero_category_name": "Hydration Serum", "positioning": "Mass-premium", "region_focus": "APAC", "price_tier": "mid-premium"},
            {"brand_id": "B002", "brand_name": "DermVeil", "hero_category_id": "C02", "hero_category_name": "UV Moisturizer", "positioning": "Clinical derma", "region_focus": "EMEA", "price_tier": "premium"},
            {"brand_id": "B003", "brand_name": "LuminaSkin", "hero_category_id": "C01", "hero_category_name": "Hydration Serum", "positioning": "Brightening expert", "region_focus": "APAC", "price_tier": "mid"},
            {"brand_id": "B004", "brand_name": "PureLattice", "hero_category_id": "C02", "hero_category_name": "UV Moisturizer", "positioning": "Eco-natural", "region_focus": "NA", "price_tier": "value"},
            {"brand_id": "B005", "brand_name": "SolarOat", "hero_category_id": "C01", "hero_category_name": "Hydration Serum", "positioning": "Sensitive care", "region_focus": "APAC", "price_tier": "mid"},
        ]
    }
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # ---------- skus.json ----------
    skus = {
        "skus": [
            # LuminaSkin SKUs
            {"sku_id": "SKU-LS-001", "brand_id": "B003", "brand_name": "LuminaSkin", "category_id": "C01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Brightening Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Vitamin C", "Niacinamide"], "ingredients": ["Ascorbic Acid", "Niacinamide", "Hyaluronic Acid"]},
            {"sku_id": "SKU-LS-002", "brand_id": "B003", "brand_name": "LuminaSkin", "category_id": "C01", "category_name": "Hydration Serum", "sku_name": "LuminaSkin Glow Booster 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Peptide complex", "Ceramide"], "ingredients": ["Ceramide NP", "Palmitoyl Tripeptide-1", "Glycerin"]},
            {"sku_id": "SKU-LS-003", "brand_id": "B003", "brand_name": "LuminaSkin", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "LuminaSkin Daily SPF 40", "size_value": 60, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Broad spectrum", "Lightweight"], "ingredients": ["Zinc Oxide", "Titanium Dioxide", "Aloe Vera"]},
            # 干扰 SKU: 其他品牌
            {"sku_id": "SKU-AP-001", "brand_id": "B001", "brand_name": "AquaPulse", "category_id": "C01", "category_name": "Hydration Serum", "sku_name": "AquaPulse Hydra Boost 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Hyaluronic acid", "Sea water"], "ingredients": ["Sodium Hyaluronate", "Marine Collagen"]},
            {"sku_id": "SKU-DV-001", "brand_id": "B002", "brand_name": "DermVeil", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "DermVeil Shield SPF 50", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Water resistant", "Anti-pollution"], "ingredients": ["Avobenzone", "Octocrylene", "Vitamin E"]},
            {"sku_id": "SKU-PL-001", "brand_id": "B004", "brand_name": "PureLattice", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "PureLattice Mineral SPF 30", "size_value": 75, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Mineral based", "Reef safe"], "ingredients": ["Non-nano Zinc Oxide", "Jojoba Oil"]},
            {"sku_id": "SKU-SO-001", "brand_id": "B005", "brand_name": "SolarOat", "category_id": "C01", "category_name": "Hydration Serum", "sku_name": "SolarOat Calm Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Oat extract", "Colloidal oatmeal"], "ingredients": ["Avena Sativa Kernel Extract", "Panthenol"]},
        ]
    }
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # ---------- price_books.json ----------
    price_books = {
        "price_books": [
            {
                "price_book_id": "PB-ARCHIVE-Q1",
                "version": "APAC-Q1-2026-ARCHIVE",
                "region": "APAC",
                "status": "archived",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": [
                    {"sku_id": "SKU-LS-001", "price": 42.0, "currency": "USD"},
                    {"sku_id": "SKU-LS-002", "price": 52.0, "currency": "USD"},
                    {"sku_id": "SKU-LS-003", "price": 58.0, "currency": "USD"},
                    {"sku_id": "SKU-AP-001", "price": 28.0, "currency": "USD"},
                ]
            },
            {
                "price_book_id": "PB-LIVE-Q2",
                "version": "APAC-Q2-2026-LIVE",
                "region": "APAC",
                "status": "approved",
                "is_current": True,
                "effective_from": "2026-04-01",
                "entries": [
                    {"sku_id": "SKU-LS-001", "price": 45.0, "currency": "USD"},
                    {"sku_id": "SKU-LS-002", "price": 55.0, "currency": "USD"},
                    {"sku_id": "SKU-LS-003", "price": 60.0, "currency": "USD"},
                    {"sku_id": "SKU-AP-001", "price": 30.0, "currency": "USD"},
                    {"sku_id": "SKU-DV-001", "price": 78.0, "currency": "USD"},
                    # 故意加入一个重复的 LuminaSkin SKU 但价格不同（干扰，但同一个 SKU 出现在两个 entry 可能代表同一 SKU 两个价格？我们设计为只有一个 entry per SKU，这里没有重复）
                ]
            },
            # 一个额外的无效价格本（无 entries）
            {
                "price_book_id": "PB-DRAFT",
                "version": "APAC-Q2-2026-DRAFT",
                "region": "APAC",
                "status": "draft",
                "is_current": False,
                "effective_from": "2026-05-01",
                "entries": []
            }
        ]
    }
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    print("Environment built successfully: data/ with brands, skus, pricing; reports/ will be created by agent.")

if __name__ == "__main__":
    build_env()
