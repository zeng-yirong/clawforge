import os
import json
import random

def build_env():
    # Ensure directories exist
    for d in ["data/resources", "data/pricing", "attachments", "output"]:
        os.makedirs(d, exist_ok=True)

    # ----- Clusters -----
    clusters = [
        {"cluster_id": "cl_ads_01", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference", "domain": "marketing", "environment": "prod", "region": "us-east-1", "owner_team": "Growth Engineering", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["ads", "ml"]},
        {"cluster_id": "cl_lake_02", "cluster_name": "lakehouse-analytics", "business_service": "Lakehouse analytics and finance marts", "domain": "data", "environment": "prod", "region": "us-east-1", "owner_team": "Data Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["analytics", "data"]},
        {"cluster_id": "cl_shared_03", "cluster_name": "shared-ops", "business_service": "Shared CI and platform tooling", "domain": "infrastructure", "environment": "prod", "region": "us-east-1", "owner_team": "Cloud Foundations", "cluster_role": "shared_platform", "service_tier": "tier_2", "workload_tags": ["ci", "platform"]},
    ]
    with open("data/resources/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f)

    # ----- Pricing catalogs -----
    # active June catalog
    active_rates = [
        {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.05},
        {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.02},
        {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.80},
        {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.10},
        {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.03}
    ]
    active_catalog = {
        "catalog_id": "cat_2026_06_live",
        "version": "2026.06-live",
        "status": "active",
        "region": "us-east-1",
        "currency": "USD",
        "billing_month": "2026-06",
        "billing_hours": 720,
        "approved_for_reporting": True,
        "effective_from": "2026-06-01",
        "effective_to": "2026-06-30",
        "rates": active_rates
    }

    # archived March catalog (with different prices – decoy)
    archived_rates = [
        {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.04},
        {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.015},
        {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.70},
        {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.08},
        {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.025}
    ]
    archived_catalog = {
        "catalog_id": "cat_2026_03_archive",
        "version": "2026.03-archive",
        "status": "archived",
        "region": "us-east-1",
        "currency": "USD",
        "billing_month": "2026-03",
        "billing_hours": 744,
        "approved_for_reporting": False,
        "effective_from": "2026-03-01",
        "effective_to": "2026-03-31",
        "rates": archived_rates
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": [active_catalog, archived_catalog]}, f)

    # ----- Resource ledger (with deliberate noise) -----
    # Correct entries for ads-ranking
    ledger_entries = [
        {"entry_id": "e001", "cluster_id": "cl_ads_01", "cluster_name": "ads-ranking", "resource_name": "ml-node-1", "resource_family": "compute", "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e002", "cluster_id": "cl_ads_01", "cluster_name": "ads-ranking", "resource_name": "ml-node-1", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 256, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e003", "cluster_id": "cl_ads_01", "cluster_name": "ads-ranking", "resource_name": "gpu-node-a", "resource_family": "compute", "metric_code": "gpu", "quantity": 4, "unit": "gpu", "billing_model": "monthly"},
        {"entry_id": "e004", "cluster_id": "cl_ads_01", "cluster_name": "ads-ranking", "resource_name": "storage-pool", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e005", "cluster_id": "cl_ads_01", "cluster_name": "ads-ranking", "resource_name": "object-store-bucket", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
        # --- Noise entries ---
        # zero quantity (should be excluded)
        {"entry_id": "e006", "cluster_id": "cl_ads_01", "cluster_name": "ads-ranking", "resource_name": "orphan-vm", "resource_family": "compute", "metric_code": "vcpu", "quantity": 0, "unit": "vcpu", "billing_model": "monthly"},
        # invalid metric_code "storage_gb" (not in standard list)
        {"entry_id": "e007", "cluster_id": "cl_ads_01", "cluster_name": "ads-ranking", "resource_name": "bak-storage", "resource_family": "storage", "metric_code": "storage_gb", "quantity": 100, "unit": "GiB", "billing_model": "monthly"},
        # entry for a different cluster
        {"entry_id": "e008", "cluster_id": "cl_lake_02", "cluster_name": "lakehouse-analytics", "resource_name": "analytics-node", "resource_family": "compute", "metric_code": "vcpu", "quantity": 50, "unit": "vcpu", "billing_model": "monthly"},
        # negative quantity (nonsense)
        {"entry_id": "e009", "cluster_id": "cl_ads_01", "cluster_name": "ads-ranking", "resource_name": "ghost-vm", "resource_family": "compute", "metric_code": "memory_gb", "quantity": -10, "unit": "GiB", "billing_model": "monthly"},
    ]
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": ledger_entries}, f)

    # ----- Attachments -----
    cost_rules_content = """# Cloud Cost Accounting Rules

## Approved metric codes (only these are billable)
- vcpu
- memory_gb
- gpu
- block_storage_gb
- object_storage_gb

## Calculation
For each (cluster, billing_month) pair:
1. Filter resource_ledger entries that belong to the target cluster.
2. Exclude entries with non‑zero negative or zero quantity.
3. Exclude entries whose metric_code is not in the approved list above.
4. Load the **active** pricing catalog for the billing month (status = "active").
5. For each remaining entry, find the matching rate by `metric_code` in the catalog's `rates` list.
6. Compute entry_cost = quantity * unit_price.
7. Total cost = sum(entry_cost).
"""
    with open("attachments/cost_accounting_rules.md", "w") as f:
        f.write(cost_rules_content)

    report_schema_content = """# Monthly Cost Report Schema

The report must be a JSON file with the following fields at the top level:
- `cluster_name` (string)
- `billing_month` (string, format YYYY-MM)
- `currency` (string, e.g. "USD")
- `catalog_id` (string, the active catalog used)
- `total_cost` (float, total cost in currency units)
- `details` (list of objects, each with `metric_code`, `quantity`, `unit_price`, `entry_cost`)

Example:
{
  "cluster_name": "example",
  "billing_month": "2026-06",
  "currency": "USD",
  "catalog_id": "cat_2026_06_live",
  "total_cost": 123.45,
  "details": [
    {"metric_code": "vcpu", "quantity": 10, "unit_price": 0.05, "entry_cost": 0.50}
  ]
}
"""
    with open("attachments/report_schema.md", "w") as f:
        f.write(report_schema_content)

    # ----- Decoy / irrelevant files -----
    with open("data/backup/clusters_old.json", "w") as f:
        f.write('{"clusters": []}')
    with open("data/unrelated.csv", "w") as f:
        f.write("name,value\njunk,0")

if __name__ == "__main__":
    build_env()
