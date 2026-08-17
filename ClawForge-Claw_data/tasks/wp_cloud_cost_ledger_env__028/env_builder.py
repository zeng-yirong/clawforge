import json
import os
import random

random.seed(42)

def build_env():
    # --- clusters.json (3 business + 1 shared_platform) ---
    clusters = [
        {
            "cluster_id": "c_ads_01",
            "cluster_name": "ads-ranking",
            "business_service": "Ads ranking and campaign inference",
            "domain": "marketing",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Growth Engineering",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["ads", "ml"]
        },
        {
            "cluster_id": "c_retail_02",
            "cluster_name": "retail-core",
            "business_service": "Storefront and order orchestration",
            "domain": "commerce",
            "environment": "production",
            "region": "eu-west-1",
            "owner_team": "Commerce Platform",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["storefront", "orders"]
        },
        {
            "cluster_id": "c_lake_03",
            "cluster_name": "lakehouse-analytics",
            "business_service": "Lakehouse analytics and finance marts",
            "domain": "data",
            "environment": "production",
            "region": "us-west-2",
            "owner_team": "Data Platform",
            "cluster_role": "shared_platform",  # not business
            "service_tier": "tier_2",
            "workload_tags": ["analytics", "finance"]
        },
        {
            "cluster_id": "c_shared_04",
            "cluster_name": "shared-ops",
            "business_service": "Shared CI and platform tooling",
            "domain": "infrastructure",
            "environment": "production",
            "region": "ap-southeast-1",
            "owner_team": "Cloud Foundations",
            "cluster_role": "shared_platform",
            "service_tier": "tier_2",
            "workload_tags": ["ci", "tools"]
        }
    ]
    os.makedirs("data/resources", exist_ok=True)
    with open("data/resources/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # --- pricing_catalogs.json (two catalogs: March archived, June live) ---
    pricing_catalogs = [
        {
            "catalog_id": "pc_2026_03_archived",
            "version": "2026.03-archive",
            "status": "archived",
            "region": "global",
            "currency": "USD",
            "billing_month": "2026-03",
            "billing_hours": 744,
            "approved_for_reporting": False,
            "effective_from": "2026-03-01",
            "effective_to": "2026-03-31",
            "rates": [
                {"metric_code": "vcpu", "unit_price": 0.042},
                {"metric_code": "memory_gb", "unit_price": 0.008},
                {"metric_code": "block_storage_gb", "unit_price": 0.10},
                {"metric_code": "object_storage_gb", "unit_price": 0.023},
                {"metric_code": "gpu", "unit_price": 1.2}
            ]
        },
        {
            "catalog_id": "pc_2026_06_live",
            "version": "2026.06-live",
            "status": "active",
            "region": "global",
            "currency": "USD",
            "billing_month": "2026-06",
            "billing_hours": 720,
            "approved_for_reporting": True,
            "effective_from": "2026-06-01",
            "effective_to": "2026-06-30",
            "rates": [
                {"metric_code": "vcpu", "unit_price": 0.045},
                {"metric_code": "memory_gb", "unit_price": 0.009},
                {"metric_code": "block_storage_gb", "unit_price": 0.12},
                {"metric_code": "object_storage_gb", "unit_price": 0.025},
                {"metric_code": "gpu", "unit_price": 1.5}
            ]
        }
    ]
    os.makedirs("data/pricing", exist_ok=True)
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": pricing_catalogs}, f, indent=2)

    # --- resource_ledger.json ---
    # business clusters: ads_01 and retail_02
    # shared clusters: lake_03, shared_04 (should be ignored)
    # include some valid entries, some with negative quantity, some missing fields
    ledger = [
        # ads-ranking valid
        {"entry_id": "e001", "cluster_id": "c_ads_01", "cluster_name": "ads-ranking", "resource_name": "ml-node-1",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e002", "cluster_id": "c_ads_01", "cluster_name": "ads-ranking", "resource_name": "ml-node-1",
         "resource_family": "compute", "metric_code": "memory_gb", "quantity": 480, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "e003", "cluster_id": "c_ads_01", "cluster_name": "ads-ranking", "resource_name": "storage-pool-1",
         "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
        # ads-ranking with negative quantity (should be excluded)
        {"entry_id": "e004", "cluster_id": "c_ads_01", "cluster_name": "ads-ranking", "resource_name": "temp-volume",
         "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": -500, "unit": "GiB", "billing_model": "monthly"},
        # ads-ranking missing metric_code (should be excluded)
        {"entry_id": "e005", "cluster_id": "c_ads_01", "cluster_name": "ads-ranking", "resource_name": "orphan",
         "resource_family": "compute", "metric_code": None, "quantity": 10, "unit": "vcpu", "billing_model": "autoscale"},
        # retail-core valid
        {"entry_id": "e006", "cluster_id": "c_retail_02", "cluster_name": "retail-core", "resource_name": "web-1",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 64, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e007", "cluster_id": "c_retail_02", "cluster_name": "retail-core", "resource_name": "web-1",
         "resource_family": "compute", "metric_code": "memory_gb", "quantity": 256, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e008", "cluster_id": "c_retail_02", "cluster_name": "retail-core", "resource_name": "db-store",
         "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 500, "unit": "GiB", "billing_model": "reserved"},
        # lakehouse (shared_platform) – should be ignored
        {"entry_id": "e009", "cluster_id": "c_lake_03", "cluster_name": "lakehouse-analytics", "resource_name": "etl-1",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 200, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e010", "cluster_id": "c_lake_03", "cluster_name": "lakehouse-analytics", "resource_name": "etl-1",
         "resource_family": "compute", "metric_code": "memory_gb", "quantity": 800, "unit": "GiB", "billing_model": "reserved"},
        # shared-ops (shared_platform) – should be ignored
        {"entry_id": "e011", "cluster_id": "c_shared_04", "cluster_name": "shared-ops", "resource_name": "runner-1",
         "resource_family": "compute", "metric_code": "vcpu", "quantity": 32, "unit": "vcpu", "billing_model": "autoscale"},
        # extra rogue entry with cluster_id that doesn't exist (should be excluded)
        {"entry_id": "e012", "cluster_id": "c_ghost_99", "cluster_name": "ghost", "resource_name": "unknown",
         "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 1000, "unit": "GiB", "billing_model": "monthly"},
        # entry with missing resource_family (should be excluded)
        {"entry_id": "e013", "cluster_id": "c_ads_01", "cluster_name": "ads-ranking", "resource_name": "weird",
         "resource_family": None, "metric_code": "gpu", "quantity": 2, "unit": "gpu", "billing_model": "monthly"},
    ]
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": ledger}, f, indent=2)

    # --- attachments.json (dummy, not needed for correctness) ---
    os.makedirs("data/attachments", exist_ok=True)
    attachments = [
        {"path": "cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules", "kind": "accounting_policy",
         "description": "Standard rules for cost allocation"},
        {"path": "report_schema.md", "title": "Monthly Cost Report Schema", "kind": "report_schema",
         "description": "Schema for the monthly cost report output"}
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # create dummy attachment files
    for att in attachments:
        with open(f"data/attachments/{att['path']}", "w") as f:
            f.write("# " + att["title"] + "\n\nPlaceholder content.\n")

    # --- create an empty ops dir for output (agent will create if needed) ---
    os.makedirs("ops", exist_ok=True)

    # --- some distracting old reports ---
    os.makedirs("old_reports", exist_ok=True)
    with open("old_reports/march_report.json", "w") as f:
        json.dump({"cluster": "ads-ranking", "total_cost": 123.45}, f)

if __name__ == "__main__":
    build_env()
