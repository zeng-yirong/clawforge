import json, os, datetime

def build_env():
    # 干扰：过期联系人文件
    os.makedirs("data/contacts", exist_ok=True)
    expired = {
        "contacts": [
            {"contact_id": "c_old_1", "name": "Old Monitoring", "role": "Monitoring Service", "phone": "+1-555-0000", "email": "old@mon.com"},
            {"contact_id": "c_old_2", "name": "Ancient Guard", "role": "Monitoring Service", "phone": "+1-555-0001", "email": "ancient@mon.com"}
        ]
    }
    with open("data/contacts/expired_contacts.json", "w") as f:
        json.dump(expired, f, indent=2)

    # 正常联系人（注意排序：第二个才是正确的Monitoring Service，第一个是警察，但按照任务规则取“第一个”角色为Monitoring Service的联系人）
    contacts = {
        "contacts": [
            {"contact_id": "c_001", "name": "Emergency Services", "role": "Police", "phone": "+1-800-555-0123", "email": "police.precinct@example.com"},
            {"contact_id": "c_002", "name": "John Smith", "role": "Monitoring Service", "phone": "+1-555-0101", "email": "john.smith@example.com"},
            {"contact_id": "c_003", "name": "Local Police Precinct", "role": "Police Non-Emergency", "phone": "+1-555-0199", "email": "police.precinct@example.com"},
            {"contact_id": "c_004", "name": "Security Company", "role": "Security Manager", "phone": "911", "email": "monitoring@securityco.com"}
        ]
    }
    with open("data/contacts/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 账户：每个账户有zones列表，只有main_account的zones包含"zone_lobby"
    accounts = {
        "accounts": [
            {
                "account_id": "acc_main",
                "account_name": "Main Building Corp",
                "location": "Headquarters",
                "zones": ["zone_lobby", "zone_garage"],
                "emergency_contacts": ["c_002", "c_004"]   # 第一个角色为Monitoring Service的是c_002
            },
            {
                "account_id": "acc_backup",
                "account_name": "Backup Storage Ltd",
                "location": "Warehouse",
                "zones": ["zone_basement", "zone_backyard"],
                "emergency_contacts": ["c_001", "c_003"]   # 第一个角色为Police，不是Mon Service，但此账户不触发告警，无所谓
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 区域：只有zone_lobby intrusion_detected=True，其他都是False
    zones = {
        "zones": [
            {"zone_id": "zone_lobby", "zone_name": "Main Lobby", "sensors": ["s_lobby_01"], "intrusion_detected": True},
            {"zone_id": "zone_garage", "zone_name": "Garage", "sensors": ["s_garage_01"], "intrusion_detected": False},
            {"zone_id": "zone_basement", "zone_name": "Basement", "sensors": ["s_basement_01"], "intrusion_detected": False},
            {"zone_id": "zone_backyard", "zone_name": "Backyard", "sensors": ["s_backyard_01"], "intrusion_detected": False}
        ]
    }
    with open("data/zones/zones.json", "w") as f:
        json.dump(zones, f, indent=2)

    # 干扰：多出一个无关的旧的alerts目录，包含一些旧记录
    os.makedirs("data/alerts", exist_ok=True)
    old_alerts = {
        "alerts": [
            {"zone_id": "zone_garage", "timestamp": "2024-01-15T03:00:00Z", "acknowledged": True},
            {"zone_id": "zone_basement", "timestamp": "2024-01-15T04:00:00Z", "acknowledged": True}
        ]
    }
    with open("data/alerts/old_alerts.json", "w") as f:
        json.dump(old_alerts, f, indent=2)

    # 再创建一个空的ops目录（agent应该在里面输出）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
