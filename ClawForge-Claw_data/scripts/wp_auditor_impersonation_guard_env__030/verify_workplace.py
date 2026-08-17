import os
import json
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores = []
    max_total = 100

    # 1. 目录结构检查 (10分)
    dirs_ok = True
    required_dirs = ["ops"]
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_ok = False
            break
    scores.append({
        "item": "目录结构 (ops/) 存在",
        "score": 10 if dirs_ok else 0,
        "max_score": 10,
        "passed": dirs_ok,
        "reason": "ops 目录存在" if dirs_ok else "缺少 ops 目录"
    })

    # 2. 目标文件存在性 (10分)
    deny_path = os.path.join(workspace, "ops", "deny_list.json")
    file_exists = os.path.isfile(deny_path)
    scores.append({
        "item": "ops/deny_list.json 文件存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })

    # 如果文件不存在，后续项得0分
    if not file_exists:
        for _ in range(4):  # 剩余4项(格式10+内容70共80分)直接0分
            scores.append({"item": "后续检查依赖文件", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
        total = sum(s["score"] for s in scores)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": scores}, f, indent=2)
        return

    # 3. JSON 格式合法性 (10分)
    try:
        with open(deny_path, "r") as f:
            content = json.load(f)
        is_valid = isinstance(content, list) and all(isinstance(item, str) for item in content)
        scores.append({
            "item": "JSON 格式合法且为字符串数组",
            "score": 10 if is_valid else 0,
            "max_score": 10,
            "passed": is_valid,
            "reason": "格式正确" if is_valid else "不是字符串数组或JSON解析失败"
        })
    except Exception as e:
        scores.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析异常: {str(e)}"
        })
        # 无法继续
        for _ in range(3):
            scores.append({"item": "后续检查依赖有效JSON", "score": 0, "max_score": 23.33, "passed": False, "reason": "JSON无效"})
        total = sum(s["score"] for s in scores)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": scores}, f, indent=2)
        return

    # 4. 内容正确性 (70分)
    # 预期答案：冒充且目标为受限资产：req_001 (Alice冒充), req_003 (Charlie不存在)
    expected = {"req_001", "req_003"}
    actual = set(content)

    # 严格匹配
    if actual == expected:
        content_score = 70
        reason = "精确匹配预期拒绝列表"
    else:
        # 计算交集占比评分：每个正确ID 35分，多余ID每个扣10分（最多扣到0）
        correct_count = len(actual & expected)
        extra_count = len(actual - expected)
        missing_count = len(expected - actual)
        base = correct_count * 35
        penalty = min(extra_count * 10, base)  # 不扣成负数
        content_score = max(0, base - penalty)
        reason = f"正确{correct_count}个，多余{extra_count}个，缺失{missing_count}个 -> 得分{content_score}"

    scores.append({
        "item": "请求ID列表正确性",
        "score": content_score,
        "max_score": 70,
        "passed": content_score == 70,
        "reason": reason
    })

    # 总分
    total_score = sum(s["score"] for s in scores)
    result = {
        "total_score": total_score,
        "details": scores
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
