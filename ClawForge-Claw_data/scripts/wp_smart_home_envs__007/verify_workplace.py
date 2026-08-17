import sys
import json
import os
from pathlib import Path

def main(workspace: str):
    score = 0
    details = []

    # ---------- 1. 文件存在性 (10分) ----------
    target_file = os.path.join(workspace, "ops", "energy_save_targets.json")
    if os.path.isfile(target_file):
        details.append({
            "item": "文件存在性: ops/energy_save_targets.json",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "目标文件存在"
        })
        score += 10
    else:
        details.append({
            "item": "文件存在性: ops/energy_save_targets.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无需执行，直接写结果并退出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # ---------- 2. JSON合法性 (10分) ----------
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON格式合法性",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件可正确解析为JSON"
        })
        score += 10
    except Exception as e:
        details.append({
            "item": "JSON格式合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # ---------- 3. 字段和类型检查 (10分) ----------
    if isinstance(data, dict) and "devices_to_turn_off" in data and isinstance(data["devices_to_turn_off"], list):
        details.append({
            "item": "字段/类型正确: devices_to_turn_off 必须为list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "键存在且值为列表"
        })
        score += 10
    else:
        details.append({
            "item": "字段/类型正确: devices_to_turn_off 必须为list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺失键或类型错误"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    device_list = data["devices_to_turn_off"]
    # 预期关闭的设备（基于已知数据逻辑）
    expected_ids = {"ac_lr", "ac_study", "plug_desk", "plug_floor", "plug_tv"}
    actual_ids = set(device_list)

    # ---------- 4. 列表长度 (10分) ----------
    if len(device_list) == len(expected_ids):
        details.append({
            "item": "列表长度正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"期望长度 {len(expected_ids)}，实际 {len(device_list)}"
        })
        score += 10
    else:
        details.append({
            "item": "列表长度正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望长度 {len(expected_ids)}，实际 {len(device_list)}"
        })

    # ---------- 5. 完全匹配元素 (30分) ----------
    if actual_ids == expected_ids:
        details.append({
            "item": "设备ID完全匹配（无多余、无遗漏）",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"实际集合 {sorted(actual_ids)} 与期望集合一致"
        })
        score += 30
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason_parts = []
        if missing:
            reason_parts.append(f"缺少设备: {sorted(missing)}")
        if extra:
            reason_parts.append(f"额外设备: {sorted(extra)}")
        details.append({
            "item": "设备ID完全匹配（无多余、无遗漏）",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })

    # ---------- 6. 无多余设备 (15分) ----------
    if extra := (actual_ids - expected_ids):
        details.append({
            "item": "无多余设备",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"发现不应关闭的设备: {sorted(extra)}"
        })
    else:
        details.append({
            "item": "无多余设备",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "没有包含不应关闭的设备"
        })
        score += 15

    # ---------- 7. 无遗漏设备 (15分) ----------
    if missing := (expected_ids - actual_ids):
        details.append({
            "item": "无遗漏设备",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"遗漏应关设备: {sorted(missing)}"
        })
    else:
        details.append({
            "item": "无遗漏设备",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "所有应关设备均已包含"
        })
        score += 15

    # 写入分数文件
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    main(workspace)
