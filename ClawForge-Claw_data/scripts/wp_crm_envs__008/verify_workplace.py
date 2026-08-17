import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    details = []

    # ---- 1. 目录结构 (10) ----
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops目录存在"})
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops目录未创建"})

    target = ops_dir / "pending_birthday_contacts.json"
    if target.is_file():
        details.append({"item": "产物文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件ops/pending_birthday_contacts.json存在"})
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件ops/pending_birthday_contacts.json不存在"})
        # 后续检查无法进行，直接写结果
        _write_score(ws, details)
        return

    # ---- 2. 格式检查 (10) ----
    try:
        with open(target, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            details.append({"item": "JSON根为数组", "score": 0, "max_score": 10, "passed": False, "reason": "JSON根元素不是数组"})
            _write_score(ws, details)
            return
        details.append({"item": "JSON根为数组", "score": 10, "max_score": 10, "passed": True, "reason": "JSON合法，根为数组"})
    except Exception as e:
        details.append({"item": "JSON解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        _write_score(ws, details)
        return

    # ---- 3. 元素类型 (10) ----
    if all(isinstance(x, str) for x in data):
        details.append({"item": "元素均为字符串", "score": 10, "max_score": 10, "passed": True, "reason": "所有元素都是字符串"})
    else:
        details.append({"item": "元素均为字符串", "score": 0, "max_score": 10, "passed": False, "reason": "数组中存在非字符串元素"})
        _write_score(ws, details)
        return

    # ---- 4. 内容准确性 (70) ----
    expected = {"ct_102", "ct_103"}
    actual_set = set(data)
    missing = expected - actual_set
    extra = actual_set - expected
    duplicates = len(data) != len(actual_set)

    content_score = 70
    reason_parts = []
    if missing:
        content_score -= len(missing) * 15
        reason_parts.append(f"缺少 {sorted(missing)}")
    if extra:
        content_score -= len(extra) * 15
        reason_parts.append(f"多余 {sorted(extra)}")
    if duplicates:
        content_score -= 10
        reason_parts.append("存在重复ID")
    content_score = max(0, content_score)
    if content_score == 70:
        reason_parts.append("完全符合预期")
    details.append({
        "item": "内容正确性",
        "score": content_score,
        "max_score": 70,
        "passed": content_score == 70,
        "reason": "; ".join(reason_parts)
    })

    # ---- 汇总 ----
    total = sum(d["score"] for d in details)
    _write_score(ws, details, total)

def _write_score(ws, details, total=None):
    if total is None:
        total = sum(d["score"] for d in details)
    result = {"total_score": total, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}")

if __name__ == "__main__":
    main()
