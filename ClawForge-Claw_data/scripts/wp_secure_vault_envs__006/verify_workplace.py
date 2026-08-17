import sys
import os
import json
import csv

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def add_score(item, score, max_score, passed, reason):
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return score if passed else 0

# ---------- 1. 目录结构 ----------
dirs_ok = True
if not os.path.isdir(os.path.join(workspace, "data")):
    total_score += add_score("data/ 目录存在", 0, 5, False, "缺少 data/ 目录")
    dirs_ok = False
else:
    total_score += add_score("data/ 目录存在", 5, 5, True, "存在")

if not os.path.isdir(os.path.join(workspace, "ops")):
    total_score += add_score("ops/ 目录存在", 0, 5, False, "缺少 ops/ 目录")
    dirs_ok = False
else:
    total_score += add_score("ops/ 目录存在", 5, 5, True, "存在")

# ---------- 2. 读取初始文件（用于生成预期结果） ----------
# 读取 vault schema
vault_path = os.path.join(workspace, "data/vault_schema.json")
with open(vault_path, "r", encoding="utf-8") as f:
    vault = json.load(f)

# 读取 password policy
policy_path = os.path.join(workspace, "ops/password_policy.json")
with open(policy_path, "r", encoding="utf-8") as f:
    policy = json.load(f)
suggested = policy["suggested_passwords"]

# 读取 credential dump
dump_path = os.path.join(workspace, "data/credential_dump.csv")
raw_rows = []
with open(dump_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        raw_rows.append(r)

# 预期处理逻辑
platform_category_map = {
    "example.com": "工作邮箱",
    "shop.com":    "电商平台",
    "bank.com":    "银行账户",
    "social.io":   "社交媒体",
    "store.com":   "电商平台"
}

# 过滤: 删除 retired 和缺少必要字段的
valid_rows = []
for row in raw_rows:
    if row["status"] == "retired":
        continue
    if not row["platform"] or not row["username"] or not row["password"]:
        continue
    valid_rows.append(row)

# 分类纠正 & 密码替换 (strength < 80 则换)
new_password_idx = 0
for row in valid_rows:
    platform = row["platform"]
    expected_cat = platform_category_map.get(platform)
    if expected_cat and expected_cat in vault["credential_categories"]:
        row["category"] = expected_cat
    # 密码强度
    strength = int(row["strength"])
    if strength < 80:
        # 用建议密码替换
        row["password"] = suggested[new_password_idx % len(suggested)]
        row["strength"] = "100"
        new_password_idx += 1
    else:
        # 保持原值，但强度字段仍为字符串
        pass

# 预期 cleaned_credentials.json
expected_cleaned = []
for row in valid_rows:
    expected_cleaned.append({
        "id": row["id"],
        "username": row["username"],
        "password": row["password"],
        "category": row["category"],
        "platform": row["platform"],
        "status": row["status"],
        "strength": row["strength"]
    })

# 预期 autofill_rules.json
platforms = sorted(set(r["platform"] for r in valid_rows))
expected_rules = []
for p in platforms:
    expected_rules.append({
        "platform": p,
        "fields": ["username", "password"],
        "autofill": True
    })

# ---------- 3. 检查 cleaned_credentials.json ----------
cleaned_path = os.path.join(workspace, "ops/cleaned_credentials.json")
if not os.path.exists(cleaned_path):
    total_score += add_score("ops/cleaned_credentials.json 存在", 0, 10, False, "文件不存在")
else:
    try:
        with open(cleaned_path, "r", encoding="utf-8") as f:
            actual_cleaned = json.load(f)
        format_ok = True
        # 必须是一个列表
        if not isinstance(actual_cleaned, list):
            format_ok = False
            total_score += add_score("cleaned_credentials 格式", 0, 10, False, "不是JSON数组")
        else:
            # 比较长度
            if len(actual_cleaned) != len(expected_cleaned):
                total_score += add_score("cleaned_credentials 记录数", 0, 10, False, f"期望{len(expected_cleaned)}条, 实际{len(actual_cleaned)}条")
            else:
                # 逐条比较 (按id顺序)
                actual_sorted = sorted(actual_cleaned, key=lambda x: x["id"])
                expected_sorted = sorted(expected_cleaned, key=lambda x: x["id"])
                match = True
                for idx, (exp, act) in enumerate(zip(expected_sorted, actual_sorted)):
                    for field in ["id","username","password","category","platform","status","strength"]:
                        if str(act.get(field,"")) != str(exp[field]):
                            match = False
                            break
                if match:
                    total_score += add_score("cleaned_credentials 内容正确", 20, 20, True, "全部字段匹配")
                else:
                    total_score += add_score("cleaned_credentials 内容正确", 0, 20, False, "字段值不匹配")
    except Exception as e:
        total_score += add_score("cleaned_credentials JSON解析", 0, 10, False, str(e))

# ---------- 4. 检查 autofill_rules.json ----------
rules_path = os.path.join(workspace, "ops/autofill_rules.json")
if not os.path.exists(rules_path):
    total_score += add_score("ops/autofill_rules.json 存在", 0, 10, False, "文件不存在")
else:
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            actual_rules = json.load(f)
        if not isinstance(actual_rules, list):
            total_score += add_score("autofill_rules 格式", 0, 10, False, "不是JSON数组")
        else:
            # 检查平台集合是否一致
            actual_platforms = sorted(set(r.get("platform","") for r in actual_rules))
            expected_platforms = sorted(set(r["platform"] for r in expected_rules))
            if actual_platforms == expected_platforms:
                # 检查每条规则结构
                structure_ok = True
                for rule in actual_rules:
                    if not isinstance(rule, dict):
                        structure_ok = False
                        break
                    if "fields" not in rule or "autofill" not in rule:
                        structure_ok = False
                        break
                if structure_ok:
                    total_score += add_score("autofill_rules 平台集合及结构", 15, 15, True, "平台正确，结构合规")
                else:
                    total_score += add_score("autofill_rules 结构", 0, 15, False, "规则缺少必要字段")
            else:
                total_score += add_score("autofill_rules 平台集合", 0, 15, False, f"期望平台{expected_platforms}, 实际{actual_platforms}")
    except Exception as e:
        total_score += add_score("autofill_rules JSON解析", 0, 10, False, str(e))

# ---------- 5. 额外：清理与顺序无关（已覆盖） ----------
# 写入评分结果
result = {
    "total_score": total_score,
    "details": score_details
}
result_path = os.path.join(workspace, "workplace_score.json")
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Total Score: {total_score}/100")
sys.exit(0 if total_score >= 100 else 1)
