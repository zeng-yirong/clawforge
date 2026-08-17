import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 ops 目录
    ops_dir = os.path.join(workspace, "ops")
    dir_ok = os.path.isdir(ops_dir)
    details.append({
        "item": "ops 目录存在",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "ops 目录" + ("存在" if dir_ok else "不存在")
    })
    if dir_ok:
        total_score += 10

    # 2. 检查目标文件存在
    target_path = os.path.join(ops_dir, "kill_target.json")
    file_ok = os.path.isfile(target_path)
    details.append({
        "item": "ops/kill_target.json 存在",
        "score": 10 if file_ok else 0,
        "max_score": 10,
        "passed": file_ok,
        "reason": "目标文件" + ("存在" if file_ok else "不存在")
    })
    if file_ok:
        total_score += 10
    else:
        # 文件不存在，后续检查无法进行，直接输出结果
        finish(total_score, details, workspace)
        return

    # 3. JSON 合法性
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        json_valid = True
    except (json.JSONDecodeError, Exception):
        json_valid = False
        data = None
    details.append({
        "item": "JSON 格式合法",
        "score": 20 if json_valid else 0,
        "max_score": 20,
        "passed": json_valid,
        "reason": "JSON 解析" + ("成功" if json_valid else "失败")
    })
    if json_valid:
        total_score += 20
    else:
        finish(total_score, details, workspace)
        return

    # 4. 包含 'pid' 字段
    has_pid = isinstance(data, dict) and "pid" in data
    details.append({
        "item": "包含 pid 字段",
        "score": 20 if has_pid else 0,
        "max_score": 20,
        "passed": has_pid,
        "reason": "pid 字段" + ("存在" if has_pid else "不存在")
    })
    if has_pid:
        total_score += 20
    else:
        finish(total_score, details, workspace)
        return

    # 5. pid 值是否为 12345
    pid_value = data["pid"]
    pid_correct = (pid_value == 12345)
    details.append({
        "item": "pid 值为 12345",
        "score": 40 if pid_correct else 0,
        "max_score": 40,
        "passed": pid_correct,
        "reason": f"pid 值 = {pid_value}" + (" (正确  12345)" if pid_correct else f" (期望 12345)")
    })
    if pid_correct:
        total_score += 40

    # 额外：不允许有多余字段（可选扣分项，此处不强制但若有多余则扣10分？可以加）
    # 但题目说“捏造多余字段/节点必须严扣分”，我们实施：只有 pid 一个key 加10分奖励（但总分上限100）。为了不超分，可以改为扣分项。
    # 更简单：若除了 pid 还有别的 key，扣10分。但原评分已有100，扣分后可能变负。我们设计为奖励，但总分不能超100。
    # 为了简单，我们保持上述评分项满分100。若有多余字段，视为不严格符合要求，但题目只要求检查必需字段。我们按照验证逻辑，不扣分，但可以在 reason 中注明。
    # 然而指令要求“捏造多余字段/节点必须严扣分”，所以需要扣分。我们把 pid 值一项改为 30分，多余字段检查设为10分。
    # 重新调整：pid字段存在 10分，pid值正确 30分，无多余字段 10分。但已输出前项，需重新设计。我们可以在最后加一项。
    # 由于我们已按顺序写了，现在调整：将第5项改为10分（pid存在）和第6项（pid值正确）30分，再加第7项（无多余字段）10分。但需总分100，且前面已定项。为了简化，我们在最终输出前修改前面的细节数组。
    # 但为了输出简洁，优先保证核心逻辑。我们采用动态调整总分，在最后加入无多余字段检查。
    # 实际上，我们可以在检查完 pid 值后，检查键的数量是否只有1个（pid）。如果是，额外加10分，但总分不能超过100，否则扣分。
    # 实施：如果有多余字段，总分减10（但前面已分配100，减后最低0）。我们就在细节中加一条，分数为10，若有多余字段则得0，否则得10。
    keys = list(data.keys()) if isinstance(data, dict) else []
    only_pid = (keys == ["pid"])
    details.append({
        "item": "无多余字段 (仅含 pid)",
        "score": 10 if only_pid else 0,
        "max_score": 10,
        "passed": only_pid,
        "reason": "字段列表 " + str(keys) + (" (仅 pid)" if only_pid else " (含多余字段)")
    })
    if only_pid:
        total_score += 10
    else:
        # 扣分：减去10分（总分最多扣到0）
        total_score = max(0, total_score - 10)

    # 确保总分不超过100（其实不会超过，因为最多110，但上面扣分逻辑保留了上限）
    total_score = min(total_score, 100)

    finish(total_score, details, workspace)


def finish(total_score, details, workspace):
    score_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"验证完成，总分 {total_score}/100")
    sys.exit(0)


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
