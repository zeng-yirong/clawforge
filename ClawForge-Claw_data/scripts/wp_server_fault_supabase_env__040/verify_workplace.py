#!/usr/bin/env python3
import sys, os, json, csv

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # ---------- 预期结果 ----------
    expected_ids = ["inc-001", "inc-005", "inc-010", "inc-003"]
    expected_csv = [
        {"incident_id": "inc-001", "title": "UPS故障-主库Billing API",   "severity": "critical", "service": "billing-api"},
        {"incident_id": "inc-005", "title": "West4 Spine上行链路中断",    "severity": "critical", "service": "west4-spine-uplink"},
        {"incident_id": "inc-010", "title": "Edge Cluster A12 UPS故障",  "severity": "critical", "service": "edge-cluster-a12"},
        {"incident_id": "inc-003", "title": "Analytics Mirror服务降级",  "severity": "high",     "service": "analytics-mirror"},
    ]

    # ---------- 1. JSON 检查 ----------
    json_path = os.path.join(workspace, "ops", "remediation_targets.json")
    if not os.path.exists(json_path):
        details.append({"item": "ops/remediation_targets.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
    else:
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            # 尝试提取列表
            ids = None
            if isinstance(data, list):
                ids = data
            else:
                for v in data.values():
                    if isinstance(v, list):
                        ids = v
                        break
            if ids is None:
                details.append({"item": "JSON 内容为有效数组", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 既不是数组，也无法从其值中找到数组"})
            else:
                details.append({"item": "JSON 内容为有效数组", "score": 10, "max_score": 10, "passed": True, "reason": "成功提取数组"})
                # 内容比对
                if ids == expected_ids:
                    details.append({"item": "remediation_targets.json 内容正确", "score": 40, "max_score": 40, "passed": True, "reason": f"ID 列表完全匹配:{expected_ids}"})
                else:
                    extra = [i for i in ids if i not in expected_ids]
                    missing = [i for i in expected_ids if i not in ids]
                    details.append({"item": "remediation_targets.json 内容正确", "score": 0, "max_score": 40, "passed": False, "reason": f"预期 {expected_ids}，实际 {ids}，多余 {extra}，缺失 {missing}"})
        except Exception as e:
            details.append({"item": "JSON 文件可解析", "score": 0, "max_score": 10, "passed": False, "reason": f"解析异常: {str(e)}"})

    # ---------- 2. CSV 检查 ----------
    csv_path = os.path.join(workspace, "ops", "audit_summary.csv")
    if not os.path.exists(csv_path):
        details.append({"item": "ops/audit_summary.csv 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
    else:
        try:
            with open(csv_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            expected_headers = ["incident_id", "title", "severity", "service"]
            # 表头
            if reader.fieldnames == expected_headers:
                details.append({"item": "CSV 表头正确", "score": 10, "max_score": 10, "passed": True, "reason": f"表头为 {expected_headers}"})
            else:
                details.append({"item": "CSV 表头正确", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 {expected_headers}，实际 {reader.fieldnames}"})
            # 行数
            if len(rows) == len(expected_ids):
                details.append({"item": "CSV 行数正确", "score": 10, "max_score": 10, "passed": True, "reason": f"共 {len(rows)} 行数据"})
            else:
                details.append({"item": "CSV 行数正确", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 {len(expected_ids)} 行，实际 {len(rows)} 行"})
            # 内容字段
            expected_map = {r["incident_id"]: r for r in expected_csv}
            match_ok = True
            issues = []
            for row in rows:
                rid = row.get("incident_id", "")
                if rid not in expected_map:
                    match_ok = False
                    issues.append(f"意外 incident_id: {rid}")
                    continue
                for key in ["title", "severity", "service"]:
                    if row.get(key) != expected_map[rid][key]:
                        match_ok = False
                        issues.append(f"{rid}.{key}: 预期 '{expected_map[rid][key]}'，实际 '{row.get(key)}'")
            if match_ok and len(rows) == len(expected_ids):
                details.append({"item": "CSV 内容字段正确", "score": 20, "max_score": 20, "passed": True, "reason": "所有记录字段均匹配"})
            else:
                details.append({"item": "CSV 内容字段正确", "score": 0, "max_score": 20, "passed": False, "reason": f"字段不匹配: {'; '.join(issues)}"})
        except Exception as e:
            details.append({"item": "CSV 文件可解析", "score": 0, "max_score": 10, "passed": False, "reason": f"解析异常: {str(e)}"})

    # ---------- 总分 ----------
    for d in details:
        total_score += d["score"]
    total_score = min(total_score, max_total)

    result = {"total_score": total_score, "details": details}
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/{max_total}")

if __name__ == "__main__":
    main()
