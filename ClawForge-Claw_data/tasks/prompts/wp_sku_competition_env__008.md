From: Jonas Li (Merchandising Ops)
To: AI Assistant
Subject: Urgent – DermVeil UV Moisturizer competitor summary needed

Hi,

We’re prepping for the APAC Q2 category review and need a quick competitor snapshot on DermVeil’s UV Moisturizer line. I’ve dropped the latest product catalog dumps into the `data/` folder – you’ll find everything under `data/brands/`, `data/skus/`, and `data/pricing/`.

Here’s what I need:
- Focus **only** on the **DermVeil** brand
- Narrow down to the **UV Moisturizer** category
- Use the **current (live) price book** – the archived one is stale and will mess up our numbers
- For each SKU in that intersection, grab its ID, name, and unit price
- Then calculate the average price across those SKUs
- Package everything into a clean JSON file: `ops/competition_summary.json`
- The file should contain the brand name, category name, total SKU count, average price, and the full list of SKU details

We need this ASAP to finalise the pricing strategy for next quarter. Please make sure the numbers are accurate – if you pick the wrong price book, we’ll have to redo the whole report.

Thanks,
Jonas
