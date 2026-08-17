import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户主数据 (wrapper=customers)
    customers = [
        {"customer_id":"C001","customer_name":"CarePulse","industry":"healthcare","tier":"enterprise","labels":["active"],"owner_name":"Alice"},
        {"customer_id":"C002","customer_name":"LedgerFlow","industry":"fintech","tier":"mid_market","labels":["standard"],"owner_name":"Bob"},
        {"customer_id":"C003","customer_name":"CarePulse","industry":"healthcare","tier":"enterprise","labels":["vip"],"owner_name":"Charlie"},
        {"customer_id":"C004","customer_name":"LedgerFlow","industry":"fintech","tier":"mid_market","labels":["premium"],"owner_name":"David"},
        {"customer_id":"C005","customer_name":"CarePulse","industry":"healthcare","tier":"mid_market","labels":["basic"],"owner_name":"Eve"},
        {"customer_id":"C006","customer_name":"LedgerFlow","industry":"fintech","tier":"enterprise","labels":["gold"],"owner_name":"Frank"},
        {"customer_id":"C007","customer_name":"CarePulse","industry":"healthcare","tier":"enterprise","labels":["silver"],"owner_name":"Grace"},
        {"customer_id":"C008","customer_name":"LedgerFlow","industry":"fintech","tier":"mid_market","labels":["bronze"],"owner_name":"Heidi"}
    ]
    with open("data/customers/customers.json","w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 消费日志 (wrapper=consumption_logs)
    consumption_logs = [
        {"customer_id":"C001","quarter_spend_usd":15000},
        {"customer_id":"C002","quarter_spend_usd":8000},
        {"customer_id":"C003","quarter_spend_usd":20000},
        {"customer_id":"C004","quarter_spend_usd":4500},
        {"customer_id":"C005","quarter_spend_usd":3000},
        {"customer_id":"C006","quarter_spend_usd":12000},
        {"customer_id":"C007","quarter_spend_usd":6000},
        {"customer_id":"C008","quarter_spend_usd":2000},
        {"customer_id":"C009","quarter_spend_usd":9999}  # 干扰：不在客户列表
    ]
    with open("data/logs/consumption_logs.json","w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

    # 活跃日志 (wrapper=activity_logs)
    activity_logs = [
        {"customer_id":"C001","risk_level":"low","last_active_days":20,"usage_trend":"up"},
        {"customer_id":"C002","risk_level":"low","last_active_days":50,"usage_trend":"down"},
        {"customer_id":"C003","risk_level":"high","last_active_days":10,"usage_trend":"up"},
        {"customer_id":"C004","risk_level":"low","last_active_days":90,"usage_trend":"down"},
        {"customer_id":"C005","risk_level":"low","last_active_days":100,"usage_trend":"down"},
        {"customer_id":"C006","risk_level":"low","last_active_days":5,"usage_trend":"up"},
        {"customer_id":"C007","risk_level":"high","last_active_days":15,"usage_trend":"up"},
        {"customer_id":"C008","risk_level":"low","last_active_days":120,"usage_trend":"down"},
        {"customer_id":"C010","risk_level":"low","last_active_days":30,"usage_trend":"up"}  # 干扰：不在客户列表
    ]
    with open("data/logs/activity_logs.json","w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 覆盖文件
    overrides = "C005:VIP\n"
    with open("ops/overrides.txt","w") as f:
        f.write(overrides)

    # 额外干扰：旧版本数据（不应被使用）
    os.makedirs("data/old", exist_ok=True)
    old_consumption = [
        {"customer_id":"C001","quarter_spend_usd":5000},  # 旧数据
    ]
    with open("data/old/consumption_logs_2024Q1.json","w") as f:
        json.dump({"consumption_logs": old_consumption}, f, indent=2)

if __name__ == "__main__":
    build_env()
