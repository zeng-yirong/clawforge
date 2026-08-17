import json
import csv
import os
import sys
import re
import math
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # === 1. 目录结构检查 (10分) ===
    required_dirs = ["ops"]
    required_files = ["ops/optimal_schedule.json"]
    dir_ok = all(os.path.isdir(os.path.join(workspace, d)) for d in required_dirs)
    file_ok = all(os.path.isfile(os.path.join(workspace, f)) for f in required_files)
    if dir_ok and file_ok:
        details.append({"item": "目录和产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 目录和 optimal_schedule.json 均存在"})
        total_score += 10
    else:
        missing = [f for f in required_files if not os.path.isfile(os.path.join(workspace, f))]
        details.append({"item": "目录和产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少文件: {missing}"})
        total_score += 0

    if not os.path.isfile(os.path.join(workspace, "ops/optimal_schedule.json")):
        return {"total_score": total_score, "details": details}

    # === 2. JSON 合法性 (20分) ===
    try:
        with open(os.path.join(workspace, "ops/optimal_schedule.json"), "r") as f:
            schedule = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        details.append({"item": "JSON 合法可解析", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON解析失败: {e}"})
        return {"total_score": total_score, "details": details}

    if not isinstance(schedule, list):
        details.append({"item": "JSON 合法可解析", "score": 0, "max_score": 20, "passed": False, "reason": "根元素应为列表"})
        return {"total_score": total_score, "details": details}

    details.append({"item": "JSON 合法可解析", "score": 20, "max_score": 20, "passed": True, "reason": "根列表，可解析"})
    total_score += 20

    # === 3. 关键设备存在性及结构 (20分，每个关键项5分) ===
    expected_devices = {"ac_bedroom", "ac_living", "humidifier_bedroom", "plug_desk", "plug_floor_lamp", "plug_tv"}
    found_devices = set()
    for entry in schedule:
        if isinstance(entry, dict) and "device_id" in entry and "schedule" in entry:
            found_devices.add(entry["device_id"])
    if expected_devices == found_devices:
        details.append({"item": "所有正常设备均有调度条目", "score": 10, "max_score": 10, "passed": True, "reason": "包含6个设备"})
        total_score += 10
    else:
        missing_dev = expected_devices - found_devices
        extra_dev = found_devices - expected_devices
        reason = f"缺少设备: {missing_dev}; 多余设备: {extra_dev}"
        details.append({"item": "所有正常设备均有调度条目", "score": 0, "max_score": 10, "passed": False, "reason": reason})
        total_score += 0

    # 检查每个条目是否包含必要字段
    field_ok = True
    for entry in schedule:
        if not all(k in entry for k in ["device_id", "schedule"]):
            field_ok = False
            break
        if not isinstance(entry["schedule"], list):
            field_ok = False
            break
        for slot in entry["schedule"]:
            if not all(k in slot for k in ["start_hour", "end_hour", "action"]):
                field_ok = False
                break
    if field_ok:
        details.append({"item": "所有条目含必需字段 (device_id, schedule, start_hour, end_hour, action)", "score": 10, "max_score": 10, "passed": True, "reason": "字段齐全"})
        total_score += 10
    else:
        details.append({"item": "所有条目含必需字段", "score": 0, "max_score": 10, "passed": False, "reason": "存在缺少字段的条目"})
        total_score += 0

    # === 4. 核心计算精确性 (50分) ===
    # 根据业务逻辑：Jane 有呼吸问题，需要湿度40-50%，温度22-24°C。
    # 电价高峰10-14点 0.35/kwh，peak 18-22点0.25，其他低。
    # 天气温度28-32°C，湿度58-70% => 需要空调制冷和除湿。
    # 最优策略：高峰时段关闭卧室和客厅空调，其他时段开启；加湿器在高湿时段（湿度>50%）应关闭或除湿，但加湿器只能加湿不能除湿，所以需要依赖空调除湿（空调制冷可除湿）。
    # 智能插头：书房电脑桌应该在办公室时间关闭以省电；落地灯和电视只在用户在家时段开启（晚上）。
    # 但题目只要求精确验证，我们设定唯一答案如下（手动计算后的合理策略）：
    # 空调：高峰10-14关闭，其他时间开启（6-10,14-18,18-22）
    # 加湿器：湿度>50%所以关闭（因为室外湿度高，室内需要除湿，加湿器无用）
    # 智能插头：plug_desk在9-18开（工作），其他关；plug_floor_lamp 18-22开；plug_tv 14-16开（下午看电视）。
    # 但注意Jane的睡眠23:00-7:00，夜间可关闭一切。
    # 我们设计答案使验证唯一。
    # 为了方便，答案硬编码为：

    correct_schedule = [
        {
            "device_id": "ac_bedroom",
            "schedule": [
                {"start_hour": 6, "end_hour": 10, "action": {"mode": "cool", "temperature": 22, "power": 1500}},
                {"start_hour": 10, "end_hour": 14, "action": {"power": 0}},   # 关闭
                {"start_hour": 14, "end_hour": 18, "action": {"mode": "cool", "temperature": 22, "power": 1500}},
                {"start_hour": 18, "end_hour": 22, "action": {"mode": "cool", "temperature": 22, "power": 1500}},
                {"start_hour": 22, "end_hour": 6, "action": {"power": 0}},    # 睡眠关闭
            ]
        },
        {
            "device_id": "ac_living",
            "schedule": [
                {"start_hour": 6, "end_hour": 10, "action": {"mode": "cool", "temperature": 24, "power": 2000}},
                {"start_hour": 10, "end_hour": 14, "action": {"power": 0}},
                {"start_hour": 14, "end_hour": 18, "action": {"mode": "cool", "temperature": 24, "power": 2000}},
                {"start_hour": 18, "end_hour": 22, "action": {"mode": "cool", "temperature": 24, "power": 2000}},
                {"start_hour": 22, "end_hour": 6, "action": {"power": 0}},
            ]
        },
        {
            "device_id": "humidifier_bedroom",
            "schedule": [
                {"start_hour": 0, "end_hour": 24, "action": {"power": 0}}   # 完全关闭因为湿度高
            ]
        },
        {
            "device_id": "plug_desk",
            "schedule": [
                {"start_hour": 9, "end_hour": 18, "action": {"power": 600}},
                {"start_hour": 0, "end_hour": 9, "action": {"power": 0}},
                {"start_hour": 18, "end_hour": 24, "action": {"power": 0}}
            ]
        },
        {
            "device_id": "plug_floor_lamp",
            "schedule": [
                {"start_hour": 18, "end_hour": 22, "action": {"power": 100}},
                {"start_hour": 0, "end_hour": 18, "action": {"power": 0}},
                {"start_hour": 22, "end_hour": 24, "action": {"power": 0}}
            ]
        },
        {
            "device_id": "plug_tv",
            "schedule": [
                {"start_hour": 14, "end_hour": 16, "action": {"power": 200}},
                {"start_hour": 0, "end_hour": 14, "action": {"power": 0}},
                {"start_hour": 16, "end_hour": 24, "action": {"power": 0}}
            ]
        }
    ]

    # 比较逻辑：忽略顺序，使用设备ID映射
    # 注意：允许 schedule 中时段顺序不同，但需合并检查
    # 我们简化：对每个设备，验证 action 的合并时段是否一致
    # 但更严谨：我们可以将 schedule 展平成 (device_id, hour, action) 的集合，但 agent 可能写为区间。
    # 我们要求区间的起止时间和功率完全匹配（允许不同顺序）。
    # 为了可操作性，我们只检查每个设备的action大致正确：比如 ac_bedroom 在10-14点 power=0，其他时段为正。
    # 但这样可能模糊。我们设计精确匹配：将正确的schedule列表排序后逐条比较。
    # 由于两个列表顺序可能不同，我们构建字典: device_id -> set of (start_hour, end_hour, power)
    def normalize_schedule(dev_schedule):
        # 将每个条目转换为元组集合
        normalized = {}
        for entry in dev_schedule:
            did = entry["device_id"]
            slots = []
            for s in entry["schedule"]:
                power = s["action"].get("power", 0)
                slots.append((s["start_hour"], s["end_hour"], power))
            normalized[did] = frozenset(slots)
        return normalized

    correct_norm = normalize_schedule(correct_schedule)
    agent_norm = normalize_schedule(schedule)

    # 检查每个设备
    all_correct = True
    for did in correct_norm:
        if did not in agent_norm:
            all_correct = False
            break
        if correct_norm[did] != agent_norm[did]:
            all_correct = False
            break
    # 检查agent是否有额外设备（不应有，但已在前面的检查中扣分）
    extra_devices = set(agent_norm.keys()) - set(correct_norm.keys())
    if extra_devices:
        all_correct = False

    if all_correct:
        details.append({"item": "调度内容精确匹配唯一答案", "score": 50, "max_score": 50, "passed": True, "reason": "所有设备时段与功率完全正确"})
        total_score += 50
    else:
        details.append({"item": "调度内容精确匹配唯一答案", "score": 0, "max_score": 50, "passed": False, "reason": "与预期答案不一致（设备或时段功率有偏差）"})
        # 可以补充具体差异，但为了简洁不展开
        total_score += 0

    # 最终总分限制在100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
