Hi there,

I'm Alice from the Operations team. We're preparing the quarterly business snapshot for the leadership board. I've pulled the latest ledgers from our three divisions – customer, product, and ops – and dumped them into the `ledgers/` folder under the working directory. Each file is a CSV with columns: period, metric_code, metric_value.

Could you please generate a concise Markdown report for **2024 Q1** (period code "2024-Q1")? I need the total aggregated metric values for each division. The report should be saved as `reports/business_report.md` with the following structure:

- A heading "# Business Report"
- A line "**Period**: <period>"
- Three lines for the totals: "**Total Customer Metrics**: <sum>", "**Total Product Metrics**: <sum>", "**Total Ops Metrics**: <sum>"

Please make sure you only consider rows where period is exactly "2024-Q1" – the other periods are just noise from previous quarters. Also, ignore any non-CSV files you might find; they're unrelated.

Thanks a ton! Let me know if anything looks off.

Best,
Alice
