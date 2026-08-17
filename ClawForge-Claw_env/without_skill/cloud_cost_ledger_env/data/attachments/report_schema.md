# Monthly Cost Report Schema

The cached monthly report must include:

- `catalog_id`, `catalog_version`, `billing_month`, and `currency`
- `cluster_ids` and `cluster_count`
- one cluster row per business cluster with:
  - `cluster_id`
  - `cluster_name`
  - `business_service`
  - `usage`
  - `monthly_cost_breakdown`
  - `monthly_compute_cost`
  - `monthly_storage_cost`
  - `monthly_cost_total`
- overall `totals`
- overall `cost_totals`
- a `summary` block naming the highest-cost cluster
