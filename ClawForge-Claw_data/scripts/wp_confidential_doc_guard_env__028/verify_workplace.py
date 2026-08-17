import json
import os
import sys
import pathlib

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    max_detail = []

    # 1. 目录结构检查（10分）
    required_dirs = ['data/requests', 'data/assets', 'ops']
    dir_score = 0
    dir_max = 10
    for d in required_dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            dir_score += 3
        else:
            details.append({"item": f"目录 {d} 不存在", "score": 0, "max_score": 3, "passed": False, "reason": "缺失"})
            dir_score -= 1  # 漏一个扣分
    # ops 必须存在
    if os.path.isdir(os.path.join(workspace, 'ops')):
        dir_score = 10  # 全部存在给满分
    else:
        dir_score = 0
    details.append({"item": "目录结构完整性", "score": dir_score, "max_score": dir_max, "passed": dir_score == dir_max, "reason": "所有必需目录存在" if dir_score == dir_max else "缺少关键目录"})
    score += dir_score

    # 2. 产物文件 ops/deny_list.json 存在且格式合法（20分）
    file_path = os.path.join(workspace, "ops/deny_list.json")
    if not os.path.isfile(file_path):
        details.append({"item": "ops/deny_list.json 存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        # 即使文件不存在，后续检查跳过
        final_score = score
        # 写结果并返回
        _write_result(workspace, final_score, details)
        return

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败: {e}"})
        _write_result(workspace, score, details)
        return

    if not isinstance(data, list):
        details.append({"item": "JSON 内容是数组", "score": 0, "max_score": 10, "passed": False, "reason": "应为列表"})
        list_score = 0
    else:
        list_score = 10
        for item in data:
            if not isinstance(item, dict) or "request_id" not in item:
                list_score = 0
                break
        if list_score == 0:
            details.append({"item": "每个元素是包含 request_id 的对象", "score": 0, "max_score": 10, "passed": False, "reason": "格式错误"})
        else:
            details.append({"item": "列表元素格式正确", "score": list_score, "max_score": 10, "passed": True, "reason": "所有元素包含 request_id 键"})
    score += list_score
    if list_score < 10:
        # 格式不对，不继续
        _write_result(workspace, score, details)
        return

    # 提取所有 request_id
    ids = set(item["request_id"] for item in data)
    # 3. 必须包含 REQ-003 和 REQ-008（各30分，共60分）
    correct_ids = {"REQ-003", "REQ-008"}
    id_score = 0
    id_max = 60
    for cid in correct_ids:
        if cid in ids:
            id_score += 30
            details.append({"item": f"包含 {cid}", "score": 30, "max_score": 30, "passed": True, "reason": "正确包含"})
        else:
            details.append({"item": f"包含 {cid}", "score": 0, "max_score": 30, "passed": False, "reason": "缺失"})
    # 4. 不得出现多余 ID（10分）
    extra = ids - correct_ids
    extra_score = 10
    if extra:
        extra_score = 0
        details.append({"item": "无多余请求 ID", "score": 0, "max_score": 10, "passed": False, "reason": f"发现多余 ID: {extra}"})
    else:
        details.append({"item": "无多余请求 ID", "score": 10, "max_score": 10, "passed": True, "reason": "没有多余条目"})
    score += id_score + extra_score

    _write_result(workspace, score, details)

def _write_result(workspace, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == '__main__':
    verify()
