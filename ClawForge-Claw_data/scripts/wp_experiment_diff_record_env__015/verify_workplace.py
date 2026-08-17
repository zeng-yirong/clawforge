import os
import sys
import json
import math

def verify(workspace: str) -> dict:
    details = []
    total = 0

    # 1. 检查产物文件是否存在（10分）
    diff_path = os.path.join(workspace, "ops", "diff_record.json")
    if os.path.isfile(diff_path):
        details.append({
            "item": "产物文件 ops/diff_record.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total += 10
    else:
        details.append({
            "item": "产物文件 ops/diff_record.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 后续检查无法进行，提前返回
        return {
            "total_score": total,
            "details": details
        }

    # 2. 检查 JSON 格式合法性（10分）
    try:
        with open(diff_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "合法 JSON"
        })
        total += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        return {"total_score": total, "details": details}

    # 3. 检查顶层字段完整性（15分）
    required_top = ["batch_id_a", "batch_id_b", "comparison_results"]
    top_ok = all(k in data for k in required_top)
    if top_ok and data["batch_id_a"] == "batch_001" and data["batch_id_b"] == "batch_002":
        details.append({
            "item": "顶层字段完整且 batch 标识正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"包含 {required_top}，且 batch_id_a=batch_001，batch_id_b=batch_002"
        })
        total += 15
    else:
        missing = [k for k in required_top if k not in data]
        details.append({
            "item": "顶层字段完整且 batch 标识正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"缺少字段: {missing} 或 batch 标识不符"
        })

    # 4. 检查 comparison_results 内部每个条目字段完整性（20分）
    if "comparison_results" not in data or not isinstance(data["comparison_results"], list):
        details.append({
            "item": "comparison_results 数组存在且为列表",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "comparison_results 缺失或非列表"
        })
    else:
        results = data["comparison_results"]
        required_sub = ["group_id", "accuracy_diff", "latency_ms_diff", "cost_usd_diff"]
        all_sub_ok = all(
            isinstance(entry, dict) and all(k in entry for k in required_sub)
            for entry in results
        )
        if all_sub_ok and len(results) == 3:
            details.append({
                "item": "每个差异条目包含 group_id、accuracy_diff、latency_ms_diff、cost_usd_diff",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": f"共 {len(results)} 个条目，每个字段完整"
            })
            total += 20
        else:
            details.append({
                "item": "每个差异条目包含 group_id、accuracy_diff、latency_ms_diff、cost_usd_diff",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"条目数={len(results)} 或字段缺失"
            })

    # 5. 数值正确性验证（45分，每个 group 15分）
    # 预期差值（注意：batch_002 - batch_001）
    expected = {
        "group_A": {"accuracy_diff": 0.02, "latency_ms_diff": -5.0, "cost_usd_diff": -0.01},
        "group_B": {"accuracy_diff": -0.03, "latency_ms_diff": 5.0, "cost_usd_diff": 0.01},
        "group_C": {"accuracy_diff": 0.02, "latency_ms_diff": -5.0, "cost_usd_diff": -0.005},
    }

    if "comparison_results" in data and isinstance(data["comparison_results"], list):
        # 构建 group_id 到条目的映射
        group_map = {entry.get("group_id"): entry for entry in data["comparison_results"]}
        groups_found = set(group_map.keys())
        groups_expected = set(expected.keys())
        if groups_found != groups_expected:
            details.append({
                "item": "数值正确性（所有 group）",
                "score": 0,
                "max_score": 45,
                "passed": False,
                "reason": f"group 集合不符，期望 {groups_expected}，实际 {groups_found}"
            })
        else:
            sub_score = 0
            all_passed = True
            for gid in groups_expected:
                entry = group_map[gid]
                exp = expected[gid]
                # 使用 math.isclose 允许微小误差
                acc_ok = math.isclose(entry.get("accuracy_diff", 0), exp["accuracy_diff"], rel_tol=1e-9)
                lat_ok = math.isclose(entry.get("latency_ms_diff", 0), exp["latency_ms_diff"], rel_tol=1e-9)
                cost_ok = math.isclose(entry.get("cost_usd_diff", 0), exp["cost_usd_diff"], rel_tol=1e-9)
                if acc_ok and lat_ok and cost_ok:
                    sub_score += 15
                else:
                    all_passed = False
                    # 给出具体错误信息
                    details.append({
                        "item": f"数值正确性 - {gid}",
                        "score": 0,
                        "max_score": 15,
                        "passed": False,
                        "reason": f"期望 {exp}，实际 accuracy_diff={entry.get('accuracy_diff')}, latency_ms_diff={entry.get('latency_ms_diff')}, cost_usd_diff={entry.get('cost_usd_diff')}"
                    })
            if all_passed:
                details.append({
                    "item": "数值正确性（所有 group）",
                    "score": 45,
                    "max_score": 45,
                    "passed": True,
                    "reason": "所有 group 的差异值精确匹配预期"
                })
                total += 45
            else:
                # 已经添加了具体错误条目，这里加一个总条目（但注意前面可能已加具体，这里避免重复）
                # 实际上我们已经在循环中加了具体错误，不需要再加总条目，直接汇总
                pass

    # 确保 details 中有数值正确性的总条目，如果前面已经添加了具体 group 错误，则这里不再添加
    # 检查是否已经包含 "数值正确性（所有 group）" 条目，若没有则说明之前有具体错误，需添加汇总
    if not any(d["item"] == "数值正确性（所有 group）" for d in details):
        # 已存在具体错误，但需要统计已分配的分数
        # 计算已从具体 group 获得的分数
        group_scores = [d["score"] for d in details if d["item"].startswith("数值正确性 - ")]
        sub_total = sum(group_scores)
        # 这部分分数已经在具体条目中体现，但为了总分正确，我们只通过具体条目加分，这里不需要再重复加
        # 但注意我们之前循环中直接加了15分到sub_score，但没有加到total？需要修正：我们应在具体条目中更新 total
        # 由于我们之前没在具体条目中更新total，而是在all_passed时加了45，否则没加。需要重构逻辑统一。
        # 简单起见，重新实现数值正确性部分：
        # 先删除前面错误实现，重写下面的代码。
        pass

    # 重新实现数值正确性部分（覆盖上面可能不完整的逻辑）
    # 清除之前可能添加的数值相关细节
    details = [d for d in details if not d["item"].startswith("数值正确性")]
    if "comparison_results" in data and isinstance(data["comparison_results"], list):
        group_map = {entry.get("group_id"): entry for entry in data["comparison_results"]}
        groups_expected = set(expected.keys())
        actual_groups = set(group_map.keys())
        if actual_groups != groups_expected:
            details.append({
                "item": "数值正确性 - group 集合",
                "score": 0,
                "max_score": 45,
                "passed": False,
                "reason": f"group 集合不符，期望 {groups_expected}，实际 {actual_groups}"
            })
        else:
            sub_score = 0
            all_ok = True
            for gid in groups_expected:
                entry = group_map[gid]
                exp = expected[gid]
                acc_ok = math.isclose(entry.get("accuracy_diff"), exp["accuracy_diff"], rel_tol=1e-9)
                lat_ok = math.isclose(entry.get("latency_ms_diff"), exp["latency_ms_diff"], rel_tol=1e-9)
                cost_ok = math.isclose(entry.get("cost_usd_diff"), exp["cost_usd_diff"], rel_tol=1e-9)
                if not (acc_ok and lat_ok and cost_ok):
                    all_ok = False
                    details.append({
                        "item": f"数值正确性 - {gid}",
                        "score": 0,
                        "max_score": 15,
                        "passed": False,
                        "reason": f"期望 {exp}，实际 accuracy_diff={entry.get('accuracy_diff')}, latency_ms_diff={entry.get('latency_ms_diff')}, cost_usd_diff={entry.get('cost_usd_diff')}"
                    })
                else:
                    sub_score += 15
            if all_ok:
                details.append({
                    "item": "数值正确性（所有 group）",
                    "score": 45,
                    "max_score": 45,
                    "passed": True,
                    "reason": "所有 group 差异值精确匹配"
                })
            # 注意：具体 group 的错误条目已经添加，但 sub_score 只用于计算，实际上分数通过“所有group”条目发放
            # 为了简单，当全部正确时给45分，否则每个错误 group 给0分，但整体不重复给分。
            # 上面的代码当 all_ok=False 时，已经添加了具体错误条目，但未添加总条目，且未分配任何分数。
            # 需要给每个错误 group 0分（已经在具体条目中体现），并且总分数应为0。
            if not all_ok:
                # 确保没有总条目，并且总分数为0
                # 但已经添加了具体条目，这些条目的分数都是0，总score=0
                pass
        # 更新 total：需要统计所有 details 的 score 和
        # 但由于我们在前面已经加了其他分数，这里重新计算 total
        total = sum(d["score"] for d in details)
    else:
        details.append({
            "item": "数值正确性（所有 group）",
            "score": 0,
            "max_score": 45,
            "passed": False,
            "reason": "comparison_results 不可用"
        })

    # 重新计算总分数
    total = sum(d["score"] for d in details)
    return {
        "total_score": total,
        "details": details
    }

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入评分文件
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
