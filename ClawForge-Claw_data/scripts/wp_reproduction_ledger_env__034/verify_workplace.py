import json
import os
import sys
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0

    # ========== 1. 目录结构检查 (10分) ==========
    dirs_ok = True
    for d in ["archive", "data", "project_docs"]:
        if not (ws / d).is_dir():
            dirs_ok = False
    if dirs_ok:
        details.append({"item": "必要目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "archive, data, project_docs 均存在"})
        total_score += 10
    else:
        details.append({"item": "必要目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少必要目录"})

    # ========== 2. ledeger.json 存在 (10分) ==========
    ledger_path = ws / "archive" / "ledger.json"
    if ledger_path.is_file():
        details.append({"item": "ledger.json 文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "ledger.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续检查无法进行，直接输出
        output_result(details, total_score)
        return

    # ========== 3. JSON 格式合法 (10分) ==========
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        output_result(details, total_score)
        return

    # ========== 4. 必需字段存在 (每个5分，共20分) ==========
    required_fields = ["project_id", "doc_id", "result", "reproduced_by", "timestamp"]
    field_scores = 0
    field_details = []
    for field in required_fields:
        if field in ledger:
            field_details.append({"item": f"字段 '{field}' 存在", "score": 5, "max_score": 5, "passed": True, "reason": "存在"})
            field_scores += 5
        else:
            field_details.append({"item": f"字段 '{field}' 存在", "score": 0, "max_score": 5, "passed": False, "reason": "缺失"})
    details.extend(field_details)
    total_score += field_scores

    # ========== 5. 字段值精确验证 (共50分) ==========
    # 5.1 project_id = "proj-034" (10分)
    if ledger.get("project_id") == "proj-034":
        details.append({"item": "project_id 正确", "score": 10, "max_score": 10, "passed": True, "reason": "值正确"})
        total_score += 10
    else:
        details.append({"item": "project_id 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 'proj-034', 实际 '{ledger.get('project_id')}'"})

    # 5.2 doc_id = "doc-007" (10分)
    if ledger.get("doc_id") == "doc-007":
        details.append({"item": "doc_id 正确", "score": 10, "max_score": 10, "passed": True, "reason": "值正确"})
        total_score += 10
    else:
        details.append({"item": "doc_id 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 'doc-007', 实际 '{ledger.get('doc_id')}'"})

    # 5.3 result = "success" (10分)
    if ledger.get("result") == "success":
        details.append({"item": "result 正确", "score": 10, "max_score": 10, "passed": True, "reason": "值正确"})
        total_score += 10
    else:
        details.append({"item": "result 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 'success', 实际 '{ledger.get('result')}'"})

    # 5.4 reproduced_by 包含 name 和 email (5分) 且与 accounts.json 中具有 reproducer 权限的用户一致 (10分, 共15分)
    rep = ledger.get("reproduced_by", {})
    if isinstance(rep, dict) and "name" in rep and "email" in rep:
        details.append({"item": "reproduced_by 包含 name 和 email", "score": 5, "max_score": 5, "passed": True, "reason": "结构正确"})
        total_score += 5
        # 从 accounts.json 中查找具有 reproducer 权限的用户
        try:
            with open(ws / "data" / "accounts.json", "r", encoding="utf-8") as f:
                accounts = json.load(f)
            reproducer = None
            for acc in accounts:
                if "reproduce" in acc.get("permissions", []):
                    reproducer = acc
                    break
            if reproducer:
                expected_name = reproducer["display_name"]
                expected_email = rep.get("email")
                # 检查 name 和 email 是否匹配
                if rep["name"] == expected_name and rep["email"] == reproducer["email"]:
                    details.append({"item": "reproduced_by 信息与团队记录一致", "score": 10, "max_score": 10, "passed": True, "reason": f"匹配 {expected_name}"})
                    total_score += 10
                else:
                    details.append({"item": "reproduced_by 信息与团队记录一致", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 name='{expected_name}', email='{reproducer['email']}', 实际 name='{rep['name']}', email='{rep['email']}'"})
            else:
                details.append({"item": "reproduced_by 信息与团队记录一致", "score": 0, "max_score": 10, "passed": False, "reason": "accounts.json 中未找到具有 reproducer 权限的用户"})
        except Exception as e:
            details.append({"item": "reproduced_by 信息与团队记录一致", "score": 0, "max_score": 10, "passed": False, "reason": f"读取 accounts.json 失败: {str(e)}"})
    else:
        details.append({"item": "reproduced_by 包含 name 和 email", "score": 0, "max_score": 5, "passed": False, "reason": "缺失或格式错误"})
        # 此子项目未通过，后面的10分也无法通过
        details.append({"item": "reproduced_by 信息与团队记录一致", "score": 0, "max_score": 10, "passed": False, "reason": "前置条件未满足"})

    # 5.5 timestamp 与 timestamp.txt 一致 (5分)
    try:
        with open(ws / "timestamp.txt", "r", encoding="utf-8") as f:
            expected_ts = f.read().strip()
        actual_ts = ledger.get("timestamp", "")
        if actual_ts == expected_ts:
            details.append({"item": "timestamp 与 timestamp.txt 一致", "score": 5, "max_score": 5, "passed": True, "reason": "值正确"})
            total_score += 5
        else:
            details.append({"item": "timestamp 与 timestamp.txt 一致", "score": 0, "max_score": 5, "passed": False, "reason": f"期望 '{expected_ts}', 实际 '{actual_ts}'"})
    except Exception as e:
        details.append({"item": "timestamp 与 timestamp.txt 一致", "score": 0, "max_score": 5, "passed": False, "reason": f"读取 timestamp.txt 失败: {str(e)}"})

    # 最终总分，确保 0-100
    total_score = min(max(total_score, 0), 100)
    output_result(details, total_score)

def output_result(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
