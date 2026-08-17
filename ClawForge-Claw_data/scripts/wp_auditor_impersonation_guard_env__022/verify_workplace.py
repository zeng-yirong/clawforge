import sys
import os
import json
import csv
from pathlib import Path

def score_workplace(workspace):
    workspace = Path(workspace)
    results = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (5分)
    ops_dir = workspace / "ops"
    if ops_dir.is_dir():
        results.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ directory found"})
        total_score += 5
    else:
        results.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ directory missing"})

    # 2. 检查 denied_requests.json 是否存在 (10分)
    denied_path = ops_dir / "denied_requests.json"
    if denied_path.is_file():
        results.append({"item": "denied_requests.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        results.append({"item": "denied_requests.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing at ops/denied_requests.json"})
        # 后续检查无法进行，直接返回
        final_score = min(total_score, 100)
        output = {"total_score": final_score, "details": results}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        return

    # 3. 内容可解析为 JSON (10分)
    try:
        with open(denied_path, "r") as f:
            data = json.load(f)
        results.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parsed successfully"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        results.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {e}"})
        final_score = min(total_score, 100)
        output = {"total_score": final_score, "details": results}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        return

    # 4. 内容是一个数组 (10分)
    if isinstance(data, list):
        results.append({"item": "JSON is a list", "score": 10, "max_score": 10, "passed": True, "reason": "top-level is array"})
        total_score += 10
    else:
        results.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"expected list but got {type(data).__name__}"})
        final_score = min(total_score, 100)
        output = {"total_score": final_score, "details": results}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        return

    # 5. 计算期望的正确答案（基于工作区原始数据）
    # 读取 contacts.json
    contacts_path = workspace / "contacts.json"
    real_auditors = set()
    if contacts_path.is_file():
        with open(contacts_path, "r") as f:
            contacts_data = json.load(f)
        contacts_list = contacts_data.get("contacts", [])
        for c in contacts_list:
            if c.get("role") == "Internal Security Auditor":
                real_auditors.add(c["name"])
    else:
        # 如果contacts.json丢失，则无法验证，但理论上应该存在
        real_auditors = {"Alice Wang", "Bob Li", "David Chen"}  # fallback

    # 读取 requests/requests.json
    requests_path = workspace / "requests" / "requests.json"
    expected_ids = set()
    if requests_path.is_file():
        with open(requests_path, "r") as f:
            req_data = json.load(f)
        req_list = req_data.get("requests", [])
        for r in req_list:
            if r.get("claimed_role") == "Internal Security Auditor" and r.get("actor_name") not in real_auditors:
                expected_ids.add(r["request_id"])
    else:
        # 使用硬编码的预期（如果文件丢失，我们仍用已知答案）
        expected_ids = {"req-003", "req-005"}

    # 检查数组元素都是字符串 (5分)
    all_strings = all(isinstance(x, str) for x in data)
    if all_strings:
        results.append({"item": "all elements are strings", "score": 5, "max_score": 5, "passed": True, "reason": "every element is a string"})
        total_score += 5
    else:
        results.append({"item": "all elements are strings", "score": 0, "max_score": 5, "passed": False, "reason": "some elements are not strings"})

    # 6. 集合比较：包含 req-003 (15分)
    if "req-003" in data:
        results.append({"item": "contains req-003", "score": 15, "max_score": 15, "passed": True, "reason": "found req-003"})
        total_score += 15
    else:
        results.append({"item": "contains req-003", "score": 0, "max_score": 15, "passed": False, "reason": "req-003 missing"})

    # 7. 包含 req-005 (15分)
    if "req-005" in data:
        results.append({"item": "contains req-005", "score": 15, "max_score": 15, "passed": True, "reason": "found req-005"})
        total_score += 15
    else:
        results.append({"item": "contains req-005", "score": 0, "max_score": 15, "passed": False, "reason": "req-005 missing"})

    # 8. 没有多余元素（即集合大小等于期望大小，且没有额外元素）(15分)
    agent_set = set(data)
    if agent_set == expected_ids:
        results.append({"item": "no extra or missing elements", "score": 15, "max_score": 15, "passed": True, "reason": f"exactly matches expected {expected_ids}"})
        total_score += 15
    elif agent_set < expected_ids:
        missing = expected_ids - agent_set
        results.append({"item": "no extra or missing elements", "score": 0, "max_score": 15, "passed": False, "reason": f"missing elements: {missing}"})
    else:
        extra = agent_set - expected_ids
        results.append({"item": "no extra or missing elements", "score": 0, "max_score": 15, "passed": False, "reason": f"extra elements: {extra}"})

    final_score = min(total_score, 100)
    output = {"total_score": final_score, "details": results}
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_workplace(workspace)
