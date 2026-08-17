import sys
import json
import os

def verify(workspace):
    results = []
    total_score = 0

    # ================== 1. 目录结构检查 (10分) ==================
    ops_dir = os.path.join(workspace, 'ops')
    data_dir = os.path.join(workspace, 'data')
    data_onboarding = os.path.join(data_dir, 'onboarding')
    ops_exists = os.path.isdir(ops_dir)
    results.append({
        "item": "ops 目录存在",
        "max_score": 5,
        "score": 5 if ops_exists else 0,
        "passed": ops_exists,
        "reason": "ops 目录已创建" if ops_exists else "缺失 ops 目录"
    })
    total_score += 5 if ops_exists else 0

    data_onboarding_exists = os.path.isdir(data_onboarding)
    results.append({
        "item": "data/onboarding 目录存在（环境完整性）",
        "max_score": 5,
        "score": 5 if data_onboarding_exists else 0,
        "passed": data_onboarding_exists,
        "reason": "目录存在" if data_onboarding_exists else "缺失 data/onboarding"
    })
    total_score += 5 if data_onboarding_exists else 0

    # ================== 2. 产物文件存在且合法 JSON (15分) ==================
    result_path = os.path.join(ops_dir, 'onboarding_result.json')
    if not os.path.isfile(result_path):
        results.append({
            "item": "ops/onboarding_result.json 存在",
            "max_score": 15,
            "score": 0,
            "passed": False,
            "reason": "文件不存在"
        })
        total_score += 0
        # 无法继续，剩余项记 0 分
        for item_name, max_s in [("email 字段正确", 20), ("systems 字段正确", 20), ("equipment 字段正确", 20), ("welcome_message 字段正确", 20)]:
            results.append({
                "item": item_name,
                "max_score": max_s,
                "score": 0,
                "passed": False,
                "reason": "结果文件缺失，跳过"
            })
        final = {
            "total_score": total_score,
            "details": results
        }
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump(final, f, indent=2)
        print(json.dumps(final, indent=2))
        return total_score

    try:
        with open(result_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError):
        results.append({
            "item": "ops/onboarding_result.json 合法 JSON",
            "max_score": 15,
            "score": 0,
            "passed": False,
            "reason": "JSON 解析失败"
        })
        total_score += 0
        # 同样终止
        for item_name, max_s in [("email 字段正确", 20), ("systems 字段正确", 20), ("equipment 字段正确", 20), ("welcome_message 字段正确", 20)]:
            results.append({
                "item": item_name,
                "max_score": max_s,
                "score": 0,
                "passed": False,
                "reason": "JSON 解析失败，跳过"
            })
        final = {
            "total_score": total_score,
            "details": results
        }
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump(final, f, indent=2)
        print(json.dumps(final, indent=2))
        return total_score

    results.append({
        "item": "ops/onboarding_result.json 合法 JSON",
        "max_score": 15,
        "score": 15,
        "passed": True,
        "reason": "JSON 解析成功"
    })
    total_score += 15

    # ================== 3. 关键字段验证 (20+20+20+20 = 80分) ==================
    # 预期值（从业务真相推导）
    expected_employee_id = "E2024-089"
    expected_email = "zhang.san@company.com"
    expected_systems = ["git", "jira", "confluence"]  # 注意顺序
    expected_equipment = "LAP-0083"
    # welcome_message 必须包含 "Welcome Zhang San" 且包含 "complete" 或类似
    # 但为了精确，我们要求包含 "Welcome Zhang San" 和 "onboarding is complete" 这一段
    expected_welcome_substrings = ["Welcome Zhang San", "onboarding is complete"]

    # 3.1 employee_id
    emp_id = data.get("employee_id")
    if emp_id == expected_employee_id:
        results.append({
            "item": "employee_id 字段正确",
            "max_score": 20,
            "score": 20,
            "passed": True,
            "reason": f"匹配 {expected_employee_id}"
        })
        total_score += 20
    else:
        results.append({
            "item": "employee_id 字段正确",
            "max_score": 20,
            "score": 0,
            "passed": False,
            "reason": f"期望 {expected_employee_id}，实际 {emp_id}"
        })

    # 3.2 email
    email = data.get("email")
    if email == expected_email:
        results.append({
            "item": "email 字段正确",
            "max_score": 20,
            "score": 20,
            "passed": True,
            "reason": f"匹配 {expected_email}"
        })
        total_score += 20
    else:
        results.append({
            "item": "email 字段正确",
            "max_score": 20,
            "score": 0,
            "passed": False,
            "reason": f"期望 {expected_email}，实际 {email}"
        })

    # 3.3 systems (列表，比较排序后)
    systems = data.get("systems", [])
    if isinstance(systems, list) and sorted(systems) == sorted(expected_systems):
        results.append({
            "item": "systems 字段正确",
            "max_score": 20,
            "score": 20,
            "passed": True,
            "reason": f"匹配 {sorted(expected_systems)}"
        })
        total_score += 20
    else:
        results.append({
            "item": "systems 字段正确",
            "max_score": 20,
            "score": 0,
            "passed": False,
            "reason": f"期望 {expected_systems}，实际 {systems}"
        })

    # 3.4 equipment
    equip = data.get("equipment")
    if equip == expected_equipment:
        results.append({
            "item": "equipment 字段正确",
            "max_score": 20,
            "score": 20,
            "passed": True,
            "reason": f"匹配 {expected_equipment}"
        })
        total_score += 20
    else:
        results.append({
            "item": "equipment 字段正确",
            "max_score": 20,
            "score": 0,
            "passed": False,
            "reason": f"期望 {expected_equipment}，实际 {equip}"
        })

    # 3.5 welcome_message (20分) — 这里因为上面已用满80分，实际需要从总分分配 20 分替代某个？不，我们从上面四个各扣5分？重新分配简单：前4个各15分（合计60），加上前两项20，正好100？调整一下更方便。
    # 重新调整：70分给核心字段，30分给 welcome_message？
    # 已输出按固定结构，我现在修改前面的分数配比：
    # 让 employee_id 15, email 15, systems 15, equipment 15, welcome_message 20
    # 但已经写了。为了简化，我额外增加 welcome_message 检查并作为第5个20分项，总分为 5+5+15+15+15+15+20 = 90？ 不对。
    # 好在我是编写时，可以直接调整上面分数。由于是生成，我重新定义更合理的分布：
    # 先清空之前的 results 重新构建？
    # 最佳：前两个目录10分，json合法性15分，四个核心字段各15分（60），welcome_message 15分，共100。
    # 但为了不重写，我可以在最后加一个 welcome_message 项，最大分数设置为 20，但总分就会变成 5+5+15+20+20+20+20=105，超了。所以必须调整。
    # 我选择重新整理 result 列表，保持逻辑清晰。
    # 由于是脚本，我可以在后面追加一个 welcome_message 项，但之前的分数要减去一些。为了简单，我重新构建 results 列表和总分。
    # 更干净：完全抛弃上面的记录，重写一个函数。但时间有限，我直接修改上面已经写的内容。
    # 快速做法：清空 results，重新按100分分配：
    # 1. ops目录存在：5分
    # 2. data/onboarding 存在：5分
    # 3. 产物JSON合法：10分
    # 4. employee_id 正确：20分
    # 5. email 正确：20分
    # 6. systems 正确：20分
    # 7. equipment 正确：10分
    # 8. welcome_message 正确：10分
    # 总和 100。这样修改：
    # 重新构建 results 列表。
    pass

# 为了确保最终输出正确，我重新编写一个清晰的函数。
def verify_v2(workspace):
    results = []
    total_score = 0

    ops_dir = os.path.join(workspace, 'ops')
    data_onboarding = os.path.join(workspace, 'data', 'onboarding')
    result_path = os.path.join(ops_dir, 'onboarding_result.json')

    # 1. ops目录 (5)
    ops_ok = os.path.isdir(ops_dir)
    results.append({
        "item": "ops 目录存在",
        "max_score": 5,
        "score": 5 if ops_ok else 0,
        "passed": ops_ok,
        "reason": "存在" if ops_ok else "缺失"
    })
    total_score += 5 if ops_ok else 0

    # 2. data/onboarding 存在 (5)
    dob_ok = os.path.isdir(data_onboarding)
    results.append({
        "item": "data/onboarding 目录存在",
        "max_score": 5,
        "score": 5 if dob_ok else 0,
        "passed": dob_ok,
        "reason": "存在" if dob_ok else "缺失"
    })
    total_score += 5 if dob_ok else 0

    # 3. 结果文件存在且合法JSON (10)
    if not os.path.isfile(result_path):
        results.append({
            "item": "ops/onboarding_result.json 存在且为合法 JSON",
            "max_score": 10,
            "score": 0,
            "passed": False,
            "reason": "文件不存在"
        })
        # 其余项0分
        for item, ms in [("employee_id 正确", 20), ("email 正确", 20), ("systems 正确", 20), ("equipment 正确", 10), ("welcome_message 正确", 10)]:
            results.append({
                "item": item,
                "max_score": ms,
                "score": 0,
                "passed": False,
                "reason": "结果文件缺失"
            })
        final = {"total_score": total_score, "details": results}
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump(final, f, indent=2)
        print(json.dumps(final, indent=2))
        return total_score

    try:
        with open(result_path, 'r') as f:
            data = json.load(f)
    except:
        results.append({
            "item": "ops/onboarding_result.json 存在且为合法 JSON",
            "max_score": 10,
            "score": 0,
            "passed": False,
            "reason": "JSON 解析失败"
        })
        for item, ms in [("employee_id 正确", 20), ("email 正确", 20), ("systems 正确", 20), ("equipment 正确", 10), ("welcome_message 正确", 10)]:
            results.append({
                "item": item,
                "max_score": ms,
                "score": 0,
                "passed": False,
                "reason": "JSON 解析失败"
            })
        final = {"total_score": total_score, "details": results}
        with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
            json.dump(final, f, indent=2)
        print(json.dumps(final, indent=2))
        return total_score

    results.append({
        "item": "ops/onboarding_result.json 存在且为合法 JSON",
        "max_score": 10,
        "score": 10,
        "passed": True,
        "reason": "JSON 解析成功"
    })
    total_score += 10

    # 4. employee_id (20)
    emp_id = data.get("employee_id")
    expected_id = "E2024-089"
    if emp_id == expected_id:
        results.append({
            "item": "employee_id 正确",
            "max_score": 20,
            "score": 20,
            "passed": True,
            "reason": f"匹配 {expected_id}"
        })
        total_score += 20
    else:
        results.append({
            "item": "employee_id 正确",
            "max_score": 20,
            "score": 0,
            "passed": False,
            "reason": f"期望 {expected_id}，实际 {emp_id}"
        })

    # 5. email (20)
    email = data.get("email")
    expected_email = "zhang.san@company.com"
    if email == expected_email:
        results.append({
            "item": "email 正确",
            "max_score": 20,
            "score": 20,
            "passed": True,
            "reason": f"匹配 {expected_email}"
        })
        total_score += 20
    else:
        results.append({
            "item": "email 正确",
            "max_score": 20,
            "score": 0,
            "passed": False,
            "reason": f"期望 {expected_email}，实际 {email}"
        })

    # 6. systems (20)
    systems = data.get("systems", [])
    expected_systems = ["git", "jira", "confluence"]
    if isinstance(systems, list) and sorted(systems) == sorted(expected_systems):
        results.append({
            "item": "systems 正确",
            "max_score": 20,
            "score": 20,
            "passed": True,
            "reason": f"匹配 {sorted(expected_systems)}"
        })
        total_score += 20
    else:
        results.append({
            "item": "systems 正确",
            "max_score": 20,
            "score": 0,
            "passed": False,
            "reason": f"期望 {expected_systems}，实际 {systems}"
        })

    # 7. equipment (10)
    equip = data.get("equipment")
    expected_equip = "LAP-0083"
    if equip == expected_equip:
        results.append({
            "item": "equipment 正确",
            "max_score": 10,
            "score": 10,
            "passed": True,
            "reason": f"匹配 {expected_equip}"
        })
        total_score += 10
    else:
        results.append({
            "item": "equipment 正确",
            "max_score": 10,
            "score": 0,
            "passed": False,
            "reason": f"期望 {expected_equip}，实际 {equip}"
        })

    # 8. welcome_message (10)
    msg = data.get("welcome_message", "")
    # 要求至少包含 "Welcome Zhang San" 和 "complete"
    contains_name = "Welcome Zhang San" in msg
    contains_complete = "complete" in msg
    # 额外检查是否包含 "confluence" 等？但简单即可
    if contains_name and contains_complete:
        results.append({
            "item": "welcome_message 正确",
            "max_score": 10,
            "score": 10,
            "passed": True,
            "reason": "消息包含欢迎语和完成标识"
        })
        total_score += 10
    else:
        reason_parts = []
        if not contains_name:
            reason_parts.append("缺少 'Welcome Zhang San'")
        if not contains_complete:
            reason_parts.append("缺少 'complete'")
        results.append({
            "item": "welcome_message 正确",
            "max_score": 10,
            "score": 0,
            "passed": False,
            "reason": "; ".join(reason_parts) if reason_parts else "未提供 welcome_message"
        })

    # 写入评分文件
    final = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
        json.dump(final, f, indent=2)
    print(json.dumps(final, indent=2))
    return total_score


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_v2(workspace)
