#!/usr/bin/env python3
"""
verify_workplace.py — 纯代码验证 agent 产出的 vault_report.json 和 autofill_rules.json
Score range: 0-100
"""
import sys
import json
import csv
import os
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # ------------------------------------------------------------
    # 1. 检查 mandatory 输出文件存在性 (各 10 分, 共20)
    # ------------------------------------------------------------
    report_path = os.path.join(workspace, "vault_report.json")
    rules_path = os.path.join(workspace, "autofill_rules.json")

    for path, name, max_s in [(report_path, "vault_report.json", 10), (rules_path, "autofill_rules.json", 10)]:
        exists = os.path.isfile(path)
        details.append({
            "item": f"文件 {name} 存在",
            "score": max_s if exists else 0,
            "max_score": max_s,
            "passed": exists,
            "reason": "文件存在" if exists else "文件缺失"
        })
        if not exists:
            # 如果缺失主报告，后续验证无法进行，直接返回
            score = sum(d["score"] for d in details)
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump({"total_score": score, "details": details}, f, indent=2)
            print(f"Critical file missing, early exit. Score={score}")
            return

    # ------------------------------------------------------------
    # 2. 解析 vault_report.json (30分)
    # ------------------------------------------------------------
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        details.append({"item": "vault_report.json 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "vault_report.json 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        score = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 结构检查：必须包含 categories 字段，且为列表
    if "categories" not in report or not isinstance(report["categories"], list):
        details.append({"item": "报告包含 categories 列表", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 categories 字段或非列表"})
        score = sum(d["score"] for d in details)
        write_score(workspace, score, details)
        return
    else:
        details.append({"item": "报告包含 categories 列表", "score": 10, "max_score": 10, "passed": True, "reason": "存在 categories 列表"})

    # 检查 categories 内容：必须包含4个预设类别，每个类别下有 credentials 列表
    expected_categories = {"工作邮箱", "电商平台", "社交媒体", "银行账户"}
    found_categories = set()
    total_credentials = 0
    for cat in report["categories"]:
        if not isinstance(cat, dict):
            continue
        name = cat.get("name", "")
        if name in expected_categories:
            found_categories.add(name)
        if "credentials" in cat and isinstance(cat["credentials"], list):
            total_credentials += len(cat["credentials"])

    cat_score = 10 if found_categories == expected_categories else 0
    details.append({
        "item": "类别覆盖完整 (四个预设类别)",
        "score": cat_score,
        "max_score": 10,
        "passed": cat_score == 10,
        "reason": f"找到类别: {found_categories}" if cat_score else f"缺失类别: {expected_categories - found_categories}"
    })

    # 凭据数量：有效凭据应为5个（所有有效未删除的），但注意 env_builder 中有效5个，但 notes 中又重复出现了支付宝和银行等，但 csv 和 notes 有重叠，
    # agent 应去重整合后仍然保留5个。排除泄露的 wechat 密码 P@ssw0rd!2025 在泄露列表中，所以 wechat 应被排除。
    # 实际应该只有4个有效凭据？再仔细分析：
    #   valid_credentials 中有: workmail, shopee, wechat, bank_icbc, alipay (5个)
    #   wechat 的密码 P@ssw0rd!2025 在 known_breaches.txt 中，所以应该被排除
    #   其余4个保留。另外 notes 中包含的支付宝和银行与 csv 重复，应去重。
    # 所以最终有效凭据应为4个：workmail, shopee, bank_icbc, alipay
    # 验证总凭据数量
    expected_count = 4
    count_ok = (total_credentials == expected_count)
    details.append({
        "item": f"有效凭据总数 (排除泄露、过期、低强度) = {expected_count}",
        "score": 20 if count_ok else 0,
        "max_score": 20,
        "passed": count_ok,
        "reason": f"找到 {total_credentials} 个凭据" if count_ok else f"期望 {expected_count} 个，实际 {total_credentials}"
    })

    # 额外扣分：如果包含不存在的平台或未去重，扣分
    platform_set = set()
    for cat in report["categories"]:
        for cred in cat.get("credentials", []):
            plat = cred.get("platform", "")
            platform_set.add(plat)
    # 期望的平台集合
    expected_platforms = {"workmail", "shopee", "bank_icbc", "alipay"}
    platform_ok = platform_set == expected_platforms
    if not platform_ok:
        # 从 total_credentials 分数中扣？我们单独一项
        details.append({
            "item": "凭据平台正确（无包含无效或重复平台）",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": f"发现平台: {platform_set}, 期望: {expected_platforms}"
        })
        # 从上面总个数分数中扣10分（如果已给满分则修改）
        for d in details:
            if d["item"].startswith("有效凭据总数"):
                if count_ok:
                    d["score"] = 10  # 扣10分
                    d["reason"] += "，但平台不正确"
                break

    # ------------------------------------------------------------
    # 3. 解析 autofill_rules.json (20分)
    # ------------------------------------------------------------
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            rules = json.load(f)
        details.append({"item": "autofill_rules.json 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "autofill_rules.json 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        write_score(workspace, sum(d["score"] for d in details), details)
        return

    # 检查规则数组
    if not isinstance(rules, dict) or "rules" not in rules or not isinstance(rules["rules"], list):
        details.append({"item": "rules 字段存在且为列表", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 rules 字段或非列表"})
        write_score(workspace, sum(d["score"] for d in details), details)
        return
    else:
        details.append({"item": "rules 字段存在且为列表", "score": 10, "max_score": 10, "passed": True, "reason": "规则数组存在"})

    # 规则数量必须与有效凭据一致 (4)
    rule_count = len(rules["rules"])
    rule_count_ok = rule_count == expected_count
    details.append({
        "item": f"规则数量 = {expected_count}",
        "score": 10 if rule_count_ok else 0,
        "max_score": 10,
        "passed": rule_count_ok,
        "reason": f"发现 {rule_count} 条规则" if rule_count_ok else f"期望 {expected_count} 条"
    })

    # 检查每条规则包含 platform, username, urlPattern
    rule_fields_ok = True
    for rule in rules["rules"]:
        if not isinstance(rule, dict):
            rule_fields_ok = False
            break
        if "platform" not in rule or "username" not in rule or "urlPattern" not in rule:
            rule_fields_ok = False
            break
        # urlPattern 应匹配 *.xxx.com 或类似
        if not re.search(r"^\*?\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", rule["urlPattern"]):
            rule_fields_ok = False
            break
    details.append({
        "item": "每条规则包含 platform, username, urlPattern (合法域名)",
        "score": 10 if rule_fields_ok else 0,
        "max_score": 10,
        "passed": rule_fields_ok,
        "reason": "字段齐全且格式正确" if rule_fields_ok else "字段缺失或错误"
    })

    # ------------------------------------------------------------
    # 4. 综合计算总分
    # ------------------------------------------------------------
    score = sum(d["score"] for d in details)
    # 确保不超过100
    score = min(score, 100)
    write_score(workspace, score, details)

def write_score(workspace, total, details):
    path = os.path.join(workspace, "workplace_score.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    print(f"Score written: {total}")

if __name__ == "__main__":
    main()
