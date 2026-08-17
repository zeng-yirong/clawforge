import sys, os, json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify(workspace):
    results = []
    total = 0
    max_total = 100

    # 1 检查分类文件存在且格式正确（10分）
    classified_path = os.path.join(workspace, "classified", "classified_data.json")
    if os.path.exists(classified_path):
        try:
            classified = load_json(classified_path)
            results.append({"item": "分类文件存在且合法", "score": 10, "max_score": 10, "passed": True, "reason": "classified_data.json 存在且可解析"})
            total += 10
        except:
            results.append({"item": "分类文件存在但非法", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败"})
    else:
        results.append({"item": "分类文件不存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 classified/classified_data.json"})

    # 2 检查分类内容正确性（30分）
    if classified_path and os.path.exists(classified_path):
        expected_categories = {
            "工作邮箱": ["cred_001"],
            "电商平台": ["cred_002"],
            "银行账户": ["cred_003", "cred_004"],
            "社交媒体": ["cred_005"]
        }
        score_cat = 30
        for cat, expected_ids in expected_categories.items():
            if cat not in classified:
                score_cat -= 7.5
                continue
            actual_ids = [cred["id"] for cred in classified[cat]]
            if sorted(actual_ids) != sorted(expected_ids):
                score_cat -= 7.5
            # 检查每个凭证字段完整性（简化：至少包含id, username, site, password, strength, expiry）
            for cred in classified[cat]:
                for field in ["id","username","site","password","strength","expiry"]:
                    if field not in cred:
                        score_cat -= 2
                        break
        # 不允许出现未知类别或无映射的凭证
        for cat in classified:
            if cat not in expected_categories:
                score_cat -= 5
        final_cat_score = max(0, min(30, score_cat))
        results.append({"item": "分类内容准确", "score": final_cat_score, "max_score": 30, "passed": final_cat_score==30, "reason": f"得分{final_cat_score}/30"})
        total += final_cat_score
    else:
        results.append({"item": "分类内容", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})

    # 3 检查银行账户升级密码（30分）
    vault_path = os.path.join(workspace, "vault", "upgraded_bank_credentials.json")
    if os.path.exists(vault_path):
        try:
            bank_creds = load_json(vault_path)
        except:
            bank_creds = []
        expected_bank_ids = ["cred_003", "cred_004"]
        expected_new_pws = {"cred_003": "NewStr0ng!Pass", "cred_004": "Another#1Strong"}
        score_vault = 30
        # 必须有且只有这两个凭证
        if len(bank_creds) != 2:
            score_vault -= 10
        for cred in bank_creds:
            if cred.get("id") not in expected_bank_ids:
                score_vault -= 10
            else:
                if cred.get("password") != expected_new_pws[cred["id"]]:
                    score_vault -= 10
                # 其他字段保留原样
                for field in ["username","site","strength","expiry"]:
                    if field not in cred:
                        score_vault -= 5
                        break
        # 不能包含无关凭证
        ids_present = set(c.get("id") for c in bank_creds)
        if ids_present - set(expected_bank_ids):
            score_vault -= 5
        final_vault_score = max(0, min(30, score_vault))
        results.append({"item": "银行账户密码升级", "score": final_vault_score, "max_score": 30, "passed": final_vault_score==30, "reason": f"得分{final_vault_score}/30"})
        total += final_vault_score
    else:
        results.append({"item": "银行账户密码升级", "score": 0, "max_score": 30, "passed": False, "reason": "vault/upgraded_bank_credentials.json 不存在"})

    # 4 检查电商 autofill 规则（30分）
    autofill_path = os.path.join(workspace, "autofill", "autofill_rules.json")
    if os.path.exists(autofill_path):
        try:
            rules = load_json(autofill_path)
        except:
            rules = []
        score_auto = 30
        expected_rules_count = 1  # 只有 cred_002 满足 strength>=70 且类别是电商
        if len(rules) != 1:
            score_auto -= 10
        # 检查规则内容
        if rules:
            rule = rules[0]
            if rule.get("site") != "shop.example.com":
                score_auto -= 10
            if rule.get("username") != "bob@shop.com":
                score_auto -= 10
            if rule.get("password") != "strong!Pass":
                score_auto -= 10
        # 不允许有多余规则
        final_auto_score = max(0, min(30, score_auto))
        results.append({"item": "电商自动填充规则", "score": final_auto_score, "max_score": 30, "passed": final_auto_score==30, "reason": f"得分{final_auto_score}/30"})
        total += final_auto_score
    else:
        results.append({"item": "电商自动填充规则", "score": 0, "max_score": 30, "passed": False, "reason": "autofill/autofill_rules.json 不存在"})

    # 写入评分文件
    score_data = {
        "total_score": min(total, max_total),
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
