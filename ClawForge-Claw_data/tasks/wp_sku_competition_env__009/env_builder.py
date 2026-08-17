import os
import json

def build_env():
    # ----- brands -----
    brands = [
        {"brand_id": "LuminaSkin", "brand_name": "LuminaSkin", "hero_category_id": "cat_HS", "hero_category_name": "Hydration Serum", "positioning": "premium", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "AquaPulse", "brand_name": "AquaPulse", "hero_category_id": "cat_HS", "hero_category_name": "Hydration Serum", "positioning": "mid-premium", "region_focus": "APAC", "price_tier": "mid-premium"},
        {"brand_id": "DermVeil", "brand_name": "DermVeil", "hero_category_id": "cat_UV", "hero_category_name": "UV Moisturizer", "positioning": "premium", "region_focus": "EMEA", "price_tier": "premium"},
        {"brand_id": "PureLattice", "brand_name": "PureLattice", "hero_category_id": "cat_HS", "hero_category_name": "Hydration Serum", "positioning": "value", "region_focus": "APAC", "price_tier": "value"},
        {"brand_id": "SolarOat", "brand_name": "SolarOat", "hero_category_id": "cat_UV", "hero_category_name": "UV Moisturizer", "positioning": "mid", "region_focus": "NA", "price_tier": "mid"}
    ]
    os.makedirs("data/brands", exist_ok=True)
    with open("data/brands/brands.json", "w") as f:
        json.dump({"brands": brands}, f, indent=2)

    # ----- skus -----
    skus = [
        # LuminaSkin – Hydration Serum (active)
        {"sku_id": "LS-HS-001", "brand_id": "LuminaSkin", "brand_name": "LuminaSkin", "category_id": "cat_HS", "category_name": "Hydration Serum", "sku_name": "HydraGlow Essence", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["deep hydration", "lightweight"], "ingredients": ["hyaluronic acid", "glycerin"]},
        {"sku_id": "LS-HS-002", "brand_id": "LuminaSkin", "brand_name": "LuminaSkin", "category_id": "cat_HS", "category_name": "Hydration Serum", "sku_name": "Radiance Boost Serum", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["brightening", "firming"], "ingredients": ["vitamin C", "peptides"]},
        # LuminaSkin – Hydration Serum (discontinued)
        {"sku_id": "LS-HS-003", "brand_id": "LuminaSkin", "brand_name": "LuminaSkin", "category_id": "cat_HS", "category_name": "Hydration Serum", "sku_name": "Classic Hydra", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "discontinued", "selling_points": ["classic formula"], "ingredients": ["water", "alcohol"]},
        # LuminaSkin – UV Moisturizer (active, not in target category)
        {"sku_id": "LS-UV-001", "brand_id": "LuminaSkin", "brand_name": "LuminaSkin", "category_id": "cat_UV", "category_name": "UV Moisturizer", "sku_name": "SunShield SPF30", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["SPF30", "water resistant"], "ingredients": ["zinc oxide", "avobenzone"]},
        # AquaPulse – Hydration Serum (active)
        {"sku_id": "AP-HS-001", "brand_id": "AquaPulse", "brand_name": "AquaPulse", "category_id": "cat_HS", "category_name": "Hydration Serum", "sku_name": "AquaCharge Serum", "size_value": 40, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["cooling", "refresh"], "ingredients": ["aloe vera", "sea water"]},
        {"sku_id": "AP-HS-002", "brand_id": "AquaPulse", "brand_name": "AquaPulse", "category_id": "cat_HS", "category_name": "Hydration Serum", "sku_name": "Deepsea Hydrator", "size_value": 60, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["marine collagen", "overnight repair"], "ingredients": ["collagen", "hyaluronic acid"]},
        # AquaPulse – UV Moisturizer (active, not target)
        {"sku_id": "AP-UV-001", "brand_id": "AquaPulse", "brand_name": "AquaPulse", "category_id": "cat_UV", "category_name": "UV Moisturizer", "sku_name": "OceanGuard SPF50", "size_value": 50, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["reef safe", "SPF50"], "ingredients": ["titanium dioxide", "octocrylene"]},
        # DermVeil – Hydration Serum (active, other brand, not requested)
        {"sku_id": "DV-HS-001", "brand_id": "DermVeil", "brand_name": "DermVeil", "category_id": "cat_HS", "category_name": "Hydration Serum", "sku_name": "VeilHydra", "size_value": 30, "size_unit": "ml", "pack_count": 1, "status": "active", "selling_points": ["soothing", "anti-redness"], "ingredients": ["niacinamide", "centella"]},
    ]
    os.makedirs("data/skus", exist_ok=True)
    with open("data/skus/skus.json", "w") as f:
        json.dump({"skus": skus}, f, indent=2)

    # ----- price books -----
    price_books = [
        {
            "price_book_id": "PB-ARCHIVE-2026Q1",
            "version": "APAC-Q1-2026-ARCHIVE",
            "region": "APAC",
            "status": "archived",
            "is_current": False,
            "effective_from": "2026-01-01",
            "entries": [
                {"sku_id": "LS-HS-001", "price": 30.00},
                {"sku_id": "LS-HS-002", "price": 34.00},
                {"sku_id": "LS-HS-003", "price": 35.00},
                {"sku_id": "AP-HS-001", "price": 32.00},
                {"sku_id": "AP-HS-002", "price": 36.00},
                {"sku_id": "DV-HS-001", "price": 28.00}
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
                {"sku_id": "LS-HS-001", "price": 28.50},
                {"sku_id": "LS-HS-002", "price": 32.00},
                {"sku_id": "AP-HS-001", "price": 30.00},
                {"sku_id": "AP-HS-002", "price": 34.00},
                {"sku_id": "DV-HS-001", "price": 27.50}
            ]
        }
    ]
    os.makedirs("data/pricing", exist_ok=True)
    with open("data/pricing/price_books.json", "w") as f:
        json.dump({"price_books": price_books}, f, indent=2)

    # ----- attachments (distractor) -----
    attachments = [
        {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template", "description": "Standard template for monthly category review."},
        {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice", "description": "Notice about APAC-Q2-2026-LIVE price book activation."}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ----- accounts & contacts (distractors) -----
    accounts = [
        {"account_id": "acc-001", "display_name": "Mira Tan", "department": "Pricing", "email": "mira.tan@northstar.example.com", "permissions": ["price_book_write"], "default_region": "APAC", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "cnt-001", "name": "Mira Tan", "role": "Pricing Operations Lead", "email": "mira.tan@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ensure reports directory exists (for agent to place output)
    os.makedirs("reports", exist_ok=True)

if __name__ == "__main__":
    build_env()
