import json
import os

def build_env():
    # ========== 品牌数据 ==========
    brands = {
        "brands": [
            {"brand_id": "B001", "brand_name": "LuminaSkin", "hero_category_id": "C01", "hero_category_name": "Hydration Serum", "positioning": "Premium", "region_focus": "APAC", "price_tier": "premium"},
            {"brand_id": "B002", "brand_name": "DermVeil", "hero_category_id": "C02", "hero_category_name": "UV Moisturizer", "positioning": "Clinical", "region_focus": "EMEA", "price_tier": "mid-premium"},
            {"brand_id": "B003", "brand_name": "AquaPulse", "hero_category_id": "C01", "hero_category_name": "Hydration Serum", "positioning": "Mass", "region_focus": "APAC", "price_tier": "value"}
        ]
    }
    os.makedirs("data/brands", exist_ok=True)
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f)

    # ========== SKU数据（包含干扰） ==========
    skus = {
        "skus": [
            # LuminaSkin 活跃SKU（应被提取）
            {"sku_id": "LS-HS-001", "brand_id": "B001", "brand_name": "LuminaSkin", "category_id": "C01", "category_name": "Hydration Serum", "sku_name": "HydraGlow Serum 30ml", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Deep hydration", "Brightening"], "ingredients": ["Hyaluronic Acid", "Vitamin C"]},
            {"sku_id": "LS-UV-002", "brand_id": "B001", "brand_name": "LuminaSkin", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "UV Shield SPF50 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Broad spectrum", "Non-greasy"], "ingredients": ["Zinc Oxide", "Vitamin E"]},
            # LuminaSkin 停产SKU（干扰）
            {"sku_id": "LS-OLD-003", "brand_id": "B001", "brand_name": "LuminaSkin", "category_id": "C01", "category_name": "Hydration Serum", "sku_name": "HydraGlow Serum 15ml (Discontinued)", "size_value": 15, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["Old formula"], "ingredients": ["Hyaluronic Acid"]},
            # DermVeil 活跃SKU（干扰品牌）
            {"sku_id": "DV-UV-001", "brand_id": "B002", "brand_name": "DermVeil", "category_id": "C02", "category_name": "UV Moisturizer", "sku_name": "Derma Shield SPF30 60ml", "size_value": 60, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Calming", "Protection"], "ingredients": ["Niacinamide", "Ceramides"]},
            # AquaPulse 活跃SKU（干扰品牌）
            {"sku_id": "AP-HS-001", "brand_id": "B003", "brand_name": "AquaPulse", "category_id": "C01", "category_name": "Hydration Serum", "sku_name": "Aqua Burst Serum 50ml", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["Water burst", "Affordable"], "ingredients": ["Glycerin", "Aloe Vera"]},
        ]
    }
    os.makedirs("data/skus", exist_ok=True)
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f)

    # ========== 价目表（包含历史版本和当前版本） ==========
    price_books = {
        "price_books": [
            {
                "price_book_id": "PB-APAC-Q1-2026",
                "version": "APAC-Q1-2026-ARCHIVE",
                "region": "APAC",
                "status": "archived",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": [
                    {"sku_id": "LS-HS-001", "price": 45.00},
                    {"sku_id": "LS-UV-002", "price": 38.00},
                    {"sku_id": "LS-OLD-003", "price": 25.00},   # 停产SKU仍在归档价目表中
                    {"sku_id": "DV-UV-001", "price": 52.00},
                    {"sku_id": "AP-HS-001", "price": 19.90}
                ]
            },
            {
                "price_book_id": "PB-APAC-Q2-2026",
                "version": "APAC-Q2-2026-LIVE",
                "region": "APAC",
                "status": "approved",
                "is_current": True,
                "effective_from": "2026-04-01",
                "entries": [
                    {"sku_id": "LS-HS-001", "price": 48.50},   # 新价格
                    {"sku_id": "LS-UV-002", "price": 40.00},   # 新价格
                    # LS-OLD-003 不在当前价目表中
                    {"sku_id": "DV-UV-001", "price": 55.00},
                    {"sku_id": "AP-HS-001", "price": 21.50}
                ]
            }
        ]
    }
    os.makedirs("data/pricing", exist_ok=True)
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f)

    # ========== 杂项干扰文件 ==========
    os.makedirs("ops", exist_ok=True)
    with open("ops/README.md", "w") as f:
        f.write("# Ops notes\nDo not modify anything here.\n")

    os.makedirs("notes", exist_ok=True)
    with open("notes/draft_report.txt", "w") as f:
        f.write("LuminaSkin pricing draft... (outdated)\n")

if __name__ == "__main__":
    build_env()
