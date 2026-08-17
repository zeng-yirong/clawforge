import json, os

def build_env():
    # Create required directories
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("pricing", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # --- resource_ledger.json (main data) ---
    entries = [
        {"entry_id": "ENT-001", "cluster_id": "cluster_ads_01", "cluster_name": "ads-ranking",
         "resource_name": "gpu-node-a", "resource_family": "compute", "metric_code": "gpu",
         "quantity": 8, "unit": "gpu", "billing_model": "monthly"},
        {"entry_id": "ENT-002", "cluster_id": "cluster_ads_01", "cluster_name": "ads-ranking",
         "resource_name": "cpu-node-b", "resource_family": "compute", "metric_code": "vcpu",
         "quantity": 64, "unit": "vcpu", "billing_model": "autoscale"},
        {"entry_id": "ENT-003", "cluster_id": "cluster_ads_01", "cluster_name": "ads-ranking",
         "resource_name": "storage-pool-c", "resource_family": "storage", "metric_code": "block_storage_gb",
         "quantity": 5000, "unit": "GiB", "billing_model": "reserved"},
        # intruder – same cluster, different model (should be included)
        {"entry_id": "ENT-005", "cluster_id": "cluster_ads_01", "cluster_name": "ads-ranking",
         "resource_name": "extra-gpu-e", "resource_family": "compute", "metric_code": "gpu",
         "quantity": 2, "unit": "gpu", "billing_model": "autoscale"},
        # intruder – different cluster (must be excluded)
        {"entry_id": "ENT-004", "cluster_id": "cluster_lakehouse_02", "cluster_name": "lakehouse-analytics",
         "resource_name": "data-node-d", "resource_family": "compute", "metric_code": "memory_gb",
         "quantity": 256, "unit": "GiB", "billing_model": "monthly"},
        # additional dirty record – quantity as string (should be int but kept for realism)
        {"entry_id": "ENT-006", "cluster_id": "cluster_ads_01", "cluster_name": "ads-ranking",
         "resource_name": "temp-vol-f", "resource_family": "storage", "metric_code": "object_storage_gb",
         "quantity": 100, "unit": "GiB", "billing_model": "monthly"},
    ]
    with open("db_dumps/resource_ledger.json", "w") as f:
        json.dump(entries, f, indent=2)

    # --- pricing_catalogs.json ---
    catalogs = [
        {"catalog_id": "catalog_2026_03", "version": "2026.03-archive", "status": "archived",
         "region": "us-east-1", "currency": "USD", "billing_month": "2026-03", "billing_hours": 744,
         "approved_for_reporting": True, "effective_from": "2026-03-01", "effective_to": "2026-03-31",
         "rates": [
             {"resource_family": "compute", "metric_code": "gpu", "billing_model": "monthly", "unit_price": 3.50},
             {"resource_family": "compute", "metric_code": "vcpu", "billing_model": "autoscale", "unit_price": 0.10},
             {"resource_family": "storage", "metric_code": "block_storage_gb", "billing_model": "reserved", "unit_price": 0.08},
             {"resource_family": "compute", "metric_code": "gpu", "billing_model": "autoscale", "unit_price": 4.00},
             {"resource_family": "storage", "metric_code": "object_storage_gb", "billing_model": "monthly", "unit_price": 0.02},
         ]},
        {"catalog_id": "catalog_2026_06", "version": "2026.06-live", "status": "active",
         "region": "us-east-1", "currency": "USD", "billing_month": "2026-06", "billing_hours": 720,
         "approved_for_reporting": True, "effective_from": "2026-06-01", "effective_to": "2026-06-30",
         "rates": [
             {"resource_family": "compute", "metric_code": "gpu", "billing_model": "monthly", "unit_price": 3.75},
             {"resource_family": "compute", "metric_code": "vcpu", "billing_model": "autoscale", "unit_price": 0.12},
             {"resource_family": "storage", "metric_code": "block_storage_gb", "billing_model": "reserved", "unit_price": 0.09},
             {"resource_family": "compute", "metric_code": "gpu", "billing_model": "autoscale", "unit_price": 4.25},
             {"resource_family": "storage", "metric_code": "object_storage_gb", "billing_model": "monthly", "unit_price": 0.022},
         ]}
    ]
    with open("pricing/pricing_catalogs.json", "w") as f:
        json.dump(catalogs, f, indent=2)

    # --- decoy / auxiliary files (unrelated to the task) ---
    accounts = [
        {"account_id": "acc-001", "display_name": "NorthStar FinOps", "department": "Finance",
         "email": "finops@northstar.example.com", "permissions": ["admin"], "default_region": "us-east-1", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    contacts = [
        {"contact_id": "c001", "name": "Daniel Song", "role": "Cloud FinOps Lead",
         "email": "daniel.song@northstar.example.com"},
        {"contact_id": "c002", "name": "Leah Kumar", "role": "Cloud Operations Manager",
         "email": "leah.kumar@northstar.example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    attachments = [
        {"path": "cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules",
         "kind": "accounting_policy", "description": "Rules for cost allocation."},
        {"path": "report_schema.md", "title": "Monthly Cost Report Schema",
         "kind": "report_schema", "description": "Schema for monthly report."},
    ]
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f)

    clusters = [
        {"cluster_id": "cluster_ads_01", "cluster_name": "ads-ranking",
         "business_service": "Ads ranking and campaign inference", "domain": "marketing",
         "environment": "prod", "region": "us-east-1", "owner_team": "Growth Engineering",
         "cluster_role": "business", "service_tier": "tier_1",
         "workload_tags": ["ad-serving", "ml-inference"]},
        {"cluster_id": "cluster_lakehouse_02", "cluster_name": "lakehouse-analytics",
         "business_service": "Lakehouse analytics and finance marts", "domain": "data",
         "environment": "prod", "region": "us-east-1", "owner_team": "Data Platform",
         "cluster_role": "business", "service_tier": "tier_1",
         "workload_tags": ["analytics", "etl"]},
    ]
    with open("data/clusters.json", "w") as f:
        json.dump(clusters, f)

if __name__ == "__main__":
    build_env()
