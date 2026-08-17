import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
results = []

def check(description, max_score, test_fn):
    try:
        passed, msg = test_fn()
        score = max_score if passed else 0
        results.append({
            "item": description,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": msg
        })
    except Exception as e:
        results.append({
            "item": description,
            "score": 0,
            "max_score": max_score,
            "passed": False,
            "reason": f"Exception: {str(e)}"
        })

# 1. 文件存在性（10分）
def file_exists():
    path = os.path.join(workspace, "recommendations.json")
    if os.path.isfile(path):
        return True, "File exists"
    return False, "recommendations.json not found"
check("recommendations.json exists", 10, file_exists)

# 2. JSON合法性（10分）
def json_valid():
    path = os.path.join(workspace, "recommendations.json")
    with open(path, "r") as f:
        data = json.load(f)
    return True, "Valid JSON"
check("Valid JSON", 10, json_valid)

# 3. 必须包含recommendations数组，长度为2（10分）
def rec_count():
    path = os.path.join(workspace, "recommendations.json")
    with open(path, "r") as f:
        data = json.load(f)
    recs = data.get("recommendations", [])
    if len(recs) == 2:
        return True, f"Found {len(recs)} recommendations"
    return False, f"Expected 2 recommendations, got {len(recs)}"
check("Exactly 2 recommendations", 10, rec_count)

# 4. 第一条建议：living room humidifier 设置55%湿度（30分）
def rec1_correct():
    path = os.path.join(workspace, "recommendations.json")
    with open(path, "r") as f:
        data = json.load(f)
    recs = data.get("recommendations", [])
    # Find the humidifier recommendation
    target = None
    for r in recs:
        if r.get("device_id") == "humid_living":
            target = r
            break
    if target is None:
        return False, "Missing recommendation for humid_living"
    expected_humidity = 55
    rec_humidity = target.get("recommended_setting", {}).get("humidity")
    if rec_humidity != expected_humidity:
        return False, f"Expected humidity={expected_humidity}, got {rec_humidity}"
    reason = target.get("reason", "")
    if len(reason.strip()) < 5:
        return False, "Reason too short or missing"
    # Check no extra fields
    allowed = {"device_id", "recommended_setting", "reason"}
    extra = set(target.keys()) - allowed
    if extra:
        return False, f"Extra fields: {extra}"
    return True, "Living room humidifier recommendation correct"
check("Humidifier recommendation (humid_living, humidity=55)", 30, rec1_correct)

# 5. 第二条建议：bedroom AC 设置21°C（30分）
def rec2_correct():
    path = os.path.join(workspace, "recommendations.json")
    with open(path, "r") as f:
        data = json.load(f)
    recs = data.get("recommendations", [])
    target = None
    for r in recs:
        if r.get("device_id") == "ac_bedroom":
            target = r
            break
    if target is None:
        return False, "Missing recommendation for ac_bedroom"
    expected_temp = 21
    rec_temp = target.get("recommended_setting", {}).get("temperature")
    if rec_temp != expected_temp:
        return False, f"Expected temperature={expected_temp}, got {rec_temp}"
    reason = target.get("reason", "")
    if len(reason.strip()) < 5:
        return False, "Reason too short or missing"
    allowed = {"device_id", "recommended_setting", "reason"}
    extra = set(target.keys()) - allowed
    if extra:
        return False, f"Extra fields: {extra}"
    return True, "Bedroom AC recommendation correct"
check("AC recommendation (ac_bedroom, temperature=21)", 30, rec2_correct)

# 6. 整体结构无多余字段（10分）
def no_extra_fields():
    path = os.path.join(workspace, "recommendations.json")
    with open(path, "r") as f:
        data = json.load(f)
    allowed_top = {"recommendations"}
    extra = set(data.keys()) - allowed_top
    if extra:
        return False, f"Extra top-level fields: {extra}"
    return True, "No extra top-level fields"
check("No extra top-level fields", 10, no_extra_fields)

# Calculate total
total_score = sum(r["score"] for r in results)
max_total = sum(r["max_score"] for r in results)
# Ensure integer
total_score = round(total_score)

output = {
    "total_score": total_score,
    "details": results
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(output, f, indent=2)

print(f"Total score: {total_score}/{max_total}")
