import json
import os
import sys
import re

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops 目录存在
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ 目录不存在"})
        # 如果目录不存在，后续无法验证文件，直接结束
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 2. 检查 todo_list.json 存在
    todo_path = os.path.join(ops_dir, "todo_list.json")
    if not os.path.isfile(todo_path):
        score_details.append({"item": "todo_list.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return
    else:
        score_details.append({"item": "todo_list.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10

    # 3. 解析 JSON 合法性
    try:
        agent_output = load_json(todo_path)
    except Exception as e:
        score_details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    if not isinstance(agent_output, list):
        score_details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "不是数组"})
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return
    score_details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "合法JSON数组"})
    total_score += 10

    # 4. 检查每个元素的字段完整性
    field_ok = True
    field_errors = []
    for idx, item in enumerate(agent_output):
        if not isinstance(item, dict):
            field_errors.append(f"元素 {idx} 不是字典")
            field_ok = False
            continue
        missing = [k for k in ["email_id", "content", "timestamp"] if k not in item]
        if missing:
            field_errors.append(f"元素 {idx} 缺少字段: {missing}")
            field_ok = False
        else:
            if not isinstance(item["email_id"], str) or not isinstance(item["content"], str) or not isinstance(item["timestamp"], str):
                field_errors.append(f"元素 {idx} 字段类型不正确")
                field_ok = False
    if field_ok:
        score_details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有元素包含必要字段且类型正确"})
        total_score += 10
    else:
        score_details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(field_errors)})

    # 5. 从邮件目录计算正确的TODO列表
    emails_dir = os.path.join(workspace, "data", "emails")
    correct_todos = []  # 每个元素 (content, email_id, timestamp)
    if os.path.isdir(emails_dir):
        for fname in os.listdir(emails_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(emails_dir, fname)
            try:
                mail = load_json(fpath)
            except:
                continue
            # 筛选条件
            if mail.get("has_read", True):
                continue
            if mail.get("importance") not in ("high", "normal"):
                continue
            labels = mail.get("labels", [])
            if "action" not in labels or "spam" in labels:
                continue
            # 提取TODO行
            body = mail.get("body", "")
            lines = body.split("\n")
            for line in lines:
                # 要求严格以 "TODO:" 开头（无前导空白）
                if line.startswith("TODO:"):
                    content = line[5:].strip()
                    if content:  # 非空
                        correct_todos.append((content, mail["id"], mail.get("timestamp", "")))
        # 去重：相同content保留timestamp最小的
        content_map = {}
        for content, eid, ts in correct_todos:
            if content not in content_map or ts < content_map[content][1]:
                content_map[content] = (eid, ts)
        # 转成列表并按照timestamp排序
        sorted_correct = sorted(content_map.items(), key=lambda x: x[1][1])  # sort by timestamp
        correct_list = [{"email_id": eid, "content": content, "timestamp": ts} for content, (eid, ts) in sorted_correct]
    else:
        correct_list = []

    N = len(correct_list)
    M = len(agent_output)

    # 6. 检查agent输出是否去重且字段匹配
    # 将agent输出转为 dict by content
    agent_map = {}
    for item in agent_output:
        content = item.get("content", "")
        if content in agent_map:
            # 重复content，标记为多余
            agent_map[content] = ("duplicate", None, None)
        else:
            agent_map[content] = (item.get("email_id"), item.get("timestamp"), item)

    # 计算正确匹配
    match_count = 0
    mismatch_reasons = []
    for correct_item in correct_list:
        content = correct_item["content"]
        if content in agent_map:
            aid, ats, _ = agent_map[content]
            if aid == correct_item["email_id"] and ats == correct_item["timestamp"]:
                match_count += 1
            else:
                mismatch_reasons.append(f"content '{content}' 的email_id或timestamp不匹配")
                # 即使不匹配，也算agent有这个content，不当作缺失
        else:
            mismatch_reasons.append(f"缺少TODO: '{content}'")

    # 计算多余条目：agent有但正确没有，或者重复content
    extra_count = 0
    for content, (aid, ats, item) in agent_map.items():
        if aid == "duplicate":
            extra_count += 1
            mismatch_reasons.append(f"重复content: '{content}'")
        elif content not in [c["content"] for c in correct_list]:
            extra_count += 1
            mismatch_reasons.append(f"多余TODO: '{content}'")

    # 缺失条目 = N - match_count
    missing_count = N - match_count

    # 评分：满分70（剩余分数在文件结构等已扣）
    max_match_score = 70
    if N == 0 and M == 0:
        match_score = max_match_score
    elif N == 0:
        # 正确为空，agent输出了多余，全扣
        match_score = 0
    else:
        # 每个正确匹配得 max_match_score / N，每个多余或缺失扣相同分数
        unit = max_match_score / N
        raw_score = match_count * unit - extra_count * unit - missing_count * unit
        match_score = max(0, raw_score)

    score_details.append({
        "item": "TODO内容精确匹配",
        "score": round(match_score, 1),
        "max_score": max_match_score,
        "passed": match_score == max_match_score,
        "reason": f"正确数={N}，匹配数={match_count}，多余={extra_count}，缺失={missing_count}; " + "; ".join(mismatch_reasons[:5])
    })
    total_score += match_score

    # 写入最终得分（四舍五入为整数）
    total_score_int = min(100, round(total_score))
    result = {"total_score": total_score_int, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
