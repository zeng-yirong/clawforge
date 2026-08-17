import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    score_details = []
    total_score = 0

    # 1. ops 目录存在 (5 分)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        score_details.append({
            "item": "ops directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    # 2. ops/kill_target.json 文件存在 (5 分)
    target_file = ops_dir / "kill_target.json"
    if target_file.is_file():
        score_details.append({
            "item": "ops/kill_target.json exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "file present"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "ops/kill_target.json exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "file not found"
        })
        # 如果不存在，后续项自动0分，但为了输出完整仍记录
        # 直接跳到结束
        finish(score_details, total_score)
        return

    # 3. JSON 可解析 (5 分)
    try:
        content = json.loads(target_file.read_text())
        score_details.append({
            "item": "JSON format valid",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "parsed successfully"
        })
        total_score += 5
    except Exception as e:
        score_details.append({
            "item": "JSON format valid",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"parse error: {e}"
        })
        finish(score_details, total_score)
        return

    # 4. 包含 "transaction_id" 键 (10 分)
    if "transaction_id" in content:
        score_details.append({
            "item": "key 'transaction_id' present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "key found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "key 'transaction_id' present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "key missing"
        })

    # 5. transaction_id 值正确（整数 999888） (50 分)
    tid = content.get("transaction_id")
    expected = 999888  # 根据 slow_query.log 中最旧 ACTIVE 的 PID
    if isinstance(tid, int) and tid == expected:
        score_details.append({
            "item": "transaction_id value = 999888",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": "exact match"
        })
        total_score += 50
    elif isinstance(tid, int) and tid != expected:
        score_details.append({
            "item": "transaction_id value = 999888",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"incorrect value: {tid}"
        })
    else:
        score_details.append({
            "item": "transaction_id value = 999888",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"not an integer or missing, got {type(tid).__name__}: {tid}"
        })

    # 6. 没有多余键 (5 分)
    extra_keys = set(content.keys()) - {"transaction_id"}
    if not extra_keys:
        score_details.append({
            "item": "no extra keys in JSON",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "only expected key"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "no extra keys in JSON",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"unexpected keys: {extra_keys}"
        })

    # 7. ops 目录下只有 kill_target.json (10 分)
    ops_files = list(ops_dir.iterdir())
    if len(ops_files) == 1 and ops_files[0].name == "kill_target.json":
        score_details.append({
            "item": "ops directory contains only kill_target.json",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "clean output"
        })
        total_score += 10
    else:
        # 如果还有其他文件，扣分（但允许目录本身）
        extra_files = [f.name for f in ops_files if f.name != "kill_target.json"]
        score_details.append({
            "item": "ops directory contains only kill_target.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"extra files: {extra_files}" if extra_files else "kill_target.json missing (should not happen here)"
        })

    # 写入结果
    finish(score_details, total_score)

def finish(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    # 确保输出目录存在
    output_path = Path("workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

if __name__ == "__main__":
    main()
