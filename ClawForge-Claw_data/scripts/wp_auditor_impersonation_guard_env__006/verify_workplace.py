import sys
import json
import os

def verify(workspace):
    score = 0
    details = []

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score += 10
        details.append({
            "item": "ops/ 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops 目录已创建"
        })
    else:
        details.append({
            "item": "ops/ 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops 目录不存在"
        })

    # 2. 检查 denied_requests.json 是否存在 (10分)
    target_file = os.path.join(workspace, "ops", "denied_requests.json")
    if os.path.isfile(target_file):
        score += 10
        details.append({
            "item": "ops/denied_requests.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
    else:
        details.append({
            "item": "ops/denied_requests.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到文件"
        })
        # 后续检查无法进行，直接返回
        return {"total_score": score, "details": details}

    # 3. JSON 格式合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            score += 10
            details.append({
                "item": "JSON 格式为合法数组",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "根元素是数组"
            })
        else:
            details.append({
                "item": "JSON 格式为合法数组",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"根元素类型为 {type(data).__name__}，期望 list"
            })
            return {"total_score": score, "details": details}
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        return {"total_score": score, "details": details}

    # 4. 数组长度恰为 1 (15分)
    if len(data) == 1:
        score += 15
        details.append({
            "item": "只拒绝了一个请求",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "数组长度为1"
        })
    else:
        details.append({
            "item": "只拒绝了一个请求",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"数组长度为 {len(data)}，期望1"
        })

    # 5. 元素包含 request_id 且值为 "req-002" (30分)
    entry = data[0]
    if isinstance(entry, dict) and "request_id" in entry and entry["request_id"] == "req-002":
        score += 30
        details.append({
            "item": "拒绝的请求 ID 正确 (req-002)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"request_id = {entry['request_id']}"
        })
    else:
        details.append({
            "item": "拒绝的请求 ID 正确 (req-002)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"缺少 request_id 或值错误: {entry.get('request_id', 'N/A')}"
        })

    # 6. 包含非空 reason 字段 (15分)
    if isinstance(entry, dict) and "reason" in entry and isinstance(entry["reason"], str) and len(entry["reason"].strip()) > 0:
        score += 15
        details.append({
            "item": "拒绝理由非空",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"reason = {entry['reason'][:50]}..."
        })
    else:
        details.append({
            "item": "拒绝理由非空",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "reason 字段缺失或为空"
        })

    # 7. 检查是否包含多余字段（可选扣分？这里不扣，但可加分） 额外检查：只应有request_id和reason
    allowed_keys = {"request_id", "reason"}
    if isinstance(entry, dict) and set(entry.keys()) == allowed_keys:
        base_addition = 10
    else:
        base_addition = 0
    score += base_addition
    details.append({
        "item": "不包含多余字段",
        "score": base_addition,
        "max_score": 10,
        "passed": (base_addition == 10),
        "reason": "多余字段会扣分" if base_addition == 0 else "仅含要求的字段"
    })

    # 总分 clamp 到 100
    score = min(score, 100)
    return {"total_score": score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
