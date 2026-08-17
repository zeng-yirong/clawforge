import sys
import os
import json
import math

def load_json(filepath):
    """安全加载JSON，返回None如果失败"""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def score_workplace(workspace):
    details = []
    total = 0

    # 1. 检查必要的目录存在（10分）
    dirs_ok = all(os.path.isdir(os.path.join(workspace, d)) for d in ['ops', 'data/sensors', 'data/locations', 'data/accounts'])
    dir_score = 10 if dirs_ok else 0
    details.append({
        "item": "目录结构完整性",
        "score": dir_score,
        "max_score": 10,
        "passed": dirs_ok,
        "reason": "需要 ops, data/sensors, data/locations, data/accounts 目录"
    })
    total += dir_score

    # 2. 检查结果文件是否存在（10分）
    result_path = os.path.join(workspace, 'ops/alerts.json')
    result_exists = os.path.isfile(result_path)
    details.append({
        "item": "结果文件 ops/alerts.json 存在",
        "score": 10 if result_exists else 0,
        "max_score": 10,
        "passed": result_exists,
        "reason": "Agent 必须产出 ops/alerts.json"
    })
    total += 10 if result_exists else 0

    if not result_exists:
        # 文件不存在，直接记录总分
        total = 0
        score_data = {"total_score": total, "details": details}
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump(score_data, f, indent=2)
        return

    # 3. 解析结果JSON（10分）
    result_data = load_json(result_path)
    if result_data is None:
        details.append({
            "item": "JSON 合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/alerts.json 不是合法的 JSON"
        })
        total += 0
        score_data = {"total_score": total, "details": details}
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump(score_data, f, indent=2)
        return

    if not isinstance(result_data, list):
        details.append({
            "item": "JSON 应为数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "期望顶层是一个数组"
        })
        total += 0
        score_data = {"total_score": total, "details": details}
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump(score_data, f, indent=2)
        return

    details.append({
        "item": "JSON 格式正确且为数组",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "结果文件是合法的 JSON 数组"
    })
    total += 10

    # 4. 检查字段完整性（20分）—— 每条记录必须包含 sensor_id, account_id, current_value, threshold_high
    required_fields = {'sensor_id', 'account_id', 'current_value', 'threshold_high'}
    field_ok = True
    field_issues = []
    for idx, rec in enumerate(result_data):
        if not isinstance(rec, dict):
            field_ok = False
            field_issues.append(f"第{idx+1}条不是对象")
            continue
        missing = required_fields - set(rec.keys())
        if missing:
            field_ok = False
            field_issues.append(f"第{idx+1}条缺少字段: {missing}")

    field_score = 20 if field_ok else 0
    details.append({
        "item": "记录字段完整性",
        "score": field_score,
        "max_score": 20,
        "passed": field_ok,
        "reason": "每个对象必须包含 sensor_id, account_id, current_value, threshold_high" + (f" 问题: {field_issues}" if field_issues else "")
    })
    total += field_score

    # 5. 计算标准答案（从资源文件推导），并比较记录数（20分）和字段值（30分）
    # 加载主传感器数据
    sensors_path = os.path.join(workspace, 'data/sensors/sensors.json')
    sensors_data = load_json(sensors_path)
    accounts_path = os.path.join(workspace, 'data/accounts/accounts.json')
    accounts_data = load_json(accounts_path)

    if sensors_data is None or accounts_data is None:
        # 资源文件缺失，无法验证
        details.append({
            "item": "资源数据完整性",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "缺失 data/sensors/sensors.json 或 data/accounts/accounts.json"
        })
    else:
        sensors = sensors_data.get('sensors', {})
        accounts = accounts_data.get('accounts', {})

        # 建立 sensor_id -> account_id 映射
        sensor_to_account = {}
        for acc_id, acc in accounts.items():
            for sid in acc.get('sensors', []):
                sensor_to_account[sid] = acc_id

        # 筛选符合条件的传感器：status == active 且 current_value > threshold_high
        expected = []
        for sid, sensor in sensors.items():
            if sensor.get('status') == 'active' and sensor.get('current_value', -math.inf) > sensor.get('threshold_high', math.inf):
                account_id = sensor_to_account.get(sid)
                if account_id is None:
                    continue  # 理论上不应该出现
                expected.append({
                    "sensor_id": sid,
                    "account_id": account_id,
                    "current_value": sensor['current_value'],
                    "threshold_high": sensor['threshold_high']
                })

        # 排序后比较（忽略顺序）
        expected_sorted = sorted(expected, key=lambda x: x['sensor_id'])
        agent_sorted = sorted(result_data, key=lambda x: x.get('sensor_id', ''))
        # 注意 agent 可能缺少字段，我们只比较字段值
        # 先比较记录数
        count_ok = len(agent_sorted) == len(expected_sorted)
        details.append({
            "item": "记录数匹配",
            "score": 20 if count_ok else 0,
            "max_score": 20,
            "passed": count_ok,
            "reason": f"期望 {len(expected_sorted)} 条记录，Agent 给出 {len(agent_sorted)} 条"
        })
        total += 20 if count_ok else 0

        # 比较每个记录的字段值（30分）
        value_ok = count_ok  # 只有数量相等时才逐条比较
        value_reason = ""
        if count_ok:
            for i, (exp, agent) in enumerate(zip(expected_sorted, agent_sorted)):
                # 检查四个关键字段
                match = (exp['sensor_id'] == agent.get('sensor_id') and
                         exp['account_id'] == agent.get('account_id') and
                         exp['current_value'] == agent.get('current_value') and
                         exp['threshold_high'] == agent.get('threshold_high'))
                if not match:
                    value_ok = False
                    value_reason = f"第{i+1}条不匹配：期望 {exp}，得到 {agent}"
                    break
            if value_ok:
                value_reason = "所有记录字段值完全正确"
        else:
            value_reason = "记录数不匹配，跳过字段值检查"

        details.append({
            "item": "记录字段值正确性",
            "score": 30 if value_ok else 0,
            "max_score": 30,
            "passed": value_ok,
            "reason": value_reason
        })
        total += 30 if value_ok else 0

    # 总分写入
    score_data = {
        "total_score": min(total, 100),
        "details": details
    }
    with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
        json.dump(score_data, f, indent=2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_workplace(workspace)

if __name__ == '__main__':
    main()
