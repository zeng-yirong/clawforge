import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录结构 (10分)
    dirs = [
        os.path.join(workspace, "data", "customers"),
        os.path.join(workspace, "data", "logs"),
        os.path.join(workspace, "data", "news"),
        os.path.join(workspace, "cache"),
    ]
    dirs_ok = all(os.path.isdir(d) for d in dirs)
    if dirs_ok:
        details.append({"item": "目录结构完整", "score": 10, "max_score": 10, "passed": True, "reason": "所有必须目录存在"})
        total_score += 10
    else:
        missing = [d for d in dirs if not os.path.isdir(d)]
        details.append({"item": "目录结构完整", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少目录: {missing}"})

    # 2. 检查产物文件存在 (10分)
    cache_file = os.path.join(workspace, "cache", "retention_mail_cache.json")
    if os.path.isfile(cache_file):
        details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "cache/retention_mail_cache.json 存在"})
        total_score += 10
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "cache/retention_mail_cache.json 未找到"})
        # 如果文件不存在，后续检查直接扣分并返回
        details.append({"item": "JSON合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，无法检查"})
        details.append({"item": "内容准确性", "score": 0, "max_score": 70, "passed": False, "reason": "文件不存在"})
        _save_score(details, total_score, max_total, workspace)
        return

    # 3. 检查JSON合法性 (10分)
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({"item": "JSON合法性", "score": 10, "max_score": 10, "passed": True, "reason": "合法JSON数组"})
            total_score += 10
        else:
            details.append({"item": "JSON合法性", "score": 5, "max_score": 10, "passed": False, "reason": "JSON不是数组"})
            total_score += 5
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "JSON合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        # 无法继续检查内容
        details.append({"item": "内容准确性", "score": 0, "max_score": 70, "passed": False, "reason": "JSON非法"})
        _save_score(details, total_score, max_total, workspace)
        return

    # 4. 内容准确性 (70分) —— 分解：剔除脏数据20分 + 关键计算50分
    # 期望结果：
    # 高风险客户：risk_level=high, last_active_days>30, ticket_sentiment=negative
    # 从activity_logs中筛选：C001(45), C003(60), C004(32) => 都满足
    # 注意C001有两条日志，取第一个（或去重按customer_id取第一个），实际正确应取C001第一个。
    # 注意C004的last_active_days=32>30，满足。
    # 匹配新闻：industry相同且tone='opportunity'
    #  fintech => N001 (opportunity), retail => N002 (opportunity)
    # 所以C001和C003匹配N001，C004匹配N002。
    # 预期邮件内容：
    expected = [
        {
            "customer_id": "C001",
            "customer_name": "LedgerFlow",
            "email": "alice@example.com",
            "industry": "fintech",
            "news_headline": "央行发布数字人民币新规",
            "subject": "【挽留】关于LedgerFlow服务优化的建议",
            "body": "尊敬的LedgerFlow团队，我们注意到您近期活跃度下降，工单反馈也显示了一些不满。央行新规带来新机遇，我们已为您准备了专属解决方案，希望能重新为您创造价值。期待您的回应。"
        },
        {
            "customer_id": "C003",
            "customer_name": "PayBridge",
            "email": "charlie@example.com",
            "industry": "fintech",
            "news_headline": "央行发布数字人民币新规",
            "subject": "【挽留】关于PayBridge服务优化的建议",
            "body": "尊敬的PayBridge团队，您已有60天未活跃，我们十分担心。恰逢数字人民币新规出台，我们的产品可帮助您快速合规升级。请给我们一次机会，一起探讨新方案。"
        },
        {
            "customer_id": "C004",
            "customer_name": "RetailSync",
            "email": "diana@example.com",
            "industry": "retail",
            "news_headline": "线下零售回暖，智慧仓储需求激增",
            "subject": "【挽留】关于RetailSync服务优化的建议",
            "body": "尊敬的RetailSync团队，您近期工单情绪较低，我们理解零售业的压力。线下回暖之际，智慧仓储需求大增，我们的系统能帮您抓住这波红利。愿与您携手共进。"
        }
    ]
    # 注意：由于现实agent可能自由发挥，但我们需要精确匹配字段值？不能要求字符串完全一致，
    # 但应要求customer_id、email、industry、news_headline与数据一致。
    # subject和body可以有一定灵活性，但必须包含关键信息（如客户名、行业新闻摘要）。
    # 但是验证规则要求纯代码可判定，不能用模糊匹配。所以我们可以设计成要求固定的subject和body吗？
    # 更合理的方法：只对可结构化抽取的客观要素评分：customer_id集合、email、news_headline。
    # 去掉对subject和body的强匹配，改为检查是否存在对应字段以及内容非空且包含客户名。
    # 但为了唯一答案，在prompt中我们并没有明确指定邮件格式，所以agent可能输出不同的subject/body。
    # 作为评测任务，我们应该允许合理变化，但需保证客观要素正确。
    # 更好的做法：在env_builder中故意设计使答案唯一：例如要求邮件body使用固定模板？
    # 但prompt没有模板，所以我们需要调整设计：让agent必须输出哪些字段？我们可以在prompt中隐含要求：收件人、主题、正文。
    # 但prompt不能泄露验证逻辑。那么我们可以用“包含哪些信息”来约束，比如“写一封简短的挽留邮件草稿，包含收件人、主题、正文”。
    # 所以验证时检查每个条目是否有customer_id, email, subject, body, industry, news_headline？这些字段。
    # 但subject和body的具体内容无法精确验证，只能检查是否非空。
    # 我们可以给这部分分值较少，而核心的客户ID和新闻匹配占大分。
    # 修改评分方案：
    # 4a. 邮件条目数量正确（只能包含3个客户C001,C003,C004，不能多不能少）(20分)
    # 4b. 每个条目的customer_id与活动日志中高风险客户一致 (10分)
    # 4c. 每个条目中email字段正确（从客户数据推断）(10分)
    # 4d. 每个条目中industry字段正确 (10分)
    # 4e. 每个条目中news_headline正确 (10分)
    # 4f. subject和body非空且包含客户名 (10分)
    # 总计70分

    sub_score = 0
    # 4a
    if isinstance(data, list):
        actual_ids = set(item.get("customer_id") for item in data if isinstance(item, dict))
        expected_ids = {"C001", "C003", "C004"}
        if actual_ids == expected_ids:
            sub_score += 20
            details.append({"item": "邮件条目正确（客户ID集合）", "score": 20, "max_score": 20, "passed": True, "reason": f"包含客户 {sorted(actual_ids)}"})
        else:
            missing = expected_ids - actual_ids
            extra = actual_ids - expected_ids
            details.append({"item": "邮件条目正确（客户ID集合）", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失: {missing}, 多余: {extra}"})
        # 构建映射
        item_map = {item["customer_id"]: item for item in data if isinstance(item, dict) and "customer_id" in item}
        # 4b,4c,4d,4e,4f
        for cid in expected_ids:
            if cid not in item_map:
                continue
            item = item_map[cid]
            # 4b customer_id 已检查过
            # 4c email
            # 模拟客户数据：C001->alice@example.com (假设owner_name+@example.com)
            # 但实际客户数据中并没有email字段！env_builder创建了customers.json但其中没有email。
            # 剧情中agent需要自己推导邮件格式？这可能有歧义。我们需要重新设计env_builder。
            # 危险！客户数据中没有email，那agent怎么知道收件人邮箱？prompt只说了客户清单，没有邮箱。
            # 所以我们需要在customers.json中加入email字段，或者在活动日志中加入邮箱。
            # 重新修改env_builder: 在customers.json中增加email字段。
            # 但由于我们已假设输出，这里需要回溯修改env_builder。
            # 为了节省时间，我们可以在验证时忽略email字段，只检查存在性。
            # 更合理的做法：在env_builder中为每个客户添加email字段。
            # 我将重新修改env_builder，添加email。
            pass

    # 由于env_builder需要同步修改，这里先占位，后面整体更新。
    # 暂时返回占位分数
    details.append({"item": "内容准确性（占位）", "score": 0, "max_score": 70, "passed": False, "reason": "需要重新实现"})

    _save_score(details, total_score, max_total, workspace)

def _save_score(details, total_score, max_total, workspace):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Scored {total_score}/{max_total}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
