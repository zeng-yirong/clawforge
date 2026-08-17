#!/usr/bin/env python3
import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # ---------- 1. 目录结构检查 (10分) ----------
    archive_dir = os.path.join(workspace, "archive")
    if os.path.isdir(archive_dir):
        details.append({
            "item": "archive 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "archive 目录已创建"
        })
        total_score += 10
    else:
        details.append({
            "item": "archive 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到 archive 目录"
        })

    # ---------- 2. 目标文件存在性 (10分) ----------
    target_file = os.path.join(archive_dir, "reproduction_ledger.json")
    if os.path.isfile(target_file):
        details.append({
            "item": "archive/reproduction_ledger.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已生成"
        })
        total_score += 10
    else:
        details.append({
            "item": "archive/reproduction_ledger.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到文件"
        })
        # 如果文件不存在，后续检查无意义，直接输出当前分数并结束
        _write_score(total_score, details, workspace)
        return

    # ---------- 3. JSON 格式合法性 (10分) ----------
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析为 JSON 对象"
        })
        total_score += 10
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        _write_score(total_score, details, workspace)
        return

    # ---------- 4. 必需字段检查 (30分) ----------
    required_fields = ["scenario_id", "project", "steps", "status"]
    field_score = 0
    field_reasons = []
    for field in required_fields:
        if field in data:
            field_score += 7.5  # 每个字段 7.5 分，共 30
            field_reasons.append(f"字段 '{field}' 存在")
        else:
            field_reasons.append(f"字段 '{field}' 缺失")
    details.append({
        "item": "必需字段完整性 (scenario_id, project, steps, status)",
        "score": int(field_score),  # 取整
        "max_score": 30,
        "passed": field_score == 30,
        "reason": "; ".join(field_reasons)
    })
    total_score += int(field_score)

    # ---------- 5. 字段值正确性 (40分) ----------
    # 正确答案（与 env_builder 中正确的 scenario 一致）
    expected = {
        "scenario_id": "S-002",
        "project": "alpha",
        "steps": [
            "Step 1: Start the server with `npm start`",
            "Step 2: Send POST request to /api/trigger with payload {\"type\": \"bug\"}",
            "Step 3: Check logs for stack trace and observe database write failure"
        ],
        "status": "verified"
    }
    value_score = 0
    value_checks = []
    # scenario_id
    if data.get("scenario_id") == expected["scenario_id"]:
        value_score += 10
        value_checks.append("scenario_id 正确")
    else:
        value_checks.append(f"scenario_id 应为 {expected['scenario_id']}，实际为 {data.get('scenario_id')}")
    # project
    if data.get("project") == expected["project"]:
        value_score += 10
        value_checks.append("project 正确")
    else:
        value_checks.append(f"project 应为 {expected['project']}，实际为 {data.get('project')}")
    # steps
    if data.get("steps") == expected["steps"]:
        value_score += 15
        value_checks.append("steps 完全匹配")
    else:
        value_checks.append("steps 不匹配（顺序、内容或数量不一致）")
    # status
    if data.get("status") == expected["status"]:
        value_score += 5
        value_checks.append("status 正确")
    else:
        value_checks.append(f"status 应为 {expected['status']}，实际为 {data.get('status')}")

    passed_value = value_score == 40
    details.append({
        "item": "字段值正确性",
        "score": value_score,
        "max_score": 40,
        "passed": passed_value,
        "reason": "; ".join(value_checks)
    })
    total_score += value_score

    # ---------- 额外扣分：多余字段 ----------
    # 只允许 required_fields + 其他任意字段不扣分？但要求不要有多余？题目说“捏造多余字段/节点必须严扣分”，
    # 我们保守一点，允许额外字段存在，但 if 有除了 expected 之外的字段，每个扣 5 分，最多扣 10 分。
    extra_fields = [k for k in data if k not in required_fields]
    deduction = min(len(extra_fields) * 5, 10)
    if deduction > 0:
        total_score -= deduction
        details.append({
            "item": "无多余字段（额外字段扣分）",
            "score": -deduction,
            "max_score": 0,
            "passed": False,
            "reason": f"发现额外字段: {extra_fields}，共扣除 {deduction} 分"
        })

    # 确保总分在 0-100 范围内
    total_score = max(0, min(total_score, 100))

    _write_score(total_score, details, workspace)

def _write_score(total_score, details, workspace):
    output = {
        "total_score": total_score,
        "details": details
    }
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
