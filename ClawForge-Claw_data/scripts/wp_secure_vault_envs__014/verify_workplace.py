import sys
import json
import os
from pathlib import Path

def load_all_credentials(workspace):
    """Load all credential entries from all JSON files under shared_vault/"""
    shared_vault = Path(workspace) / "shared_vault"
    if not shared_vault.exists():
        return []
    entries = []
    for json_file in shared_vault.rglob("*.json"):
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                entries.extend(data)
        except (json.JSONDecodeError, IOError):
            continue
    return entries

def compute_expected(entries):
    """Filter active bank accounts and deduplicate by latest last_updated."""
    bank_active = [e for e in entries if e.get("category") == "bank" and e.get("is_active") is True]
    dedup = {}
    for e in bank_active:
        eid = e.get("id")
        if not eid:
            continue
        if eid not in dedup or e["last_updated"] > dedup[eid]["last_updated"]:
            dedup[eid] = e
    return list(dedup.values())

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 security/ 目录是否存在 (10分)
    security_dir = Path(workspace) / "security"
    if security_dir.is_dir():
        details.append({"item": "security/ 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
        total_score += 10
    else:
        details.append({"item": "security/ 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录未找到"})

    # 2. 检查输出文件是否存在 (10分)
    output_file = security_dir / "cleaned_bank_credentials.json"
    if output_file.is_file():
        details.append({"item": "输出文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
        total_score += 10
    else:
        details.append({"item": "输出文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未找到"})
        # 后续检查无法进行，直接返回
        score = {"total_score": total_score, "details": details}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(score, f, indent=2)
        return

    # 3. 解析输出文件，检查 JSON 合法性 (10分)
    try:
        with open(output_file, "r") as f:
            output_data = json.load(f)
        details.append({"item": "输出文件 JSON 合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except (json.JSONDecodeError, IOError) as e:
        details.append({"item": "输出文件 JSON 合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        score = {"total_score": total_score, "details": details}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(score, f, indent=2)
        return

    if not isinstance(output_data, list):
        details.append({"item": "输出数据格式", "score": 0, "max_score": 10, "passed": False, "reason": "输出不是列表"})
        score = {"total_score": total_score, "details": details}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(score, f, indent=2)
        return

    # 4. 计算预期结果
    all_entries = load_all_credentials(workspace)
    expected = compute_expected(all_entries)
    expected_ids = {e["id"] for e in expected}
    output_ids = {e.get("id") for e in output_data}

    # 5. 检查长度匹配 (15分)
    if len(output_data) == len(expected):
        details.append({"item": "输出条目数量正确", "score": 15, "max_score": 15, "passed": True, "reason": f"数量 {len(output_data)} 等于预期 {len(expected)}"})
        total_score += 15
    else:
        details.append({"item": "输出条目数量正确", "score": 0, "max_score": 15, "passed": False, "reason": f"数量 {len(output_data)}，预期 {len(expected)}"})

    # 6. 检查字段完整性 (10分) - 每个条目必须包含 id, username, password, category, is_active, last_updated
    required_fields = {"id", "username", "password", "category", "is_active", "last_updated"}
    field_ok = True
    for idx, item in enumerate(output_data):
        if not required_fields.issubset(item.keys()):
            field_ok = False
            break
    if field_ok:
        details.append({"item": "每条记录包含必需字段", "score": 10, "max_score": 10, "passed": True, "reason": "所有字段完整"})
        total_score += 10
    else:
        details.append({"item": "每条记录包含必需字段", "score": 0, "max_score": 10, "passed": False, "reason": "部分记录缺少必需字段"})

    # 7. 检查 id 集合一致性 (20分)
    if output_ids == expected_ids:
        details.append({"item": "输出 id 集合与预期一致", "score": 20, "max_score": 20, "passed": True, "reason": f"包含 id: {sorted(output_ids)}"})
        total_score += 20
    else:
        missing = expected_ids - output_ids
        extra = output_ids - expected_ids
        details.append({"item": "输出 id 集合与预期一致", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少 {missing}，多余 {extra}"})

    # 8. 检查每个 id 对应的字段值与预期最新版本一致 (20分)
    # 按 id 构造预期映射
    expected_map = {e["id"]: e for e in expected}
    value_ok = True
    for item in output_data:
        eid = item.get("id")
        if eid not in expected_map:
            value_ok = False
            break
        exp = expected_map[eid]
        for field in required_fields:
            if item.get(field) != exp.get(field):
                value_ok = False
                break
        if not value_ok:
            break
    if value_ok:
        details.append({"item": "每条记录字段值与预期最新版本一致", "score": 20, "max_score": 20, "passed": True, "reason": "所有字段匹配"})
        total_score += 20
    else:
        details.append({"item": "每条记录字段值与预期最新版本一致", "score": 0, "max_score": 20, "passed": False, "reason": "存在字段值不匹配"})

    # 9. 检查无多余字段 (5分)
    allowed_fields = required_fields | {"last_updated"}  # 已经包含
    extra_field_ok = True
    for item in output_data:
        if set(item.keys()) != required_fields:
            extra_field_ok = False
            break
    if extra_field_ok:
        details.append({"item": "无多余字段", "score": 5, "max_score": 5, "passed": True, "reason": "字段完全符合要求"})
        total_score += 5
    else:
        details.append({"item": "无多余字段", "score": 0, "max_score": 5, "passed": False, "reason": "存在额外字段"})

    # 输出最终评分
    score = {"total_score": total_score, "details": details}
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(score, f, indent=2)

if __name__ == "__main__":
    main()
