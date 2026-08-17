import sys
import os
import json

def verify(workspace: str):
    total_score = 0
    details = []

    # ---------- 1. 检查 ops 目录是否存在 (10分) ----------
    ops_path = os.path.join(workspace, "ops")
    item = {"item": "ops 目录存在", "max_score": 10}
    if os.path.isdir(ops_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops 目录已创建"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "缺少 ops 目录"
    details.append(item)
    total_score += item["score"]

    # ---------- 2. 检查 ops/anomaly_waypoint.json 是否存在 (15分) ----------
    result_path = os.path.join(ops_path, "anomaly_waypoint.json")
    item = {"item": "目标文件 ops/anomaly_waypoint.json 存在", "max_score": 15}
    if os.path.isfile(result_path):
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "文件存在"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "文件不存在"
    details.append(item)
    total_score += item["score"]

    # 如果文件不存在，则后续项得0分并退出（继续检查但给0分）
    file_exists = os.path.isfile(result_path)

    # ---------- 3. 文件是否为合法 JSON (20分) ----------
    item = {"item": "JSON 格式合法", "max_score": 20}
    if file_exists:
        try:
            with open(result_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            item["score"] = 20
            item["passed"] = True
            item["reason"] = "可正常解析为 JSON 对象"
        except Exception as e:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"JSON 解析失败: {str(e)}"
            data = None
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "文件不存在"
        data = None
    details.append(item)
    total_score += item["score"]

    # ---------- 4. 检查 anomaly_waypoint_id 字段 (40分) ----------
    item = {"item": "anomaly_waypoint_id 字段存在且值为 'poi-003'", "max_score": 40}
    if data is not None and isinstance(data, dict):
        wid = data.get("anomaly_waypoint_id")
        if wid == "poi-003":
            item["score"] = 40
            item["passed"] = True
            item["reason"] = f"异常途径点 ID 为 {wid}"
        elif wid is None:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "缺少 anomaly_waypoint_id 字段"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"ID 不匹配，实际值 '{wid}'，期望 'poi-003'"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "数据无效"
    details.append(item)
    total_score += item["score"]

    # ---------- 5. 额外：检查是否有 reason 字段 (15分，非空即可) ----------
    item = {"item": "reason 字段存在且非空", "max_score": 15}
    if data is not None and isinstance(data, dict):
        reason = data.get("reason")
        if reason and isinstance(reason, str) and len(reason.strip()) > 0:
            item["score"] = 15
            item["passed"] = True
            item["reason"] = f"原因描述: {reason}"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "reason 字段缺失或为空字符串"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "数据无效"
    details.append(item)
    total_score += item["score"]

    # 最终写入结果
    result = {
        "total_score": min(total_score, 100),  # 确保不超过100
        "details": details
    }
    result_path_out = os.path.join(workspace, "workplace_score.json")
    with open(result_path_out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
