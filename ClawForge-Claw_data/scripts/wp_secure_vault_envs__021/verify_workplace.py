import sys
import json
import os
from pathlib import Path

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace)

    details = []
    total_score = 0

    # 1. 检查目录结构（10分）
    # 期望工作区根目录存在，且包含下述文件
    required_files = [
        "vault_export.json",
        "vault_schema.json",
        "mapping.json",
        "classified_vault.json",
        "autofill_rules.json"
    ]
    req_ok = True
    for fname in required_files:
        if not (workspace / fname).exists():
            req_ok = False
            break
    if req_ok:
        details.append({"item": "目录结构与必需文件", "score": 10, "max_score": 10, "passed": True, "reason": "所有必需文件均存在"})
        total_score += 10
    else:
        missing = [f for f in required_files if not (workspace / f).exists()]
        details.append({"item": "目录结构与必需文件", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少文件: {missing}"})

    # 2. 检查 classified_vault.json 合法性（10分）
    try:
        classified = load_json(workspace / "classified_vault.json")
        if isinstance(classified, list) and len(classified) > 0:
            details.append({"item": "classified_vault.json 合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功且为列表"})
            total_score += 10
        else:
            details.append({"item": "classified_vault.json 合法", "score": 0, "max_score": 10, "passed": False, "reason": "内容不是非空列表"})
    except Exception as e:
        details.append({"item": "classified_vault.json 合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})

    # 3. 检查 autofill_rules.json 合法性（10分）
    try:
        rules = load_json(workspace / "autofill_rules.json")
        if isinstance(rules, list) and len(rules) > 0:
            details.append({"item": "autofill_rules.json 合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功且为列表"})
            total_score += 10
        else:
            details.append({"item": "autofill_rules.json 合法", "score": 0, "max_score": 10, "passed": False, "reason": "内容不是非空列表"})
    except Exception as e:
        details.append({"item": "autofill_rules.json 合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})

    # === 如果前几步已经失败，后续评分可能依赖解析后的数据，但尽量继续以给出完整反馈 ===

    # 4. 分类正确性（每条凭据1分，共8分）
    # 加载原始凭据和 mapping 以及 schema，计算预期分类
    try:
        vault_raw = load_json(workspace / "vault_export.json")
        mapping = load_json(workspace / "mapping.json")
        schema_raw = load_json(workspace / "vault_schema.json")
        category_names = {c["name"] for c in schema_raw["credential_categories"]}
    except Exception as e:
        # 如果依赖文件无法加载，跳过此项
        vault_raw = []
        mapping = {}
        category_names = set()
        print(f"Warning: cannot load reference files, skip classification check. {e}")

    # 构建预期分类映射：根据 platform 中出现的 keyword 映射到分类名
    def expected_category(platform):
        plat_lower = platform.lower()
        for kw, cat in mapping.items():
            if kw in plat_lower:
                return cat
        return None

    # 如果 classified 是列表，构建一个 id -> category 的字典
    if isinstance(classified, list):
        classified_dict = {}
        for item in classified:
            if "id" in item and "category" in item:
                classified_dict[item["id"]] = item["category"]
    else:
        classified_dict = {}

    classification_score = 0
    classification_items = []
    for cred in vault_raw:
        cid = cred["id"]
        expected = expected_category(cred["platform"])
        actual = classified_dict.get(cid)
        # 如果预期分类不在 schema 中，忽略（理论上应该都在）
        if expected not in category_names:
            continue
        if actual == expected:
            classification_score += 1
            classification_items.append({"id": cid, "passed": True})
        else:
            classification_items.append({"id": cid, "passed": False, "expected": expected, "got": actual})
    total_classification = len([c for c in vault_raw if expected_category(c["platform"]) in category_names])
    # 最多8分（凭据数）
    max_class_score = min(len(vault_raw), 8)
    details.append({"item": "分类正确性", "score": classification_score, "max_score": max_class_score, "passed": classification_score == max_class_score,
                    "reason": f"正确分类了 {classification_score}/{max_class_score} 条凭据"})
    total_score += classification_score

    # 5. 分类无多余分类（2分）
    # 检查 classified_vault 中是否出现了 schema 之外的分类名
    schema_names = {c["name"] for c in schema_raw["credential_categories"]}
    extra_categories = set()
    for item in classified:
        cat = item.get("category")
        if cat and cat not in schema_names:
            extra_categories.add(cat)
    if len(extra_categories) == 0:
        details.append({"item": "无多余分类", "score": 2, "max_score": 2, "passed": True, "reason": "所有分类均在 schema 中"})
        total_score += 2
    else:
        details.append({"item": "无多余分类", "score": 0, "max_score": 2, "passed": False, "reason": f"发现额外分类: {extra_categories}"})

    # 6. autofill_rules 完整性（10分）
    # 必须包含所有四种分类的规则
    rule_categories = {r.get("category") for r in rules}
    missing_rules = schema_names - rule_categories
    extra_rules = rule_categories - schema_names
    if len(missing_rules) == 0 and len(extra_rules) == 0:
        details.append({"item": "autofill_rules 完整性", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有分类且无多余"})
        total_score += 10
    else:
        msg = ""
        if missing_rules:
            msg += f"缺少分类: {missing_rules}; "
        if extra_rules:
            msg += f"多余分类: {extra_rules}"
        details.append({"item": "autofill_rules 完整性", "score": 0, "max_score": 10, "passed": False, "reason": msg})

    # 7. autofill_rules 每个规则的字段正确性（每个分类7分，共28分）
    # 根据 schema 中的 priority 和 requires_mfa 验证
    # 构建 schema 中 category name -> 属性
    schema_cat_map = {}
    for c in schema_raw["credential_categories"]:
        schema_cat_map[c["name"]] = {"priority": c["priority"], "requires_mfa": c["requires_mfa"]}

    rule_field_score = 0
    for rule in rules:
        cat = rule.get("category")
        if cat not in schema_cat_map:
            continue  # 已在上一步处理
        expected = schema_cat_map[cat]
        # 检查必要字段
        fields_ok = True
        if not isinstance(rule.get("fill_username"), bool) or rule["fill_username"] != True:
            fields_ok = False
        if not isinstance(rule.get("fill_password"), bool) or rule["fill_password"] != True:
            fields_ok = False
        if rule.get("requires_mfa") != expected["requires_mfa"]:
            fields_ok = False
        if rule.get("priority") != expected["priority"]:
            fields_ok = False
        # 检查没有多余字段（可选，但宽松处理）
        if fields_ok:
            rule_field_score += 7
    # 最多 4*7=28
    max_rule_field = 4 * 7
    details.append({"item": "autofill_rules 字段正确性", "score": rule_field_score, "max_score": max_rule_field, "passed": rule_field_score == max_rule_field,
                    "reason": f"规则字段正确 {rule_field_score}/{max_rule_field} 分"})
    total_score += rule_field_score

    # 8. 一致性与整体质量（10分）
    # 验证 classified_vault 中的分类集合与 autofill_rules 中的分类集合一致（都只有 schema 内的且一致）
    classified_cats = set()
    for item in classified:
        cat = item.get("category")
        if cat in schema_names:
            classified_cats.add(cat)
    rule_cats = set()
    for rule in rules:
        cat = rule.get("category")
        if cat in schema_names:
            rule_cats.add(cat)
    if classified_cats == rule_cats == schema_names:
        details.append({"item": "整体一致性", "score": 10, "max_score": 10, "passed": True, "reason": "两个输出文件的分类集合完全匹配且覆盖所有 schema 分类"})
        total_score += 10
    else:
        details.append({"item": "整体一致性", "score": 0, "max_score": 10, "passed": False, "reason": f"分类集合不一致: classified有 {classified_cats}, rules有 {rule_cats}"})

    # 总分截断到100
    total_score = min(total_score, 100)
    # 输出结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
