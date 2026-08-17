import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查 (10分)
    item = {"item": "目标目录 ops 存在", "max_score": 5, "passed": False, "score": 0, "reason": ""}
    if os.path.isdir("ops"):
        item["passed"] = True
        item["score"] = 5
        item["reason"] = "ops/ 目录存在"
    else:
        item["reason"] = "ops/ 目录不存在"
    details.append(item)
    total_score += item["score"]

    item = {"item": "输出文件 ops/denied_requests.json 存在", "max_score": 5, "passed": False, "score": 0, "reason": ""}
    if os.path.isfile("ops/denied_requests.json"):
        item["passed"] = True
        item["score"] = 5
        item["reason"] = "文件存在"
    else:
        item["reason"] = "ops/denied_requests.json 不存在"
    details.append(item)
    total_score += item["score"]

    # 2. JSON 合法性 (10分)
    item = {"item": "输出文件 JSON 合法且包含列表", "max_score": 10, "passed": False, "score": 0, "reason": ""}
    if not os.path.isfile("ops/denied_requests.json"):
        item["reason"] = "文件缺失，无法校验"
        details.append(item)
    else:
        try:
            with open("ops/denied_requests.json", "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                item["passed"] = True
                item["score"] = 10
                item["reason"] = "有效 JSON 数组"
            else:
                item["reason"] = "JSON 根不是数组"
        except Exception as e:
            item["reason"] = f"JSON 解析失败: {e}"
        details.append(item)
        total_score += item["score"]

    # 3. 计算预期的拒绝列表 (基于工作区自有数据)
    expected_denied = set()
    # 读取 accounts 和 contacts
    try:
        with open("data/accounts.json") as f:
            accounts_data = json.load(f)
        accounts = {a["account_id"]: a for a in accounts_data.get("accounts", [])}
        with open("data/contacts.json") as f:
            contacts_data = json.load(f)
        # 获取合法审计员的邮箱集合
        auditor_emails = {c["email"] for c in contacts_data.get("contacts", []) if c.get("role") == "Security Auditor"}
        # 读取请求
        with open("data/requests/requests.json") as f:
            reqs_data = json.load(f)
        for req in reqs_data.get("requests", []):
            if req.get("claimed_role") != "Internal Security Auditor":
                continue
            # 只关心pending？ prompt 未限定状态，但所有请求都是pending，默认全考虑
            actor = req.get("actor_name")
            if actor not in accounts:
                # 账户不存在 → 冒充
                expected_denied.add(req["request_id"])
            else:
                account_email = accounts[actor]["email"]
                if account_email not in auditor_emails:
                    # 账户存在但邮箱不在合法审计员列表 → 冒充
                    expected_denied.add(req["request_id"])
                # 否则是合法审计员，不加入
    except Exception as e:
        # 如果工作区数据无法解析，则说明 agent 的环境有问题，但此情形不应出现
        pass

    # 4. 结果准确性 (70分)
    # 读取 agent 输出的列表
    agent_ids = set()
    if os.path.isfile("ops/denied_requests.json"):
        try:
            with open("ops/denied_requests.json") as f:
                agent_ids = set(json.load(f))
        except:
            pass

    # 精确匹配：没有误报（agent 多出的）和没有漏报（agent 缺少的）
    missed = expected_denied - agent_ids
    extra = agent_ids - expected_denied
    if len(missed) == 0 and len(extra) == 0:
        item = {"item": "拒绝列表完全正确", "max_score": 70, "passed": True, "score": 70, "reason": "无漏报、无误报"}
        total_score += 70
    else:
        # 按比例扣分
        total_expected = len(expected_denied)
        correct_hits = len(expected_denied & agent_ids)
        # 漏报扣分：每个漏报扣 35/total_expected (最多35)
        # 误报扣分：每个误报扣 35/total_expected (最多35)
        if total_expected == 0:
            penalty = 0
        else:
            penalty_miss = len(missed) * (35.0 / total_expected)
            penalty_extra = len(extra) * (35.0 / total_expected)
            penalty = min(70, int(penalty_miss + penalty_extra))
        score = max(0, 70 - penalty)
        reason = f"预期拒绝 {sorted(expected_denied)}, 实际拒绝 {sorted(agent_ids)}; 漏报 {len(missed)}, 误报 {len(extra)}"
        item = {"item": "拒绝列表正确性", "max_score": 70, "passed": score == 70, "score": score, "reason": reason}
        total_score += score
        details.append(item)

    # 补充缺失的 item
    # 注意: above 中的最终 item 需要 append
    # 因为上面在分支中 append 了，但 item 变量被覆盖，我们确保在最后只保留一个
    # 重组 details: 上面的 item 已经在分支中 append，但最后这个 item 没被 append？ 检查：
    # 在精确匹配分支中，我们做了 details.append(item)？ 没有，我们需要补上。
    # 我们重新组织一下：先计算 item，然后 append

    # 重新整理：为了代码清晰，单独处理正确性 item
    if len(missed) == 0 and len(extra) == 0:
        item_correct = {"item": "拒绝列表完全正确", "max_score": 70, "passed": True, "score": 70, "reason": "无漏报、无误报"}
    else:
        total_expected = len(expected_denied) if len(expected_denied) > 0 else 1  # 避免除零
        correct_hits = len(expected_denied & agent_ids)
        penalty_miss = len(missed) * (35.0 / total_expected)
        penalty_extra = len(extra) * (35.0 / total_expected)
        penalty = min(70, int(penalty_miss + penalty_extra))
        score = max(0, 70 - penalty)
        reason = f"预期拒绝 {sorted(expected_denied)}, 实际拒绝 {sorted(agent_ids)}; 漏报 {len(missed)}, 误报 {len(extra)}"
        item_correct = {"item": "拒绝列表正确性", "max_score": 70, "passed": score == 70, "score": score, "reason": reason}
    details.append(item_correct)
    total_score += item_correct["score"]

    # 确保总分在0-100
    total_score = min(100, max(0, total_score))

    # 输出评分结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")
    sys.exit(0 if total_score == 100 else 1)

if __name__ == "__main__":
    main()
