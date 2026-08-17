import sys
import json
import os

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录 ops 存在（10分）
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到ops目录"})
        total_score += 10
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到ops目录"})

    # 2. 检查 blocked_exports.json 文件存在（10分）
    result_file = os.path.join(workspace, "ops", "blocked_exports.json")
    if os.path.isfile(result_file):
        details.append({"item": "blocked_exports.json存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "blocked_exports.json存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续无法继续，直接结束
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 检查 JSON 合法性（10分）
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. 检查是否为列表（10分）
    if isinstance(data, list):
        details.append({"item": "内容是列表", "score": 10, "max_score": 10, "passed": True, "reason": "类型正确"})
        total_score += 10
    else:
        details.append({"item": "内容是列表", "score": 0, "max_score": 10, "passed": False, "reason": f"类型为 {type(data).__name__}，期望列表"})

    # 5. 检查列表长度（10分）
    if len(data) == 3:
        details.append({"item": "列表长度正确", "score": 10, "max_score": 10, "passed": True, "reason": "长度为3"})
        total_score += 10
    else:
        details.append({"item": "列表长度正确", "score": 0, "max_score": 10, "passed": False, "reason": f"长度为{len(data)}，期望3"})

    # 6. 检查所有元素是否为字符串（10分）
    all_str = all(isinstance(x, str) for x in data)
    if all_str:
        details.append({"item": "元素均为字符串", "score": 10, "max_score": 10, "passed": True, "reason": "类型正确"})
        total_score += 10
    else:
        non_str = [i for i, x in enumerate(data) if not isinstance(x, str)]
        details.append({"item": "元素均为字符串", "score": 0, "max_score": 10, "passed": False, "reason": f"非字符串元素索引: {non_str}"})

    # 7. 核心内容比对（40分）
    expected = {"req_001", "req_002", "req_006"}
    actual = set(data)
    if actual == expected:
        details.append({"item": "越权请求ID完全正确", "score": 40, "max_score": 40, "passed": True, "reason": "所有越权ID均正确且无多余"})
        total_score += 40
    else:
        missing = expected - actual
        extra = actual - expected
        lost = 0
        if missing:
            lost += len(missing) * 10
        if extra:
            lost += len(extra) * 10
        score = max(0, 40 - lost)
        details.append({"item": "越权请求ID正确", "score": score, "max_score": 40, "passed": False, "reason": f"缺少: {missing}, 多余: {extra}"})
        total_score += score

    # 写入评分结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
