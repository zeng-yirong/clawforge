#!/usr/bin/env python3
import json, os, sys, datetime
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    scores = []
    total_score = 0

    # ==================== 1. 检查 ops/acknowledgement.json 存在 (10分) ====================
    ack_path = ws / "ops" / "acknowledgement.json"
    if ack_path.exists() and ack_path.is_file():
        scores.append({"item": "ops/acknowledgement.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10
    else:
        scores.append({"item": "ops/acknowledgement.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 关键文件缺失，后续无法评分，直接输出
        finalize(scores, total_score, ws)
        return

    # ==================== 2. JSON 格式合法 (10分) ====================
    try:
        with open(ack_path, "r") as f:
            ack = json.load(f)
        scores.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        total_score += 10
    except Exception as e:
        scores.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        finalize(scores, total_score, ws)
        return

    # ==================== 3. 必备字段检查 (20分) ====================
    required_fields = ["zone_id", "account_id", "contact_id", "acknowledged_at"]
    missing = [f for f in required_fields if f not in ack]
    if not missing:
        scores.append({"item": "Required fields present", "score": 20, "max_score": 20, "passed": True, "reason": "All fields: zone_id, account_id, contact_id, acknowledged_at"})
        total_score += 20
    else:
        scores.append({"item": "Required fields present", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing fields: {missing}"})
        finalize(scores, total_score, ws)
        return

    # ==================== 4. zone_id 正确性 (15分) ====================
    expected_zone_id = "zone_lobby"
    if ack["zone_id"] == expected_zone_id:
        scores.append({"item": "zone_id is correct", "score": 15, "max_score": 15, "passed": True, "reason": f"Value equals '{expected_zone_id}'"})
        total_score += 15
    else:
        scores.append({"item": "zone_id is correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected '{expected_zone_id}', got '{ack.get('zone_id')}'"})

    # ==================== 5. account_id 正确性 (15分) ====================
    expected_account_id = "acc_main"
    if ack["account_id"] == expected_account_id:
        scores.append({"item": "account_id is correct", "score": 15, "max_score": 15, "passed": True, "reason": f"Value equals '{expected_account_id}'"})
        total_score += 15
    else:
        scores.append({"item": "account_id is correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected '{expected_account_id}', got '{ack.get('account_id')}'"})

    # ==================== 6. contact_id 正确性 (20分) ====================
    # 根据env_builder，acc_main的emergency_contacts第一个角色为Monitoring Service的是c_002
    expected_contact_id = "c_002"
    if ack["contact_id"] == expected_contact_id:
        scores.append({"item": "contact_id is correct (first Monitoring Service)", "score": 20, "max_score": 20, "passed": True, "reason": f"Value equals '{expected_contact_id}'"})
        total_score += 20
    else:
        scores.append({"item": "contact_id is correct (first Monitoring Service)", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected '{expected_contact_id}', got '{ack.get('contact_id')}'"})

    # ==================== 7. acknowledged_at 格式与范围 (10分) ====================
    timestamp_str = ack.get("acknowledged_at", "")
    try:
        # 解析ISO格式，允许'Z'结尾
        if timestamp_str.endswith("Z"):
            timestamp_str_clean = timestamp_str[:-1] + "+00:00"
        else:
            timestamp_str_clean = timestamp_str
        dt = datetime.datetime.fromisoformat(timestamp_str_clean)
        # 时间应在 env_builder 执行后附近（允许前后5分钟偏差）
        now = datetime.datetime.now(datetime.timezone.utc)
        lower = now - datetime.timedelta(minutes=5)
        upper = now + datetime.timedelta(minutes=5)
        if lower <= dt <= upper:
            scores.append({"item": "acknowledged_at valid ISO UTC timestamp", "score": 10, "max_score": 10, "passed": True, "reason": f"Timestamp {ack['acknowledged_at']} within acceptable range"})
            total_score += 10
        else:
            scores.append({"item": "acknowledged_at valid ISO UTC timestamp", "score": 5, "max_score": 10, "passed": False, "reason": f"Timestamp {ack['acknowledged_at']} is outside ±5 min window (now={now.isoformat()})"})
    except Exception as e:
        scores.append({"item": "acknowledged_at valid ISO UTC timestamp", "score": 0, "max_score": 10, "passed": False, "reason": f"Cannot parse timestamp: {e}"})

    finalize(scores, total_score, ws)

def finalize(scores, total_score, ws):
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": scores
    }
    score_path = ws / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {score_path}: {total_score}/100")
    # 退出代码不强制，保持兼容

if __name__ == "__main__":
    main()
