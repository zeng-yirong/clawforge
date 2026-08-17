import json
import os
import sys
import re

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(WORKSPACE, rel_path)
    if not os.path.exists(full):
        return None
    try:
        with open(full, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return None

def score():
    details = []
    total = 0

    # 1. 检查 ops 目录是否存在 (10 分)
    ops_dir = os.path.join(WORKSPACE, "ops")
    dir_ok = os.path.isdir(ops_dir)
    details.append({
        "item": "ops 目录存在",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "目录存在" if dir_ok else "ops/ 目录未创建"
    })
    total += 10 if dir_ok else 0

    # 2. 检查 ops/postmortem.json 是否存在且合法 JSON (20 分)
    result_path = "ops/postmortem.json"
    result_full = os.path.join(WORKSPACE, result_path)
    exists = os.path.isfile(result_full)
    if not exists:
        details.append({
            "item": "产物文件存在",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"{result_path} 不存在"
        })
        # 后续无法检查，直接结束
        out = {"total_score": total, "details": details}
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump(out, f, indent=2)
        return

    data = load_json(result_path)
    valid_json = data is not None
    if not valid_json:
        details.append({
            "item": "产物文件是合法 JSON",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "文件存在但非合法 JSON 或为空"
        })
        total += 0
    else:
        # 检查是否为 dict
        if not isinstance(data, dict):
            details.append({
                "item": "产物文件是合法 JSON",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "JSON 不是 object"
            })
            valid_json = False
        else:
            details.append({
                "item": "产物文件是合法 JSON",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "JSON 解析成功且为 object"
            })
            total += 20

    if not valid_json:
        out = {"total_score": total, "details": details}
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump(out, f, indent=2)
        return

    # 3. 检查 root_cause 字段 (30 分)
    root_cause = data.get("root_cause", None)
    expected_root_cause = "OutOfMemoryError"
    rc_ok = (root_cause == expected_root_cause)
    details.append({
        "item": "root_cause 正确",
        "score": 30 if rc_ok else 0,
        "max_score": 30,
        "passed": rc_ok,
        "reason": f"根因字段值 '{root_cause}' {'正确' if rc_ok else f'应为 {expected_root_cause}'}"
    })
    total += 30 if rc_ok else 0

    # 4. 检查 repair_plan 字段 (30 分)
    repair_plan = data.get("repair_plan", None)
    expected_repair = "Increase heap to 2GB and enable garbage collection logging"
    rp_ok = (repair_plan == expected_repair)
    details.append({
        "item": "repair_plan 正确",
        "score": 30 if rp_ok else 0,
        "max_score": 30,
        "passed": rp_ok,
        "reason": f"修复方案字段值 '{repair_plan}' {'正确' if rp_ok else f'应为 {expected_repair}'}"
    })
    total += 30 if rp_ok else 0

    # 5. 额外扣分项：如果存在多余字段（除了 root_cause, repair_plan 之外），每个扣 2 分，最多扣 10 分
    allowed = {"root_cause", "repair_plan"}
    extra = set(data.keys()) - allowed
    extra_penalty = min(len(extra) * 2, 10)
    if extra_penalty > 0:
        details.append({
            "item": "无多余字段",
            "score": -extra_penalty,
            "max_score": 0,
            "passed": False,
            "reason": f"存在多余字段: {extra}, 扣除 {extra_penalty} 分"
        })
        total = max(0, total - extra_penalty)
    else:
        details.append({
            "item": "无多余字段",
            "score": 0,
            "max_score": 0,
            "passed": True,
            "reason": "仅包含要求的字段"
        })

    # 6. 加分项：如果包含 fault_id 且值为 fault_003，加 10 分 (不扣分，仅加分)
    fault_id_val = data.get("fault_id", None)
    if fault_id_val == "fault_003":
        details.append({
            "item": "包含 fault_id 且正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "fault_id 字段存在且值为 fault_003"
        })
        total += 10
    else:
        details.append({
            "item": "包含 fault_id 且正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未提供 fault_id 或值不正确"
        })

    # 总分上限 100
    total = min(total, 100)

    out = {"total_score": total, "details": details}
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    score()
