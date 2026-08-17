import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查文件是否存在
    target_file = os.path.join(workspace, "ops", "denied_requests.json")
    if not os.path.isfile(target_file):
        details.append({
            "item": "ops/denied_requests.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 后续检查无法进行，直接返回
        final_score = 0
        write_score(workspace, final_score, details)
        return final_score
    else:
        details.append({
            "item": "ops/denied_requests.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10

    # 2. 检查 JSON 合法性
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        final_score = total_score
        write_score(workspace, final_score, details)
        return final_score

    # 3. 检查类型是否为列表，且元素均为字符串
    if not isinstance(data, list):
        details.append({
            "item": "内容为列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望列表，实际 {type(data).__name__}"
        })
        total_score += 0
    else:
        if all(isinstance(item, str) for item in data):
            details.append({
                "item": "列表元素均为字符串",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"包含 {len(data)} 个字符串项"
            })
            total_score += 10
        else:
            details.append({
                "item": "列表元素均为字符串",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "存在非字符串元素"
            })

    # 4. 检查精确内容 (顺序无关)
    expected = {"req_002", "req_004"}
    actual = set(data)
    missing = expected - actual
    extra = actual - expected

    content_correct = True
    reasons = []
    if missing:
        content_correct = False
        reasons.append(f"缺少: {', '.join(sorted(missing))}")
    if extra:
        content_correct = False
        reasons.append(f"多余: {', '.join(sorted(extra))}")

    if content_correct:
        details.append({
            "item": "内容正确（仅包含 req_002, req_004）",
            "score": 70,
            "max_score": 70,
            "passed": True,
            "reason": "与预期完全一致"
        })
        total_score += 70
    else:
        # 弹性评分：缺少每个扣15，多余每个扣10，最多扣70
        penalty = 0
        penalty += len(missing) * 15
        penalty += len(extra) * 10
        gained = max(0, 70 - penalty)
        details.append({
            "item": "内容正确（仅包含 req_002, req_004）",
            "score": gained,
            "max_score": 70,
            "passed": False,
            "reason": "; ".join(reasons)
        })
        total_score += gained

    final_score = min(total_score, 100)
    write_score(workspace, final_score, details)
    return final_score

def write_score(workspace, score, details):
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w") as f:
        json.dump({
            "total_score": score,
            "details": details
        }, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
