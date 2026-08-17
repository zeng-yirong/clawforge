import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score_details = []

def check(condition, item_name, score, max_score, reason_if_pass="", reason_if_fail=""):
    passed = bool(condition)
    reason = reason_if_pass if passed else reason_if_fail
    score_details.append({
        "item": item_name,
        "score": score if passed else 0,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return passed

def load_json(relative_path):
    full_path = os.path.join(workspace, relative_path)
    if not os.path.isfile(full_path):
        return None
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

# ---------- 1. 目录结构 ----------
check(os.path.isdir(os.path.join(workspace, "ops")),
      "ops/ 目录存在", 5, 5,
      "ops/ 目录已创建",
      "ops/ 目录不存在")
check(os.path.isdir(os.path.join(workspace, "data/offboarding")),
      "data/offboarding/ 目录存在", 5, 5,
      "data/offboarding/ 已存在 (初始数据)",
      "data/offboarding/ 不存在")

# ---------- 2. 产物存在且合法 ----------
checklist = load_json("ops/handover_checklist.json")
check(checklist is not None,
      "ops/handover_checklist.json 存在且是合法 JSON", 10, 10,
      "文件存在，JSON 解析成功",
      "文件不存在或 JSON 格式错误")

# ---------- 3. 清单内容正确性 ----------
if checklist and isinstance(checklist, dict):
    items = checklist.get("checklist", checklist.get("items", []))  # 兼容常见结构
    if not items and isinstance(checklist, list):
        items = checklist
    check(len(items) == 1,
          "清单中仅包含一条记录", 10, 10,
          "只有一条记录，符合要求",
          f"记录了 {len(items)} 条，期望 1 条")
    if items and len(items) == 1:
        rec = items[0]
        check(rec.get("employee_id") == "E003",
              "清单中 employee_id 为 E003", 10, 10,
              "employee_id 正确",
              f"实际为 {rec.get('employee_id')}")
        check(rec.get("employee_name") == "张三",
              "清单中 employee_name 为 张三", 10, 10,
              "employee_name 正确",
              f"实际为 {rec.get('employee_name')}")
        check(rec.get("department") == "Engineering",
              "清单中 department 为 Engineering", 10, 10,
              "部门正确",
              f"实际为 {rec.get('department')}")
        # 处理状态（字段名可能为 access_revoked / revoked / status）
        revoked = rec.get("access_revoked") or rec.get("revoked") or rec.get("access_status") == "revoked"
        check(revoked,
              "访问已被撤销（access_revoked 为 true）", 5, 5,
              "访问撤销标志正确",
              "access_revoked 缺失或不为 true")
        reclaimed = rec.get("equipment_reclaimed") or rec.get("reclaimed") or rec.get("equipment_status") == "reclaimed"
        check(reclaimed,
              "设备已被回收（equipment_reclaimed 为 true）", 5, 5,
              "设备回收标志正确",
              "equipment_reclaimed 缺失或不为 true")
    else:
        # 跳过后续字段检查
        pass

# ---------- 4. 原始文件修改检查 ----------
# 4.1 system_access.json - E003 应为 revoked
sa = load_json("data/offboarding/system_access.json")
if sa:
    s_list = sa.get("system_access", sa if isinstance(sa, list) else [])
    e003_sa = [x for x in s_list if x.get("employee_id") == "E003"]
    e004_sa = [x for x in s_list if x.get("employee_id") == "E004"]
    e001_sa = [x for x in s_list if x.get("employee_id") == "E001"]
    check(e003_sa and all(x.get("status") == "revoked" for x in e003_sa),
          "system_access.json 中 E003 所有记录 status 为 revoked", 10, 10,
          "E003 访问已全部撤销",
          "E003 仍有未撤销记录")
    check(e004_sa and all(x.get("status") == "active" for x in e004_sa),
          "system_access.json 中 E004 记录未被修改 (仍为 active)", 5, 5,
          "E004 未受影响",
          "E004 状态被错误修改")
    check(e001_sa and all(x.get("status") == "revoked" for x in e001_sa),
          "system_access.json 中 E001 原 revoked 状态未变", 5, 5,
          "E001 保持 revoked",
          "E001 状态被意外更改")
else:
    check(False, "system_access.json 可读取", 0, 20, "", "无法读取 system_access.json 文件")

# 4.2 equipment_assignments.json - E003 应为 reclaimed
ea = load_json("data/offboarding/equipment_assignments.json")
if ea:
    e_list = ea.get("equipment_assignments", ea if isinstance(ea, list) else [])
    e003_ea = [x for x in e_list if x.get("employee_id") == "E003"]
    e004_ea = [x for x in e_list if x.get("employee_id") == "E004"]
    e001_ea = [x for x in e_list if x.get("employee_id") == "E001"]
    check(e003_ea and all(x.get("status") == "reclaimed" for x in e003_ea),
          "equipment_assignments.json 中 E003 所有记录 status 为 reclaimed", 10, 10,
          "E003 设备已全部回收",
          "E003 仍有未回收设备")
    check(e004_ea and all(x.get("status") == "assigned" for x in e004_ea),
          "equipment_assignments.json 中 E004 记录未被修改 (仍为 assigned)", 5, 5,
          "E004 未受影响",
          "E004 状态被错误修改")
    check(e001_ea and all(x.get("status") == "reclaimed" for x in e001_ea),
          "equipment_assignments.json 中 E001 原 reclaimed 状态未变", 5, 5,
          "E001 保持 reclaimed",
          "E001 状态被意外更改")
else:
    check(False, "equipment_assignments.json 可读取", 0, 20, "", "无法读取 equipment_assignments.json 文件")

# 计算总分
total_score = sum(d["score"] for d in score_details)
output = {
    "total_score": total_score,
    "details": score_details
}
out_path = os.path.join(workspace, "workplace_score.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"Score written to {out_path}: {total_score}/100")
