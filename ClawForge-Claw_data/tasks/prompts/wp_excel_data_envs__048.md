Hi there,

I'm Clark, the Sales Director. We've been having headaches with our quarterly sales report - turns out the raw data has been contaminated with duplicate transactions and some entries with negative or missing amounts. Could you please take a look at the latest dump I put in `data/raw_data/sales_raw.csv`? There's also an old backup in `data/old_sales_backup.csv` but ignore that - it's outdated.

I need a clean summary by product category. Specifically:

- Remove any rows that are exact duplicates (same transaction_id appearing more than once - keep the first occurrence).
- Drop rows where sales_amount is empty or negative.
- Then, for each category, calculate the total sales amount and the average order amount (total sales divided by number of orders in that category).

Save the result as a JSON file at `reports/summary.json`. In the JSON, put a list called `category_summary`, each item should have fields: `category`, `total_sales`, and `average_order`. Round the numbers to two decimal places.

Thanks, and let me know if you have any questions!

Clark
