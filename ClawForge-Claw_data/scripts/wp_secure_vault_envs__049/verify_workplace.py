import json
import os
import sys
import math
import re

def score_password(password):
    """计算密码强度：长度*4 + 数字个数*5 + 大写字母个数*3，保留两位小数"""
    length = len(password)
    digits = sum(1 for c in password if c.isdigit())
    uppers = sum(1 for c in password if c.isupper())
    raw = length * 4 + digits * 5 + uppers * 3
    return round(raw, 2)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # ----- 1. 检查目录结构 (10分) -----
    score_item = {"item": "工作区文件存在性", "max_score": 10, "passed": True, "reason": ""}
    required_files = ["data/vault_schema.json", "data/credential_store.json"]
    for f in required_files:
        if not os.path.isfile(os.path.join(workspace, f)):
            score_item["passed"] = False
            score_item["reason"] += f"缺少 {f}; "
    if score_item["passed"]:
        score_item["score"] = 10
        score_item["reason"] = "所有必需文件都存在"
    else:
        score_item["score"] = 0
    total_score += score_item["score"]
    details.append(score_item)

    # ----- 2. 检查 classified_credentials.json 是否存在且合法 (10分) -----
    score_item2 = {"item": "classified_credentials.json 存在且为合法JSON", "max_score": 10, "passed": True, "reason": ""}
    cc_path = os.path.join(workspace, "classified_credentials.json")
    if not os.path.isfile(cc_path):
        score_item2["passed"] = False
        score_item2["reason"] = "文件不存在"
        score_item2["score"] = 0
        total_score += score_item2["score"]
        details.append(score_item2)
        # 后续依赖此文件，直接返回当前分数
        print(json.dumps({"total_score": total_score, "details": details}, indent=2))
        return

    try:
        cc = load_json(cc_path)
        if not isinstance(cc, list):
            raise ValueError("不是列表")
    except Exception as e:
        score_item2["passed"] = False
        score_item2["reason"] = f"JSON解析失败: {str(e)}"
        score_item2["score"] = 0
        total_score += score_item2["score"]
        details.append(score_item2)
        print(json.dumps({"total_score": total_score, "details": details}, indent=2))
        return
    score_item2["score"] = 10
    score_item2["reason"] = "文件存在且为合法JSON数组"
    total_score += score_item2["score"]
    details.append(score_item2)

    # ----- 3. 检查数量与字段完整性 (15分) -----
    score_item3 = {"item": "记录数量与字段完整性", "max_score": 15, "passed": True, "reason": ""}
    # 预期有效记录: cred_001, cred_002, cred_003, cred_005, cred_008, cred_009 (6条)
    expected_ids = {"cred_001", "cred_002", "cred_003", "cred_005", "cred_008", "cred_009"}
    actual_ids = set()
    for rec in cc:
        if not all(k in rec for k in ("id", "username", "platform", "category_id", "password", "password_strength")):
            score_item3["passed"] = False
            score_item3["reason"] = "存在缺少字段的记录"
            break
        actual_ids.add(rec["id"])
    else:
        if actual_ids == expected_ids:
            score_item3["score"] = 15
            score_item3["reason"] = f"记录了正确数量的有效凭证 ({len(expected_ids)}条)"
        else:
            score_item3["passed"] = False
            missing = expected_ids - actual_ids
            extra = actual_ids - expected_ids
            score_item3["reason"] = f"ID不匹配, 缺少{missing}, 多余{extra}"
            score_item3["score"] = 0
    total_score += score_item3["score"]
    details.append(score_item3)

    # 如果记录数量不对，后续验证可能无意义，但继续检查已有记录
    # ----- 4. 检查每条密码强度计算是否正确 (25分) -----
    score_item4 = {"item": "密码强度计算", "max_score": 25, "passed": True, "reason": ""}
    # 建立期望强度字典
    # 预计算
    passwords_map = {
        "cred_001": "Alice2024!Strong",
        "cred_002": "Bob123",
        "cred_003": "charlie!",
        "cred_005": "DaveBank!2024StrongSecure",
        "cred_008": "Grace2024!",
        "cred_009": "Alice2024!Strong"
    }
    errors = []
    for rec in cc:
        rid = rec["id"]
        if rid in passwords_map:
            expected_strength = score_password(passwords_map[rid])
            actual_strength = rec.get("password_strength")
            if actual_strength is None or not isinstance(actual_strength, (int, float)):
                errors.append(f"{rid}: strength缺失或非数值")
            elif abs(actual_strength - expected_strength) > 0.01:
                errors.append(f"{rid}: 期望{expected_strength}, 得到{actual_strength}")
    if errors:
        score_item4["passed"] = False
        score_item4["reason"] = "; ".join(errors)
        score_item4["score"] = 0
    else:
        score_item4["score"] = 25
        score_item4["reason"] = "所有记录密码强度计算正确"
    total_score += score_item4["score"]
    details.append(score_item4)

    # ----- 5. 检查分类映射是否正确 (20分) -----
    score_item5 = {"item": "分类映射", "max_score": 20, "passed": True, "reason": ""}
    # 加载 schema
    schema = load_json(os.path.join(workspace, "data/vault_schema.json"))
    cat_map = {cat["name"]: cat["category_id"] for cat in schema["credential_categories"]}
    # 期望映射 (根据原始记录中的 category_name)
    expected_cat_id = {
        "cred_001": "cat_work",
        "cred_002": "cat_ecom",
        "cred_003": "cat_social",
        "cred_005": "cat_bank",
        "cred_008": "cat_social",
        "cred_009": "cat_work"
    }
    errors2 = []
    for rec in cc:
        rid = rec["id"]
        if rid in expected_cat_id:
            if rec.get("category_id") != expected_cat_id[rid]:
                errors2.append(f"{rid}: 期望{expected_cat_id[rid]}, 得到{rec.get('category_id')}")
    if errors2:
        score_item5["passed"] = False
        score_item5["reason"] = "; ".join(errors2)
        score_item5["score"] = 0
    else:
        score_item5["score"] = 20
        score_item5["reason"] = "所有记录分类映射正确"
    total_score += score_item5["score"]
    details.append(score_item5)

    # ----- 6. 检查 autofill_rules.json (20分) -----
    score_item6 = {"item": "autofill_rules.json", "max_score": 20, "passed": True, "reason": ""}
    af_path = os.path.join(workspace, "autofill_rules.json")
    if not os.path.isfile(af_path):
        score_item6["passed"] = False
        score_item6["reason"] = "文件不存在"
        score_item6["score"] = 0
        total_score += score_item6["score"]
        details.append(score_item6)
    else:
        try:
            af = load_json(af_path)
            if not isinstance(af, dict):
                raise ValueError("不是字典")
            # 期望有4个分类的规则
            expected_categories = ["cat_work", "cat_ecom", "cat_social", "cat_bank"]
            name_en_map = {cat["category_id"]: cat["name_en"] for cat in schema["credential_categories"]}
            for cid in expected_categories:
                if cid not in af:
                    score_item6["passed"] = False
                    score_item6["reason"] = f"缺少分类 {cid}"
                    break
                rule = af[cid]
                expected_url = f"https://*.example.com/{name_en_map[cid]}"
                if rule.get("url_pattern") != expected_url:
                    score_item6["passed"] = False
                    score_item6["reason"] = f"{cid} url_pattern期望 {expected_url}, 得到 {rule.get('url_pattern')}"
                    break
                if rule.get("fields") != ["username", "password"]:
                    score_item6["passed"] = False
                    score_item6["reason"] = f"{cid} fields期望 ['username','password'], 得到 {rule.get('fields')}"
                    break
            else:
                # 允许额外分类，但只检查必要
                score_item6["score"] = 20
                score_item6["reason"] = "所有标准分类的autofill规则正确"
        except Exception as e:
            score_item6["passed"] = False
            score_item6["reason"] = f"解析或验证失败: {str(e)}"
            score_item6["score"] = 0
        total_score += score_item6["score"]
        details.append(score_item6)

    # 打包最终分数
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
