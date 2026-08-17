import json, os, sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 1. 检查 ops/denial_report.json 是否存在 (10分)
    report_path = os.path.join(workspace, "ops", "denial_report.json")
    if os.path.exists(report_path):
        details.append({
            "item": "Ops denial report file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found ops/denial_report.json"
        })
        score += 10
    else:
        details.append({
            "item": "Ops denial report file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File ops/denial_report.json not found"
        })

    # 2. 检查JSON格式合法性 (10分)
    if os.path.exists(report_path):
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            details.append({
                "item": "JSON is valid",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Valid JSON"
            })
            score += 10
        except (json.JSONDecodeError, Exception):
            details.append({
                "item": "JSON is valid",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Malformed JSON"
            })

    # 3. 检查必需字段 (request_id) (20分)
    if os.path.exists(report_path):
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) and "request_id" in data:
                details.append({
                    "item": "Contains 'request_id' field",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": f"Found request_id: {data['request_id']}"
                })
                score += 20
            elif isinstance(data, list) and len(data) > 0 and "request_id" in data[0]:
                # 也支持数组格式
                details.append({
                    "item": "Contains 'request_id' field",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": f"Found request_id in list: {data[0]['request_id']}"
                })
                score += 20
            else:
                details.append({
                    "item": "Contains 'request_id' field",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": "Missing 'request_id' field or unexpected structure"
                })
        except:
            pass

    # 4. 检查 request_id 是否正确 (应该为 req_003) (40分)
    if os.path.exists(report_path):
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            rid = None
            if isinstance(data, dict):
                rid = data.get("request_id")
            elif isinstance(data, list) and len(data) > 0:
                rid = data[0].get("request_id") if isinstance(data[0], dict) else None
            if rid == "req_003":
                details.append({
                    "item": "Correct request_id (req_003)",
                    "score": 40,
                    "max_score": 40,
                    "passed": True,
                    "reason": "Request ID matches the only overprivileged request"
                })
                score += 40
            else:
                details.append({
                    "item": "Correct request_id (req_003)",
                    "score": 0,
                    "max_score": 40,
                    "passed": False,
                    "reason": f"Expected 'req_003', got '{rid}'"
                })
        except:
            pass
    else:
        details.append({
            "item": "Correct request_id (req_003)",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "Report file missing, cannot check"
        })

    # 5. 检查是否包含拒绝理由（reason 字段）(20分)
    if os.path.exists(report_path):
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            reason = None
            if isinstance(data, dict):
                reason = data.get("reason") or data.get("message") or data.get("justification")
            elif isinstance(data, list) and len(data) > 0:
                item = data[0] if isinstance(data[0], dict) else {}
                reason = item.get("reason") or item.get("message") or item.get("justification")
            if reason and len(str(reason)) > 5:
                details.append({
                    "item": "Contains reason for denial",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": f"Reason provided: {str(reason)[:80]}"
                })
                score += 20
            else:
                details.append({
                    "item": "Contains reason for denial",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": "No denial reason found or too short"
                })
        except:
            pass
    else:
        details.append({
            "item": "Contains reason for denial",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Report file missing"
        })

    # 总分
    total_score = min(score, max_score)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    main()
