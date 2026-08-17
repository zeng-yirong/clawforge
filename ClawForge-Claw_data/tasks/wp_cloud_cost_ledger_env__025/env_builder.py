import os
import json
import random
from datetime import datetime

def build_env():
    # ---------- 集群数据 ----------
    clusters = [
        {
            "cluster_id": "cl-retail-001",
            "cluster_name": "retail-core",
            "domain": "commerce",
            "environment": "production",
            "region": "us-east-1",
            "owner_team": "Commerce Platform",
            "service_tier": "tier_1",
            "cluster_role": "business",
            "workload_tags": ["storefront", "order-orchestration"]
        },
        {
            "cluster_id": "cl-ads-002",
            "cluster_name": "ads-ranking",
            "domain": "marketing",
            "environment": "production",
            "region": "us-west-2",
            "owner_team": "Growth Engineering",
            "service_tier": "tier_1",
            "cluster_role": "business",
            "workload_tags": ["campaign", "inference"]
        },
        {
            "cluster_id": "cl-ops-003",
            "cluster_name": "shared-ops",
            "domain": "infrastructure",
            "environment": "staging",
            "region": "eu-central-1",
            "owner_team": "Cloud Foundations",
            "service_tier": "tier_2",
            "cluster_role": "shared_platform",
            "workload_tags": ["ci", "tooling"]
        }
    ]

    # ---------- 资源账本 ----------
    ledger_entries = []
    # retail-core 六月用量 (主要目标)
    entry_id_counter = 1
    def entry(cid, cname, rname, family, metric, qty, unit, model):
        nonlocal entry_id_counter
        e = {
            "entry_id": f"ent-{entry_id_counter:05d}",
            "cluster_id": cid,
            "cluster_name": cname,
            "resource_name": rname,
            "resource_family": family,
            "metric_code": metric,
            "quantity": qty,
            "unit": unit,
            "billing_model": model
        }
        entry_id_counter += 1
        return e

    # retail-core 条目 (故意混合 billing_model，但计算仅按 active 定价，这里无影响)
    ledger_entries.append(entry("cl-retail-001", "retail-core", "web-servers", "compute", "vcpu", 48, "vcpu", "monthly"))
    ledger_entries.append(entry("cl-retail-001", "retail-core", "web-servers", "compute", "memory_gb", 192, "GiB", "monthly"))
    ledger_entries.append(entry("cl-retail-001", "retail-core", "db-tier", "storage", "block_storage_gb", 2048, "GiB", "reserved"))
    ledger_entries.append(entry("cl-retail-001", "retail-core", "ml-inference", "compute", "gpu", 4, "gpu", "autoscale"))
    ledger_entries.append(entry("cl-retail-001", "retail-core", "object-store", "storage", "object_storage_gb", 5120, "GiB", "monthly"))
    # 干扰：ads-ranking 也有很多资源
    ledger_entries.append(entry("cl-ads-002", "ads-ranking", "gpu-cluster", "compute", "gpu", 32, "gpu", "reserved"))
    ledger_entries.append(entry("cl-ads-002", "ads-ranking", "data-lake", "storage", "object_storage_gb", 15000, "GiB", "monthly"))
    # 干扰：shared-ops 是 shared_platform，不应计算
    ledger_entries.append(entry("cl-ops-003", "shared-ops", "build-agents", "compute", "vcpu", 16, "vcpu", "autoscale"))

    # ---------- 定价目录 ----------
    pricing_catalogs = [
        {
            "catalog_id": "cat-202603",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.042},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.0056},
                {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.85},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.10},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.023}
            ]
        },
        {
            "catalog_id": "cat-202606",
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
                {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.045},
                {"resource_family": "compute", "metric_code": "memory_gb", "unit_price": 0.0061},
                {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.92},
                {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.12},
                {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.025}
            ]
        }
    ]

    # ---------- 附件 ----------
    attachments = [
        {
            "path": "report_schema.md",
            "title": "Monthly Cost Report Schema",
            "kind": "report_schema",
            "description": "Specifies the required fields for the monthly cost report."
        }
    ]

    # report_schema.md 内容
    report_schema_content = """# Monthly Cost Report Schema
The cost report must be a single JSON file with the following fields:
- **cluster_id**: string, the cluster identifier from the cluster inventory.
- **month**: string, format YYYY-MM (e.g. 2026-06).
- **currency**: string, three-letter ISO currency code.
- **items**: array of objects, each with:
  - resource_family: string
  - quantity: number (total quantity for that family)
  - unit_price: number (from the active pricing catalog)
  - cost: number (quantity * unit_price)
- **total_cost**: number, sum of all item costs.

Example:
{
  "cluster_id": "cl-retail-001",
  "month": "2026-06",
  "currency": "USD",
  "items": [...],
  "total_cost": 1234.56
}
"""

    # ---------- 写入文件 ----------
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("data/pricing", exist_ok=True)

    with open("data/resources/clusters.json", "w") as f:
        json.dump({"clusters": clusters}, f, indent=2)

    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump({"resource_ledger": ledger_entries}, f, indent=2)

    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump({"pricing_catalogs": pricing_catalogs}, f, indent=2)

    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    with open("report_schema.md", "w") as f:
        f.write(report_schema_content)

    # 再放一个干扰文件，确保 agent 不会误读
    with open("old_note.txt", "w") as f:
        f.write("这个文件没用，别管。")

if __name__ == "__main__":
    build_env()
