import sys
import json
import os
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 目录结构检查（10分）
    dirs_ok = True
    for req_dir in ["db_dumps", "ops"]:
        p = os.path.join(workspace, req_dir)
        if not os.path.isdir(p):
            details.append({"item": f"目录 {req_dir} 存在", "score": 0, "max_score": 5, "passed": False, "reason": f"缺失目录 {req_dir}"})
            dirs_ok = False
        else:
            details.append({"item": f"目录 {req_dir} 存在", "score": 5, "max_score": 5, "passed": True, "reason": ""})
            total_score += 5
    if not dirs_ok:
        # 如果目录缺失，后续检查可能失败，但仍继续
        pass

    # 2. 目标文件存在性（10分）
    target_path = os.path.join(workspace, "ops", "kill_target.json")
    if not os.path.isfile(target_path):
        details.append({"item": "目标文件 ops/kill_target.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        print(json.dumps({"total_score": total_score, "details": details}))
        # 写入分数并退出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return
    else:
        details.append({"item": "目标文件 ops/kill_target.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10

    # 3. 文件格式合法（JSON）且无多余字段（20分）
    file_ok = True
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        details.append({"item": "仅包含 transaction_id 字段", "score": 0, "max_score": 10, "passed": False, "reason": "无法检查字段"})
        print(json.dumps({"total_score": total_score, "details": details}))
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return
    if not isinstance(data, dict):
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "根元素不是字典"})
        total_score += 0
        file_ok = False
    else:
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10
        # 检查字段数量
        keys = set(data.keys())
        if keys == {"transaction_id"}:
            details.append({"item": "仅包含 transaction_id 字段", "score": 10, "max_score": 10, "passed": True, "reason": ""})
            total_score += 10
        else:
            details.append({"item": "仅包含 transaction_id 字段", "score": 0, "max_score": 10, "passed": False, "reason": f"额外字段: {keys - {'transaction_id'}}"})

    if not file_ok:
        print(json.dumps({"total_score": total_score, "details": details}))
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 4. 数值正确性（50分）—— 唯一正确答案为 "98765"
    if "transaction_id" not in data:
        details.append({"item": "transaction_id 字段值正确", "score": 0, "max_score": 50, "passed": False, "reason": "缺失 transaction_id 字段"})
    else:
        val = data["transaction_id"]
        if val == "98765":
            details.append({"item": "transaction_id 字段值正确", "score": 50, "max_score": 50, "passed": True, "reason": ""})
            total_score += 50
        else:
            details.append({"item": "transaction_id 字段值正确", "score": 0, "max_score": 50, "passed": False, "reason": f"期望 98765，实际得到 {val}"})

    # 5. 额外严谨性检查：确认 lock_info.txt 中确有事务98765为阻塞者（5分）
    lock_info_path = os.path.join(workspace, "db_dumps", "lock_info.txt")
    if os.path.isfile(lock_info_path):
        with open(lock_info_path, "r") as f:
            content = f.read()
        # 简单检查是否包含 Transaction: 98765 并且 Waits 非空
        if re.search(r"Held by Transaction:\s*98765", content):
            details.append({"item": "lock_info.txt 包含事务98765作为持有者", "score": 5, "max_score": 5, "passed": True, "reason": ""})
            total_score += 5
        else:
            details.append({"item": "lock_info.txt 包含事务98765作为持有者", "score": 0, "max_score": 5, "passed": False, "reason": "未在 lock_info.txt 中找到事务98765或格式不匹配"})
    else:
        details.append({"item": "lock_info.txt 存在（用于辅助验证）", "score": 0, "max_score": 5, "passed": False, "reason": "lock_info.txt 缺失"})

    # 6. 干扰项检查（5分）—— 验证 agent 没有误将其他事务写入（可选加分项，这里只做扣分，但满分100，所以作为 bonus 不合适，算了）
    # 为了保持满分100，我们计入上面 lock_info 检查的5分，但多加了5分导致总分可能超过100？我们已经在上面将分数分配为10+10+20+50+5=95，需要再加5分凑100。
    # 可以增加一个"结果数据类型正确"的5分项
    if isinstance(data.get("transaction_id"), str):
        details.append({"item": "transaction_id 为字符串类型", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        total_score += 5
    else:
        details.append({"item": "transaction_id 为字符串类型", "score": 0, "max_score": 5, "passed": False, "reason": "不是字符串"})

    # 写入结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f)
    print(json.dumps({"total_score": total_score, "details": details}))

if __name__ == "__main__":
    main()
