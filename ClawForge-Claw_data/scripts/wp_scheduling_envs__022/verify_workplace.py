import sys, os, json

def verify(workspace):
    score = 0
    details = []
    ws = workspace if workspace else "."

    # 1. ops目录存在 (3分)
    ops_path = os.path.join(ws, "ops")
    if os.path.isdir(ops_path):
        details.append({"item": "ops directory exists", "score": 3, "max_score": 3, "passed": True, "reason": "ops/ found"})
        score += 3
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 3, "passed": False, "reason": "ops/ missing"})

    pending_path = os.path.join(ops_path, "pending_tasks.json")
    # 2. pending_tasks.json存在 (3分)
    if os.path.isfile(pending_path):
        details.append({"item": "pending_tasks.json exists", "score": 3, "max_score": 3, "passed": True, "reason": "file exists"})
        score += 3
    else:
        details.append({"item": "pending_tasks.json exists", "score": 0, "max_score": 3, "passed": False, "reason": "file not found"})
        # 无法继续，输出结果
        total_score = score
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(ws, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. JSON解析成功 (3分)
    try:
        with open(pending_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON parse successful", "score": 3, "max_score": 3, "passed": True, "reason": "valid JSON"})
        score += 3
    except Exception as e:
        details.append({"item": "JSON parse successful", "score": 0, "max_score": 3, "passed": False, "reason": str(e)})
        total_score = score
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(ws, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 数据是列表 (3分)
    if isinstance(data, list):
        details.append({"item": "data is a list", "score": 3, "max_score": 3, "passed": True, "reason": "list type"})
        score += 3
    else:
        details.append({"item": "data is a list", "score": 0, "max_score": 3, "passed": False, "reason": f"got {type(data).__name__}"})
        total_score = score
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(ws, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 5. 列表长度等于2 (8分)
    if len(data) == 2:
        details.append({"item": "exactly 2 pending tasks", "score": 8, "max_score": 8, "passed": True, "reason": "count 2"})
        score += 8
    else:
        details.append({"item": "exactly 2 pending tasks", "score": 0, "max_score": 8, "passed": False, "reason": f"found {len(data)} tasks"})

    # 构建辅助字典
    data_dict = {}
    for task in data:
        sid = task.get("schedule_id")
        data_dict[sid] = task

    # 检查 s002 (共 3+8+6+6=23分)
    s002_detail = {"schedule_id": "s002", "device_id": "humidifier_001", "action": "turn_on", "planned_time": "2025-04-05T21:00"}
    s002_score = 0
    s002_passed = []
    # 6. s002记录存在 (3分)
    if "s002" in data_dict:
        details.append({"item": "schedule s002 present", "score": 3, "max_score": 3, "passed": True, "reason": "found"})
        score += 3
        s002_score += 3
        s002_passed.append(True)
        t = data_dict["s002"]
        # 7. device_id正确 (8分)
        if t.get("device_id") == s002_detail["device_id"]:
            details.append({"item": "s002 device_id correct", "score": 8, "max_score": 8, "passed": True, "reason": "humidifier_001"})
            score += 8
            s002_score += 8
            s002_passed.append(True)
        else:
            details.append({"item": "s002 device_id correct", "score": 0, "max_score": 8, "passed": False, "reason": f"got {t.get('device_id')}"})
            s002_passed.append(False)
        # 8. action正确 (6分)
        if t.get("action") == s002_detail["action"]:
            details.append({"item": "s002 action correct", "score": 6, "max_score": 6, "passed": True, "reason": "turn_on"})
            score += 6
            s002_score += 6
            s002_passed.append(True)
        else:
            details.append({"item": "s002 action correct", "score": 0, "max_score": 6, "passed": False, "reason": f"got {t.get('action')}"})
            s002_passed.append(False)
        # 9. planned_time正确 (6分)
        if t.get("planned_time") == s002_detail["planned_time"]:
            details.append({"item": "s002 planned_time correct", "score": 6, "max_score": 6, "passed": True, "reason": "2025-04-05T21:00"})
            score += 6
            s002_score += 6
            s002_passed.append(True)
        else:
            details.append({"item": "s002 planned_time correct", "score": 0, "max_score": 6, "passed": False, "reason": f"got {t.get('planned_time')}"})
            s002_passed.append(False)
    else:
        details.append({"item": "schedule s002 present", "score": 0, "max_score": 3, "passed": False, "reason": "missing"})
        # 缺失则跳过后续子项，但依然记录未通过
        for sub in ["s002 device_id correct", "s002 action correct", "s002 planned_time correct"]:
            details.append({"item": sub, "score": 0, "max_score": (8 if "device" in sub else 6), "passed": False, "reason": "s002 not present"})

    # 检查 s004 (同样 23分)
    s004_detail = {"schedule_id": "s004", "device_id": "plug_001", "action": "turn_off", "planned_time": "2025-04-04T20:00"}
    if "s004" in data_dict:
        details.append({"item": "schedule s004 present", "score": 3, "max_score": 3, "passed": True, "reason": "found"})
        score += 3
        t = data_dict["s004"]
        if t.get("device_id") == s004_detail["device_id"]:
            details.append({"item": "s004 device_id correct", "score": 8, "max_score": 8, "passed": True, "reason": "plug_001"})
            score += 8
        else:
            details.append({"item": "s004 device_id correct", "score": 0, "max_score": 8, "passed": False, "reason": f"got {t.get('device_id')}"})
        if t.get("action") == s004_detail["action"]:
            details.append({"item": "s004 action correct", "score": 6, "max_score": 6, "passed": True, "reason": "turn_off"})
            score += 6
        else:
            details.append({"item": "s004 action correct", "score": 0, "max_score": 6, "passed": False, "reason": f"got {t.get('action')}"})
        if t.get("planned_time") == s004_detail["planned_time"]:
            details.append({"item": "s004 planned_time correct", "score": 6, "max_score": 6, "passed": True, "reason": "2025-04-04T20:00"})
            score += 6
        else:
            details.append({"item": "s004 planned_time correct", "score": 0, "max_score": 6, "passed": False, "reason": f"got {t.get('planned_time')}"})
    else:
        details.append({"item": "schedule s004 present", "score": 0, "max_score": 3, "passed": False, "reason": "missing"})
        for sub in ["s004 device_id correct", "s004 action correct", "s004 planned_time correct"]:
            details.append({"item": sub, "score": 0, "max_score": (8 if "device" in sub else 6), "passed": False, "reason": "s004 not present"})

    # 10. 无多余调度ID (10分)
    extra_ids = [sid for sid in data_dict if sid not in ["s002", "s004"]]
    if not extra_ids:
        details.append({"item": "no extra schedule IDs", "score": 10, "max_score": 10, "passed": True, "reason": "only s002, s004"})
        score += 10
    else:
        details.append({"item": "no extra schedule IDs", "score": 0, "max_score": 10, "passed": False, "reason": f"unexpected: {extra_ids}"})

    # 11. 所有任务包含必要字段 (8分)
    required_keys = {"schedule_id", "device_id", "action", "planned_time"}
    all_have = all(required_keys.issubset(task.keys()) for task in data)
    if all_have:
        details.append({"item": "all tasks have required fields", "score": 8, "max_score": 8, "passed": True, "reason": "schedule_id,device_id,action,planned_time"})
        score += 8
    else:
        details.append({"item": "all tasks have required fields", "score": 0, "max_score": 8, "passed": False, "reason": "missing some fields"})

    # 12. 所有 device_id 在设备清单中存在 (10分)
    devices_path = os.path.join(ws, "data", "devices.json")
    valid_device_ids = set()
    if os.path.isfile(devices_path):
        try:
            with open(devices_path, "r") as f:
                dev_list = json.load(f)
            valid_device_ids = {d["device_id"] for d in dev_list}
        except:
            pass
    dev_ok = all(task.get("device_id") in valid_device_ids for task in data)
    if dev_ok:
        details.append({"item": "all device_ids exist in devices.json", "score": 10, "max_score": 10, "passed": True, "reason": "valid devices"})
        score += 10
    else:
        details.append({"item": "all device_ids exist in devices.json", "score": 0, "max_score": 10, "passed": False, "reason": "invalid device_id found"})

    # 13. 额外 bonus: 每个任务包含 reason 字段 (6分)
    has_reason = all("reason" in task for task in data)
    if has_reason:
        details.append({"item": "reason field present (bonus)", "score": 6, "max_score": 6, "passed": True, "reason": "bonus"})
        score += 6

    total_score = min(score, 100)
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(ws, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
