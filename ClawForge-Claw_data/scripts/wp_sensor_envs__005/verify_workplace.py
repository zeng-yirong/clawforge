import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)
    details = []
    total_score = 0

    # 1. 检查必要的目录结构 (10分)
    dirs = ["data/sensors", "ops"]
    dir_score = 0
    for d in dirs:
        if os.path.isdir(d):
            dir_score += 5
        else:
            dir_score += 0
    details.append({
        "item": "必要的目录存在 (data/sensors, ops)",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": f"缺少目录: {[d for d in dirs if not os.path.isdir(d)]}" if dir_score < 10 else "所有目录存在"
    })
    total_score += dir_score

    # 2. 检查 ops/active_sensors.json 是否存在 (10分)
    score_file_exists = 0
    out_path = "ops/active_sensors.json"
    if os.path.isfile(out_path):
        score_file_exists = 10
        reason = "文件存在"
    else:
        reason = "文件不存在"
    details.append({
        "item": "输出文件 ops/active_sensors.json 存在",
        "score": score_file_exists,
        "max_score": 10,
        "passed": score_file_exists == 10,
        "reason": reason
    })
    total_score += score_file_exists

    # 3. 解析 JSON 是否合法 (10分)
    json_valid = False
    data = None
    if score_file_exists == 10:
        try:
            with open(out_path, "r") as f:
                data = json.load(f)
            json_valid = True
            reason = "JSON 格式正确"
        except Exception as e:
            reason = f"JSON 解析失败: {e}"
    else:
        reason = "文件不可用，跳过 JSON 检查"
    details.append({
        "item": "输出文件 JSON 合法性",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    total_score += (10 if json_valid else 0)

    # 4. 检查数据结构：是否为字典，且包含 'active_sensors' 键 (10分)
    struct_ok = False
    sensor_list = []
    if json_valid and isinstance(data, dict):
        if "active_sensors" in data:
            sensor_list = data["active_sensors"]
            struct_ok = True
            reason = "包含 active_sensors 键，类型为列表"
        else:
            reason = "缺少 active_sensors 键"
    elif json_valid:
        reason = "顶层不是字典"
    else:
        reason = "JSON 不可用"
    details.append({
        "item": "输出数据包含 active_sensors 字段且为列表",
        "score": 10 if struct_ok else 0,
        "max_score": 10,
        "passed": struct_ok,
        "reason": reason
    })
    total_score += (10 if struct_ok else 0)

    # 5. 检查 active_sensors 列表的值是否正确 (60分)
    # 正确答案：从正确数据源 sensors.json 中筛选 status == 'active' 的 sensor_id
    correct_active_ids = {"S-TEMP-001", "S-TEMP-003", "S-EN-001"}
    if struct_ok:
        actual_ids = set(sensor_list)
        # 检查是否有多余或缺失
        missing = correct_active_ids - actual_ids
        extra = actual_ids - correct_active_ids
        if not missing and not extra:
            score_content = 60
            reason = "完全匹配正确的活跃传感器ID"
        else:
            # 部分得分：每缺失/多出一个扣20分（最多扣到0）
            penalty = (len(missing) + len(extra)) * 20
            score_content = max(0, 60 - penalty)
            reason = f"缺失: {missing}, 多余: {extra}"
    else:
        score_content = 0
        reason = "数据结构不符合要求，无法比较内容"
    details.append({
        "item": "active_sensors 内容正确性",
        "score": score_content,
        "max_score": 60,
        "passed": score_content == 60,
        "reason": reason
    })
    total_score += score_content

    # 额外：检查是否包含了多余字段（比如 extra_ids 等） - 可以扣分，但为了简单，目前只按上述评分
    # 但为增加梯度，如果存在非 sensor_id 字符串，额外扣10分
    if struct_ok:
        all_str = all(isinstance(x, str) for x in sensor_list)
        if not all_str:
            items_penalty = 10
            total_score -= items_penalty
            details.append({
                "item": "列表中元素均为字符串",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"包含非字符串元素: {[x for x in sensor_list if not isinstance(x, str)]}"
            })
        else:
            details.append({
                "item": "列表中元素均为字符串",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "所有元素都是字符串"
            })

    # 最终总分控制在0-100
    total_score = max(0, min(100, total_score))

    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total_score}")

if __name__ == "__main__":
    main()
