import sys
import json
import os
from pathlib import Path

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []

    # 1. 检查 ops/ 目录存在 (10分)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录已创建"})
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录不存在"})

    # 2. 检查 ops/postmortem.json 存在且合法 (10分)
    pm_path = ops_dir / "postmortem.json"
    pm_data = load_json(pm_path)
    if pm_data is not None:
        details.append({"item": "postmortem.json存在且合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且解析成功"})
    else:
        details.append({"item": "postmortem.json存在且合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失或JSON格式错误"})
        # 如果文件缺失，后续无法检查，直接返回
        total = sum(d["score"] for d in details)
        result = {"total_score": total, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查必需字段 (20分)
    required_fields = ["fault_id", "service_name", "severity", "root_cause", "repair_plan", "analyzed_attachments"]
    missing = [f for f in required_fields if f not in pm_data]
    if not missing:
        details.append({"item": "必需字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有必需字段存在"})
    else:
        details.append({"item": "必需字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {', '.join(missing)}"})
        total = sum(d["score"] for d in details)
        result = {"total_score": total, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 读取 ground truth 故障案例 (从 fault_cases.json 中找出 payment-service + critical)
    fault_cases_path = ws / "data" / "faults" / "fault_cases.json"
    fault_data = load_json(fault_cases_path)
    if fault_data is None:
        details.append({"item": "读取故障案例基准", "score": 0, "max_score": 40, "passed": False, "reason": "无法读取fault_cases.json"})
        total = sum(d["score"] for d in details)
        result = {"total_score": total, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 寻找目标故障 (唯一: service_name=payment-service, severity=critical)
    target_case = None
    for case in fault_data.get("fault_cases", []):
        if case.get("service_name") == "payment-service" and case.get("severity") == "critical":
            target_case = case
            break
    if target_case is None:
        details.append({"item": "基准数据完整", "score": 0, "max_score": 40, "passed": False, "reason": "未在fault_cases中找到payment-service critical案例"})
        total = sum(d["score"] for d in details)
        result = {"total_score": total, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4a. 检查 fault_id (5分)
    field_score = 0
    field_items = [
        ("fault_id", target_case["fault_id"], 5),
        ("service_name", target_case["service_name"], 10),
        ("severity", target_case["severity"], 10),
        ("root_cause", target_case["root_cause_hint"], 5),
        ("repair_plan", target_case["repair_plan_hint"], 5)
    ]
    attr_reasons = []
    for field_name, expected, weight in field_items:
        actual = pm_data.get(field_name)
        if actual == expected:
            field_score += weight
            attr_reasons.append(f"{field_name}正确")
        else:
            attr_reasons.append(f"{field_name}错误(期望'{expected}', 实际'{actual}')")
    details.append({
        "item": "关键字段值正确性",
        "score": field_score,
        "max_score": 35,
        "passed": field_score == 35,
        "reason": "; ".join(attr_reasons)
    })

    # 5. 检查附件列表 (从 attachments.json 筛选出 description 包含 F-003 的记录)
    attachments_path = ws / "data" / "attachments.json"
    att_data = load_json(attachments_path)
    if att_data is None:
        details.append({"item": "附件列表正确性", "score": 0, "max_score": 20, "passed": False, "reason": "无法读取attachments.json"})
    else:
        expected_attachments = []
        for att in att_data:
            if "F-003" in att.get("description", ""):
                expected_attachments.append({"title": att["title"], "path": att["path"]})
        expected_attachments.sort(key=lambda x: x["title"])
        actual_attachments = pm_data.get("analyzed_attachments", [])
        # 允许顺序不同，统一排序后比较
        actual_sorted = sorted(actual_attachments, key=lambda x: x.get("title", ""))
        if actual_sorted == expected_attachments:
            details.append({"item": "附件列表正确性", "score": 20, "max_score": 20, "passed": True, "reason": "附件标题和路径完全匹配"})
        else:
            details.append({"item": "附件列表正确性", "score": 0, "max_score": 20, "passed": False, "reason": f"期望附件: {expected_attachments}, 实际附件: {actual_sorted}"})

    # 汇总
    total_score = sum(d["score"] for d in details)
    result = {"total_score": total_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
