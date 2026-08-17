import os
import json

def build_env():
    # Create directories
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty output directory

    # ---- brands.json ----
    brands = [
        {"brand_id":"solar_oat","brand_name":"SolarOat","hero_category_id":"cat_01","hero_category_name":"UV Moisturizer","positioning":"Natural sun care","region_focus":"APAC","price_tier":"mid"},
        {"brand_id":"lumina_skin","brand_name":"LuminaSkin","hero_category_id":"cat_01","hero_category_name":"UV Moisturizer","positioning":"Premium","region_focus":"APAC","price_tier":"premium"},
        {"brand_id":"derm_veil","brand_name":"DermVeil","hero_category_id":"cat_01","hero_category_name":"UV Moisturizer","positioning":"Derm-approved","region_focus":"Global","price_tier":"premium"},
        {"brand_id":"aqua_pulse","brand_name":"AquaPulse","hero_category_id":"cat_02","hero_category_name":"Hydration Serum","positioning":"Hydration","region_focus":"APAC","price_tier":"mid-premium"}
    ]
    with open("db_dumps/brands.json","w") as f:
        json.dump(brands, f, indent=2)

    # ---- skus.json ----
    skus = [
        {"sku_id":"SO-1001","brand_id":"solar_oat","brand_name":"SolarOat","category_id":"cat_01","category_name":"UV Moisturizer","sku_name":"Daily SPF 50","size_value":50,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Natural","Water-resistant"],"ingredients":["Zinc Oxide","Aloe Vera"]},
        {"sku_id":"LS-2001","brand_id":"lumina_skin","brand_name":"LuminaSkin","category_id":"cat_01","category_name":"UV Moisturizer","sku_name":"Luminous Shield SPF 50","size_value":50,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Brightening","Anti-pollution"],"ingredients":["Niacinamide","Vitamin C"]},
        {"sku_id":"DV-3001","brand_id":"derm_veil","brand_name":"DermVeil","category_id":"cat_01","category_name":"UV Moisturizer","sku_name":"DermaDefense SPF 50","size_value":40,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Sensitive skin","Hypoallergenic"],"ingredients":["Ceramides","Panthenol"]},
        # Distractor: same brand, different category
        {"sku_id":"SO-2002","brand_id":"solar_oat","brand_name":"SolarOat","category_id":"cat_02","category_name":"Hydration Serum","sku_name":"Hydra Boost Serum","size_value":30,"size_unit":"ml","pack_count":1,"status":"active","selling_points":["Hydrating","Lightweight"],"ingredients":["Hyaluronic Acid","Glycerin"]},
        # Distractor: discontinued SKU
        {"sku_id":"LS-2002","brand_id":"lumina_skin","brand_name":"LuminaSkin","category_id":"cat_01","category_name":"UV Moisturizer","sku_name":"Old Formula SPF 30","size_value":50,"size_unit":"ml","pack_count":1,"status":"discontinued","selling_points":["Old"],"ingredients":["Oxybenzone"]}
    ]
    with open("db_dumps/skus.json","w") as f:
        json.dump(skus, f, indent=2)

    # ---- price_books.json ----
    price_books = [
        {
            "price_book_id":"pb_001",
            "version":"APAC-Q2-2026-LIVE",
            "region":"APAC",
            "status":"approved",
            "is_current":True,
            "effective_from":"2026-04-01",
            "entries": [
                {"sku_id":"SO-1001","price":24.80,"currency":"USD"},
                {"sku_id":"LS-2001","price":29.90,"currency":"USD"},
                {"sku_id":"DV-3001","price":32.00,"currency":"USD"},
                {"sku_id":"SO-2002","price":18.50,"currency":"USD"},
                # Dirty data: missing sku_id
                {"price":0,"currency":"USD"}
            ]
        },
        {
            "price_book_id":"pb_002",
            "version":"APAC-Q1-2026-ARCHIVE",
            "region":"APAC",
            "status":"archived",
            "is_current":False,
            "effective_from":"2026-01-01",
            "entries": [
                {"sku_id":"SO-1001","price":22.50,"currency":"USD"},
                {"sku_id":"LS-2001","price":27.50,"currency":"USD"},
                {"sku_id":"DV-3001","price":30.00,"currency":"USD"},
                {"sku_id":"SO-2002","price":17.00,"currency":"USD"}
            ]
        }
    ]
    with open("db_dumps/price_books.json","w") as f:
        json.dump(price_books, f, indent=2)

    # ---- contacts.json (distractor, not needed) ----
    contacts = [
        {"contact_id":"c001","name":"Alina Bose","role":"Category Director","email":"alina.bose@northstar.example.com"},
        {"contact_id":"c002","name":"Jonas Li","role":"Merchandising Ops","email":"jonas.li@northstar.example.com"},
        {"contact_id":"c003","name":"Mira Tan","role":"Pricing Operations Lead","email":"mira.tan@northstar.example.com"}
    ]
    with open("db_dumps/contacts.json","w") as f:
        json.dump(contacts, f, indent=2)

    # ---- README distractor ----
    with open("db_dumps/README.md","w") as f:
        f.write("# Database Dumps\nThese files are snapshots from the product catalog.\n")

if __name__ == "__main__":
    build_env()
