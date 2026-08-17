import sys
import json
import os
from pathlib import Path

def check(workspace):
    details = []
    total_score = 0

    # 1. 检查输出目录 ops 是否存在 (10分)
    ops_dir = Path(workspace) / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops directory found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops directory missing"
        })

    # 2. 检查 deny_report.json 是否存在 (10分)
    report_path = ops_dir / "deny_report.json"
    if report_path.is_file():
        details.append({
            "item": "deny_report.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "file found"
        })
        total_score += 10
    else:
        details.append({
            "item": "deny_report.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file missing"
        })
        # 后续无法进行，返回
        final_score = total_score
        write_score(workspace, final_score, details)
        return

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parse succeeded"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        final_score = total_score
        write_score(workspace, final_score, details)
        return

    # 4. 数据必须是数组 (10分)
    if isinstance(data, list):
        details.append({
            "item": "data is a list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "top-level is array"
        })
        total_score += 10
    else:
        details.append({
            "item": "data is a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"top-level is {type(data).__name__}, expected list"
        })
        final_score = total_score
        write_score(workspace, final_score, details)
        return

    # 5. 数组长度应为 1 (只有 req_003 违规) (10分)
    if len(data) == 1:
        details.append({
            "item": "exactly one denied request",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"array length = {len(data)}"
        })
        total_score += 10
    else:
        details.append({
            "item": "exactly one denied request",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"array length = {len(data)}, expected 1"
        })
        # 继续检查第一个元素即使长度不对

    # 6. 检查第一个元素的 request_id (25分)
    item = data[0] if data else {}
    req_id = item.get("request_id", "")
    if req_id == "req_003":
        details.append({
            "item": "correct request_id (req_003)",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"found request_id = {req_id}"
        })
        total_score += 25
    else:
        details.append({
            "item": "correct request_id (req_003)",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"got request_id = {repr(req_id)}"
        })

    # 7. 检查 reason_code (25分)
    reason = item.get("reason_code", "")
    expected_reason = "policy_violation_access_without_ticket"
    if reason == expected_reason:
        details.append({
            "item": "correct reason_code",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"reason_code = {reason}"
        })
        total_score += 25
    else:
        details.append({
            "item": "correct reason_code",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"got reason_code = {repr(reason)}, expected {expected_reason}"
        })

    # 8. 不允许有多余字段 (10分) (只允许 request_id 和 reason_code)
    allowed_keys = {"request_id", "reason_code"}
    actual_keys = set(item.keys())
    if actual_keys == allowed_keys:
        details.append({
            "item": "no extra fields in record",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "only required fields present"
        })
        total_score += 10
    else:
        extra = actual_keys - allowed_keys
        details.append({
            "item": "no extra fields in record",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"extra keys: {extra}"
        })

    final_score = min(total_score, 100)  # 防止溢出
    write_score(workspace, final_score, details)

def write_score(workspace, score, details):
    out = {
        "total_score": score,
        "details": details
    }
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    check(workspace)
