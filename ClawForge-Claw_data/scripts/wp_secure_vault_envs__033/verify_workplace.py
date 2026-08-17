import os
import sys
import json
import csv
import re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_csv(filename):
    path = os.path.join(workspace, filename)
    if not os.path.exists(path):
        return []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_json(filename):
    path = os.path.join(workspace, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def check_weak_policy(password, policy):
    # policy: dict with keys: min_length, require_upper, require_lower, require_digit, require_special
    if len(password) < policy["min_length"]:
        return True
    if policy.get("require_upper") and not re.search(r'[A-Z]', password):
        return True
    if policy.get("require_lower") and not re.search(r'[a-z]', password):
        return True
    if policy.get("require_digit") and not re.search(r'[0-9]', password):
        return True
    if policy.get("require_special"):
        special = r'[!@#$%^&*()_+\-=\[\]{}|;:\'",./<>?~`]'
        if not re.search(special, password):
            return True
    return False

def build_expected(workspace):
    # Load raw credentials
    raw_rows = load_csv("data/raw_credentials.csv")
    # Load category mapping
    mapping_rows = load_csv("data/category_mapping.csv")
    category_map = {r["raw_category"]: r["vault_category"] for r in mapping_rows}
    # Load policy
    policy = load_json("policies/password_policy.json")
    if not policy:
        policy = {"min_length": 8, "require_upper": True, "require_lower": True,
                  "require_digit": True, "require_special": True}

    # Deduplicate: keep last occurrence by id
    seen = {}
    for row in raw_rows:
        rid = row["id"]
        seen[rid] = row  # overwrites previous

    expected = []
    for rid in sorted(seen.keys(), key=lambda x: int(x)):
        row = seen[rid]
        cat_raw = row["category"]
        cat = category_map.get(cat_raw, "未分类")
        pwd = row["password"]
        is_weak = check_weak_policy(pwd, policy)
        expected.append({
            "id": int(rid),
            "username": row["username"],
            "password": pwd,
            "category": cat,
            "is_weak": is_weak
        })
    return expected

details = []
total_score = 0

# 1. File existence (10)
target_path = os.path.join(workspace, "vault/classified_credentials.json")
if os.path.exists(target_path):
    details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "vault/classified_credentials.json 存在"})
    total_score += 10
else:
    details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})

if os.path.exists(target_path):
    # 2. Valid JSON (10)
    try:
        with open(target_path) as f:
            agent_data = json.load(f)
        details.append({"item": "合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        total_score += 10
    except json.JSONDecodeError as e:
        details.append({"item": "合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        agent_data = None

    if agent_data is not None:
        # 3. Structure (10)
        struct_ok = True
        if not isinstance(agent_data, list):
            struct_ok = False
            details.append({"item": "数据结构", "score": 0, "max_score": 10, "passed": False, "reason": "根元素不是数组"})
        else:
            required_fields = ["id","username","password","category","is_weak"]
            for i, entry in enumerate(agent_data):
                if not isinstance(entry, dict):
                    struct_ok = False
                    break
                missing = [f for f in required_fields if f not in entry]
                if missing:
                    struct_ok = False
                    break
            if struct_ok:
                details.append({"item": "数据结构", "score": 10, "max_score": 10, "passed": True, "reason": "数组且每个元素包含所有必需字段"})
                total_score += 10
            else:
                details.append({"item": "数据结构", "score": 0, "max_score": 10, "passed": False, "reason": "字段缺失或结构错误"})

        if struct_ok:
            # Build expected
            expected = build_expected(workspace)

            # 4. Deduplication correctness (20) - compare record count and id uniqueness
            agent_ids = set(e["id"] for e in agent_data)
            expected_ids = set(e["id"] for e in expected)
            if agent_ids == expected_ids and len(agent_data) == len(expected):
                dedup_ok = True
            else:
                dedup_ok = False
            if dedup_ok:
                details.append({"item": "去重正确", "score": 20, "max_score": 20, "passed": True, "reason": f"记录数{len(agent_data)}，id集合与预期一致"})
                total_score += 20
            else:
                details.append({"item": "去重正确", "score": 0, "max_score": 20, "passed": False, "reason": f"agent记录数{len(agent_data)}，预期{len(expected)}；id集合差异"})

            # 5. Category mapping (25) - 每正确一条得1分，最多25
            cat_score = 0
            cat_max = 25
            # Build lookup map from agent data by id
            agent_by_id = {e["id"]: e for e in agent_data}
            for exp in expected:
                a = agent_by_id.get(exp["id"])
                if a and a["category"] == exp["category"]:
                    cat_score += 1
            cat_score = min(cat_score, cat_max)
            total_score += cat_score
            details.append({
                "item": "Category映射正确",
                "score": cat_score,
                "max_score": cat_max,
                "passed": cat_score == cat_max,
                "reason": f"正确匹配{cat_score}/{cat_max}条"
            })

            # 6. Weak password judgment (20)
            weak_score = 0
            weak_max = 20
            for exp in expected:
                a = agent_by_id.get(exp["id"])
                if a and a["is_weak"] == exp["is_weak"]:
                    weak_score += 1
            weak_score = min(weak_score, weak_max)
            total_score += weak_score
            details.append({
                "item": "弱密码判断正确",
                "score": weak_score,
                "max_score": weak_max,
                "passed": weak_score == weak_max,
                "reason": f"正确判断{weak_score}/{weak_max}条"
            })

            # 7. Sorting by id (5)
            agent_sorted = all(agent_data[i]["id"] <= agent_data[i+1]["id"] for i in range(len(agent_data)-1))
            if agent_sorted:
                details.append({"item": "排序正确", "score": 5, "max_score": 5, "passed": True, "reason": "按id升序排列"})
                total_score += 5
            else:
                details.append({"item": "排序正确", "score": 0, "max_score": 5, "passed": False, "reason": "未按id升序"})

else:
    # File missing, skip other checks
    pass

# Ensure total_score integer
total_score = min(total_score, 100)

result = {
    "total_score": total_score,
    "details": details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
