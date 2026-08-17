Hey team — it’s Mira from Pricing Ops.

We just pushed the APAC Q2 2026 pricebook (`data/pricing/price_books.json`) live, and I’ve got a bad feeling about a few line items. Some prices just don’t look right when you compare them to other SKUs in the same product category. You can find the category info for each SKU in `data/skus/skus.json`.

Could you dig through both files, figure out which SKUs have truly off‑the‑wall prices relative to their own category, and dump the results into `ops/price_outliers.json`? For each outlier I need the SKU ID, its current price, the category name, the average price for that category, and whether it’s significantly above or below the pack.

There’s also a pricing adjustment template in `data/attachments.json` in case we need it later — but the outlier list is what I need first.

Thanks.
Mira
