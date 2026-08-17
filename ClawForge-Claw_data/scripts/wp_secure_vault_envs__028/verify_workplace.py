import sys
import os
import csv
import json
import re

def load_expected_weak(workspace: str) -> list:
    """
    从 vault_export.csv 中筛选不符合密码策略的凭据。
    策略：密码长度 >= 12 且包含大写、小写、数字、特殊字符（至少一个 !@#$%^&*）
    返回按 id 排序的 [{"id": ..., "name": ...}] 列表
    """
    csv_path = os.path.join(workspace, "vault_export.csv")
    if not os.path.isfile(csv_path):
        return None, "vault_export.csv not found"

    special = set("!@#$%^&*")
    result = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pwd = row.get("password", "")
            if len(pwd) < 12:
                result.append({"id": row["id"], "name": row["name"]})
                continue
            # 检查包含大写、小写、数字、特殊字符
            has_upper = bool(re.search(r'[A-Z]', pwd))
            has_lower = bool(re.search(r'[a-z]', pwd))
            has_digit = bool(re.search(r'\d', pwd))
            has_special = bool(set(pwd) & special)
            if not (has_upper and has_lower and has_digit and has_special):
                result.append({"id": row["id"], "name": row["name"]})
    # 按 id 排序
    result.sort(key=lambda x: x["id"])
    return result, None

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. ops 目录是否存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        total_score += 5
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ missing"})

    # 2. ops/weak_credentials.json 文件是否存在 (10分)
    json_path = os.path.join(workspace, "ops", "weak_credentials.json")
    if os.path.isfile(json_path):
        details.append({"item": "weak_credentials.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "weak_credentials.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # 后续检查无法进行，直接返回
        return {"total_score": total_score, "details": details}

    # 3. JSON 合法性 (10分)
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({"item": "JSON 格式合法且为数组", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON array"})
            total_score += 10
        else:
            details.append({"item": "JSON 格式合法且为数组", "score": 0, "max_score": 10, "passed": False, "reason": "not a list"})
            return {"total_score": total_score, "details": details}
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {str(e)}"})
        return {"total_score": total_score, "details": details}

    # 4. 验证数据内容是否与预期一致 (75分)
    expected, err = load_expected_weak(workspace)
    if err:
        details.append({"item": "从 vault_export.csv 读取预期数据", "score": 0, "max_score": 75, "passed": False, "reason": err})
        return {"total_score": total_score, "details": details}

    # 对 data 也按 id 排序
    data_sorted = sorted(data, key=lambda x: x.get("id", ""))
    # 比较长度
    if len(data_sorted) != len(expected):
        details.append({"item": "弱凭据列表长度匹配", "score": 0, "max_score": 75, "passed": False, "reason": f"长度不匹配: 得到 {len(data_sorted)}, 期望 {len(expected)}"})
        return {"total_score": total_score, "details": details}

    # 逐个比较
    all_match = True
    for i, (a, e) in enumerate(zip(data_sorted, expected)):
        if a.get("id") != e["id"] or a.get("name") != e["name"]:
            all_match = False
            details.append({"item": "弱凭据列表内容正确", "score": 0, "max_score": 75, "passed": False, "reason": f"第 {i} 条不匹配: 得到 {a}, 期望 {e}"})
            break
    if all_match:
        details.append({"item": "弱凭据列表内容正确", "score": 75, "max_score": 75, "passed": True, "reason": "完全匹配"})
        total_score += 75

    return {"total_score": total_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
