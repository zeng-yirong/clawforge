import json
import os
import sys
import re

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0
    
    # 1. 检查 ops 目录和 launch_payload.json 存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    target_file = os.path.join(ops_dir, "launch_payload.json")
    
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/ directory found."
        })
        total += 5
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ directory not found."
        })
    
    if os.path.isfile(target_file):
        details.append({
            "item": "launch_payload.json exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "File found."
        })
        total += 5
    else:
        details.append({
            "item": "launch_payload.json exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "File not found at ops/launch_payload.json"
        })
        # 如果文件不存在，后续检查无法进行，直接返回
        final = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return
    
    # 2. 解析 JSON 格式 (10分)
    try:
        payload = load_json(target_file)
        details.append({
            "item": "JSON format valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Successfully parsed."
        })
        total += 10
    except Exception as e:
        details.append({
            "item": "JSON format valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        final = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return
    
    # 3. 检查必填字段是否存在及内容正确 (80分)
    # 期望内容来自 att_orbital_brief_v3.txt
    expected = {
        "brief_id": "bri_009",
        "mission_name": "Nova-7",
        "launch_date": "2025-04-18",
        "approved_message": "We are thrilled to announce the successful launch of Nova-7 satellite, marking a new era in orbital communications. The payload is now in orbit and performing nominally."
    }
    
    # 3a. brief_id (20分)
    if payload.get("brief_id") == expected["brief_id"]:
        details.append({
            "item": "brief_id = bri_009",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct brief_id."
        })
        total += 20
    else:
        details.append({
            "item": "brief_id = bri_009",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {payload.get('brief_id')}, expected bri_009."
        })
    
    # 3b. mission_name (20分)
    if payload.get("mission_name") == expected["mission_name"]:
        details.append({
            "item": "mission_name = Nova-7",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct mission_name."
        })
        total += 20
    else:
        details.append({
            "item": "mission_name = Nova-7",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {payload.get('mission_name')}, expected Nova-7."
        })
    
    # 3c. launch_date (20分)
    if payload.get("launch_date") == expected["launch_date"]:
        details.append({
            "item": "launch_date = 2025-04-18",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct launch_date."
        })
        total += 20
    else:
        details.append({
            "item": "launch_date = 2025-04-18",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {payload.get('launch_date')}, expected 2025-04-18."
        })
    
    # 3d. approved_message (20分)
    # 允许微小的空格差异，但核心字符串必须包含
    msg = payload.get("approved_message", "")
    # 由于可能有换行，我们检查是否包含关键子串
    required_substrings = [
        "thrilled to announce",
        "successful launch",
        "Nova-7 satellite",
        "new era in orbital communications",
        "payload is now in orbit"
    ]
    missing = [s for s in required_substrings if s not in msg]
    if not missing and len(msg) > 50:
        details.append({
            "item": "approved_message contains correct content",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Message matches the approved v3 brief."
        })
        total += 20
    else:
        details.append({
            "item": "approved_message contains correct content",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing substrings: {missing if missing else 'message too short'}"
        })
    
    # 额外检查：禁止出现旧版内容 (扣分项，但不影响总分上限)
    forbidden = ["bri_007", "bri_005", "April 20"]
    for f in forbidden:
        if f in json.dumps(payload):
            # 出现干扰项则扣20分，但总分不低于0
            total = max(0, total - 20)
            details.append({
                "item": f"No forbidden data ({f})",
                "score": -20,
                "max_score": 0,
                "passed": False,
                "reason": f"Payload contains reference to {f} from old brief."
            })
    
    # 确保总分在 0-100 之间
    total = max(0, min(100, total))
    
    final = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
