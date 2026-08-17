import sys
import json
import csv
import hashlib
from pathlib import Path

def main():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    total_score = 0
    details = []

    # ---------- 1. 目录结构检查 (10 分) ----------
    # 检查 ops 目录存在
    ops_dir = workspace / "ops"
    if ops_dir.is_dir():
        total_score += 10
        details.append({
            "item": "ops 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops 目录已创建"
        })
    else:
        details.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops 目录不存在"
        })

    # ---------- 2. 检查必要输出文件格式 (20 分: 每个文件 10 分) ----------
    platforms_path = ops_dir / "platforms.json"
    hash_path = ops_dir / "credential_hash.json"
    platforms_ok = False
    hash_ok = False

    # platforms.json
    if platforms_path.is_file():
        try:
            with open(platforms_path, "r") as f:
                platforms_data = json.load(f)
            if isinstance(platforms_data, list):
                platforms_ok = True
                details.append({
                    "item": "platforms.json 格式合法",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "文件存在且为 JSON 数组"
                })
            else:
                details.append({
                    "item": "platforms.json 格式合法",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "JSON 内容不是数组"
                })
        except Exception as e:
            details.append({
                "item": "platforms.json 格式合法",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"无法解析 JSON: {e}"
            })
    else:
        details.append({
            "item": "platforms.json 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })

    # credential_hash.json
    if hash_path.is_file():
        try:
            with open(hash_path, "r") as f:
                hash_data = json.load(f)
            if isinstance(hash_data, dict) and "hash" in hash_data and isinstance(hash_data["hash"], str):
                hash_ok = True
                details.append({
                    "item": "credential_hash.json 格式合法",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "文件存在且为包含 hash 字段的对象"
                })
            else:
                details.append({
                    "item": "credential_hash.json 格式合法",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "JSON 结构不符合预期（需 {hash: str}）"
                })
        except Exception as e:
            details.append({
                "item": "credential_hash.json 格式合法",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"无法解析 JSON: {e}"
            })
    else:
        details.append({
            "item": "credential_hash.json 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })

    if not (platforms_ok and hash_ok):
        # 如果格式都不对，直接结束，后面无法比对
        details.append({
            "item": "结果验证",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "必要输出文件缺失或格式错误，跳过内容比对"
        })
        final = {
            "total_score": total_score,
            "details": details
        }
        with open(str(workspace / "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # ---------- 3. 内容正确性比对 (70 分: platforms 20 + hash 50) ----------
    # 读取原始 CSV 并计算预期结果
    csv_path = workspace / "vault" / "credentials.csv"
    if not csv_path.is_file():
        details.append({
            "item": "内容验证",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "原始 credentials.csv 不存在，无法验证"
        })
        final = {
            "total_score": total_score + 0,
            "details": details
        }
        with open(str(workspace / "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    records = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    # 筛选符合条件的记录
    candidates = []
    for r in records:
        if (r.get("category","").strip() == "社交媒体" and
            r.get("expired","").strip() == "no" and
            int(r.get("strength","0").strip()) < 50):
            candidates.append(r)

    # 按密码长度降序，长度相同按 platform 升序
    candidates.sort(key=lambda x: (-len(x["password"]), x["platform"]))

    # 取前两个
    top_two = candidates[:2]
    # 构建字符串：按密码长度从长到短排列（已排序），每行 "username:password"
    strings = [f"{r['username']}:{r['password']}" for r in top_two]
    concatenated = "\n".join(strings)
    expected_hash = hashlib.sha256(concatenated.encode('utf-8')).hexdigest()

    # 预期 platforms 去重排序
    expected_platforms = sorted(set(r["platform"] for r in candidates))

    # 比对 platforms.json
    with open(platforms_path, "r") as f:
        actual_platforms = json.load(f)
    if actual_platforms == expected_platforms:
        total_score += 20
        details.append({
            "item": "platforms.json 内容正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"平台列表一致: {expected_platforms}"
        })
    else:
        details.append({
            "item": "platforms.json 内容正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"预期 {expected_platforms}，实际 {actual_platforms}"
        })

    # 比对 credential_hash.json
    with open(hash_path, "r") as f:
        actual_hash_data = json.load(f)
    actual_hash = actual_hash_data["hash"]
    if actual_hash == expected_hash:
        total_score += 50
        details.append({
            "item": "credential_hash.json 哈希正确",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": f"SHA256 匹配: {expected_hash[:16]}..."
        })
    else:
        details.append({
            "item": "credential_hash.json 哈希正确",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"预期 {expected_hash}，实际 {actual_hash}"
        })

    # 写入评分
    final = {
        "total_score": total_score,
        "details": details
    }
    with open(str(workspace / "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
