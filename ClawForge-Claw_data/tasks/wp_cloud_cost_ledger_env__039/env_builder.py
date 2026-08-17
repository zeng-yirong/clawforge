import os
import json


def build_env():
    # Ensure directories exist
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # ---------- clusters ----------
    clusters = {
        "clusters": [
            {
                "cluster_id": "cluster_ads",
                "cluster_name": "ads-ranking",
                "business_service": "Ads ranking and campaign inference",
                "domain": "marketing",
                "environment": "prod",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["ml-inference", "ads"]
            },
            {
                "cluster_id": "cluster_retail",
                "cluster_name": "retail-core",
                "business_service": "Storefront and order orchestration",
                "domain": "commerce",
                "environment": "prod",
                "region": "eu-west-1",
                "owner_team": "Commerce Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["web", "checkout"]
            },
            {
                "cluster_id": "cluster_shared",
                "cluster_name": "shared-ops",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "environment": "prod",
                "region": "us-west-2",
                "owner_team": "Cloud Foundations",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["ci", "monitoring"]
            }
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # ---------- pricing catalogs ----------
    pricing_catalogs = {
        "pricing_catalogs": [
            {
                "catalog_id": "catalog_2026_03",
                "version": "2026.03-archive",
                "status": "archived",
                "region": "us-east-1",
                "currency": "USD",
                "billing_month": "2026-03",
                "billing_hours": 1,
                "approved_for_reporting": False,
                "effective_from": "2026-03-01",
                "effective_to": "2026-03-31",
                "rates": [
                    {"resource_family": "compute", "metric": "vcpu", "unit": "vcpu", "rate_per_unit": 0.15},
                    {"resource_family": "compute", "metric": "memory_gb", "unit": "GiB", "rate_per_unit": 0.08},
                    {"resource_family": "storage", "metric": "block_storage_gb", "unit": "GiB", "rate_per_unit": 0.02},
                    {"resource_family": "storage", "metric": "object_storage_gb", "unit": "GiB", "rate_per_unit": 0.01}
                ]
            },
            {
                "catalog_id": "catalog_2026_06",
                "version": "2026.06-live",
                "status": "active",
                "region": "us-east-1",
                "currency": "USD",
                "billing_month": "2026-06",
                "billing_hours": 1,
                "approved_for_reporting": True,
                "effective_from": "2026-06-01",
                "effective_to": "2026-06-30",
                "rates": [
                    {"resource_family": "compute", "metric": "vcpu", "unit": "vcpu", "rate_per_unit": 0.10},
                    {"resource_family": "compute", "metric": "memory_gb", "unit": "GiB", "rate_per_unit": 0.05},
                    {"resource_family": "storage", "metric": "block_storage_gb", "unit": "GiB", "rate_per_unit": 0.01},
                    {"resource_family": "storage", "metric": "object_storage_gb", "unit": "GiB", "rate_per_unit": 0.005}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # ---------- resource ledger ----------
    resource_ledger = {
        "resource_ledger": [
            # ads-ranking – business
            {"entry_id": "entry_001", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking",
             "resource_name": "ads-inference-vcpus", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 10, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "entry_002", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking",
             "resource_name": "ads-model-memory", "resource_family": "compute", "metric_code": "memory_gb",
             "quantity": 20, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "entry_003", "cluster_id": "cluster_ads", "cluster_name": "ads-ranking",
             "resource_name": "ads-block-store", "resource_family": "storage", "metric_code": "block_storage_gb",
             "quantity": 100, "unit": "GiB", "billing_model": "monthly"},
            # retail-core – business
            {"entry_id": "entry_004", "cluster_id": "cluster_retail", "cluster_name": "retail-core",
             "resource_name": "retail-web-vcpus", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 8, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "entry_005", "cluster_id": "cluster_retail", "cluster_name": "retail-core",
             "resource_name": "retail-web-memory", "resource_family": "compute", "metric_code": "memory_gb",
             "quantity": 16, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "entry_006", "cluster_id": "cluster_retail", "cluster_name": "retail-core",
             "resource_name": "retail-db-storage", "resource_family": "storage", "metric_code": "block_storage_gb",
             "quantity": 200, "unit": "GiB", "billing_model": "monthly"},
            # shared-ops – shared_platform (should be ignored)
            {"entry_id": "entry_007", "cluster_id": "cluster_shared", "cluster_name": "shared-ops",
             "resource_name": "monitoring-vcpus", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 5, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "entry_008", "cluster_id": "cluster_shared", "cluster_name": "shared-ops",
             "resource_name": "monitoring-memory", "resource_family": "compute", "metric_code": "memory_gb",
             "quantity": 8, "unit": "GiB", "billing_model": "monthly"},
            # orphan entry with no matching cluster (distractor)
            {"entry_id": "entry_009", "cluster_id": "cluster_phantom", "cluster_name": "phantom-ops",
             "resource_name": "ghost-storage", "resource_family": "storage", "metric_code": "object_storage_gb",
             "quantity": 9999, "unit": "GiB", "billing_model": "monthly"}
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # ---------- dummy attachments (not used but present for realism) ----------
    attachments = {
        "attachments": [
            {"path": "data/attachments/cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules",
             "kind": "accounting_policy", "description": "Rules for attributing costs to business units"},
            {"path": "data/attachments/report_schema.md", "title": "Monthly Cost Report Schema",
             "kind": "report_schema", "description": "JSON schema for monthly cost reports"}
        ]
    }
    with open("data/attachments/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # ---------- contacts ----------
    contacts = {
        "contacts": [
            {"contact_id": "daniel_song", "name": "Daniel Song", "role": "Cloud FinOps Lead",
             "email": "daniel.song@northstar.example.com"},
            {"contact_id": "leah_kumar", "name": "Leah Kumar", "role": "Cloud Operations Manager",
             "email": "leah.kumar@northstar.example.com"},
            {"contact_id": "tara_ng", "name": "Tara Ng", "role": "Data Platform Director",
             "email": "tara.ng@northstar.example.com"}
        ]
    }
    with open("data/contacts/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ---------- accounts ----------
    accounts = {
        "accounts": [
            {"account_id": "acct_ads", "display_name": "Ads Platform", "department": "Engineering",
             "email": "ads-team@northstar.example.com", "permissions": ["billing_admin"],
             "default_region": "us-east-1", "voice": []},
            {"account_id": "acct_retail", "display_name": "Retail Platform", "department": "Commerce",
             "email": "retail-team@northstar.example.com", "permissions": ["billing_viewer"],
             "default_region": "eu-west-1", "voice": []}
        ]
    }
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)


if __name__ == "__main__":
    build_env()
