import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    result = {"total_score": 0, "details": []}
    total_max = 100

    # 1. 检查 ops 目录是否存在
    dir_check = os.path.isdir("ops")
    result["details"].append({
        "item": "检查 ops 目录是否存在",
        "score": 10 if dir_check else 0,
        "max_score": 10,
        "passed": dir_check,
        "reason": "ops 目录存在" if dir_check else "ops 目录不存在"
    })

    # 2. 检查 ops/alert.json 文件是否存在
    file_path = "ops/alert.json"
    file_exists = os.path.isfile(file_path)
    result["details"].append({
        "item": "检查 ops/alert.json 文件是否存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "alert.json 存在" if file_exists else "alert.json 不存在"
    })

    if not file_exists:
        result["total_score"] = sum(d["score"] for d in result["details"])
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 文件格式合法性（JSON）
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        valid_json = True
        reason = "JSON 解析成功"
    except Exception as e:
        valid_json = False
        reason = f"JSON 解析失败: {str(e)}"
    result["details"].append({
        "item": "文件格式合法 JSON",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": reason
    })

    if not valid_json:
        result["total_score"] = sum(d["score"] for d in result["details"])
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 检查 competitor_id 字段
    expected_id = "smart_saas_001"
    actual_id = data.get("competitor_id")
    id_match = actual_id == expected_id
    result["details"].append({
        "item": "competitor_id 正确",
        "score": 20 if id_match else 0,
        "max_score": 20,
        "passed": id_match,
        "reason": f"competitor_id = '{actual_id}'" if id_match else f"期望 '{expected_id}', 实际 '{actual_id}'"
    })

    # 5. 检查 name 字段
    expected_name = "SmartSaaS"
    actual_name = data.get("name")
    name_match = actual_name == expected_name
    result["details"].append({
        "item": "name 正确",
        "score": 10 if name_match else 0,
        "max_score": 10,
        "passed": name_match,
        "reason": f"name = '{actual_name}'" if name_match else f"期望 '{expected_name}', 实际 '{actual_name}'"
    })

    # 6. 检查 market_share 数值（精确到小数点后1位）
    expected_share = 12.5
    actual_share = data.get("market_share")
    share_match = isinstance(actual_share, (int, float)) and abs(actual_share - expected_share) < 0.01
    result["details"].append({
        "item": "market_share 数值正确",
        "score": 10 if share_match else 0,
        "max_score": 10,
        "passed": share_match,
        "reason": f"market_share = {actual_share}" if share_match else f"期望 {expected_share}, 实际 {actual_share}"
    })

    # 7. 检查 growth_rate 数值
    expected_growth = 8.3
    actual_growth = data.get("growth_rate")
    growth_match = isinstance(actual_growth, (int, float)) and abs(actual_growth - expected_growth) < 0.01
    result["details"].append({
        "item": "growth_rate 数值正确",
        "score": 10 if growth_match else 0,
        "max_score": 10,
        "passed": growth_match,
        "reason": f"growth_rate = {actual_growth}" if growth_match else f"期望 {expected_growth}, 实际 {actual_growth}"
    })

    # 8. 检查 policies 数组
    policies = data.get("policies")
    if not isinstance(policies, list):
        policies = []
    expected_policies = [
        {"policy_id": "pol_01", "title": "EU Digital Markets Act Compliance"}
    ]
    # 规范化比较：只校验必要字段，且忽略顺序
    def normalize_policy(p):
        return {"policy_id": p.get("policy_id"), "title": p.get("title")}
    actual_set = {tuple(sorted(normalize_policy(p).items())) for p in policies if isinstance(p, dict)}
    expected_set = {tuple(sorted(normalize_policy(ep).items())) for ep in expected_policies}
    policies_match = actual_set == expected_set
    result["details"].append({
        "item": "policies 数组包含正确的活跃政策",
        "score": 20 if policies_match else 0,
        "max_score": 20,
        "passed": policies_match,
        "reason": f"实际 policies = {policies}" if policies_match else f"期望 {expected_policies}, 实际 {policies}"
    })

    # 计算总分
    total = sum(d["score"] for d in result["details"])
    result["total_score"] = total

    # 写入评分文件
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
