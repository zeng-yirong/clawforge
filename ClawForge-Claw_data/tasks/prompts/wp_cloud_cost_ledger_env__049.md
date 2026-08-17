Hey there,

Daniel Song here – Cloud FinOps Lead. I need your help with the June 2026 cost run. The last person used an archived pricing catalog and almost sent a bogus report to the CFO. Let’s not repeat that.

All the raw data lives in the `data/` directory:
- Cluster definitions are in `data/resources/clusters.json`
- Usage records are in `data/resources/resource_ledger.json`
- Pricing catalogs are under `data/pricing/pricing_catalogs.json` (there are a few versions – make sure to pick the one that’s *active* and *approved for reporting* for billing month 2026-06).

I only care about **business** clusters (not shared platform ones). For each business cluster, I want:
- Total compute cost (sum of all `vcpu`, `memory_gb`, and `gpu` usage, priced with the correct unit rates)
- Total storage cost (sum of all `block_storage_gb` and `object_storage_gb` usage, also with the correct rates)

Please aggregate by cluster and write the result as a JSON file to `ops/cost_report_june_2026.json`. The JSON should be a list of objects, each containing the cluster name, compute cost, storage cost, and total cost (compute + storage). Use two decimal places for all costs.

I’ll double-check the numbers, so be as precise as those hidden old reports in `ops/` will never fool me again. Thanks!

— Daniel
