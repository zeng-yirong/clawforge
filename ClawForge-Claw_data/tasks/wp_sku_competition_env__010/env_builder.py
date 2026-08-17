import json, os, random

random.seed(20260401)

def build_env():
    # --- SKU master ---
    brands = {
        "LuminaSkin": {"brand_id": "b-001", "hero_category": "Hydration Serum"},
        "DermVeil":   {"brand_id": "b-002", "hero_category": "UV Moisturizer"},
        "AquaPulse":  {"brand_id": "b-003", "hero_category": "Hydration Serum"},
    }

    # LuminaSkin SKUs (5 total)
    lumina_skus = [
        {"sku_id": "LSK-001", "sku_name": "Glow Revival Serum",  "size_value": 30, "size_unit": "ml", "category_name": "Hydration Serum"},
        {"sku_id": "LSK-002", "sku_name": "Bright Dew Drops",    "size_value": 50, "size_unit": "ml", "category_name": "Hydration Serum"},
        {"sku_id": "LSK-003", "sku_name": "Radiance Boost Oil",  "size_value": 15, "size_unit": "ml", "category_name": "Hydration Serum"},
        {"sku_id": "LSK-004", "sku_name": "Hydra Lock Gel",      "size_value": 40, "size_unit": "ml", "category_name": "Hydration Serum"},
        {"sku_id": "LSK-005", "sku_name": "Night Renew Complex", "size_value": 30, "size_unit": "ml", "category_name": "Hydration Serum"},
    ]
    # DermVeil SKUs (distraction)
    derm_skus = [
        {"sku_id": "DVK-010", "sku_name": "Shield SPF 50",     "size_value": 50, "size_unit": "ml", "category_name": "UV Moisturizer"},
        {"sku_id": "DVK-011", "sku_name": "Matte Finish SPF30", "size_value": 40, "size_unit": "ml", "category_name": "UV Moisturizer"},
    ]
    # AquaPulse SKUs (distraction)
    aqua_skus = [
        {"sku_id": "APK-100", "sku_name": "Sea Mineral Mist",   "size_value": 100, "size_unit": "ml", "category_name": "Hydration Serum"},
    ]

    all_skus = []
    for s in lumina_skus:
        entry = {"brand_id": "b-001", "brand_name": "LuminaSkin", **s}
        entry["status"] = "active"
        entry["selling_points"] = ["hydrating", "brightening"]
        entry["ingredients"] = ["hyaluronic acid", "vitamin C"]
        all_skus.append(entry)
    for s in derm_skus:
        entry = {"brand_id": "b-002", "brand_name": "DermVeil", **s}
        entry["status"] = "active"
        entry["selling_points"] = ["sun protection", "lightweight"]
        entry["ingredients"] = ["zinc oxide", "aloe vera"]
        all_skus.append(entry)
    for s in aqua_skus:
        entry = {"brand_id": "b-003", "brand_name": "AquaPulse", **s}
        entry["status"] = "active"
        entry["selling_points"] = ["mineral-rich", "refreshing"]
        entry["ingredients"] = ["sea water", "kelp extract"]
        all_skus.append(entry)

    os.makedirs("data/skus", exist_ok=True)
    with open("data/skus/skus.json", "w") as f:
        json.dump({"wrapper": "skus", "data": all_skus}, f, indent=2)

    # --- Price books ---
    # Two versions: archived (Q1) and live (Q2)
    # LuminaSkin prices: archive vs live
    # Live has 4 out of 5 LuminaSkin SKUs, plus one ghost entry (sku not in master)
    # Archive has all 5 but different prices
    # Also includes DermVeil and AquaPulse entries (distractors)
    price_entries_archive = []
    price_entries_live = []

    # Archive prices (old)
    for sku in lumina_skus:
        price_entries_archive.append({
            "sku_id": sku["sku_id"],
            "unit_price": round(random.uniform(20.0, 80.0), 2),
            "currency": "USD"
        })
    # plus some other brand entries in archive (distractor)
    for sku in derm_skus:
        price_entries_archive.append({
            "sku_id": sku["sku_id"],
            "unit_price": round(random.uniform(15.0, 50.0), 2),
            "currency": "USD"
        })

    # Live prices (new) – only 4 LuminaSkin, missing LSK-005, plus extra brand & ghost
    live_sku_list = [s for s in lumina_skus if s["sku_id"] != "LSK-005"]  # 4
    for sku in live_sku_list:
        price_entries_live.append({
            "sku_id": sku["sku_id"],
            "unit_price": round(random.uniform(22.0, 95.0), 2),
            "currency": "USD"
        })
    # DermVeil entries in live (distractor)
    for sku in derm_skus:
        price_entries_live.append({
            "sku_id": sku["sku_id"],
            "unit_price": round(random.uniform(18.0, 55.0), 2),
            "currency": "USD"
        })
    # ghost entry – sku_id that does not exist in master
    price_entries_live.append({
        "sku_id": "FAKE-999",
        "unit_price": 999.99,
        "currency": "USD"
    })

    # Fixed seed so we know exact prices for verification
    # We'll compute what prices the live LuminaSkin entries got from random with seed 20260401
    # Let's precompute to have exact numbers in verifier (but verifier will read from file anyway)
    # Actually builder just writes them; verifier will load and compare against the written data.
    # So we don't need to hardcode numbers in verifier; we can re-read from built files.

    archive_book = {
        "price_book_id": "PB-ARC-001",
        "version": "APAC-Q1-2026-ARCHIVE",
        "region": "APAC",
        "status": "archived",
        "is_current": False,
        "effective_from": "2026-01-01",
        "entries": price_entries_archive
    }
    live_book = {
        "price_book_id": "PB-LIVE-002",
        "version": "APAC-Q2-2026-LIVE",
        "region": "APAC",
        "status": "approved",
        "is_current": True,
        "effective_from": "2026-04-01",
        "entries": price_entries_live
    }

    os.makedirs("ops/pricing", exist_ok=True)
    with open("ops/pricing/price_books.json", "w") as f:
        json.dump({"wrapper": "price_books", "data": [archive_book, live_book]}, f, indent=2)

    # --- Other distraction files (brands, attachments, contacts) ---
    os.makedirs("data/brands", exist_ok=True)
    brand_list = [
        {"brand_id": "b-001", "brand_name": "LuminaSkin", "hero_category_id": "HC01", "hero_category_name": "Hydration Serum", "positioning": "premium", "region_focus": "APAC", "price_tier": "premium"},
        {"brand_id": "b-002", "brand_name": "DermVeil",   "hero_category_id": "HC02", "hero_category_name": "UV Moisturizer", "positioning": "clinical", "region_focus": "APAC", "price_tier": "mid-premium"},
        {"brand_id": "b-003", "brand_name": "AquaPulse",  "hero_category_id": "HC03", "hero_category_name": "Hydration Serum", "positioning": "natural", "region_focus": "APAC", "price_tier": "mid"},
    ]
    with open("data/brands/brands.json", "w") as f:
        json.dump({"wrapper": "brands", "data": brand_list}, f, indent=2)

    os.makedirs("data/attachments", exist_ok=True)
    attachments = [
        {"path": "category_review_template.md", "title": "Category Review Template", "kind": "report_template", "description": "Standard template for competitive category analysis"},
        {"path": "current_pricebook_notice.md", "title": "Current Price Book Notice", "kind": "pricing_notice", "description": "Notice regarding the live Q2 price book"}
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"wrapper": "attachments", "data": attachments}, f, indent=2)

    os.makedirs("data/contacts", exist_ok=True)
    contacts = [
        {"contact_id": "c001", "name": "Alina Bose", "role": "Category Director", "email": "alina.bose@northstar.example.com"},
        {"contact_id": "c002", "name": "Jonas Li", "role": "Merchandising Ops", "email": "jonas.li@northstar.example.com"},
        {"contact_id": "c003", "name": "Mira Tan", "role": "Pricing Operations Lead", "email": "mira.tan@northstar.example.com"},
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"wrapper": "contacts", "data": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
