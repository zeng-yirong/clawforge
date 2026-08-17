import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 检查 ops/summary.json 是否存在
    summary_path = os.path.join(workspace, "ops", "summary.json")
    exists = os.path.isfile(summary_path)
    if exists:
        results.append({
            "item": "ops/summary.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已创建"
        })
        total_score += 10
    else:
        results.append({
            "item": "ops/summary.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件缺失"
        })
        # 如果文件不存在，后续检查无法进行，直接输出结果
        _write_score(workspace, total_score, results)
        return

    # 检查 JSON 合法性
    try:
        with open(summary_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        results.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        _write_score(workspace, total_score, results)
        return

    results.append({
        "item": "JSON 格式合法",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "有效的 JSON"
    })
    total_score += 10

    # 检查键名
    if "summary" not in data or len(data.keys()) != 1:
        results.append({
            "item": "唯一键 'summary'",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"键不唯一或缺少 summary。实际键: {list(data.keys())}"
        })
    else:
        results.append({
            "item": "唯一键 'summary'",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "包含且仅包含 summary 键"
        })
        total_score += 20

    # 检查值内容（必须匹配 env_builder 中写入的 final_summary）
    expected_summary = "Alpha 发射计划定于2025年Q3，首先覆盖北美和欧洲市场，后续扩展至亚太区。"
    actual = data.get("summary", "")
    if actual == expected_summary:
        results.append({
            "item": "摘要内容正确",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": "摘要完全匹配最终批准版"
        })
        total_score += 60
    else:
        results.append({
            "item": "摘要内容正确",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": f"内容不匹配。期望: '{expected_summary}', 实际: '{actual}'"
        })

    _write_score(workspace, total_score, results)

def _write_score(workspace, total_score, details):
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False)
    print(f"Score written: {total_score}")

if __name__ == "__main__":
    main()
