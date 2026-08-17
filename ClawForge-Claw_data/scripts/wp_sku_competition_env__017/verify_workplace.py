import sys
import json
import os
import math

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查 ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ missing"})
        # 后续检查需要ops目录，如果不存在直接返回
        details.append({"item": "competition_report.json exists", "score": 0, "max_score": 20, "passed": False, "reason": "ops dir missing"})
        details.append({"item": "report JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": "ops dir missing"})
        details.append({"item": "correct fields", "score": 0, "max_score": 30, "passed": False, "reason": "ops dir missing"})
        details.append({"item": "numerical accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "ops dir missing"})
        total = sum(d["score"] for d in details)
        result = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 检查 competition_report.json 存在 (20分)
    report_path = os.path.join(ops_dir, "competition_report.json")
    report = load_json(report_path)
    if report is not None:
        details.append({"item": "competition_report.json exists and is valid JSON", "score": 20, "max_score": 20, "passed": True, "reason": "found and parseable"})
        score += 20
    else:
        details.append({"item": "competition_report.json exists and is valid JSON", "score": 0, "max_score": 20, "passed": False, "reason": "missing or invalid JSON"})
        # 无法继续
        details.append({"item": "correct fields", "score": 0, "max_score": 30, "passed": False, "reason": "report missing"})
        details.append({"item": "numerical accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "report missing"})
        total = score + 0 + 0
        result = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查必需字段 (30分)
    required_fields = ["lumina_skin_avg_price", "derm_veil_avg_price", "price_difference", "anomaly"]
    missing_fields = [f for f in required_fields if f not in report]
    if not missing_fields:
        details.append({"item": "report contains all required fields", "score": 30, "max_score": 30, "passed": True, "reason": f"fields: {required_fields}"})
        score += 30
    else:
        details.append({"item": "report contains all required fields", "score": 0, "max_score": 30, "passed": False, "reason": f"missing: {missing_fields}"})
        # 数值检查跳过
        details.append({"item": "numerical accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "fields incomplete"})
        total = score + 0
        result = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 数值准确性 (30分)
    # 期望值: 根据env_builder数据:
    # LuminaSkin active Hydration Serum: LS-HS-001 (48.0), LS-HS-002 (62.0), LS-HS-003 (79.0) -> avg = (48+62+79)/3 = 63.0
    # DermVeil active Hydration Serum: DV-HS-001 (44.0), DV-HS-002 (59.0) -> avg = (44+59)/2 = 51.5
    # price_difference = 63.0 - 51.5 = 11.5, anomaly = false (因为大于0)
    expected_lumina = 63.0
    expected_derm = 51.5
    expected_diff = 11.5
    expected_anomaly = False

    actual_lumina = report.get("lumina_skin_avg_price")
    actual_derm = report.get("derm_veil_avg_price")
    actual_diff = report.get("price_difference")
    actual_anomaly = report.get("anomaly")

    # 允许浮点误差0.01
    num_ok = True
    reasons = []
    if not isinstance(actual_lumina, (int, float)) or abs(actual_lumina - expected_lumina) > 0.01:
        reasons.append(f"lumina_skin_avg_price expected {expected_lumina}, got {actual_lumina}")
        num_ok = False
    if not isinstance(actual_derm, (int, float)) or abs(actual_derm - expected_derm) > 0.01:
        reasons.append(f"derm_veil_avg_price expected {expected_derm}, got {actual_derm}")
        num_ok = False
    if not isinstance(actual_diff, (int, float)) or abs(actual_diff - expected_diff) > 0.01:
        reasons.append(f"price_difference expected {expected_diff}, got {actual_diff}")
        num_ok = False
    if actual_anomaly != expected_anomaly:
        reasons.append(f"anomaly expected {expected_anomaly}, got {actual_anomaly}")
        num_ok = False

    if num_ok:
        details.append({"item": "numerical accuracy", "score": 30, "max_score": 30, "passed": True, "reason": "all values correct within tolerance"})
        score += 30
    else:
        details.append({"item": "numerical accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "; ".join(reasons)})

    # 5. 额外检查：没有多余字段 (10分 奖励？为了总分100可调整，这里作为bonus去掉，总分正好100)
    # 其实不扣分，但要确保只检查要求的

    total_score = score
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
