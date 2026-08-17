import sys
import os
import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1) 检查 ops 目录存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops/ 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录存在"})
        total_score += 5
    else:
        details.append({"item": "ops/ 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 ops/ 目录"})

    # 2) 检查 fix_schedules.json 存在 (10分)
    target_file = os.path.join(workspace, "ops", "fix_schedules.json")
    if os.path.isfile(target_file):
        details.append({"item": "fix_schedules.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "fix_schedules.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ops/fix_schedules.json"})
        # 后续无法继续，直接写入结果返回
        _write_score(total_score, details)
        return

    # 3) JSON 合法性 (10分)
    try:
        result = load_json(target_file)
        if isinstance(result, list):
            details.append({"item": "JSON 格式正确且为列表", "score": 10, "max_score": 10, "passed": True, "reason": "合法 JSON 列表"})
            total_score += 10
        else:
            details.append({"item": "JSON 格式正确且为列表", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 不是列表"})
            _write_score(total_score, details)
            return
    except Exception as e:
        details.append({"item": "JSON 格式正确且为列表", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        _write_score(total_score, details)
        return

    # 4) 加载原始数据，确定正确答案
    try:
        devices_path = os.path.join(workspace, "data", "devices.json")
        schedules_path = os.path.join(workspace, "data", "schedules.json")
        devices_data = load_json(devices_path)
        schedules_data = load_json(schedules_path)
        devices = devices_data["devices"]
        schedules = schedules_data["schedules"]
    except Exception as e:
        details.append({"item": "原始数据读取", "score": 0, "max_score": 0, "passed": False, "reason": f"无法读取原始数据: {e}"})
        _write_score(total_score, details)
        return

    # 找出所有符合条件（卧室空调、深夜时段、制冷）的调度 ID
    correct_ids = []
    for s in schedules:
        # 查找对应设备
        dev = next((d for d in devices if d["device_id"] == s["device_id"]), None)
        if dev is None:
            continue
        if dev["device_type"] == "ac" and dev["location"] == "bedroom":
            # 深夜时段：start_time == "22:00" and end_time == "06:00"
            if s.get("start_time") == "22:00" and s.get("end_time") == "06:00":
                if s.get("mode") == "cool":
                    correct_ids.append(s["schedule_id"])
    
    expected_count = len(correct_ids)  # 应为1
    # 5) 结果列表长度 (15分)
    if len(result) == expected_count:
        details.append({"item": "结果列表长度正确", "score": 15, "max_score": 15, "passed": True, "reason": f"列表长度为 {expected_count}"})
        total_score += 15
    else:
        details.append({"item": "结果列表长度正确", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 {expected_count} 条，实际 {len(result)} 条"})

    # 6) 检查结果中的每个条目是否正确 (20分，如果长度不对额外扣分这里就不加了)
    # 先检查 schedule_id 是否匹配
    res_ids = set()
    for item in result:
        if "schedule_id" in item:
            res_ids.add(item["schedule_id"])
    
    if expected_count > 0:
        expected_id = correct_ids[0]
        if expected_id in res_ids:
            details.append({"item": "包含正确的 schedule_id", "score": 10, "max_score": 10, "passed": True, "reason": f"包含 {expected_id}"})
            total_score += 10
        else:
            details.append({"item": "包含正确的 schedule_id", "score": 0, "max_score": 10, "passed": False, "reason": f"未找到期望的 schedule_id {expected_id}"})
        
        # 7) mode 改为 heat (10分)
        target_item = next((it for it in result if it.get("schedule_id") == expected_id), None)
        if target_item is not None and target_item.get("mode") == "heat":
            details.append({"item": "mode 正确改为 heat", "score": 10, "max_score": 10, "passed": True, "reason": "mode 为 heat"})
            total_score += 10
        else:
            details.append({"item": "mode 正确改为 heat", "score": 0, "max_score": 10, "passed": False, "reason": "mode 不是 heat 或条目缺失"})
        
        # 8) 其他字段与原始调度一致 (15分)
        # 找到原始调度
        orig_sched = next((s for s in schedules if s["schedule_id"] == expected_id), None)
        if orig_sched is not None and target_item is not None:
            # 检查除 mode 以外的字段
            ignored_keys = {"mode"}  # 只忽略 mode
            all_match = True
            diff_reason = ""
            for k, v in orig_sched.items():
                if k in ignored_keys:
                    continue
                if k not in target_item:
                    all_match = False
                    diff_reason = f"丢失字段 {k}"
                    break
                if target_item[k] != v:
                    all_match = False
                    diff_reason = f"字段 {k} 值不同：期望 {v}，实际 {target_item[k]}"
                    break
            # 检查是否有多余字段（不包括 mode 和必须保留的）
            extra_keys = set(target_item.keys()) - set(orig_sched.keys()) - {"mode"}
            if extra_keys:
                all_match = False
                diff_reason = f"存在多余字段：{extra_keys}"
            if all_match:
                details.append({"item": "其他字段原样保留", "score": 15, "max_score": 15, "passed": True, "reason": "所有字段（除 mode）一致"})
                total_score += 15
            else:
                details.append({"item": "其他字段原样保留", "score": 0, "max_score": 15, "passed": False, "reason": diff_reason})
        else:
            details.append({"item": "其他字段原样保留", "score": 0, "max_score": 15, "passed": False, "reason": "无法比对"})
    else:
        # 没有期望的条目，但代码不该走到这里，因为 expected_count 应该是1
        details.append({"item": "包含正确的 schedule_id", "score": 0, "max_score": 10, "passed": False, "reason": "无期望条目"})
        details.append({"item": "mode 正确改为 heat", "score": 0, "max_score": 10, "passed": False, "reason": "无条目"})
        details.append({"item": "其他字段原样保留", "score": 0, "max_score": 15, "passed": False, "reason": "无条目"})

    # 9) 检查是否混入了不需要修改的条目 (5分)
    allowed_ids = correct_ids
    has_extra = False
    for item in result:
        sid = item.get("schedule_id")
        if sid not in allowed_ids:
            has_extra = True
            break
    if not has_extra:
        details.append({"item": "没有多余条目", "score": 5, "max_score": 5, "passed": True, "reason": "结果只包含需要修改的条目"})
        total_score += 5
    else:
        details.append({"item": "没有多余条目", "score": 0, "max_score": 5, "passed": False, "reason": "包含不应修改的条目"})

    # 10) 额外加分：确保没有修改其他字段（已检查）-> 已经包含在8中，不再重复

    # 写最终分数
    _write_score(total_score, details)

def _write_score(total, details):
    out = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(out, f, indent=2)
    # 打印简要结果（可选）
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    main()
