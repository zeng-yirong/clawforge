import sys
import os
import json
import csv
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)  # 切换到工作区根目录

    # 初始化得分
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录结构 (10分)
    dir_score = 0
    dir_max = 10
    required_dirs = ["ops", "data", "data/requests", "data/assets"]
    missing_dirs = []
    for d in required_dirs:
        if not os.path.isdir(d):
            missing_dirs.append(d)
    if not missing_dirs:
        dir_score = dir_max
        details.append({
            "item": "Directory structure",
            "score": dir_max,
            "max_score": dir_max,
            "passed": True,
            "reason": "All required directories exist."
        })
    else:
        dir_score = 0
        details.append({
            "item": "Directory structure",
            "score": 0,
            "max_score": dir_max,
            "passed": False,
            "reason": f"Missing directories: {missing_dirs}"
        })
    total_score += dir_score

    # 2. 检查结果文件 ops/deny_queue.json 存在 (10分)
    file_score = 0
    file_max = 10
    deny_file = "ops/deny_queue.json"
    if os.path.isfile(deny_file):
        file_score = file_max
        details.append({
            "item": "Output file existence",
            "score": file_max,
            "max_score": file_max,
            "passed": True,
            "reason": f"{deny_file} present."
        })
    else:
        file_score = 0
        details.append({
            "item": "Output file existence",
            "score": 0,
            "max_score": file_max,
            "passed": False,
            "reason": f"{deny_file} not found."
        })
    total_score += file_score

    # 3. 解析结果文件格式合法 (10分)
    format_score = 0
    format_max = 10
    try:
        with open(deny_file, "r") as f:
            data = json.load(f)
        # 应该是字典，且包含一个列表字段，比如 "deny_ids" 或 "targets" 等
        # 我们允许多种合理结构：确保顶层是字典，并且至少有一个列表值
        if isinstance(data, dict):
            # 找出第一个列表字段
            list_field = None
            for key, val in data.items():
                if isinstance(val, list):
                    list_field = key
                    break
            if list_field is not None:
                deny_ids = data[list_field]
                format_score = format_max
                details.append({
                    "item": "Output file format",
                    "score": format_max,
                    "max_score": format_max,
                    "passed": True,
                    "reason": f"Valid JSON with list field '{list_field}'."
                })
            else:
                details.append({
                    "item": "Output file format",
                    "score": 0,
                    "max_score": format_max,
                    "passed": False,
                    "reason": "JSON object does not contain a list field."
                })
        else:
            details.append({
                "item": "Output file format",
                "score": 0,
                "max_score": format_max,
                "passed": False,
                "reason": "Top-level is not a dict."
            })
    except Exception as e:
        details.append({
            "item": "Output file format",
            "score": 0,
            "max_score": format_max,
            "passed": False,
            "reason": f"Cannot parse JSON: {e}"
        })
    total_score += format_score

    # 如果文件格式不合法，无法继续验证内容，直接返回
    if format_score < format_max:
        details.append({
            "item": "Content correctness",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "Skipped due to format error."
        })
        final_score = total_score
    else:
        # 4. 通过重新计算得到正确拒绝列表 (基于env_builder产生的数据，使用相同逻辑)
        # 读取资产
        with open("data/assets/assets.json", "r") as f:
            assets_data = json.load(f)
        assets = assets_data.get("assets", {})
        # 读取请求
        with open("data/requests/requests.json", "r") as f:
            reqs_data = json.load(f)
        requests_list = reqs_data.get("requests", [])

        correct_ids = set()
        for req in requests_list:
            # 必须包含必要字段
            rid = req.get("request_id")
            channel = req.get("channel")
            risk_level = req.get("risk_level")
            risk_type = req.get("risk_type")
            target_asset_id = req.get("target_asset_id")
            status = req.get("status")
            # 跳过缺少字段的记录
            if not all([rid, channel, risk_level, risk_type, target_asset_id, status]):
                continue
            # 只处理外部请求
            if channel != "external":
                continue
            # 风险等级必须是小写 high
            if risk_level != "high":
                continue
            # 风险类型必须是 external_access
            if risk_type != "external_access":
                continue
            # 目标资产必须存在且 classification 为 unpublished 且 asset_type 符合
            asset = assets.get(target_asset_id)
            if asset is None:
                continue
            if asset.get("classification") != "unpublished":
                continue
            if asset.get("asset_type") not in ("technical_plan", "finance_archive"):
                continue
            # 状态必须是 open 或 pending（未处理）
            if status not in ("open", "pending"):
                continue
            correct_ids.add(rid)

        # 获取 agent 提交的 ID 列表
        agent_ids = set()
        # 上面已经解析了 deny_ids
        for item in deny_ids:
            if isinstance(item, str):
                agent_ids.add(item)
            elif isinstance(item, dict):
                # 尝试从 dict 中提取 request_id
                if "request_id" in item:
                    agent_ids.add(item["request_id"])
                # 也可以其他字段，但简单起见只处理字符串和带request_id的字典

        # 计算正确性分数 (70分)
        content_max = 70
        # 正确命中：agent 包含 correct_ids 中的每一个
        correct_hit = correct_ids & agent_ids
        false_positive = agent_ids - correct_ids
        false_negative = correct_ids - agent_ids

        # 权重：每个正确ID给 70 / len(correct_ids) 分，但可能有0个正确ID时的处理
        if len(correct_ids) == 0:
            # 如果环境没有任何正确ID，agent 提交空集则满分，否则0分
            if len(agent_ids) == 0:
                content_score = content_max
                reason = "No correct IDs expected, agent correctly submitted empty list."
            else:
                content_score = 0
                reason = f"No correct IDs expected, but agent submitted {agent_ids}."
        else:
            per_item = content_max / len(correct_ids)
            hit_score = len(correct_hit) * per_item
            # 误报扣分：每个误报扣 per_item 分，最多扣到0
            false_positive_penalty = len(false_positive) * per_item
            content_score = max(0, round(hit_score - false_positive_penalty))
            reason_parts = []
            if correct_hit:
                reason_parts.append(f"Hit: {sorted(correct_hit)}")
            if false_negative:
                reason_parts.append(f"Missed: {sorted(false_negative)}")
            if false_positive:
                reason_parts.append(f"Wrong extra: {sorted(false_positive)}")
            reason = "; ".join(reason_parts) if reason_parts else "All correct."

        details.append({
            "item": "Content correctness",
            "score": content_score,
            "max_score": content_max,
            "passed": content_score == content_max,
            "reason": reason
        })
        total_score += content_score

    # 总分为整数，不超过100
    total_score = min(100, total_score)

    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score written: {total_score}/100")
    return total_score

if __name__ == "__main__":
    main()
