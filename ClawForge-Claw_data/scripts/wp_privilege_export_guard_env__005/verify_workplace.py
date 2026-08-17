#!/usr/bin/env python3
"""
Workplace verification for wp_privilege_export_guard_env__005.
Checks that the agent correctly identifies privilege-violating bulk-export requests
and outputs their IDs to ops/deny_requests.json.
"""
import json
import os
import sys
import pathlib

def verify_workplace(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # Helper to construct paths
    def wspath(relative: str) -> str:
        return os.path.join(workspace, relative)

    # ---- 1. 目录结构检查 (10分) ----
    item = {"item": "Required directories exist", "max_score": 10}
    required_dirs = ["data", "data/assets", "data/requests", "ops", "logs"]
    missing_dirs = [d for d in required_dirs if not os.path.isdir(wspath(d))]
    if missing_dirs:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Missing directories: {missing_dirs}"
    else:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "All required directories present"
    details.append(item)
    total_score += item["score"]

    # ---- 2. 核心数据文件存在且合法 (10分) ----
    item = {"item": "Core data files are valid JSON", "max_score": 10}
    required_files = [
        "data/accounts.json",
        "data/assets/assets.json",
        "data/requests/requests.json"
    ]
    parse_errors = []
    for f in required_files:
        path = wspath(f)
        if not os.path.isfile(path):
            parse_errors.append(f"{f} missing")
        else:
            try:
                with open(path) as fh:
                    json.load(fh)
            except Exception as e:
                parse_errors.append(f"{f} invalid JSON: {e}")
    if parse_errors:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "; ".join(parse_errors)
    else:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "All core files valid"
    details.append(item)
    total_score += item["score"]

    # ---- 3. 输出文件存在且合法 (10分) ----
    item = {"item": "ops/deny_requests.json exists and is valid JSON", "max_score": 10}
    output_path = wspath("ops/deny_requests.json")
    if not os.path.isfile(output_path):
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "File not found"
        details.append(item)
        total_score += item["score"]
        # 如果输出不存在，后续检查无法进行，但为了完整性继续？
        # 这里我们直接返回当前分数并结束，避免崩溃
        # 但按照设计，我们继续检查但跳过后续依赖项？更好的做法是返回当前分数
        # 我们继续但跳过引用该文件的检查，但为了代码健壮，提前返回
        final_score = total_score  # 最多20分
        # 写入分数
        result = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return
    try:
        with open(output_path) as f:
            deny_list = json.load(f)
        if not isinstance(deny_list, list):
            raise ValueError("deny_list is not a list")
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Valid JSON list"
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Invalid JSON: {e}"
    details.append(item)
    total_score += item["score"]

    # ---- 4. 核心推理：正确识别越权请求 (总分60分, 每正确识别一个越权请求得15分, 误报扣分) ----
    # 越权请求定义：请求的actor对应的账户权限中不包含目标资产所需的read_policy。
    # 资产所需的read_policy由assets.json中的read_policy字段给出，但简化：我们直接与permissions比较。
    # 更精确：资产asset_type对应permissions中的关键字（例如 architecture_data 对应 architecture_data_read? 但permissions直接包含类型？）
    # 但在我们的数据集里，permissions是 ["customer_data_read", "architecture_data_read"]，而资产asset_type是 "customer_data" 或 "architecture_data"。
    # 规则：actor的permissions必须包含 "customer_data_read" 才能访问客户资产，包含 "architecture_data_read" 才能访问架构资产。
    # 同时，如果资产类型是 "general"，则不受限（但我们的资产中没有general的请求，忽略）。
    # 预计算真实答案：
    # 从env_builder中提取数据（避免硬编码，从文件读）
    with open(wspath("data/accounts.json")) as f:
        accounts_data = json.load(f)["accounts"]
    with open(wspath("data/assets/assets.json")) as f:
        assets_data = json.load(f)["assets"]
    with open(wspath("data/requests/requests.json")) as f:
        requests_data = json.load(f)["requests"]

    # 建立映射
    acc_perm = {a["account_id"]: a["permissions"] for a in accounts_data}
    # 用display_name作为actor_name（env中actor_name就是display_name）
    acc_by_name = {a["display_name"]: a for a in accounts_data}
    asset_type_map = {a["asset_id"]: a["asset_type"] for a in assets_data}
    # 权限映射：资产类型到所需权限字符串
    type_to_perm = {
        "architecture_data": "architecture_data_read",
        "customer_data": "customer_data_read",
        "general": "general_read"
    }

    # 真实越权请求ID (只考虑status为pending的请求)
    true_violations = set()
    for req in requests_data:
        if req["status"] != "pending":
            continue
        actor = req["actor_name"]
        target = req["target_asset_id"]
        if target not in asset_type_map:
            # 目标资产不存在，跳过（视为无法判断，但不越权）
            continue
        asset_type = asset_type_map[target]
        required_perm = type_to_perm.get(asset_type)
        if required_perm is None:
            continue  # 未知类型，略过
        # 查找actor的权限
        account = acc_by_name.get(actor)
        if account is None:
            continue
        if required_perm not in account["permissions"]:
            true_violations.add(req["request_id"])

    # 检查输出列表
    agent_violations = set(deny_list)
    # 计算正确识别的越权请求
    correctly_identified = true_violations & agent_violations
    # 误报：agent上报了但不是真正越权的
    false_positives = agent_violations - true_violations
    # 遗漏
    false_negatives = true_violations - agent_violations

    item = {"item": "Correctly identified privileged violations (pending + no permission)", "max_score": 60}
    # 每正确一个得15分，最多60（四个越权请求：req_003, req_004, req_005，注意req_008目标不存在，不计入越权）
    # 实际上，正确的越权请求有：req_003, req_004, req_005  (三个? 让我们检查: Bob无架构权限请求ast_001 => 越权；Carol无客户权限请求ast_002 => 越权；Dave无任何权限请求ast_001 => 越权)
    # 但Alice和Eve有完全权限，正常。req_008目标不存在，不越权。
    # 所以 true_violations = {'req_003', 'req_004', 'req_005'}  3个
    true_count = len(true_violations)
    correct_count = len(correctly_identified)
    fp_count = len(false_positives)
    fn_count = len(false_negatives)
    # 得分：每个正确+20分? 但总60分，3个正确每个20分正好60。如果有4个则每个15分。
    # 这里只有3个，我们按每个20分算，满分60。如果有4个则分配15分一个。
    if true_count > 0:
        per_correct = 60 // true_count  # 整数除法，20
        remaining = 60 - per_correct * true_count
        # 我们简化为每正确一个得20分
        base = correct_count * 20
    else:
        base = 0
    # 误报扣分：每个误报扣5分（最多扣到0）
    penalty = min(fp_count * 5, base)
    final_42 = max(base - penalty, 0)
    # 如果遗漏则每个扣2分（但已有正确得分考虑，实际上遗漏已经体现在correct_count少，我们不再额外扣，因为base已经少了）
    # 但我们也可以加上遗漏扣分，但为了简单，不再重复扣。最终得分就是final_42
    item["score"] = final_42
    item["passed"] = (final_42 == 60)  # 完美匹配
    item["reason"] = f"Correct: {correct_count}/{true_count}, False positive: {fp_count}, False negative: {fn_count}"
    details.append(item)
    total_score += item["score"]

    # ---- 5. 额外检查：输出列表不能包含已denied的请求（req_006） (10分) ----
    item = {"item": "No already-denied requests included (should ignore req_006)", "max_score": 10}
    if "req_006" in agent_violations:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "Included req_006 which was already denied"
    else:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Correctly excluded req_006"
    details.append(item)
    total_score += item["score"]

    # 总分限制在0-100
    total_score = min(max(total_score, 0), 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
