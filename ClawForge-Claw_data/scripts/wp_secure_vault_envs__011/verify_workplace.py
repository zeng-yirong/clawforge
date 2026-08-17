import json
import csv
import os
import sys
import re
from datetime import datetime, timedelta

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 辅助函数
    def check(condition, item_name, score, max_score, reason):
        nonlocal total_score
        score_details.append({
            "item": item_name,
            "score": score if condition else 0,
            "max_score": max_score,
            "passed": condition,
            "reason": reason if not condition else "OK"
        })
        if condition:
            total_score += score

    # 1. 检查必要目录结构 (10分)
    vault_exists = os.path.isdir(os.path.join(workspace, "vault"))
    policy_exists = os.path.isfile(os.path.join(workspace, "policy.json"))
    rules_exists = os.path.isfile(os.path.join(workspace, "category_rules.json"))
    dir_ok = vault_exists and policy_exists and rules_exists
    check(dir_ok, "必要目录与策略文件存在", 10, 10,
          "缺少 vault/ policy.json 或 category_rules.json")

    if not dir_ok:
        # 无法继续
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 加载策略和规则
    policy = load_json(os.path.join(workspace, "policy.json"))
    rules = load_json(os.path.join(workspace, "category_rules.json"))

    # 2. 检查输出文件存在 (10分)
    clean_path = os.path.join(workspace, "cleaned_vault.json")
    autofill_path = os.path.join(workspace, "autofill_rules.json")
    clean_exists = os.path.isfile(clean_path)
    autofill_exists = os.path.isfile(autofill_path)
    check(clean_exists, "cleaned_vault.json 存在", 5, 5, "文件未找到")
    check(autofill_exists, "autofill_rules.json 存在", 5, 5, "文件未找到")

    if not clean_exists or not autofill_exists:
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. 验证 JSON 格式合法 (10分)
    try:
        cleaned = load_json(clean_path)
        check(True, "cleaned_vault.json 格式合法", 5, 5, "")
    except Exception as e:
        check(False, "cleaned_vault.json 格式合法", 5, 5, f"解析失败: {e}")
        cleaned = []
    try:
        autofill = load_json(autofill_path)
        check(True, "autofill_rules.json 格式合法", 5, 5, "")
    except Exception as e:
        check(False, "autofill_rules.json 格式合法", 5, 5, f"解析失败: {e}")
        autofill = []

    if not isinstance(cleaned, list):
        check(False, "cleaned_vault.json 是列表", 2, 2, "不是列表")
    else:
        check(True, "cleaned_vault.json 是列表", 2, 2, "")

    if not isinstance(autofill, list):
        check(False, "autofill_rules.json 是列表", 2, 2, "不是列表")
    else:
        check(True, "autofill_rules.json 是列表", 2, 2, "")

    # 4. 去重验证 (20分)
    # 预期唯一数据（按 domain+username 去重保留最新）
    ref_date = datetime.strptime(policy["reference_date"], "%Y-%m-%d")
    expire_limit = ref_date - timedelta(days=policy["expire_threshold_days"])
    # 从 builder 的原始数据构建预期
    # 我们只读取原始文件，但这里直接硬编码 expected 会更精确
    # 从 builder 逻辑出发：
    raw_files = ["vault/credentials_main.csv", "vault/legacy_export.csv"]
    all_raw = []
    for fname in raw_files:
        fpath = os.path.join(workspace, fname)
        if os.path.isfile(fpath):
            with open(fpath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('domain') and row.get('username') and row.get('password') and row.get('created'):
                        all_raw.append(row)
    # 按照 builder 实际写入的内容，手工构造预期
    # 出于安全，我们直接根据 builder 中的列表计算
    # 有效凭证
    valid = [
        ("internal.corp.com", "alice", "Alice@2024!", "2025-05-01"),
        ("shop.example.com", "bob", "Bob#12345", "2025-04-15"),
        ("social.example.com", "charlie", "Charlie!2025", "2025-05-20"),
        ("bank.example.com", "dave", "Dave@Secure1", "2025-05-10"),
        ("market.example.com", "eve", "Eve!StrongPwd", "2025-03-01"),
    ]
    weak = [
        ("weakshop.example.com", "hank", "short", "2025-04-01"),
        ("weakbank.example.com", "iris", "alllowercase", "2025-04-10"),
        ("weakcorp.example.com", "jack", "NODIGIT!", "2025-05-01"),
    ]
    dup = [
        ("internal.corp.com", "alice", "OldPass1!", "2024-12-01"),
        ("shop.example.com", "bob", "BobWeak1", "2024-11-15"),
        ("bank.example.com", "dave", "DaveOld!", "2024-10-20"),
    ]
    expired = [
        ("oldbank.example.com", "frank", "Frank2022!", "2024-06-01"),
        ("chatsocial.example.com", "grace", "Grace!Old", "2024-05-15"),
    ]
    # 合并并去重 (保留每个 domain+username 的最新 created)
    all_entries = {}
    for domain, uname, pwd, created in valid + weak + dup + expired:
        key = (domain, uname)
        if key not in all_entries or created > all_entries[key][2]:
            all_entries[key] = (domain, uname, pwd, created)
    # 过滤过期
    expected_entries = []
    for key, (domain, uname, pwd, created) in all_entries.items():
        created_dt = datetime.strptime(created, "%Y-%m-%d")
        if created_dt >= expire_limit:
            expected_entries.append((domain, uname, pwd, created))
    # 对弱密码替换
    default_pwd = policy["default_password"]
    # 定义密码强度规则
    def is_strong(pwd):
        if len(pwd) < policy["password_min_length"]:
            return False
        if policy["require_uppercase"] and not re.search(r'[A-Z]', pwd):
            return False
        if policy["require_lowercase"] and not re.search(r'[a-z]', pwd):
            return False
        if policy["require_digit"] and not re.search(r'\d', pwd):
            return False
        if policy["require_special"] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            return False
        return True
    expected_cleaned = []
    for domain, uname, pwd, created in expected_entries:
        if not is_strong(pwd):
            pwd = default_pwd
        # 分类
        category = "other"
        for cat, rule in rules.items():
            for dom in rule["domains"]:
                if dom in domain:
                    category = cat
                    break
            if category != "other":
                break
        expected_cleaned.append({
            "domain": domain,
            "username": uname,
            "password": pwd,
            "created": created,
            "category": category
        })
    # 排序以便比较
    expected_cleaned.sort(key=lambda x: (x["domain"], x["username"]))
    # 实际
    actual_cleaned = sorted(cleaned, key=lambda x: (x.get("domain",""), x.get("username","")))
    # 检查数量
    if len(actual_cleaned) == len(expected_cleaned):
        check(True, "清洗后记录数量正确", 5, 5, f"预期 {len(expected_cleaned)}, 实际 {len(actual_cleaned)}")
    else:
        check(False, "清洗后记录数量正确", 5, 5, f"预期 {len(expected_cleaned)}, 实际 {len(actual_cleaned)}")
    # 检查每条记录字段
    correct_fields = True
    if len(actual_cleaned) == len(expected_cleaned):
        for i, (exp, act) in enumerate(zip(expected_cleaned, actual_cleaned)):
            if (exp["domain"] != act.get("domain") or
                exp["username"] != act.get("username") or
                exp["password"] != act.get("password") or
                exp["category"] != act.get("category")):
                correct_fields = False
                break
    else:
        correct_fields = False
    check(correct_fields, "清洗后记录字段完全正确 (去重、过期、密码替换、分类)", 15, 15,
          "字段不匹配" if not correct_fields else "")

    # 5. 自动填充规则验证 (10分)
    # 预期规则：每个类别一条规则，包含某些字段映射
    expected_categories = set(entry["category"] for entry in expected_cleaned)
    expected_autofill = []
    for cat in sorted(expected_categories):
        expected_autofill.append({
            "category": cat,
            "fields": {
                "username": "username",
                "password": "password"
            }
        })
    # 实际
    actual_autofill = sorted(autofill, key=lambda x: x.get("category","")) if isinstance(autofill, list) else []
    if len(actual_autofill) == len(expected_autofill):
        check(True, "自动填充规则数量正确", 3, 3, "")
    else:
        check(False, "自动填充规则数量正确", 3, 3, f"预期 {len(expected_autofill)}, 实际 {len(actual_autofill)}")
    # 检查内容
    rule_ok = True
    for exp_rule in expected_autofill:
        # 找匹配
        found = False
        for act_rule in actual_autofill:
            if act_rule.get("category") == exp_rule["category"]:
                if act_rule.get("fields") == exp_rule["fields"]:
                    found = True
                    break
        if not found:
            rule_ok = False
            break
    check(rule_ok, "自动填充规则内容正确", 7, 7, "")

    # 6. 字段完整性与额外字段检查 (扣分项)
    required_fields = ["domain", "username", "password", "created", "category"]
    extra_fields_penalty = 0
    for entry in actual_cleaned:
        if not all(f in entry for f in required_fields):
            extra_fields_penalty -= 2  # 缺字段
        # 不允许额外字段
        allowed = set(required_fields)
        if set(entry.keys()) - allowed:
            extra_fields_penalty -= 1  # 每个条目最多扣1
    # 仅记录但不超出20分上限，这里单独扣分
    if extra_fields_penalty < 0:
        total_score += extra_fields_penalty  # 直接扣总分
        score_details.append({
            "item": "字段完整性 (扣分项)",
            "score": extra_fields_penalty,
            "max_score": 0,
            "passed": extra_fields_penalty >= 0,
            "reason": f"存在缺失字段或多余字段，扣 {abs(extra_fields_penalty)} 分"
        })

    # 写入结果
    total_score = max(0, min(100, total_score))
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
