import os
import sys
import json
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total = 0

    # ---------- 1. 目录结构 (10 分) ----------
    score_dir = 0
    max_dir = 10
    dirs_required = ["ops"]
    for d in dirs_required:
        if os.path.isdir(os.path.join(workspace, d)):
            score_dir += 5
        else:
            results.append({"item": f"Directory '{d}' exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing directory"})
            continue
    if score_dir == 10:
        results.append({"item": "Required directories (ops)", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories exist"})
    else:
        # 如果部分缺失，已经在循环中添加了条目
        pass
    total += score_dir

    # ---------- 2. 文件存在与合法性 (10 分) ----------
    score_file = 0
    max_file = 10
    required_files = [
        ("ops/remediation_results.json", "JSON"),
        ("ops/audit.log", "text")
    ]
    file_issues = []
    for fname, ftype in required_files:
        path = os.path.join(workspace, fname)
        if not os.path.isfile(path):
            file_issues.append(f"Missing {fname}")
            continue
        if ftype == "JSON":
            try:
                with open(path, "r") as fh:
                    data = json.load(fh)
                if not isinstance(data, list):
                    file_issues.append(f"{fname} is not a JSON array")
                    continue
            except (json.JSONDecodeError, Exception) as e:
                file_issues.append(f"{fname} invalid JSON: {str(e)}")
                continue
        elif ftype == "text":
            # 只要存在就算通过，内容在后续检查
            pass
    if not file_issues:
        score_file = 10
        results.append({"item": "Required output files exist and are valid", "score": 10, "max_score": 10, "passed": True, "reason": "All required files present and valid"})
    else:
        score_file = max(0, 10 - 3 * len(file_issues))  # 每个问题扣3分
        results.append({"item": "Required output files exist and are valid", "score": score_file, "max_score": 10, "passed": False, "reason": "; ".join(file_issues)})
    total += score_file

    # ---------- 3. remediation_results.json 内容正确性 (50 分) ----------
    score_remediation = 0
    max_remediation = 50
    rem_path = os.path.join(workspace, "ops/remediation_results.json")
    if not os.path.isfile(rem_path):
        results.append({"item": "remediation_results.json content", "score": 0, "max_score": 50, "passed": False, "reason": "File not found"})
        total += 0
        # 跳过后续检查
    else:
        try:
            with open(rem_path, "r") as f:
                rem_data = json.load(f)
        except Exception:
            results.append({"item": "remediation_results.json content", "score": 0, "max_score": 50, "passed": False, "reason": "Invalid JSON"})
            total += 0
            rem_data = None

        if rem_data is not None:
            # 检查是否为数组
            if not isinstance(rem_data, list):
                results.append({"item": "remediation_results.json content", "score": 0, "max_score": 50, "passed": False, "reason": "Not a JSON array"})
            else:
                # 目标ID集合 (从env_builder中确定的三个)
                expected_ids = {"UPS-001", "UPS-002", "UPS-003"}
                found_ids = set()
                extra_ids = set()
                all_entries_valid = True
                entry_errors = []
                for i, entry in enumerate(rem_data):
                    if not isinstance(entry, dict):
                        entry_errors.append(f"Entry {i} is not a dictionary")
                        all_entries_valid = False
                        continue
                    eid = entry.get("incident_id")
                    action = entry.get("action")
                    status = entry.get("status")
                    if eid is None or action is None or status is None:
                        entry_errors.append(f"Entry {i} missing required fields (incident_id, action, status)")
                        all_entries_valid = False
                        continue
                    if action != "remediated":
                        entry_errors.append(f"Entry {i} action is '{action}', expected 'remediated'")
                        all_entries_valid = False
                    if status != "resolved":
                        entry_errors.append(f"Entry {i} status is '{status}', expected 'resolved'")
                        all_entries_valid = False
                    if eid not in expected_ids:
                        extra_ids.add(eid)
                    else:
                        found_ids.add(eid)

                # 计算分数
                missing_ids = expected_ids - found_ids
                score_rem = 0
                # 每个正确找到的ID得10分，最多30
                correct_ids_score = len(found_ids) * 10
                # 没有额外ID得10分
                extra_penalty = 0 if not extra_ids else -10
                # 所有条目字段正确得10分
                fields_ok = (all_entries_valid and len(entry_errors) == 0)
                fields_score = 10 if fields_ok else 0
                score_rem = correct_ids_score + extra_penalty + fields_score
                score_rem = max(0, min(50, score_rem))

                reasons = []
                if missing_ids:
                    reasons.append(f"Missing IDs: {sorted(missing_ids)}")
                if extra_ids:
                    reasons.append(f"Unexpected IDs: {sorted(extra_ids)}")
                if not fields_ok:
                    reasons.append(f"Field errors: {'; '.join(entry_errors[:3])}")
                if not reasons:
                    reasons.append("All entries correct")
                passed = (len(missing_ids) == 0 and not extra_ids and fields_ok)
                results.append({"item": "remediation_results.json content", "score": score_rem, "max_score": 50, "passed": passed, "reason": "; ".join(reasons)})
                total += score_rem

    # ---------- 4. audit.log 格式与内容 (30 分) ----------
    score_audit = 0
    max_audit = 30
    aud_path = os.path.join(workspace, "ops/audit.log")
    if not os.path.isfile(aud_path):
        results.append({"item": "audit.log content", "score": 0, "max_score": 30, "passed": False, "reason": "File not found"})
        total += 0
    else:
        try:
            with open(aud_path, "r") as f:
                lines = f.readlines()
        except Exception:
            lines = []
        # 期望3行（对应三个目标incident）
        expected_ids = {"UPS-001", "UPS-002", "UPS-003"}
        audit_ids = set()
        line_format_ok = True
        format_errors = []
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            # 格式：ISO时间戳 | 操作 | 事件ID
            pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\s*\|\s*remediated\s*\|\s*(UPS-\d+)$'
            m = re.match(pattern, line)
            if not m:
                format_errors.append(f"Line {idx+1} does not match expected format")
                line_format_ok = False
            else:
                eid = m.group(1)
                audit_ids.add(eid)

        # 评分
        # 行数正确（3）= 10分；格式全部正确 = 10分；覆盖全部目标ID = 10分
        score_audit_lines = 10 if len(lines) == 3 else 0
        score_audit_format = 10 if line_format_ok else 0
        missing_audit = expected_ids - audit_ids
        extra_audit = audit_ids - expected_ids
        score_audit_coverage = 10 if (not missing_audit and not extra_audit) else 0
        score_audit = score_audit_lines + score_audit_format + score_audit_coverage

        reasons_audit = []
        if len(lines) != 3:
            reasons_audit.append(f"Expected 3 lines, got {len(lines)}")
        if not line_format_ok:
            reasons_audit.append("Format errors: " + "; ".join(format_errors[:2]))
        if missing_audit:
            reasons_audit.append(f"Missing incident IDs: {sorted(missing_audit)}")
        if extra_audit:
            reasons_audit.append(f"Unexpected incident IDs: {sorted(extra_audit)}")
        if not reasons_audit:
            reasons_audit.append("All checks passed")
        passed_audit = (score_audit == max_audit)
        results.append({"item": "audit.log content", "score": score_audit, "max_score": max_audit, "passed": passed_audit, "reason": "; ".join(reasons_audit)})
        total += score_audit

    # ---------- 总分 ----------
    total_score = min(100, total)
    output = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
