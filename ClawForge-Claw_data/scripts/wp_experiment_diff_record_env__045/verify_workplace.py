import sys
import os
import json
import csv
import math

def verify(workspace):
    """验证 agent 生成的 ops/diff_record.json 是否与预期一致"""
    details = []
    total_score = 0

    # ---------- 检查必要目录 ----------
    ops_dir = os.path.join(workspace, "ops")
    if not os.path.isdir(ops_dir):
        details.append({
            "item": "目录 ops/ 存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ 目录不存在"
        })
        total_score += 0
    else:
        details.append({
            "item": "目录 ops/ 存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/ 目录已创建"
        })
        total_score += 5

    # ---------- 检查文件存在性 ----------
    diff_path = os.path.join(workspace, "ops", "diff_record.json")
    if not os.path.isfile(diff_path):
        details.append({
            "item": "ops/diff_record.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        total_score += 0
        # 后续检查无法进行，直接输出
        _write_score(details, total_score)
        return

    details.append({
        "item": "ops/diff_record.json 存在",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "文件存在"
    })
    total_score += 10

    # ---------- 解析 JSON ----------
    try:
        with open(diff_path, "r") as f:
            content = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        total_score += 0
        _write_score(details, total_score)
        return

    details.append({
        "item": "JSON 格式合法",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON 格式正确"
    })
    total_score += 10

    # ---------- 检查结构：必须是字典，包含组ID作为键 ----------
    if not isinstance(content, dict):
        details.append({
            "item": "JSON 顶层结构为字典",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"顶层是 {type(content).__name__}，期望 dict"
        })
        total_score += 0
    else:
        details.append({
            "item": "JSON 顶层结构为字典",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "顶层是字典"
        })
        total_score += 10

    # ---------- 检查必须包含的组 ----------
    expected_groups = ["group_a", "group_b", "group_c"]
    missing_groups = [g for g in expected_groups if g not in content]
    extra_groups = [g for g in content if g not in expected_groups]  # 允许额外组，但扣分（因为 agent 应只关心 batch_001/002 共有的组）

    # 组存在性计分：每个必须组 5 分，共15
    group_score = 0
    for g in expected_groups:
        if g in content:
            group_score += 5
            reason = f"包含组 {g}"
        else:
            reason = f"缺少组 {g}"
        details.append({
            "item": f"必须组 {g} 存在",
            "score": 5 if g in content else 0,
            "max_score": 5,
            "passed": g in content,
            "reason": reason
        })
    total_score += group_score

    # ---------- 检查每个组的指标 ----------
    # 预期差值 (batch_002 - batch_001)
    expected_diffs = {
        "group_a": {"accuracy_diff": round(0.945 - 0.923, 3), "latency_ms_diff": round(42.8 - 45.2, 1), "cost_usd_diff": round(0.38 - 0.35, 2)},
        "group_b": {"accuracy_diff": round(0.902 - 0.887, 3), "latency_ms_diff": round(49.5 - 52.1, 1), "cost_usd_diff": round(0.44 - 0.41, 2)},
        "group_c": {"accuracy_diff": round(0.967 - 0.951, 3), "latency_ms_diff": round(36.2 - 38.7, 1), "cost_usd_diff": round(0.32 - 0.29, 2)},
    }
    diff_score = 0
    for g in expected_groups:
        if g not in content:
            continue
        item = content[g]
        # 检查三个指标字段
        for metric in ["accuracy_diff", "latency_ms_diff", "cost_usd_diff"]:
            if metric not in item:
                details.append({
                    "item": f"组 {g} 包含 {metric}",
                    "score": 0,
                    "max_score": 5,
                    "passed": False,
                    "reason": f"缺少字段 {metric}"
                })
                continue
            expected_val = expected_diffs[g][metric]
            actual_val = item[metric]
            # 允许浮点误差 1e-9
            if isinstance(actual_val, (int, float)) and math.isclose(actual_val, expected_val, rel_tol=1e-9):
                details.append({
                    "item": f"组 {g} {metric} 数值正确",
                    "score": 5,
                    "max_score": 5,
                    "passed": True,
                    "reason": f"值为 {actual_val} (期望 {expected_val})"
                })
                diff_score += 5
            else:
                details.append({
                    "item": f"组 {g} {metric} 数值正确",
                    "score": 0,
                    "max_score": 5,
                    "passed": False,
                    "reason": f"值为 {actual_val} (期望 {expected_val})"
                })
    total_score += diff_score

    # ---------- 额外组扣分（1分/个，最多扣5分） ----------
    extra_penalty = min(len(extra_groups), 5) * (-1)
    if extra_penalty < 0:
        details.append({
            "item": "额外组未出现在预期中",
            "score": extra_penalty,
            "max_score": 0,
            "passed": False,
            "reason": f"存在非必要组: {extra_groups}，扣除 {abs(extra_penalty)} 分"
        })
        total_score += extra_penalty

    # ---------- 检查是否有多余字段（字段白名单：accuracy_diff, latency_ms_diff, cost_usd_diff） ----------
    allowed_fields = {"accuracy_diff", "latency_ms_diff", "cost_usd_diff"}
    extra_fields_penalty = 0
    for g in content:
        if g in expected_groups:
            for k in content[g]:
                if k not in allowed_fields:
                    extra_fields_penalty -= 2
                    details.append({
                        "item": f"组 {g} 无多余字段",
                        "score": -2,
                        "max_score": 0,
                        "passed": False,
                        "reason": f"存在不在预期中的字段: {k}"
                    })
    total_score += extra_fields_penalty

    # ---------- 最终总分限定在 0-100 ----------
    total_score = max(0, min(100, total_score))
    details.append({
        "item": "总分",
        "score": total_score,
        "max_score": 100,
        "passed": total_score >= 80,  # 80以上算通过，但这里只是显示
        "reason": f"最终得分 {total_score}/100"
    })

    _write_score(details, total_score)

def _write_score(details, total_score):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
