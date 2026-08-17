import sys
import os
import json
import re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
os.chdir(workspace)

score = 0
details = []
total_items = []

def add_result(item, passed, score_val, max_score, reason=""):
    total_items.append({
        "item": item,
        "passed": passed,
        "score": score_val,
        "max_score": max_score,
        "reason": reason
    })

# 1. 检查 ops 目录是否存在 (10分)
if os.path.isdir("ops"):
    add_result("ops/ directory exists", True, 10, 10, "Found ops/ directory")
else:
    add_result("ops/ directory exists", False, 0, 10, "Missing ops/ directory")

# 2. 检查 ops/todo.json 格式合法性 (10分)
todo_path = "ops/todo.json"
if os.path.isfile(todo_path):
    try:
        with open(todo_path, "r") as f:
            todo = json.load(f)
        if isinstance(todo, dict):
            add_result("todo.json valid JSON dict", True, 10, 10, "Parsed successfully")
        else:
            add_result("todo.json valid JSON dict", False, 0, 10, "Not a dict")
            todo = {}
    except Exception as e:
        add_result("todo.json valid JSON dict", False, 0, 10, f"Parse error: {e}")
        todo = {}
else:
    add_result("todo.json exists", False, 0, 10, "File not found")
    todo = {}

# 3. 检查 ops/reply_draft.json 格式合法性 (10分)
reply_path = "ops/reply_draft.json"
if os.path.isfile(reply_path):
    try:
        with open(reply_path, "r") as f:
            reply = json.load(f)
        if isinstance(reply, dict):
            add_result("reply_draft.json valid JSON dict", True, 10, 10, "Parsed successfully")
        else:
            add_result("reply_draft.json valid JSON dict", False, 0, 10, "Not a dict")
            reply = {}
    except Exception as e:
        add_result("reply_draft.json valid JSON dict", False, 0, 10, f"Parse error: {e}")
        reply = {}
else:
    add_result("reply_draft.json exists", False, 0, 10, "File not found")
    reply = {}

# 4. 检查 todo.json 关键字段 (15分)
todo_fields = {"title": "Q3 Progress Report", "deadline": "2025-03-20"}
for field, expected in todo_fields.items():
    if field in todo:
        val = todo[field]
        if val == expected:
            add_result(f"todo.json field '{field}' matches", True, 7.5, 7.5, f"Value = {val}")
        else:
            add_result(f"todo.json field '{field}' matches", False, 0, 7.5, f"Expected '{expected}', got '{val}'")
    else:
        add_result(f"todo.json field '{field}' exists", False, 0, 7.5, f"Field '{field}' missing")

# 5. 检查 reply_draft.json 关键字段 (15分)
reply_fields = {
    "to": "john.manager@company.com",
    "subject": "Re: Q3 Progress Report - Urgent"
}
for field, expected in reply_fields.items():
    if field in reply:
        val = reply[field]
        if val == expected:
            add_result(f"reply_draft.json field '{field}' matches", True, 7.5, 7.5, f"Value = {val}")
        else:
            add_result(f"reply_draft.json field '{field}' matches", False, 0, 7.5, f"Expected '{expected}', got '{val}'")
    else:
        add_result(f"reply_draft.json field '{field}' exists", False, 0, 7.5, f"Field '{field}' missing")

# 6. 检查 reply_draft.body 是否包含签名（从 accounts.json 读取默认签名） (15分)
if "body" in reply:
    body = reply["body"]
    # 读取账户签名
    accounts_path = "data/accounts.json"
    expected_signature = ""
    if os.path.isfile(accounts_path):
        try:
            with open(accounts_path) as f:
                acc_data = json.load(f)
            if "accounts" in acc_data and len(acc_data["accounts"]) > 0:
                expected_signature = acc_data["accounts"][0].get("default_signature", "")
        except:
            pass
    if expected_signature and expected_signature in body:
        add_result("reply_draft.body contains signature", True, 15, 15, "Signature present")
    elif expected_signature:
        add_result("reply_draft.body contains signature", False, 0, 15, f"Signature '{expected_signature}' not found in body")
    else:
        add_result("reply_draft.body contains signature", False, 0, 15, "Could not read signature from accounts.json")
else:
    add_result("reply_draft.json has 'body' field", False, 0, 15, "Missing 'body' field")

# 7. 检查是否有多余的文件或字段（扣分项：每发现一个额外文件 -5 但最低扣到0分）
extra_penalty = 0
# 只允许 ops/ 下只有两个我们需要的文件
ops_files = os.listdir("ops") if os.path.isdir("ops") else []
allowed = {"todo.json", "reply_draft.json"}
for f in ops_files:
    if f not in allowed:
        extra_penalty -= 5
if extra_penalty < 0:
    add_result("No extra files in ops/", False, max(extra_penalty, -15), 0, f"Found extra files: {[f for f in ops_files if f not in allowed]}")

# 计算总分
total_score = sum(item["score"] for item in total_items)
total_score = max(0, min(100, total_score))  # 限制在0-100
total_score = int(round(total_score))

output = {
    "total_score": total_score,
    "details": total_items
}

with open("workplace_score.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"Verification complete. Score: {total_score}/100")
