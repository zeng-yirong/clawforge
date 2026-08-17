import json
import os
import sys
from datetime import datetime

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
details = []
total_score = 0

# 1. 检查目录结构（10分）
dirs = ["data", "data/devices", "data/schedules", "ops", "logs"]
dir_score = 10
dir_passed = True
for d in dirs:
    if not os.path.isdir(os.path.join(workspace, d)):
        dir_passed = False
        dir_score = 0
        break
details.append({
    "item": "目录结构",
    "score": dir_score,
    "max_score": 10,
    "passed": dir_passed,
    "reason": "所有必需目录存在" if dir_passed else f"缺少目录 {d}"
})
total_score += dir_score

# 2. 检查必需文件存在（10分）
files = ["ops/conflict_report.json"]
file_score = 10
file_passed = True
missing_files = []
for f in files:
    if not os.path.isfile(os.path.join(workspace, f)):
        file_passed = False
        missing_files.append(f)
file_score = 0 if not file_passed else 10
details.append({
    "item": "必需文件存在",
    "score": file_score,
    "max_score": 10,
    "passed": file_passed,
    "reason": "存在 ops/conflict_report.json" if file_passed else f"缺少 {missing_files}"
})
total_score += file_score

# 3. 解析 JSON 并检查结构有效性（10分）
json_valid = False
parse_error = ""
try:
    report_path = os.path.join(workspace, "ops/conflict_report.json")
    with open(report_path, "r") as f:
        report = json.load(f)
    if isinstance(report, dict) and "device_id" in report and "conflict_schedule_ids" in report:
        json_valid = True
    else:
        parse_error = "缺少 device_id 或 conflict_schedule_ids 字段"
except Exception as e:
    parse_error = str(e)

details.append({
    "item": "JSON 格式与结构",
    "score": 10 if json_valid else 0,
    "max_score": 10,
    "passed": json_valid,
    "reason": "解析成功且包含必要字段" if json_valid else f"解析失败: {parse_error}"
})
total_score += 10 if json_valid else 0

# 如果基本结构都失败，后续不再检查，但保留总分
if not json_valid:
    details.append({"item": "冲突设备ID", "score": 0, "max_score": 30, "passed": False, "reason": "前序检查失败"})
    details.append({"item": "冲突调度ID列表", "score": 0, "max_score": 40, "passed": False, "reason": "前序检查失败"})
    total_score += 0 + 0
    # 写入结果
    out = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(out, f, indent=2)
    sys.exit(0)

# 4. 检查 conflict_schedule_ids 必须为 list（额外 5 分，但上面已经给了结构分，这里细化）
if not isinstance(report["conflict_schedule_ids"], list):
    # 结构分已扣，这里额外扣分
    details.append({"item": "冲突调度ID必须是列表", "score": 0, "max_score": 5, "passed": False, "reason": "conflict_schedule_ids 不是列表"})
    total_score += 0
else:
    # 该项已经在结构分中覆盖，但我们不再重复加分，仅用于后续判断
    pass

# 5. 检查设备 ID 是否正确（30分）
expected_device = "bedroom_ac_001"
device_passed = report["device_id"] == expected_device
device_score = 30 if device_passed else 0
details.append({
    "item": "冲突设备ID",
    "score": device_score,
    "max_score": 30,
    "passed": device_passed,
    "reason": f"设备ID正确: {expected_device}" if device_passed else f"期望 {expected_device}, 实际 {report['device_id']}"
})
total_score += device_score

# 6. 检查冲突调度ID列表（40分）
# 预期冲突：两个活跃且重叠的调度 sch_004 和 sch_005
expected_ids = {"sch_004", "sch_005"}
actual_ids = set(report["conflict_schedule_ids"])
id_passed = (actual_ids == expected_ids)
id_score = 40 if id_passed else 0
if not id_passed:
    reason = f"预期 {expected_ids}, 实际 {actual_ids}"
else:
    reason = "所有冲突调度ID正确"
details.append({
    "item": "冲突调度ID列表",
    "score": id_score,
    "max_score": 40,
    "passed": id_passed,
    "reason": reason
})
total_score += id_score

# 写入总得分
out = {"total_score": total_score, "details": details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(out, f, indent=2)
