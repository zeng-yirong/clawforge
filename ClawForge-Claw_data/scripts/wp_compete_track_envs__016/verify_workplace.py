"""
verify_workplace.py — 纯代码验证 agent 产物
使用方式: python verify_workplace.py [workplace_path]
"""
import sys
import os
import json
import re
from collections import Counter

WORKPLACE = sys.argv[1] if len(sys.argv) > 1 else "."

def path(*parts):
    return os.path.join(WORKPLACE, *parts)

def load_json(rel_path):
    try:
        with open(path(rel_path), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def clean_user(user):
    """清洗单条用户记录，返回有效用户 dict 或 None"""
    if not isinstance(user, dict):
        return None
    src = user.get("acquisition_source", "")
    if not src or not isinstance(src, str) or src.strip() == "":
        return None
    cid = user.get("competitor_id", "")
    if not cid or not isinstance(cid, str):
        return None
    # 检查 competitor_id 是否在已知竞品中
    known_ids = {"CloudMajor", "DataFlow AI", "SmartSaaS", "TechCorp"}
    if cid not in known_ids:
        return None
    return user

def expected_result():
    """计算预期结果，与 agent 产物比较"""
    # 1. 加载所有 policy 文件
    policy_dir = path("data", "policies")
    if not os.path.isdir(policy_dir):
        return None, "缺少 data/policies 目录"
    targets = set()
    for fname in os.listdir(policy_dir):
        if not fname.endswith(".json"):
            continue
        policy = load_json(os.path.join("data", "policies", fname))
        if policy is None:
            continue
        if policy.get("status") == "active" and policy.get("impact_level") == "high":
            affected = policy.get("impact", {}).get("affected_competitors", [])
            if isinstance(affected, list):
                targets.update(affected)
    # 2. 加载所有 competitor 文件，只保留存在于目录中的
    comp_dir = path("data", "competitors")
    if not os.path.isdir(comp_dir):
        return None, "缺少 data/competitors 目录"
    comp_map = {}
    for fname in os.listdir(comp_dir):
        if not fname.endswith(".json"):
            continue
        comp = load_json(os.path.join("data", "competitors", fname))
        if comp is None:
            continue
        cid = comp.get("competitor_id")
        if cid:
            comp_map[cid] = comp
    # 只保留存在且合法的 competitor_id
    valid_targets = {cid for cid in targets if cid in comp_map}
    # 3. 加载所有用户文件，清洗
    user_dir = path("data", "users")
    if not os.path.isdir(user_dir):
        return None, "缺少 data/users 目录"
    users = []
    for fname in os.listdir(user_dir):
        if not fname.endswith(".json"):
            continue
        user = load_json(os.path.join("data", "users", fname))
        if user is None:
            continue
        cleaned = clean_user(user)
        if cleaned:
            users.append(cleaned)
    # 4. 对每个有效竞品统计 acquisition_source
    result = {"affected_competitors": []}
    sorted_targets = sorted(valid_targets)
    for cid in sorted_targets:
        comp = comp_map[cid]
        source_counter = Counter()
        for u in users:
            if u["competitor_id"] == cid:
                source_counter[u["acquisition_source"]] += 1
        if not source_counter:
            top_source = None
        else:
            top_source = source_counter.most_common(1)[0][0]
        result["affected_competitors"].append({
            "competitor_id": cid,
            "name": comp["name"],
            "market_cap": comp["market_cap"],
            "user_count": comp["user_count"],
            "top_acquisition_source": top_source
        })
    return result, None

def verify():
    # 检查目标文件是否存在
    target_rel = os.path.join("ops", "competitive_analysis.json")
    target_abs = path(target_rel)
    details = []

    # ---- item 1: 文件存在 ----
    if os.path.isfile(target_abs):
        details.append({"item": "目标文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops/competitive_analysis.json 存在"})
    else:
        details.append({"item": "目标文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件未找到"})
        # 终止，无需继续检查
        score = 0
        save_score(score, details)
        return

    # ---- item 2: JSON 合法性 ----
    try:
        with open(target_abs, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 5, "max_score": 5, "passed": True, "reason": "无解析错误"})
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 5, "passed": False, "reason": f"解析失败: {e}"})
        save_score(0, details)
        return

    # ---- 计算期望值 ----
    expected, err = expected_result()
    if err:
        details.append({"item": "期望结果可计算", "score": 0, "max_score": 5, "passed": False, "reason": f"环境数据异常: {err}"})
        save_score(0, details)
        return

    # ---- item 3: 顶级键正确 ----
    if list(data.keys()) == ["affected_competitors"]:
        details.append({"item": "顶级键正确", "score": 5, "max_score": 5, "passed": True, "reason": "仅有 affected_competitors"})
    else:
        details.append({"item": "顶级键正确", "score": 0, "max_score": 5, "passed": False, "reason": f"期望键 ['affected_competitors']，得到 {list(data.keys())}"})

    # ---- item 4: 数组长度匹配 ----
    agent_list = data.get("affected_competitors", [])
    expected_list = expected["affected_competitors"]
    len_ok = len(agent_list) == len(expected_list)
    if len_ok:
        details.append({"item": "affected_competitors 数组长度正确", "score": 5, "max_score": 5, "passed": True, "reason": f"长度 {len(agent_list)}"})
    else:
        details.append({"item": "affected_competitors 数组长度正确", "score": 0, "max_score": 5, "passed": False, "reason": f"期望 {len(expected_list)} 个，实际 {len(agent_list)}"})

    # ---- item 5: 每个对象字段完整 ----
    field_ok = True
    for idx, entry in enumerate(agent_list):
        for key in ["competitor_id", "name", "market_cap", "user_count", "top_acquisition_source"]:
            if key not in entry:
                field_ok = False
                break
        if not field_ok:
            break
    if field_ok:
        details.append({"item": "每个对象包含所有必需字段", "score": 10, "max_score": 10, "passed": True, "reason": "字段齐全"})
    else:
        details.append({"item": "每个对象包含所有必需字段", "score": 0, "max_score": 10, "passed": False, "reason": "缺少字段"})

    # ---- item 6: 字段值逐项正确 ----
    # 按 competitor_id 排序比较
    agent_sorted = sorted(agent_list, key=lambda x: x.get("competitor_id", ""))
    expected_sorted = sorted(expected_list, key=lambda x: x["competitor_id"])
    values_ok = True
    mismatch_reason = ""
    for a, e in zip(agent_sorted, expected_sorted):
        for key in ["competitor_id", "name", "market_cap", "user_count", "top_acquisition_source"]:
            if a.get(key) != e[key]:
                values_ok = False
                mismatch_reason = f"在竞品 {e['competitor_id']} 的 {key} 字段：期望 {e[key]}，实际 {a.get(key)}"
                break
    if values_ok and len(agent_sorted) == len(expected_sorted):
        details.append({"item": "字段值完全匹配预期", "score": 50, "max_score": 50, "passed": True, "reason": "所有条目正确"})
    else:
        score_penalty = 50
        if not len_ok:
            score_penalty = min(score_penalty, 0)  # 长度已扣分，这里只给部分分
        else:
            # 如果有错误，每个错误扣 15 分，最多扣完
            pass
        # 简化：标记失败，给 0 分
        details.append({"item": "字段值完全匹配预期", "score": 0, "max_score": 50, "passed": False, "reason": mismatch_reason or "数组长度不同导致无法逐项比较"})

    # ---- item 7: 无多余字段 ----
    extra_ok = True
    for entry in agent_list:
        if set(entry.keys()) - {"competitor_id", "name", "market_cap", "user_count", "top_acquisition_source"}:
            extra_ok = False
            break
    if extra_ok:
        details.append({"item": "无多余字段", "score": 5, "max_score": 5, "passed": True, "reason": "每个对象仅含指定字段"})
    else:
        details.append({"item": "无多余字段", "score": 0, "max_score": 5, "passed": False, "reason": "发现未要求的字段"})

    # ---- item 8: 文件无其他顶级键 ----
    if list(data.keys()) == ["affected_competitors"]:
        # 已在 item 3 加分，这里不再重复
        pass
    else:
        # 已扣过
        pass

    # ---- 计算总分 ----
    total_score = sum(item["score"] for item in details)
    max_possible = sum(item["max_score"] for item in details)
    # 确保不超 100
    total_score = min(total_score, 100)

    save_score(total_score, details)

def save_score(score, details):
    output = {
        "total_score": score,
        "details": details
    }
    with open(path("workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    # 标准输出也打印
    print(f"Total score: {score}/100")
    for d in details:
        status = "PASS" if d["passed"] else "FAIL"
        print(f"  {status} {d['item']}: {d['score']}/{d['max_score']} - {d['reason']}")

if __name__ == "__main__":
    verify()
