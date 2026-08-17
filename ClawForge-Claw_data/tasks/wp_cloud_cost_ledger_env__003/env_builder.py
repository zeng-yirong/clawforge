import os
import json

def build_env():
    # Ensure required directories exist
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # --- clusters.json (only two relevant clusters, others as noise) ---
    clusters = {
        "clusters": [
            {
                "cluster_id": "cluster_001",
                "cluster_name": "ads-ranking",
                "business_service": "Ads ranking and campaign inference",
                "domain": "marketing",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["ml-inference", "real-time"]
            },
            {
                "cluster_id": "cluster_002",
                "cluster_name": "lakehouse-analytics",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "environment": "production",
                "region": "us-west-2",
                "owner_team": "Data Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["etl", "analytics"]
            },
            {
                "cluster_id": "cluster_003",
                "cluster_name": "shared-ops",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "environment": "production",
                "region": "eu-central-1",
                "owner_team": "Cloud Foundations",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["ci", "monitoring"]
            }
        ]
    }
    with open("data/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # --- resource_ledger.json (mix of valid entries for ads-ranking and noise) ---
    # Valid ads-ranking entries:
    # compute: vcpu 8, memory_gb 16
    # storage: block_storage_gb 200
    # + one extra vcpu entry that is invalid (negative quantity -> should be ignored)
    # + one entry for lakehouse-analytics (noise)
    # + one entry with missing cluster_id (noise)
    resource_ledger = {
        "resource_ledger": [
            {
                "entry_id": "entry_001",
                "cluster_id": "cluster_001",
                "cluster_name": "ads-ranking",
                "resource_name": "cpu-instance-001",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 8,
                "unit": "vcpu",
                "billing_model": "reserved"
            },
            {
                "entry_id": "entry_002",
                "cluster_id": "cluster_001",
                "cluster_name": "ads-ranking",
                "resource_name": "mem-instance-001",
                "resource_family": "compute",
                "metric_code": "memory_gb",
                "quantity": 16,
                "unit": "GiB",
                "billing_model": "reserved"
            },
            {
                "entry_id": "entry_003",
                "cluster_id": "cluster_001",
                "cluster_name": "ads-ranking",
                "resource_name": "storage-vol-001",
                "resource_family": "storage",
                "metric_code": "block_storage_gb",
                "quantity": 200,
                "unit": "GiB",
                "billing_model": "monthly"
            },
            # Invalid: negative quantity (should be filtered out)
            {
                "entry_id": "entry_004",
                "cluster_id": "cluster_001",
                "cluster_name": "ads-ranking",
                "resource_name": "faulty-cpu",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": -2,
                "unit": "vcpu",
                "billing_model": "reserved"
            },
            # Noise: different cluster
            {
                "entry_id": "entry_005",
                "cluster_id": "cluster_002",
                "cluster_name": "lakehouse-analytics",
                "resource_name": "analytics-cpu",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 32,
                "unit": "vcpu",
                "billing_model": "autoscale"
            },
            # Noise: missing cluster_id (should also be ignored since no cluster match)
            {
                "entry_id": "entry_006",
                "cluster_name": "orphan-resource",
                "resource_family": "storage",
                "metric_code": "object_storage_gb",
                "quantity": 500,
                "unit": "GiB",
                "billing_model": "monthly"
            }
        ]
    }
    with open("data/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # --- pricing_catalogs.json (one active June catalog, one archived March catalog) ---
    pricing_catalogs = {
        "pricing_catalogs": [
            {
                "catalog_id": "catalog_june_2026",
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
                    {
                        "resource_family": "compute",
                        "metric_code": "vcpu",
                        "unit_price": 0.05
                    },
                    {
                        "resource_family": "compute",
                        "metric_code": "memory_gb",
                        "unit_price": 0.02
                    },
                    {
                        "resource_family": "storage",
                        "metric_code": "block_storage_gb",
                        "unit_price": 0.10
                    }
                ]
            },
            {
                "catalog_id": "catalog_march_2026",
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
                    {
                        "resource_family": "compute",
                        "metric_code": "vcpu",
                        "unit_price": 0.06
                    },
                    {
                        "resource_family": "compute",
                        "metric_code": "memory_gb",
                        "unit_price": 0.025
                    },
                    {
                        "resource_family": "storage",
                        "metric_code": "block_storage_gb",
                        "unit_price": 0.12
                    }
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # --- Additional noise files (irrelevant to task) ---
    # accounts.json (not needed)
    accounts = {
        "accounts": [
            {"account_id": "acc_001", "display_name": "Growth", "department": "Engineering", "email": "growth@northstar.example.com", "permissions": ["admin"], "default_region": "us-east-1", "voice": []},
            {"account_id": "acc_002", "display_name": "Data", "department": "Data", "email": "data@northstar.example.com", "permissions": ["read"], "default_region": "us-west-2", "voice": []}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # backup/old_ledger.json (outdated, should not be used)
    old_ledger = {"resource_ledger": [{"entry_id": "old_001", "cluster_id": "cluster_001", "cluster_name": "ads-ranking", "resource_family": "compute", "metric_code": "vcpu", "quantity": 999, "unit": "vcpu", "billing_model": "reserved"}]}
    with open("backup/old_ledger.json", "w") as f:
        json.dump(old_ledger, f, indent=2)

    # ops/ directory exists so agent can place report (empty initially)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
