import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户数据 (5个客户，第5个没有消费/活动记录)
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "mid_market", "labels": ["growth"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["premium", "vip"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "MediTech", "industry": "healthcare", "tier": "low_value", "labels": ["basic"], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "FinVault", "industry": "fintech", "tier": "mid_market", "labels": ["growth"], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "DataStream", "industry": "fintech", "tier": "enterprise", "labels": ["premium", "vip"], "owner_name": "Eve"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 消费日志 (4个客户，对应C001~C004，故意多一个过时备份)
    consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 20000},
        {"customer_id": "C002", "quarter_spend_usd": 10000},
        {"customer_id": "C003", "quarter_spend_usd": 3000},
        {"customer_id": "C004", "quarter_spend_usd": 7000},
        # 干扰：同一个客户出现过时记录（故意用不同值）
        {"customer_id": "C001", "quarter_spend_usd": 5000}  # 这条会被当作重复？规则文件里说明取第一条？Agent需自行根据规则处理重复。为简化，我们让规则指定取最新一条，但这里没时间戳，实际可以忽略重复。为了让答案唯一，假设消费日志里只有一条有效记录，重复是干扰，Agent应视为脏数据去重（取首次出现或平均值等）。但其实我们设计规则时只对每个客户一条有效，这条重复会让结果产生歧义。所以更好的做法是只放唯一记录，干扰放在backup文件。
    ]
    # 修正：去掉重复，放入干扰备份
    consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 20000},
        {"customer_id": "C002", "quarter_spend_usd": 10000},
        {"customer_id": "C003", "quarter_spend_usd": 3000},
        {"customer_id": "C004", "quarter_spend_usd": 7000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption, f, indent=2)

    # 干干扰：过时备份消费数据
    consumption_backup = [
        {"customer_id": "C001", "quarter_spend_usd": 5000},
        {"customer_id": "C002", "quarter_spend_usd": 8000},
        {"customer_id": "C003", "quarter_spend_usd": 2000}
    ]
    with open("data/logs/consumption_logs_backup.json", "w") as f:
        json.dump(consumption_backup, f, indent=2)

    # 活动日志 (与消费日志对应，C005没有)
    activity = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 40, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 50, "usage_trend": "down"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity, f, indent=2)

    # 正确规则文件
    rules = {
        "rules": [
            {
                "conditions": {
                    "min_spend": 15000,
                    "max_active_days": 30,
                    "risk_level": "low"
                },
                "tier": "enterprise",
                "labels": ["premium", "vip"]
            },
            {
                "conditions": {
                    "min_spend": 15000,
                    "max_active_days": None,
                    "risk_level": None
                },
                "tier": "mid_market",
                "labels": ["growth"]
            },
            {
                "conditions": {
                    "min_spend": 5000,
                    "max_spend": 14999,
                    "max_active_days": 60,
                    "risk_level": None
                },
                "tier": "mid_market",
                "labels": ["growth"]
            },
            {
                "conditions": {
                    "min_spend": None,
                    "max_spend": None,
                    "max_active_days": None,
                    "risk_level": None
                },
                "tier": "low_value",
                "labels": ["basic"]
            }
        ]
    }
    with open("data/segmentation_rules.json", "w") as f:
        json.dump(rules, f, indent=2)

    # 干扰规则（旧版）
    old_rules = {
        "rules": [
            {"conditions": {"min_spend": 10000}, "tier": "gold", "labels": ["vip"]},
            {"conditions": {"min_spend": 5000}, "tier": "silver", "labels": ["star"]}
        ]
    }
    with open("data/old_rules.json", "w") as f:
        json.dump(old_rules, f, indent=2)

    # 其他诱饵文件
    extra_customers = [
        {"customer_id": "C006", "customer_name": "Ghost", "industry": "tech", "tier": "low_value", "labels": ["basic"], "owner_name": "Frank"}
    ]
    with open("data/customers/other_customers.json", "w") as f:
        json.dump(extra_customers, f, indent=2)

    print("环境构建完成")

if __name__ == "__main__":
    build_env()
