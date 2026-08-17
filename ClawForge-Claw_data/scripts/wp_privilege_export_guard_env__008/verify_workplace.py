import sys
import os
import json
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base = Path(workspace).resolve()
    score = 0
    details = []

    # 1) 检查目录结构 (10分) —— ops目录存在
    ops_dir = base / "ops"
    dir_exists = ops_dir.is_dir()
    details.append({
        "item": "ops 目录存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops 目录存在" if dir_exists else "ops 目录不存在"
    })
    if dir_exists:
        score += 10

    # 2) 检查 deny_list.json 是否存在且合法 (10分)
    deny_path = ops_dir / "deny_list.json"
    file_exists = deny_path.is_file()
    details.append({
        "item": "deny_list.json 文件存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })
    if file_exists:
        score += 10
    else:
        # 剩余项目直接0分
        details.append({"item": "deny_list.json 内容合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "拒绝列表包含正确越权请求", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})
        details.append({"item": "无多余越权请求", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        details.append({"item": "无遗漏越权请求", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        write_score(base, score, details)
        return

    # 尝试解析JSON
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "deny_list.json 内容合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        details.append({"item": "拒绝列表包含正确越权请求", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 无效"})
        details.append({"item": "无多余越权请求", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 无效"})
        details.append({"item": "无遗漏越权请求", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 无效"})
        write_score(base, score, details)
        return

    # 数据必须是一个列表（或至少包含一个列表）
    if isinstance(data, dict):
        # 尝试常见键名
        if "request_ids" in data:
            deny_list = data["request_ids"]
        elif "ids" in data:
            deny_list = data["ids"]
        elif "requests" in data:
            deny_list = data["requests"]
        else:
            # 取第一个列表值
            for v in data.values():
                if isinstance(v, list):
                    deny_list = v
                    break
            else:
                deny_list = []
    elif isinstance(data, list):
        deny_list = data
    else:
        deny_list = []

    if not isinstance(deny_list, list):
        deny_list = []

    # 3) 合法JSON (10分)
    details.append({
        "item": "deny_list.json 内容合法",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "合法 JSON，且包含列表"
    })
    score += 10

    # 应该被拒绝的请求ID: req_001 (arch, bulk, pending, 权限不足)
    expected = {"req_001"}
    # 不应被拒绝的: req_002, req_005 (customer bulk pending, 权限内)
    allowed = {"req_002", "req_005"}

    detected_set = set(deny_list)
    expected_found = expected.intersection(detected_set)
    unexpected = detected_set - expected - allowed
    missing = expected - detected_set

    # 4) 包含正确越权请求 (30分) - req_001必须在列表中
    if "req_001" in detected_set:
        score += 30
        details.append({
            "item": "包含 req_001 (架构批量导出越权)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "req_001 在列表中"
        })
    else:
        details.append({
            "item": "包含 req_001 (架构批量导出越权)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "req_001 缺失"
        })

    # 5) 无多余越权请求 (20分) - 不允许出现非expected且非allowed的
    if unexpected:
        details.append({
            "item": "无多余越权请求",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"多余请求: {unexpected}"
        })
    else:
        score += 20
        details.append({
            "item": "无多余越权请求",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "没有多余请求"
        })

    # 6) 无遗漏越权请求 (20分) - 必须包含所有expected
    if missing:
        details.append({
            "item": "无遗漏越权请求",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"遗漏请求: {missing}"
        })
    else:
        score += 20
        details.append({
            "item": "无遗漏越权请求",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "所有越权请求都已包含"
        })

    # 最终总分
    total = min(score, 100)
    write_score(base, total, details)

def write_score(base, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open(base / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/100")
    sys.exit(0 if total == 100 else 1)

if __name__ == "__main__":
    main()
