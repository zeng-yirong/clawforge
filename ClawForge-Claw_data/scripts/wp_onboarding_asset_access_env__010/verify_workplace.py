import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1) 检查文件是否存在
    target_file = os.path.join(workspace, "onboarding_actions.json")
    if os.path.isfile(target_file):
        details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "onboarding_actions.json 存在"})
        score += 10
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续检查无法进行，直接结束
        _write_score(workspace, score, details)
        return

    # 2) 读取并验证 JSON 合法性
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("期望顶层为 list")
        details.append({"item": "JSON 格式合法且为列表", "score": 10, "max_score": 10, "passed": True, "reason": "格式正确"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法且为列表", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        _write_score(workspace, score, details)
        return

    # 3) 检查是否包含恰好3个员工记录 (E001, E002, E004)
    emp_ids = {item.get("employee_id") for item in data if isinstance(item, dict)}
    expected_ids = {"E001", "E002", "E004"}
    extra = emp_ids - expected_ids
    missing = expected_ids - emp_ids
    if not extra and not missing:
        details.append({"item": "员工 ID 正确", "score": 10, "max_score": 10, "passed": True, "reason": "包含 E001, E002, E004 且无多余"})
        score += 10
    else:
        reason = "多出ID: " + ", ".join(sorted(extra)) if extra else ""
        if missing:
            reason += (" ; " if reason else "") + "缺失ID: " + ", ".join(sorted(missing))
        details.append({"item": "员工 ID 正确", "score": 0, "max_score": 10, "passed": False, "reason": reason})
        # 仍可继续检查已有记录

    # 4) 检查每个员工的 actions（顺序不限，但内容需完全匹配预期）
    expected_actions = {
        "E001": [
            {"type": "assign_system_access", "pack_id": "pack_engineering", "systems": ["crm", "erp", "git"]},
            {"type": "allocate_equipment", "asset_tags": ["LAPTOP-E001", "MONITOR-E001"]},
            {"type": "post_welcome_message", "to": "alice@example.com", "channel": "general"}
        ],
        "E002": [
            {"type": "create_email_profile", "email": "bob@example.com", "display_name": "Bob Li"},
            {"type": "assign_system_access", "pack_id": "pack_engineering", "systems": ["crm", "erp", "git"]},
            {"type": "allocate_equipment", "asset_tags": ["LAPTOP-E002", "MONITOR-E002"]},
            {"type": "post_welcome_message", "to": "bob@example.com", "channel": "general"}
        ],
        "E004": [
            {"type": "create_email_profile", "email": "diana@example.com", "display_name": "Diana Chen"},
            {"type": "assign_system_access", "pack_id": "pack_engineering", "systems": ["crm", "erp", "git"]},
            {"type": "allocate_equipment", "asset_tags": ["LAPTOP-E004", "MONITOR-E004"]},
            {"type": "post_welcome_message", "to": "diana@example.com", "channel": "general"}
        ]
    }

    action_score = 0
    action_max = 60  # 每个员工20分
    for emp_id, expected_acts in expected_actions.items():
        emp_record = next((item for item in data if item.get("employee_id") == emp_id), None)
        if emp_record is None:
            action_score += 0
            continue
        actual_acts = emp_record.get("actions", [])
        # 将实际 actions 规范化为可比较的形式（忽略顺序）
        # 先转为 tuple 集合，但字典不可哈希，先排序再比较列表
        def normalize(acts):
            # 按 type 排序，每项排序 keys
            sorted_acts = sorted(acts, key=lambda x: x.get("type", ""))
            return [dict(sorted(d.items())) for d in sorted_acts]
        exp_normal = normalize(expected_acts)
        act_normal = normalize(actual_acts)
        if exp_normal == act_normal:
            action_score += 20
        else:
            # 部分正确可给分数，但这里精确匹配才满分
            pass
    score += action_score
    if action_score == 60:
        details.append({"item": "每个员工 actions 完全正确", "score": 60, "max_score": 60, "passed": True, "reason": "所有预期动作匹配"})
    else:
        details.append({"item": "每个员工 actions 完全正确", "score": action_score, "max_score": 60, "passed": False, "reason": f"得分 {action_score}/60"})

    # 5) 没有多余员工记录（已在第3步检查过）
    # 最终汇总
    _write_score(workspace, score, details)

def _write_score(workspace, total, details):
    result = {"total_score": total, "details": details}
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
