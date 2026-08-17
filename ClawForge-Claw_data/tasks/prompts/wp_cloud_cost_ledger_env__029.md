Hey there,

Hope you're having a better week than I am. I just got chewed out by the VP because our May cost report was off by nearly $2k — turns out the pricing catalog we used was archived and stale. We cannot let that happen again.

For June, I need it right. Head into the workspace and dig through the data. I've dumped everything into the `data/` directory:

- Resource ledgers and cluster definitions are under `data/resources/`.
- Pricing catalogs live under `data/pricing/`.
- There's a schema file for the report format in `data/attachments/report_schema.md` — please follow it exactly.

Please generate a clean cost report for **June 2026**, saved as **`reports/2026-06-cost-report.json`**.  
Only include our **business clusters**—that's `ads-ranking`, `lakehouse-analytics`, and `retail-core`. The shared platform cluster (`shared-ops`) belongs to a different budget and should be left out.  

Also, use the **live pricing catalog** (the one approved for reporting) — don't pick the archived one.  
Be careful: the ledger might contain stale or duplicate entries. Apply good judgment to get the real usage numbers.

I need the report on my desk by lunch. Make it accurate this time.

— Daniel
