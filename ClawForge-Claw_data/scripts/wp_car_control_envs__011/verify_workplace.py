import sys
import json
import os
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops directory exists"
        })
        total_score += 5
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops directory not found"
        })

    # 2. 检查 fan_avg.json 文件是否存在 (10分)
    result_file = os.path.join(ops_dir, "fan_avg.json") if os.path.isdir(ops_dir) else os.path.join(workspace, "fan_avg.json")
    if os.path.isfile(result_file):
        details.append({
            "item": "fan_avg.json file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "file exists at expected path"
        })
        total_score += 10
    else:
        details.append({
            "item": "fan_avg.json file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file not found"
        })

    # 3. 文件内容合法性检查 (10分)
    content_ok = False
    if os.path.isfile(result_file):
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "average" in data:
                content_ok = True
            else:
                details.append({
                    "item": "JSON content has 'average' field",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "JSON is valid but missing 'average' key or structure incorrect"
                })
            if content_ok:
                details.append({
                    "item": "JSON is valid and contains 'average'",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "valid JSON with required field"
                })
                total_score += 10
            else:
                # 如果JSON解析失败，已在前面catch处理
                pass
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            details.append({
                "item": "JSON is valid and contains 'average'",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"invalid JSON: {str(e)}"
            })
    else:
        details.append({
            "item": "JSON is valid and contains 'average'",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file missing, skip content check"
        })

    # 4. 核心数值验证 (75分)
    if os.path.isfile(result_file) and content_ok:
        with open(result_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        avg_val = data["average"]
        # 预期平均值：从日志中有效速度列表 [1,2,3,4,5,2,3,4,5,1] 平均3.0 四舍五入3
        expected_avg = 3
        if isinstance(avg_val, int) and avg_val == expected_avg:
            details.append({
                "item": "average value correct",
                "score": 75,
                "max_score": 75,
                "passed": True,
                "reason": f"average is {avg_val}, matches expected {expected_avg}"
            })
            total_score += 75
        else:
            details.append({
                "item": "average value correct",
                "score": 0,
                "max_score": 75,
                "passed": False,
                "reason": f"average is {avg_val} (type: {type(avg_val).__name__}), expected {expected_avg}"
            })
    else:
        details.append({
            "item": "average value correct",
            "score": 0,
            "max_score": 75,
            "passed": False,
            "reason": "file not available or content not valid, cannot verify value"
        })

    # 汇总
    total_score = min(total_score, 100)  # 保险
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Score: {total_score}/100 written to {score_path}")
    return total_score

if __name__ == "__main__":
    verify()
