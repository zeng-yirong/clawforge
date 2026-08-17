Subject: Urgent – Sales Data Cleanup Needed

Hi Data Analyst,

We've got a mess in our sales records. I've put two files in the workspace:  
- `sales_raw.csv` – all transactions but full of duplicates and missing product names.  
- `product_reference.csv` – maps product IDs to names and categories.

Could you please clean up the raw data? Remove exact duplicate rows (where all fields match exactly).  
For any missing product name, look up the ID in the reference file and fill it in.  

Then I need a monthly category sales summary – group by year‑month and category, sum the `sales_amount`.  
Save that as `sales_summary.csv`.  

Also calculate the average order value (total sales ÷ total number of unique order IDs) and save just the number in `average_order.txt`.  

I need these before the board meeting tomorrow. Thanks!

Best,  
Sales Manager
