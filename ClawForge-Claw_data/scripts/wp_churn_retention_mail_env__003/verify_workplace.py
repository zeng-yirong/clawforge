"""
验证工作区：检查 cache/retention_emails.json 是否按规则生成。
规则：
1. 高风险客户定义：risk_level=='high' and last_active_days>=30 and usage_trend=='down'
   -> 应为 C001, C005 (注意 activity_logs 中 C002 活跃天数10，C003 risk_level低，C004 usage_trend stable)
2. 每个高风险客户匹配行业新闻：从 news_samples 中选 industry 相同且 tone=='opportunity' 的第一条。
   -> C001/C005 均为 fintech，匹配新闻 N001 (headline: 新支付技术让 LedgerFlow 用户交易量翻倍)
3. 输出 JSON 数组，每个元素必须包含 customer_id, subject, body，且 body 须包含对应新闻 headline。
评分项及权重：
- 10分：文件 cache/retention_emails.json 存在
- 10分：JSON 解析合法
- 10分：输出为数组，且长度 == 2
- 10分：第一个客户 customer_id == 'C001'
- 10分：第二个客户 customer_id == 'C005'
- 10分：C001 的 body 包含 headline "新支付技术让 LedgerFlow 用户交易量翻倍"
- 10分：C005 的 body 包含 headline "新支付技术让 LedgerFlow 用户交易量翻倍"（因为相同新闻）
- 10分：C001 的 subject 非空
- 10分：C005 的 subject 非空
- 10分：无多余高风险客户（即数组中只有这两条记录）
总分 100 分。
"""
import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # ---- 1. 文件存在 ----
    target_path = os.path.join(workspace, "cache", "retention_emails.json")
    file_exists = os.path.isfile(target_path)
    details.append({
        "item": "文件 cache/retention_emails.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })
    if not file_exists:
        # 后续检查无法进行，直接返回
        total_score = 0
        _write_score(details, total_score, workspace)
        return

    # ---- 2. JSON 合法性 ----
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        json_valid = True
        reason = "JSON 解析成功"
    except Exception as e:
        json_valid = False
        reason = f"JSON 解析失败: {e}"
    details.append({
        "item": "JSON 格式合法",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    if not json_valid:
        total_score = sum(d["score"] for d in details)
        _write_score(details, total_score, workspace)
        return

    # ---- 3. 数组长度（应恰好为2）----
    if not isinstance(data, list):
        length_score = 0
        reason = "输出不是数组"
    else:
        length = len(data)
        if length == 2:
            length_score = 10
            reason = f"数组长度 {length}，符合预期"
        else:
            length_score = 0
            reason = f"数组长度 {length}，期望为 2"
    details.append({
        "item": "输出为数组且长度为 2",
        "score": length_score,
        "max_score": 10,
        "passed": length_score == 10,
        "reason": reason
    })

    # ---- 4. 检查每个客户 ----
    # 期望结果：C001, C005
    expected_ids = ["C001", "C005"]
    # 提取实际客户ID列表
    actual_ids = [item.get("customer_id", "") for item in data] if isinstance(data, list) else []

    # 检查第一个客户ID
    first_ok = len(actual_ids) >= 1 and actual_ids[0] == "C001"
    details.append({
        "item": "第一个客户 customer_id = 'C001'",
        "score": 10 if first_ok else 0,
        "max_score": 10,
        "passed": first_ok,
        "reason": f"实际第一个ID: {actual_ids[0] if len(actual_ids)>=1 else 'N/A'}"
    })

    # 检查第二个客户ID
    second_ok = len(actual_ids) >= 2 and actual_ids[1] == "C005"
    details.append({
        "item": "第二个客户 customer_id = 'C005'",
        "score": 10 if second_ok else 0,
        "max_score": 10,
        "passed": second_ok,
        "reason": f"实际第二个ID: {actual_ids[1] if len(actual_ids)>=2 else 'N/A'}"
    })

    # 检查 body 是否包含 headline（期望 headline）
    expected_headline = "新支付技术让 LedgerFlow 用户交易量翻倍"
    # 对C001
    c001_body = ""
    c001_subject = ""
    for item in data:
        if item.get("customer_id") == "C001":
            c001_body = item.get("body", "")
            c001_subject = item.get("subject", "")
            break
    c001_body_ok = expected_headline in c001_body
    details.append({
        "item": "C001 正文包含新闻标题",
        "score": 10 if c001_body_ok else 0,
        "max_score": 10,
        "passed": c001_body_ok,
        "reason": f"实际body包含标题: {c001_body_ok}"
    })

    # 对C005
    c005_body = ""
    c005_subject = ""
    for item in data:
        if item.get("customer_id") == "C005":
            c005_body = item.get("body", "")
            c005_subject = item.get("subject", "")
            break
    c005_body_ok = expected_headline in c005_body
    details.append({
        "item": "C005 正文包含新闻标题",
        "score": 10 if c005_body_ok else 0,
        "max_score": 10,
        "passed": c005_body_ok,
        "reason": f"实际body包含标题: {c005_body_ok}"
    })

    # 检查 subject 非空
    c001_subject_ok = bool(c001_subject and c001_subject.strip())
    details.append({
        "item": "C001 的 subject 非空",
        "score": 10 if c001_subject_ok else 0,
        "max_score": 10,
        "passed": c001_subject_ok,
        "reason": f"subject: '{c001_subject}'"
    })

    c005_subject_ok = bool(c005_subject and c005_subject.strip())
    details.append({
        "item": "C005 的 subject 非空",
        "score": 10 if c005_subject_ok else 0,
        "max_score": 10,
        "passed": c005_subject_ok,
        "reason": f"subject: '{c005_subject}'"
    })

    # ---- 最后检查：是否有多余客户ID（即只有C001和C005）----
    extra_ids = set(actual_ids) - set(expected_ids)
    extra_ok = len(extra_ids) == 0
    details.append({
        "item": "无多余高风险客户（仅含 C001 和 C005）",
        "score": 10 if extra_ok else 0,
        "max_score": 10,
        "passed": extra_ok,
        "reason": f"额外ID: {extra_ids}" if extra_ids else "正确"
    })

    # 计算总分
    total_score = sum(d["score"] for d in details)
    _write_score(details, total_score, workspace)

def _write_score(details, total_score, workspace):
    output = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"验证完成，总分: {total_score}/100")

if __name__ == "__main__":
    main()
