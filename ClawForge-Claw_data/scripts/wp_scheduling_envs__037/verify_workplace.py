import sys
import json
import os
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # 辅助函数：添加评分项
    def add_item(name, score, max_score, passed, reason=""):
        nonlocal total_score
        total_score += score
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # 1. 文件存在性 (10分)
    target_path = Path(workspace) / "ops" / "auto_off.json"
    if target_path.exists():
        add_item("文件存在性", 10, 10, True, "ops/auto_off.json 存在")
    else:
        add_item("文件存在性", 0, 10, False, "ops/auto_off.json 不存在")
        # 如果文件不存在，直接结束评分
        return {"total_score": 0, "details": details}

    # 2. JSON 合法性 (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        add_item("JSON合法", 10, 10, True, "文件为合法JSON")
    except (json.JSONDecodeError, Exception) as e:
        add_item("JSON合法", 0, 10, False, f"JSON解析失败: {e}")
        return {"total_score": total_score, "details": details}

    # 3. 结果是一个列表 (10分)
    if isinstance(data, list):
        add_item("数据类型是列表", 10, 10, True, "顶层结构是列表")
    else:
        add_item("数据类型是列表", 0, 10, False, f"顶层结构是 {type(data).__name__}，应为列表")
        return {"total_score": total_score, "details": details}

    # 4. 列表长度应为1 (20分)
    if len(data) == 1:
        add_item("列表长度正确", 20, 20, True, f"长度为 {len(data)}")
    else:
        add_item("列表长度正确", 0, 20, False, f"长度为 {len(data)}，预期为1")

    # 5. 每个元素包含 device_id 和 action (10分)
    all_have_fields = True
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            all_have_fields = False
            break
        if "device_id" not in item or "action" not in item:
            all_have_fields = False
            break
    if all_have_fields:
        add_item("字段完整性 (device_id, action)", 10, 10, True, "每个元素均有 device_id 和 action")
    else:
        add_item("字段完整性 (device_id, action)", 0, 10, False, "缺少必要字段或元素不是字典")

    # 6. 具体值: device_id 应为 living_room_ac (20分)
    device_id_ok = True
    for item in data:
        if item.get("device_id") != "living_room_ac":
            device_id_ok = False
            break
    if device_id_ok:
        add_item("device_id 值正确", 20, 20, True, "所有设备ID均为 living_room_ac")
    else:
        add_item("device_id 值正确", 0, 20, False, "存在非预期的 device_id")

    # 7. 具体值: action 应为 turn_off (10分)
    action_ok = True
    for item in data:
        if item.get("action") != "turn_off":
            action_ok = False
            break
    if action_ok:
        add_item("action 值正确", 10, 10, True, "所有动作均为 turn_off")
    else:
        add_item("action 值正确", 0, 10, False, "存在非预期的 action")

    # 8. 无多余字段 (5分)
    extra_fields = False
    for item in data:
        allowed = {"device_id", "action"}
        if set(item.keys()) - allowed:
            extra_fields = True
            break
    if not extra_fields:
        add_item("无多余字段", 5, 5, True, "每个元素仅有 device_id 和 action")
    else:
        add_item("无多余字段", 0, 5, False, "存在多余字段")

    # 9. 无额外设备（长度已检查，但额外检查以确保没有重复或多余）(5分)
    if len(data) == 1:
        add_item("无多余条目", 5, 5, True, "列表只包含必要的条目")
    else:
        add_item("无多余条目", 0, 5, False, f"列表包含 {len(data)} 个条目，应为1")

    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = Path(workspace) / "workplace_score.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
