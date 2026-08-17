import os
import json

def build_env():
    # 确保基础目录存在
    os.makedirs("data/pricing", exist_ok=True)
    os.makedirs("data/resources", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("reports", exist_ok=True)  # 目标输出目录，初始为空

    # --- 附件：成本会计规则 ---
    rules_md = """# Cloud Cost Accounting Rules (生效期：2026-06)

## 适用范围
仅计算 cluster_role 为 'business' 的集群。共享平台（shared_platform）不计入。

## 定价目录选择
使用状态为 'active' 且 approved_for_reporting 为 true 的定价目录。当前生效目录为 2026-06-live。

## 资源-成本映射
- compute 类资源：
  - vcpu：按 vcpu 单价（美元/vcpu）* 数量
  - gpu：按 gpu 单价（美元/gpu）* 数量
  - memory_gb：不计入（已包含在 vcpu 捆绑中）
- storage 类资源：
  - block_storage_gb：按 block_storage 单价（美元/GiB）* 数量
  - object_storage_gb：按 object_storage 单价（美元/GiB）* 数量

## 输出格式
每个集群一行，包含字段：
  - cluster_id
  - cluster_name
  - compute_cost (美元)
  - storage_cost (美元)
  - total_cost (美元)
"""
    with open("attachments/cost_accounting_rules.md", "w") as f:
        f.write(rules_md)

    # --- 联系人（干扰）---
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Daniel Song", "role": "Cloud FinOps Lead",
             "email": "daniel.song@northstar.example.com"},
            {"contact_id": "c002", "name": "Leah Kumar", "role": "Cloud Operations Manager",
             "email": "leah.kumar@northstar.example.com"},
            {"contact_id": "c003", "name": "Tara Ng", "role": "Data Platform Director",
             "email": "tara.ng@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- 账户（干扰）---
    accounts = {
        "accounts": [
            {"account_id": "a-001", "display_name": "NorthStar Prod", "department": "Engineering",
             "email": "cloudops@northstar.example.com", "permissions": ["admin"],
             "default_region": "us-east-1", "voice": ["en"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- 定价目录 ---
    # 归档版（三月，不可用）
    catalog_archived = {
        "catalog_id": "2026-03-archive",
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
            {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.08},
            {"resource_family": "compute", "metric_code": "gpu", "unit_price": 0.80},
            {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.04},
            {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.015}
        ]
    }
    # 生效版（六月，可用）
    catalog_live = {
        "catalog_id": "2026-06-live",
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
            {"resource_family": "compute", "metric_code": "vcpu", "unit_price": 0.10},
            {"resource_family": "compute", "metric_code": "gpu", "unit_price": 1.00},
            {"resource_family": "storage", "metric_code": "block_storage_gb", "unit_price": 0.05},
            {"resource_family": "storage", "metric_code": "object_storage_gb", "unit_price": 0.02}
        ]
    }
    pricing_catalogs = {
        "pricing_catalogs": [catalog_archived, catalog_live]
    }
    with open("data/pricing/pricing_catalogs.json", "w") as f:
        json.dump(pricing_catalogs, f, indent=2)

    # --- 集群 ---
    clusters = {
        "clusters": [
            {"cluster_id": "c-ads", "cluster_name": "ads-ranking",
             "business_service": "Ads ranking and campaign inference",
             "domain": "marketing", "environment": "production", "region": "us-east-1",
             "owner_team": "Growth Engineering", "cluster_role": "business",
             "service_tier": "tier_1", "workload_tags": ["ad-serving", "real-time"]},
            {"cluster_id": "c-lake", "cluster_name": "lakehouse-analytics",
             "business_service": "Lakehouse analytics and finance marts",
             "domain": "data", "environment": "production", "region": "us-east-1",
             "owner_team": "Data Platform", "cluster_role": "business",
             "service_tier": "tier_1", "workload_tags": ["etl", "reporting"]},
            {"cluster_id": "c-retail", "cluster_name": "retail-core",
             "business_service": "Storefront and order orchestration",
             "domain": "commerce", "environment": "production", "region": "us-east-1",
             "owner_team": "Commerce Platform", "cluster_role": "business",
             "service_tier": "tier_1", "workload_tags": ["storefront", "orders"]},
            {"cluster_id": "c-shared", "cluster_name": "shared-ops",
             "business_service": "Shared CI and platform tooling",
             "domain": "infrastructure", "environment": "production", "region": "us-east-1",
             "owner_team": "Cloud Foundations", "cluster_role": "shared_platform",
             "service_tier": "tier_2", "workload_tags": ["ci-cd", "monitoring"]}
        ]
    }
    with open("data/resources/clusters.json", "w") as f:
        json.dump(clusters, f, indent=2)

    # --- 资源流水（包含脏数据：重复 entry_id、不存在的集群引用、非业务集群条目）---
    resource_ledger = {
        "resource_ledger": [
            # ads-ranking 正常条目
            {"entry_id": "e001", "cluster_id": "c-ads", "cluster_name": "ads-ranking",
             "resource_name": "ads-vcpu-pool", "resource_family": "compute",
             "metric_code": "vcpu", "quantity": 80, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "e002", "cluster_id": "c-ads", "cluster_name": "ads-ranking",
             "resource_name": "ads-gpu-nodes", "resource_family": "compute",
             "metric_code": "gpu", "quantity": 4, "unit": "gpu", "billing_model": "monthly"},
            {"entry_id": "e003", "cluster_id": "c-ads", "cluster_name": "ads-ranking",
             "resource_name": "ads-block-store", "resource_family": "storage",
             "metric_code": "block_storage_gb", "quantity": 2000, "unit": "GiB", "billing_model": "monthly"},
            # lakehouse-analytics 正常条目
            {"entry_id": "e004", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics",
             "resource_name": "lake-vcpu", "resource_family": "compute",
             "metric_code": "vcpu", "quantity": 120, "unit": "vcpu", "billing_model": "autoscale"},
            {"entry_id": "e005", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics",
             "resource_name": "lake-object-store", "resource_family": "storage",
             "metric_code": "object_storage_gb", "quantity": 5000, "unit": "GiB", "billing_model": "monthly"},
            # retail-core 正常条目
            {"entry_id": "e006", "cluster_id": "c-retail", "cluster_name": "retail-core",
             "resource_name": "retail-vcpu", "resource_family": "compute",
             "metric_code": "vcpu", "quantity": 200, "unit": "vcpu", "billing_model": "reserved"},
            {"entry_id": "e007", "cluster_id": "c-retail", "cluster_name": "retail-core",
             "resource_name": "retail-block-store", "resource_family": "storage",
             "metric_code": "block_storage_gb", "quantity": 3500, "unit": "GiB", "billing_model": "monthly"},
            # shared-ops (非业务集群，应排除)
            {"entry_id": "e008", "cluster_id": "c-shared", "cluster_name": "shared-ops",
             "resource_name": "shared-vcpu", "resource_family": "compute",
             "metric_code": "vcpu", "quantity": 50, "unit": "vcpu", "billing_model": "monthly"},
            {"entry_id": "e009", "cluster_id": "c-shared", "cluster_name": "shared-ops",
             "resource_name": "shared-block-store", "resource_family": "storage",
             "metric_code": "block_storage_gb", "quantity": 800, "unit": "GiB", "billing_model": "monthly"},
            # 脏数据：重复 entry_id (e002 已经存在，这个副本 quantity 不同，需要处理)
            {"entry_id": "e002", "cluster_id": "c-ads", "cluster_name": "ads-ranking",
             "resource_name": "ads-gpu-duplicate", "resource_family": "compute",
             "metric_code": "gpu", "quantity": 99, "unit": "gpu", "billing_model": "monthly"},
            # 脏数据：引用不存在的 cluster_id (应被忽略，因为找不到匹配的 business 集群)
            {"entry_id": "e010", "cluster_id": "c-ghost", "cluster_name": "ghost-cluster",
             "resource_name": "ghost-vcpu", "resource_family": "compute",
             "metric_code": "vcpu", "quantity": 30, "unit": "vcpu", "billing_model": "monthly"},
            # 脏数据：memory 条目（规则说忽略）
            {"entry_id": "e011", "cluster_id": "c-lake", "cluster_name": "lakehouse-analytics",
             "resource_name": "lake-memory", "resource_family": "compute",
             "metric_code": "memory_gb", "quantity": 512, "unit": "GiB", "billing_model": "monthly"},
        ]
    }
    with open("data/resources/resource_ledger.json", "w") as f:
        json.dump(resource_ledger, f, indent=2)

    # --- 额外附件（干扰）---
    schema_md = """# Monthly Cost Report Schema

## 字段定义
- cluster_id: 集群标识
- cluster_name: 集群名称
- compute_cost: 计算资源总成本（美元）
- storage_cost: 存储资源总成本（美元）
- total_cost: 总成本（美元）
"""
    with open("attachments/report_schema.md", "w") as f:
        f.write(schema_md)

if __name__ == "__main__":
    build_env()
