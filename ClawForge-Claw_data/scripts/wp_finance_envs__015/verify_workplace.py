import sys
import json
import os
import pathlib

def verify(workspace):
    score = 0
    max_score = 100
    details = []
    workspace_path = pathlib.Path(workspace)

    # 1. 检查 tech_brief.json 是否存在 (10分)
    brief_path = workspace_path / "tech_brief.json"
    if not brief_path.exists():
        details.append({
            "item": "tech_brief.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 如果文件都不存在，后续检查无意义，直接返回
        total = sum(d["score"] for d in details)
        return {"total_score": total, "details": details}
    else:
        details.append({
            "item": "tech_brief.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })

    # 2. 解析 JSON 合法性 (10分)
    try:
        with open(brief_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        total = sum(d["score"] for d in details)
        return {"total_score": total, "details": details}

    # 3. ticker 是否正确 (20分)
    if data.get("ticker") == "TECH":
        details.append({
            "item": "ticker 字段正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "ticker 为 TECH"
        })
    else:
        details.append({
            "item": "ticker 字段正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 TECH，实际得到 {data.get('ticker')}"
        })

    # 4. recommendation 是否为 "Buy" (20分)
    if data.get("recommendation") == "Buy":
        details.append({
            "item": "recommendation 字段为 Buy",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "推荐为 Buy"
        })
    else:
        details.append({
            "item": "recommendation 字段为 Buy",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 Buy，实际得到 {data.get('recommendation')}"
        })

    # 5. earnings_ids 检查 (20分)
    earnings_ids = data.get("earnings_ids", [])
    if not isinstance(earnings_ids, list):
        details.append({
            "item": "earnings_ids 类型正确且包含 e001",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "earnings_ids 不是列表"
        })
    elif len(earnings_ids) == 1 and earnings_ids[0] == "e001":
        details.append({
            "item": "earnings_ids 类型正确且包含 e001",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "仅包含 e001"
        })
    elif "e001" in earnings_ids and len(earnings_ids) > 1:
        details.append({
            "item": "earnings_ids 类型正确且包含 e001",
            "score": 10,
            "max_score": 20,
            "passed": False,
            "reason": f"包含 e001 但有多余 ID: {earnings_ids}"
        })
    else:
        details.append({
            "item": "earnings_ids 类型正确且包含 e001",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"未包含 e001，实际: {earnings_ids}"
        })

    # 6. news_ids 检查 (20分)
    news_ids = data.get("news_ids", [])
    if not isinstance(news_ids, list):
        details.append({
            "item": "news_ids 类型正确且包含 n001",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "news_ids 不是列表"
        })
    elif len(news_ids) == 1 and news_ids[0] == "n001":
        details.append({
            "item": "news_ids 类型正确且包含 n001",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "仅包含 n001"
        })
    elif "n001" in news_ids and len(news_ids) > 1:
        details.append({
            "item": "news_ids 类型正确且包含 n001",
            "score": 10,
            "max_score": 20,
            "passed": False,
            "reason": f"包含 n001 但有多余 ID: {news_ids}"
        })
    else:
        details.append({
            "item": "news_ids 类型正确且包含 n001",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"未包含 n001，实际: {news_ids}"
        })

    total_score = sum(d["score"] for d in details)
    return {
        "total_score": total_score,
        "details": details
    }

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
