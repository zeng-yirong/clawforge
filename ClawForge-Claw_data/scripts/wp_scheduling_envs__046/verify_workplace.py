import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "ops", "ac_command.json")
    details = []
    total_score = 0

    # 1. 目录结构检查（ops 目录）
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops/ directory found" if dir_exists else "ops/ directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. 文件存在性
    file_exists = os.path.isfile(result_path)
    details.append({
        "item": "ac_command.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "ops/ac_command.json found" if file_exists else "ops/ac_command.json not found"
    })
    if file_exists:
        total_score += 10

    # 3. JSON 合法性
    data = None
    json_valid = False
    if file_exists:
        try:
            with open(result_path, 'r') as f:
                data = json.load(f)
            json_valid = True
            details.append({
                "item": "valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "File is valid JSON"
            })
            total_score += 10
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {str(e)}"
            })
    else:
        details.append({
            "item": "valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File does not exist, cannot validate JSON"
        })

    # 4. 字段检查（仅当 JSON 合法时）
    device_id_ok = False
    action_ok = False
    temp_ok = False
    if json_valid and data is not None:
        # 4a. device_id
        did = data.get("device_id")
        if did == "Living Room AC":
            device_id_ok = True
            details.append({
                "item": "device_id correct",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "device_id is 'Living Room AC'"
            })
            total_score += 20
        else:
            details.append({
                "item": "device_id correct",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"Expected 'Living Room AC', got '{did}'"
            })

        # 4b. action
        act = data.get("action")
        if act == "turn_on":
            action_ok = True
            details.append({
                "item": "action correct",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "action is 'turn_on'"
            })
            total_score += 20
        else:
            details.append({
                "item": "action correct",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"Expected 'turn_on', got '{act}'"
            })

        # 4c. temperature_celsius
        temp = data.get("temperature_celsius")
        if temp == 24:
            temp_ok = True
            details.append({
                "item": "temperature_celsius correct",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": "temperature_celsius is 24"
            })
            total_score += 30
        else:
            details.append({
                "item": "temperature_celsius correct",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": f"Expected 24, got {temp}"
            })
    else:
        # 如果 JSON 无效，相应项得 0 分
        details.append({
            "item": "device_id correct",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "JSON invalid, cannot check field"
        })
        details.append({
            "item": "action correct",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "JSON invalid, cannot check field"
        })
        details.append({
            "item": "temperature_celsius correct",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "JSON invalid, cannot check field"
        })

    # 写入评分
    score_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(score_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Score: {total_score}/100")
    sys.exit(0 if total_score >= 60 else 1)  # 60 分及格

if __name__ == "__main__":
    main()
