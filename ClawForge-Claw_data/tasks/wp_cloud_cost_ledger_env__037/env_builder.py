import os
import json

def build_env():
    base = "."
    # Make directories
    dirs = [
        "data/resources",
        "data/pricing",
        "data/attachments",
    ]
    for d in dirs:
        os.makedirs(os.path.join(base, d), exist_ok=True)

    # ---- clusters.json ----
    clusters = [
        {
            "cluster_id": "ads-ranking",
            "cluster_name": "ads-ranking",
            "business_service": "Ads ranking and campaign inference",
            "domain": "marketing",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Growth Engineering",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["ads", "inference", "production"]
        },
        {
            "cluster_id": "lakehouse-analytics",
            "cluster_name": "lakehouse-analytics",
            "business_service": "Lakehouse analytics and finance marts",
            "domain": "data",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Data Platform",
            "cluster_role": "business",
            "service_tier": "tier_1",
            "workload_tags": ["analytics", "data"]
        },
        {
            "cluster_id": "retail-core",
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
            "cluster_id": "shared-ops",
            "cluster_name": "shared-ops",
            "business_service": "Shared CI and platform tooling",
            "domain": "infrastructure",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Cloud Foundations",
            "cluster_role": "shared_platform",
            "service_tier": "tier_2",
            "workload_tags": ["ci", "platform"]
        }
    ]
    with open(os.path.join(base, "data/resources/clusters.json"), "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    # ---- resource_ledger.json ----
    ledger = [
        # ads-ranking entries (clean)
        {"entry_id": "ledger-001", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_name": "compute-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 24, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "ledger-002", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_name": "compute-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 128, "unit": "GiB", "billing_model": "reserved"},
        {"entry_id": "ledger-003", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_name": "gpu-node", "resource_family": "compute", "metric_code": "gpu", "quantity": 4, "unit": "gpu", "billing_model": "reserved"},
        {"entry_id": "ledger-004", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_name": "data-store", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 2048, "unit": "GiB", "billing_model": "monthly"},
        # distraction: another cluster
        {"entry_id": "ledger-005", "cluster_id": "shared-ops", "cluster_name": "shared-ops", "resource_name": "ci-builder", "resource_family": "compute", "metric_code": "vcpu", "quantity": 8, "unit": "vcpu", "billing_model": "autoscale"},
        {"entry_id": "ledger-006", "cluster_id": "shared-ops", "cluster_name": "shared-ops", "resource_name": "ci-builder", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 32, "unit": "GiB", "billing_model": "autoscale"},
        # distraction: ads-ranking but old/noise (extra line with zero quantity)
        {"entry_id": "ledger-007", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_name": "scratch-volume", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 0, "unit": "GiB", "billing_model": "monthly"},
        # distraction: unknown cluster
        {"entry_id": "ledger-008", "cluster_id": "retail-core", "cluster_name": "retail-core", "resource_name": "db-store", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 512, "unit": "GiB", "billing_model": "monthly"}
    ]
    with open(os.path.join(base, "data/resources/resource_ledger.json"), "w") as f:
        json.dump({"resource_ledger": ledger}, f, indent=2)

    # ---- pricing_catalogs.json ----
    catalogs = [
        {
            "catalog_id": "cat-2026-03-archive",
            "version": "2026.03-archive",
            "status": "archived",
            "region": "us-east-1",
            "currency": "USD",
            "billing_month": "2026-03",
            "billing_hours": 720,
            "approved_for_reporting": False,
            "effective_from": "2026-03-01",
            "effective_to": "2026-03-31",
            "rates": [
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.08, "currency": "USD"},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.04, "currency": "USD"},
                {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.90, "currency": "USD"},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.08, "currency": "USD"}
            ]
        },
        {
            "catalog_id": "cat-2026-06-live",
            "version": "2026.06-live",
            "status": "active",
            "region": "us-east-1",
            "currency": "USD",
            "billing_month": "2026-06",
            "billing_hours": 720,
            "approved_for_reporting": True,
            "effective_from": "2026-06-01",
            "effective_to": "2026-06-30",
            "rates": [
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.10, "currency": "USD"},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.05, "currency": "USD"},
                {"resource_family": "compute", "metric_code": "gpu", "unit_price": 1.00, "currency": "USD"},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.10, "currency": "USD"}
            ]
        }
    ]
    with open(os.path.join(base, "data/pricing/pricing_catalogs.json"), "w") as f:
        json.dump({"pricing_catalogs": catalogs}, f, indent=2)

    # ---- attachments (distraction) ----
    att = [
        {
            "path": "cost_accounting_rules.md",
            "title": "Cloud Cost Accounting Rules",
            "kind": "accounting_policy",
            "description": "Internal policy for cost allocation (unused for this report)"
        },
        {
            "path": "report_schema.md",
            "title": "Monthly Cost Report Schema",
            "kind": "report_schema",
            "description": "Schema for cost report output (informational)"
        }
    ]
    with open(os.path.join(base, "data/attachments/attachments.json"), "w") as f:
        json.dump({"attachments": att}, f, indent=2)

    # ---- accounts.json (extra distraction) ----
    accounts = [
        {"account_id": "acc-finops", "display_name": "FinOps Admin", "department": "Finance", "email": "cloud.cost@northstar.example.com", "permissions": ["read", "write"], "default_region": "us-east-1", "voice": []}
    ]
    with open(os.path.join(base, "data/accounts.json"), "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
