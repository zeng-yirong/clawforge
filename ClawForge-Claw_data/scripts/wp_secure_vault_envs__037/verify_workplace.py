import sys
import json
import os

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 辅助函数
    def add_item(name, score, max_score, passed, reason=""):
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. 检查必要目录/文件是否存在（10分）
    dirs_exist = all(os.path.isdir(os.path.join(workspace, d)) for d in ["data", "ops"])
    if dirs_exist:
        total_score += add_item("目录结构 data/ ops/ 存在", 5, 5, True)
    else:
        total_score += add_item("目录结构 data/ ops/ 存在", 0, 5, False, "缺少必要目录")

    vault_path = os.path.join(workspace, "data/vault_entries.json")
    strong_path = os.path.join(workspace, "data/strong_passwords.txt")
    report_path = os.path.join(workspace, "ops/audit_report.json")
    if os.path.isfile(report_path):
        total_score += add_item("产物文件 ops/audit_report.json 存在", 5, 5, True)
    else:
        total_score += add_item("产物文件 ops/audit_report.json 存在", 0, 5, False, "文件缺失")
        # 如果产物缺失，后续无法验证，直接返回
        _write_score(total_score, details)
        return

    # 2. 读取原始数据
    try:
        with open(vault_path, "r") as f:
            vault_entries = json.load(f)
    except Exception as e:
        total_score += add_item("读取 data/vault_entries.json", 0, 5, False, str(e))
        _write_score(total_score, details)
        return
    total_score += add_item("读取 data/vault_entries.json 成功", 5, 5, True)

    try:
        with open(strong_path, "r") as f:
            strong_passwords = [line.strip() for line in f if line.strip()]
    except Exception as e:
        total_score += add_item("读取 data/strong_passwords.txt", 0, 5, False, str(e))
        _write_score(total_score, details)
        return
    total_score += add_item("读取 data/strong_passwords.txt 成功", 5, 5, True)

    # 3. 解析产物
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
    except Exception as e:
        total_score += add_item("产物 JSON 合法", 0, 10, False, f"JSON解析失败: {e}")
        _write_score(total_score, details)
        return
    if not isinstance(report, list):
        total_score += add_item("产物是数组", 0, 10, False, "应为列表")
        _write_score(total_score, details)
        return
    total_score += add_item("产物 JSON 合法且为数组", 10, 10, True)

    # 4. 构建期望结果
    expected = []
    weak_idx = 0
    for entry in vault_entries:
        cid = entry["credential_id"]
        pwd = entry["password"]
        length = len(pwd)
        if length < 10:
            classification = "weak"
            new_pwd = strong_passwords[weak_idx] if weak_idx < len(strong_passwords) else None
            weak_idx += 1
        else:
            classification = "strong"
            new_pwd = None
        expected.append({
            "credential_id": cid,
            "old_strength": length,
            "new_password": new_pwd,
            "classification": classification
        })

    # 5. 逐项检查产物与期望 (60分)
    # 先构建映射便于查找
    report_map = {item.get("credential_id"): item for item in report}
    score_per_cred = 60 // len(vault_entries)  # 每个凭证基础分，余数加到最后
    remainder = 60 % len(vault_entries)
    for i, exp in enumerate(expected):
        cid = exp["credential_id"]
        this_max = score_per_cred + (1 if i < remainder else 0)
        if cid not in report_map:
            total_score += add_item(f"凭证 {cid} 在产物中存在", 0, this_max, False, "缺失")
            continue
        rep = report_map[cid]
        # 检查三个关键字段
        field_ok = True
        reasons = []
        if rep.get("old_strength") != exp["old_strength"]:
            field_ok = False
            reasons.append(f"old_strength应为{exp['old_strength']}，实际{rep.get('old_strength')}")
        if rep.get("classification") != exp["classification"]:
            field_ok = False
            reasons.append(f"classification应为{exp['classification']}，实际{rep.get('classification')}")
        if rep.get("new_password") != exp["new_password"]:
            field_ok = False
            reasons.append(f"new_password应为{exp['new_password']}，实际{rep.get('new_password')}")
        if field_ok:
            total_score += add_item(f"凭证 {cid} 字段正确", this_max, this_max, True)
        else:
            total_score += add_item(f"凭证 {cid} 字段正确", 0, this_max, False, "; ".join(reasons))

    # 6. 检查没有多余凭证 (5分)
    extra_cids = set(report_map.keys()) - set(e["credential_id"] for e in expected)
    if extra_cids:
        total_score += add_item("无多余凭证", 0, 5, False, f"发现多余凭证ID: {extra_cids}")
    else:
        total_score += add_item("无多余凭证", 5, 5, True)

    # 7. 检查字段类型 (5分) —— old_strength是整数，new_password是字符串或null
    type_ok = True
    for item in report:
        if not isinstance(item.get("old_strength"), int):
            type_ok = False
        if not (item.get("new_password") is None or isinstance(item.get("new_password"), str)):
            type_ok = False
        if item.get("classification") not in ("weak", "strong"):
            type_ok = False
    if type_ok:
        total_score += add_item("字段类型正确", 5, 5, True)
    else:
        total_score += add_item("字段类型正确", 0, 5, False, "存在类型错误")

    # 总分上限100
    final_score = min(total_score, 100)
    _write_score(final_score, details)

def _write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
