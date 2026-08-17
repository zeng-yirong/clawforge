import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    details = []
    total_score = 0

    # 1. 目录结构（ops目录是否存在）
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    details.append({
        "item": "ops目录存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops目录存在" if dir_exists else "ops目录不存在"
    })
    if dir_exists:
        total_score += 10

    # 2. 结果文件 ops/resolved_schedule.json 是否存在
    result_path = os.path.join(ops_path, "resolved_schedule.json")
    file_exists = os.path.isfile(result_path)
    details.append({
        "item": "结果文件 resolved_schedule.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })
    if file_exists:
        total_score += 10

    # 3. JSON格式合法性
    if file_exists:
        try:
            data = load_json(result_path)
            json_valid = True
            reason = "JSON格式合法"
        except (json.JSONDecodeError, Exception) as e:
            json_valid = False
            reason = f"JSON解析失败: {str(e)}"
    else:
        json_valid = False
        reason = "文件不存在，无法校验JSON"
    details.append({
        "item": "JSON格式合法",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    if json_valid:
        total_score += 10

    # 4. 包含必要字段 device_id 和 schedule
    if json_valid:
        has_device_id = "device_id" in data
        has_schedule = "schedule" in data
        fields_ok = has_device_id and has_schedule
        reason_parts = []
        if not has_device_id:
            reason_parts.append("缺少device_id字段")
        if not has_schedule:
            reason_parts.append("缺少schedule字段")
        details.append({
            "item": "必要字段 device_id 和 schedule 存在",
            "score": 10 if fields_ok else 0,
            "max_score": 10,
            "passed": fields_ok,
            "reason": "字段齐全" if fields_ok else "; ".join(reason_parts)
        })
        if fields_ok:
            total_score += 10
    else:
        details.append({
            "item": "必要字段存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "JSON无效，跳过"
        })

    # 5. device_id 正确（必须是 ac_lr_001，不能是旧空调或其他）
    if json_valid and "device_id" in data:
        correct_device = data["device_id"] == "ac_lr_001"
        details.append({
            "item": "device_id 为 ac_lr_001（客厅空调）",
            "score": 10 if correct_device else 0,
            "max_score": 10,
            "passed": correct_device,
            "reason": f"device_id = {data['device_id']}" if correct_device else f"错误设备: {data['device_id']}"
        })
        if correct_device:
            total_score += 10
    else:
        details.append({
            "item": "device_id 正确性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "无法校验（字段缺失或JSON无效）"
        })

    # 6. schedule 的合法性：至少包含 start/end/active（或类似结构）
    if json_valid and "schedule" in data:
        sched = data["schedule"]
        # 允许 schedule 是一个对象或列表？按prompt暗示“新时段”，应为一个具体的调度条目。
        # 我们期望是一个对象，包含 start, end 字段。为兼容，支持对象或列表第一个元素。
        if isinstance(sched, dict):
            sched_list = [sched]
        elif isinstance(sched, list) and len(sched) > 0:
            sched_list = sched
        else:
            sched_list = []
        # 检查每个条目是否有 start 和 end 字段
        all_have_time = all("start" in item and "end" in item for item in sched_list)
        if not all_have_time:
            details.append({
                "item": "schedule 包含 start/end 字段",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "缺少start或end字段"
            })
            total_score += 0
        else:
            # 时间格式检查 HH:MM
            import re
            time_pattern = re.compile(r"^\d{2}:\d{2}$")
            times_ok = all(time_pattern.match(item["start"]) and time_pattern.match(item["end"]) for item in sched_list)
            if not times_ok:
                details.append({
                    "item": "schedule 时间格式 HH:MM",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "时间格式不符合 HH:MM"
                })
                total_score += 0
            else:
                details.append({
                    "item": "schedule 结构完整",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "包含start/end且格式正确"
                })
                total_score += 10
    else:
        details.append({
            "item": "schedule 结构完整性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "schedule字段缺失或JSON无效"
        })

    # 7. 核心：冲突解决正确 —— 新时间必须与咖啡机不重叠
    # 咖啡机原有调度 15:00-16:00（我们已知）。空调新时间应调整为 15:30-16:30 或 14:30-15:30？但prompt说“往后调30分钟”，所以应该是开始从15:00变成15:30，结束变为16:30。
    # 唯一正确解：start=15:30, end=16:30。
    if json_valid and "schedule" in data:
        sched = data["schedule"]
        # 类似上面提取
        if isinstance(sched, dict):
            sched_list = [sched]
        elif isinstance(sched, list) and len(sched) > 0:
            sched_list = sched
        else:
            sched_list = []
        if len(sched_list) > 0:
            target = sched_list[0]  # 第一个条目作为目标
            start = target.get("start", "")
            end = target.get("end", "")
            # 期望 start=15:30, end=16:30
            correct = (start == "15:30" and end == "16:30")
            if correct:
                details.append({
                    "item": "冲突解决正确（新时段15:30-16:30，不与咖啡机重叠）",
                    "score": 30,
                    "max_score": 30,
                    "passed": True,
                    "reason": f"start={start}, end={end}"
                })
                total_score += 30
            else:
                details.append({
                    "item": "冲突解决正确",
                    "score": 0,
                    "max_score": 30,
                    "passed": False,
                    "reason": f"期望15:30-16:30，实际{start}-{end}"
                })
        else:
            details.append({
                "item": "冲突解决正确",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": "schedule为空列表"
            })
    else:
        details.append({
            "item": "冲突解决正确",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "JSON无效或schedule缺失"
        })

    # 最终总分 —— 确保不超过100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    main()
