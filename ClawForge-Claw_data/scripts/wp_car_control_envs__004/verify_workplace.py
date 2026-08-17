import sys
import json
import os

def write_score(total, details):
    output = {"total_score": total, "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    score = 0

    # 读取源数据中的运动预设
    presets_path = os.path.join(workspace, "data/ac_presets.json")
    target_preset = None
    try:
        with open(presets_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for p in data.get("presets", []):
            if p.get("name") == "运动" and p.get("fan_speed") == "high":
                target_preset = p
                break
    except Exception:
        pass

    # 1. ops目录存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录存在"})
        score += 5
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "目录不存在"})

    # 2. 报告文件存在 (10分)
    report_path = os.path.join(workspace, "ops/fan_fix_report.json")
    if os.path.isfile(report_path):
        details.append({"item": "报告文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        score += 10
    else:
        details.append({"item": "报告文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        write_score(score, details)
        return

    # 3. JSON合法性 (15分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        details.append({"item": "JSON格式合法", "score": 15, "max_score": 15, "passed": True, "reason": "解析成功"})
        score += 15
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 15, "passed": False, "reason": f"解析失败: {e}"})
        write_score(score, details)
        return

    # 4. 必需字段完整 (15分)
    required = {"preset_id", "current_fan_speed", "expected_fan_speed"}
    keys = set(report.keys())
    missing = required - keys
    if not missing:
        details.append({"item": "必需字段完整", "score": 15, "max_score": 15, "passed": True, "reason": "所有必需字段存在"})
        score += 15
    else:
        details.append({"item": "必需字段完整", "score": 0, "max_score": 15, "passed": False, "reason": f"缺少字段: {missing}"})

    # 5. 无多余字段 (5分)
    extras = keys - required
    if not extras:
        details.append({"item": "无多余字段", "score": 5, "max_score": 5, "passed": True, "reason": "没有多余字段"})
        score += 5
    else:
        details.append({"item": "无多余字段", "score": 0, "max_score": 5, "passed": False, "reason": f"发现多余字段: {extras}"})

    # 6. preset_id 正确 (20分)
    p_id_ok = False
    if "preset_id" in report and target_preset is not None:
        p_id_ok = report["preset_id"] == target_preset["preset_id"]
    if p_id_ok:
        details.append({"item": "preset_id正确", "score": 20, "max_score": 20, "passed": True, "reason": f"ID={report['preset_id']}"})
        score += 20
    else:
        expected_id = target_preset["preset_id"] if target_preset else "未知"
        details.append({"item": "preset_id正确", "score": 0, "max_score": 20, "passed": False, "reason": f"期望{expected_id}, 实际{report.get('preset_id', '缺失')}"})

    # 7. current_fan_speed 正确 (15分)
    cfs_ok = "current_fan_speed" in report and report["current_fan_speed"] == "high"
    if cfs_ok:
        details.append({"item": "current_fan_speed正确", "score": 15, "max_score": 15, "passed": True, "reason": "值为high"})
        score += 15
    else:
        details.append({"item": "current_fan_speed正确", "score": 0, "max_score": 15, "passed": False, "reason": f"期望high, 实际{report.get('current_fan_speed', '缺失')}"})

    # 8. expected_fan_speed 正确 (10分)
    efs_ok = "expected_fan_speed" in report and report["expected_fan_speed"] == "auto"
    if efs_ok:
        details.append({"item": "expected_fan_speed正确", "score": 10, "max_score": 10, "passed": True, "reason": "值为auto"})
        score += 10
    else:
        details.append({"item": "expected_fan_speed正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望auto, 实际{report.get('expected_fan_speed', '缺失')}"})

    # 最后写入总分
    write_score(score, details)

if __name__ == "__main__":
    main()
