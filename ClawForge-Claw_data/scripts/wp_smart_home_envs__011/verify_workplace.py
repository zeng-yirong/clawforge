import sys
import os
import json
import re

def verify(workspace):
    score = 0
    max_score = 100
    details = []

    # 1. 目录结构 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops 目录已创建"})
        score += 5
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops 目录不存在"})

    # 2. 产物文件存在 (5分)
    report_path = os.path.join(ops_dir, "health_conflict_report.json")
    if os.path.isfile(report_path):
        details.append({"item": "产物文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "health_conflict_report.json 已找到"})
        score += 5
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "health_conflict_report.json 不存在"})
        # 如果文件不存在，后续检查跳过
        return {"total_score": score, "details": details}

    # 3. JSON 格式合法性 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可解析为有效 JSON"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        return {"total_score": score, "details": details}

    # 4. 数据结构：必须是 list (5分)
    if isinstance(data, list):
        details.append({"item": "顶层结构为列表", "score": 5, "max_score": 5, "passed": True, "reason": "数据是列表"})
        score += 5
    else:
        details.append({"item": "顶层结构为列表", "score": 0, "max_score": 5, "passed": False, "reason": f"类型为 {type(data).__name__}，期望 list"})
        # 不对非列表做后续检查
        return {"total_score": score, "details": details}

    conflicts = data

    # 5. 冲突条目数量 (10分)  必须恰好包含两条冲突 (AC-001 和 HUM-001)
    expected_devices = {"AC-001", "HUM-001"}
    actual_devices = set()
    for c in conflicts:
        if "device_id" in c:
            actual_devices.add(c["device_id"])
    if actual_devices == expected_devices:
        details.append({"item": "冲突设备数量与ID正确", "score": 10, "max_score": 10, "passed": True, "reason": f"包含设备 {sorted(expected_devices)}"})
        score += 10
    else:
        details.append({"item": "冲突设备数量与ID正确", "score": 0, "max_score": 10, "passed": False, "reason": f"实际设备 {sorted(actual_devices)}，期望 {sorted(expected_devices)}"})

    # 6. 每条冲突必须包含必要字段 (5分)
    required_fields = {"device_id", "type", "current_setting", "recommended_setting", "reason"}
    all_fields_ok = True
    for i, c in enumerate(conflicts):
        missing = required_fields - set(c.keys())
        if missing:
            all_fields_ok = False
            details.append({"item": f"冲突 {i} 字段完整性", "score": 0, "max_score": 5, "passed": False, "reason": f"缺少字段 {missing}"})
            break
    if all_fields_ok:
        details.append({"item": "每条冲突包含必需字段", "score": 5, "max_score": 5, "passed": True, "reason": "所有冲突均有 device_id, type, current_setting, recommended_setting, reason"})
        score += 5

    # 7. AC-001 冲突具体数值验证 (25分)
    ac_conflict = None
    for c in conflicts:
        if c.get("device_id") == "AC-001":
            ac_conflict = c
            break
    if ac_conflict:
        # 检查 type 为 temperature
        t_ok = ac_conflict.get("type") == "temperature"
        # 检查 current_setting 中的 target_temperature 为 18
        c_temp = ac_conflict.get("current_setting", {}).get("target_temperature")
        c_val_ok = (c_temp == 18)
        # 检查 recommended_setting 中的 target_temperature 在 22-24 之间 (取中值23)
        r_temp = ac_conflict.get("recommended_setting", {}).get("target_temperature")
        r_val_ok = isinstance(r_temp, (int, float)) and 22 <= r_temp <= 24
        # 检查 reason 提到 Jane 的温度偏好
        reason_ok = "Jane" in ac_conflict.get("reason", "") and "22" in ac_conflict.get("reason", "")
        ac_score = sum([t_ok, c_val_ok, r_val_ok, reason_ok]) * 6.25  # 每项 6.25 分
        ac_score = min(int(ac_score), 25)  # 取整
        if ac_score == 25:
            details.append({"item": "AC-001 冲突细节正确", "score": 25, "max_score": 25, "passed": True, "reason": "类型、当前温度18、建议温度22-24、理由提及 Jane 偏好"})
        else:
            details.append({"item": "AC-001 冲突细节正确", "score": ac_score, "max_score": 25, "passed": False, "reason": f"部分错误: type={t_ok}, current temp={c_val_ok}, recommend temp={r_val_ok}, reason mentions Jane={reason_ok}"})
        score += ac_score
    else:
        details.append({"item": "AC-001 冲突细节正确", "score": 0, "max_score": 25, "passed": False, "reason": "未找到 AC-001 冲突条目"})

    # 8. HUM-001 冲突具体数值验证 (30分)
    hum_conflict = None
    for c in conflicts:
        if c.get("device_id") == "HUM-001":
            hum_conflict = c
            break
    if hum_conflict:
        # type 为 humidity
        t_ok = hum_conflict.get("type") == "humidity"
        # current_setting 中 humidity 为 30 或 0（因为关闭）, 我们允许 current_setting.humidity == 30 或 current_setting.mode == "off" 且 humidity 30
        cur = hum_conflict.get("current_setting", {})
        # 检查当前湿度为 30
        c_hum = cur.get("target_humidity") if "target_humidity" in cur else cur.get("humidity")
        c_ok = (c_hum == 30)
        # 检查 recommended_setting 中的 target_humidity 在 40-50 之间
        r_hum = hum_conflict.get("recommended_setting", {})
        r_val = r_hum.get("target_humidity") if "target_humidity" in r_hum else r_hum.get("humidity")
        r_ok = isinstance(r_val, (int, float)) and 40 <= r_val <= 50
        # reason 提到 respiratory 或 humidity 偏好
        reason_ok = ("respiration" in hum_conflict.get("reason", "").lower() or "humidity" in hum_conflict.get("reason", "").lower())
        hum_score = sum([t_ok, c_ok, r_ok, reason_ok]) * 7.5
        hum_score = min(int(hum_score), 30)
        if hum_score == 30:
            details.append({"item": "HUM-001 冲突细节正确", "score": 30, "max_score": 30, "passed": True, "reason": "类型、当前湿度30、建议湿度40-50、理由涉及呼吸道/湿度"})
        else:
            details.append({"item": "HUM-001 冲突细节正确", "score": hum_score, "max_score": 30, "passed": False, "reason": f"部分错误: type={t_ok}, current humidity={c_ok}, recommend humidity={r_ok}, reason mentions health={reason_ok}"})
        score += hum_score
    else:
        details.append({"item": "HUM-001 冲突细节正确", "score": 0, "max_score": 30, "passed": False, "reason": "未找到 HUM-001 冲突条目"})

    # 9. 不得包含其他设备冲突 (5分)
    extra = actual_devices - expected_devices
    if not extra:
        details.append({"item": "无多余设备冲突", "score": 5, "max_score": 5, "passed": True, "reason": "没有报告额外设备"})
        score += 5
    else:
        details.append({"item": "无多余设备冲突", "score": 0, "max_score": 5, "passed": False, "reason": f"多报了设备 {sorted(extra)}"})

    total = min(score, max_score)
    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入评分文件
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
