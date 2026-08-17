import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score_details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查 (10分)
    required_dirs = ["ops"]
    dir_score = 0
    for d in required_dirs:
        if os.path.isdir(d):
            dir_score += 5
        else:
            dir_score += 0
    score_details.append({
        "item": "目录结构 ops 存在",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": f"期望目录 ops，实际存在 {[d for d in required_dirs if os.path.isdir(d)]}"
    })
    total_score += dir_score

    # 2. 目标文件存在 (10分)
    target_file = "ops/handover_checklist.json"
    file_exists = os.path.isfile(target_file)
    file_score = 10 if file_exists else 0
    score_details.append({
        "item": "ops/handover_checklist.json 存在",
        "score": file_score,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })
    total_score += file_score
    if not file_exists:
        # 如果文件不存在，后续无法检查，直接结束
        write_score(total_score, score_details)
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            checklist = json.load(f)
        json_ok = True
        json_reason = "JSON 解析成功"
    except Exception as e:
        json_ok = False
        json_reason = f"JSON 解析失败: {e}"
    json_score = 10 if json_ok else 0
    score_details.append({
        "item": "JSON 格式合法",
        "score": json_score,
        "max_score": 10,
        "passed": json_ok,
        "reason": json_reason
    })
    total_score += json_score
    if not json_ok:
        write_score(total_score, score_details)
        return

    # 4. 必需字段存在并正确 (每项10分,共60分)
    # employee_id
    emp_id_ok = checklist.get("employee_id") == "EMP003"
    score_details.append({
        "item": "employee_id 正确 (EMP003)",
        "score": 10 if emp_id_ok else 0,
        "max_score": 10,
        "passed": emp_id_ok,
        "reason": f"实际值: {checklist.get('employee_id')}"
    })
    total_score += 10 if emp_id_ok else 0

    # employee_name
    name_ok = checklist.get("employee_name") == "张三"
    score_details.append({
        "item": "employee_name 正确 (张三)",
        "score": 10 if name_ok else 0,
        "max_score": 10,
        "passed": name_ok,
        "reason": f"实际值: {checklist.get('employee_name')}"
    })
    total_score += 10 if name_ok else 0

    # department
    dept_ok = checklist.get("department") == "Finance"
    score_details.append({
        "item": "department 正确 (Finance)",
        "score": 10 if dept_ok else 0,
        "max_score": 10,
        "passed": dept_ok,
        "reason": f"实际值: {checklist.get('department')}"
    })
    total_score += 10 if dept_ok else 0

    # revoked_systems  (期望包含 "Admin Portal" 和 "CRM"，且没有多余项)
    expected_systems = {"Admin Portal", "CRM"}
    actual_systems = set(checklist.get("revoked_systems", []))
    sys_ok = actual_systems == expected_systems
    score_details.append({
        "item": "revoked_systems 内容准确 (Admin Portal, CRM)",
        "score": 20 if sys_ok else 0,
        "max_score": 20,
        "passed": sys_ok,
        "reason": f"期望 {expected_systems}，实际 {actual_systems}"
    })
    total_score += 20 if sys_ok else 0

    # reclaimed_equipment (期望包含 "LT-2041")
    expected_eq = {"LT-2041"}
    actual_eq = set(checklist.get("reclaimed_equipment", []))
    eq_ok = actual_eq == expected_eq
    score_details.append({
        "item": "reclaimed_equipment 内容准确 (LT-2041)",
        "score": 20 if eq_ok else 0,
        "max_score": 20,
        "passed": eq_ok,
        "reason": f"期望 {expected_eq}，实际 {actual_eq}"
    })
    total_score += 20 if eq_ok else 0

    # checklist_items (期望包含至少两条对应描述，且不多余)
    # 我们检查是否包含 "revoked" 和 "reclaimed" 相关的字符串，不要求精确顺序
    items = checklist.get("checklist_items", [])
    item_set = set(items)
    # 期望至少包含 "Admin Portal" 和 "CRM" 的撤销描述以及 "LT-2041" 的回收描述
    required_keywords = ["Admin Portal", "CRM", "LT-2041"]
    # 每个元素应包含对应关键词
    has_admin = any("Admin Portal" in i for i in items)
    has_crm = any("CRM" in i for i in items)
    has_lt = any("LT-2041" in i for i in items)
    items_ok = has_admin and has_crm and has_lt
    score_details.append({
        "item": "checklist_items 包含必要的撤销和回收描述",
        "score": 10 if items_ok else 0,
        "max_score": 10,
        "passed": items_ok,
        "reason": f"检查关键词: Admin Portal={'是' if has_admin else '否'}, CRM={'是' if has_crm else '否'}, LT-2041={'是' if has_lt else '否'}"
    })
    total_score += 10 if items_ok else 0

    # 写入结果
    write_score(total_score, score_details)


def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Score written: {total}/100")


if __name__ == "__main__":
    main()
