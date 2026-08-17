import json
import os
import sys
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace).resolve()
    
    score_details = []
    total_score = 0
    
    # 1. 检查 ops/remediated_ids.json 是否存在
    target_file = workspace_path / "ops" / "remediated_ids.json"
    if not target_file.exists():
        score_details.append({
            "item": "文件 ops/remediated_ids.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 直接结束，没必要继续
        final_score = 0
        write_score(workspace_path, final_score, score_details)
        return
    
    score_details.append({
        "item": "文件 ops/remediated_ids.json 存在",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "文件存在"
    })
    total_score += 10
    
    # 2. 检查 JSON 合法性
    try:
        with open(target_file, "r") as f:
            content = json.load(f)
        score_details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析 JSON"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        write_score(workspace_path, total_score, score_details)
        return
    
    # 3. 检查 content 是否为 list
    if not isinstance(content, list):
        score_details.append({
            "item": "内容为数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望数组，获得 {type(content).__name__}"
        })
        write_score(workspace_path, total_score, score_details)
        return
    
    score_details.append({
        "item": "内容为数组",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "是 JSON 数组"
    })
    total_score += 10
    
    # 4. 计算预期答案 (从 incident_pool.json)
    pool_path = workspace_path / "data" / "incidents" / "incident_pool.json"
    try:
        with open(pool_path, "r") as f:
            pool_data = json.load(f)
    except Exception as e:
        # 如果池文件异常，则无法验证
        score_details.append({
            "item": "工单池数据读取",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"无法读取 incident_pool.json: {str(e)}"
        })
        write_score(workspace_path, total_score, score_details)
        return
    
    incidents = pool_data.get("incidents", [])
    expected_ids = []
    for inc in incidents:
        cat = inc.get("category", "")
        sev = inc.get("severity", "")
        # 根据 runbook 规则：精确匹配小写字符串
        if (cat == "ups_outage" or cat == "service_down") and sev == "critical":
            expected_ids.append(inc["incident_id"])
    expected_ids.sort()  # 按字母序排序
    
    # 5. 比较长度
    agent_ids = content
    agent_ids_str = [str(x) for x in agent_ids]  # 确保都是字符串
    len_correct = len(agent_ids_str) == len(expected_ids)
    if len_correct:
        score_details.append({
            "item": "数组长度正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"长度 {len(agent_ids_str)} 与预期一致"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "数组长度正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"长度 {len(agent_ids_str)}，预期 {len(expected_ids)}"
        })
    
    # 6. 逐元素比较（顺序必须一致）
    element_passed = True
    if len_correct:
        for i, (a, e) in enumerate(zip(agent_ids_str, expected_ids)):
            if a != e:
                element_passed = False
                break
        if element_passed:
            score_details.append({
                "item": "所有元素及顺序正确",
                "score": 60,
                "max_score": 60,
                "passed": True,
                "reason": f"元素匹配：{expected_ids}"
            })
            total_score += 60
        else:
            score_details.append({
                "item": "所有元素及顺序正确",
                "score": 0,
                "max_score": 60,
                "passed": False,
                "reason": f"元素不匹配。预期 {expected_ids}，获得 {agent_ids_str}"
            })
    else:
        # 长度不对时，无法得元素分
        score_details.append({
            "item": "所有元素及顺序正确",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "长度错误，无法逐元素比较"
        })
    
    # 写入评分
    final_score = min(total_score, 100)  # 防止意外超过
    write_score(workspace_path, final_score, score_details)

def write_score(workspace_path, total_score, details):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    score_file = workspace_path / "workplace_score.json"
    with open(score_file, "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    main()
