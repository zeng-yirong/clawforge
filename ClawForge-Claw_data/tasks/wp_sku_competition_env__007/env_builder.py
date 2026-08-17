import json
import os

def build_env():
    # Create directory structure
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # agent will write here
    os.makedirs("data", exist_ok=True)

    # --- SKUs ---
    skus = [
        {"sku_id": "LS-HS-001", "brand_id": "LuminaSkin", "brand_name": "LuminaSkin",
         "category_id": "HS", "category_name": "Hydration Serum",
         "sku_name": "LuminaSkin Hydra Boost", "size_value": 30, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["24h moisture", "sensitive skin"],
         "ingredients": ["hyaluronic acid", "glycerin"]},
        {"sku_id": "LS-HS-002", "brand_id": "LuminaSkin", "brand_name": "LuminaSkin",
         "category_id": "HS", "category_name": "Hydration Serum",
         "sku_name": "LuminaSkin Glow Drops", "size_value": 30, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["brightening", "vitamin C"],
         "ingredients": ["ascorbic acid", "tocopherol"]},
        {"sku_id": "AP-HS-001", "brand_id": "AquaPulse", "brand_name": "AquaPulse",
         "category_id": "HS", "category_name": "Hydration Serum",
         "sku_name": "AquaPulse Hydro Burst", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["ocean minerals", "refreshing"],
         "ingredients": ["sea water", "aloe vera"]},
        {"sku_id": "AP-HS-002", "brand_id": "AquaPulse", "brand_name": "AquaPulse",
         "category_id": "HS", "category_name": "Hydration Serum",
         "sku_name": "AquaPulse Deep Revive", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["revitalizing", "anti‑aging"],
         "ingredients": ["retinol", "peptides"]},
        {"sku_id": "DV-HS-001", "brand_id": "DermVeil", "brand_name": "DermVeil",
         "category_id": "HS", "category_name": "Hydration Serum",
         "sku_name": "DermVeil Barrier Shield", "size_value": 40, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["ceramide complex", "for dry skin"],
         "ingredients": ["ceramide NP", "niacinamide"]},
        {"sku_id": "DV-HS-002", "brand_id": "DermVeil", "brand_name": "DermVeil",
         "category_id": "HS", "category_name": "Hydration Serum",
         "sku_name": "DermVeil Soothing Serum", "size_value": 40, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["calming", "redness reduction"],
         "ingredients": ["centella asiatica", "panthenol"]},
        # UV Moisturizer category
        {"sku_id": "LS-UV-001", "brand_id": "LuminaSkin", "brand_name": "LuminaSkin",
         "category_id": "UV", "category_name": "UV Moisturizer",
         "sku_name": "LuminaSkin Sun Shield SPF50", "size_value": 50, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["broad spectrum", "non‑greasy"],
         "ingredients": ["zinc oxide", "titanium dioxide"]},
        {"sku_id": "AP-UV-001", "brand_id": "AquaPulse", "brand_name": "AquaPulse",
         "category_id": "UV", "category_name": "UV Moisturizer",
         "sku_name": "AquaPulse Ocean Protect SPF30", "size_value": 75, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["water resistant", "reef safe"],
         "ingredients": ["octocrylene", "avobenzone"]},
        {"sku_id": "DV-UV-001", "brand_id": "DermVeil", "brand_name": "DermVeil",
         "category_id": "UV", "category_name": "UV Moisturizer",
         "sku_name": "DermVeil Matte Finish SPF40", "size_value": 40, "size_unit": "ml",
         "pack_count": 1, "status": "active",
         "selling_points": ["oil control", "invisible"],
         "ingredients": ["silica", "homosalate"]},
    ]

    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # --- Price Books ---
    # Live version (APAC Q2 2026 – current)
    live_entries = [
        {"sku_id": "LS-HS-001", "price": 30.0},
        {"sku_id": "LS-HS-002", "price": 32.0},
        {"sku_id": "AP-HS-001", "price": 35.0},
        {"sku_id": "AP-HS-002", "price": 150.0},   # 异常高 (>1.5 * 类平均)
        {"sku_id": "DV-HS-001", "price": 28.0},
        {"sku_id": "DV-HS-002", "price": 5.0},     # 异常低 (<0.5 * 类平均)
        {"sku_id": "LS-UV-001", "price": 40.0},
        {"sku_id": "AP-UV-001", "price": 42.0},
        {"sku_id": "DV-UV-001", "price": 38.0},
    ]

    # Archived version (Q1 2026 – not current) – 干扰
    archived_entries = [
        {"sku_id": "LS-HS-001", "price": 28.0},
        {"sku_id": "LS-HS-002", "price": 30.0},
        {"sku_id": "AP-HS-001", "price": 33.0},
        {"sku_id": "DV-HS-001", "price": 26.0},
        {"sku_id": "LS-UV-001", "price": 39.0},
        {"sku_id": "AP-UV-001", "price": 40.0},
    ]

    price_books = [
        {
            "price_book_id": "APAC-Q1-2026-ARCHIVE",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": archived_entries
        },
        {
            "price_book_id": "APAC-Q2-2026-LIVE",
            "version": "APAC-Q2-2026-LIVE",
            "region": "APAC",
            "status": "approved",
            "is_current": True,
            "effective_from": "2026-04-01",
            "entries": live_entries
        }
    ]

    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # --- Attachments (干扰) ---
    attachments = [
        {
            "path": "category_review_template.md",
            "title": "Category Review Template",
            "kind": "report_template",
            "description": "Markdown template for category competitive analysis"
        },
        {
            "path": "current_pricebook_notice.md",
            "title": "Current Price Book Notice",
            "kind": "pricing_notice",
            "description": "Internal memo about Q2 pricebook deployment"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

if __name__ == "__main__":
    build_env()
