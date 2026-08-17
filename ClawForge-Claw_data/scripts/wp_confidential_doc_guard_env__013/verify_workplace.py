import os
import sys
import json

def verify(workspace):
    result = {
        "total_score": 0,
        "details": []
    }

    # 1. 检查 ops/block_list.json 是否存在 (10分)
    block_list_path = os.path.join(workspace, "ops", "block_list.json")
    if os.path.isfile(block_list_path):
        result["details"].append({
            "item": "ops/block_list.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found at expected path"
        })
    else:
        result["details"].append({
            "item": "ops/block_list.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        result["total_score"] = 0
        # 如果文件不存在直接返回，以免后面出错
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 检查 JSON 是否合法 (10分)
    try:
        with open(block_list_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            result["details"].append({
                "item": "JSON is a valid list",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "File contains a JSON array"
            })
        else:
            result["details"].append({
                "item": "JSON is a valid list",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Expected list, got {type(data).__name__}"
            })
            # 即使不是列表也继续尝试处理
    except Exception as e:
        result["details"].append({
            "item": "JSON is a valid list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        result["total_score"] = 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 预期答案：根据 env_builder 构建的数据，应拦截的请求ID
    expected_ids = {"req-001", "req-002", "req-006"}
    actual_ids = set(data) if isinstance(data, list) else set()

    # 3. 检查是否包含了所有预期ID (70分，每个约23.33，但按总分70分配)
    # 这里我们设计每个预期ID占 20分，全部正确再加10分奖励（共70）
    # 实际更简单：检查交集和多余
    correct = actual_ids & expected_ids
    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids

    # 基础分：每个正确ID得20分
    base_correct_score = len(correct) * 20
    # 漏掉一个扣15分（但不超过基础分）
    penalty_missing = len(missing) * 15
    # 多余一个扣10分
    penalty_extra = len(extra) * 10

    core_score = max(0, base_correct_score - penalty_missing - penalty_extra)
    core_score = min(core_score, 70)  # 封顶70

    detail_reason = f"Correct IDs: {correct}. Missing: {missing}. Extra: {extra}."
    result["details"].append({
        "item": "Correct request IDs in block_list",
        "score": core_score,
        "max_score": 70,
        "passed": (len(missing) == 0 and len(extra) == 0),
        "reason": detail_reason
    })

    # 汇总总分
    total = sum(d["score"] for d in result["details"])
    result["total_score"] = total

    # 写入结果文件
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
