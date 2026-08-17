import sys
import json
import os
from pathlib import Path

def check_password(password: str, policy: dict) -> bool:
    """根据密码策略检查密码是否满足要求。"""
    if len(password) < policy.get("min_length", 0):
        return False
    if policy.get("require_uppercase", False) and not any(c.isupper() for c in password):
        return False
    if policy.get("require_lowercase", False) and not any(c.islower() for c in password):
        return False
    if policy.get("require_digit", False) and not any(c.isdigit() for c in password):
        return False
    if policy.get("require_special", False):
        special_chars = set("!@#$%^&*()_+-=[]{}|;':\",./<>?`~")
        if not any(c in special_chars for c in password):
            return False
    return True

def compute_expected(creds_path: str, schema_path: str) -> list:
    with open(schema_path) as f:
        schema = json.load(f)
    categories = {cat["category_id"]: cat for cat in schema["categories"]}
    valid_ids = set(categories.keys())

    with open(creds_path) as f:
        creds = json.load(f)

    expected = []
    for cred in creds:
        cid = cred["id"]
        original_cat = cred.get("category", "")
        # 如果原分类不在有效列表中，归为uncategorized
        final_cat = original_cat if original_cat in valid_ids else "uncategorized"
        policy = categories[final_cat]["password_policy"]
        compliant = check_password(cred["password"], policy)
        expected.append({
            "id": cid,
            "category_id": final_cat,
            "strength_compliant": compliant
        })
    # 按 id 排序以方便比较
    expected.sort(key=lambda x: x["id"])
    return expected

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    details = []
    total_score = 0

    # 1. 检查 ops 目录存在 (10分)
    ops_dir = ws / "ops"
    if ops_dir.exists() and ops_dir.is_dir():
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录已创建"})
        total_score += 10
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录不存在或不是目录"})

    # 2. 检查 classified_credentials.json 文件存在 (10分)
    result_file = ops_dir / "classified_credentials.json"
    if result_file.exists() and result_file.is_file():
        details.append({"item": "classified_credentials.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "classified_credentials.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未找到"})
        # 如果文件不存在，后面无法评分，直接输出结果
        score_record = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score_record, f, indent=2)
        return

    # 3. JSON 格式合法 (10分)
    try:
        with open(result_file) as f:
            agent_result = json.load(f)
        if not isinstance(agent_result, list):
            raise ValueError("结果必须是JSON数组")
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功且为列表"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        score_record = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score_record, f, indent=2)
        return

    # 4. 字段完整性 (每个条目必须有 id, category_id, strength_compliant) (10分)
    field_ok = True
    missing_info = []
    for i, entry in enumerate(agent_result):
        if not isinstance(entry, dict):
            field_ok = False
            missing_info.append(f"索引{i}不是字典")
            continue
        for field in ["id", "category_id", "strength_compliant"]:
            if field not in entry:
                field_ok = False
                missing_info.append(f"条目 {entry.get('id', '?')} 缺少字段 '{field}'")
    if field_ok:
        details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有条目包含必需字段"})
        total_score += 10
    else:
        details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(missing_info)})

    # 5. 分类正确性 (共30分，每个凭证6分)
    try:
        expected = compute_expected(
            str(ws / "data/credentials.json"),
            str(ws / "data/vault_schema.json")
        )
    except Exception as e:
        details.append({"item": "分类正确性", "score": 0, "max_score": 30, "passed": False, "reason": f"计算预期结果时出错: {str(e)}"})
        expected = None

    if expected is not None:
        # 将agent结果按id排序
        agent_sorted = sorted(agent_result, key=lambda x: x.get("id", ""))
        cat_score = 0
        for i, exp in enumerate(expected):
            if i >= len(agent_sorted):
                break
            agent_cat = agent_sorted[i].get("category_id", "")
            if agent_cat == exp["category_id"]:
                cat_score += 6
            else:
                cat_score += 0
        cat_passed = cat_score == 30
        details.append({
            "item": "分类正确性",
            "score": cat_score,
            "max_score": 30,
            "passed": cat_passed,
            "reason": f"正确分类 {cat_score//6} 个，共5个"
        })
        total_score += cat_score

    # 6. 强度合规正确性 (共30分，每个凭证6分)
    if expected is not None:
        strength_score = 0
        for i, exp in enumerate(expected):
            if i >= len(agent_sorted):
                break
            agent_compliant = agent_sorted[i].get("strength_compliant", None)
            if isinstance(agent_compliant, bool) and agent_compliant == exp["strength_compliant"]:
                strength_score += 6
        strength_passed = strength_score == 30
        details.append({
            "item": "强度合规正确性",
            "score": strength_score,
            "max_score": 30,
            "passed": strength_passed,
            "reason": f"正确标记 {strength_score//6} 个，共5个"
        })
        total_score += strength_score

    # 最终总分
    final_score = min(total_score, 100)  # 确保不超过100
    score_record = {"total_score": final_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(score_record, f, indent=2)

if __name__ == "__main__":
    verify()
