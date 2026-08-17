import sys
import os
import json
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace)
    score = 0
    details = []

    # 1. 目录结构检查 (10分)
    dirs = ["data/emails", "data/attachments", "data/social", "ops"]
    missing_dirs = [d for d in dirs if not (ws / d).is_dir()]
    if missing_dirs:
        details.append({"item": "required directories exist", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing directories: {missing_dirs}"})
    else:
        details.append({"item": "required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories present"})
        score += 10

    # 2. 结果文件存在性 (10分)
    result_file = ws / "ops" / "pre_launch_posts.json"
    if not result_file.is_file():
        details.append({"item": "result file ops/pre_launch_posts.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 不能继续检查内容，直接输出结果
        final_score = sum(d["score"] for d in details)
        result = {"total_score": final_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    details.append({"item": "result file ops/pre_launch_posts.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists"})
    score += 10

    # 3. 文件格式合法性 (10分)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            details.append({"item": "result file contains a JSON array", "score": 0, "max_score": 10, "passed": False, "reason": "Top-level value is not a list"})
        else:
            details.append({"item": "result file contains a JSON array", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON array"})
            score += 10
    except json.JSONDecodeError as e:
        details.append({"item": "result file valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON decode error: {e}"})
        # 停止后续检查
        final_score = sum(d["score"] for d in details)
        result = {"total_score": final_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 内容准确性 (60分)
    expected = ["post_001_aurora_x1_preview", "post_002_aurora_x1_teaser"]
    actual = data
    # 去重？允许重复吗？不允许重复，但可标记
    if len(actual) != len(expected):
        details.append({"item": "correct number of posts", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {len(expected)} posts, got {len(actual)}"})
    else:
        details.append({"item": "correct number of posts", "score": 15, "max_score": 15, "passed": True, "reason": "Count matches"})
        score += 15

    # 检查精确集合
    set_actual = set(actual)
    set_expected = set(expected)
    if set_actual == set_expected:
        details.append({"item": "exact post ID set", "score": 45, "max_score": 45, "passed": True, "reason": "All correct posts present, no extras or missing"})
        score += 45
    else:
        missing = set_expected - set_actual
        extra = set_actual - set_expected
        reason_parts = []
        if missing:
            reason_parts.append(f"Missing: {missing}")
        if extra:
            reason_parts.append(f"Extra: {extra}")
        details.append({"item": "exact post ID set", "score": 0, "max_score": 45, "passed": False, "reason": "; ".join(reason_parts)})

    # 5. 额外检查：没有多余字段 (10分)
    # 如果data是列表且每个元素是字符串，通过
    all_strings = all(isinstance(p, str) for p in actual)
    if not all_strings:
        details.append({"item": "all elements are strings", "score": 0, "max_score": 10, "passed": False, "reason": "Some elements are not strings"})
    else:
        details.append({"item": "all elements are strings", "score": 10, "max_score": 10, "passed": True, "reason": "All elements are string post IDs"})
        score += 10

    final_score = score
    result = {"total_score": final_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
