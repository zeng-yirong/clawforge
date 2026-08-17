import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def add_item(name, score, max_score, passed, reason):
    global total_score
    total_score += score
    score_details.append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# 1. 目录结构：检查 ops 和 logs 存在（10分）
dir_check_ok = True
if not os.path.isdir(os.path.join(workspace, "ops")):
    add_item("目录 ops 存在", 0, 10, False, "缺少 ops 目录")
    dir_check_ok = False
else:
    add_item("目录 ops 存在", 5, 10, True, "ops 目录存在")

if not os.path.isdir(os.path.join(workspace, "logs")):
    add_item("目录 logs 存在", 0, 10, False, "缺少 logs 目录")
    dir_check_ok = False
else:
    add_item("目录 logs 存在", 5, 10, True, "logs 目录存在")

# 2. 产物文件 ops/waypoints_order.json 存在（10分）
target_path = os.path.join(workspace, "ops", "waypoints_order.json")
if not os.path.isfile(target_path):
    add_item("产物文件 ops/waypoints_order.json 存在", 0, 10, False, "文件不存在")
    # 其余检查无法进行，直接写总分结束
    add_item("JSON 格式合法", 0, 10, False, "文件缺失")
    add_item("waypoints 数组正确", 0, 70, False, "文件缺失")
    total_score = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, ensure_ascii=False, indent=2)
    sys.exit(0)

add_item("产物文件存在", 10, 10, True, "文件存在")

# 3. JSON 语法合法性（10分）
try:
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        add_item("JSON 格式合法", 0, 10, False, "根对象不是 JSON 对象")
        json_ok = False
    else:
        add_item("JSON 格式合法", 10, 10, True, "语法正确且为对象")
        json_ok = True
except Exception as e:
    add_item("JSON 格式合法", 0, 10, False, f"解析失败: {str(e)}")
    json_ok = False

# 4. waypoints 字段验证（70分）
if json_ok:
    if "waypoints" not in data:
        add_item("waypoints 数组存在", 0, 70, False, "缺少 waypoints 键")
        wp_ok = False
    elif not isinstance(data["waypoints"], list):
        add_item("waypoints 为数组", 0, 70, False, "waypoints 不是列表")
        wp_ok = False
    else:
        wp_list = data["waypoints"]
        # 验证长度
        if len(wp_list) != 3:
            add_item("waypoints 元素数量为3", 0, 20, False, f"实际数量 {len(wp_list)}")
        else:
            add_item("waypoints 元素数量为3", 20, 20, True, "长度正确")
        # 验证顺序和ID
        expected = ["poi_001", "poi_002", "poi_003"]
        if wp_list == expected:
            add_item("waypoints 顺序和ID完全正确", 50, 50, True, "匹配预期")
        else:
            # 部分匹配给出梯度
            match_count = sum(1 for i in range(min(len(wp_list), 3)) if wp_list[i] == expected[i])
            if match_count == 2:
                add_item("waypoints 部分正确（2/3位置正确）", 30, 50, False, f"当前顺序 {wp_list}")
            elif match_count == 1:
                add_item("waypoints 部分正确（1/3位置正确）", 10, 50, False, f"当前顺序 {wp_list}")
            else:
                # 检查ID集合是否正确（即使顺序不对）
                if set(wp_list) == set(expected):
                    add_item("waypoints 集合正确但顺序错误", 20, 50, False, "ID 全对但顺序不符")
                else:
                    add_item("waypoints 内容错误", 0, 50, False, f"预期 {expected}，实际 {wp_list}")
else:
    add_item("waypoints 数组正确", 0, 70, False, "JSON 无效，无法验证")

# 总计
total_score = sum(d["score"] for d in score_details)
result = {
    "total_score": total_score,
    "details": score_details
}
output_path = os.path.join(workspace, "workplace_score.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
