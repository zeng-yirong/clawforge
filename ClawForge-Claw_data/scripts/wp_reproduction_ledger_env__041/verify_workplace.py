#!/usr/bin/env python3
import sys
import os
import json
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace)
    score_details = []
    total_score = 0

    # 1. 检查 reproduction_ledger.json 是否存在
    ledger_path = ws / "reproduction_ledger.json"
    if ledger_path.exists():
        score_details.append({
            "item": "reproduction_ledger.json 存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "文件已创建"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "reproduction_ledger.json 存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "文件缺失"
        })
        # 如果文件不存在，直接结束，后续无法验证
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        sys.exit(0)

    # 2. 解析 JSON 合法性
    try:
        with open(ledger_path, "r") as f:
            ledger = json.load(f)
        score_details.append({
            "item": "JSON 格式合法",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "成功解析"
        })
        total_score += 5
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        sys.exit(0)

    # 3. 检查必需字段
    required_fields = ["bug_id", "project", "session_id", "timestamp", "steps", "result", "documentation_ref"]
    missing_fields = [f for f in required_fields if f not in ledger]
    if missing_fields:
        score_details.append({
            "item": "必需的账本字段存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"缺少字段: {missing_fields}"
        })
    else:
        score_details.append({
            "item": "必需的账本字段存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有必需字段都存在"
        })
        total_score += 10

    if missing_fields:
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        sys.exit(0)

    # 4. 验证 bug_id 为 REPRO-2025-001，project 为 project_alpha
    bug_id_pass = True
    if ledger["bug_id"] != "REPRO-2025-001":
        bug_id_pass = False
    if ledger["project"] != "project_alpha":
        bug_id_pass = False
    if bug_id_pass:
        score_details.append({
            "item": "bug_id 和 project 正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"bug_id={ledger['bug_id']}, project={ledger['project']}"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "bug_id 和 project 正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 bug_id=REPRO-2025-001, project=project_alpha，实际 bug_id={ledger.get('bug_id')}, project={ledger.get('project')}"
        })

    # 5. 验证 session_id 应为 session_003（最新成功）
    if ledger["session_id"] == "session_003":
        score_details.append({
            "item": "session_id 指向最新成功会话",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "session_id=session_003"
        })
        total_score += 15
    else:
        score_details.append({
            "item": "session_id 指向最新成功会话",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"实际 session_id={ledger['session_id']}，应为 session_003"
        })

    # 6. 验证 timestamp 应为 2025-03-15T10:30:00Z
    if ledger["timestamp"] == "2025-03-15T10:30:00Z":
        score_details.append({
            "item": "timestamp 正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "时间戳匹配"
        })
        total_score += 15
    else:
        score_details.append({
            "item": "timestamp 正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"实际 timestamp={ledger['timestamp']}，期望 2025-03-15T10:30:00Z"
        })

    # 7. 验证 steps 列表不为空且包含预期步骤内容
    steps = ledger.get("steps", [])
    if isinstance(steps, list) and len(steps) >= 3:
        # 检查至少包含关键步骤（从 session_003 的 summary 中提取）
        expected_steps = ["1. checkout tag v1.7", "2. enable dark mode", "3. run widget test suite"]
        step_match = all(s in steps for s in expected_steps)
        if step_match:
            score_details.append({
                "item": "steps 内容正确",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "步骤包含预期的三个关键操作"
            })
            total_score += 15
        else:
            score_details.append({
                "item": "steps 内容正确",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"期望步骤 {expected_steps}，实际步骤 {steps}"
            })
    else:
        score_details.append({
            "item": "steps 内容正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"steps 格式无效或数量不足: {steps}"
        })

    # 8. 验证 result 字段
    if ledger.get("result") == "Glitch observed on all test runs, confirmed":
        score_details.append({
            "item": "result 字段准确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "result 内容与 session_003 一致"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "result 字段准确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际 result={ledger.get('result')}，期望为 'Glitch observed on all test runs, confirmed'"
        })

    # 9. 验证 documentation_ref 指向 project_alpha/doc_001.md
    if ledger.get("documentation_ref") == "project_alpha/doc_001.md":
        score_details.append({
            "item": "documentation_ref 正确",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "文档引用正确"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "documentation_ref 正确",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"实际 documentation_ref={ledger.get('documentation_ref')}，期望 project_alpha/doc_001.md"
        })

    # 10. (Bonus) 如果帐本中还包含了 knowledge_entries 关联，则加分。但 prompt 提到可选，不作为硬性要求，因此额外加5分。
    if "knowledge_ref" in ledger:
        if isinstance(ledger["knowledge_ref"], dict) and "entry_id" in ledger["knowledge_ref"]:
            score_details.append({
                "item": "knowledge_entries 关联（额外）",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": f"已关联知识条目 {ledger['knowledge_ref']['entry_id']}"
            })
            total_score += 5
        else:
            score_details.append({
                "item": "knowledge_entries 关联（额外）",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "knowledge_ref 存在但格式不正确"
            })
    else:
        # 不扣分，但也不加分
        score_details.append({
            "item": "knowledge_entries 关联（额外）",
            "score": 0,
            "max_score": 5,
            "passed": True,
            "reason": "未包含可选的 knowledge_ref（不扣分）"
        })

    # 写入结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    main()
