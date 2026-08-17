import os
import json

def build_env():
    # 基础目录
    os.makedirs("raw_data/brands", exist_ok=True)
    os.makedirs("raw_data/skus", exist_ok=True)
    os.makedirs("raw_data/pricing", exist_ok=True)
    os.makedirs("raw_data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # brands.json
    brands = [
        {"brand_id": "LS", "brand_name": "LuminaSkin", "hero_category_id": "UV", "hero_category_name": "UV Moisturizer", "positioning": "Mid-premium", "region_focus": "APAC", "price_tier": "mid-premium"},
        {"brand_id": "DV", "brand_name": "DermVeil", "hero_category_id": "UV", "hero_category_name": "UV Moisturizer", "positioning": "Premium", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "AP", "brand_name": "AquaPulse", "hero_category_id": "UV", "hero_category_name": "UV Moisturizer", "positioning": "Mid", "region_focus": "APAC", "price_tier": "mid"},
        {"brand_id": "PL", "brand_name": "PureLattice", "hero_category_id": "HY", "hero_category_name": "Hydration Serum", "positioning": "Value", "region_focus": "APAC", "price_tier": "value"},
        {"brand_id": "SO", "brand_name": "SolarOat", "hero_category_id": "HY", "hero_category_name": "Hydration Serum", "positioning": "Mid-premium", "region_focus": "APAC", "price_tier": "mid-premium"}
    ]
    with open("raw_data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # skus.json — 包含目标品类、干扰品类、下架状态
    skus = [
        # LuminaSkin UV Moisturizer (active)
        {"sku_id": "LS-UV-001", "brand_id": "LS", "brand_name": "LuminaSkin", "category_id": "UV", "category_name": "UV Moisturizer", "sku_name":"Lumina Daily Shield SPF50", "size_value":50,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Lightweight","Non-greasy"],"ingredients":["Zinc Oxide","Aloe Vera"]},
        {"sku_id": "LS-UV-002", "brand_id": "LS", "brand_name": "LuminaSkin", "category_id": "UV", "category_name": "UV Moisturizer", "sku_name":"Lumina Brightening UV Cream", "size_value":40,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Brightening","Anti-pollution"],"ingredients":["Vitamin C","SPF 30"]},
        {"sku_id": "LS-UV-003", "brand_id": "LS", "brand_name": "LuminaSkin", "category_id": "UV", "category_name": "UV Moisturizer", "sku_name":"Lumina Matte Finish SPF45", "size_value":30,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Matte finish","Oil control"],"ingredients":["Salicylic Acid","SPF 45"]},
        # LuminaSkin UV 下架 SKU (干扰)
        {"sku_id": "LS-UV-099", "brand_id": "LS", "brand_name": "LuminaSkin", "category_id": "UV", "category_name": "UV Moisturizer", "sku_name":"Lumina Old Formula", "size_value":50,"size_unit":"ml","pack_count":1,"status":"discontinued","selling_points":["Older version"],"ingredients":["Zinc Oxide"]},
        # LuminaSkin 精华液品类 (干扰)
        {"sku_id": "LS-HY-001", "brand_id": "LS", "brand_name": "LuminaSkin", "category_id": "HY", "category_name": "Hydration Serum", "sku_name":"Lumina Deep Hydrate", "size_value":30,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Hydrating"],"ingredients":["Hyaluronic Acid"]},
        # DermVeil UV Moisturizer (active)
        {"sku_id": "DV-UV-101", "brand_id": "DV", "brand_name": "DermVeil", "category_id": "UV", "category_name": "UV Moisturizer", "sku_name":"DermVeil Pro Protect SPF60", "size_value":50,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["High protection","Dermatologist tested"],"ingredients":["Zinc Oxide","Titanium Dioxide"]},
        {"sku_id": "DV-UV-102", "brand_id": "DV", "brand_name": "DermVeil", "category_id": "UV", "category_name": "UV Moisturizer", "sku_name":"DermVeil Age Defense UV", "size_value":30,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Anti-aging","SPF 55"],"ingredients":["Retinol","Zinc Oxide"]},
        # DermVeil UV 下架 SKU (干扰)
        {"sku_id": "DV-UV-199", "brand_id": "DV", "brand_name": "DermVeil", "category_id": "UV", "category_name": "UV Moisturizer", "sku_name":"DermVeil Classic", "size_value":50,"size_unit":"ml","pack_count":1,"status":"discontinued","selling_points":["Old"],"ingredients":["Zinc"]},
        # AquaPulse UV Moisturizer (active)
        {"sku_id": "AP-UV-201", "brand_id": "AP", "brand_name": "AquaPulse", "category_id": "UV", "category_name": "UV Moisturizer", "sku_name":"AquaPulse Ocean Shield SPF30", "size_value":100,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Reef-safe","Water-resistant"],"ingredients":["Coconut Oil","Zinc Oxide"]},
        # PureLattice UV 品类 (干扰，但品牌不在比较范围)
        {"sku_id": "PL-UV-001", "brand_id": "PL", "brand_name": "PureLattice", "category_id": "UV", "category_name": "UV Moisturizer", "sku_name":"PureLattice Mineral Shield", "size_value":60,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Clean ingredients"],"ingredients":["Non-nano Zinc"]}
    ]
    with open("raw_data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # 价格册 — 两个版本，一个归档一个当前
    price_books = [
        {
            "price_book_id": "PB-ARCH-2026Q1",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "LS-UV-001", "price": 22.99, "currency": "USD"},
                {"sku_id": "LS-UV-002", "price": 27.99, "currency": "USD"},
                {"sku_id": "DV-UV-101", "price": 20.99, "currency": "USD"},
                {"sku_id": "AP-UV-201", "price": 19.99, "currency": "USD"}
            ]
        },
        {
            "price_book_id": "PB-LIVE-2026Q2",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": [
                {"sku_id": "LS-UV-001", "price": 24.99, "currency": "USD"},
                {"sku_id": "LS-UV-002", "price": 29.99, "currency": "USD"},
                {"sku_id": "LS-UV-003", "price": 19.99, "currency": "USD"},
                {"sku_id": "DV-UV-101", "price": 22.99, "currency": "USD"},
                {"sku_id": "DV-UV-102", "price": 27.99, "currency": "USD"},
                {"sku_id": "AP-UV-201", "price": 21.99, "currency": "USD"}
            ]
        }
    ]
    with open("raw_data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # 附件：模板
    template_content = """{
  "report_type": "category_competitor_review",
  "price_book": "APAC-Q2-2026-LIVE",
  "category": "UV Moisturizer",
  "brands": {
    "LuminaSkin": {
      "skus": [
        {
          "sku_id": "<string>",
          "sku_name": "<string>",
          "current_price": <number>
        }
      ],
      "avg_price": <number>
    },
    "DermVeil": {
      "skus": [
        {
          "sku_id": "<string>",
          "sku_name": "<string>",
          "current_price": <number>
        }
      ],
      "avg_price": <number>
    },
    "AquaPulse": {
      "skus": [
        {
          "sku_id": "<string>",
          "sku_name": "<string>",
          "current_price": <number>
        }
      ],
      "avg_price": <number>
    }
  }
}"""
    with open("raw_data/attachments/category_review_template.md", "w") as f:
        f.write(template_content)

    # 另一个附件（干扰项不会影响主任务）
    notice = "# Current Price Book Notice\nPlease refer to the price book with `is_current` set to true.\n"
    with open("raw_data/attachments/current_pricebook_notice.md", "w") as f:
        f.write(notice)

    # 额外干扰文件
    with open("raw_data/old_price_books.csv", "w") as f:
        f.write("sku,price\nLS-UV-001,22.99\n")
    with open("raw_data/notes.txt", "w") as f:
        f.write("Note: Only active SKUs should be considered.\n")

if __name__ == "__main__":
    build_env()
