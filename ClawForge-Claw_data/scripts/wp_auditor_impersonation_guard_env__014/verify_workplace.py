import sys
import os
import json
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = pathlib.Path(workspace)

    # 结果累计
    details = []
    total_score = 0

    # --- 检查 ops 目录是否存在 (10分) ---
    ops_dir = workspace / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops_dir_exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ directory found"})
        total_score += 10
    else:
        details.append({"item": "ops_dir_exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ directory missing"})

    # --- 检查 high_risk_denials.json 是否存在 (10分) ---
    result_file = ops_dir / "high_risk_denials.json"
    if result_file.is_file():
        details.append({"item": "result_file_exists", "score": 10, "max_score": 10, "passed": True, "reason": "file exists"})
        total_score += 10
    else:
        details.append({"item": "result_file_exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # 后续无法继续，直接写总分并退出
        _finalize(workspace, total_score, details)
        return

    # --- 解析 JSON 合法性 (10分) ---
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        details.append({"item": "json_valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
        total_score += 10
    except Exception as e:
        details.append({"item": "json_valid", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        _finalize(workspace, total_score, details)
        return

    # --- 检查是否为数组 (10分) ---
    if isinstance(data, list):
        details.append({"item": "is_array", "score": 10, "max_score": 10, "passed": True, "reason": "top-level is list"})
        total_score += 10
    else:
        details.append({"item": "is_array", "score": 0, "max_score": 10, "passed": False, "reason": f"expected list, got {type(data).__name__}"})
        _finalize(workspace, total_score, details)
        return

    # 预期被拒绝的 request_id (冒充审计员且不在真实审计员名单中)
    expected_denied = {"req-003", "req-004", "req-006", "req-007"}
    # 真正审计员的请求 ID（不应出现在结果中）
    expected_allowed = {"req-001", "req-002"}
    # 其他无关请求
    other_ids = {"req-005"}

    # 检查数组每个元素是字符串 (10分)
    all_strings = all(isinstance(item, str) for item in data)
    if all_strings:
        details.append({"item": "all_strings", "score": 10, "max_score": 10, "passed": True, "reason": "all elements are strings"})
        total_score += 10
    else:
        details.append({"item": "all_strings", "score": 0, "max_score": 10, "passed": False, "reason": "non-string element found"})
        # 仍然继续检查内容，但对非字符串项视为无效

    # 计算实际集合
    actual_set = set(item for item in data if isinstance(item, str))

    # 检查是否包含所有预期被拒绝的 ID (20分)
    missing = expected_denied - actual_set
    extra = actual_set - expected_denied
    if not missing and not extra.intersection(expected_allowed):
        # 没有漏掉，也没有包含真正的审计员请求
        details.append({"item": "contains_all_expected", "score": 20, "max_score": 20, "passed": True, "reason": "all expected denied IDs present"})
        total_score += 20
    else:
        reason_parts = []
        if missing:
            reason_parts.append(f"missing IDs: {sorted(missing)}")
        if extra:
            # 检查 extra 中是否包含不应出现的 true auditor 请求
            forbidden = extra.intersection(expected_allowed)
            if forbidden:
                reason_parts.append(f"contains forbidden true auditor IDs: {sorted(forbidden)}")
        details.append({"item": "contains_all_expected", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(reason_parts)})

    # 检查是否包含任何真正的审计员请求 (20分)
    forbidden_present = actual_set.intersection(expected_allowed)
    if not forbidden_present:
        details.append({"item": "no_true_auditor_included", "score": 20, "max_score": 20, "passed": True, "reason": "no legitimate auditor requests included"})
        total_score += 20
    else:
        details.append({"item": "no_true_auditor_included", "score": 0, "max_score": 20, "passed": False, "reason": f"improperly included: {sorted(forbidden_present)}"})

    # 额外奖励：没有多余的非预期 ID (但不在 expected set 中的也不算大错，可酌情扣分)
    unexpected = actual_set - expected_denied - expected_allowed - other_ids
    if unexpected:
        details.append({"item": "no_extra_unexpected", "score": 0, "max_score": 10, "passed": False, "reason": f"unexpected IDs present: {sorted(unexpected)}"})
        # 从 total_score 扣除？实际上总分满分100，我们已经分配了90，这里加一项扣分
        # 修改：将最后一项设为扣分项，直接在总分中体现
        # 更稳健：在 details 里记录，总分直接计算
        pass  # 上面已经计了0分

    _finalize(workspace, total_score, details)

def _finalize(workspace, total_score, details):
    # 确保总分在0-100
    total_score = max(0, min(total_score, 100))
    score_data = {
        "total_score": total_score,
        "details": details
    }
    score_path = workspace / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Score written to {score_path}: {total_score}")

if __name__ == "__main__":
    main()
