import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # Helper to check file existence
    def exists(path):
        return os.path.exists(os.path.join(workspace, path))

    # Helper to read file content
    def read_file(path):
        try:
            with open(os.path.join(workspace, path), "r", encoding="utf-8") as f:
                return f.read()
        except:
            return None

    # 1. drafts directory exists (10)
    item = {"item": "drafts directory exists", "max_score": 10}
    if exists("drafts"):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "drafts/ found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "drafts/ missing"
    score_details.append(item)
    total_score += item["score"]

    # 2. tasks directory exists (10)
    item = {"item": "tasks directory exists", "max_score": 10}
    if exists("tasks"):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "tasks/ found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "tasks/ missing"
    score_details.append(item)
    total_score += item["score"]

    # 3. Count files in drafts (must be exactly 2) (10)
    item = {"item": "drafts file count == 2", "max_score": 10}
    drafts_dir = os.path.join(workspace, "drafts")
    if os.path.isdir(drafts_dir):
        draft_files = [f for f in os.listdir(drafts_dir) if os.path.isfile(os.path.join(drafts_dir, f))]
        if len(draft_files) == 2:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = f"found {len(draft_files)} file(s)"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"expected 2, got {len(draft_files)}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "drafts/ not a directory"
    score_details.append(item)
    total_score += item["score"]

    # 4. Each draft file contains "alice@clientcorp.com" (10)
    # We check all files in drafts for simplicity; if count not 2, partial credit possible
    item = {"item": "all draft files contain alice@clientcorp.com", "max_score": 10}
    if os.path.isdir(drafts_dir):
        draft_files = [f for f in os.listdir(drafts_dir) if os.path.isfile(os.path.join(drafts_dir, f))]
        all_have = True
        for fname in draft_files:
            content = read_file(os.path.join("drafts", fname))
            if content is None or "alice@clientcorp.com" not in content:
                all_have = False
                break
        if all_have and len(draft_files) > 0:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "all draft files contain the email"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "one or more files lack expected email"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "drafts/ missing"
    score_details.append(item)
    total_score += item["score"]

    # 5. Each draft file contains "Re:" (10)
    item = {"item": "all draft files contain 'Re:'", "max_score": 10}
    if os.path.isdir(drafts_dir):
        draft_files = [f for f in os.listdir(drafts_dir) if os.path.isfile(os.path.join(drafts_dir, f))]
        all_have = True
        for fname in draft_files:
            content = read_file(os.path.join("drafts", fname))
            if content is None or "Re:" not in content:
                all_have = False
                break
        if all_have and len(draft_files) > 0:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "all draft files contain Re:"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "one or more files lack 'Re:'"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "drafts/ missing"
    score_details.append(item)
    total_score += item["score"]

    # 6. tasks directory contains exactly 1 file (10)
    item = {"item": "tasks file count == 1", "max_score": 10}
    tasks_dir = os.path.join(workspace, "tasks")
    if os.path.isdir(tasks_dir):
        task_files = [f for f in os.listdir(tasks_dir) if os.path.isfile(os.path.join(tasks_dir, f))]
        if len(task_files) == 1:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = f"found {len(task_files)} file(s)"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"expected 1, got {len(task_files)}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "tasks/ missing"
    score_details.append(item)
    total_score += item["score"]

    # 7. The tasks file contains "交付产品原型" (10)
    item = {"item": "tasks file contains '交付产品原型'", "max_score": 10}
    if os.path.isdir(tasks_dir):
        task_files = [f for f in os.listdir(tasks_dir) if os.path.isfile(os.path.join(tasks_dir, f))]
        if len(task_files) == 1:
            content = read_file(os.path.join("tasks", task_files[0]))
            if content and "交付产品原型" in content:
                item["score"] = 10
                item["passed"] = True
                item["reason"] = "found target text"
            else:
                item["score"] = 0
                item["passed"] = False
                item["reason"] = "target text not found"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "wrong number of files"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "tasks/ missing"
    score_details.append(item)
    total_score += item["score"]

    # 8. Spam email (email_004.json) is deleted (10)
    item = {"item": "spam email deleted (email_004.json missing)", "max_score": 10}
    spam_path = "data/emails/email_004.json"
    if not exists(spam_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "file removed"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "file still exists"
    score_details.append(item)
    total_score += item["score"]

    # 9. All non-spam original emails remain (10)
    item = {"item": "other original emails not deleted", "max_score": 10}
    required = ["data/emails/email_001.json", "data/emails/email_002.json", "data/emails/email_003.json", "data/emails/email_005.json"]
    all_present = all(exists(p) for p in required)
    if all_present:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "all 4 emails present"
    else:
        missing = [p for p in required if not exists(p)]
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"missing: {', '.join(missing)}"
    score_details.append(item)
    total_score += item["score"]

    # 10. (Bonus) No extra unexpected files in drafts or tasks? Not required.
    # We'll skip to make total exactly 100 with the above.

    # Write result
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Total score: {total_score}/100")

if __name__ == "__main__":
    main()
