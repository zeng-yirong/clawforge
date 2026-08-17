Hey, quick one from FinOps. We just got the raw cloud ledger dump for June 2026, and I need the exact total monthly cost for our **retail-core** cluster – the one powering the storefront and order orchestration.

You'll find the resource usage records in `data/resources/resource_ledger.json` – it's got entries for all clusters, but I only care about retail-core. The approved pricing catalog for June is in `data/pricing/pricing_catalogs.json`; make sure you use the one that's actually **active** and matches the billing month.

I don't have time to hunt down stale versions or irrelevant clusters. Just give me a clear, single JSON file at `cost_report.json` with:

- the cluster ID
- the billing month
- the catalog you used
- the final total cost (USD, two decimals)

That's it – no fluff, no extra files. I need this before the monthly review call. Thanks.
