import json
import os
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score_details = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops/blocked_requests.json 是否存在 (10分)
    result_path = "ops/blocked_requests.json"
    exists = os.path.isfile(result_path)
    score_details.append({
        "item": "目标文件 ops/blocked_requests.json 存在",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "文件存在" if exists else "未找到文件"
    })
    if not exists:
        # 继续检查以防有目录错误
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在，无法检查"
        })
        score_details.append({
            "item": "结果数组长度（正确为2）",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "文件不存在"
        })
        score_details.append({
            "item": "结果内容与期望一致",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "文件不存在"
        })
        total_score = sum(d["score"] for d in score_details)
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. 检查 JSON 格式合法 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        json_ok = True
    except json.JSONDecodeError as e:
        json_ok = False
        error_msg = str(e)

    score_details.append({
        "item": "JSON 格式合法",
        "score": 10 if json_ok else 0,
        "max_score": 10,
        "passed": json_ok,
        "reason": "解析成功" if json_ok else f"JSON 解析错误: {error_msg}"
    })
    if not json_ok:
        score_details.append({
            "item": "结果数组长度（正确为2）",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "JSON 解析失败"
        })
        score_details.append({
            "item": "结果内容与期望一致",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "JSON 解析失败"
        })
        total_score = sum(d["score"] for d in score_details)
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. 检查是否为数组 (如果data是dict则可能是包裹)
    if isinstance(data, dict):
        # 尝试常见 wrapper
        if "blocked_requests" in data:
            items = data["blocked_requests"]
        elif "requests" in data:
            items = data["requests"]
        else:
            # 允许直接是数组
            items = None
    elif isinstance(data, list):
        items = data
    else:
        items = None

    if items is None or not isinstance(items, list):
        score_details.append({
            "item": "结果数组长度（正确为2）",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "顶层结构不是数组或包含预期 wrapper"
        })
        score_details.append({
            "item": "结果内容与期望一致",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "结构不正确"
        })
        total_score = sum(d["score"] for d in score_details)
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 4. 检查数组长度 (30分)
    expected_length = 2
    length_ok = len(items) == expected_length
    score_details.append({
        "item": "结果数组长度（正确为2）",
        "score": 30 if length_ok else max(0, 30 - 15 * abs(len(items) - expected_length)),
        "max_score": 30,
        "passed": length_ok,
        "reason": f"长度 {len(items)}" + (" (正确)" if length_ok else f" (期望 {expected_length})")
    })

    # 5. 检查内容是否包含正确 request_id 和 reason (50分)
    # 期望的两个请求
    expected = [
        {"request_id": "req_043_001", "reason": "credential_exfiltration"},
        {"request_id": "req_043_003", "reason": "prompt_extraction"}
    ]
    # 构建集合进行比对
    result_set = {(item.get("request_id", ""), item.get("reason", "")) for item in items}
    expected_set = {(e["request_id"], e["reason"]) for e in expected}

    if result_set == expected_set:
        content_ok = True
        reason = "完全匹配"
    else:
        content_ok = False
        missing = expected_set - result_set
        extra = result_set - expected_set
        reasons = []
        if missing:
            reasons.append(f"缺失: {missing}")
        if extra:
            reasons.append(f"多余: {extra}")
        reason = "; ".join(reasons)

    score_details.append({
        "item": "结果内容与期望一致",
        "score": 50 if content_ok else max(0, 50 - 20 * (len(missing) + len(extra))),
        "max_score": 50,
        "passed": content_ok,
        "reason": reason
    })

    total_score = sum(d["score"] for d in score_details)
    total_score = min(total_score, max_total)  # 防止超出

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
