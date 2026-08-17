import sys
import json
import csv
import os
import math

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # -------------------- 1. 目录结构检查（10分）--------------------
    # 期望存在的目录和文件
    required_structure = [
        "data",
        "data/ac_presets.json",
        "ops",
        "ops/modifications.csv",
        "ops/fan_target.json"   # Agent 应生成的产物
    ]
    structure_score = 0
    structure_max = 10
    for path in required_structure:
        full = os.path.join(workspace, path)
        if os.path.exists(full):
            structure_score += 1
        else:
            structure_score -= 0.5   # 缺失扣分，但不高
    structure_score = max(0, int(structure_score * 2))  # 转换到 0-10 分
    # 给分更合理：存在得满分，缺失酌情
    missing = [p for p in required_structure if not os.path.exists(os.path.join(workspace, p))]
    if len(missing) == 0:
        structure_score = 10
        details.append({"item": "目录结构完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有必需文件/目录都存在"})
    else:
        structure_score = max(0, 10 - len(missing)*5)
        details.append({"item": "目录结构完整性", "score": structure_score, "max_score": 10, "passed": False, "reason": f"缺失: {', '.join(missing)}"})
    total_score += structure_score

    # -------------------- 2. 数据文件合法性检查（10分）----------------
    legality_score = 0
    legality_max = 10
    # 检查 ac_presets.json
    try:
        with open(os.path.join(workspace, "data/ac_presets.json"), "r", encoding="utf-8") as f:
            presets = json.load(f)
            if isinstance(presets, list) and len(presets) == 6:
                legality_score += 5
            else:
                legality_score += 2
    except:
        legality_score += 0
    # 检查 modifications.csv
    try:
        with open(os.path.join(workspace, "ops/modifications.csv"), "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) >= 5:  # 表头+4条记录
                legality_score += 5
            else:
                legality_score += 2
    except:
        legality_score += 0
    details.append({"item": "输入数据文件合法性", "score": legality_score, "max_score": legality_max, "passed": legality_score >= 8, "reason": f"JSON解析{'成功' if legality_score>=5 else '失败'}, CSV解析{'成功' if legality_score%5==0 else '失败'}"})
    total_score += legality_score

    # -------------------- 3. 产物文件存在性（10分）--------------------
    fan_target_path = os.path.join(workspace, "ops/fan_target.json")
    if os.path.exists(fan_target_path):
        details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/fan_target.json 已生成"})
        total_score += 10
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/fan_target.json 未找到"})
        # 后续检查不再进行，返回当前分数
        return {"total_score": total_score, "details": details}

    # -------------------- 4. 产物内容解析与正确性（70分）----------------
    content_score = 0
    content_max = 70
    try:
        with open(fan_target_path, "r", encoding="utf-8") as f:
            target = json.load(f)
        # 检查字段
        if not isinstance(target, dict):
            raise ValueError("不是 JSON 对象")
        if "preset_id" not in target or "correct_fan_speed" not in target:
            raise ValueError("缺少必要字段")
        if target["preset_id"] != "sport":
            content_score += 10   # 部分分
            reason = f"预设ID错误，期望'sport'，实际'{target['preset_id']}'"
            passed = False
        else:
            content_score += 20
            reason = "预设ID正确"
            passed_part1 = True

        # 从 modifications.csv 中提取原始 fan_speed 值
        original_fan_speed = None
        with open(os.path.join(workspace, "ops/modifications.csv"), "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["preset_id"] == "sport" and row["affected_field"] == "fan_speed":
                    original_fan_speed = row["original_value"]
                    break
        if original_fan_speed is None:
            content_score += 0
            reason += "；无法从修改记录中找到运动模式的风扇速度原始值"
        else:
            if target["correct_fan_speed"] == original_fan_speed:
                content_score += 50
                reason += f"；正确风扇速度为 '{original_fan_speed}'"
                passed_final = True
            else:
                content_score += 10
                reason += f"；期望 '{original_fan_speed}'，实际 '{target['correct_fan_speed']}'"
                passed_final = False

        details.append({"item": "产物内容正确性", "score": content_score, "max_score": content_max, "passed": passed_final if 'passed_final' in locals() else False, "reason": reason})
    except Exception as e:
        details.append({"item": "产物内容正确性", "score": 0, "max_score": content_max, "passed": False, "reason": f"产物解析失败: {str(e)}"})
        content_score = 0

    total_score += content_score

    # 最终总分
    total_score = min(100, total_score)
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入 workplace_score.json
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result)
