import json
import sys
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace).resolve()
    score_details = []
    total_score = 0

    # ---------- 1. 检查产物文件是否存在 ----------
    expected_file = workspace_path / "ops" / "tom_urgent.json"
    if expected_file.exists():
        score_details.append({
            "item": "产物文件 ops/tom_urgent.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "产物文件 ops/tom_urgent.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"文件不存在 (检查路径: {expected_file})"
        })
        # 无法继续检查，直接写结果并退出
        result = {"total_score": total_score, "details": score_details}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # ---------- 2. 检查 JSON 合法性 ----------
    try:
        with open(expected_file, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "产物文件为合法 JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON 解析成功"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "产物文件为合法 JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        _write_and_exit(total_score, score_details, workspace_path)
        return

    # ---------- 3. 检查是否为列表 ----------
    if isinstance(data, list):
        score_details.append({
            "item": "产物为列表结构",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "顶层为数组"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "产物为列表结构",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"顶层类型为 {type(data).__name__}，期望 list"
        })
        _write_and_exit(total_score, score_details, workspace_path)
        return

    # ---------- 4. 列表长度验证（正确答案应为 2）----------
    expected_ids = {"e001", "e006"}
    if len(data) == 2:
        score_details.append({
            "item": "列表长度为 2",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"长度 {len(data)}，匹配预期"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "列表长度为 2",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"长度 {len(data)}，期望 2"
        })

    # ---------- 5. 每个元素必须包含 id 和 subject ----------
    all_have_keys = True
    for idx, item in enumerate(data):
        if not isinstance(item, dict) or "id" not in item or "subject" not in item:
            all_have_keys = False
            break
    if all_have_keys:
        score_details.append({
            "item": "每个元素包含 id 与 subject 字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有元素均具备必要字段"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "每个元素包含 id 与 subject 字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "部分元素缺失 id 或 subject"
        })

    # ---------- 6. 检查实际 ID 集合是否完全正确 ----------
    actual_ids = set(item["id"] for item in data if isinstance(item, dict) and "id" in item)
    if actual_ids == expected_ids:
        score_details.append({
            "item": "邮件 ID 集合正确 (e001, e006)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"实际 ID 集合 {actual_ids} 与预期完全一致"
        })
        total_score += 20
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason = ""
        if missing:
            reason += f"缺少ID: {missing}; "
        if extra:
            reason += f"多余ID: {extra}; "
        score_details.append({
            "item": "邮件 ID 集合正确 (e001, e006)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": reason
        })

    # ---------- 7. 检查 subject 是否正确匹配 ----------
    # 构建映射：正确ID -> 正确subject
    correct_subjects = {"e001": "Project deadline tomorrow", "e006": "Urgent: server down"}
    subject_ok = True
    for item in data:
        if isinstance(item, dict) and "id" in item and "subject" in item:
            expected_sub = correct_subjects.get(item["id"])
            if item["subject"] != expected_sub:
                subject_ok = False
                break
    if subject_ok:
        score_details.append({
            "item": "每个元素的 subject 与原始邮件匹配",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有 subject 正确"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "每个元素的 subject 与原始邮件匹配",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在 subject 错误"
        })

    # ---------- 8. 检查是否有多余字段 ----------
    allowed_keys = {"id", "subject"}
    extra_fields_exist = False
    for item in data:
        if isinstance(item, dict):
            if set(item.keys()) - allowed_keys:
                extra_fields_exist = True
                break
    if not extra_fields_exist:
        score_details.append({
            "item": "元素仅包含 id 和 subject，无多余字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "无多余字段"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "元素仅包含 id 和 subject，无多余字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在多余字段（如 body, importance 等）"
        })

    # 确保总分不超过100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(workspace_path / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

def _write_and_exit(score, details, workspace_path):
    result = {"total_score": score, "details": details}
    with open(workspace_path / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
