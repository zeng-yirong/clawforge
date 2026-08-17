import os
import json

def build_env():
    # 确保工作区干净（cwd 已切到 .）
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 旅行政策（标准级别）
    policy = {
        "policy_id": "standard",
        "tier": "standard",
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True, "budget": 400.0},
            {"category_id": "flight",      "name": "机票",   "reimbursable": True, "budget": 1000.0},
            {"category_id": "food",        "name": "餐饮",   "reimbursable": True, "budget": 300.0},
            {"category_id": "taxi",        "name": "出租车", "reimbursable": True, "budget": 100.0},
            {"category_id": "metro",       "name": "地铁公交","reimbursable": True, "budget": 50.0},
            {"category_id": "communication","name": "通讯费", "reimbursable": True, "budget": 80.0},
            {"category_id": "misc",        "name": "其他杂费","reimbursable": True, "budget": 200.0}
        ]
    }
    # 干扰：高级别政策（与任务无关）
    exec_policy = {
        "policy_id": "executive",
        "tier": "executive",
        "categories": [{"category_id": "accommodation","name":"住宿","reimbursable":True,"budget":800.0}]
    }
    with open("data/travel_policies.json", "w", encoding="utf-8") as f:
        json.dump(policy, f, ensure_ascii=False, indent=2)
    with open("data/exec_policy.json", "w", encoding="utf-8") as f:
        json.dump(exec_policy, f, ensure_ascii=False, indent=2)

    # 2. 消费记录（主要 + 干扰）
    records = [
        # ---- Alice 上海出差 SH-2024-01 ----
        {"record_id":"rec001","employee_name":"Alice","trip_id":"SH-2024-01",
         "category":"accommodation","date":"2024-03-10","amount":250.0,"receipt":True,"vendor":"锦江之星","nights":1,"description":"上海住宿第一晚"},
        {"record_id":"rec002","employee_name":"Alice","trip_id":"SH-2024-01",
         "category":"accommodation","date":"2024-03-11","amount":250.0,"receipt":True,"vendor":"锦江之星","nights":1,"description":"上海住宿第二晚"},
        {"record_id":"rec003","employee_name":"Alice","trip_id":"SH-2024-01",
         "category":"flight","date":"2024-03-09","amount":1200.0,"receipt":True,"vendor":"南航","description":"上海往返机票"},
        {"record_id":"rec004","employee_name":"Alice","trip_id":"SH-2024-01",
         "category":"food","date":"2024-03-10","amount":150.0,"receipt":True,"vendor":"小杨生煎","description":"午餐"},
        {"record_id":"rec005","employee_name":"Alice","trip_id":"SH-2024-01",
         "category":"food","date":"2024-03-10","amount":100.0,"receipt":True,"vendor":"外婆家","description":"晚餐"},
        {"record_id":"rec006","employee_name":"Alice","trip_id":"SH-2024-01",
         "category":"taxi","date":"2024-03-09","amount":50.0,"receipt":True,"vendor":"滴滴","description":"机场到酒店"},
        # ---- 干扰：Bob 的出差 ----
        {"record_id":"rec010","employee_name":"Bob","trip_id":"BJ-2024-02",
         "category":"accommodation","date":"2024-03-15","amount":300.0,"receipt":True,"vendor":"汉庭","nights":1,"description":"北京出差"},
        {"record_id":"rec011","employee_name":"Bob","trip_id":"BJ-2024-02",
         "category":"flight","date":"2024-03-14","amount":800.0,"receipt":True,"vendor":"国航","description":"北京机票"},
        # ---- 干扰：Alice 的其他出差（非上海） ----
        {"record_id":"rec020","employee_name":"Alice","trip_id":"GZ-2024-03",
         "category":"accommodation","date":"2024-04-01","amount":350.0,"receipt":True,"vendor":"希尔顿","nights":1,"description":"广州出差"},
        # ---- 干扰：缺少收据的脏数据 ----
        {"record_id":"rec030","employee_name":"Alice","trip_id":"SH-2024-01",
         "category":"misc","date":"2024-03-10","amount":100.0,"receipt":False,"vendor":"无","description":"未报销收据"},
        # ---- 干扰：过期记录 ----
        {"record_id":"rec040","employee_name":"Alice","trip_id":"SH-2023-12",
         "category":"accommodation","date":"2023-12-20","amount":200.0,"receipt":True,"vendor":"如家","nights":1,"description":"去年出差"}
    ]
    with open("data/consumption_records.json", "w", encoding="utf-8") as f:
        json.dump({"records": records}, f, ensure_ascii=False, indent=2)

    # 3. 额外干扰文件（无用）
    with open("data/old_policy_backup.json", "w", encoding="utf-8") as f:
        json.dump({"note": "此文件已废弃，勿用"}, f)

    # 确保 ops 存在（已创建）
    # 不写入额外内容

if __name__ == "__main__":
    build_env()
