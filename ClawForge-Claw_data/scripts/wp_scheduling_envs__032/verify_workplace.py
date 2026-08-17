import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查目录结构 (10分) —— 必须有schedules, logs, ops 和 devices.json, rules.conf
    required_dirs = ["schedules", "logs", "ops"]
    required_files = ["devices.json", "rules.conf"]
    dir_ok = all(os.path.isdir(os.path.join(workspace, d)) for d in required_dirs)
    file_ok = all(os.path.isfile(os.path.join(workspace, f)) for f in required_files)
    if dir_ok and file_ok:
        details.append({"item": "目录结构包含schedules/logs/ops及基础文件", "score": 10, "max_score": 10, "passed": True, "reason": "所有必要目录和文件存在"})
        score += 10
    else:
        missing = [d for d in required_dirs if not os.path.isdir(os.path.join(workspace, d))] + \
                  [f for f in required_files if not os.path.isfile(os.path.join(workspace, f))]
        details.append({"item": "目录结构包含schedules/logs/ops及基础文件", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失: {missing}"})

    # 2. 检查 ops/overrides.json 是否存在 (10分)
    override_path = os.path.join(workspace, "ops", "overrides.json")
    if os.path.isfile(override_path):
        details.append({"item": "ops/overrides.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已生成"})
        score += 10
    else:
        details.append({"item": "ops/overrides.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未找到"})
        # 如果文件不存在，后面不必再检查
        write_score(workspace, score, details)
        return

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(override_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON解析成功", "score": 10, "max_score": 10, "passed": True, "reason": "格式合法"})
        score += 10
    except json.JSONDecodeError as e:
        details.append({"item": "JSON格式", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        write_score(workspace, score, details)
        return

    # 4. 检查内容结构 (10分) —— 必须有一个overrides列表
    if not isinstance(data, dict) or "overrides" not in data:
        details.append({"item": "JSON包含overrides字段", "score": 0, "max_score": 10, "passed": False, "reason": "缺少overrides键或不是对象"})
        write_score(workspace, score, details)
        return
    overrides = data["overrides"]
    if not isinstance(overrides, list) or len(overrides) == 0:
        details.append({"item": "overrides为非空列表", "score": 0, "max_score": 10, "passed": False, "reason": "overrides不是列表或为空"})
        write_score(workspace, score, details)
        return
    details.append({"item": "基本结构正确", "score": 10, "max_score": 10, "passed": True, "reason": "overrides字段存在且为列表"})
    score += 10

    # 5. 精确比对期望的overrides (60分)
    # 期望结果：两个违规调度：
    # sched_002 (周一14:00-15:00 卧室AC，违反规则1) -> 应禁掉或改时间
    # sched_004 (周一09:00-10:00 卧室AC，与加湿器sched_003冲突 06-07不冲突，实际上sched_003是06-07，sched_004是09-10，没有时间重叠，但规则2是“同时运行”，需要检查同房间设备时间段重叠。注意sched_003是humidifier 06-07，sched_004是AC 09-10，并没有重叠。但我们设定的违规2是：我们想要一个AC和humidifier同时段运行的。仔细看，我们设了sched_004是卧室AC 09-10，而humidifier的sched_003是06-07，没有重叠。为了制造重叠，我们应该让humidifier也有一个09-10的调度，或者让AC在06-07运行。但我们在builder中故意留下了一个缺失：没有创建同时段冲突的调度，只有规则2的威胁但实际没有违规。这会导致答案不唯一。我们需要修正builder，使得确实存在一个AC和humidifier同时段运行的调度。重新设计：让sched_003改为卧室humidifier在09:00-10:00运行，以便与sched_004冲突。同时保留sched_003原本的时间作为干扰？不，我们需要唯一性：规则2应检测到：sched_003 (device_003, 09-10) 和 sched_004 (device_002, 09-10) 在同一个卧室中同时运行。所以应该只有这两个违规。另外规则1违规：sched_002 (14:00-15:00) 是单个违规。总共2个。但注意sched_006是humidifier 20-21不冲突。sched_001合法，sched_005禁用。所以期望overrides包含两个项：sched_002和sched_003? 不对，规则2要修改的是同时运行的调度，可能两者都需要修改？根据prompt“找出违规的调度”，可能只针对违规的调度本身，但冲突是两个调度之间的，应该同时处理两个。为简化，我们规定需修改的调度ID为[sched_002, sched_003, sched_004]？但sched_002是规则1，sched_003和sched_004是规则2冲突。但注意规则2：humidifier和AC不能同时运行，那么这两个调度都需要调整，可以禁用一个或错开。为了让答案唯一，我们设定“需要调整的调度”为所有涉及违规的调度ID。这样有3个：sched_002, sched_003, sched_004。但规则1只有sched_002，规则2有两个。所以最终期望overrides数组包含三个元素，每个元素结构如下：
    # {"schedule_id": "sched_002", "action": "reschedule", "new_start": "20:00", "new_end": "21:00"} (改为非高峰)
    # {"schedule_id": "sched_003", "action": "reschedule", "new_start": "11:00", "new_end": "12:00"} (与AC错开)
    # {"schedule_id": "sched_004", "action": "disable"} (也可以禁用，但为了简化我们要求禁用sched_004)
    # 注意：验证时不要求具体action字段，只要schedule_id正确即可？但为了凸显区分度，可以要求包含action且至少禁用或reschedule。但最好固定：我们让所有违规调度都必须出现在列表中。prompt说“找出那些当前正在违反规则的调度”，所以只要ID正确即可。我们简化：只验证ID集合是否匹配。
    # 我们设定期望ID集合：{'sched_002', 'sched_003', 'sched_004'}
    expected_ids = {"sched_002", "sched_003", "sched_004"}
    actual_ids = set()
    for item in overrides:
        if isinstance(item, dict) and "schedule_id" in item:
            actual_ids.add(item["schedule_id"])
    # 也允许overrides包含额外字段，不扣分。但要求包含全部期望ID且不能有多余ID？为了精确，我们要求完全匹配。
    if actual_ids == expected_ids:
        details.append({"item": "overrides包含所有违规调度ID且无多余", "score": 60, "max_score": 60, "passed": True, "reason": f"匹配期望ID: {expected_ids}"})
        score += 60
    elif expected_ids.issubset(actual_ids) and len(actual_ids) <= len(expected_ids) + 1:
        # 部分正确给部分分
        correct_count = len(expected_ids & actual_ids)
        points = int(60 * correct_count / len(expected_ids))
        details.append({"item": "overrides ID部分正确", "score": points, "max_score": 60, "passed": False, "reason": f"期望{expected_ids}, 得到{actual_ids}, 正确{correct_count}个"})
        score += points
    else:
        details.append({"item": "overrides ID匹配", "score": 0, "max_score": 60, "passed": False, "reason": f"期望{expected_ids}, 得到{actual_ids}"})

    write_score(workspace, score, details)

def write_score(workspace, total, details):
    total = min(total, 100)  # 确保不超过100
    score_data = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    main()
