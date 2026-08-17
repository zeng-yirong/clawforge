**From:** Daniel Song <daniel.song@northstar.example.com>  
**To:** SRE / Data Ops  
**Subject:** 💸 Ads‑ranking June cost report – urgent redo

Hey team,

The finance board meeting is in 3 hours, and I just caught that last month’s cost report for our **ads‑ranking** cluster used the old March pricing catalog. We need the **June 2026** version, and it has to be accurate this time.

I’ve dumped everything into the `data/` and `pricing/` folders in our shared workspace:

- Cluster definitions are in `data/resources/clusters.json`
- Raw resource usage ledger is in `data/resources/resource_ledger.json`
- The two pricing catalogs are in `data/pricing/pricing_catalogs.json` – pick the one that’s actually **approved for June**.
- There’s also a couple of stale files in `data/reports/` – ignore those, they’re from last quarter.

What I need:

1. A clean cost breakdown for **ads‑ranking** only (not the other clusters – they’re handled separately).
2. Use the **June 2026** pricing rates. Compute and storage costs should be itemized separately.
3. The result should go into an `ops/` folder as a single JSON file named `cluster_cost_report.json`.

Please be careful – I noticed some of the raw ledger entries look suspicious (e.g., zero quantities, negative values). I trust you to filter those out. Just give me the real numbers.

Thanks,  
Daniel

P.S. – The report structure should be self‑explanatory: cluster name, month, total cost, and a breakdown per resource family.
