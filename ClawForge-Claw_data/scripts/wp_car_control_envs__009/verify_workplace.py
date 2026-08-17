import sys
import json
import os
import csv
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 report 目录是否存在 (10分)
    report_dir = os.path.join(workspace, "report")
    if os.path.isdir(report_dir):
        details.append({"item": "report目录存在", "score": 10, "max_score": 10, "passed": True,
                        "reason": "report目录已创建"})
        total_score += 10
    else:
        details.append({"item": "report目录存在", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"report目录不存在 ({report_dir})"})

    # 2. 检查 fan_avg.json 文件是否存在 (10分)
    result_path = os.path.join(report_dir, "fan_avg.json")
    if os.path.isfile(result_path):
        details.append({"item": "fan_avg.json文件存在", "score": 10, "max_score": 10, "passed": True,
                        "reason": "文件已生成"})
        total_score += 10
    else:
        details.append({"item": "fan_avg.json文件存在", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"文件不存在 ({result_path})"})
        # 后续检查不再执行，但为了结构完整性，写入剩余项为0分
        for item in ["JSON格式合法", "avg字段存在", "数值类型正确", "数值等于4"]:
            details.append({"item": item, "score": 0, "max_score": 15, "passed": False,
                            "reason": "前置检查失败"})
        write_score(details, total_score)
        return

    # 3. 解析 JSON 是否合法 (15分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 15, "max_score": 15, "passed": True,
                        "reason": "文件可解析为JSON"})
        total_score += 15
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 15, "passed": False,
                        "reason": f"JSON解析失败: {e}"})
        write_score(details, total_score)
        return

    # 4. 检查 avg 键是否存在 (15分)
    if isinstance(data, dict) and "avg" in data:
        details.append({"item": "avg字段存在", "score": 15, "max_score": 15, "passed": True,
                        "reason": "包含avg键"})
        total_score += 15
    else:
        details.append({"item": "avg字段存在", "score": 0, "max_score": 15, "passed": False,
                        "reason": f"缺少avg键，当前键: {list(data.keys()) if isinstance(data, dict) else '非字典'}"})
        write_score(details, total_score)
        return

    # 5. avg 字段类型是否数字 (10分)
    val = data["avg"]
    if isinstance(val, (int, float)):
        details.append({"item": "avg字段为数字类型", "score": 10, "max_score": 10, "passed": True,
                        "reason": f"值为 {val}"})
        total_score += 10
    else:
        details.append({"item": "avg字段为数字类型", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"类型错误: {type(val).__name__}，值: {val}"})
        write_score(details, total_score)
        return

    # 6. 数值等于 4 (四舍五入取整后应为4) (40分)
    expected = 4
    if math.isclose(val, expected, abs_tol=1e-9):
        details.append({"item": "数值等于4", "score": 40, "max_score": 40, "passed": True,
                        "reason": f"平均值取整正确: {val}"})
        total_score += 40
    else:
        details.append({"item": "数值等于4", "score": 0, "max_score": 40, "passed": False,
                        "reason": f"期望 {expected}，实际 {val}"})

    # 最终汇总
    write_score(details, total_score)

def write_score(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"评分完成: total={total_score}")

if __name__ == "__main__":
    main()
