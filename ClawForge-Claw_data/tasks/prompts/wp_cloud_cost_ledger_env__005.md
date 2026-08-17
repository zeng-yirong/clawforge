Subject: [URGENT] Cost report correction for ads-ranking – please recalculate

Hi DataBot,

We just discovered that last month’s cost report for the **ads-ranking** cluster used the wrong pricing catalog – someone pulled the archived March 2026 rates instead of the live June one. This was caught during the monthly FinOps review and the CFO is asking for a corrected version by end of day.

I’ve prepped the workspace with the raw resource ledger (`data/resources/resource_ledger.json`) and the latest pricing catalogs (`data/pricing/pricing_catalogs.json`). There’s also a spec in `data/attachments/report_schema.md` that tells you exactly what format the output should follow.

Here’s what I need from you:
1. Find the **correct, currently active and approved pricing catalog** – ignore anything that’s archived or not marked for reporting.
2. Use it to calculate the **total monthly cost** for the **ads-ranking** cluster. The ledger contains entries for multiple clusters, and there might be some bad rows (missing fields, zero/negative quantities) – please clean them out before calculating. Only entries that belong to ads-ranking and have all required fields with a positive quantity should count.
3. Write the result as a JSON file to `ops/cost_summary.json` following the `report_schema.md` specification.

Make sure the currency matches the catalog, and the breakdown lists each resource family (compute / storage) with its cost. I need the final file to be accurate – a single wrong number will break the quarterly audit.

Let me know if you hit any snags.

– Daniel Song, Cloud FinOps Lead
