import sys
import json
import os
from pathlib import Path

def time_to_minutes(t: str) -> int:
    """将 HH:MM 格式转换为分钟数"""
    parts = t.split(":")
    return int(parts[0]) * 60 + int(parts[1])

def overlap_length(start1: int, end1: int, start2: int, end2: int) -> int:
    """返回两个区间重叠的分钟数，如果没有重叠返回 0"""
    start = max(start1, start2)
    end = min(end1, end2)
    return max(0, end - start)

def compute_answer(workspace: str) -> dict:
    """计算预期的答案（用于调试，但最终 verifier 直接用硬编码值）"""
    # 实际 verifier 不应依赖此函数，这里只是为了说明答案唯一性
    pass

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base = Path(workspace)
    details = []
    total_score = 0

    # ===== 1. 检查 ops 目录是否存在 (10分) =====
    ops_dir = base / "ops"
    item = {"item": "ops 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if ops_dir.is_dir():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops 目录已创建"
    else:
        item["reason"] = "ops 目录不存在"
    details.append(item)
    total_score += item["score"]

    # ===== 2. 检查 peak_conflict.json 文件是否存在 (10分) =====
    result_file = ops_dir / "peak_conflict.json"
    item = {"item": "peak_conflict.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if result_file.is_file():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "文件存在"
    else:
        item["reason"] = f"文件不存在: {result_file}"
    details.append(item)
    total_score += item["score"]

    # ===== 3. JSON 合法 (10分) =====
    item = {"item": "peak_conflict.json 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "JSON 解析成功"
    except Exception as e:
        item["reason"] = f"JSON 解析失败: {e}"
        # 后续检查跳过，直接输出
        details.append(item)
        total_score += item["score"]
        # 输出结果并退出
        final = {"total_score": total_score, "details": details}
        with open(base / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        print(json.dumps(final))
        return

    details.append(item)
    total_score += item["score"]

    # ===== 4. 检查字段存在且正确 (20分) =====
    item = {"item": "字段完整性（device_id_a, device_id_b, total_overlap_minutes）", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    required_fields = ["device_id_a", "device_id_b", "total_overlap_minutes"]
    if all(f in data for f in required_fields):
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "所有必填字段存在"
    else:
        missing = [f for f in required_fields if f not in data]
        item["reason"] = f"缺少字段: {missing}"
    details.append(item)
    total_score += item["score"]

    # ===== 5. 精确数值匹配 (50分) =====
    item = {"item": "精确答案匹配", "score": 0, "max_score": 50, "passed": False, "reason": ""}
    # 预期答案
    expected_device_a = "device_001"
    expected_device_b = "device_002"
    expected_overlap = 60  # 分钟

    device_a_ok = data.get("device_id_a") == expected_device_a
    device_b_ok = data.get("device_id_b") == expected_device_b
    overlap_ok = data.get("total_overlap_minutes") == expected_overlap

    if device_a_ok and device_b_ok and overlap_ok:
        item["score"] = 50
        item["passed"] = True
        item["reason"] = f"正确: device_id_a={expected_device_a}, device_id_b={expected_device_b}, total_overlap_minutes={expected_overlap}"
    else:
        errors = []
        if not device_a_ok:
            errors.append(f"device_id_a 应为 {expected_device_a}，实际为 {data.get('device_id_a')}")
        if not device_b_ok:
            errors.append(f"device_id_b 应为 {expected_device_b}，实际为 {data.get('device_id_b')}")
        if not overlap_ok:
            errors.append(f"total_overlap_minutes 应为 {expected_overlap}，实际为 {data.get('total_overlap_minutes')}")
        item["reason"] = "; ".join(errors)
    details.append(item)
    total_score += item["score"]

    # ===== 汇总并写入 =====
    final = {
        "total_score": total_score,
        "details": details
    }
    with open(base / "workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)
    print(json.dumps(final))

if __name__ == "__main__":
    main()
