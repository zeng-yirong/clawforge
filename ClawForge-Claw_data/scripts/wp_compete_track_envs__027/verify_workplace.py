#!/usr/bin/env python3
"""
Verify the agent's output for wp_compete_track_envs__027.
Checks that reports/affected_competitors.json exists, is valid JSON,
and contains the expected data based on the environment built by env_builder.py.
"""
import json
import os
import sys
from collections import Counter

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."
SCORE_PATH = os.path.join(WORKSPACE, "workplace_score.json")

def load_json(rel_path):
    full = os.path.join(WORKSPACE, rel_path)
    if not os.path.isfile(full):
        return None
    with open(full, "r") as f:
        return json.load(f)

def main():
    details = []
    total = 0

    # 1. 检查报告目录存在 (5分)
    dir_ok = os.path.isdir(os.path.join(WORKSPACE, "reports"))
    details.append({
        "item": "reports directory exists",
        "score": 5 if dir_ok else 0,
        "max_score": 5,
        "passed": dir_ok,
        "reason": "reports/ 目录存在" if dir_ok else "reports/ 目录不存在"
    })
    if dir_ok:
        total += 5

    # 2. 检查 affected_competitors.json 存在 (10分)
    file_path = "reports/affected_competitors.json"
    data = load_json(file_path)
    file_ok = data is not None
    details.append({
        "item": "affected_competitors.json exists and is valid JSON",
        "score": 10 if file_ok else 0,
        "max_score": 10,
        "passed": file_ok,
        "reason": "文件存在且 JSON 合法" if file_ok else f"文件 {file_path} 不存在或不是合法 JSON"
    })
    if file_ok:
        total += 10
    else:
        # 无法继续验证，直接写结果
        write_score(total, details)
        return

    # 3. 顶层结构 (10分)
    required_top_keys = {"policy", "affected_competitors"}
    top_keys_ok = set(data.keys()) >= required_top_keys
    details.append({
        "item": "JSON 顶层包含 policy 和 affected_competitors",
        "score": 10 if top_keys_ok else 0,
        "max_score": 10,
        "passed": top_keys_ok,
        "reason": "" if top_keys_ok else f"缺失字段, 现有键: {list(data.keys())}"
    })
    if top_keys_ok:
        total += 10

    # 4. policy 字段值正确 (10分)
    policy_ok = isinstance(data.get("policy"), str) and data["policy"] == "EU Digital Markets Act Compliance"
    details.append({
        "item": "policy 字段值为 'EU Digital Markets Act Compliance'",
        "score": 10 if policy_ok else 0,
        "max_score": 10,
        "passed": policy_ok,
        "reason": f"policy = {data.get('policy')}" if not policy_ok else ""
    })
    if policy_ok:
        total += 10

    # 5. affected_competitors 是列表且长度正确 (5分)
    ac = data.get("affected_competitors", [])
    if not isinstance(ac, list):
        ac_len_ok = False
        reason = "不是列表"
    else:
        if len(ac) == 2:
            ac_len_ok = True
            reason = ""
        else:
            ac_len_ok = False
            reason = f"预期 2 个竞品，实际 {len(ac)} 个"
    details.append({
        "item": "affected_competitors 列表长度为 2",
        "score": 5 if ac_len_ok else 0,
        "max_score": 5,
        "passed": ac_len_ok,
        "reason": reason if not ac_len_ok else ""
    })
    if ac_len_ok:
        total += 5

    # 6. 验证第一个竞品 (comp_001 - CloudMajor) (20分)
    # 使用类，但标准化检查
    comp1_ok = False
    comp1_reason = ""
    score1 = 0
    for c in ac:
        if c.get("competitor_id") == "comp_001":
            expected_name = "CloudMajor"
            expected_products = ["DataLake", "Analytics Suite"]
            expected_top_source = "referral"
            # 检查 name
            name_ok = c.get("name") == expected_name
            # 检查 products (顺序忽略？我们强制排序后比较)
            products_ok = isinstance(c.get("products"), list) and sorted(c["products"]) == sorted(expected_products)
            # 检查 top_acquisition_source
            source_ok = c.get("top_acquisition_source") == expected_top_source
            if name_ok and products_ok and source_ok:
                comp1_ok = True
                score1 = 20
                comp1_reason = ""
            else:
                parts = []
                if not name_ok: parts.append("name")
                if not products_ok: parts.append("products")
                if not source_ok: parts.append("top_acquisition_source")
                comp1_reason = f"字段不符: {', '.join(parts)}"
            break
    details.append({
        "item": "comp_001 (CloudMajor) 数据正确 (name, products, top_acquisition_source)",
        "score": score1,
        "max_score": 20,
        "passed": comp1_ok,
        "reason": comp1_reason if not comp1_ok else "正确"
    })
    if comp1_ok:
        total += 20

    # 7. 验证第二个竞品 (comp_002 - DataFlow AI) (20分)
    comp2_ok = False
    comp2_reason = ""
    score2 = 0
    for c in ac:
        if c.get("competitor_id") == "comp_002":
            expected_name = "DataFlow AI"
            expected_products = ["CRM", "Marketing Automation"]
            expected_top_source = "paid_ads"
            name_ok = c.get("name") == expected_name
            products_ok = isinstance(c.get("products"), list) and sorted(c["products"]) == sorted(expected_products)
            source_ok = c.get("top_acquisition_source") == expected_top_source
            if name_ok and products_ok and source_ok:
                comp2_ok = True
                score2 = 20
                comp2_reason = ""
            else:
                parts = []
                if not name_ok: parts.append("name")
                if not products_ok: parts.append("products")
                if not source_ok: parts.append("top_acquisition_source")
                comp2_reason = f"字段不符: {', '.join(parts)}"
            break
    details.append({
        "item": "comp_002 (DataFlow AI) 数据正确 (name, products, top_acquisition_source)",
        "score": score2,
        "max_score": 20,
        "passed": comp2_ok,
        "reason": comp2_reason if not comp2_ok else "正确"
    })
    if comp2_ok:
        total += 20

    # 8. 检查没有多余竞品 (不应包含 comp_003 或 comp_004) (5分)
    extra_ids = [c.get("competitor_id") for c in ac if c.get("competitor_id") not in ("comp_001", "comp_002")]
    extra_ok = len(extra_ids) == 0
    details.append({
        "item": "affected_competitors 中不包含无关竞品",
        "score": 5 if extra_ok else 0,
        "max_score": 5,
        "passed": extra_ok,
        "reason": f"多余竞品: {extra_ids}" if not extra_ok else ""
    })
    if extra_ok:
        total += 5

    # 9. 检查每个竞品都有必要字段 (5分)
    required_comp_fields = {"competitor_id", "name", "products", "top_acquisition_source"}
    fields_ok = True
    bad_fields = []
    for c in ac:
        if not isinstance(c, dict):
            fields_ok = False
            bad_fields.append("非字典元素")
            continue
        missing = required_comp_fields - set(c.keys())
        if missing:
            fields_ok = False
            bad_fields.append(f"{c.get('competitor_id','?')} 缺失 {missing}")
    details.append({
        "item": "每个竞品包含全部必需字段",
        "score": 5 if fields_ok else 0,
        "max_score": 5,
        "passed": fields_ok,
        "reason": "; ".join(bad_fields) if not fields_ok else ""
    })
    if fields_ok:
        total += 5

    # 总分上限 100，但可能超出（如果前面都满分就100，这里不会超）
    total = min(total, 100)

    write_score(total, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open(SCORE_PATH, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
