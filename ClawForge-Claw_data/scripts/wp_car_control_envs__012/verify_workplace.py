import os
import json
import sys

def verify(workspace: str):
    details = []
    total_score = 0

    # 1. 目录结构检查（10分）
    score = 0
    max_score = 10
    passed = True
    reasons = []
    
    if not os.path.isdir(os.path.join(workspace, "ops")):
        passed = False
        reasons.append("ops目录不存在")
    else:
        reasons.append("ops目录存在")
        score += 5
    
    fan_path = os.path.join(workspace, "ops", "fan_speed.json")
    if not os.path.isfile(fan_path):
        passed = False
        reasons.append("ops/fan_speed.json文件不存在")
    else:
        reasons.append("目标文件存在")
        score += 5
    
    total_score += score
    details.append({
        "item": "目录与文件存在性",
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": "; ".join(reasons)
    })

    # 2. 文件格式合法性（10分）
    score = 0
    max_score = 10
    passed = True
    reasons = []
    data = None
    try:
        with open(fan_path, "r") as f:
            data = json.load(f)
        reasons.append("JSON解析成功")
        score += 10
    except (json.JSONDecodeError, FileNotFoundError) as e:
        passed = False
        reasons.append(f"文件不可解析: {e}")
    
    total_score += score
    details.append({
        "item": "JSON格式合法性",
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": "; ".join(reasons)
    })
    
    # 3. 内容键值正确性（80分）
    score = 0
    max_score = 80
    passed = True
    reasons = []
    
    if data is not None:
        # 只应包含一个顶级字段（允许额外字段但应扣分，这里我们只检查fan_speed）
        if isinstance(data, dict):
            if "fan_speed" in data:
                fan_speed = data["fan_speed"]
                if isinstance(fan_speed, int) and fan_speed == 3:
                    score += 70
                    reasons.append("fan_speed值为3，正确")
                elif isinstance(fan_speed, int):
                    reasons.append(f"fan_speed值为{fan_speed}，期望3")
                    passed = False
                else:
                    reasons.append("fan_speed类型非整数")
                    passed = False
            else:
                reasons.append("缺少fan_speed键")
                passed = False
            
            # 检查是否有无关键（扣分选项）
            allowed_keys = {"fan_speed"}
            extra_keys = set(data.keys()) - allowed_keys
            if extra_keys:
                # 有额外键，扣10分
                score = max(0, score - 10)
                reasons.append(f"发现多余键{extra_keys}，扣10分")
        else:
            reasons.append("顶层不是字典")
            passed = False
    else:
        passed = False
        reasons.append("无数据可检查")
    
    total_score += score
    details.append({
        "item": "内容精确值验证",
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": "; ".join(reasons)
    })

    # 最终总分不得超过100
    total_score = min(total_score, 100)
    
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
