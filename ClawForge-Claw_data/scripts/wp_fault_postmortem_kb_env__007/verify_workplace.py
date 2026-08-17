import sys, os, json

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 辅助函数
    def check(item: str, max_score: int, condition: bool, reason: str):
        nonlocal total_score, details
        score = max_score if condition else 0
        total_score += score
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": condition,
            "reason": reason
        })

    # 1. 目录 ops/postmortem 存在 (10)
    dir_path = os.path.join(workspace, "ops", "postmortem")
    check("directory ops/postmortem exists", 10, os.path.isdir(dir_path), "目录存在" if os.path.isdir(dir_path) else "目录缺失")

    # 2. 文件 fault_007_postmortem.json 存在 (10)
    report_path = os.path.join(dir_path, "fault_007_postmortem.json")
    file_exists = os.path.isfile(report_path)
    check("file fault_007_postmortem.json exists", 10, file_exists, "文件存在" if file_exists else "文件缺失")

    # 如果文件不存在，后续检查直接记为失败（0分）
    if not file_exists:
        check("JSON is valid", 10, False, "文件不存在无法解析")
        check("has required fields (fault_id, root_cause, repair_plan)", 10, False, "文件不存在")
        check("fault_id equals 'fault_007'", 20, False, "文件不存在")
        check("root_cause matches expected string", 20, False, "文件不存在")
        check("repair_plan matches expected string", 20, False, "文件不存在")
    else:
        # 3. JSON 合法性 (10)
        try:
            with open(report_path, "r") as f:
                report = json.load(f)
            check("JSON is valid", 10, True, "JSON解析成功")
        except Exception as e:
            check("JSON is valid", 10, False, f"JSON解析失败: {str(e)}")
            report = None

        if report is None:
            check("has required fields (fault_id, root_cause, repair_plan)", 10, False, "JSON解析失败")
            check("fault_id equals 'fault_007'", 20, False, "JSON解析失败")
            check("root_cause matches expected string", 20, False, "JSON解析失败")
            check("repair_plan matches expected string", 20, False, "JSON解析失败")
        else:
            # 4. 包含必要字段 (10)
            has_fields = all(k in report for k in ["fault_id", "root_cause", "repair_plan"])
            check("has required fields (fault_id, root_cause, repair_plan)", 10, has_fields,
                  "字段完整" if has_fields else f"缺少字段: 现有键 {list(report.keys())}")

            # 5. fault_id 正确 (20)
            fault_id_ok = report.get("fault_id") == "fault_007"
            check("fault_id equals 'fault_007'", 20, fault_id_ok,
                  f"预期 'fault_007', 实际 '{report.get('fault_id')}'" if not fault_id_ok else "一致")

            # 6. root_cause 精确匹配 (20)
            expected_root_cause = "Deadlock on table orders due to concurrent updates without proper locking."
            root_cause = report.get("root_cause", "")
            root_cause_ok = (root_cause == expected_root_cause)
            check("root_cause matches expected string", 20, root_cause_ok,
                  f"预期 '{expected_root_cause}', 实际 '{root_cause}'" if not root_cause_ok else "一致")

            # 7. repair_plan 精确匹配 (20)
            expected_repair = "Use SELECT ... FOR UPDATE NOWAIT and add retry logic for order updates."
            repair = report.get("repair_plan", "")
            repair_ok = (repair == expected_repair)
            check("repair_plan matches expected string", 20, repair_ok,
                  f"预期 '{expected_repair}', 实际 '{repair}'" if not repair_ok else "一致")

    return {"total_score": total_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {result['total_score']}/100 written to {output_path}")

if __name__ == "__main__":
    main()
