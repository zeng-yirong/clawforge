import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        details.append({"item": "ops 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 目录已创建"})
        total_score += 10
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ 目录不存在"})

    # 2. 检查目标文件 acknowledged_alert.json 是否存在 (10分)
    target_file = os.path.join(ops_path, "acknowledged_alert.json")
    if os.path.isfile(target_file):
        details.append({"item": "acknowledged_alert.json 文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已生成"})
        total_score += 10
    else:
        details.append({"item": "acknowledged_alert.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未找到"})
        # 无法继续检查，直接输出结果
        output_result(total_score, details)
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(target_file, 'r') as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可正常解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        output_result(total_score, details)
        return

    # 4. 字段 alert_id 存在且值为 "alert-002" (70分)
    if isinstance(data, dict) and "alert_id" in data:
        if data["alert_id"] == "alert-002":
            details.append({"item": "alert_id 字段正确", "score": 70, "max_score": 70, "passed": True, "reason": "告警ID匹配预期值 alert-002"})
            total_score += 70
        else:
            details.append({"item": "alert_id 字段正确", "score": 0, "max_score": 70, "passed": False, "reason": f"alert_id 值为 {data['alert_id']}，应为 alert-002"})
    else:
        details.append({"item": "alert_id 字段正确", "score": 0, "max_score": 70, "passed": False, "reason": "JSON 对象中缺少 alert_id 字段"})

    # 输出结果
    output_result(total_score, details)

def output_result(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {total_score}/100")

if __name__ == "__main__":
    main()
