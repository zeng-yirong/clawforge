Subject: Urgent: Q1 Quarterly Review — Need Aggregated Metrics Report

Hi,

The quarterly review board is tomorrow morning, and I’m drowning in messy ledgers. The ops team dumped a bunch of CSV files into `data/ledgers/` — I can see old backups, temporary exports, and even a few with wrong headers. I need you to cut through the noise.

Please go to `data/ledgers/` and pick out the **current, primary** ledgers for:
- Customer metrics
- Product metrics  
- Operations metrics

Ignore any files with “_old”, “_backup”, “_temp”, or anything that isn’t the standard naming (`customer_ledger.csv`, `product_ledger.csv`, `ops_ledger.csv`). Once you have those three correct files, focus **only on the entries for the 2024 Q1 period**. I need the **grand total** of all `metric_value` fields across those three ledgers.

Write a clean Markdown report in `ops/report.md` that includes:
- A brief header identifying the Q1 2024 aggregation
- A table showing each ledger, metric code, and its value
- A clear **Total** line at the bottom

I need the number nailed down to the integer — no decimals, no rounding. Double-check you’ve included every single row from those three files.

Thanks,
Alex (Operations Director)
