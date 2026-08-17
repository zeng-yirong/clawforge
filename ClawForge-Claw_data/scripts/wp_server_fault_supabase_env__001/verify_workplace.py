import sys, os, json

def verify(workspace):
    details = []
    total = 0
    max_total = 100

    # 1. 检查必要目录/文件是否存在（10分）
    required_files = [
        'ops/remediation.json',
        'logs/audit.json'
    ]
    for req in required_files:
        path = os.path.join(workspace, req)
        exists = os.path.isfile(path)
        if exists:
            details.append({
                "item": f"File {req} exists",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "File found"
            })
            total += 5
        else:
            details.append({
                "item": f"File {req} exists",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"File {req} not found"
            })

    # 2. 检查 JSON 格式合法性（10分）
    remediation_path = os.path.join(workspace, 'ops/remediation.json')
    audit_path = os.path.join(workspace, 'logs/audit.json')

    for fp, name in [(remediation_path, 'remediation.json'), (audit_path, 'audit.json')]:
        if not os.path.isfile(fp):
            continue
        try:
            with open(fp, 'r') as f:
                json.load(f)
            details.append({
                "item": f"{name} is valid JSON",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Parse succeeded"
            })
            total += 5
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": f"{name} is valid JSON",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Parse failed: {str(e)}"
            })

    # 3. 核心数据检查 remediation.json（60分）
    core_score = 0
    if os.path.isfile(remediation_path):
        try:
            with open(remediation_path, 'r') as f:
                rem = json.load(f)
        except:
            rem = None

        if isinstance(rem, dict):
            # 检查 incident_id (20分)
            if rem.get('incident_id') == 'INC-004':
                details.append({
                    "item": "remediation.json incident_id is correct",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": "incident_id = INC-004"
                })
                core_score += 20
            else:
                details.append({
                    "item": "remediation.json incident_id is correct",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"Expected INC-004, got {rem.get('incident_id')}"
                })

            # 检查 transaction_id (20分)
            if rem.get('transaction_id') == 'txn_7f9a2b1c':
                details.append({
                    "item": "remediation.json transaction_id is correct",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": "transaction_id = txn_7f9a2b1c"
                })
                core_score += 20
            else:
                details.append({
                    "item": "remediation.json transaction_id is correct",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"Expected txn_7f9a2b1c, got {rem.get('transaction_id')}"
                })

            # 检查 action 字段 (20分)
            if rem.get('action') in ['kill_transaction', 'terminate_transaction', 'pg_terminate_backend']:
                details.append({
                    "item": "remediation.json action field is present and plausible",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": f"action = {rem.get('action')}"
                })
                core_score += 20
            else:
                details.append({
                    "item": "remediation.json action field is present and plausible",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"Expected a kill/terminate action, got {rem.get('action')}"
                })
        else:
            details.append({
                "item": "remediation.json is a dict",
                "score": 0,
                "max_score": 60,
                "passed": False,
                "reason": "remediation.json is not a dictionary"
            })
    else:
        details.append({
            "item": "remediation.json exists for core checks",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "remediation.json not found"
        })

    total += core_score

    # 4. 审计日志检查（20分）
    audit_score = 0
    if os.path.isfile(audit_path):
        try:
            with open(audit_path, 'r') as f:
                audit = json.load(f)
        except:
            audit = None

        if isinstance(audit, list) and len(audit) > 0:
            entry = audit[0] if isinstance(audit[0], dict) else None
            if entry:
                # 检查是否包含 INC-004
                if 'INC-004' in str(entry) or entry.get('target') == 'INC-004' or entry.get('incident_id') == 'INC-004':
                    audit_score += 10
                    passed = True
                    reason = "Audit contains INC-004 reference"
                else:
                    passed = False
                    reason = "No reference to INC-004 found in audit entry"
                details.append({
                    "item": "Audit log references correct incident",
                    "score": 10 if passed else 0,
                    "max_score": 10,
                    "passed": passed,
                    "reason": reason
                })

                # 检查是否包含 txn_7f9a2b1c
                if 'txn_7f9a2b1c' in str(entry) or entry.get('transaction_id') == 'txn_7f9a2b1c':
                    audit_score += 10
                    passed = True
                    reason = "Audit contains txn_7f9a2b1c reference"
                else:
                    passed = False
                    reason = "No reference to txn_7f9a2b1c found in audit entry"
                details.append({
                    "item": "Audit log references correct transaction_id",
                    "score": 10 if passed else 0,
                    "max_score": 10,
                    "passed": passed,
                    "reason": reason
                })
            else:
                details.append({
                    "item": "Audit log entry is a dict",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": "First audit entry is not a dictionary"
                })
        else:
            details.append({
                "item": "Audit log is a non-empty list",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "audit.json is not a list or is empty"
            })
    else:
        details.append({
            "item": "Audit log exists",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "audit.json not found"
        })

    total += audit_score

    # 写入得分
    result = {
        "total_score": min(total, max_total),
        "details": details
    }
    score_path = os.path.join(workspace, 'workplace_score.json')
    with open(score_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Score: {result['total_score']}/100")
    return result['total_score']

if __name__ == '__main__':
    workspace = sys.argv[1] if len(sys.argv) > 1 else '.'
    verify(workspace)
