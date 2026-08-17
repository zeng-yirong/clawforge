import os
import json
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

results = []
total_score = 0
max_total = 100

def check(description, max_score, condition_func):
    global total_score
    try:
        passed = condition_func()
        score = max_score if passed else 0
        total_score += score
        results.append({
            "item": description,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": "通过" if passed else f"未满足条件"
        })
    except Exception as e:
        results.append({
            "item": description,
            "score": 0,
            "max_score": max_score,
            "passed": False,
            "reason": f"异常: {str(e)}"
        })

# ====== 1. 目录结构检查 ======
def dir_exists(rel):
    return os.path.isdir(os.path.join(workspace, rel))

check("ops/ 目录存在", 10, lambda: dir_exists("ops"))

# ====== 2. 目标文件存在 ======
nav_plan_path = os.path.join(workspace, "ops/nav_plan.json")
check("ops/nav_plan.json 文件存在", 10, lambda: os.path.isfile(nav_plan_path))

# ====== 3. JSON 合法性 ======
def load_nav():
    with open(nav_plan_path, "r", encoding="utf-8") as f:
        return json.load(f)

check("ops/nav_plan.json 是合法 JSON", 10, lambda: isinstance(load_nav(), dict))

# ====== 4. 字段结构检查 ======
def fields_ok():
    data = load_nav()
    return "waypoints" in data and isinstance(data["waypoints"], list)

check("包含 waypoints 字段且为列表", 10, lambda: fields_ok())

# ====== 5. waypoints 长度 ======
def length_ok():
    data = load_nav()
    return len(data["waypoints"]) == 2

check("waypoints 长度为 2", 10, lambda: length_ok())

# ====== 6. 第一个 waypoint ID ======
def first_poi_ok():
    data = load_nav()
    return data["waypoints"][0] == "poi_001"

check("第一个 waypoint 是 poi_001 (北京市中心充电站)", 20, lambda: first_poi_ok())

# ====== 7. 第二个 waypoint ID ======
def second_poi_ok():
    data = load_nav()
    return data["waypoints"][1] == "poi_003"

check("第二个 waypoint 是 poi_003 (北京市中心美食餐厅)", 20, lambda: second_poi_ok())

# ====== 8. 无多余字段 ======
def no_extra_keys():
    data = load_nav()
    allowed = {"waypoints"}
    return set(data.keys()) == allowed

check("nav_plan.json 中没有多余字段", 10, lambda: no_extra_keys())

# ====== 汇总 ======
final_score = min(total_score, max_total)
score_doc = {
    "total_score": final_score,
    "details": results
}
with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
    json.dump(score_doc, f, ensure_ascii=False, indent=2)

print(f"Verification complete. Score: {final_score}/{max_total}")
