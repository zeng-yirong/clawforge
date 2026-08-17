> **From:** Finance Ops <ops@fin-analytics.local>
> **To:** Data Support Desk
> **Subject:** Q4 2024 metric summary – urgent

Hey team,

The CFO is breathing down our necks for the Q4 2024 consolidated metrics report. I’ve pulled together the raw ledger dumps into `data/ledgers/` – three CSV files for customer, product, and operations. Unfortunately, the upstream ETL had a few hiccups: some rows are malformed, and I suspect a duplicate import sneaked in (you’ll know it when you see identical rows). Also there’s a bunch of older period data we don’t care about right now.

We need a clean, single Markdown document that gives a bird’s-eye view of **only Q4 2024** metrics. Please:

- Read every CSV file inside `data/ledgers/`.
- Skip any row that is broken (missing fields, wrong format).
- If you see two rows that are exactly the same (same period, metric code, value), count it only once – no double counting.
- Only keep rows where the period is `2024-Q4`.
- For each distinct metric code that appears in the filtered data, calculate the **total** value across all ledgers (some metric codes might appear in multiple files – just sum them). If a code appears only once, that single value is its total.
- Build a summary table in Markdown with columns: `Metric Code` and `Total Value`. At the bottom of the table, add a **Grand Total** row that sums all the totals.
- Write the final report to `reports/quarterly_review.md`.

Make sure the report is clean and professional – the CFO will read it directly. Name it exactly as above. Thanks!

– Ana (Finance Ops)
