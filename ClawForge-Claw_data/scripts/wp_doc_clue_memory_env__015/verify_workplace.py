import sys
import os
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. 目录结构检查 (总分10)
    ops_dir = os.path.join(workspace, "ops")
    clue_path = os.path.join(ops_dir, "clue_list.json")
    if os.path.isdir(ops_dir):
        results.append({"item": "ops/ 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops目录已创建"})
        total_score += 5
    else:
        results.append({"item": "ops/ 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops目录不存在"})

    if os.path.isfile(clue_path):
        results.append({"item": "ops/clue_list.json 文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件已创建"})
        total_score += 5
    else:
        results.append({"item": "ops/clue_list.json 文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续检查也无意义，直接写结果
        _write_score(results, total_score, workspace)
        return

    # 2. 文件格式合法性 (总分10)
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            results.append({"item": "JSON 格式合法且为数组", "score": 10, "max_score": 10, "passed": True, "reason": "正确解析为列表"})
            total_score += 10
        else:
            results.append({"item": "JSON 格式合法且为数组", "score": 0, "max_score": 10, "passed": False, "reason": f"顶层不是列表，而是{type(data).__name__}"})
            _write_score(results, total_score, workspace)
            return
    except (json.JSONDecodeError, IOError) as e:
        results.append({"item": "JSON 格式合法且为数组", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        _write_score(results, total_score, workspace)
        return

    # 3. 字段完整性 (总分20) 每个元素必须包含 source, id, title, summary
    field_ok = True
    for idx, item in enumerate(data):
        missing = []
        for field in ["source", "id", "title", "summary"]:
            if field not in item:
                missing.append(field)
        if missing:
            field_ok = False
            results.append({"item": f"元素 {idx} 字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {', '.join(missing)}"})
            break
    if field_ok:
        results.append({"item": "所有元素包含 source, id, title, summary 字段", "score": 20, "max_score": 20, "passed": True, "reason": "字段完整"})
        total_score += 20

    # 4. 内容正确性 (总分60)
    # 预期结果 (5个文档，顺序无关)
    expected = [
        {"source": "report",   "id": "RPT-001", "title": "Edge Inference in Manufacturing", "summary": "Explores deployment of HelioSync at factory floor for real-time defect detection."},
        {"source": "report",   "id": "RPT-002", "title": "Logistics AI Trends 2026", "summary": "Covers HelioSync for warehouse optimization and route planning."},
        {"source": "presentation", "id": "PRES-001", "title": "HelioSync Product Overview", "summary": "Slide deck introducing HelioSync features and target market."},
        {"source": "presentation", "id": "PRES-002", "title": "Partner Ecosystem Update", "summary": "Includes HelioSync integration case study with major logistics provider."},
        {"source": "media_sample", "id": "MS-001",   "title": "Podcast: Edge AI Revolution", "summary": "Interview with VP of Engineering on HelioSync rollout in smart factories."}
    ]

    # 将结果按 (source, id) 标准化为字典以便比较
    actual_map = {}
    for item in data:
        key = (item.get("source"), item.get("id"))
        if key in actual_map:
            results.append({"item": "内容正确性", "score": 0, "max_score": 60, "passed": False, "reason": f"存在重复条目: {key}"})
            _write_score(results, total_score, workspace)
            return
        actual_map[key] = item

    # 检查预期是否全部匹配
    matched = 0
    for exp in expected:
        key = (exp["source"], exp["id"])
        actual = actual_map.get(key)
        if not actual:
            continue
        # 比较 title 和 summary (忽略大小写和首尾空格)
        if actual.get("title","").strip().lower() == exp["title"].strip().lower() and \
           actual.get("summary","").strip().lower() == exp["summary"].strip().lower():
            matched += 1

    if matched == len(expected):
        results.append({"item": "内容正确性 (5个文档全部匹配)", "score": 60, "max_score": 60, "passed": True, "reason": "所有预期文档均正确出现"})
        total_score += 60
    else:
        results.append({"item": f"内容正确性", "score": int(60 * matched / len(expected)), "max_score": 60, "passed": False,
                        "reason": f"匹配 {matched}/{len(expected)} 个预期文档"})
        total_score += int(60 * matched / len(expected))

    _write_score(results, total_score, workspace)

def _write_score(details, total, workspace):
    output = {"total_score": total, "details": details}
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
