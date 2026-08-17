import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    score_details = []
    total_score = 0

    # ------------------ 1. 检查结果文件是否存在 (10分) ------------------
    result_path = os.path.join(workspace, "ops", "ai_growth_leaders.json")
    if os.path.isfile(result_path):
        score_details.append({
            "item": "结果文件 ops/ai_growth_leaders.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "结果文件 ops/ai_growth_leaders.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"文件不存在: {result_path}"
        })
        # 后续检查依赖文件存在，直接跳到写入结果
        write_score(workspace, total_score, score_details)
        return total_score

    # ------------------ 2. JSON 格式合法 (10分) ------------------
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "合法 JSON"
        })
        total_score += 10
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        write_score(workspace, total_score, score_details)
        return total_score

    # ------------------ 3. 结果为列表 (10分) ------------------
    if isinstance(data, list):
        score_details.append({
            "item": "结果类型为列表",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "data 是 list"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "结果类型为列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 list，实际 {type(data).__name__}"
        })
        write_score(workspace, total_score, score_details)
        return total_score

    # ------------------ 4. 列表长度正确 (20分) ------------------
    # 正确结果应包含两个竞品：DataFlow AI (df-002) 和 SmartSaaS (ss-003)
    expected_ids = {"df-002", "ss-003"}
    actual_ids = set()
    for i, item in enumerate(data):
        if isinstance(item, dict):
            cid = item.get("competitor_id")
            if cid:
                actual_ids.add(cid)
    if actual_ids == expected_ids:
        score_details.append({
            "item": "列表包含正确数量的竞品（2个）",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"实际ID: {sorted(actual_ids)}"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "列表包含正确数量的竞品（2个）",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望ID: {sorted(expected_ids)}, 实际ID: {sorted(actual_ids)}"
        })

    # ------------------ 5. 每个元素必须包含 competitor_id 和 name (20分) ------------------
    fields_ok = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            fields_ok = False
            reason = f"第{i}个元素不是字典"
            break
        if "competitor_id" not in item or "name" not in item:
            fields_ok = False
            reason = f"第{i}个元素缺少 competitor_id 或 name"
            break
    if fields_ok:
        score_details.append({
            "item": "每个元素包含必需字段 (competitor_id, name)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "字段齐全"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "每个元素包含必需字段 (competitor_id, name)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": reason
        })

    # ------------------ 6. 字段值精确匹配 (20分) ------------------
    # 排序后逐一对比（严格按 competitor_id 升序）
    sorted_data = sorted(data, key=lambda x: x.get("competitor_id", ""))
    expected_entries = [
        {"competitor_id": "df-002", "name": "DataFlow AI"},
        {"competitor_id": "ss-003", "name": "SmartSaaS"}
    ]
    all_match = True
    for i, (actual, expected) in enumerate(zip(sorted_data, expected_entries)):
        if actual["competitor_id"] != expected["competitor_id"] or actual["name"] != expected["name"]:
            all_match = False
            reason = f"第{i}个元素不匹配: 期望 {expected}, 实际 {actual}"
            break
    if all_match and len(sorted_data) == len(expected_entries):
        score_details.append({
            "item": "每个竞品的 ID 和名称完全正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "所有字段值匹配"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "每个竞品的 ID 和名称完全正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": reason if not all_match else f"长度不匹配: 实际 {len(sorted_data)}, 期望 {len(expected_entries)}"
        })

    # ------------------ 7. 没有多余字段（可选扣分项） ------------------
    # 仅作警告，不扣总分
    extra_fields = []
    for item in data:
        if isinstance(item, dict):
            keys = set(item.keys())
            if keys != {"competitor_id", "name"}:
                extra_fields.append({item.get("competitor_id"): list(keys - {"competitor_id", "name"})})
    if extra_fields:
        # 扣5分（但不超过0）
        penalty = min(5, total_score)
        total_score -= penalty
        score_details.append({
            "item": "结果中无多余字段",
            "score": max(0, total_score - (total_score + penalty)),  # 实际已扣分，记录扣分
            "max_score": 0,
            "passed": False,
            "reason": f"存在多余字段: {extra_fields}, 已扣{penalty}分"
        })

    # 确保总分在0-100之间
    total_score = max(0, min(100, total_score))
    score_details.append({
        "item": "总分控制",
        "score": total_score,
        "max_score": 100,
        "passed": True,
        "reason": "计算完毕"
    })

    write_score(workspace, total_score, score_details)
    return total_score

def write_score(workspace, total_score, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
