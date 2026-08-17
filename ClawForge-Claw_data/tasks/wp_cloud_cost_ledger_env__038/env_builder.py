import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- 定价目录 ----------
    pricing_catalogs = {
        "pricing_catalogs": [
            {
                "catalog_id": "cat_2026_03",
                "version": "2026.03-archive",
                "status": "archived",
                "region": "us-east-1",
                "currency": "USD",
                "billing_month": "2026-03",
                "billing_hours": 744,
                "approved_for_reporting": False,
                "effective_from": "2026-03-01",
                "effective_to": "2026-03-31",
                "rates": [
                    {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.035},
                    {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.008},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.09},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.04},
                    {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.45}
                ]
            },
            {
                "catalog_id": "cat_2026_06",
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
                    {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.04},
                    {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.01},
                    {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.10},
                    {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.05},
                    {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.50}
                ]
            }
        ]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # ---------- 集群信息 ----------
    clusters = {
        "clusters": [
            {
                "cluster_id": "c1",
                "cluster_name": "ads-ranking",
                "business_service": "Ads ranking and campaign inference",
                "domain": "marketing",
                "environment": "prod",
                "region": "us-east-1",
                "owner_team": "Growth Engineering",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["ml-inference", "online"]
            },
            {
                "cluster_id": "c2",
                "cluster_name": "lakehouse-analytics",
                "business_service": "Lakehouse analytics and finance marts",
                "domain": "data",
                "environment": "prod",
                "region": "us-east-1",
                "owner_team": "Data Platform",
                "cluster_role": "business",
                "service_tier": "tier_2",
                "workload_tags": ["batch", "analytics"]
            },
            {
                "cluster_id": "c3",
                "cluster_name": "retail-core",
                "business_service": "Storefront and order orchestration",
                "domain": "commerce",
                "environment": "prod",
                "region": "us-west-2",
                "owner_team": "Commerce Platform",
                "cluster_role": "business",
                "service_tier": "tier_1",
                "workload_tags": ["online", "transactional"]
            },
            {
                "cluster_id": "c4",
                "cluster_name": "shared-ops",
                "business_service": "Shared CI and platform tooling",
                "domain": "infrastructure",
                "environment": "prod",
                "region": "eu-west-1",
                "owner_team": "Cloud Foundations",
                "cluster_role": "shared_platform",
                "service_tier": "tier_2",
                "workload_tags": ["ci", "monitoring"]
            }
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # ---------- 资源台账 (含干扰项) ----------
    resource_ledger = {
        "resource_ledger": [
            # --- ads-ranking 的正确条目 ---
            {
                "entry_id": "e1",
                "cluster_id": "c1",
                "cluster_name": "ads-ranking",
                "resource_name": "cpu-pool",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 120,
                "unit": "vcpu",
                "billing_model": "reserved"
            },
            {
                "entry_id": "e2",
                "cluster_id": "c1",
                "cluster_name": "ads-ranking",
                "resource_name": "mem-pool",
                "resource_family": "compute",
                "metric_code": "memory_gb",
                "quantity": 512,
                "unit": "GiB",
                "billing_model": "reserved"
            },
            {
                "entry_id": "e3",
                "cluster_id": "c1",
                "cluster_name": "ads-ranking",
                "resource_name": "ssd-vol",
                "resource_family": "storage",
                "metric_code": "block_storage_gb",
                "quantity": 2000,
                "unit": "GiB",
                "billing_model": "monthly"
            },
            # --- 干扰：其他集群 ---
            {
                "entry_id": "e4",
                "cluster_id": "c2",
                "cluster_name": "lakehouse-analytics",
                "resource_name": "batch-vcpus",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 200,
                "unit": "vcpu",
                "billing_model": "autoscale"
            },
            {
                "entry_id": "e5",
                "cluster_id": "c2",
                "cluster_name": "lakehouse-analytics",
                "resource_name": "analytics-mem",
                "resource_family": "compute",
                "metric_code": "memory_gb",
                "quantity": 1024,
                "unit": "GiB",
                "billing_model": "monthly"
            },
            {
                "entry_id": "e6",
                "cluster_id": "c4",
                "cluster_name": "shared-ops",
                "resource_name": "ci-vcpus",
                "resource_family": "compute",
                "metric_code": "vcpu",
                "quantity": 32,
                "unit": "vcpu",
                "billing_model": "reserved"
            },
            # --- 干扰：ads-ranking 但 metric 不在 active 目录中（故意增加迷惑性） ---
            {
                "entry_id": "e7",
                "cluster_id": "c1",
                "cluster_name": "ads-ranking",
                "resource_name": "gpu-node",
                "resource_family": "compute",
                "metric_code": "gpu",
                "quantity": 0,
                "unit": "gpu",
                "billing_model": "reserved"
            }
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # ---------- 其他辅助文件（干扰/参考） ----------
    accounts = {
        "accounts": [
            {"account_id": "a001", "display_name": "Marketing Prod", "department": "Marketing", "email": "marketing-prod@northstar.example.com", "permissions": ["billing-read"], "default_region": "us-east-1", "voice": ["daniel.song@northstar.example.com"]},
            {"account_id": "a002", "display_name": "Data Platform Prod", "department": "Data", "email": "data-prod@northstar.example.com", "permissions": ["billing-read"], "default_region": "us-east-1", "voice": ["leah.kumar@northstar.example.com"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    attachments = {
        "attachments": [
            {
                "path": "cost_accounting_rules.md",
                "title": "Cloud Cost Accounting Rules",
                "kind": "accounting_policy",
                "description": "Use active pricing catalog for billing month. Only business clusters are billed."
            },
            {
                "path": "report_schema.md",
                "title": "Monthly Cost Report Schema",
                "kind": "report_schema",
                "description": "Report must include total_cost and line items with resource_name, quantity, unit_price, cost."
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Daniel Song", "role": "Cloud FinOps Lead", "email": "daniel.song@northstar.example.com"},
            {"contact_id": "c002", "name": "Leah Kumar", "role": "Cloud Operations Manager", "email": "leah.kumar@northstar.example.com"},
            {"contact_id": "c003", "name": "Tara Ng", "role": "Data Platform Director", "email": "tara.ng@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 一个无关的日志目录
    os.makedirs("logs", exist_ok=True)
    with open("logs/audit_2026_06.log", "w") as f:
        f.write("2026-06-15 10:00:00 [INFO] Billing snapshot taken\n")

if __name__ == "__main__":
    build_env()
