import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    total_max = 100

    # 1. 检查 ops/affected_bookings.json 是否存在 (10分)
    filepath = os.path.join(workspace, "ops", "affected_bookings.json")
    if os.path.exists(filepath):
        details.append({"item": "文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        score += 10
    else:
        details.append({"item": "文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        _write_score(score, details)
        return

    # 2. 检查 JSON 格式合法且为数组 (10分)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({"item": "JSON格式合法且为数组", "score": 10, "max_score": 10, "passed": True, "reason": "合法JSON数组"})
            score += 10
        else:
            details.append({"item": "JSON格式合法且为数组", "score": 0, "max_score": 10, "passed": False, "reason": f"不是数组，而是{type(data).__name__}"})
            _write_score(score, details)
            return
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        _write_score(score, details)
        return

    # 3. 检查包含预期的酒店预订ID "HB-001" (30分)
    expected_hotel = "HB-001"
    if expected_hotel in data:
        details.append({"item": f"包含酒店预订ID {expected_hotel}", "score": 30, "max_score": 30, "passed": True, "reason": "找到预期ID"})
        score += 30
    else:
        details.append({"item": f"包含酒店预订ID {expected_hotel}", "score": 0, "max_score": 30, "passed": False, "reason": "未找到"})

    # 4. 检查包含预期的交通预订ID "TB-001" (30分)
    expected_transport = "TB-001"
    if expected_transport in data:
        details.append({"item": f"包含交通预订ID {expected_transport}", "score": 30, "max_score": 30, "passed": True, "reason": "找到预期ID"})
        score += 30
    else:
        details.append({"item": f"包含交通预订ID {expected_transport}", "score": 0, "max_score": 30, "passed": False, "reason": "未找到"})

    # 5. 检查数组长度，确保无多余或缺失 (20分)
    if len(data) == 2:
        details.append({"item": "数组长度正确，无多余或缺失", "score": 20, "max_score": 20, "passed": True, "reason": f"长度={len(data)}"})
        score += 20
    else:
        details.append({"item": "数组长度正确，无多余或缺失", "score": 0, "max_score": 20, "passed": False, "reason": f"期望长度2，实际{len(data)}"})

    score = min(score, 100)
    _write_score(score, details)

def _write_score(total, details):
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total}")

if __name__ == "__main__":
    main()
