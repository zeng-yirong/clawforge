import sys
import os
import json
import re
import math

def check_password_policy(password, policy):
    """检查单个密码是否满足策略（与builder中逻辑一致）"""
    if len(password) < policy["min_length"]:
        return False
    if policy["require_uppercase"] and not re.search(r'[A-Z]', password):
        return False
    if policy["require_lowercase"] and not re.search(r'[a-z]', password):
        return False
    if policy["require_digit"] and not re.search(r'\d', password):
        return False
    if policy["require_special"] and not re.search(r'[^a-zA-Z0-9]', password):
        return False
    return True

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        score_details.append({
            "item": "ops目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops目录已创建"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops目录不存在"
        })
        # 如果目录不存在，后续文件检查无意义，直接返回
        final_score = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final_score, f)
        return

    # 2. 检查 updated_credentials.json 文件存在且格式合法 (10分)
    cred_file = os.path.join(ops_path, "updated_credentials.json")
    if not os.path.isfile(cred_file):
        score_details.append({
            "item": "updated_credentials.json合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
    else:
        try:
            with open(cred_file, "r") as f:
                updated_creds = json.load(f)
            if not isinstance(updated_creds, list):
                raise ValueError("不是列表")
            score_details.append({
                "item": "updated_credentials.json合法性",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "文件存在且为合法JSON列表"
            })
            total_score += 10
        except Exception as e:
            score_details.append({
                "item": "updated_credentials.json合法性",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON解析失败: {str(e)}"
            })

    # 3. 检查 autofill_rules.json 文件存在且格式合法 (10分)
    autofill_file = os.path.join(ops_path, "autofill_rules.json")
    if not os.path.isfile(autofill_file):
        score_details.append({
            "item": "autofill_rules.json合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
    else:
        try:
            with open(autofill_file, "r") as f:
                autofill_rules = json.load(f)
            if not isinstance(autofill_rules, list):
                raise ValueError("不是列表")
            for rule in autofill_rules:
                if not isinstance(rule, dict) or "platform" not in rule or "enabled" not in rule:
                    raise ValueError("规则缺少platform或enabled字段")
            score_details.append({
                "item": "autofill_rules.json合法性",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "文件存在且为合法JSON列表，每条规则有platform和enabled"
            })
            total_score += 10
        except Exception as e:
            score_details.append({
                "item": "autofill_rules.json合法性",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"解析失败: {str(e)}"
            })

    # 如果任一产物不合法，无法继续精确验证，返回
    if not os.path.isfile(cred_file) or not os.path.isfile(autofill_file):
        final_score = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final_score, f)
        return

    # 4. 验证 updated_credentials.json 内容正确性 (核心，50分)
    # 需要重新加载原始数据，计算期望结果
    try:
        with open(os.path.join(workspace, "vault", "credentials.json")) as f:
            original_creds = json.load(f)
        with open(os.path.join(workspace, "vault", "password_policy.json")) as f:
            policy = json.load(f)
        with open(os.path.join(workspace, "vault", "secure_passwords_pool.json")) as f:
            pool = json.load(f)
        with open(os.path.join(workspace, "vault", "categories.json")) as f:
            categories = json.load(f)
        # build category lookup
        cat_lookup = {c["category_id"]: c for c in categories}
    except Exception as e:
        score_details.append({
            "item": "updated_credentials.json内容正确性",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"无法读取原始数据: {str(e)}"
        })
        total_score += 0
        # 继续后续评分
        pass
    else:
        # 找出所有active凭据，保持原始顺序
        active_creds = [c for c in original_creds if c.get("status") == "active"]
        # 按原始顺序（原文件顺序）
        # 确定哪些需要替换：密码不符合策略的
        needing_replace = []
        for cred in active_creds:
            if not check_password_policy(cred["password"], policy):
                needing_replace.append(cred)
        # 顺序取池中密码
        pool_iter = iter(pool)
        expected_updated = []
        for cred in active_creds:
            new_cred = cred.copy()
            if cred in needing_replace:
                try:
                    new_cred["password"] = next(pool_iter)
                except StopIteration:
                    pass  # 池不足，留原密码（不会发生）
            expected_updated.append(new_cred)
        # 比较 actual updated_creds 与 expected
        cred_errors = []
        if len(updated_creds) != len(expected_updated):
            cred_errors.append(f"凭据条目数不匹配: 期望{len(expected_updated)}，实际{len(updated_creds)}")
        else:
            for i, (exp, act) in enumerate(zip(expected_updated, updated_creds)):
                # 检查关键字段一致：id, username, password, platform, category, status
                keys_to_check = ["id", "username", "password", "platform", "category", "status"]
                for k in keys_to_check:
                    if exp.get(k) != act.get(k):
                        cred_errors.append(f"第{i}条凭据 {k} 不匹配: 期望'{exp.get(k)}', 实际'{act.get(k)}'")
                # 不允许有多余字段（除了原始字段可能有的额外字段，但最好保持一致）
                # 允许有额外字段但不扣分？严格一点：只检查必要字段，有多余字段不扣分
        if cred_errors:
            score_details.append({
                "item": "updated_credentials.json内容正确性",
                "score": 0,
                "max_score": 50,
                "passed": False,
                "reason": "内容错误: " + "; ".join(cred_errors[:5])
            })
        else:
            score_details.append({
                "item": "updated_credentials.json内容正确性",
                "score": 50,
                "max_score": 50,
                "passed": True,
                "reason": "所有凭据更新正确，密码符合策略且按池分配"
            })
            total_score += 50

    # 5. 验证 autofill_rules.json 内容 (剩余20分)
    try:
        # 从 active 凭据中找出密码本就合规的那些（即没有在 needing_replace 中的）
        active_creds = [c for c in original_creds if c.get("status") == "active"]
        compliant_creds = []
        for cred in active_creds:
            if check_password_policy(cred["password"], policy):
                compliant_creds.append(cred)
        # 期望规则：对于每个合规凭据，查看其category的requires_mfa
        expected_rules = []
        for cred in compliant_creds:
            cat = cat_lookup.get(cred["category"])
            if cat is None:
                continue
            # 注意：prompt要求“如果分类要求了MFA，则启用；否则关闭”
            enabled = cat["requires_mfa"]
            expected_rules.append({"platform": cred["platform"], "enabled": enabled})
        # 去重？可能多个凭据有相同平台，但每个规则可以重复？规则通常按平台唯一，但prompt没说去重，所以保留重复定义也接受。
        # 但更好要求每条凭据生成一条规则，所以数量应与合规凭据数量一致。
        # 比较
        rule_errors = []
        if len(autofill_rules) != len(expected_rules):
            rule_errors.append(f"规则数量不匹配: 期望{len(expected_rules)}，实际{len(autofill_rules)}")
        else:
            # 为了让顺序无关，使用排序后比较（但prompt暗示按凭据顺序，所以按顺序比较）
            for i, (exp, act) in enumerate(zip(expected_rules, autofill_rules)):
                if exp["platform"] != act["platform"] or exp["enabled"] != act["enabled"]:
                    rule_errors.append(f"第{i}条规则不匹配: 期望 platform={exp['platform']}, enabled={exp['enabled']}; 实际 platform={act.get('platform')}, enabled={act.get('enabled')}")
        if rule_errors:
            score_details.append({
                "item": "autofill_rules.json内容",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "规则错误: " + "; ".join(rule_errors[:3])
            })
        else:
            score_details.append({
                "item": "autofill_rules.json内容",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "所有自动填充规则正确"
            })
            total_score += 20
    except Exception as e:
        score_details.append({
            "item": "autofill_rules.json内容",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"验证过程异常: {str(e)}"
        })

    # 写入最终评分
    final_score = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final_score, f, indent=2)

if __name__ == "__main__":
    main()
