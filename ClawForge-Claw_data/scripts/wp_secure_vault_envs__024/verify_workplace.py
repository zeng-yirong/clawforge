import sys
import os
import json
import csv
import re
from pathlib import Path

def load_expected_rules(workspace):
    """从 vault_schema.json 加载分类规则"""
    schema_path = Path(workspace) / "data" / "vault_schema.json"
    if not schema_path.exists():
        return None
    with open(schema_path) as f:
        schema = json.load(f)
    # 构建 category_name -> category_id 映射
    category_map = {}
    for cat in schema["credential_categories"]:
        category_map[cat["name"]] = cat["category_id"]
    return category_map

def check_password_strength(password):
    """
    定义强度规则：
    强：长度 >= 12 并且至少包含 3 类字符（大写、小写、数字、特殊字符）
    弱：否则
    """
    if len(password) < 12:
        return "弱"
    categories = 0
    if re.search(r'[A-Z]', password): categories += 1
    if re.search(r'[a-z]', password): categories += 1
    if re.search(r'[0-9]', password): categories += 1
    if re.search(r'[^A-Za-z0-9]', password): categories += 1
    return "强" if categories >= 3 else "弱"

def load_original_csv(workspace):
    """读取原始 CSV，按最后出现去重（由时间戳决定）"""
    csv_path = Path(workspace) / "credentials.csv"
    if not csv_path.exists():
        return None
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    # 按 name 分组，保留时间戳最大的那个（字符串比较即可，因为格式固定 YYYY-MM-DD HH:MM:SS）
    seen = {}
    for row in rows:
        name = row["name"]
        ts = row["timestamp"]
        if name not in seen or ts > seen[name]["timestamp"]:
            seen[name] = row
    return list(seen.values())

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace)
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录结构 (10分)
    score = 0
    max_score = 10
    reason = ""
    if (workspace / "ops").is_dir():
        score += 5
        reason += "ops目录存在; "
    else:
        reason += "ops目录缺失; "
    if (workspace / "ops" / "vault_audit.json").is_file():
        score += 5
        reason += "vault_audit.json存在; "
    else:
        reason += "vault_audit.json缺失; "
    details.append({
        "item": "目录与文件结构",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reason.strip()
    })
    total_score += score

    # 2. JSON 合法性 (10分)
    score = 0
    max_score = 10
    reason = ""
    audit_path = workspace / "ops" / "vault_audit.json"
    if audit_path.exists():
        try:
            with open(audit_path) as f:
                audit_data = json.load(f)
            if isinstance(audit_data, list):
                score += 5
                reason += "根节点是数组; "
            else:
                reason += "根节点不是数组; "
        except (json.JSONDecodeError, ValueError):
            reason += "JSON解析失败; "
            audit_data = None
    else:
        reason += "文件不存在; "
        audit_data = None
    details.append({
        "item": "JSON格式与结构",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reason.strip()
    })
    total_score += score

    if audit_data is None:
        # 后续无法检查，直接输出
        output = {"total_score": total_score, "details": details}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        return

    # 3. 字段检查 (10分)
    score = 0
    max_score = 10
    reason = ""
    required_fields = {"id": str, "name": str, "category": str, "strength": str, "action": str}
    # id 可能不存在，但为了区分，我们要求每条记录至少包含name, category, strength, action
    # id可以是字符串，如果缺失则用name作为id？但要求明确，我们要求必须包含上述字段
    # 简化：检查每一条是否有name, category, strength, action
    all_ok = True
    for item in audit_data:
        for field in ["name", "category", "strength", "action"]:
            if field not in item or not isinstance(item[field], str):
                all_ok = False
                break
        if not all_ok:
            break
    if all_ok:
        score = max_score
        reason = "每条记录包含name, category, strength, action字段"
    else:
        reason = "存在记录缺少必要字段"
    details.append({
        "item": "字段完备性",
        "score": score,
        "max_score": max_score,
        "passed": score == max_score,
        "reason": reason
    })
    total_score += score

    # 4. 去重后凭证数量正确性 (20分)
    score = 0
    max_score = 20
    reason = ""
    expected_records = load_original_csv(workspace)
    if expected_records is None:
        reason = "原始credentials.csv不存在"
        details.append({"item": "去重数量", "score": 0, "max_score": max_score, "passed": False, "reason": reason})
        total_score += 0
        # 后续无法比较
        # 跳过后续计算
    else:
        expected_names = sorted([r["name"] for r in expected_records])
        got_names = sorted([item.get("name", "") for item in audit_data])
        if expected_names == got_names:
            score = max_score
            reason = f"去重后凭证数量 {len(expected_names)}，名称匹配"
        else:
            reason = f"名称不匹配：期望 {expected_names}，实际 {got_names}"
        details.append({
            "item": "去重凭证数量与名称",
            "score": score,
            "max_score": max_score,
            "passed": score == max_score,
            "reason": reason
        })
        total_score += score

        # 5. 分类正确性 (20分)
        score = 0
        max_score = 20
        reason = ""
        category_map = load_expected_rules(workspace)
        if category_map is None:
            reason = "vault_schema.json缺失"
            details.append({"item": "分类正确性", "score": 0, "max_score": max_score, "passed": False, "reason": reason})
            total_score += 0
        else:
            # 构建期望分类：原始CSV中category字段若为空，应填入"未分类"；否则应与category_map中name对应
            expected_cats = {}
            for rec in expected_records:
                name = rec["name"]
                raw_cat = rec["category"].strip()
                if raw_cat == "":
                    expected_cats[name] = "未分类"
                else:
                    # 检查是否是有效分类名称
                    if raw_cat in category_map:
                        # 使用分类名称作为最终分类（或者用id？prompt未明确，但审计文件里直接用名称即可）
                        expected_cats[name] = raw_cat
                    else:
                        expected_cats[name] = "未分类"  # 未知分类也归为未分类
            # 比较审计结果
            all_cat_ok = True
            for item in audit_data:
                name = item.get("name", "")
                actual_cat = item.get("category", "")
                expected_cat = expected_cats.get(name, "未分类")
                if actual_cat != expected_cat:
                    all_cat_ok = False
                    reason += f"凭证 {name} 分类期望 '{expected_cat}', 实际 '{actual_cat}'; "
            if all_cat_ok:
                score = max_score
                reason = "所有凭证分类正确"
            else:
                score = min(score, 5)  # 部分错误扣分
            details.append({
                "item": "分类正确性",
                "score": score,
                "max_score": max_score,
                "passed": score == max_score,
                "reason": reason
            })
            total_score += score

        # 6. 密码强度计算正确性 (30分)
        score = 0
        max_score = 30
        reason = ""
        all_strength_ok = True
        for item in audit_data:
            name = item.get("name", "")
            actual_strength = item.get("strength", "")
            # 从原始CSV中找到该凭证最后出现的密码
            original_password = None
            for rec in expected_records:
                if rec["name"] == name:
                    original_password = rec["password"]
                    break
            if original_password is None:
                all_strength_ok = False
                reason += f"凭证 {name} 无原始数据; "
                continue
            expected_strength = check_password_strength(original_password)
            if actual_strength != expected_strength:
                all_strength_ok = False
                reason += f"凭证 {name} 密码强度期望 '{expected_strength}', 实际 '{actual_strength}'; "
        if all_strength_ok:
            score = max_score
            reason = "所有密码强度判定正确"
        else:
            score = max(0, 30 - 10 * reason.count(";"))
        details.append({
            "item": "密码强度计算",
            "score": score,
            "max_score": max_score,
            "passed": score == max_score,
            "reason": reason
        })
        total_score += score

    # 汇总
    total_score = min(total_score, max_total)
    output = {
        "total_score": total_score,
        "details": details
    }
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
