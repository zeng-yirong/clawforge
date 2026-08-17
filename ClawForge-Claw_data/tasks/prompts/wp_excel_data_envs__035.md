Subject: Urgent: Sales Data Cleanup Needed

Hey team,

Our Q1 sales report is due, and the raw data in `data/raw_data/sales_raw.csv` is a disaster! There are duplicate entries everywhere — I've spotted at least a few identical rows. Can you clean it up? Remove all exact duplicate rows so we have unique records.

After that, I need a quick analysis: for each product category, calculate the average sales amount. Round each average to two decimal places. Save the result as a JSON file at `ops/average_sales.json`, with categories as keys and averages as values.

Ignore the `data/old_sales.csv` file — that's historical data from last year and not needed.

Please get this done ASAP. Thanks!

- Boss
