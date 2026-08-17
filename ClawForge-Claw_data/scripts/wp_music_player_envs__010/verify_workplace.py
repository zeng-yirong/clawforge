import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 期望答案
    expected = {
        "song_001": "觉醒",
        "song_005": "追梦赤子心",
        "song_007": "海阔天空",
        "song_009": "逆战"
    }

    # 1. ops目录存在 (10)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        results.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录已创建"})
        total_score += 10
    else:
        results.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录不存在"})
        # 后续检查无法进行，直接输出
        write_score(results, total_score)
        return

    # 2. 文件存在且合法JSON (10)
    target_path = os.path.join(workspace, "ops", "playlist_analysis.json")
    if not os.path.isfile(target_path):
        results.append({"item": "playlist_analysis.json存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        write_score(results, total_score)
        return
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        results.append({"item": "playlist_analysis.json合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        total_score += 10
    except json.JSONDecodeError:
        results.append({"item": "playlist_analysis.json合法", "score": 0, "max_score": 10, "passed": False, "reason": "无效JSON格式"})
        write_score(results, total_score)
        return

    # 3. 数据必须是列表 (10)
    if not isinstance(data, list):
        results.append({"item": "数据格式为列表", "score": 0, "max_score": 10, "passed": False, "reason": f"期望列表，但得到 {type(data)}"})
        write_score(results, total_score)
        return
    results.append({"item": "数据格式为列表", "score": 10, "max_score": 10, "passed": True, "reason": "数据为列表"})
    total_score += 10

    # 4. 列表长度正确 (20)
    if len(data) == len(expected):
        results.append({"item": "列表长度", "score": 20, "max_score": 20, "passed": True, "reason": f"长度正确，共{len(expected)}条"})
        total_score += 20
    else:
        results.append({"item": "列表长度", "score": 0, "max_score": 20, "passed": False, "reason": f"期望{len(expected)}条，实际{len(data)}条"})
        # 继续检查但会扣分

    # 5. 每个元素结构 (20) - 必须包含song_id和title，且不能有多余字段
    passed_structure = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            results.append({"item": f"元素{i}是字典", "score": 0, "max_score": 20, "passed": False, "reason": f"第{i}个元素不是字典"})
            passed_structure = False
            break
        if "song_id" not in item or "title" not in item:
            results.append({"item": f"元素{i}包含song_id和title", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失必要字段"})
            passed_structure = False
            break
        # 检查多余字段（允许但扣分，此处只检查无多余字段）
        allowed = {"song_id", "title"}
        extra = set(item.keys()) - allowed
        if extra:
            results.append({"item": f"元素{i}无多余字段", "score": 0, "max_score": 20, "passed": False, "reason": f"包含额外字段{extra}"})
            passed_structure = False
            break
    if passed_structure:
        results.append({"item": "每个元素结构正确", "score": 20, "max_score": 20, "passed": True, "reason": "所有元素包含song_id和title，且无多余字段"})
        total_score += 20

    # 6. 内容匹配 (20) - song_id和title必须完全匹配期望
    actual_map = {item["song_id"]: item["title"] for item in data}
    if actual_map == expected:
        results.append({"item": "内容完全匹配", "score": 20, "max_score": 20, "passed": True, "reason": "song_id和title与期望一致"})
        total_score += 20
    else:
        # 部分匹配扣分
        correct_ids = [sid for sid in expected if sid in actual_map and actual_map[sid] == expected[sid]]
        missing_ids = [sid for sid in expected if sid not in actual_map]
        wrong_title = [sid for sid in expected if sid in actual_map and actual_map[sid] != expected[sid]]
        extra_ids = [sid for sid in actual_map if sid not in expected]
        reasons = []
        if missing_ids:
            reasons.append(f"缺少{missing_ids}")
        if wrong_title:
            reasons.append(f"歌名错误{wrong_title}")
        if extra_ids:
            reasons.append(f"多余ID{extra_ids}")
        # 按比例给分：每正确一个5分，最多20
        correct_count = len(correct_ids)
        partial_score = min(correct_count * 5, 20)
        results.append({"item": "内容匹配", "score": partial_score, "max_score": 20, "passed": partial_score >= 20, "reason": "; ".join(reasons) if reasons else "部分匹配"})
        total_score += partial_score

    # 确保总分不超过100
    final_score = min(total_score, 100)
    write_score(results, final_score)

def write_score(results, total):
    output = {"total_score": total, "details": results}
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
