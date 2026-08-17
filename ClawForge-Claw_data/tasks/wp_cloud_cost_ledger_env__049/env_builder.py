import os
import json
import random

def build_env():
    # Base directories
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- accounts (dummy data) ---
    accounts = {
        "accounts": [
            {"account_id": "acct-001", "display_name": "Engineering", "department": "Engineering", "email": "eng@northstar.example.com", "permissions": ["admin"], "default_region": "us-east-1", "voice": []},
            {"account_id": "acct-002", "display_name": "Finance", "department": "Finance", "email": "fin@northstar.example.com", "permissions": ["read"], "default_region": "us-west-2", "voice": []}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- contacts ---
    contacts = {
        "contacts": [
            {"contact_id": "c-daniel", "name": "Daniel Song", "role": "Cloud FinOps Lead", "email": "daniel.song@northstar.example.com"},
            {"contact_id": "c-leah", "name": "Leah Kumar", "role": "Cloud Operations Manager", "email": "leah.kumar@northstar.example.com"},
            {"contact_id": "c-tara", "name": "Tara Ng", "role": "Data Platform Director", "email": "tara.ng@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- attachments (distraction) ---
    attachments = {
        "attachments": [
            {"path": "cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules", "kind": "accounting_policy", "description": "Internal policy on cost allocation"},
            {"path": "report_schema.md", "title": "Monthly Cost Report Schema", "kind": "report_schema", "description": "Schema for the final report JSON"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # --- clusters ---
    clusters = {
        "clusters": [
            {"cluster_id": "c-ads", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference", "domain": "marketing", "environment": "production", "region": "us-east-1", "owner_team": "Growth Engineering", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["ads", "real-time"]},
            {"cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "business_service": "Lakehouse analytics and finance marts", "domain": "data", "environment": "production", "region": "us-west-2", "owner_team": "Data Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["analytics", "batch"]},
            {"cluster_id": "c-retail", "cluster_name": "retail-core", "business_service": "Storefront and order orchestration", "domain": "commerce", "environment": "production", "region": "eu-west-1", "owner_team": "Commerce Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["ecommerce", "core"]},
            {"cluster_id": "c-shared", "cluster_name": "shared-ops", "business_service": "Shared CI and platform tooling", "domain": "infrastructure", "environment": "production", "region": "us-east-1", "owner_team": "Cloud Foundations", "cluster_role": "shared_platform", "service_tier": "tier_2", "workload_tags": ["ci", "platform"]}
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # --- resource ledger (with distraction entries) ---
    ledger = {
        "resource_ledger": [
            # ads-ranking (business)
            {"entry_id": "e-ads-1", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "worker-pool-a", "resource_family": "compute", "metric_code": "vcpu", "quantity": 100, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "e-ads-2", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "worker-pool-a", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 200, "unit": "GiB", "billing_model": "reserved"},
            {"entry_id": "e-ads-3", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "model-store", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
            # lakehouse-analytics (business)
            {"entry_id": "e-lake-1", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "compute-nodes", "resource_family": "compute", "metric_code": "vcpu", "quantity": 50, "unit": "vcpu", "billing_model": "autoscale"},
            {"entry_id": "e-lake-2", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "compute-nodes", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 100, "unit": "GiB", "billing_model": "autoscale"},
            {"entry_id": "e-lake-3", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "data-lake", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 1000, "unit": "GiB", "billing_model": "monthly"},
            # retail-core (business)
            {"entry_id": "e-retail-1", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "app-servers", "resource_family": "compute", "metric_code": "vcpu", "quantity": 80, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "e-retail-2", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "app-servers", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 160, "unit": "GiB", "billing_model": "reserved"},
            {"entry_id": "e-retail-3", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "db-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 200, "unit": "GiB", "billing_model": "monthly"},
            # shared-ops (shared_platform – should be ignored)
            {"entry_id": "e-shared-1", "cluster_id": "c-shared", "cluster_name": "shared-ops", "resource_name": "ci-runners", "resource_family": "compute", "metric_code": "vcpu", "quantity": 20, "unit": "vcpu", "billing_model": "autoscale"},
            {"entry_id": "e-shared-2", "cluster_id": "c-shared", "cluster_name": "shared-ops", "resource_name": "ci-runners", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 40, "unit": "GiB", "billing_model": "autoscale"},
            # extra irrelevant entry with bogus metric (distraction)
            {"entry_id": "e-orphan", "cluster_id": "c-nonexistent", "cluster_name": "ghost-cluster", "resource_name": "unknown", "resource_family": "compute", "metric_code": "gpu", "quantity": 5, "unit": "gpu", "billing_model": "reserved"}
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(ledger, f, indent=2)

    # --- pricing catalogs (two versions) ---
    pricing_catalogs = {
        "pricing_catalogs": [
            {
                "catalog_id": "cat-2026-03",
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
                    {"metric_code": "vcpu", "unit_price": 0.04},
                    {"metric_code": "memory_gb", "unit_price": 0.015},
                    {"metric_code": "block_storage_gb", "unit_price": 0.08},
                    {"metric_code": "object_storage_gb", "unit_price": 0.02},
                    {"metric_code": "gpu", "unit_price": 1.2}
                ]
            },
            {
                "catalog_id": "cat-2026-06",
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
                    {"metric_code": "vcpu", "unit_price": 0.06},
                    {"metric_code": "memory_gb", "unit_price": 0.02},
                    {"metric_code": "block_storage_gb", "unit_price": 0.12},
                    {"metric_code": "object_storage_gb", "unit_price": 0.03},
                    {"metric_code": "gpu", "unit_price": 2.0}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # --- distraction: old report in ops/ ---
    old_report = [
        {"cluster": "ads-ranking", "compute": 8.0, "storage": 45.0, "total": 53.0}
    ]
    with open("ops/previous_report.json", "w") as f:
        json.dump(old_report, f, indent=2)

    # --- distraction: markdown attachments (not needed but harmless) ---
    with open("data/cost_accounting_rules.md", "w") as f:
        f.write("# Cloud Cost Accounting Rules\n\n...")
    with open("data/report_schema.md", "w") as f:
        f.write("# Report Schema\n\n...")

if __name__ == "__main__":
    build_env()
