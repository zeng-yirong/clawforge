import sys
import json
import os
import csv
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total = 0
    max_total = 0

    def check(condition, item_name, score, max_score, reason_true="", reason_false=""):
        nonlocal total, max_total
        max_total += max_score
        passed = bool(condition)
        if passed:
            total += score
            detail = {
                "item": item_name,
                "score": score,
                "max_score": max_score,
                "passed": True,
                "reason": reason_true or "OK"
            }
        else:
            detail = {
                "item": item_name,
                "score": 0,
                "max_score": max_score,
                "passed": False,
                "reason": reason_false or "FAIL"
            }
        score_details.append(detail)
        return passed

    # 1. 检查产物文件是否存在
    creds_path = os.path.join(workspace, "vault", "credentials.json")
    file_exists = os.path.isfile(creds_path)
    check(file_exists, "目标文件 vault/credentials.json 存在", 10, 10,
          "文件存在", "文件不存在")

    if not file_exists:
        # 无法继续，直接输出分数
        output_score(total, score_details)
        return

    try:
        with open(creds_path, "r") as f:
            creds = json.load(f)
        json_valid = isinstance(creds, list)
    except Exception:
        json_valid = False
    check(json_valid, "文件为合法JSON数组", 10, 10,
          "合法JSON数组", "JSON格式错误或不是数组")

    if not json_valid:
        output_score(total, score_details)
        return

    # 2. 读取规则文件和onboard.csv计算预期密码
    rules_path = os.path.join(workspace, "ops", "password_rules.json")
    onboard_path = os.path.join(workspace, "ops", "onboard.csv")
    expected_new = {}
    if os.path.isfile(rules_path) and os.path.isfile(onboard_path):
        with open(rules_path) as f:
            rules = json.load(f)
        with open(onboard_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                platform = row["platform"].strip()
                username = row["username"].strip()
                category = row["category_id"].strip()
                # 根据规则生成密码
                # parts: ["platform[:4]", "username[-4:]", "@2025"]
                platform_part = platform[:4]
                username_part = username[-4:] if len(username) >= 4 else username
                password = platform_part + username_part + "@2025"
                expected_new[(platform, username)] = {
                    "password": password,
                    "category_id": category
                }

    # 3. 检查记录数量（原始2条 + 新2条 = 4条）
    expected_count = 4  # 2 original + 2 new
    actual_count = len(creds)
    count_ok = (actual_count == expected_count)
    check(count_ok, f"记录总数为 {expected_count}", 15, 15,
          f"实际 {actual_count}，正确",
          f"实际 {actual_count}，期望 {expected_count}")

    # 4. 检查所有记录的必要字段
    fields_ok = True
    missing_fields = []
    for i, rec in enumerate(creds):
        for field in ["platform", "username", "password", "category_id", "autofill"]:
            if field not in rec:
                fields_ok = False
                missing_fields.append(f"记录 {i} 缺少字段 {field}")
    check(fields_ok, "所有记录包含必要字段 (platform, username, password, category_id, autofill)", 10, 10,
          "字段齐全", "缺少字段: " + "; ".join(missing_fields) if missing_fields else "")

    # 5. 检查新记录的autofill是否为true
    autofill_ok = True
    bad_autofill = []
    for rec in creds:
        key = (rec.get("platform",""), rec.get("username",""))
        if key in expected_new:
            if rec.get("autofill") is not True:
                autofill_ok = False
                bad_autofill.append(f"{key[0]}/{key[1]}")
    check(autofill_ok, "新记录 autofill = true", 15, 15,
          "所有新记录autofill为true",
          f"以下新记录autofill不是true: {bad_autofill}" if bad_autofill else "")

    # 6. 检查新记录密码是否符合规则
    password_ok = True
    bad_password = []
    for rec in creds:
        key = (rec.get("platform",""), rec.get("username",""))
        if key in expected_new:
            expected_pwd = expected_new[key]["password"]
            actual_pwd = rec.get("password","")
            if actual_pwd != expected_pwd:
                password_ok = False
                bad_password.append(f"{key[0]}/{key[1]}: 期望 {expected_pwd}, 实际 {actual_pwd}")
    check(password_ok, "新记录密码符合 password_rules.json", 30, 30,
          "所有新记录密码正确",
          f"密码不匹配: {bad_password}" if bad_password else "")

    # 7. 检查原有记录未被修改（即原始两条记录应该保持不变）
    original_expected = [
        {"platform": "internal_tools", "username": "admin", "password": "OldPass123!", "category_id": "work_email", "autofill": False},
        {"platform": "shopify", "username": "store_manager", "password": "Shopify123", "category_id": "ecommerce", "autofill": True}
    ]
    original_preserved = True
    for orig in original_expected:
        found = False
        for rec in creds:
            if rec.get("platform") == orig["platform"] and rec.get("username") == orig["username"]:
                if (rec.get("password") == orig["password"] and
                    rec.get("category_id") == orig["category_id"] and
                    rec.get("autofill") == orig["autofill"]):
                    found = True
                break
        if not found:
            original_preserved = False
            break
    check(original_preserved, "原有记录未被修改或删除", 10, 10,
          "所有原始记录保持不变",
          "原始记录被修改或删除")

    # 输出分数
    output_score(total, score_details)

def output_score(total, details):
    result = {
        "total_score": min(total, 100),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    main()
