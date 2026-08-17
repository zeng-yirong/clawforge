import os
import json

def build_env():
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # clusters.json – defines business vs shared platform
    clusters = {
        "clusters": [
            {
                "cluster_id": "ads-ranking",
                "cluster_name": "ads-ranking",
                "cluster_role": "business",
                "business_service": "Ads ranking and campaign inference",
                "domain": "marketing",
                "environment": "prod",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "service_tier": "tier_1"
            },
            {
                "cluster_id": "retail-core",
                "cluster_name": "retail-core",
                "cluster_role": "business",
                "business_service": "Storefront and order orchestration",
                "domain": "commerce",
                "environment": "prod",
                "region": "us-east-1",
                "owner_team": "Commerce Platform",
                "service_tier": "tier_1"
            },
            {
                "cluster_id": "lakehouse-analytics",
                "cluster_name": "lakehouse-analytics",
                "cluster_role": "business",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "environment": "prod",
                "region": "us-west-2",
                "owner_team": "Data Platform",
                "service_tier": "tier_2"
            },
            {
                "cluster_id": "shared-ops",
                "cluster_name": "shared-ops",
                "cluster_role": "shared_platform",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "environment": "prod",
                "region": "us-east-1",
                "owner_team": "Cloud Foundations",
                "service_tier": "tier_2"
            }
        ]
    }
    with open("data/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # pricing_catalogs.json – one archived, one active
    pricing = {
        "pricing_catalogs": [
            {
                "catalog_id": "catalog-archive-2026-03",
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
                    {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.08},
                    {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.04}
                ]
            },
            {
                "catalog_id": "catalog-live-2026-06",
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
                    {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.10},
                    {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.05},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.02},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.01}
                ]
            }
        ]
    }
    with open("data/pricing_catalogs.json", "w") as f:
        json.dump(pricing, f, indent=2)

    # resource_ledger.json – includes valid entries, shared‑ops (distractor),
    # and dirty data (zero / negative quantities)
    ledger_entries = [
        # ads-ranking (business)
        {"entry_id": "e001", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_family": "compute", "metric_code": "vcpu", "quantity": 40, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e002", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 256, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e003", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
        # retail-core (business)
        {"entry_id": "e004", "cluster_id": "retail-core", "cluster_name": "retail-core", "resource_family": "compute", "metric_code": "vcpu", "quantity": 80, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e005", "cluster_id": "retail-core", "cluster_name": "retail-core", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 512, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e006", "cluster_id": "retail-core", "cluster_name": "retail-core", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
        # lakehouse-analytics (business)
        {"entry_id": "e007", "cluster_id": "lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_family": "compute", "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "reserved"},
        {"entry_id": "e008", "cluster_id": "lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 768, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e009", "cluster_id": "lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 3000, "unit": "GiB", "billing_model": "monthly"},
        {"entry_id": "e010", "cluster_id": "lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 5000, "unit": "GiB", "billing_model": "monthly"},
        # shared-ops (shared_platform – distractor, should NOT be included)
        {"entry_id": "e011", "cluster_id": "shared-ops", "cluster_name": "shared-ops", "resource_family": "compute", "metric_code": "vcpu", "quantity": 10, "unit": "vcpu", "billing_model": "monthly"},
        {"entry_id": "e012", "cluster_id": "shared-ops", "cluster_name": "shared-ops", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 100, "unit": "GiB", "billing_model": "monthly"},
        # dirty data – zero quantity
        {"entry_id": "e013", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_family": "compute", "metric_code": "vcpu", "quantity": 0, "unit": "vcpu", "billing_model": "monthly"},
        # dirty data – negative quantity
        {"entry_id": "e014", "cluster_id": "retail-core", "cluster_name": "retail-core", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": -5, "unit": "GiB", "billing_model": "monthly"},
    ]
    ledger = {"resource_ledger": ledger_entries}
    with open("data/resource_ledger.json", "w") as f:
        json.dump(ledger, f, indent=2)

if __name__ == "__main__":
    build_env()
