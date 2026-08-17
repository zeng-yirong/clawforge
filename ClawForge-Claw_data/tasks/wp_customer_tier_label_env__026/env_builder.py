import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户数据
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "CarePulse",
            "industry": "healthcare",
            "tier": "enterprise",
            "labels": ["vip"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "HealthPlus",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": ["new"],
            "owner_name": "Carol"
        },
        {
            "customer_id": "C004",
            "customer_name": "FinCorp",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["old_partner"],
            "owner_name": "Dave"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 消费日志
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 25000},
        {"customer_id": "C002", "quarter_spend_usd": 15000},
        {"customer_id": "C003", "quarter_spend_usd": 8000},
        {"customer_id": "C004", "quarter_spend_usd": 5000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

    # 活跃日志
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 45, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 90, "usage_trend": "up"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 10, "usage_trend": "down"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 规则文件
    rules_content = """客户分层规则（2025版）：
1. 消费等级：根据每季度消费额（quarter_spend_usd）和最近活跃天数（last_active_days）划分：
   - Gold: 消费 >= 20000 且 活跃天数 <= 30
   - Silver: 消费 >= 10000 且 活跃天数 <= 60
   - Bronze: 其他
2. 附加标签：如果风险等级（risk_level）为'high'且使用趋势（usage_trend）为'down'，则增加标签'attention'
3. 最终标签 = 原有标签 + 消费等级标签 + 条件附加标签（如有重复则合并）"""
    with open("ops/tier_rules.txt", "w") as f:
        f.write(rules_content)

    # 干扰文件：过期的旧日志、无关客户、附件等
    # 旧消费日志（模拟旧季度数据，应被忽略）
    old_consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 18000},
        {"customer_id": "C002", "quarter_spend_usd": 9000}
    ]
    with open("data/logs/old_consumption_logs.json", "w") as f:
        json.dump({"old_consumption_logs": old_consumption}, f, indent=2)

    # 一个不在客户列表中的额外活动记录（干扰）
    extra_activity = [
        {"customer_id": "X001", "risk_level": "high", "last_active_days": 5, "usage_trend": "down"}
    ]
    with open("data/logs/extra_activity_logs.json", "w") as f:
        json.dump({"extra_activity_logs": extra_activity}, f, indent=2)

    # 附件文件（无关）
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": []}, f, indent=2)

    # 为增加复杂度，添加一个空的 backup 目录
    os.makedirs("ops/backup", exist_ok=True)
    with open("ops/backup/old_rules.txt", "w") as f:
        f.write("旧版规则（已废弃）")

if __name__ == "__main__":
    build_env()
