Hey there! I'm Sarah, the regional sales lead. We've got a mess on our hands – I just exported all our 2024 and 2025 transaction logs into `raw_data/`, but the data is a train wreck. There are duplicate rows (some even have different amounts for the same transaction!), missing fields, and a few records that look like test entries (negative prices, obviously bogus dates). I need you to dig through those CSVs, clean up the mess, and give me the hard numbers I need for tomorrow's board meeting.

I've dumped everything into `raw_data/` – there's `orders_2024.csv`, `orders_2025.csv`, and also a backup folder `raw_data/backup/` with an older version that might be garbage. Ignore anything that isn't a valid sales record. I need two key figures:

1. **Total net revenue** – sum of all legitimate `sales_amount` after removing duplicates and bogus entries.
2. **Average order value** – that's total revenue divided by the number of clean, unique transactions.

Please put the final numbers in a simple JSON file at `ops/cleaned_summary.json`. The format should be flat, like:
- `total_revenue`: number (two decimal places)
- `average_order_value`: number (two decimal places)
- `clean_order_count`: integer

I only care about accuracy – don't bother with charts or pivot tables, just the raw cleaned numbers. Oh, and keep the file clean: no extra fields, no commentary. Thanks!
