**Subject:** Urgent: LuminaSkin Hydration Serum pricing snapshot needed

Hi there,

The APAC pricing team just dropped the Q2 2026 price book – it's live now. Our merchandising lead Alina needs a clean, consolidated picture of **LuminaSkin**'s **Hydration Serum** category so she can finalize shelf talks for next month's promo.

I've dumped the raw data into the `data/` directory:
- Brand master: `data/brands/brands.json`
- SKU catalog: `data/skus/skus.json`
- Price books: `data/pricing/price_books.json`
- There's also a template hint in `data/attachments/` if you need a reference format.

**What I need you to produce:**

Only pull SKUs that belong to **LuminaSkin** AND fall under the **Hydration Serum** category. Use the **current approved price book** (the one that's actually in effect for APAC right now) to grab each SKU's current selling price. For each qualifying SKU, also include its main selling points as listed in the SKU catalog.

Please gather everything into a single JSON file at `output/competitor_price_report.json`. The file should contain a report title (something like "LuminaSkin Hydration Serum Price Competition") and an array of SKU objects with their ID, name, current price, and selling points.

**Important:**
- Ignore any backup or archive versions of the data (there are some stale copies lying around).
- Make sure you only use the price book that is **approved** and **marked as current**.
- No other brands or categories – focus strictly on LuminaSkin / Hydration Serum.

I need this ready within 10 minutes. Thanks!

– Mira
