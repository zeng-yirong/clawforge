import json, os

def build_env():
    # Create directory structure
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # accounts.json (minimal, for context)
    accounts = {
        "accounts": [
            {"account_id": "acc-001", "display_name": "Cloud Prod", "department": "Engineering",
             "email": "cloud-prod@northstar.example.com", "permissions": ["admin"], "default_region": "us-east-1", "voice": ["slack"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # attachments.json (irrelevant but present)
    attachments = {
        "attachments": [
            {"path": "cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules", "kind": "accounting_policy",
             "description": "Standard cost allocation rules."},
            {"path": "report_schema.md", "title": "Monthly Cost Report Schema", "kind": "report_schema",
             "description": "Schema for monthly cost reports."}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # contacts.json (needed for email context)
    contacts = {
        "contacts": [
            {"contact_id": "c-daniel", "name": "Daniel Song", "role": "Cloud FinOps Lead",
             "email": "daniel.song@northstar.example.com"},
            {"contact_id": "c-leah", "name": "Leah Kumar", "role": "Cloud Operations Manager",
             "email": "leah.kumar@northstar.example.com"},
            {"contact_id": "c-tara", "name": "Tara Ng", "role": "Data Platform Director",
             "email": "tara.ng@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # clusters.json – includes ads-ranking and shared-ops (distractor)
    clusters = {
        "clusters": [
            {"cluster_id": "c-ads", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference",
             "domain": "marketing", "environment": "production", "region": "us-east-1",
             "owner_team": "Growth Engineering", "cluster_role": "business", "service_tier": "tier_1",
             "workload_tags": ["ml-inference", "ads"]},
            {"cluster_id": "c-shared", "cluster_name": "shared-ops", "business_service": "Shared CI and platform tooling",
             "domain": "infrastructure", "environment": "production", "region": "us-east-1",
             "owner_team": "Cloud Foundations", "cluster_role": "shared_platform", "service_tier": "tier_2",
             "workload_tags": ["ci", "monitoring"]}
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # resource_ledger.json – entries for ads-ranking and shared-ops (distractor)
    resource_ledger = {
        "resource_ledger": [
            {"entry_id": "e-ads-001", "cluster_id": "c-ads", "cluster_name": "ads-ranking",
             "resource_name": "primary compute", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 10, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "e-ads-002", "cluster_id": "c-ads", "cluster_name": "ads-ranking",
             "resource_name": "inference memory", "resource_family": "compute", "metric_code": "memory_gb",
             "quantity": 64, "unit": "GiB", "billing_model": "monthly"},
            {"entry_id": "e-ads-003", "cluster_id": "c-ads", "cluster_name": "ads-ranking",
             "resource_name": "model storage", "resource_family": "storage", "metric_code": "block_storage_gb",
             "quantity": 500, "unit": "GiB", "billing_model": "monthly"},
            # distractor: shared-ops entry
            {"entry_id": "e-shared-001", "cluster_id": "c-shared", "cluster_name": "shared-ops",
             "resource_name": "CI runner vcpu", "resource_family": "compute", "metric_code": "vcpu",
             "quantity": 4, "unit": "vcpu", "billing_model": "autoscale"}
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # pricing_catalogs.json – one active (June 2026), one archived (March 2026)
    pricing_catalogs = {
        "pricing_catalogs": [
            {"catalog_id": "cat-2026-03", "version": "2026.03-archive", "status": "archived",
             "region": "us-east-1", "currency": "USD", "billing_month": "2026-03", "billing_hours": 744,
             "approved_for_reporting": False, "effective_from": "2026-03-01", "effective_to": "2026-03-31",
             "rates": [
                 {"resource_family": "compute", "metric_code": "vcpu", "unit_cost": 0.15},
                 {"resource_family": "compute", "metric_code": "memory_gb", "unit_cost": 0.025},
                 {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_cost": 0.10}
             ]},
            {"catalog_id": "cat-2026-06", "version": "2026.06-live", "status": "active",
             "region": "us-east-1", "currency": "USD", "billing_month": "2026-06", "billing_hours": 720,
             "approved_for_reporting": True, "effective_from": "2026-06-01", "effective_to": "2026-06-30",
             "rates": [
                 {"resource_family": "compute", "metric_code": "vcpu", "unit_cost": 0.12},
                 {"resource_family": "compute", "metric_code": "memory_gb", "unit_cost": 0.02},
                 {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_cost": 0.08}
             ]}
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

if __name__ == "__main__":
    build_env()
