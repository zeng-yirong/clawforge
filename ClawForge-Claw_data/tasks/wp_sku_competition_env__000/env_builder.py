import os
import json
import datetime

def build_env():
    # Create directory structure
    os.makedirs("data/brands", exist_ok=True)
    os.makedirs("data/skus", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Brands
    brands = {
        "brands": [
            {"brand_id": "B001", "brand_name": "LuminaSkin", "hero_category_id": "C001",
             "hero_category_name": "Hydration Serum", "positioning": "Premium", "region_focus": "APAC", "price_tier": "premium"},
            {"brand_id": "B002", "brand_name": "AquaPulse", "hero_category_id": "C002",
             "hero_category_name": "UV Moisturizer", "positioning": "Mass", "region_focus": "EMEA", "price_tier": "value"},
            {"brand_id": "B003", "brand_name": "DermVeil", "hero_category_id": "C001",
             "hero_category_name": "Hydration Serum", "positioning": "Derm", "region_focus": "APAC", "price_tier": "mid-premium"},
        ]
    }
    with open("data/brands/brands.json", "w") as f:
        json.dump(brands, f, indent=2)

    # SKUs (LuminaSkin Hydration Serum: 3 SKUs; DermVeil Hydration Serum: 2 SKUs; AquaPulse UV Moisturizer: 2 SKUs)
    skus = {
        "skus": [
            # LuminaSkin Hydration Serum
            {"sku_id": "LS-HS-001", "brand_id": "B001", "brand_name": "LuminaSkin", "category_id": "C001",
             "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Boost Serum",
             "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active",
             "selling_points": ["Deep hydration", "Lightweight gel texture", "Vitamin B5 enriched"],
             "ingredients": ["Water", "Glycerin", "Vitamin B5", "Hyaluronic Acid"]},
            {"sku_id": "LS-HS-002", "brand_id": "B001", "brand_name": "LuminaSkin", "category_id": "C001",
             "category_name": "Hydration Serum", "sku_name": "Lumina Night Repair Serum",
             "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active",
             "selling_points": ["Overnight repair", "Brightening effect", "Ceramide complex"],
             "ingredients": ["Squalane", "Niacinamide", "Ceramide NP", "Peptides"]},
            {"sku_id": "LS-HS-003", "brand_id": "B001", "brand_name": "LuminaSkin", "category_id": "C001",
             "category_name": "Hydration Serum", "sku_name": "Lumina Vitamin C Radiance Serum",
             "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active",
             "selling_points": ["Vitamin C brightening", "Antioxidant protection", "Collagen boosting"],
             "ingredients": ["Ascorbic Acid", "Ferulic Acid", "Vitamin E", "Hyaluronic Acid"]},
            # DermVeil Hydration Serum (interference – same category but different brand)
            {"sku_id": "DV-HS-001", "brand_id": "B003", "brand_name": "DermVeil", "category_id": "C001",
             "category_name": "Hydration Serum", "sku_name": "DermVeil Barrier Repair Serum",
             "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active",
             "selling_points": ["Barrier strengthening", "Ceramide rich", "Sensitive skin"],
             "ingredients": ["Ceramide AP", "Panthenol", "Shea Butter"]},
            # AquaPulse UV Moisturizer (different category)
            {"sku_id": "AP-UM-001", "brand_id": "B002", "brand_name": "AquaPulse", "category_id": "C002",
             "category_name": "UV Moisturizer", "sku_name": "AquaPulse SPF50 Daily Moisturizer",
             "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active",
             "selling_points": ["SPF50 protection", "Matte finish", "Oil-free"],
             "ingredients": ["Zinc Oxide", "Titanium Dioxide", "Niacinamide"]},
        ]
    }
    with open("data/skus/skus.json", "w") as f:
        json.dump(skus, f, indent=2)

    # Price books
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
                    {"sku_id": "LS-HS-001", "price": 26.00},
                    {"sku_id": "LS-HS-002", "price": 32.00},
                    {"sku_id": "LS-HS-003", "price": 40.00},
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
                    {"sku_id": "LS-HS-001", "price": 28.50},
                    {"sku_id": "LS-HS-002", "price": 35.00},
                    {"sku_id": "LS-HS-003", "price": 42.00},
                    # Also include a DermVeil SKU price (should be excluded because brand mismatch)
                    {"sku_id": "DV-HS-001", "price": 38.00},
                ]
            },
            {
                "price_book_id": "PB-EMEA-Q1-2026",
                "version": "EMEA-Q1-2026-ARCHIVE",
                "region": "EMEA",
                "status": "archived",
                "is_current": False,
                "effective_from": "2026-01-01",
                "entries": [
                    {"sku_id": "AP-UM-001", "price": 18.00},
                ]
            },
        ]
    }
    with open("data/pricing/price_books.json", "w") as f:
        json.dump(price_books, f, indent=2)

    # Attachments (with a template hint)
    attachments = {
        "attachments": [
            {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template",
             "description": "Template for category price comparison report. Use fields: report_title, skus[].sku_id, sku_name, current_price, selling_points."},
            {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice",
             "description": "Reminder: always use the price book with is_current=true and status=approved."}
        ]
    }
    with open("data/attachments/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # Create a dummy template file for reference (optional)
    template_content = """# Category Review Template
## Report Title
[report_title]

## SKU List
| SKU ID | SKU Name | Current Price | Selling Points |
|--------|----------|---------------|----------------|
| ...    | ...      | ...           | ...            |
"""
    with open("data/attachments/category_review_template.md", "w") as f:
        f.write(template_content)

    # Interference: stale backup of skus (old version with different prices/names)
    stale_skus = {
        "skus": [
            {"sku_id": "LS-HS-001", "brand_id": "B001", "brand_name": "LuminaSkin", "category_id": "C001",
             "category_name": "Hydration Serum", "sku_name": "Lumina Hydra Boost Serum (OLD)",
             "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "discontinued",
             "selling_points": ["Hydrating", "Lightweight"],
             "ingredients": ["Water", "Glycerin"]},
            # ... others
        ]
    }
    with open("data/skus/skus_backup.json", "w") as f:
        json.dump(stale_skus, f, indent=2)

    # Interference: raw logs (irrelevant)
    with open("raw_logs/system.log", "w") as f:
        f.write("2026-04-10 03:12:45 INFO  main thread started\n")
        f.write("2026-04-10 03:13:01 WARN  connection pool exhausted\n")

    # Interference: ops folder with old kill list (different domain)
    with open("ops/old_kill_target.json", "w") as f:
        json.dump({"transaction_id": "TX-9999"}, f, indent=2)

if __name__ == "__main__":
    build_env()
