import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    results = []
    total_score = 0

    # 1. 检查 ops 目录是否存在（10分）
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    results.append({
        "item": "ops目录存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops目录存在" if dir_exists else "ops目录不存在"
    })
    total_score += 10 if dir_exists else 0

    # 2. 检查 market_alert.json 是否存在（10分）
    alert_path = os.path.join(workspace, "ops", "market_alert.json")
    file_exists = os.path.isfile(alert_path)
    results.append({
        "item": "market_alert.json 文件存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })
    total_score += 10 if file_exists else 0

    if not file_exists:
        # 后续评分无法进行，跳出
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": results}, f, indent=2)
        return

    # 3. 解析 JSON 合法性（10分）
    try:
        with open(alert_path, "r") as f:
            data = json.load(f)
        json_valid = True
        reason = "JSON格式合法"
    except (json.JSONDecodeError, Exception) as e:
        json_valid = False
        reason = f"JSON解析失败: {str(e)}"
    results.append({
        "item": "JSON格式合法",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    total_score += 10 if json_valid else 0

    if not json_valid:
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": results}, f, indent=2)
        return

    # 4. 检查关键字段存在性（10分）
    required_keys = ["competitor_id", "competitor_name", "policy_id", "policy_title", "impact_level", "alert_type"]
    missing_keys = [k for k in required_keys if k not in data]
    keys_ok = len(missing_keys) == 0
    results.append({
        "item": "必须字段存在",
        "score": 10 if keys_ok else 0,
        "max_score": 10,
        "passed": keys_ok,
        "reason": "所有必须字段都存在" if keys_ok else f"缺少字段: {missing_keys}"
    })
    total_score += 10 if keys_ok else 0

    if not keys_ok:
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": results}, f, indent=2)
        return

    # 5. competitor_id 准确性（10分）
    correct_comp_id = "comp_001"
    comp_id_ok = data.get("competitor_id") == correct_comp_id
    results.append({
        "item": "competitor_id 正确",
        "score": 10 if comp_id_ok else 0,
        "max_score": 10,
        "passed": comp_id_ok,
        "reason": f"competitor_id = {data.get('competitor_id')}, 期望 {correct_comp_id}" if not comp_id_ok else "正确"
    })
    total_score += 10 if comp_id_ok else 0

    # 6. competitor_name 准确性（5分）
    correct_comp_name = "CloudMajor"
    comp_name_ok = data.get("competitor_name") == correct_comp_name
    results.append({
        "item": "competitor_name 正确",
        "score": 5 if comp_name_ok else 0,
        "max_score": 5,
        "passed": comp_name_ok,
        "reason": f"competitor_name = {data.get('competitor_name')}, 期望 {correct_comp_name}" if not comp_name_ok else "正确"
    })
    total_score += 5 if comp_name_ok else 0

    # 7. policy_id 准确性（15分）
    correct_policy_id = "pol_003"
    policy_id_ok = data.get("policy_id") == correct_policy_id
    results.append({
        "item": "policy_id 正确",
        "score": 15 if policy_id_ok else 0,
        "max_score": 15,
        "passed": policy_id_ok,
        "reason": f"policy_id = {data.get('policy_id')}, 期望 {correct_policy_id}" if not policy_id_ok else "正确"
    })
    total_score += 15 if policy_id_ok else 0

    # 8. policy_title 准确性（5分）
    correct_policy_title = "US AI Transparency Act"
    policy_title_ok = data.get("policy_title") == correct_policy_title
    results.append({
        "item": "policy_title 正确",
        "score": 5 if policy_title_ok else 0,
        "max_score": 5,
        "passed": policy_title_ok,
        "reason": f"policy_title = {data.get('policy_title')}, 期望 {correct_policy_title}" if not policy_title_ok else "正确"
    })
    total_score += 5 if policy_title_ok else 0

    # 9. impact_level 准确性（15分）
    correct_impact = "high"
    impact_ok = data.get("impact_level") == correct_impact
    results.append({
        "item": "impact_level 正确",
        "score": 15 if impact_ok else 0,
        "max_score": 15,
        "passed": impact_ok,
        "reason": f"impact_level = {data.get('impact_level')}, 期望 high" if not impact_ok else "正确"
    })
    total_score += 15 if impact_ok else 0

    # 10. alert_type 合理性（5分）
    # 期望是"risk_alert"或类似，只要非空且合理即可
    alert_type = data.get("alert_type", "")
    alert_type_ok = isinstance(alert_type, str) and len(alert_type) > 0
    results.append({
        "item": "alert_type 非空且为字符串",
        "score": 5 if alert_type_ok else 0,
        "max_score": 5,
        "passed": alert_type_ok,
        "reason": f"alert_type = {alert_type}" if alert_type_ok else "alert_type 缺失或非字符串"
    })
    total_score += 5 if alert_type_ok else 0

    # 11. 额外加分：是否有 action_required（5分，灵活）
    action_required = data.get("action_required", None)
    action_ok = action_required is not None and isinstance(action_required, str) and len(action_required) > 0
    results.append({
        "item": "存在 action_required 字段（额外）",
        "score": 5 if action_ok else 0,
        "max_score": 5,
        "passed": action_ok,
        "reason": "有 action_required" if action_ok else "无 action_required"
    })
    total_score += 5 if action_ok else 0

    # 12. 最终得分不超过100
    final_score = min(total_score, 100)

    # 写入结果
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump({"total_score": final_score, "details": results}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
