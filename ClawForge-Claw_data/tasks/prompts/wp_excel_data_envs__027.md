Subject: Urgent: Clean & analyze sales data before quarterly review

Hey,

We're drowning in messy sales records. I've dropped everything into the `data_sources/` folder – there's the latest raw dump, but also some old backups and last year's data mixed in. You'll need to figure out which file is the real one.

Our `city_region.csv` has the mapping you'll need. Please:

1. Clean the mess: drop any duplicate transactions (same transaction_id should appear only once).
2. Fill in the missing "region" column using the city-to-region mapping.
3. For each product *in each region*, calculate the average order amount. Then save the results as a single JSON file at `report/avg_by_product_region.json`. Each entry should have `product_id`, `product_name`, `region`, and `avg_order_amount` (rounded to two decimal places).

We'll use this to decide regional marketing pushes. Don't waste time on extra files – just that JSON.

Thanks,
Sarah (Sales Ops)
