import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace)

    score = 0
    details = []

    # ── 1. 检查目标文件存在 (10分) ──
    target = workspace / "ops" / "handover_checklist.json"
    if target.exists():
        details.append({
            "item": "文件存在性: ops/handover_checklist.json",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "目标文件存在"
        })
        score += 10
    else:
        details.append({
            "item": "文件存在性: ops/handover_checklist.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续无法检查，直接输出结果
        _write_score(score, details)
        return

    # ── 2. JSON 合法性 (10分) ──
    try:
        with open(target, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法性",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "合法 JSON"
        })
        score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        _write_score(score, details)
        return

    # ── 3. 数据结构：是否为列表 (10分) ──
    if isinstance(data, list):
        details.append({
            "item": "根元素类型",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "根元素为列表"
        })
        score += 10
    else:
        details.append({
            "item": "根元素类型",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望列表，得到 {type(data).__name__}"
        })
        _write_score(score, details)
        return

    # ── 4. 记录数量 (15分) ──
    expected_count = 3  # E001, E002, E004
    actual_count = len(data)
    if actual_count == expected_count:
        details.append({
            "item": "记录数量",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"包含 {expected_count} 条记录"
        })
        score += 15
    else:
        details.append({
            "item": "记录数量",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"期望 {expected_count} 条，实际 {actual_count} 条"
        })

    # ── 5. 每条记录的字段完整性 (15分) ──
    required_fields = {"employee_id", "systems_to_revoke", "equipment_to_reclaim"}
    field_ok = True
    for i, rec in enumerate(data):
        if not isinstance(rec, dict):
            details.append({
                "item": f"记录 #{i} 类型",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "不是字典"
            })
            field_ok = False
            break
        missing = required_fields - set(rec.keys())
        if missing:
            details.append({
                "item": f"记录 {rec.get('employee_id','?')} 字段完整性",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"缺少字段: {missing}"
            })
            field_ok = False
            break
    if field_ok:
        details.append({
            "item": "每条记录字段完整性",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "所有记录包含 employee_id, systems_to_revoke, equipment_to_reclaim"
        })
        score += 15

    # ── 6. 精确内容验证 (40分) ──
    # 构建期望结果
    expected = [
        {"employee_id": "E001", "systems_to_revoke": ["Admin Portal", "CRM"], "equipment_to_reclaim": ["LT-2041"]},
        {"employee_id": "E002", "systems_to_revoke": ["CRM"], "equipment_to_reclaim": []},
        {"employee_id": "E004", "systems_to_revoke": [], "equipment_to_reclaim": ["BG-8821"]}
    ]
    # 按 employee_id 排序后比较
    data_sorted = sorted(data, key=lambda x: x["employee_id"])
    expected_sorted = sorted(expected, key=lambda x: x["employee_id"])
    match = True
    for i, (d, e) in enumerate(zip(data_sorted, expected_sorted)):
        if d["employee_id"] != e["employee_id"]:
            match = False
            break
        if sorted(d.get("systems_to_revoke", [])) != sorted(e["systems_to_revoke"]):
            match = False
            break
        if sorted(d.get("equipment_to_reclaim", [])) != sorted(e["equipment_to_reclaim"]):
            match = False
            break
    if match and len(data_sorted) == len(expected_sorted):
        details.append({
            "item": "精确内容匹配",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": "所有员工对应系统/设备列表完全正确"
        })
        score += 40
    else:
        details.append({
            "item": "精确内容匹配",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": f"期望 {expected_sorted}，实际 {data_sorted}"
        })

    # 写入最终得分
    _write_score(score, details)


def _write_score(total, details):
    result = {
        "total_score": min(total, 100),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {result['total_score']}/100")


if __name__ == "__main__":
    main()
