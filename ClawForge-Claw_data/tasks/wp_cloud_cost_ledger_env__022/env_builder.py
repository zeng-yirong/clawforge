import os, json

def build_env():
    # Create directories
    for d in ["data/pricing", "data/resources", "data/attachments", "ops"]:
        os.makedirs(d, exist_ok=True)

    # accounts.json (simple)
    accounts = [
        {"account_id": "acc1", "display_name": "NorthStar Prod", "department": "Engineering", "email": "ops@northstar.example.com", "permissions": ["admin"], "default_region": "us-east-1", "voice": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # attachments.json and actual attachment files
    attachments_json = [
        {"path": "cost_accounting_rules.md", "title": "Cloud Cost Accounting Rules", "kind": "accounting_policy", "description": "Internal rules for cost allocation"},
        {"path": "report_schema.md", "title": "Monthly Cost Report Schema", "kind": "report_schema", "description": "Expected output format"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump(attachments_json, f)
    with open("data/attachments/cost_accounting_rules.md", "w") as f:
        f.write("# Cloud Cost Accounting Rules\n\n1. Always use active pricing catalog.\n2. Only business clusters are billed.\n3. Shared platform costs are allocated separately.\n")
    with open("data/attachments/report_schema.md", "w") as f:
        f.write("# Monthly Cost Report Schema\n\nThe report must be a JSON file with the following structure:\n- report_month: string (e.g., '2026-06')\n- clusters: array of objects, each with cluster_id and cost\n- total_cost: number (sum of all cluster costs)\n\nExample:\n```json\n{\n  \"report_month\": \"2026-06\",\n  \"clusters\": [\n    {\"cluster_id\": \"ads-ranking\", \"cost\": 12.0},\n    {\"cluster_id\": \"lakehouse-analytics\", \"cost\": 22.5}\n  ],\n  \"total_cost\": 34.5\n}\n```\n")

    # clusters.json
    clusters = [
        {"cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "business_service": "Ads ranking and campaign inference", "domain": "marketing", "environment": "production", "region": "us-east-1", "owner_team": "Growth Engineering", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["ads", "ml"]},
        {"cluster_id": "lakehouse-analytics", "cluster_name": "lakehouse-analytics", "business_service": "Lakehouse analytics and finance marts", "domain": "data", "environment": "production", "region": "us-west-2", "owner_team": "Data Platform", "cluster_role": "business", "service_tier": "tier_1", "workload_tags": ["analytics", "lakehouse"]},
        {"cluster_id": "retail-core", "cluster_name": "retail-core", "business_service": "Storefront and order orchestration", "domain": "commerce", "environment": "production", "region": "eu-west-1", "owner_team": "Commerce Platform", "cluster_role": "business", "service_tier": "tier_2", "workload_tags": ["storefront"]},
        {"cluster_id": "shared-ops", "cluster_name": "shared-ops", "business_service": "Shared CI and platform tooling", "domain": "infrastructure", "environment": "production", "region": "us-east-1", "owner_team": "Cloud Foundations", "cluster_role": "shared_platform", "service_tier": "tier_2", "workload_tags": ["ci", "shared"]}
    ]
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f)

    # pricing catalogs
    pricing_catalogs = [
        {
            "catalog_id": "cat-archived-2026-03",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit": "vcpu", "price": 0.04},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit": "GiB", "price": 0.008},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit": "GiB", "price": 0.0008},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit": "GiB", "price": 0.0004}
            ]
        },
        {
            "catalog_id": "cat-live-2026-06",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit": "vcpu", "price": 0.05},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit": "GiB", "price": 0.01},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit": "GiB", "price": 0.001},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit": "GiB", "price": 0.0005}
            ]
        }
    ]
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f)

    # resource ledger - many entries with interference
    resource_ledger = [
        # ads-ranking June entries
        {"entry_id": "e001", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_name": "ads-cpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 100, "unit": "vcpu", "billing_model": "monthly", "billing_month": "2026-06"},
        {"entry_id": "e002", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_name": "ads-mem-pool", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 500, "unit": "GiB", "billing_model": "monthly", "billing_month": "2026-06"},
        {"entry_id": "e003", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_name": "ads-block-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly", "billing_month": "2026-06"},
        # ads-ranking May entries (interference)
        {"entry_id": "e004", "cluster_id": "ads-ranking", "cluster_name": "ads-ranking", "resource_name": "ads-cpu-pool", "resource_family": "compute", "metric_code": "vcpu", "quantity": 80, "unit": "vcpu", "billing_model": "monthly", "billing_month": "2026-05"},
        # lakehouse-analytics June entries
        {"entry_id": "e005", "cluster_id": "lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_name": "lakehouse-cpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 200, "unit": "vcpu", "billing_model": "reserved", "billing_month": "2026-06"},
        {"entry_id": "e006", "cluster_id": "lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_name": "lakehouse-mem", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 1000, "unit": "GiB", "billing_model": "reserved", "billing_month": "2026-06"},
        {"entry_id": "e007", "cluster_id": "lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_name": "lakehouse-object-store", "resource_family": "storage", "metric_code": "object_storage_gb", "quantity": 5000, "unit": "GiB", "billing_model": "monthly", "billing_month": "2026-06"},
        # lakehouse-analytics March entries (interference)
        {"entry_id": "e008", "cluster_id": "lakehouse-analytics", "cluster_name": "lakehouse-analytics", "resource_name": "lakehouse-cpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 150, "unit": "vcpu", "billing_model": "reserved", "billing_month": "2026-03"},
        # retail-core June entries (interference, business cluster but not requested)
        {"entry_id": "e009", "cluster_id": "retail-core", "cluster_name": "retail-core", "resource_name": "store-cpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 300, "unit": "vcpu", "billing_model": "monthly", "billing_month": "2026-06"},
        {"entry_id": "e010", "cluster_id": "retail-core", "cluster_name": "retail-core", "resource_name": "store-mem", "resource_family": "compute", "metric_code": "memory_gb", "quantity": 1500, "unit": "GiB", "billing_model": "monthly", "billing_month": "2026-06"},
        # shared-ops June entries (interference, shared_platform)
        {"entry_id": "e011", "cluster_id": "shared-ops", "cluster_name": "shared-ops", "resource_name": "ci-cpu", "resource_family": "compute", "metric_code": "vcpu", "quantity": 50, "unit": "vcpu", "billing_model": "autoscale", "billing_month": "2026-06"},
        {"entry_id": "e012", "cluster_id": "shared-ops", "cluster_name": "shared-ops", "resource_name": "ci-storage", "resource_family": "storage", "metric_code": "block_storage_gb", "quantity": 1000, "unit": "GiB", "billing_model": "monthly", "billing_month": "2026-06"},
    ]
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f)

    # contacts.json (optional)
    contacts = [
        {"contact_id": "c1", "name": "Daniel Song", "role": "Cloud FinOps Lead", "email": "daniel.song@northstar.example.com"},
        {"contact_id": "c2", "name": "Leah Kumar", "role": "Cloud Operations Manager", "email": "leah.kumar@northstar.example.com"},
        {"contact_id": "c3", "name": "Tara Ng", "role": "Data Platform Director", "email": "tara.ng@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

if __name__ == "__main__":
    build_env()
