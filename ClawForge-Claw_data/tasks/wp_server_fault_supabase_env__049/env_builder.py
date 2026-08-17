import os
import json
from datetime import datetime, timedelta
import random

def build_env():
    base = os.getcwd()
    # 创建必要目录
    os.makedirs(os.path.join(base, "data", "incidents"), exist_ok=True)
    os.makedirs(os.path.join(base, "ops"), exist_ok=True)
    os.makedirs(os.path.join(base, "backup"), exist_ok=True)

    # 正确工单池 —— 包含目标和非目标，含脏数据
    incidents = []
    now = datetime.utcnow()

    # 定义合法工单模板
    categories = ['ups_outage', 'service_down', 'db_replica_lag', 'network_degradation']
    severities = ['critical', 'high', 'medium']
    statuses = ['open', 'triaged', 'closed', 'resolved']
    teams = ['power_ops', 'app_ops', 'db_ops', 'network_ops', 'ml_platform']
    ticket_types = ['risk_work_order', 'watchlist']
    services = ['west4-spine-uplink', 'billing-api', 'edge-cluster-a12', 'inference-worker', 'analytics-mirror']

    # 生成基础工单（含所有组合）
    for i in range(1, 36):
        cat = random.choice(categories)
        sev = random.choice(severities)
        st = random.choice(statuses)
        team = random.choice(teams)
        tt = random.choice(ticket_types)
        svc = random.choice(services)
        opened = (now - timedelta(hours=random.randint(1, 48))).isoformat() + "Z"
        updated = (now - timedelta(hours=random.randint(0, 24))).isoformat() + "Z"
        incident = {
            "incident_id": f"INC-{i:04d}",
            "title": f"模拟工单 {i}",
            "category": cat,
            "severity": sev,
            "status": st,
            "assigned_team": team,
            "ticket_type": tt,
            "service": svc,
            "opened_at": opened,
            "updated_at": updated,
            "description": f"这是工单 {i} 的描述",
            "tags": ["simulated"]
        }
        incidents.append(incident)

    # 手动设定一批目标工单（确保唯一答案）
    target_ids = ["INC-0101", "INC-0102", "INC-0103", "INC-0104", "INC-0105"]
    target_data = [
        {"category": "ups_outage", "severity": "critical", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink"},
        {"category": "service_down", "severity": "high", "status": "open", "assigned_team": "app_ops", "ticket_type": "risk_work_order", "service": "billing-api"},
        {"category": "ups_outage", "severity": "medium", "status": "triaged", "assigned_team": "power_ops", "ticket_type": "watchlist", "service": "edge-cluster-a12"},
        {"category": "service_down", "severity": "critical", "status": "triaged", "assigned_team": "ml_platform", "ticket_type": "risk_work_order", "service": "inference-worker"},
        {"category": "ups_outage", "severity": "high", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink"},
    ]
    for tid, td in zip(target_ids, target_data):
        inc = {
            "incident_id": tid,
            "title": f"真实UPS/服务中断 {tid}",
            "category": td["category"],
            "severity": td["severity"],
            "status": td["status"],
            "assigned_team": td["assigned_team"],
            "ticket_type": td["ticket_type"],
            "service": td["service"],
            "opened_at": (now - timedelta(hours=2)).isoformat() + "Z",
            "updated_at": (now - timedelta(minutes=15)).isoformat() + "Z",
            "description": "紧急：需要立即处理！",
            "tags": ["urgent", "power"]
        }
        incidents.append(inc)

    # 添加脏数据 / 干扰项
    # 1. 缺少 category
    incidents.append({
        "incident_id": "DIRTY-1",
        "title": "脏数据缺少category",
        "severity": "low",
        "status": "open",
        "assigned_team": "power_ops",
        "ticket_type": "risk_work_order",
        "service": "analytics-mirror",
        "opened_at": now.isoformat() + "Z",
        "updated_at": now.isoformat() + "Z",
        "description": "字段缺失",
        "tags": []
    })
    # 2. status 为 closed 但 category 符合
    incidents.append({
        "incident_id": "DIRTY-2",
        "title": "已经是关闭的工单",
        "category": "ups_outage",
        "severity": "critical",
        "status": "closed",
        "assigned_team": "power_ops",
        "ticket_type": "risk_work_order",
        "service": "west4-spine-uplink",
        "opened_at": (now - timedelta(days=1)).isoformat() + "Z",
        "updated_at": (now - timedelta(hours=10)).isoformat() + "Z",
        "description": "早已处理",
        "tags": []
    })
    # 3. category 合法但 service 不匹配（不影响筛选，但用于混淆）
    incidents.append({
        "incident_id": "DIRTY-3",
        "title": "服务字段不正确",
        "category": "service_down",
        "severity": "high",
        "status": "open",
        "assigned_team": "db_ops",
        "ticket_type": "risk_work_order",
        "service": "db-replica-lag",
        "opened_at": now.isoformat() + "Z",
        "updated_at": now.isoformat() + "Z",
        "description": "服务名不符合枚举",
        "tags": []
    })

    # 写入主文件
    with open(os.path.join(base, "data", "incidents", "incident_pool.json"), "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # 放置干扰文件：备份中的过期池
    backup_incidents = []
    for i in range(1, 6):
        backup_incidents.append({
            "incident_id": f"OLD-{i:04d}",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
        })
    with open(os.path.join(base, "backup", "incident_pool_20250301.json"), "w") as f:
        json.dump(backup_incidents, f)

    # 另一个目录下的同名文件（诱饵）
    os.makedirs(os.path.join(base, "tmp"), exist_ok=True)
    with open(os.path.join(base, "tmp", "incident_pool.json"), "w") as f:
        json.dump({"dummy": True}, f)

    # 创建一个空的运行手册（用于氛围）
    with open(os.path.join(base, "runbook_ups_and_service.md"), "w") as f:
        f.write("# UPS and Service Outage Runbook\n\nSee attachment for details.\n")

    # 可选日志文件（制造干扰）
    with open(os.path.join(base, "syslog.txt"), "w") as f:
        f.write("Mar 15 03:14:15 west4-kernel: UPS critical battery\n")

if __name__ == "__main__":
    build_env()
