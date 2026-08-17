Hey team,

Alice from regional sales here. We've got a bit of a mess with our raw order exports – I've dumped the latest snapshot into `sales_raw.csv` in the workspace. There are duplicates (some rows are exact copies, and some orders appear multiple times with different dates), plus a bunch of missing product names and city-region info.

I've also put two helper files there: `products.csv` has our product catalog with IDs and names, and `city_region.csv` maps cities to regions. Could you please:

- Clean up the raw data: remove all duplicate rows (for orders that appear more than once, keep only the one with the most recent date), fill in any missing product names using the catalog, and fill in missing regions using the city mapping.
- Then, calculate the **average sales amount per region** (just the `sales_amount` column, no discounts or adjustments). Round each average to 2 decimal places.
- Save the result as a JSON dict (region -> average) in `report/regional_avg.json`.
- Also save the cleaned, complete data as `report/clean_sales.csv`.

Only the final two files matter — everything else can be tidied up however you like.

Thanks!
