Hey, urgent! We need the Q2 cost breakdown by tomorrow. I've dumped the raw resource usage snapshots into `data/resource_ledger.json` and the latest pricing catalog is in `data/pricing_catalogs.json`. The cluster definitions with their roles live in `data/clusters.json`.

We only care about **business clusters** (the ones actually running our revenue‑generating services). Please calculate each one's total cost for June using the **active** pricing catalog (ignore archived ones). Some entries in the ledger might look off – zero or negative quantities – those shouldn't count towards the actual bill.

Save the result as a clean JSON array in `ops/cost_report.json`. Each element should clearly show the cluster id and its total cost. I need it accurate – double‑check your numbers before you drop the file. Thanks!
