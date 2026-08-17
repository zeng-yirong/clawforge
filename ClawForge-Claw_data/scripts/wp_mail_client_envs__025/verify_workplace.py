import json
import os
import sys
import re

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    required_dirs = ["data", "data/emails", "ops"]
    all_dirs_exist = True
    for d in required_dirs:
        full_path = os.path.join(workspace, d)
        if not os.path.isdir(full_path):
            all_dirs_exist = False
            details.append({"item": f"Directory '{d}' exists", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing directory: {d}"})
            break
    if all_dirs_exist:
        details.append({"item": "Required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "All three directories present"})
        total_score += 10

    # 2. 结果文件存在性 (10分)
    result_file = os.path.join(workspace, "ops", "bob_urgent.json")
    if not os.path.isfile(result_file):
        details.append({"item": "ops/bob_urgent.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 后续步骤无法进行，直接返回
        return {"total_score": total_score, "details": details}
    else:
        details.append({"item": "ops/bob_urgent.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10

    # 3. JSON 合法性 (10分)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        details.append({"item": "File is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        return {"total_score": total_score, "details": details}
    if not isinstance(data, list):
        details.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": "Root element is not a list"})
        return {"total_score": total_score, "details": details}
    details.append({"item": "File is valid JSON array", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully as list"})
    total_score += 10

    # 4. 内容正确性 (70分)
    # 重新扫描所有邮件，按条件过滤出标准答案
    emails_dir = os.path.join(workspace, "data", "emails")
    expected = []  # list of (id, subject) sorted by id
    if os.path.isdir(emails_dir):
        for filename in os.listdir(emails_dir):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(emails_dir, filename)
            try:
                with open(filepath, "r") as f:
                    email = json.load(f)
            except:
                continue
            sender = email.get("sender_id", "")
            importance = email.get("importance", "")
            if sender == "bob@vendor-services.com" and importance == "high":
                eid = email.get("id", "")
                subject = email.get("subject", "")
                expected.append((eid, subject))
        expected.sort(key=lambda x: x[0])  # 按 ID 排序
    else:
        # 目录不存在，但前面已检查，不会走到这里
        pass

    # 检查 agent 输出的列表
    agent_items = []
    for item in data:
        if not isinstance(item, dict):
            continue
        eid = item.get("id", "")
        subject = item.get("subject", "")
        agent_items.append((eid, subject))
    # 由于 prompt 要求按 id 排序，这里也假设 agent 排序了，但为了稳健，先排序再比较
    agent_sorted = sorted(agent_items, key=lambda x: x[0])

    # 完全匹配（顺序和内容）
    if agent_sorted == expected:
        details.append({"item": "Correct IDs and subjects (sorted)", "score": 70, "max_score": 70, "passed": True, "reason": "All items match expected"})
        total_score += 70
    else:
        # 部分匹配：检查集合是否一致（不考虑顺序）
        agent_set = set(agent_sorted)
        expected_set = set(expected)
        if agent_set == expected_set:
            # 顺序错误，扣10分
            details.append({"item": "Correct items but wrong order", "score": 60, "max_score": 70, "passed": False, "reason": f"Items match but order differs. Expected sorted: {expected}, got: {agent_sorted}"})
            total_score += 60
        else:
            # 计算正确个数
            correct = len(agent_set & expected_set)
            wrong = len(agent_set - expected_set)
            missing = len(expected_set - agent_set)
            # 每项满分 70 / len(expected) 但期望至少3项，简化：给正确比例分
            if len(expected) > 0:
                score_per_item = 70 / len(expected)
                correct_score = int(correct * score_per_item)
            else:
                correct_score = 0
            # 但需保持整数，向下取整
            details.append({"item": "Correct items", "score": min(correct_score, 70), "max_score": 70, "passed": False, "reason": f"Correct: {correct}, wrong extra: {wrong}, missing: {missing}"})
            total_score += min(correct_score, 70)

    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入 score 文件
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {result['total_score']}/100")
