import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace)
    
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目标文件是否存在 (10分)
    target_file = workspace / "data/labels/tier_labels.json"
    if target_file.is_file():
        details.append({"item": "文件 data/labels/tier_labels.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "文件 data/labels/tier_labels.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未找到"})
        # 缺失则结束，后面无法检查
        write_score(total_score, details)
        return

    # 2. JSON 格式合法 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "能正确解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(total_score, details)
        return

    # 3. 必须是列表 (5分)
    if isinstance(data, list):
        details.append({"item": "数据是列表", "score": 5, "max_score": 5, "passed": True, "reason": "类型正确"})
        total_score += 5
    else:
        details.append({"item": "数据是列表", "score": 0, "max_score": 5, "passed": False, "reason": f"类型为 {type(data).__name__}"})
        # 继续检查，可能会失败

    # 4. 列表长度应为5 (5分) — 应包含全部5个真实客户，不应包含Ghost
    if len(data) == 5:
        details.append({"item": "列表长度正确（5个客户）", "score": 5, "max_score": 5, "passed": True, "reason": "长度为5"})
        total_score += 5
    else:
        details.append({"item": "列表长度正确（5个客户）", "score": 0, "max_score": 5, "passed": False, "reason": f"实际长度 {len(data)}"})

    # 5. 每个元素必须有customer_id和tier字段 (10分)
    field_ok = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_ok = False
            break
        if "customer_id" not in entry or "tier" not in entry:
            field_ok = False
            break
    if field_ok:
        details.append({"item": "每个条目包含 customer_id 和 tier", "score": 10, "max_score": 10, "passed": True, "reason": "字段完整"})
        total_score += 10
    else:
        details.append({"item": "每个条目包含 customer_id 和 tier", "score": 0, "max_score": 10, "passed": False, "reason": "缺少必要字段"})

    # 6. 验证每个客户的标签 (50分) — 每个客户10分，共5个
    # 预期规则：
    # C001 CarePulse: 消费8000, active 5 -> Bronze (消费<10000)
    # C002 LedgerFlow: 消费15000, active 100 -> Bronze (active>90)
    # C003 HealthPlus: 消费50000, active 10 -> Gold
    # C004 FinTechX: 消费25000, active 60 -> Silver
    # C005 OldData: 无消费 -> Unclassified
    expected = {
        "C001": "Bronze",
        "C002": "Bronze",
        "C003": "Gold",
        "C004": "Silver",
        "C005": "Unclassified"
    }
    # 构建查找字典
    result_map = {}
    for entry in data:
        cid = entry.get("customer_id")
        tier = entry.get("tier")
        if cid is not None:
            result_map[cid] = tier

    correct_count = 0
    for cid, expected_tier in expected.items():
        actual = result_map.get(cid)
        if actual == expected_tier:
            correct_count += 1
        else:
            # 记录错误理由
            pass

    # 给每个客户正确10分，错误0分
    for cid, expected_tier in expected.items():
        actual = result_map.get(cid)
        passed = (actual == expected_tier)
        if passed:
            details.append({"item": f"客户 {cid} 标签正确为 {expected_tier}", "score": 10, "max_score": 10, "passed": True, "reason": f"actual={actual}"})
            total_score += 10
        else:
            details.append({"item": f"客户 {cid} 标签正确为 {expected_tier}", "score": 0, "max_score": 10, "passed": False, "reason": f"actual={actual}"})

    # 7. 额外检查：没有Ghost客户 (5分)
    if "GHOST" not in result_map:
        details.append({"item": "不应包含GHOST客户", "score": 5, "max_score": 5, "passed": True, "reason": "无GHOST"})
        total_score += 5
    else:
        details.append({"item": "不应包含GHOST客户", "score": 0, "max_score": 5, "passed": False, "reason": "包含GHOST"})

    # 总分可能超出，但max_total=100，我们按实际得分写，但限制在100内
    total_score = min(total_score, 100)
    write_score(total_score, details)

def write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
