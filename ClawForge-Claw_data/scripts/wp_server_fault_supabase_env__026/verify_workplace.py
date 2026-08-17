import sys
import os
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score = 0
    details = []

    # --- 1. 检查 ops 目录是否存在 (10分) ---
    if os.path.isdir("ops"):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录存在"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录不存在"})

    # --- 2. 检查 ops/escalation_list.json 是否存在 (10分) ---
    target_path = "ops/escalation_list.json"
    if os.path.isfile(target_path):
        details.append({"item": "escalation_list.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        score += 10
    else:
        details.append({"item": "escalation_list.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续无法检查，直接返回
        details.append({"item": "JSON格式 & 内容验证", "score": 0, "max_score": 80, "passed": False, "reason": "跳过后续检查"})
        total_score = score
        output = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        print(f"Score: {total_score}/100")
        return

    # --- 3. 解析JSON合法性 (15分) ---
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON validity", "score": 15, "max_score": 15, "passed": True, "reason": "JSON解析成功"})
        score += 15
    except Exception as e:
        details.append({"item": "JSON validity", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON解析失败: {e}"})
        # 无法继续
        total_score = score
        output = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        print(f"Score: {total_score}/100")
        return

    # --- 4. 检查内容是否为列表 (5分) ---
    if isinstance(data, list):
        details.append({"item": "top-level is list", "score": 5, "max_score": 5, "passed": True, "reason": "顶层是数组"})
        score += 5
    else:
        details.append({"item": "top-level is list", "score": 0, "max_score": 5, "passed": False, "reason": f"顶层类型是 {type(data).__name__}"})
        total_score = score
        output = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        print(f"Score: {total_score}/100")
        return

    # --- 5. 检查列表长度 (10分) 正确应为2个 ---
    if len(data) == 2:
        details.append({"item": "list length is 2", "score": 10, "max_score": 10, "passed": True, "reason": f"长度2，符合预期"})
        score += 10
    else:
        details.append({"item": "list length is 2", "score": 0, "max_score": 10, "passed": False, "reason": f"实际长度 {len(data)}"})

    # --- 6. 检查每个元素都是字符串且格式正确 (10分) ---
    all_strings = all(isinstance(item, str) for item in data)
    if all_strings:
        details.append({"item": "all elements are strings", "score": 10, "max_score": 10, "passed": True, "reason": "全部为字符串"})
        score += 10
    else:
        details.append({"item": "all elements are strings", "score": 0, "max_score": 10, "passed": False, "reason": "存在非字符串元素"})

    # --- 7. 检查ID集合是否完全正确 (40分) 只有I-2024-0001和I-2024-0002，按opened_at升序 ---
    expected_ids = ["I-2024-0002", "I-2024-0001"]  # 0002时间更早 (00:15) < 0001 (01:30)
    if data == expected_ids:
        details.append({"item": "exact list content", "score": 40, "max_score": 40, "passed": True, "reason": "ID列表与顺序完全正确"})
        score += 40
    else:
        # 部分正确给部分分数
        correct_count = sum(1 for e in data if e in expected_ids)
        correct_order = (data == sorted(expected_ids))  # 如果只是顺序错，扣10分
        reason = f"正确ID个数 {correct_count}/2；顺序正确？{correct_order}"
        if correct_count == 2 and not correct_order:
            details.append({"item": "exact list content", "score": 30, "max_score": 40, "passed": True, "reason": "ID正确但顺序错误"})
            score += 30
        elif correct_count == 1:
            details.append({"item": "exact list content", "score": 10, "max_score": 40, "passed": False, "reason": "只有一个正确ID"})
            score += 10
        elif correct_count == 0:
            details.append({"item": "exact list content", "score": 0, "max_score": 40, "passed": False, "reason": "没有正确ID"})
        else:
            # 包含多余ID或顺序错
            details.append({"item": "exact list content", "score": 20, "max_score": 40, "passed": False, "reason": "存在额外ID或缺失"})
            score += 20

    total_score = score
    output = {"total_score": total_score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    verify()
