import json
import sys
import os
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace).resolve()
    score_details = []
    total_score = 0

    # ---------- 1. 检查目录结构 ----------
    expected_dirs = ["creds", "config", "ops"]
    dir_ok = all((ws / d).is_dir() for d in expected_dirs)
    score_details.append({
        "item": "基础目录存在",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "creds、config、ops 三个目录均存在" if dir_ok else "缺少必要目录"
    })
    if dir_ok:
        total_score += 10

    # ---------- 2. 检查报告文件存在且合法 JSON ----------
    report_path = ws / "ops" / "audit_summary.json"
    report_exists = report_path.is_file()
    report_ok = False
    report_data = None
    if report_exists:
        try:
            with open(report_path, "r") as f:
                report_data = json.load(f)
            report_ok = True
        except (json.JSONDecodeError, Exception):
            report_ok = False
    score_details.append({
        "item": "审计报告存在且格式合法",
        "score": 10 if report_ok else 0,
        "max_score": 10,
        "passed": report_ok,
        "reason": "ops/audit_summary.json 是合法 JSON" if report_ok else "文件缺失或格式错误"
    })
    if report_ok:
        total_score += 10

    if not report_ok or report_data is None:
        # 早期退出，避免后续KeyError
        fail_rest = {
            "item": "后续检查（因报告缺失）",
            "score": 0,
            "max_score": 80,
            "passed": False,
            "reason": "报告不存在，无法继续"
        }
        score_details.append(fail_rest)
        final = {"total_score": total_score, "details": score_details}
        with open(str(ws / "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # ---------- 3. 检查 weak_passwords 字段 ----------
    expected_weak = [
        {"id": "cred_001", "original": "password123", "new": "Strong@123"},
        {"id": "cred_003", "original": "12345678", "new": "Strong@456"},
        {"id": "cred_005", "original": "weakpw", "new": "Strong@789"}
    ]
    weak_ok = True
    weak_reason = ""
    if "weak_passwords" not in report_data:
        weak_ok = False
        weak_reason = "缺少 weak_passwords 字段"
    else:
        actual = report_data["weak_passwords"]
        if not isinstance(actual, list):
            weak_ok = False
            weak_reason = "weak_passwords 不是列表"
        else:
            # 比较（忽略顺序）
            actual_sorted = sorted(actual, key=lambda x: x.get("id",""))
            expected_sorted = sorted(expected_weak, key=lambda x: x["id"])
            if actual_sorted == expected_sorted:
                weak_ok = True
                weak_reason = "弱密码列表完全正确"
            else:
                weak_ok = False
                weak_reason = f"内容不符，期望 {expected_sorted}，实际 {actual_sorted}"
    score_details.append({
        "item": "弱密码识别与替换",
        "score": 30 if weak_ok else 0,
        "max_score": 30,
        "passed": weak_ok,
        "reason": weak_reason
    })
    if weak_ok:
        total_score += 30

    # ---------- 4. 检查 uncategorized 字段 ----------
    expected_uncat = [
        {"id": "cred_003", "platform": "bank", "suggested_category": "银行账户"}
    ]
    uncat_ok = True
    uncat_reason = ""
    if "uncategorized" not in report_data:
        uncat_ok = False
        uncat_reason = "缺少 uncategorized 字段"
    else:
        actual = report_data["uncategorized"]
        if not isinstance(actual, list):
            uncat_ok = False
            uncat_reason = "uncategorized 不是列表"
        else:
            actual_sorted = sorted(actual, key=lambda x: x.get("id",""))
            expected_sorted = sorted(expected_uncat, key=lambda x: x["id"])
            if actual_sorted == expected_sorted:
                uncat_ok = True
                uncat_reason = "未分类凭据修补正确"
            else:
                uncat_ok = False
                uncat_reason = f"内容不符，期望 {expected_sorted}，实际 {actual_sorted}"
    score_details.append({
        "item": "未分类凭据补充",
        "score": 20 if uncat_ok else 0,
        "max_score": 20,
        "passed": uncat_ok,
        "reason": uncat_reason
    })
    if uncat_ok:
        total_score += 20

    # ---------- 5. 检查 missing_autofill 字段 ----------
    expected_autofill = [
        {"id": "cred_002", "platform": "twitter", "suggested_autofill": {"url": "https://twitter.example.com", "enabled": True}},
        {"id": "cred_005", "platform": "old", "suggested_autofill": {"url": "https://old.example.com", "enabled": True}}
    ]
    autofill_ok = True
    autofill_reason = ""
    if "missing_autofill" not in report_data:
        autofill_ok = False
        autofill_reason = "缺少 missing_autofill 字段"
    else:
        actual = report_data["missing_autofill"]
        if not isinstance(actual, list):
            autofill_ok = False
            autofill_reason = "missing_autofill 不是列表"
        else:
            actual_sorted = sorted(actual, key=lambda x: x.get("id",""))
            expected_sorted = sorted(expected_autofill, key=lambda x: x["id"])
            if actual_sorted == expected_sorted:
                autofill_ok = True
                autofill_reason = "缺失自动填充规则修补正确"
            else:
                autofill_ok = False
                autofill_reason = f"内容不符，期望 {expected_sorted}，实际 {actual_sorted}"
    score_details.append({
        "item": "缺失自动填充规则补充",
        "score": 20 if autofill_ok else 0,
        "max_score": 20,
        "passed": autofill_ok,
        "reason": autofill_reason
    })
    if autofill_ok:
        total_score += 20

    # ---------- 6. 检查 final_status 字段 ----------
    status_ok = (report_data.get("final_status") == "completed")
    score_details.append({
        "item": "最终状态标记",
        "score": 10 if status_ok else 0,
        "max_score": 10,
        "passed": status_ok,
        "reason": 'final_status 为 "completed"' if status_ok else f'期望 "completed"，实际 {report_data.get("final_status")}'
    })
    if status_ok:
        total_score += 10

    # 总分截断至100
    total_score = min(total_score, 100)
    final = {"total_score": total_score, "details": score_details}
    with open(str(ws / "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    verify()
