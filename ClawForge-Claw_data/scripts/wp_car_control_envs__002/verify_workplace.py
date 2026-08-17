import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    fan_path = os.path.join(workspace, "ops", "fan_setting.json")

    # 1. 检查文件是否存在 (10分)
    if os.path.exists(fan_path):
        details.append({
            "item": "ops/fan_setting.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/fan_setting.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 后续检查无法进行，直接结束
        report(details, total_score, max_total)
        return

    # 2. 尝试解析 JSON (10分)
    try:
        with open(fan_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        report(details, total_score, max_total)
        return

    # 3. 检查 preset_id 字段 (10分)
    if "preset_id" in data:
        details.append({
            "item": "包含 preset_id 字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"字段存在，值为 {data['preset_id']}"
        })
        total_score += 10
    else:
        details.append({
            "item": "包含 preset_id 字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 preset_id 字段"
        })

    # 4. 检查 fan_speed 字段 (10分)
    if "fan_speed" in data:
        details.append({
            "item": "包含 fan_speed 字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"字段存在，值为 {data['fan_speed']}"
        })
        total_score += 10
    else:
        details.append({
            "item": "包含 fan_speed 字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 fan_speed 字段"
        })

    # 5. preset_id 值必须为 "defog_001" (30分)
    expected_preset = "defog_001"
    if data.get("preset_id") == expected_preset:
        details.append({
            "item": "preset_id 正确 (defog_001)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"值匹配 {expected_preset}"
        })
        total_score += 30
    else:
        details.append({
            "item": "preset_id 正确 (defog_001)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"实际值为 {data.get('preset_id')}，期望 {expected_preset}"
        })

    # 6. fan_speed 值必须为 "auto" (30分)
    expected_speed = "auto"
    if data.get("fan_speed") == expected_speed:
        details.append({
            "item": "fan_speed 正确 (auto)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"值匹配 {expected_speed}"
        })
        total_score += 30
    else:
        details.append({
            "item": "fan_speed 正确 (auto)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"实际值为 {data.get('fan_speed')}，期望 {expected_speed}"
        })

    report(details, total_score, max_total)

def report(details, total_score, max_total):
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(
        sys.argv[1] if len(sys.argv) > 1 else ".",
        "workplace_score.json"
    )
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"总分: {total_score}/{max_total}")
    for d in details:
        print(f"  {d['item']}: {'✅' if d['passed'] else '❌'} {d['score']}/{d['max_score']}")

if __name__ == "__main__":
    main()
