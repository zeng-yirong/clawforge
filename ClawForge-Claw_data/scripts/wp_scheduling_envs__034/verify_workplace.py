"""
验证 agent 产出的 repair_plan.json 是否准确。
评分项：
1. 目标文件是否存在 (10分)
2. JSON 格式合法 (10分)
3. 内容结构正确（列表，每个元素有 device_id, action, reason）(10分)
4. 正确过滤干扰（只包含空调，只包含高峰时段内为 on 的调度）(40分)
5. 设备列表无重复、排序正确 (30分)
总分100。
"""
import sys, os, json

def time_to_minutes(t: str) -> int:
    """将 'HH:MM' 转换为分钟数，若格式错误返回 -1。"""
    try:
        h, m = map(int, t.split(':'))
        return h * 60 + m
    except:
        return -1

def verify(workspace: str):
    score_details = []
    total = 0

    # ---------- 1. 目标文件是否存在 ----------
    target_path = os.path.join(workspace, "repair_plan.json")
    exists = os.path.isfile(target_path)
    score_details.append({
        "item": "目标文件 repair_plan.json 存在",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "文件存在" if exists else "文件不存在"
    })
    if not exists:
        # 文件不存在，后续检查无法进行，直接结束
        total = 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    # ---------- 2. JSON 格式合法 ----------
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        valid_json = True
        score_details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
    except Exception as e:
        valid_json = False
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    # ---------- 3. 内容结构正确 ----------
    if not isinstance(data, list):
        score_details.append({
            "item": "内容是列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "顶层应为 JSON 数组"
        })
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    structural_errors = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            structural_errors.append(f"第{i}个元素不是对象")
            continue
        for field in ["device_id", "action", "reason"]:
            if field not in entry:
                structural_errors.append(f"第{i}个元素缺少字段 {field}")
    if structural_errors:
        score_details.append({
            "item": "内容结构正确（字段齐全）",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "; ".join(structural_errors)
        })
    else:
        score_details.append({
            "item": "内容结构正确（字段齐全）",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有元素包含 device_id, action, reason"
        })

    # ---------- 4. 正确过滤干扰 ----------
    # 加载原始数据（由 env_builder 生成，但也可以直接在工作区读取以避免依赖）
    accounts_path = os.path.join(workspace, "data/accounts.json")
    devices_path = os.path.join(workspace, "data/devices/devices.json")
    try:
        with open(accounts_path) as f:
            accounts_data = json.load(f)
        with open(devices_path) as f:
            devices_data = json.load(f)
    except Exception as e:
        # 如果原始数据缺失则扣全分
        score_details.append({
            "item": "过滤干扰（依赖原始数据）",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": f"无法读取原始数据文件: {str(e)}"
        })
        total = sum(d["score"] for d in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    # 构建空调设备ID集合
    ac_device_ids = {d["device_id"] for d in devices_data["devices"] if d["device_type"] == "ac"}

    # 解析有效调度：时间格式正确且在高峰时段内 (17:00-21:00) 且 action == "on"
    peak_start = time_to_minutes("17:00")
    peak_end = time_to_minutes("21:00")
    valid_schedules = set()
    for acc in accounts_data["accounts"]:
        for sch in acc["schedules"]:
            t_start = time_to_minutes(sch.get("start_time", ""))
            t_end = time_to_minutes(sch.get("end_time", ""))
            if t_start == -1 or t_end == -1:
                continue
            if t_start >= peak_start and t_end <= peak_end:
                # 必须完全落在高峰内？我们定义为只要开始时间在高峰内（含端点）且动作是on
                # 这里要求 start >= peak_start 且 start < peak_end (21:00) 并且 end > start
                if t_start >= peak_start and t_start < peak_end and sch.get("action") == "on":
                    if sch["device_id"] in ac_device_ids:
                        valid_schedules.add(sch["device_id"])
    # 注意：一个设备可能有多条有效调度，但只需出现一次
    expected_device_ids = sorted(valid_schedules)

    # 提取 agent 输出中的 device_id 并去重排序
    output_device_ids = sorted(set(entry.get("device_id") for entry in data if isinstance(entry, dict)))

    # 检查是否有多余设备（非空调或不在高峰内）
    extra = set(output_device_ids) - set(expected_device_ids)
    missing = set(expected_device_ids) - set(output_device_ids)
    filter_errors = []
    if extra:
        filter_errors.append(f"包含多余设备: {sorted(extra)}")
    if missing:
        filter_errors.append(f"缺失设备: {sorted(missing)}")
    # 也检查 action 是否正确
    for entry in data:
        if isinstance(entry, dict) and entry.get("device_id") in expected_device_ids:
            if entry.get("action") != "off":
                filter_errors.append(f"设备 {entry['device_id']} 的 action 应为 'off'，实际为 '{entry.get('action')}'")

    if filter_errors:
        score_details.append({
            "item": "正确过滤干扰（只包含空调+高峰on）",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "; ".join(filter_errors)
        })
    else:
        score_details.append({
            "item": "正确过滤干扰（只包含空调+高峰on）",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": f"正确筛选出设备: {expected_device_ids}"
        })

    # ---------- 5. 设备列表无重复、排序正确 ----------
    # 检查是否重复
    ids_in_output = [entry.get("device_id") for entry in data if isinstance(entry, dict)]
    if len(ids_in_output) != len(set(ids_in_output)):
        dup_score = 0
        dup_reason = "存在重复设备ID"
    else:
        dup_score = 15
        dup_reason = "无重复"
    # 检查排序（按device_id字母序）
    sorted_output = sorted(ids_in_output)
    if ids_in_output != sorted_output:
        sort_score = 0
        sort_reason = f"顺序应为 {sorted_output}，实际为 {ids_in_output}"
    else:
        sort_score = 15
        sort_reason = "排序正确"

    score_details.append({
        "item": "设备列表无重复",
        "score": dup_score,
        "max_score": 15,
        "passed": dup_score == 15,
        "reason": dup_reason
    })
    score_details.append({
        "item": "设备列表排序正确（字母序）",
        "score": sort_score,
        "max_score": 15,
        "passed": sort_score == 15,
        "reason": sort_reason
    })

    total = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": score_details}, f)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
