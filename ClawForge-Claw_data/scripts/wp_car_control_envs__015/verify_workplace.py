import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops目录存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops目录存在" if dir_exists else "ops目录缺失"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 fan_setting.json 是否存在 (10分)
    target_file = os.path.join(ops_dir, "fan_setting.json")
    file_exists = os.path.isfile(target_file)
    details.append({
        "item": "fan_setting.json存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件缺失"
    })
    if file_exists:
        total_score += 10
    else:
        # 文件不存在则后续检查全部跳过
        write_result(total_score, details)
        return

    # 3. 检查 JSON 语法是否合法 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        json_valid = True
        reason = "JSON语法正确"
    except (json.JSONDecodeError, Exception) as e:
        json_valid = False
        reason = f"JSON解析失败: {str(e)}"
    details.append({
        "item": "JSON格式合法",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    if json_valid:
        total_score += 10
    else:
        write_result(total_score, details)
        return

    # 4. 检查 fan_speed 字段是否存在且为字符串 (10分)
    if isinstance(data, dict) and "fan_speed" in data:
        fan_speed = data["fan_speed"]
        if isinstance(fan_speed, str):
            field_ok = True
            reason = f"fan_speed字段存在且为字符串: '{fan_speed}'"
        else:
            field_ok = False
            reason = f"fan_speed字段存在但类型为 {type(fan_speed).__name__}，期望字符串"
    else:
        field_ok = False
        fan_speed = None
        reason = "缺少fan_speed字段或顶层不是字典"

    details.append({
        "item": "fan_speed字段合法",
        "score": 10 if field_ok else 0,
        "max_score": 10,
        "passed": field_ok,
        "reason": reason
    })
    if field_ok:
        total_score += 10
    else:
        write_result(total_score, details)
        return

    # 5. 核心值校验：fan_speed 必须等于 "high" (60分)
    expected = "high"
    value_correct = (fan_speed == expected)
    details.append({
        "item": "fan_speed值正确",
        "score": 60 if value_correct else 0,
        "max_score": 60,
        "passed": value_correct,
        "reason": f"fan_speed = '{fan_speed}' (期望 '{expected}')" if not value_correct else "值正确"
    })
    if value_correct:
        total_score += 60

    write_result(total_score, details)

def write_result(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"总分: {total_score}/100")

if __name__ == "__main__":
    main()
