import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def read_or_fail(path, label="file"):
    full = os.path.join(workspace, path)
    if not os.path.isfile(full):
        return None, f"{label} {path} 不存在"
    try:
        with open(full, "r") as f:
            return f.read(), None
    except Exception as e:
        return None, f"读取 {path} 失败: {e}"

def check_notify_emails(content):
    lines = [line.strip() for line in content.strip().splitlines() if line.strip()]
    expected = {"john.smith@example.com"}
    actual = set(lines)
    if actual == expected:
        return True, f"邮箱集合完全匹配 ({expected})"
    else:
        return False, f"期望 {expected}，实际得到 {actual}"

def main():
    results = []
    total = 0

    # 1. 检查输出目录 ops 存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        results.append({"item": "输出目录 ops/ 存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops 目录已创建"})
        total += 10
    else:
        results.append({"item": "输出目录 ops/ 存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops 目录不存在"})

    # 2. 检测 notify_emails.txt 存在且可读 (20分)
    content, err = read_or_fail("ops/notify_emails.txt", "通知邮箱文件")
    if err:
        results.append({"item": "ops/notify_emails.txt 存在且可读", "score": 0, "max_score": 20, "passed": False, "reason": err})
        # 后续无法检查，直接写分结束
        final = {"total_score": total, "details": results}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        print(json.dumps(final, indent=2))
        return

    results.append({"item": "ops/notify_emails.txt 存在且可读", "score": 20, "max_score": 20, "passed": True, "reason": "文件正常读取"})
    total += 20

    # 3. 内容格式：每行一个邮箱，无多余空白 (10分)
    lines = [line.strip() for line in content.strip().splitlines() if line.strip()]
    if len(lines) == 1 and "@" in lines[0]:
        results.append({"item": "邮箱格式正确（每行一个有效邮箱）", "score": 10, "max_score": 10, "passed": True, "reason": f"共 {len(lines)} 个邮箱"})
        total += 10
    else:
        results.append({"item": "邮箱格式正确（每行一个有效邮箱）", "score": 0, "max_score": 10, "passed": False, "reason": f"行数={len(lines)}，内容={lines}"})

    # 4. 关键：邮箱内容是否等于唯一正确答案 john.smith@example.com (50分)
    passed, reason = check_notify_emails(content)
    score = 50 if passed else 0
    results.append({"item": "通知邮箱与预期完全一致", "score": score, "max_score": 50, "passed": passed, "reason": reason})
    total += score

    # 5. 额外检查：没有引入无关文件 (10分) – 只允许 ops/notify_emails.txt
    ops_files = [f for f in os.listdir(ops_dir) if os.path.isfile(os.path.join(ops_dir, f))]
    extra = [f for f in ops_files if f != "notify_emails.txt"]
    if extra:
        results.append({"item": "ops 目录无多余文件", "score": 0, "max_score": 10, "passed": False, "reason": f"发现多余文件: {extra}"})
    else:
        results.append({"item": "ops 目录无多余文件", "score": 10, "max_score": 10, "passed": True, "reason": "只有需要的结果文件"})
        total += 10

    # 写入评分
    final = {"total_score": total, "details": results}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    print(json.dumps(final, indent=2))

if __name__ == "__main__":
    main()
