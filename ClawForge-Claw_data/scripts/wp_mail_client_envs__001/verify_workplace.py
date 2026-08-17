import sys
import json
import os
import pathlib

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

results = []

def wpath(path):
    return os.path.join(workspace, path)

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def check(description, score, max_score, passed, reason=""):
    results.append({
        "item": description,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# ------------------------------------------------------------
# 1. 检查 ops/urgent_replies.json 存在且合法 JSON
urgent_path = wpath("ops/urgent_replies.json")
if os.path.isfile(urgent_path):
    try:
        with open(urgent_path) as f:
            urgent_data = json.load(f)
        check("ops/urgent_replies.json 存在且是合法 JSON", 10, 10, True, "文件存在且解析成功")
    except Exception as e:
        check("ops/urgent_replies.json 存在但解析失败", 0, 10, False, str(e))
        urgent_data = None
else:
    check("ops/urgent_replies.json 文件不存在", 0, 10, False, "文件未找到")
    urgent_data = None

# ------------------------------------------------------------
# 2. 检查邮件修改: 符合条件的3封 (email_001, email_002, email_006)
expected_client_emails = ["email_001", "email_002", "email_006"]
contact_email_map = {
    "contact_alice": "alice@clientcorp.com"
}
# 先加载 contacts 以获得邮箱映射
contacts_path = wpath("data/contacts.json")
try:
    contacts_data = load_json(contacts_path)
    contact_map = {}
    for c in contacts_data.get("contacts", []):
        contact_map[c["contact_id"]] = c.get("email", "")
except:
    contact_map = {}

email_dir = wpath("data/emails")
score_email_mod = 0
for eid in expected_client_emails:
    fpath = os.path.join(email_dir, f"{eid}.json")
    if not os.path.isfile(fpath):
        check(f"邮件 {eid}.json 文件不存在", 0, 15, False, "文件丢失")
        continue
    try:
        email = load_json(fpath)
        passed = (email.get("folder") == "work/client") and ("client" in email.get("labels", []))
        if passed:
            score_email_mod += 15
            check(f"邮件 {eid} 文件夹和标签正确", 15, 15, True, f"folder={email.get('folder')}, labels={email.get('labels')}")
        else:
            check(f"邮件 {eid} 文件夹或标签不正确", 0, 15, False, f"folder={email.get('folder')}, labels={email.get('labels')}")
    except Exception as e:
        check(f"邮件 {eid}.json 解析失败", 0, 15, False, str(e))

# ------------------------------------------------------------
# 3. 检查非条件邮件未被误改 (email_003, email_004, email_005, email_007)
should_stay_inbox = ["email_003", "email_004", "email_005", "email_007"]
score_non_mod = 0
for eid in should_stay_inbox:
    fpath = os.path.join(email_dir, f"{eid}.json")
    if not os.path.isfile(fpath):
        check(f"邮件 {eid}.json 不存在", 0, 5, False, "文件丢失")
        continue
    try:
        email = load_json(fpath)
        # 期望 folder 仍然是 inbox，labels 不应包含 client
        passed = (email.get("folder") == "inbox") and ("client" not in email.get("labels", []))
        if passed:
            score_non_mod += 5
            check(f"非条件邮件 {eid} 未被误改", 5, 5, True, f"folder={email.get('folder')}, labels={email.get('labels')}")
        else:
            check(f"非条件邮件 {eid} 被意外修改", 0, 5, False, f"folder={email.get('folder')}, labels={email.get('labels')}")
    except Exception as e:
        check(f"邮件 {eid}.json 解析失败", 0, 5, False, str(e))

# ------------------------------------------------------------
# 4. 检查清单内容正确性
score_list = 0
max_list = 25
if urgent_data is not None:
    # 必须是列表
    if isinstance(urgent_data, list):
        # 预期每条包含 email_id 和 contact_email
        # 构建预期集合
        expected_entries = []
        for eid in expected_client_emails:
            expected_entries.append({
                "email_id": eid,
                "contact_email": contact_map.get("contact_alice", "alice@clientcorp.com")
            })
        # 忽略顺序，转换为可比较的集合（元组）
        expected_set = {(e["email_id"], e["contact_email"]) for e in expected_entries}
        actual_set = set()
        valid_entries = 0
        for entry in urgent_data:
            if isinstance(entry, dict) and "email_id" in entry and "contact_email" in entry:
                actual_set.add((entry["email_id"], entry["contact_email"]))
                valid_entries += 1
        if len(urgent_data) != len(expected_entries):
            check(f"清单条目数量不匹配: 期望 {len(expected_entries)} 实际 {len(urgent_data)}", 0, 25, False, f"数量差异")
        elif expected_set == actual_set:
            score_list = 25
            check("清单内容完全正确", 25, 25, True, f"包含 {len(expected_entries)} 条正确记录")
        else:
            missing = expected_set - actual_set
            extra = actual_set - expected_set
            reason = f"缺失: {missing}, 多余: {extra}"
            check("清单内容部分正确", 10, 25, False, reason)
    else:
        check("清单根元素不是列表", 0, 25, False, "type: " + str(type(urgent_data)))
else:
    check("清单文件不可用，跳过内容检查", 0, 25, False, "文件解析失败")

# ------------------------------------------------------------
# 汇总总分
total = sum(r["score"] for r in results)
# 确保不超过100
total = min(total, 100)
check("总分", total, 100, total >= 80, f"总分 {total}/100")

# 写入结果
out_path = os.path.join(workspace, "workplace_score.json")
with open(out_path, "w") as f:
    json.dump({"total_score": total, "details": results}, f, indent=2)

print(f"验证完成，总分 {total}/100")
sys.exit(0 if total >= 80 else 1)
