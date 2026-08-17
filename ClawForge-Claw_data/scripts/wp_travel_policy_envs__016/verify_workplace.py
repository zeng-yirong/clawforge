import sys
import os
import json
import csv
from datetime import datetime, date

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查 audit 目录是否存在 (10分)
    audit_dir = os.path.join(workspace, "audit")
    details.append(check_dir_exists(audit_dir, "audit directory", 10))
    if details[-1]["passed"]:
        score += 10

    # 2. 检查 audit_report.json 是否存在 (10分)
    report_path = os.path.join(audit_dir, "audit_report.json")
    details.append(check_file_exists(report_path, "audit_report.json", 10))
    if details[-1]["passed"]:
        score += 10

    # 3. 文件内容合法性 (10分)
    report = None
    if details[-1]["passed"]:
        try:
            with open(report_path, "r") as f:
                report = json.load(f)
            details.append({
                "item": "JSON valid and parseable",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "File is valid JSON."
            })
            score += 10
        except Exception as e:
            details.append({
                "item": "JSON valid and parseable",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {str(e)}"
            })
            # 无法继续解析，但继续检查其他低级项
            report = None
    else:
        details.append({
            "item": "JSON valid and parseable",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Report file missing, cannot parse."
        })

    # 4. 检查 report_date 字段 (5分)
    if report and "report_date" in report:
        try:
            dt = datetime.strptime(report["report_date"], "%Y-%m-%d").date()
            expected = date(2026, 7, 1)
            if dt == expected:
                details.append({
                    "item": "report_date is 2026-07-01",
                    "score": 5,
                    "max_score": 5,
                    "passed": True,
                    "reason": "Date matches."
                })
                score += 5
            else:
                details.append({
                    "item": "report_date is 2026-07-01",
                    "score": 0,
                    "max_score": 5,
                    "passed": False,
                    "reason": f"Found {report['report_date']}, expected 2026-07-01"
                })
        except:
            details.append({
                "item": "report_date is 2026-07-01",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "Date format invalid or not parseable."
            })
    else:
        details.append({
            "item": "report_date field exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "report_date missing."
        })

    # 5. 检查 policy_version (5分)
    if report and "policy_version" in report:
        if report["policy_version"] == "2.0":
            details.append({
                "item": "policy_version is 2.0",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Correct version."
            })
            score += 5
        else:
            details.append({
                "item": "policy_version is 2.0",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Found {report['policy_version']}, expected 2.0"
            })
    else:
        details.append({
            "item": "policy_version field exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "policy_version missing."
        })

    # 6. violations 数组存在且长度正确 (20分)
    violations_len_score = 0
    if report and "violations" in report:
        expected_len = 4
        actual_len = len(report["violations"])
        if actual_len == expected_len:
            violations_len_score = 20
            details.append({
                "item": "violations array length = 4",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": f"Found {actual_len} violations."
            })
            score += 20
        else:
            details.append({
                "item": "violations array length = 4",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"Found {actual_len} violations, expected 4."
            })
    else:
        details.append({
            "item": "violations array exists",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "violations missing."
        })

    # 7. 检查每个违规的 booking_id 和 reason (40分, 每个10分)
    expected_violations = {
        "B002": "cabin_class business not allowed; total_cost 4500 exceeds max 3000",
        "B003": "total_cost 3200 exceeds max 3000; advance_booking_days 4 less than required 7",
        "B006": "cabin_class premium_economy not allowed",
        "B008": "total_cost 3500 exceeds max 3000"
    }
    # 注意：违规原因顺序可能因实现不同而不同，但内容必须包含所有点，我们用集合判等
    if report and "violations" in report:
        # 构建实际映射
        actual = {}
        for v in report["violations"]:
            if "booking_id" in v and "reason" in v:
                actual[v["booking_id"]] = v["reason"]
        # 逐项检查
        for bid, expected_reason in expected_violations.items():
            if bid in actual:
                # 将两个原因拆分成无序集合比较
                expected_set = set(r.strip() for r in expected_reason.split(";"))
                actual_set = set(r.strip() for r in actual[bid].split(";"))
                if expected_set == actual_set:
                    details.append({
                        "item": f"Violation {bid} reason matches",
                        "score": 10,
                        "max_score": 10,
                        "passed": True,
                        "reason": f"Found {actual[bid]}"
                    })
                    score += 10
                else:
                    details.append({
                        "item": f"Violation {bid} reason matches",
                        "score": 0,
                        "max_score": 10,
                        "passed": False,
                        "reason": f"Expected reasons {expected_set}, got {actual_set}"
                    })
            else:
                details.append({
                    "item": f"Violation {bid} found",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"booking_id {bid} missing from violations."
                })
    else:
        for bid in expected_violations:
            details.append({
                "item": f"Violation {bid} present",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "violations array not available."
            })

    # 写入评分
    total = sum(d["score"] for d in details)
    result = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Total score: {total}/100")
    sys.exit(0 if total == 100 else 1)

def check_dir_exists(path, label, max_score):
    if os.path.isdir(path):
        return {"item": label, "score": max_score, "max_score": max_score, "passed": True, "reason": "Directory exists."}
    else:
        return {"item": label, "score": 0, "max_score": max_score, "passed": False, "reason": "Directory missing."}

def check_file_exists(path, label, max_score):
    if os.path.isfile(path):
        return {"item": label, "score": max_score, "max_score": max_score, "passed": True, "reason": "File exists."}
    else:
        return {"item": label, "score": 0, "max_score": max_score, "passed": False, "reason": "File missing."}

if __name__ == "__main__":
    main()
