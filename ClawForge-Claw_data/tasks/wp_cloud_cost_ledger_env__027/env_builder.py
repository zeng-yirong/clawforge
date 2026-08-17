import os
import json
import shutil

def build_env():
    # --- ensure base directories exist ---
    os.makedirs("cost_report", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- 1. accounts.json (decoy) ---
    accounts = {
        "accounts": [
            {"account_id": "acc-01", "display_name": "Infra", "department": "Engineering", "email": "infra@northstar.example.com", "permissions": ["read", "write"], "default_region": "us-east-1", "voice": []},
            {"account_id": "acc-02", "display_name": "Data", "department": "Data Platform", "email": "data@northstar.example.com", "permissions": ["read"], "default_region": "eu-west-1", "voice": []}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- 2. contacts.json (decoy) ---
    contacts = {
        "contacts": [
            {"contact_id": "c-01", "name": "Daniel Song", "role": "Cloud FinOps Lead", "email": "daniel.song@northstar.example.com"},
            {"contact_id": "c-02", "name": "Leah Kumar", "role": "Cloud Operations Manager", "email": "leah.kumar@northstar.example.com"},
            {"contact_id": "c-03", "name": "Tara Ng", "role": "Data Platform Director", "email": "tara.ng@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- 3. attachments.json + actual files (decoy) ---
    attachments = {
        "attachments": [
            {"path": "data/attachments/cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules", "kind": "accounting_policy", "description": "Rules for distributing shared costs"},
            {"path": "data/attachments/report_schema.md", "title": "Monthly Cost Report Schema", "kind": "report_schema", "description": "Expected structure of a cost report"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)
    # actual attachment files (dummy content)
    with open("data/attachments/cost_accounting_rules.md", "w") as f:
        f.write("# Accounting Rules\nOnly active pricing catalogs should be used. Exclude shared platform clusters.\n")
    with open("data/attachments/report_schema.md", "w") as f:
        f.write("# Report Schema\nreport_month, clusters (name, total_cost, details), total_cost\n")

    # --- 4. pricing catalogs ---
    # archived catalog (March 2026)
    archived = {
        "catalog_id": "cat-mar-2026",
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
            {"resource_family": "compute", "metric_code": "vcpu", "unit": "vcpu", "unit_price": 0.03},
            {"resource_family": "compute", "metric_code": "gpu", "unit": "gpu", "unit_price": 0.60}
        ]
    }
    # active catalog (June 2026)
    active = {
        "catalog_id": "cat-jun-2026",
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
            {"resource_family": "compute", "metric_code": "vcpu", "unit": "vcpu", "unit_price": 0.02},
            {"resource_family": "compute", "metric_code": "gpu", "unit": "gpu", "unit_price": 0.50}
        ]
    }
    pricing_catalogs = {
        "pricing_catalogs": [archived, active]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # --- 5. clusters ---
    clusters = {
        "clusters": [
            {
                "cluster_id": "c-ads",
                "cluster_name": "ads-ranking",
                "business_service": "Ads ranking and campaign inference",
                "domain": "commerce",
                "environment": "production",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["ads", "ml"]
            },
            {
                "cluster_id": "c-retail",
                "cluster_name": "retail-core",
                "business_service": "Storefront and order orchestration",
                "domain": "commerce",
                "environment": "production",
                "region": "us-west-2",
                "owner_team": "Commerce Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["storefront", "orders"]
            },
            {
                "cluster_id": "c-lake",
                "cluster_name": "lakehouse-analytics",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "environment": "production",
                "region": "eu-central-1",
                "owner_team": "Data Platform",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["analytics", "finance"]
            },
            {
                "cluster_id": "c-shared",
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
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # --- 6. resource ledger (with decoys and multiple entries) ---
    # We only need business clusters: ads-ranking (c-ads) and retail-core (c-retail)
    # Enteries for these:
    # ads-ranking: vcpu 400+600=1000, gpu 20+30=50
    # retail-core: vcpu 800+1200=2000, gpu 0
    # Decoys: lakehouse-analytics vcpu 500, shared-ops gpu 100, and a storage entry for ads-ranking.
    ledger = {
        "resource_ledger": [
            # --- ads-ranking compute ---
            {"entry_id": "e-001", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ml-vm-1", "resource_family": "compute", "metric_code": "vcpu", "quantity": 400, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "e-002", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "ml-vm-2", "resource_family": "compute", "metric_code": "vcpu", "quantity": 600, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "e-003", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "gpu-node-1", "resource_family": "compute", "metric_code": "gpu", "quantity": 20, "unit": "gpu", "billing_model": "reserved"},
            {"entry_id": "e-004", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "gpu-node-2", "resource_family": "compute", "metric_code": "gpu", "quantity": 30, "unit": "gpu", "billing_model": "reserved"},
            # --- retail-core compute ---
            {"entry_id": "e-005", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "app-srv-1", "resource_family": "compute", "metric_code": "vcpu", "quantity": 800, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "e-006", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "app-srv-2", "resource_family": "compute", "metric_code": "vcpu", "quantity": 1200, "unit": "vcpu", "billing_model": "monthly"},
            # --- decoys: non-business cluster compute ---
            {"entry_id": "e-007", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics", "resource_name": "etl-node", "resource_family": "compute", "metric_code": "vcpu", "quantity": 500, "unit": "vcpu", "billing_model": "autoscale"},
            {"entry_id": "e-008", "cluster_id": "c-shared", "cluster_name": "shared-ops", "resource_name": "ci-gpu-pool", "resource_family": "compute", "metric_code": "gpu", "quantity": 100, "unit": "gpu", "billing_model": "monthly"},
            # --- decoys: storage (not compute) ---
            {"entry_id": "e-009", "cluster_id": "c-ads", "cluster_name": "ads-ranking", "resource_name": "model-store", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 5000, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e-010", "cluster_id": "c-retail", "cluster_name": "retail-core", "resource_name": "db-backup", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "reserved"}
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(ledger, f, indent=2)

    # --- 7. an extra decoy file in ops/ ---
    with open("ops/old_report_2026_03.json", "w") as f:
        json.dump({"month": "2026-03", "total": 123.45}, f)

if __name__ == "__main__":
    build_env()
