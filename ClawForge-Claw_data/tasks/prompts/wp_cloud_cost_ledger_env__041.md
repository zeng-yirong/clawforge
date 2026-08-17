Hey,

Our June cost report for **ads-ranking** got mangled again — someone fed it the archived March pricing. The cluster cost shot up by 15% and Leah is breathing down my neck.

I've dumped everything into the workspace: the latest resource ledger under `data/resources/`, the current and old pricing catalogs in `data/pricing/`, and the cluster definitions in `data/resources/clusters.json`. The approved pricing catalog for June is live (status: active), you'll recognize it by the billing month.

Please recalculate the June cost for the **ads-ranking** cluster only. Break it down into compute (vcpu + memory_gb) and storage (block_storage_gb). Use the rates from the active catalog. Drop the result as a JSON file at `reports/ads_june_cost.json` with these fields: `cluster`, `month`, `compute_cost`, `storage_cost`, `total_cost`, `currency`.

You know the drill — ignore everything that isn't ads-ranking, and don't touch the archived rates. Make it clean, no extra fields.

Thanks,
Daniel
