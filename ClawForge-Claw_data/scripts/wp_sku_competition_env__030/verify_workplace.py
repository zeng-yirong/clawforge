import sys
import os
import json

def verify(workspace: str):
    details = []
    max_total = 100

    # 1. 检查 ops 目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        details.append({
            "item": "ops 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ 目录已创建"
        })
    else:
        details.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ 目录不存在"
        })

    # 2. ops/brand_summary.json 文件存在且合法 JSON (10分)
    result_file = os.path.join(ops_path, "brand_summary.json")
    if os.path.isfile(result_file):
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            details.append({
                "item": "brand_summary.json 存在且合法 JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "文件可解析为 JSON"
            })
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "brand_summary.json 存在且合法 JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON 解析失败: {str(e)}"
            })
    else:
        details.append({
            "item": "brand_summary.json 存在且合法 JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 如果文件不存在，后续检查无法进行，直接跳转
        total = sum(d["score"] for d in details)
        write_score(workspace, total, details)
        return total

    # 3. 字段 brand 正确 (10分)
    expected_brand = "LuminaSkin"
    if isinstance(data, dict) and data.get("brand") == expected_brand:
        details.append({
            "item": "brand 字段正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"brand = {data['brand']}"
        })
    else:
        actual = data.get("brand") if isinstance(data, dict) else None
        details.append({
            "item": "brand 字段正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 '{expected_brand}', 得到 '{actual}'"
        })

    # 4. total_skus 正确 (30分)
    expected_total = 5
    if isinstance(data, dict) and data.get("total_skus") == expected_total:
        details.append({
            "item": "total_skus 正确",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"total_skus = {data['total_skus']}"
        })
    else:
        actual = data.get("total_skus") if isinstance(data, dict) else None
        details.append({
            "item": "total_skus 正确",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"期望 {expected_total}, 得到 {actual}"
        })

    # 5. with_niacinamide 正确 (40分)
    expected_with_nia = 3
    if isinstance(data, dict) and data.get("with_niacinamide") == expected_with_nia:
        details.append({
            "item": "with_niacinamide 正确",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": f"with_niacinamide = {data['with_niacinamide']}"
        })
    else:
        actual = data.get("with_niacinamide") if isinstance(data, dict) else None
        details.append({
            "item": "with_niacinamide 正确",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": f"期望 {expected_with_nia}, 得到 {actual}"
        })

    total = sum(d["score"] for d in details)
    write_score(workspace, total, details)
    return total

def write_score(workspace, total, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total,
        "details": details
    }
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
