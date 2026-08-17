import json
import os
import sys

def score_workplace(workspace):
    details = []
    total = 0
    max_total = 100

    # 1. 目录结构检查（10分）
    # 检查 ops 目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops 目录存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops 目录已创建"
        })
        total += 5
    else:
        details.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "缺少 ops 目录"
        })

    # 检查 data/sensors/sensors.json 是否存在（确保 agent 工作区正确）
    sensors_path = os.path.join(workspace, "data", "sensors", "sensors.json")
    if os.path.isfile(sensors_path):
        details.append({
            "item": "原始数据文件存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "data/sensors/sensors.json 可读"
        })
        total += 5
    else:
        details.append({
            "item": "原始数据文件存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "数据文件丢失，无法验证"
        })
        # 后续检查无法进行，直接返回
        details.append({"item": "结果文件合法性", "score": 0, "max_score": 10, "passed": False, "reason": "依赖的数据文件缺失"})
        details.append({"item": "结果文件数值正确性", "score": 0, "max_score": 75, "passed": False, "reason": "依赖的数据文件缺失"})
        total_score = total
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        sys.exit(0)

    # 2. 产物文件 ops/alarm_sensors.json 合法性（10分）
    alarm_path = os.path.join(ops_dir, "alarm_sensors.json")
    alarm_passed = False
    alarm_content = None
    if not os.path.isfile(alarm_path):
        details.append({
            "item": "结果文件 ops/alarm_sensors.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未生成"
        })
        # 跳过后续数值检查
        details.append({"item": "结果文件数值正确性", "score": 0, "max_score": 75, "passed": False, "reason": "结果文件不存在"})
        total_score = total
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        sys.exit(0)

    try:
        with open(alarm_path, "r") as f:
            alarm_content = json.load(f)
        # 必须是列表，且元素为字符串
        if not isinstance(alarm_content, list):
            raise ValueError("根元素不是列表")
        for elem in alarm_content:
            if not isinstance(elem, str):
                raise ValueError("列表元素不是字符串")
        details.append({
            "item": "结果文件格式合法且为 sensor_id 列表",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"JSON 列表，包含 {len(alarm_content)} 个元素"
        })
        total += 10
    except Exception as e:
        details.append({
            "item": "结果文件格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        # 仍然可以尝试继续，但数值检查可能无法进行
        alarm_content = []  # 设置为空

    # 3. 数值正确性（75分）
    # 从原始数据中计算正确结果
    true_alarm_ids = set()
    try:
        with open(sensors_path, "r") as f:
            raw = json.load(f)
        sensor_list = raw.get("sensors", [])
        for s in sensor_list:
            # 必须包含必要字段：sensor_id, status, threshold_high, current_value, threshold_low 可选
            if not isinstance(s, dict):
                continue
            sid = s.get("sensor_id")
            status = s.get("status")
            thresh_high = s.get("threshold_high")
            curr_val = s.get("current_value")
            # 字段必须存在且类型正确
            if not isinstance(sid, str) or not isinstance(status, str) or not isinstance(thresh_high, (int, float)) \
                    or not isinstance(curr_val, (int, float)):
                continue
            if status == "active" and curr_val > thresh_high:
                true_alarm_ids.add(sid)
    except Exception as e:
        details.append({
            "item": "原始数据解析",
            "score": 0,
            "max_score": 75,
            "passed": False,
            "reason": f"读取 sensors.json 失败: {str(e)}"
        })
        total_score = total
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        sys.exit(0)

    # 根据我们的 env_builder 构造，正确答案应为：
    # sensor_temp_01 (active, 34.5 > 28.0)  -> 包含
    # sensor_temp_02 (active, 27.2 > 30.0? 27.2 < 30, 不包含)
    # sensor_temp_03 (inactive, 不包含)
    # sensor_hum_01 (active, 45.0 > 70.0? 45<70, 不包含)
    # sensor_energy_01 (active, 95.2 > 80.0) -> 包含
    # sensor_bad_01 缺失 threshold_high (None) -> 跳过
    # sensor_temp_04 缺少 threshold_high (字段名错误) -> 跳过
    # sensor_hum_02 缺少 status -> 跳过
    # 所以正确集合为 {'sensor_temp_01', 'sensor_energy_01'}
    agent_ids = set(alarm_content) if alarm_content else set()
    correct_ids = true_alarm_ids  # 由程序计算确保一致

    # 检查是否完全一致（顺序无关）
    if agent_ids == correct_ids:
        details.append({
            "item": "报警传感器 ID 完全正确",
            "score": 75,
            "max_score": 75,
            "passed": True,
            "reason": f"包含正确 ID: {sorted(correct_ids)}"
        })
        total += 75
    else:
        # 部分匹配或完全不匹配
        missing = correct_ids - agent_ids
        extra = agent_ids - correct_ids
        score = 0
        reason_parts = []
        if not missing and extra:
            score = 30
            reason_parts.append(f"多出了不应包含的 ID: {sorted(extra)}")
        elif missing and not extra:
            score = 30
            reason_parts.append(f"缺少必要 ID: {sorted(missing)}")
        elif missing and extra:
            # 错漏各半
            score = 15
            reason_parts.append(f"缺少 {sorted(missing)}，多出 {sorted(extra)}")
        else:
            # 两者均为空，扣分
            reason_parts.append("结果列表为空，而正确答案非空")
        details.append({
            "item": "报警传感器 ID 正确性",
            "score": score,
            "max_score": 75,
            "passed": score >= 75,
            "reason": "; ".join(reason_parts) if reason_parts else "ID 不匹配"
        })
        total += score

    # 写入最终得分
    total_score = total
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_workplace(workspace)
