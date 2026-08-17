import json
import os
import sys
import glob

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score = 0
    max_score = 100
    details = []

    # 1. 检查 ops/todo_tasks.json 是否存在 (10分)
    target_path = "ops/todo_tasks.json"
    if os.path.isfile(target_path):
        details.append({"item": "目标文件存在", "score": 10, "max_score": 10, "passed": True, "reason": f"{target_path} 存在"})
        score += 10
    else:
        details.append({"item": "目标文件存在", "score": 0, "max_score": 10, "passed": False, "reason": f"{target_path} 不存在"})
        # 后续检查无法进行，直接记总分并退出
        dump_score(score, details)
        return

    # 2. JSON 合法性 (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "根元素不是数组"})
            dump_score(score, details)
            return
        # 检查每个元素包含 id 和 subject
        for item in data:
            if not isinstance(item, dict) or "id" not in item or "subject" not in item:
                details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "元素缺少 id 或 subject 字段"})
                dump_score(score, details)
                return
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功，数组元素包含 id 和 subject"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        dump_score(score, details)
        return

    # 3. 读取所有原始邮件，构造期望结果
    email_files = glob.glob("data/emails/*.json")
    expected = []
    for ef in email_files:
        with open(ef, "r") as f:
            mail = json.load(f)
        # 条件：重要性 high, 未回复, 标签不含 spam 和 newsletter
        if (mail.get("importance") == "high"
                and mail.get("has_reply") is False
                and "spam" not in mail.get("labels", [])
                and "newsletter" not in mail.get("labels", [])):
            expected.append({
                "id": mail["id"],
                "subject": mail["subject"]
            })
    # 按 id 排序保持确定性
    expected.sort(key=lambda x: x["id"])

    # 4. 比较结果 (70分)
    # 4.1 过滤条件：不含垃圾/新闻 (10分)
    submitted_ids = [item["id"] for item in data]
    spam_ids = set()
    for ef in email_files:
        with open(ef, "r") as f:
            mail = json.load(f)
        if "spam" in mail.get("labels", []) or "newsletter" in mail.get("labels", []):
            spam_ids.add(mail["id"])
    if any(sid in submitted_ids for sid in spam_ids):
        details.append({"item": "排除垃圾/新闻邮件", "score": 0, "max_score": 10, "passed": False, "reason": f"包含不应出现的垃圾/新闻邮件 ID: {[sid for sid in spam_ids if sid in submitted_ids]}"})
    else:
        details.append({"item": "排除垃圾/新闻邮件", "score": 10, "max_score": 10, "passed": True, "reason": "未包含垃圾或新闻邮件"})
        score += 10

    # 4.2 排除已回复 (10分)
    replied_ids = set()
    for ef in email_files:
        with open(ef, "r") as f:
            mail = json.load(f)
        if mail.get("has_reply") is True:
            replied_ids.add(mail["id"])
    if any(rid in submitted_ids for rid in replied_ids):
        details.append({"item": "排除已回复邮件", "score": 0, "max_score": 10, "passed": False, "reason": f"包含已回复的邮件 ID: {[rid for rid in replied_ids if rid in submitted_ids]}"})
    else:
        details.append({"item": "排除已回复邮件", "score": 10, "max_score": 10, "passed": True, "reason": "未包含已回复邮件"})
        score += 10

    # 4.3 只包含高优先级 (10分)
    low_ids = set()
    for ef in email_files:
        with open(ef, "r") as f:
            mail = json.load(f)
        if mail.get("importance") != "high":
            low_ids.add(mail["id"])
    if any(lid in submitted_ids for lid in low_ids):
        details.append({"item": "只包含高优先级", "score": 0, "max_score": 10, "passed": False, "reason": f"包含非高优先级邮件 ID: {[lid for lid in low_ids if lid in submitted_ids]}"})
    else:
        details.append({"item": "只包含高优先级", "score": 10, "max_score": 10, "passed": True, "reason": "所有条目均为高优先级"})
        score += 10

    # 4.4 数量正确 (10分)
    if len(data) == len(expected):
        details.append({"item": "条目数量正确", "score": 10, "max_score": 10, "passed": True, "reason": f"期望 {len(expected)} 条，实际 {len(data)} 条"})
        score += 10
    else:
        details.append({"item": "条目数量正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {len(expected)} 条，实际 {len(data)} 条"})
        # 继续检查但不加分

    # 4.5 内容完全匹配 (20分) - 严格检查 id 和 subject
    # 先将提交列表按 id 排序
    submitted_sorted = sorted(data, key=lambda x: x["id"])
    match = True
    for i, (exp, sub) in enumerate(zip(expected, submitted_sorted)):
        if exp["id"] != sub["id"] or exp["subject"] != sub["subject"]:
            match = False
            details.append({"item": "内容完全匹配", "score": 0, "max_score": 20, "passed": False, "reason": f"第 {i} 项不匹配: 期望 {exp}，实际 {sub}"})
            break
    if match:
        details.append({"item": "内容完全匹配", "score": 20, "max_score": 20, "passed": True, "reason": "所有条目 id 和 subject 均与期望一致"})
        score += 20

    # 额外：检查字段是否有多余
    extra_fields = False
    for item in data:
        keys = set(item.keys())
        if keys - {"id", "subject"}:
            extra_fields = True
            break
    if extra_fields:
        # 扣分但保留前面得分，可添加一个惩罚
        # 这里设计为扣 10 分（没有独立项，直接在总分扣）
        penalty = 10
        details.append({"item": "无多余字段", "score": 0, "max_score": 10, "passed": False, "reason": "包含除 id 和 subject 以外的多余字段"})
        # 实际总分减少 penalty，但为了格式，我们在总分中扣，不在 details 里重复扣？按设计 we 单独扣分
        # 这里我们添加一个-10的细节，但max_score=10? 为简单，我们单独扣10
        score -= penalty
    else:
        details.append({"item": "无多余字段", "score": 10, "max_score": 10, "passed": True, "reason": "仅包含 id 和 subject 字段"})

    dump_score(score, details)


def dump_score(score, details):
    # 限制总分在 0~100
    total = max(0, min(100, score))
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

if __name__ == "__main__":
    main()
